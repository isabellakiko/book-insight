#!/usr/bin/env python3
"""
数据格式迁移脚本

将旧格式 characters_detailed/{hash}.json 迁移到新格式 characters/{name}/profile.json

用法:
    python scripts/migrate_data.py [--dry-run] [--book-id BOOK_ID]
"""

import argparse
import json
import shutil
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ANALYSIS_DIR = DATA_DIR / "analysis"


def migrate_book(book_id: str, dry_run: bool = False) -> dict:
    """迁移单本书的人物数据"""
    book_dir = ANALYSIS_DIR / book_id
    if not book_dir.exists():
        return {"status": "skip", "reason": f"书籍目录不存在: {book_dir}"}

    old_dir = book_dir / "characters_detailed"
    new_dir = book_dir / "characters"

    if not old_dir.exists():
        return {"status": "skip", "reason": "无旧格式数据"}

    # 统计
    stats = {
        "status": "success",
        "migrated": [],
        "skipped": [],
        "errors": [],
    }

    # 确保新目录存在
    if not dry_run:
        new_dir.mkdir(parents=True, exist_ok=True)

    # 遍历旧格式文件
    for old_file in old_dir.glob("*.json"):
        try:
            data = json.loads(old_file.read_text(encoding="utf-8"))
            name = data.get("name")

            if not name:
                stats["errors"].append(f"{old_file.name}: 缺少 name 字段")
                continue

            # 检查新格式是否已存在
            char_dir = new_dir / name
            profile_path = char_dir / "profile.json"

            if profile_path.exists():
                stats["skipped"].append(f"{name}: 新格式已存在")
                continue

            # 迁移数据
            if not dry_run:
                char_dir.mkdir(parents=True, exist_ok=True)

                # 确保 analysis_status 字段存在
                if "analysis_status" not in data:
                    data["analysis_status"] = "completed"

                # 写入新格式
                profile_path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )

            stats["migrated"].append(name)
            print(f"  {'[DRY-RUN] ' if dry_run else ''}迁移: {name}")

        except Exception as e:
            stats["errors"].append(f"{old_file.name}: {str(e)}")

    # 更新 characters.json 索引
    if stats["migrated"] and not dry_run:
        update_characters_index(book_id, stats["migrated"])

    return stats


def update_characters_index(book_id: str, new_names: list[str]) -> None:
    """更新 characters.json 索引"""
    book_dir = ANALYSIS_DIR / book_id
    index_path = book_dir / "characters.json"

    # 读取现有索引
    characters = []
    if index_path.exists():
        characters = json.loads(index_path.read_text(encoding="utf-8"))

    existing_names = {c.get("name") for c in characters}

    # 为新迁移的人物添加索引条目
    for name in new_names:
        if name in existing_names:
            continue

        # 从 profile.json 读取基础信息
        profile_path = book_dir / "characters" / name / "profile.json"
        if profile_path.exists():
            data = json.loads(profile_path.read_text(encoding="utf-8"))
            characters.append({
                "name": name,
                "aliases": data.get("aliases", []),
                "description": data.get("description", ""),
                "first_appearance": data.get("first_appearance", 0),
                "role": data.get("role", "supporting"),
            })

    # 保存更新后的索引
    index_path.write_text(
        json.dumps(characters, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"  更新 characters.json: 新增 {len(new_names)} 个人物")


def cleanup_old_format(book_id: str, dry_run: bool = False) -> None:
    """清理旧格式目录"""
    old_dir = ANALYSIS_DIR / book_id / "characters_detailed"

    if not old_dir.exists():
        return

    if dry_run:
        print(f"  [DRY-RUN] 将删除: {old_dir}")
    else:
        shutil.rmtree(old_dir)
        print(f"  已删除: {old_dir}")


def main():
    parser = argparse.ArgumentParser(description="迁移人物数据格式")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际执行")
    parser.add_argument("--book-id", help="指定书籍 ID，不指定则迁移所有")
    parser.add_argument("--cleanup", action="store_true", help="迁移后删除旧格式目录")
    args = parser.parse_args()

    print("=" * 60)
    print("Book Insight 数据格式迁移")
    print("=" * 60)
    print()

    if args.dry_run:
        print("[DRY-RUN 模式] 不会实际修改任何文件")
        print()

    # 确定要迁移的书籍
    if args.book_id:
        book_ids = [args.book_id]
    else:
        book_ids = [d.name for d in ANALYSIS_DIR.iterdir() if d.is_dir()]

    if not book_ids:
        print("未找到任何书籍数据")
        return

    # 执行迁移
    total_migrated = 0
    for book_id in book_ids:
        print(f"\n[{book_id}]")
        result = migrate_book(book_id, args.dry_run)

        if result["status"] == "skip":
            print(f"  跳过: {result['reason']}")
            continue

        if result["migrated"]:
            total_migrated += len(result["migrated"])

        if result["skipped"]:
            for msg in result["skipped"]:
                print(f"  跳过: {msg}")

        if result["errors"]:
            for msg in result["errors"]:
                print(f"  错误: {msg}")

        # 清理旧格式
        if args.cleanup and result["migrated"]:
            cleanup_old_format(book_id, args.dry_run)

    # 总结
    print()
    print("=" * 60)
    print(f"迁移完成: 共迁移 {total_migrated} 个人物")
    if not args.cleanup:
        print("提示: 使用 --cleanup 参数可删除旧格式目录")
    print("=" * 60)


if __name__ == "__main__":
    main()
