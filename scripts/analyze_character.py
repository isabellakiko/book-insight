#!/usr/bin/env python3
"""
离线人物分析脚本 - 在 Claude Code 中使用，分析结果保存到文件
"""

import asyncio
import json
import os
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / "apps" / "api" / ".env"
load_dotenv(env_path)

# 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen-plus")

DATA_DIR = Path(__file__).parent.parent / "data"
BOOKS_DIR = DATA_DIR / "books"
ANALYSIS_DIR = DATA_DIR / "analysis"

# OpenAI 客户端
client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL)


def chat_json(prompt: str, system: str = "", max_tokens: int = 4096) -> dict:
    """发送消息并解析 JSON 响应"""
    system_with_json = system + "\n\nRespond with valid JSON only. No markdown code blocks."

    messages = []
    if system_with_json:
        messages.append({"role": "system", "content": system_with_json})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        max_tokens=max_tokens,
        messages=messages,
        temperature=0.3,
    )

    text = response.choices[0].message.content.strip()

    # 清理 markdown 代码块
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    return json.loads(text)


def analyze_chapter_appearance(
    character_name: str,
    chapter_index: int,
    chapter_title: str,
    chapter_content: str,
) -> dict:
    """分析人物在某一章节的表现"""

    # 截断内容避免 token 过长
    content = chapter_content[:15000]

    prompt = f"""分析人物「{character_name}」在以下章节中的表现。

章节：第{chapter_index + 1}章 {chapter_title}

内容：
{content}

请分析并返回 JSON：
{{
    "events": ["该人物在本章参与的事件，2-4条"],
    "interactions": ["与其他人物的互动，格式：与XX：互动内容"],
    "quote": "本章中最能体现该人物特点的描述或台词（原文摘录，50字内）",
    "mood": "本章中该人物的情绪状态（一个词）"
}}"""

    system = f"你是一个小说分析助手。只关注人物「{character_name}」的相关内容。"

    try:
        result = chat_json(prompt, system, max_tokens=1000)
        return {
            "chapter_index": chapter_index,
            "chapter_title": chapter_title,
            **result
        }
    except Exception as e:
        print(f"  分析第{chapter_index + 1}章失败: {e}")
        return {
            "chapter_index": chapter_index,
            "chapter_title": chapter_title,
            "events": [],
            "interactions": [],
            "quote": "",
            "mood": "unknown",
            "error": str(e)
        }


def analyze_character_profile(
    character_name: str,
    appearances: list[dict],
    sample_contents: list[str],
) -> dict:
    """基于章节分析结果，生成人物总档案"""

    # 汇总关键信息
    all_events = []
    all_interactions = []
    all_quotes = []

    for app in appearances:
        all_events.extend(app.get("events", []))
        all_interactions.extend(app.get("interactions", []))
        if app.get("quote"):
            all_quotes.append(f"第{app['chapter_index']+1}章: {app['quote']}")

    # 取部分原文作为参考
    sample_text = "\n\n---\n\n".join(sample_contents[:3])[:10000]

    prompt = f"""基于以下信息，为人物「{character_name}」生成完整档案。

## 章节事件汇总
{json.dumps(all_events[:30], ensure_ascii=False, indent=2)}

## 人物互动汇总
{json.dumps(all_interactions[:30], ensure_ascii=False, indent=2)}

## 代表性描述
{json.dumps(all_quotes[:10], ensure_ascii=False, indent=2)}

## 原文片段参考
{sample_text}

请生成 JSON 格式的人物档案：
{{
    "name": "人物名字",
    "aliases": ["别名/称呼"],
    "description": "人物简介（100-200字）",
    "role": "protagonist/antagonist/supporting/minor",
    "personality": ["性格特点1", "性格特点2", "..."],
    "background": "人物背景（家庭、职业等）",
    "relations": [
        {{"target_name": "关系人名", "relation_type": "friend/enemy/lover/family/other", "description": "关系描述"}}
    ]
}}"""

    system = "你是一个专业的小说分析师。基于提供的信息生成准确的人物档案。"

    return chat_json(prompt, system, max_tokens=2000)


