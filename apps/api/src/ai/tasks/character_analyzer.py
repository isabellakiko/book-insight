"""Character on-demand analyzer."""

import re
from typing import AsyncGenerator

from ..client import chat_json
from ...knowledge.models import (
    CharacterSearchResult,
    DetailedCharacter,
    CharacterAppearance,
    CharacterRelation,
    CharacterTrait,
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

    async def analyze_deep_profile(
        self,
        character_name: str,
        appearances: list[CharacterAppearance],
        relations: list[CharacterRelation],
        description: str,
        personality: list[str],
    ) -> dict:
        """深度分析人物，生成 summary, growth_arc, core_traits, strengths, weaknesses, notable_quotes"""
        # 收集素材
        all_events = []
        all_quotes = []
        for app in appearances:
            for event in app.events:
                all_events.append(f"第{app.chapter_index + 1}章({app.chapter_title}): {event}")
            if app.quote:
                all_quotes.append(f"「{app.quote}」")

        relations_text = "\n".join([
            f"- {r.target_name}({r.relation_type}): {r.description}"
            for r in relations
        ])

        prompt = f"""基于以下信息，对人物"{character_name}"进行深度分析：

## 基本信息
简介：{description}
性格：{', '.join(personality)}

## 人物关系
{relations_text if relations_text else '暂无'}

## 主要事件（部分）
{chr(10).join(all_events[:30])}

## 台词/描述（部分）
{chr(10).join(all_quotes[:10])}

请以 JSON 格式返回：
{{
    "summary": "一句话概括这个人物（15-30字）",
    "growth_arc": "人物成长轨迹描述（100-200字），描述其从出场到现在的变化",
    "core_traits": [
        {{
            "trait": "性格特征名称",
            "description": "这个特征如何体现（一句话）",
            "evidence": "支撑证据（某章节的具体表现）"
        }}
    ],
    "strengths": ["优点1", "优点2", "优点3"],
    "weaknesses": ["缺点1", "缺点2"],
    "notable_quotes": ["最经典的语录1", "最经典的语录2", "最经典的语录3"]
}}

注意：
- core_traits 最多 5 个，按重要性排序
- notable_quotes 从已有台词中选择最能代表人物的 3-5 句
- 如果信息不足，可以返回空数组或简短描述
"""
        result = await chat_json(prompt, system="你是专业的小说人物分析师，擅长深度解读人物性格和成长轨迹。")

        # 解析 core_traits
        core_traits = []
        for t in result.get("core_traits", [])[:5]:
            if isinstance(t, dict):
                core_traits.append(CharacterTrait(
                    trait=t.get("trait", ""),
                    description=t.get("description", ""),
                    evidence=t.get("evidence", ""),
                ))

        return {
            "summary": result.get("summary", ""),
            "growth_arc": result.get("growth_arc", ""),
            "core_traits": core_traits,
            "strengths": result.get("strengths", [])[:5],
            "weaknesses": result.get("weaknesses", [])[:5],
            "notable_quotes": result.get("notable_quotes", [])[:5],
        }

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

        # 6. 深度分析
        deep_profile = await self.analyze_deep_profile(
            character_name, appearances, relations, description, personality
        )

        return DetailedCharacter(
            name=character_name,
            description=description,
            role=role,
            personality=personality,
            # 深度分析字段
            summary=deep_profile["summary"],
            growth_arc=deep_profile["growth_arc"],
            core_traits=deep_profile["core_traits"],
            strengths=deep_profile["strengths"],
            weaknesses=deep_profile["weaknesses"],
            notable_quotes=deep_profile["notable_quotes"],
            # 出现信息
            appearances=appearances,
            first_appearance=search_result.found_in_chapters[0],
            last_appearance=search_result.found_in_chapters[-1],
            total_chapters=len(search_result.found_in_chapters),
            total_analyzed_chapters=len(chapters_to_analyze),
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
        yield {
            "event": "personality_analyzed",
            "data": {"description": description, "personality": personality, "role": role},
        }

        # 6. 深度分析
        deep_profile = await self.analyze_deep_profile(
            character_name, appearances, relations, description, personality
        )
        yield {
            "event": "deep_profile_analyzed",
            "data": {
                "summary": deep_profile["summary"],
                "growth_arc": deep_profile["growth_arc"],
                "strengths": deep_profile["strengths"],
                "weaknesses": deep_profile["weaknesses"],
                "notable_quotes": deep_profile["notable_quotes"],
            },
        }

        # 7. 返回完整结果
        result = DetailedCharacter(
            name=character_name,
            description=description,
            role=role,
            personality=personality,
            # 深度分析字段
            summary=deep_profile["summary"],
            growth_arc=deep_profile["growth_arc"],
            core_traits=deep_profile["core_traits"],
            strengths=deep_profile["strengths"],
            weaknesses=deep_profile["weaknesses"],
            notable_quotes=deep_profile["notable_quotes"],
            # 出现信息
            appearances=appearances,
            first_appearance=search_result.found_in_chapters[0],
            last_appearance=search_result.found_in_chapters[-1],
            total_chapters=len(search_result.found_in_chapters),
            total_analyzed_chapters=len(appearances),
            relations=relations,
            analysis_status="completed",
            analyzed_chapters=[a.chapter_index for a in appearances],
        )

        yield {"event": "completed", "data": result.model_dump()}

    async def analyze_continue(
        self,
        book: Book,
        existing: DetailedCharacter,
        additional_chapters: int = 30,
    ) -> AsyncGenerator[dict, None]:
        """继续分析更多章节，基于已有分析结果"""
        character_name = existing.name

        # 1. 重新搜索获取完整章节列表
        search_result = self.search(book, character_name)
        yield {
            "event": "search_complete",
            "data": search_result.model_dump(),
        }

        if not search_result.found_in_chapters:
            yield {"event": "completed", "data": existing.model_dump()}
            return

        # 2. 找出尚未分析的章节
        analyzed_set = set(existing.analyzed_chapters)
        remaining = [c for c in search_result.found_in_chapters if c not in analyzed_set]

        if not remaining:
            yield {
                "event": "info",
                "data": {"message": "所有章节已分析完毕"},
            }
            yield {"event": "completed", "data": existing.model_dump()}
            return

        # 3. 取要分析的章节
        chapters_to_analyze = remaining[:additional_chapters]
        yield {
            "event": "continue_info",
            "data": {
                "already_analyzed": len(existing.analyzed_chapters),
                "remaining": len(remaining),
                "will_analyze": len(chapters_to_analyze),
            },
        }

        # 4. 复制已有的出现信息
        appearances = list(existing.appearances)

        # 5. 逐章分析新章节
        for idx in chapters_to_analyze:
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
                    "data": {"chapter_index": idx, "error": str(e)},
                }

        # 6. 重新分析关系（基于所有已分析章节）
        relations = await self.analyze_relations(character_name, appearances)
        yield {
            "event": "relations_analyzed",
            "data": {"relations": [r.model_dump() for r in relations]},
        }

        # 7. 重新分析性格
        description, personality, role = await self.analyze_personality(
            character_name, appearances
        )
        yield {
            "event": "personality_analyzed",
            "data": {"description": description, "personality": personality, "role": role},
        }

        # 8. 深度分析
        deep_profile = await self.analyze_deep_profile(
            character_name, appearances, relations, description, personality
        )
        yield {
            "event": "deep_profile_analyzed",
            "data": {
                "summary": deep_profile["summary"],
                "growth_arc": deep_profile["growth_arc"],
                "strengths": deep_profile["strengths"],
                "weaknesses": deep_profile["weaknesses"],
                "notable_quotes": deep_profile["notable_quotes"],
            },
        }

        # 9. 合并所有已分析章节
        all_analyzed = sorted(set(existing.analyzed_chapters) | set(chapters_to_analyze))

        # 10. 返回完整结果
        result = DetailedCharacter(
            name=character_name,
            aliases=existing.aliases,
            description=description,
            role=role,
            personality=personality,
            summary=deep_profile["summary"],
            growth_arc=deep_profile["growth_arc"],
            core_traits=deep_profile["core_traits"],
            strengths=deep_profile["strengths"],
            weaknesses=deep_profile["weaknesses"],
            notable_quotes=deep_profile["notable_quotes"],
            appearances=appearances,
            first_appearance=search_result.found_in_chapters[0],
            last_appearance=search_result.found_in_chapters[-1],
            total_chapters=len(search_result.found_in_chapters),
            total_analyzed_chapters=len(all_analyzed),
            relations=relations,
            analysis_status="completed",
            analyzed_chapters=all_analyzed,
        )

        yield {"event": "completed", "data": result.model_dump()}
