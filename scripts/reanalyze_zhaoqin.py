#!/usr/bin/env python3
"""重新分析赵秦 - 使用智能采样覆盖全书范围"""

import httpx
import json
import sys
from datetime import datetime

BOOK_ID = "a04f9ba66252"
CHARACTER_NAME = "赵秦"

def main():
    url = f"http://localhost:8000/api/analysis/{BOOK_ID}/characters/stream"
    params = {"name": CHARACTER_NAME}

    print("=" * 60)
    print(f"赵秦智能采样分析")
    print("=" * 60)
    print(f"采样策略: 均匀采样 30 章，覆盖 169-8098 章范围")
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
    print()

    analyzed_count = 0
    total_chapters = 30
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
                        first = data['found_in_chapters'][0] + 1
                        last = data['found_in_chapters'][-1] + 1
                        print(f"范围: 第{first}章 - 第{last}章")
                        print(f"总提及次数: {data['total_mentions']}")
                        print()
                        print("开始智能采样分析...")
                        print("-" * 40)

                    elif current_event == "chapter_analyzed":
                        analyzed_count += 1
                        idx = data['chapter_index']
                        title = data['chapter_title']

                        elapsed = (datetime.now() - start_time).seconds
                        avg = elapsed / analyzed_count if analyzed_count > 0 else 0
                        remaining = (total_chapters - analyzed_count) * avg

                        print(f"[{analyzed_count}/{total_chapters}] 第{idx+1}章 {title}")
                        if analyzed_count % 5 == 0:
                            print(f"    已用时: {elapsed}秒, 预计剩余: {int(remaining)}秒")

                    elif current_event == "chapter_error":
                        print(f"警告: 第{data['chapter_index']+1}章分析失败: {data['error']}")

                    elif current_event == "relations_analyzed":
                        print(f"\n关系分析完成: {len(data['relations'])} 个关系")
                        for r in data['relations'][:3]:
                            print(f"  - {r['target_name']}: {r['relation_type']}")

                    elif current_event == "personality_analyzed":
                        print(f"\n性格分析完成:")
                        print(f"  角色: {data['role']}")
                        print(f"  性格: {data['personality']}")

                    elif current_event == "deep_profile_analyzed":
                        print(f"\n深度分析完成:")
                        print(f"  总结: {data['summary']}")

                    elif current_event == "completed":
                        print()
                        print("=" * 60)
                        print("分析完成!")
                        print("=" * 60)

                        if "error" in data:
                            print(f"错误: {data['error']}")
                        else:
                            chapters = data.get('analyzed_chapters', [])
                            print(f"总分析章节: {len(chapters)} 章")
                            if chapters:
                                print(f"采样范围: 第{chapters[0]+1}章 - 第{chapters[-1]+1}章")
                            print(f"出现记录数: {len(data.get('appearances', []))} 条")
                            print(f"人物关系: {len(data.get('relations', []))} 个")

                        elapsed = (datetime.now() - start_time).seconds
                        print(f"\n总耗时: {elapsed // 60}分{elapsed % 60}秒")

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
