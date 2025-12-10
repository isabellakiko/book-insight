#!/usr/bin/env python3
"""
人物分析统一 CLI

通过 HTTP 调用后端 API，不直接访问文件系统。

用法:
    # 智能采样分析（新人物）
    python scripts/analyze.py 赵秦

    # 增量分析（已有人物）
    python scripts/analyze.py 赵秦 --continue --chapters 100

    # 批量分析多个人物
    python scripts/analyze.py 张成 赵秦 夏诗

    # 指定书籍 ID
    python scripts/analyze.py 赵秦 --book-id a04f9ba66252

    # 查看人物当前状态
    python scripts/analyze.py 赵秦 --status
"""

import argparse
import sys
from pathlib import Path

# 添加 lib 到路径
sys.path.insert(0, str(Path(__file__).parent))

from lib.api_client import APIClient


# 默认书籍 ID（那些热血飞扬的日子）
DEFAULT_BOOK_ID = "a04f9ba66252"


def print_header(title: str) -> None:
    """打印标题"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def print_progress(current: int, total: int, prefix: str = "") -> None:
    """打印进度条"""
    width = 40
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percent = current / total * 100
    print(f"\r{prefix}[{bar}] {percent:.1f}% ({current}/{total})", end="", flush=True)


def analyze_character(
    client: APIClient,
    book_id: str,
    name: str,
    continue_mode: bool = False,
    additional_chapters: int = 100,
) -> bool:
    """分析单个人物"""
    print_header(f"{'继续分析' if continue_mode else '分析人物'}: {name}")

    # 检查 API 健康
    if not client.check_health():
        print("错误: 后端 API 未启动，请先运行 pnpm dev")
        return False

    # 检查现有分析
    existing = client.get_detailed_character(book_id, name)

    if continue_mode:
        if not existing:
            print(f"错误: {name} 尚未分析，请先执行初始分析")
            return False

        analyzed = len(existing.get("analyzed_chapters", []))
        total = existing.get("total_chapters", 0)
        print(f"当前状态: 已分析 {analyzed}/{total} 章")
        print(f"本次将继续分析 {additional_chapters} 章")
        print()

        # 调用继续分析 API
        stream = client.stream_continue_analysis(
            book_id, name, additional_chapters
        )
    else:
        if existing:
            analyzed = len(existing.get("analyzed_chapters", []))
            total = existing.get("total_chapters", 0)
            print(f"注意: {name} 已有分析数据 ({analyzed}/{total} 章)")
            print("将使用智能采样重新分析")
            print()

        # 调用流式分析 API
        stream = client.stream_analyze_character(book_id, name)

    # 处理 SSE 事件
    try:
        chapters_analyzed = 0
        total_chapters = 0

        for event in stream:
            if event.event == "search_complete":
                total_chapters = event.data.get("total_chapters", 0)
                found = event.data.get("found_in_chapters", 0)
                if isinstance(found, list):
                    found = len(found)
                print(f"搜索完成: 在 {found} 章中出现")

            elif event.event == "continue_info":
                print(f"剩余未分析: {event.data.get('remaining', 0)} 章")
                print(f"本次分析: {event.data.get('will_analyze', 0)} 章")

            elif event.event == "sample_info":
                sample = event.data.get("sample_chapters", [])
                if sample:
                    print(f"智能采样: {len(sample)} 章")
                    print(f"  范围: {min(sample)} - {max(sample)}")

            elif event.event == "chapter_analyzed":
                chapters_analyzed += 1
                to_analyze = event.data.get("chapters_to_analyze", total_chapters)
                if to_analyze > 0:
                    print_progress(chapters_analyzed, to_analyze, "分析进度: ")

            elif event.event == "relations_analyzed":
                print()  # 换行
                relations = event.data.get("relations", [])
                print(f"关系分析完成: 发现 {len(relations)} 个关系")
                for rel in relations[:5]:  # 显示前5个
                    print(f"  - {rel.get('target_name')}: {rel.get('relation_type')}")

            elif event.event == "personality_analyzed":
                personality = event.data.get("personality", [])
                role = event.data.get("role", "unknown")
                print(f"性格分析完成: {role}")
                print(f"  性格特点: {', '.join(personality[:5])}")

            elif event.event == "deep_profile_analyzed":
                summary = event.data.get("summary", "")
                print(f"深度分析完成")
                if summary:
                    print(f"  简介: {summary[:50]}...")

            elif event.event == "completed":
                print()
                print_header("分析完成")
                final = event.data
                print(f"人物: {final.get('name')}")
                print(f"角色: {final.get('role')}")
                print(f"出现章节: {final.get('first_appearance')} - {final.get('last_appearance')}")
                print(f"已分析章节: {len(final.get('analyzed_chapters', []))}")
                return True

            elif event.event == "error":
                print()
                print(f"错误: {event.data.get('message', '未知错误')}")
                return False

    except KeyboardInterrupt:
        print("\n\n分析已取消")
        return False
    except Exception as e:
        print(f"\n错误: {str(e)}")
        return False

    return True


def show_status(client: APIClient, book_id: str, name: str) -> None:
    """显示人物分析状态"""
    print_header(f"人物状态: {name}")

    # 先搜索
    search = client.search_character(book_id, name)
    found = search.get("found_in_chapters", [])

    if not found:
        print(f"在书中未找到 '{name}'")
        return

    print(f"出现章节: {len(found)} 章")
    print(f"首次出场: 第 {min(found) + 1} 章")
    print(f"最后出场: 第 {max(found) + 1} 章")
    print()

    # 检查已有分析
    existing = client.get_detailed_character(book_id, name)

    if not existing:
        print("分析状态: 尚未分析")
        print()
        print("运行以下命令开始分析:")
        print(f"  python scripts/analyze.py {name}")
        return

    analyzed = existing.get("analyzed_chapters", [])
    print(f"分析状态: 已分析 {len(analyzed)}/{len(found)} 章 ({len(analyzed)/len(found)*100:.1f}%)")
    print()

    # 显示摘要信息
    if existing.get("summary"):
        print(f"简介: {existing['summary']}")
    if existing.get("role"):
        print(f"角色: {existing['role']}")
    if existing.get("personality"):
        print(f"性格: {', '.join(existing['personality'][:5])}")

    print()
    print("继续分析:")
    print(f"  python scripts/analyze.py {name} --continue --chapters 100")


def main():
    parser = argparse.ArgumentParser(
        description="人物分析 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/analyze.py 赵秦              # 智能采样分析
  python scripts/analyze.py 赵秦 --continue   # 继续分析更多章节
  python scripts/analyze.py 赵秦 --status     # 查看分析状态
  python scripts/analyze.py 张成 赵秦 夏诗    # 批量分析
        """
    )

    parser.add_argument("names", nargs="+", help="要分析的人物名")
    parser.add_argument("--book-id", default=DEFAULT_BOOK_ID, help="书籍 ID")
    parser.add_argument("--continue", dest="continue_mode", action="store_true",
                        help="继续分析已有人物的更多章节")
    parser.add_argument("--chapters", type=int, default=100,
                        help="继续分析时的章节数 (默认 100)")
    parser.add_argument("--status", action="store_true", help="查看人物分析状态")
    parser.add_argument("--api-url", default="http://localhost:8000",
                        help="API 地址 (默认 http://localhost:8000)")

    args = parser.parse_args()

    client = APIClient(args.api_url)

    # 检查 API
    if not client.check_health():
        print("错误: 后端 API 未启动")
        print("请先运行: pnpm dev")
        sys.exit(1)

    # 检查书籍
    book = client.get_book(args.book_id)
    if not book:
        print(f"错误: 书籍 {args.book_id} 不存在")
        sys.exit(1)

    print(f"书籍: {book.get('title', args.book_id)}")

    # 处理每个人物
    success_count = 0
    for name in args.names:
        if args.status:
            show_status(client, args.book_id, name)
        else:
            if analyze_character(
                client,
                args.book_id,
                name,
                continue_mode=args.continue_mode,
                additional_chapters=args.chapters,
            ):
                success_count += 1

    # 总结
    if not args.status and len(args.names) > 1:
        print()
        print(f"完成: {success_count}/{len(args.names)} 个人物分析成功")


if __name__ == "__main__":
    main()
