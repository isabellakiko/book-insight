"""Character on-demand analyzer."""

import re
from typing import AsyncGenerator

from ..client import chat_json
from ...knowledge.models import (
    CharacterSearchResult,
    DetailedCharacter,
    CharacterAppearance,
    CharacterRelation,
)
from ...core.book import Book


class CharacterOnDemandAnalyzer:
    """按需分析单个人物"""

    def search(self, book: Book, character_name: str) -> CharacterSearchResult:
        """搜索人物出现的所有章节（纯文本搜索，快速）"""
        pattern = re.compile(re.escape(character_name))

        found_chapters = []
        chapter_titles = []
        total_mentions = 0

        for chapter in book.chapters:
            content = book.content[chapter.start:chapter.end + 1]
            matches = pattern.findall(content)
            if matches:
                found_chapters.append(chapter.index)
                chapter_titles.append(chapter.title)
                total_mentions += len(matches)

        return CharacterSearchResult(
            name=character_name,
            found_in_chapters=found_chapters,
            chapter_titles=chapter_titles,
            total_mentions=total_mentions,
        )

    async def analyze_chapter_appearance(
        self,
        character_name: str,
        chapter_index: int,
        chapter_title: str,
        content: str,
    ) -> CharacterAppearance:
        """分析人物在单个章节的表现"""
        # 截断过长内容
        if len(content) > 15000:
            content = content[:15000]

        prompt = f"""分析人物"{character_name}"在以下章节中的表现：

章节：{chapter_title}
内容：
{content}

请以 JSON 格式返回：
{{
    "events": ["该人物在本章参与的事件，每个事件一句话，最多3个"],
    "interactions": ["与其他人物的互动，格式：与XX的互动描述，最多3个"],
    "quote": "最能体现该人物的一句台词或描述（如没有则为空字符串）"
}}

注意：如果该人物在本章只是被提及而没有实际出场，events 可以为空。
"""
        result = await chat_json(prompt, system="你是小说分析专家。简洁回答。")

        return CharacterAppearance(
            chapter_index=chapter_index,
            chapter_title=chapter_title,
            events=result.get("events", [])[:3],
            interactions=result.get("interactions", [])[:3],
            quote=result.get("quote", ""),
        )

    async def analyze_relations(
        self,
        character_name: str,
        appearances: list[CharacterAppearance],
    ) -> list[CharacterRelation]:
        """基于所有章节分析人物关系"""
        # 汇总所有互动信息
        all_interactions = []
        for app in appearances:
            for interaction in app.interactions:
                all_interactions.append(f"第{app.chapter_index + 1}章：{interaction}")

        if not all_interactions:
            return []

        # 限制数量
        interactions_text = "\n".join(all_interactions[:30])

        prompt = f"""基于以下互动记录，分析人物"{character_name}"的人物关系：

{interactions_text}

请以 JSON 格式返回：
{{
    "relations": [
        {{
            "target_name": "关系对象姓名",
            "relation_type": "friend/enemy/lover/family/mentor/rival",
            "description": "关系描述（一句话）"
        }}
    ]
}}

最多返回 5 个最重要的关系。
"""
        result = await chat_json(prompt, system="你是小说分析专家。")

        return [
            CharacterRelation(
                target_name=r.get("target_name", ""),
                relation_type=r.get("relation_type", "unknown"),
                description=r.get("description", ""),
                evidence_chapters=[],
            )
            for r in result.get("relations", [])[:5]
        ]

    async def analyze_personality(
        self,
        character_name: str,
        appearances: list[CharacterAppearance],
    ) -> tuple[str, list[str], str]:
        """分析人物性格，返回 (description, personality, role)"""
        # 收集事件和台词
        events_summary = []
        quotes = []
        for app in appearances[:15]:
            events_summary.extend(app.events[:2])
            if app.quote:
                quotes.append(app.quote)

        prompt = f"""基于以下信息，分析人物"{character_name}"的性格特点：

主要事件：
{chr(10).join(events_summary[:20])}

代表性台词/描述：
{chr(10).join(quotes[:5])}

请以 JSON 格式返回：
{{
    "description": "人物简介，50-100字",
    "personality": ["性格特点关键词，如：勇敢、机智、冷酷等，最多5个"],
    "role": "角色定位：protagonist/antagonist/supporting/minor"
}}
"""
        result = await chat_json(prompt, system="你是小说分析专家。")

        return (
            result.get("description", ""),
            result.get("personality", [])[:5],
            result.get("role", "unknown"),
        )

    async def analyze_full(
        self,
        book: Book,
        character_name: str,
        max_chapters: int = 30,
    ) -> DetailedCharacter:
        """完整分析流程"""
        # 1. 搜索
        search_result = self.search(book, character_name)

        if not search_result.found_in_chapters:
            return DetailedCharacter(
                name=character_name,
                analysis_status="completed",
                error_message="未找到该人物",
            )

        # 2. 限制分析章节数
        chapters_to_analyze = search_result.found_in_chapters[:max_chapters]

        # 3. 分析每个章节
        appearances = []
        for idx in chapters_to_analyze:
            chapter = book.chapters[idx]
            content = book.content[chapter.start:chapter.end + 1]
            app = await self.analyze_chapter_appearance(
                character_name, idx, chapter.title, content
            )
            appearances.append(app)

        # 4. 分析关系
        relations = await self.analyze_relations(character_name, appearances)

        # 5. 分析性格
        description, personality, role = await self.analyze_personality(
            character_name, appearances
        )

        return DetailedCharacter(
            name=character_name,
            description=description,
            role=role,
            personality=personality,
            appearances=appearances,
            first_appearance=search_result.found_in_chapters[0],
            total_chapters=len(search_result.found_in_chapters),
            relations=relations,
            analysis_status="completed",
            analyzed_chapters=chapters_to_analyze,
        )

    async def analyze_stream(
        self,
        book: Book,
        character_name: str,
        max_chapters: int = 30,
    ) -> AsyncGenerator[dict, None]:
        """流式分析，逐步产出结果"""
        # 1. 搜索
        search_result = self.search(book, character_name)
        yield {
            "event": "search_complete",
            "data": search_result.model_dump(),
        }

        if not search_result.found_in_chapters:
            yield {
                "event": "completed",
                "data": {"error": "未找到该人物"},
            }
            return

        # 2. 限制章节数
        chapters = search_result.found_in_chapters[:max_chapters]
        appearances = []

        # 3. 逐章分析
        for idx in chapters:
            chapter = book.chapters[idx]
            content = book.content[chapter.start:chapter.end + 1]

            try:
                app = await self.analyze_chapter_appearance(
                    character_name, idx, chapter.title, content
                )
                appearances.append(app)

                yield {
                    "event": "chapter_analyzed",
                    "data": {
                        "chapter_index": idx,
                        "chapter_title": chapter.title,
                        "appearance": app.model_dump(),
                    },
                }
            except Exception as e:
                yield {
                    "event": "chapter_error",
                    "data": {
                        "chapter_index": idx,
                        "error": str(e),
                    },
                }

        # 4. 分析关系
        relations = await self.analyze_relations(character_name, appearances)
        yield {
            "event": "relations_analyzed",
            "data": {"relations": [r.model_dump() for r in relations]},
        }

        # 5. 分析性格
        description, personality, role = await self.analyze_personality(
            character_name, appearances
        )

        # 6. 返回完整结果
        result = DetailedCharacter(
            name=character_name,
            description=description,
            role=role,
            personality=personality,
            appearances=appearances,
            first_appearance=search_result.found_in_chapters[0],
            total_chapters=len(search_result.found_in_chapters),
            relations=relations,
            analysis_status="completed",
            analyzed_chapters=[a.chapter_index for a in appearances],
        )

        yield {"event": "completed", "data": result.model_dump()}
