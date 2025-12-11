#!/usr/bin/env python3
"""
人物分析统一 CLI

通过 HTTP 调用后端 API，不直接访问文件系统。

用法:
    # 智能采样分析（新人物）
    python scripts/analyze.py 赵秦

    # 增量分析（交互式，会询问章节数和是否刷新总结）
    python scripts/analyze.py 赵秦 --continue

    # 增量分析（非交互式，指定章节数）
    python scripts/analyze.py 赵秦 --continue --chapters 100

    # 增量分析并刷新总结
    python scripts/analyze.py 赵秦 --continue --chapters 50 --refresh-summary

    # 仅刷新总结（不分析新章节）
    python scripts/analyze.py 赵秦 --refresh-summary-only

    # 查看人物当前状态
    python scripts/analyze.py 赵秦 --status

    # 批量分析多个人物
    python scripts/analyze.py 张成 赵秦 夏诗

    # 指定书籍 ID
    python scripts/analyze.py 赵秦 --book-id a04f9ba66252
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


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """询问是/否问题"""
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        response = input(f"{prompt} {suffix}: ").strip().lower()
        if response == "":
            return default
        if response in ("y", "yes", "是"):
            return True
        if response in ("n", "no", "否"):
            return False
        print("请输入 y 或 n")


def ask_number(prompt: str, default: int, min_val: int = 1, max_val: int = 1000) -> int:
    """询问数字"""
    while True:
        response = input(f"{prompt} [默认 {default}]: ").strip()
        if response == "":
            return default
        try:
            value = int(response)
            if min_val <= value <= max_val:
                return value
            print(f"请输入 {min_val} - {max_val} 之间的数字")
        except ValueError:
            print("请输入有效数字")


def analyze_character(
    client: APIClient,
    book_id: str,
    name: str,
    continue_mode: bool = False,
    additional_chapters: int | None = None,
    refresh_summary: bool = False,
    interactive: bool = True,
) -> bool:
    """分析单个人物

    Args:
        client: API 客户端
        book_id: 书籍 ID
        name: 人物名称
        continue_mode: 是否为增量分析模式
        additional_chapters: 要分析的章节数（None 表示交互式询问）
        refresh_summary: 是否刷新总结字段
        interactive: 是否允许交互式询问
    """
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
        remaining = total - analyzed

        print(f"当前状态: 已分析 {analyzed}/{total} 章 ({analyzed/total*100:.1f}%)")
        print(f"剩余未分析: {remaining} 章")
        print()

        # 交互式询问章节数
        if additional_chapters is None:
            if interactive and remaining > 0:
                additional_chapters = ask_number(
                    "本次分析多少章？",
                    default=min(50, remaining),
                    min_val=1,
                    max_val=remaining
                )
            else:
                additional_chapters = min(100, remaining)

        print(f"本次将分析 {additional_chapters} 章")
        print()

        # 调用继续分析 API
        stream = client.stream_continue_analysis(
            book_id, name, additional_chapters, refresh_summary
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
        analysis_completed = False
        final_data = None

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
                if event.data.get('refresh_summary'):
                    print("总结字段: 将会刷新")
                else:
                    print("总结字段: 保持不变")

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

            elif event.event == "summary_skipped":
                print()  # 换行
                print(f"提示: {event.data.get('message', '总结字段保持不变')}")

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
                final_data = final
                print(f"人物: {final.get('name')}")
                print(f"角色: {final.get('role')}")
                print(f"出现章节: {final.get('first_appearance')} - {final.get('last_appearance')}")
                print(f"已分析章节: {len(final.get('analyzed_chapters', []))}")
                analysis_completed = True

            elif event.event == "error":
                print()
                print(f"错误: {event.data.get('message', '未知错误')}")
                return False

        # 增量分析完成后，询问是否刷新总结（仅在未刷新时询问）
        if continue_mode and analysis_completed and not refresh_summary and interactive:
            print()
            new_analyzed = len(final_data.get('analyzed_chapters', [])) if final_data else 0
            new_total = final_data.get('total_chapters', 0) if final_data else 0

            if new_analyzed < new_total:
                # 还有未分析的章节
                print(f"当前进度: {new_analyzed}/{new_total} 章 ({new_analyzed/new_total*100:.1f}%)")
                print()

                if ask_yes_no("是否刷新总结字段（基于已分析的章节重新生成）？", default=False):
                    print()
                    print("正在刷新总结...")
                    # 调用刷新总结（分析 0 章但刷新总结）
                    refresh_stream = client.stream_continue_analysis(
                        book_id, name, 0, refresh_summary=True
                    )
                    for event in refresh_stream:
                        if event.event == "relations_analyzed":
                            print("  关系分析完成")
                        elif event.event == "personality_analyzed":
                            print("  性格分析完成")
                        elif event.event == "deep_profile_analyzed":
                            print("  深度分析完成")
                        elif event.event == "completed":
                            print("  总结刷新完成！")

        return analysis_completed

    except KeyboardInterrupt:
        print("\n\n分析已取消")
        return False
    except Exception as e:
        print(f"\n错误: {str(e)}")
        return False


def refresh_summary_only(client: APIClient, book_id: str, name: str) -> bool:
    """仅刷新总结（不分析新章节）"""
    print_header(f"刷新总结: {name}")

    # 检查 API 健康
    if not client.check_health():
        print("错误: 后端 API 未启动，请先运行 pnpm dev")
        return False

    # 检查现有分析
    existing = client.get_detailed_character(book_id, name)
    if not existing:
        print(f"错误: {name} 尚未分析，请先执行初始分析")
        return False

    analyzed = len(existing.get("analyzed_chapters", []))
    print(f"当前已分析: {analyzed} 章")
    print("正在基于已分析章节重新生成总结...")
    print()

    try:
        # 分析 0 章但刷新总结
        stream = client.stream_continue_analysis(
            book_id, name, additional_chapters=0, refresh_summary=True
        )

        for event in stream:
            if event.event == "relations_analyzed":
                relations = event.data.get("relations", [])
                print(f"关系分析完成: {len(relations)} 个关系")

            elif event.event == "personality_analyzed":
                role = event.data.get("role", "unknown")
                personality = event.data.get("personality", [])
                print(f"性格分析完成: {role}")
                print(f"  特点: {', '.join(personality[:5])}")

            elif event.event == "deep_profile_analyzed":
                summary = event.data.get("summary", "")
                print(f"深度分析完成")
                if summary:
                    print(f"  简介: {summary}")

            elif event.event == "completed":
                print()
                print("总结刷新完成！")
                return True

            elif event.event == "error":
                print(f"错误: {event.data.get('message', '未知错误')}")
                return False

    except KeyboardInterrupt:
        print("\n\n操作已取消")
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
    coverage = len(analyzed) / len(found) * 100
    print(f"分析状态: 已分析 {len(analyzed)}/{len(found)} 章 ({coverage:.1f}%)")
    print()

    # 显示摘要信息
    if existing.get("summary"):
        print(f"简介: {existing['summary']}")
    if existing.get("role"):
        print(f"角色: {existing['role']}")
    if existing.get("personality"):
        print(f"性格: {', '.join(existing['personality'][:5])}")
    if existing.get("growth_arc"):
        print(f"成长轨迹: {existing['growth_arc'][:100]}...")

    print()
    print("可用命令:")
    print(f"  python scripts/analyze.py {name} --continue           # 继续分析（交互式）")
    print(f"  python scripts/analyze.py {name} --refresh-summary-only  # 仅刷新总结")


def main():
    parser = argparse.ArgumentParser(
        description="人物分析 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/analyze.py 赵秦              # 智能采样分析
  python scripts/analyze.py 赵秦 --continue   # 继续分析（交互式询问章节数）
  python scripts/analyze.py 赵秦 --continue --chapters 50  # 继续分析 50 章
  python scripts/analyze.py 赵秦 --continue --chapters 50 --refresh-summary  # 分析并刷新总结
  python scripts/analyze.py 赵秦 --refresh-summary-only  # 仅刷新总结
  python scripts/analyze.py 赵秦 --status     # 查看分析状态
  python scripts/analyze.py 张成 赵秦 夏诗    # 批量分析
        """
    )

    parser.add_argument("names", nargs="+", help="要分析的人物名")
    parser.add_argument("--book-id", default=DEFAULT_BOOK_ID, help="书籍 ID")
    parser.add_argument("--continue", dest="continue_mode", action="store_true",
                        help="继续分析已有人物的更多章节（交互式询问章节数）")
    parser.add_argument("--chapters", type=int, default=None,
                        help="继续分析时的章节数（不指定则交互式询问）")
    parser.add_argument("--refresh-summary", dest="refresh_summary", action="store_true",
                        help="分析完成后刷新总结字段")
    parser.add_argument("--refresh-summary-only", dest="refresh_summary_only", action="store_true",
                        help="仅刷新总结（不分析新章节）")
    parser.add_argument("--status", action="store_true", help="查看人物分析状态")
    parser.add_argument("--no-interactive", dest="no_interactive", action="store_true",
                        help="禁用交互式询问")
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

    interactive = not args.no_interactive

    # 处理每个人物
    success_count = 0
    for name in args.names:
        if args.status:
            show_status(client, args.book_id, name)
        elif args.refresh_summary_only:
            if refresh_summary_only(client, args.book_id, name):
                success_count += 1
        else:
            if analyze_character(
                client,
                args.book_id,
                name,
                continue_mode=args.continue_mode,
                additional_chapters=args.chapters,
                refresh_summary=args.refresh_summary,
                interactive=interactive,
            ):
                success_count += 1

    # 总结
    if not args.status and len(args.names) > 1:
        print()
        print(f"完成: {success_count}/{len(args.names)} 个人物分析成功")


if __name__ == "__main__":
    main()
