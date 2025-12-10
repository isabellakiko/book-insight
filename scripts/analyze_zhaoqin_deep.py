#!/usr/bin/env python3
"""对赵秦进行深度分析的脚本"""

import asyncio
import json
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))

from src.core.book import BookManager
from src.ai.tasks.character_analyzer import CharacterOnDemandAnalyzer
from src.knowledge.models import DetailedCharacter


async def main():
    book_id = "a04f9ba66252"
    character_name = "赵秦"

    print(f"=== 赵秦深度分析 ===\n")

    # 1. 获取已有分析结果
    existing = BookManager.get_detailed_character(book_id, character_name)
    if not existing:
        print("错误: 未找到赵秦的分析结果")
        return

    print(f"已有分析: {len(existing.analyzed_chapters)} 章")
    print(f"- 首次出场: 第 {existing.first_appearance + 1} 章")
    print(f"- 共出现: {existing.total_chapters} 章")
    print(f"- 当前描述: {existing.description[:50]}...")
    print(f"- 当前性格: {existing.personality}")
    print()

    # 2. 获取书籍
    book = BookManager.get_book(book_id)
    if not book:
        print("错误: 未找到书籍")
        return

    # 3. 执行深度分析
    analyzer = CharacterOnDemandAnalyzer()

    print("正在进行深度分析...")
    deep_profile = await analyzer.analyze_deep_profile(
        character_name,
        existing.appearances,
        existing.relations,
        existing.description,
        existing.personality,
    )

    print("\n=== 深度分析结果 ===\n")

    print(f"📝 一句话总结:")
    print(f"   {deep_profile['summary']}\n")

    print(f"📈 成长轨迹:")
    print(f"   {deep_profile['growth_arc']}\n")

    print(f"🎭 核心性格特征:")
    for i, trait in enumerate(deep_profile['core_traits'], 1):
        print(f"   {i}. {trait.trait}")
        print(f"      描述: {trait.description}")
        print(f"      证据: {trait.evidence}")
    print()

    print(f"✅ 优点: {deep_profile['strengths']}")
    print(f"❌ 缺点: {deep_profile['weaknesses']}")
    print()

    print(f"💬 经典语录:")
    for i, quote in enumerate(deep_profile['notable_quotes'], 1):
        print(f"   {i}. {quote}")
    print()

    # 4. 更新并保存
    updated = DetailedCharacter(
        name=existing.name,
        aliases=existing.aliases,
        description=existing.description,
        role=existing.role,
        personality=existing.personality,
        summary=deep_profile["summary"],
        growth_arc=deep_profile["growth_arc"],
        core_traits=deep_profile["core_traits"],
        strengths=deep_profile["strengths"],
        weaknesses=deep_profile["weaknesses"],
        notable_quotes=deep_profile["notable_quotes"],
        appearances=existing.appearances,
        first_appearance=existing.first_appearance,
        last_appearance=existing.last_appearance,
        total_chapters=existing.total_chapters,
        total_analyzed_chapters=len(existing.analyzed_chapters),
        relations=existing.relations,
        analysis_status="completed",
        analyzed_chapters=existing.analyzed_chapters,
    )

    BookManager.save_detailed_character(book_id, updated)
    print("✅ 深度分析结果已保存!")


if __name__ == "__main__":
    asyncio.run(main())
