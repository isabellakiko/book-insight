#!/usr/bin/env python3
"""赵秦分析数据修复脚本

修复问题：
1. analyzed_chapters 和 appearances 数据不同步
2. 标记虚假出场记录（无 events 且无 interactions）

运行：python scripts/fix_zhaoqin_data.py
"""

import json
from pathlib import Path

PROFILE_PATH = Path("data/analysis/a04f9ba66252/characters/赵秦/profile.json")


def fix_data():
    """修复赵秦分析数据"""
    print("=" * 60)
    print("  赵秦分析数据修复")
    print("=" * 60)

    # 读取数据
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        profile = json.load(f)

    analyzed_chapters = set(profile.get("analyzed_chapters", []))
    appearances = profile.get("appearances", [])
    appearance_chapters = {a["chapter_index"] for a in appearances}

    print(f"\n原始数据:")
    print(f"  analyzed_chapters: {len(analyzed_chapters)} 章")
    print(f"  appearances: {len(appearances)} 章")

    # 1. 找出不同步的章节
    missing_in_appearances = analyzed_chapters - appearance_chapters
    extra_in_appearances = appearance_chapters - analyzed_chapters

    if missing_in_appearances:
        print(f"\n问题 1: analyzed_chapters 中有但 appearances 中没有的章节:")
        print(f"  {sorted(missing_in_appearances)}")
        print(f"  将从 analyzed_chapters 中移除这些章节")

    if extra_in_appearances:
        print(f"\n问题 2: appearances 中有但 analyzed_chapters 中没有的章节:")
        print(f"  {sorted(extra_in_appearances)}")

    # 2. 修复：只保留在 appearances 中的章节
    fixed_analyzed = sorted(appearance_chapters)

    # 3. 标记虚假出场记录
    mentioned_only_count = 0
    actual_appearance_count = 0

    for app in appearances:
        events = app.get("events", [])
        interactions = app.get("interactions", [])

        if not events and not interactions:
            app["is_mentioned_only"] = True
            mentioned_only_count += 1
        else:
            app["is_mentioned_only"] = False
            actual_appearance_count += 1

    print(f"\n问题 3: 虚假出场记录（无 events 且无 interactions）:")
    print(f"  仅被提及: {mentioned_only_count} 章")
    print(f"  实际出场: {actual_appearance_count} 章")

    # 4. 更新 profile
    profile["analyzed_chapters"] = fixed_analyzed
    profile["total_analyzed_chapters"] = len(fixed_analyzed)

    # 5. 保存
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    print(f"\n修复完成:")
    print(f"  analyzed_chapters: {len(fixed_analyzed)} 章")
    print(f"  appearances: {len(appearances)} 章")
    print(f"  is_mentioned_only 已标记: {mentioned_only_count} 条")

    # 6. 验证
    if len(fixed_analyzed) == len(appearances):
        print(f"\n✓ 数据同步验证通过")
    else:
        print(f"\n✗ 数据同步验证失败！")

    return missing_in_appearances


if __name__ == "__main__":
    missing = fix_data()
    if missing:
        print(f"\n需要重新分析的章节: {sorted(missing)}")
        print(f"运行: python scripts/analyze.py 赵秦 --continue --chapters {len(missing) + 5}")
