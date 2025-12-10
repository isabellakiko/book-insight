#!/usr/bin/env python3
"""继续分析赵秦 - 大批量分析脚本"""

import httpx
import json
import sys
from datetime import datetime

BOOK_ID = "a04f9ba66252"
CHARACTER_NAME = "赵秦"
ADDITIONAL_CHAPTERS = 200

def main():
    url = f"http://localhost:8000/api/analysis/{BOOK_ID}/characters/continue"
    params = {"name": CHARACTER_NAME, "additional_chapters": ADDITIONAL_CHAPTERS}

    print("=" * 60)
    print(f"赵秦大批量分析 - 新增 {ADDITIONAL_CHAPTERS} 章")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
    print()

    analyzed_count = 0
    start_time = datetime.now()

    try:
        with httpx.stream("GET", url, params=params, timeout=600.0) as response:
            if response.status_code != 200:
                print(f"错误: HTTP {response.status_code}")
                return

            current_event = None

            for line in response.iter_lines():
                line = line.strip()
                if not line:
                    continue

                if line.startswith("event:"):
                    current_event = line[6:].strip()
                elif line.startswith("data:"):
                    try:
                        data = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        continue

                    if current_event == "search_complete":
                        print(f"搜索完成: 赵秦出现在 {len(data['found_in_chapters'])} 章中")
                        print(f"总提及次数: {data['total_mentions']}")
                        print()

                    elif current_event == "continue_info":
                        print(f"已分析: {data['already_analyzed']} 章")
                        print(f"剩余待分析: {data['remaining']} 章")
                        print(f"本次将分析: {data['will_analyze']} 章")
                        print()
                        print("开始逐章分析...")
                        print("-" * 40)

                    elif current_event == "chapter_analyzed":
                        analyzed_count += 1
                        idx = data['chapter_index']
                        title = data['chapter_title']
                        # 简洁输出，每 10 章显示一次详情
                        if analyzed_count % 10 == 0:
                            elapsed = (datetime.now() - start_time).seconds
                            avg = elapsed / analyzed_count if analyzed_count > 0 else 0
                            remaining = (ADDITIONAL_CHAPTERS - analyzed_count) * avg
                            print(f"[{analyzed_count}/{ADDITIONAL_CHAPTERS}] 第{idx+1}章 {title}")
                            print(f"    已用时: {elapsed}秒, 预计剩余: {int(remaining)}秒")
                        else:
                            # 简洁进度指示
                            sys.stdout.write(".")
                            sys.stdout.flush()

                    elif current_event == "chapter_error":
                        print(f"\n警告: 第{data['chapter_index']+1}章分析失败: {data['error']}")

                    elif current_event == "relations_analyzed":
                        print(f"\n\n关系分析完成: {len(data['relations'])} 个关系")

                    elif current_event == "personality_analyzed":
                        print(f"性格分析完成: {data['role']}")
                        print(f"  描述: {data['description'][:50]}...")

                    elif current_event == "deep_profile_analyzed":
                        print(f"深度分析完成:")
                        print(f"  总结: {data['summary']}")
                        print(f"  成长轨迹: {data['growth_arc'][:50]}...")

                    elif current_event == "completed":
                        print()
                        print("=" * 60)
                        print("分析完成!")
                        print("=" * 60)

                        if "error" in data:
                            print(f"错误: {data['error']}")
                        else:
                            print(f"总分析章节: {len(data.get('analyzed_chapters', []))} 章")
                            print(f"出现记录数: {len(data.get('appearances', []))} 条")
                            print(f"人物关系: {len(data.get('relations', []))} 个")

                        elapsed = (datetime.now() - start_time).seconds
                        print(f"\n总耗时: {elapsed // 60}分{elapsed % 60}秒")

                    elif current_event == "info":
                        print(f"信息: {data.get('message', '')}")

    except httpx.TimeoutException:
        print("\n错误: 请求超时")
    except httpx.ConnectError:
        print("\n错误: 无法连接到服务器，请确认后端服务已启动")
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == "__main__":
    main()