def main():
    """主函数"""
    book_id = "a04f9ba66252"
    character_name = "赵秦"

    # 配置路径
    chapters_dir = BOOKS_DIR / book_id / "chapters"
    output_dir = ANALYSIS_DIR / book_id / "characters" / character_name
    appearances_dir = output_dir / "appearances"

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    appearances_dir.mkdir(exist_ok=True)

    # 搜索所有包含该人物的章节
    print(f"搜索包含「{character_name}」的章节...")
    found_chapters = []

    for i in range(1, 7541):
        file_path = chapters_dir / f"{i:04d}.json"
        if file_path.exists():
            data = json.loads(file_path.read_text())
            if character_name in data["content"]:
                found_chapters.append({
                    "index": data["index"],
                    "title": data["title"],
                    "content": data["content"],
                    "mentions": data["content"].count(character_name)
                })

    print(f"找到 {len(found_chapters)} 个章节")

    # 采样策略：首次出现 + 高频章节 + 等距采样
    selected = []

    # 首次出现
    selected.append(found_chapters[0])

    # 高频 top 15
    by_mentions = sorted(found_chapters, key=lambda x: x["mentions"], reverse=True)
    for c in by_mentions[:15]:
        if c not in selected:
            selected.append(c)

    # 等距采样
    step = max(1, len(found_chapters) // 20)
    for i in range(0, len(found_chapters), step):
        if found_chapters[i] not in selected and len(selected) < 40:
            selected.append(found_chapters[i])

    # 按章节顺序排序
    selected = sorted(selected, key=lambda x: x["index"])

    print(f"选中 {len(selected)} 章进行分析")

    # 逐章分析
    appearances = []
    sample_contents = []

    for i, chapter in enumerate(selected):
        print(f"[{i+1}/{len(selected)}] 分析第{chapter['index']+1}章: {chapter['title']}")

        # 检查是否已分析过
        appearance_file = appearances_dir / f"{chapter['index']+1:04d}.json"
        if appearance_file.exists():
            print(f"  已存在，跳过")
            app = json.loads(appearance_file.read_text())
            appearances.append(app)
            sample_contents.append(chapter["content"][:5000])
            continue

        app = analyze_chapter_appearance(
            character_name,
            chapter["index"],
            chapter["title"],
            chapter["content"]
        )

        # 保存单章分析
        appearance_file.write_text(
            json.dumps(app, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        appearances.append(app)
        sample_contents.append(chapter["content"][:5000])

        # 避免 API 限流
        import time
        time.sleep(0.5)

    print(f"\n章节分析完成，共 {len(appearances)} 章")

    # 生成人物总档案
    print("\n生成人物总档案...")

    profile = analyze_character_profile(
        character_name,
        appearances,
        sample_contents[:5]
    )

    # 添加统计信息
    profile["first_appearance"] = found_chapters[0]["index"]
    profile["total_chapters"] = len(found_chapters)
    profile["total_mentions"] = sum(c["mentions"] for c in found_chapters)
    profile["analyzed_chapters"] = len(appearances)

    # 保存档案
    profile_file = output_dir / "profile.json"
    profile_file.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n完成！档案已保存到: {profile_file}")
    print(f"章节分析保存到: {appearances_dir}")

    # 输出简要信息
    print(f"\n=== {character_name} 人物档案 ===")
    print(f"角色: {profile.get('role', 'unknown')}")
    print(f"简介: {profile.get('description', '')[:100]}...")
    print(f"性格: {', '.join(profile.get('personality', []))}")
    print(f"出现章节: {profile['total_chapters']} 章")
    print(f"总提及: {profile['total_mentions']} 次")


if __name__ == "__main__":
    main()
