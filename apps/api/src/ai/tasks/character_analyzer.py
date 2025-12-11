"""Character on-demand analyzer."""

import asyncio
import re
from typing import AsyncGenerator

from ..client import chat_json
from ...config import settings
from ...knowledge.models import (
    CharacterSearchResult,
    DetailedCharacter,
    CharacterAppearance,
    CharacterInteraction,
    CharacterRelation,
    CharacterTrait,
)
from ...core.book import Book
from ...utils.logger import get_logger

logger = get_logger(__name__)


class CharacterOnDemandAnalyzer:
    """按需分析单个人物

    重要说明：本小说《那些热血飞扬的日子》采用第一人称视角，
    叙述者为主角"张成"。分析其他人物时需注意：
    - 所有描写都是从张成视角观察的
    - 其他人物的内心活动是张成的推测，非客观事实
    - 需要区分"张成的主观印象"和"客观行为/对话"
    """

    # 第一人称视角提示词（用于所有 prompt）
    FIRST_PERSON_CONTEXT = """
【重要背景】
这是一部第一人称小说，叙述者是主角"张成"。你正在分析的内容都是从张成的视角描写的。

分析时请注意区分：
1. **客观事实**：人物的对话、具体行为、外貌描写
2. **主观推测**：张成对该人物心理、动机的猜测（如"她可能在想..."、"看起来她..."）
3. **关系偏差**：张成与该人物的关系会影响描写的倾向性

分析原则：
- 优先采信对话和行为等客观内容
- 对张成的主观评价持保留态度
- 明确标注哪些是推测、哪些是事实
- 如果张成对某人有好感/敌意，注意描写可能带有偏见
"""

    def _smart_sample_chapters(
        self, found_chapters: list[int], max_chapters: int
    ) -> list[int]:
        """智能采样章节，覆盖人物出现的全部范围。

        采样策略：
        - 如果章节数 <= max_chapters，返回全部
        - 否则均匀采样，确保覆盖开头、中间、结尾
        """
        total = len(found_chapters)
        if total <= max_chapters:
            return found_chapters

        # 均匀采样
        step = total / max_chapters
        sampled_indices = set()

        # 确保包含首尾
        sampled_indices.add(0)
        sampled_indices.add(total - 1)

        # 均匀选取中间章节
        for i in range(max_chapters - 2):
            idx = int((i + 1) * step)
            if idx < total:
                sampled_indices.add(idx)

        # 转换为实际章节号并排序
        sampled = sorted([found_chapters[i] for i in sampled_indices])

        logger.info(
            f"Smart sampling: {total} chapters -> {len(sampled)} samples "
            f"(range: {found_chapters[0]}-{found_chapters[-1]})"
        )
        return sampled

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
        """分析人物在单个章节的表现（最大化信息提取）"""
        # FIXED: 使用配置常数截断过长内容
        max_len = settings.max_chapter_content_length
        if len(content) > max_len:
            content = content[:max_len]

        prompt = f"""{self.FIRST_PERSON_CONTEXT}

分析人物"{character_name}"在以下章节中的**完整表现**，同时记录所有与其相关的人物信息。

章节：{chapter_title}
内容：
{content}

请以 JSON 格式返回：
{{
    "events": [
        "该人物参与的具体事件（一句话描述）",
        "只记录客观发生的事件，不含张成的主观推测",
        "最多5个，按重要性排序"
    ],
    "interactions": [
        {{
            "character": "互动对象姓名（准确全名）",
            "type": "dialogue/conflict/cooperation/support/observation",
            "description": "具体互动内容（一句话）",
            "sentiment": "positive/neutral/negative（这次互动的情感基调）",
            "initiated_by": "target/other/mutual（{character_name}发起/对方发起/双向）"
        }}
    ],
    "quote": "该人物最能体现性格的一句原话（必须是{character_name}说的，不是张成的描述）",
    "narrator_bias": "张成对{character_name}的态度倾向：positive/neutral/negative/unclear",
    "emotional_state": "{character_name}在本章的主要情感状态（如：愤怒、紧张、喜悦、平静、担忧等）",
    "chapter_significance": "本章对{character_name}发展的重要性：low/medium/high",
    "mentioned_characters": ["本章中与{character_name}有关联的所有人物姓名（含间接提及）"],
    "key_moment": "本章最能体现{character_name}的关键时刻（一句话，如无则空）"
}}

**分析要点**：
1. interactions 按重要性排序，最多记录5个核心互动
2. type 类型说明：
   - dialogue: 对话交流
   - conflict: 冲突对抗
   - cooperation: 合作配合
   - support: 支持帮助
   - observation: 单方面观察/关注（无直接互动）
3. mentioned_characters 要全面，包括：被提及但未出场的、间接相关的人物
4. 如果{character_name}本章只是被提及而未实际出场，events可为空，但要在key_moment说明
5. quote 必须是原话，如果该人物本章没有台词则返回空字符串
"""
        result = await chat_json(
            prompt,
            system="你是专业的小说分析师，擅长从第一人称叙述中提取客观信息。要全面、准确、结构化。"
        )

        # 解析 interactions
        interactions = []
        for i in result.get("interactions", [])[:5]:
            if isinstance(i, dict):
                interactions.append(CharacterInteraction(
                    character=i.get("character", ""),
                    type=i.get("type", "interaction"),
                    description=i.get("description", ""),
                    sentiment=i.get("sentiment", "neutral"),
                    initiated_by=i.get("initiated_by", ""),
                ))
            elif isinstance(i, str):
                # 兼容旧格式
                interactions.append(CharacterInteraction(
                    character="",
                    type="interaction",
                    description=i,
                ))

        return CharacterAppearance(
            chapter_index=chapter_index,
            chapter_title=chapter_title,
            events=result.get("events", [])[:5],
            interactions=interactions,
            quote=result.get("quote", ""),
            narrator_bias=result.get("narrator_bias", ""),
            emotional_state=result.get("emotional_state", ""),
            chapter_significance=result.get("chapter_significance", ""),
            mentioned_characters=result.get("mentioned_characters", []),
            key_moment=result.get("key_moment", ""),
        )

    async def analyze_relations(
        self,
        character_name: str,
        appearances: list[CharacterAppearance],
    ) -> list[CharacterRelation]:
        """基于所有章节分析人物关系（利用结构化互动数据）"""
        # 汇总结构化互动信息
        interactions_by_character: dict[str, list[dict]] = {}
        for app in appearances:
            for interaction in app.interactions:
                char = interaction.character
                if not char:
                    continue
                if char not in interactions_by_character:
                    interactions_by_character[char] = []
                interactions_by_character[char].append({
                    "chapter": app.chapter_index + 1,
                    "type": interaction.type,
                    "description": interaction.description,
                    "sentiment": interaction.sentiment,
                })

        if not interactions_by_character:
            return []

        # 格式化互动汇总
        interactions_summary = []
        for char, interactions in interactions_by_character.items():
            summary = f"\n【与 {char} 的互动】共 {len(interactions)} 次\n"
            for i in interactions[:5]:  # 每人最多展示5次
                summary += f"  - 第{i['chapter']}章 [{i['type']}] {i['description']} ({i['sentiment']})\n"
            if len(interactions) > 5:
                summary += f"  - ... 还有 {len(interactions) - 5} 次互动\n"
            interactions_summary.append(summary)

        prompt = f"""{self.FIRST_PERSON_CONTEXT}

基于以下结构化互动记录，深度分析人物"{character_name}"的人物关系网络：

{''.join(interactions_summary[:10])}

请以 JSON 格式返回：
{{
    "relations": [
        {{
            "target_name": "关系对象姓名（准确全名）",
            "relation_type": "friend/enemy/lover/family/mentor/rival/partner/complex",
            "description": "关系本质描述（一句话），基于实际互动模式",
            "objective_basis": "客观判断依据：具体的行为模式或对话特征",
            "first_interaction_chapter": 首次互动的章节号,
            "relation_evolution": "关系演变简述（如有变化，否则'稳定'）",
            "confidence": "high/medium/low（判断可信度）"
        }}
    ]
}}

**关系类型说明**：
- friend: 朋友，互相支持帮助
- enemy: 敌人，明确对抗
- lover: 恋人/暧昧对象
- family: 家人/亲属
- mentor: 师徒/指导关系
- rival: 竞争对手（非敌对）
- partner: 合作伙伴/战友
- complex: 复杂关系，难以简单分类

**分析要点**：
1. 优先分析互动次数多的人物
2. relation_type 基于行为模式判断，不受张成主观影响
3. 关注关系是否有演变（从敌对到合作等）
4. 如果信息不足以判断，confidence 设为 low
5. 最多返回 8 个最重要的关系，按重要性排序
"""
        result = await chat_json(
            prompt,
            system="你是专业的文学分析师，擅长从第一人称叙述中还原客观人物关系网络。"
        )

        relations = []
        for r in result.get("relations", [])[:8]:
            target = r.get("target_name", "")
            # 从原始数据中提取证据章节
            evidence = []
            if target in interactions_by_character:
                evidence = [i["chapter"] for i in interactions_by_character[target][:10]]

            relations.append(CharacterRelation(
                target_name=target,
                relation_type=r.get("relation_type", "unknown"),
                description=r.get("description", ""),
                evidence_chapters=evidence,
                objective_basis=r.get("objective_basis", ""),
                first_interaction_chapter=r.get("first_interaction_chapter", -1),
                relation_evolution=r.get("relation_evolution", ""),
                confidence=r.get("confidence", "medium"),
            ))

        return relations

    async def analyze_personality(
        self,
        character_name: str,
        appearances: list[CharacterAppearance],
    ) -> tuple[str, list[str], str]:
        """分析人物性格，返回 (description, personality, role)"""
        # 收集丰富的分析素材
        events_summary = []
        quotes = []
        emotional_states = []
        key_moments = []
        narrator_biases = []

        for app in appearances:
            # 事件
            for event in app.events[:2]:
                events_summary.append(f"第{app.chapter_index + 1}章: {event}")
            # 台词
            if app.quote:
                quotes.append(f"「{app.quote}」")
            # 情感状态
            if app.emotional_state:
                emotional_states.append(f"第{app.chapter_index + 1}章: {app.emotional_state}")
            # 关键时刻
            if app.key_moment:
                key_moments.append(f"第{app.chapter_index + 1}章: {app.key_moment}")
            # 叙述者偏见
            if app.narrator_bias:
                narrator_biases.append(app.narrator_bias)

        # 统计叙述者偏见倾向
        bias_summary = ""
        if narrator_biases:
            from collections import Counter
            bias_counts = Counter(narrator_biases)
            total = len(narrator_biases)
            bias_summary = f"张成态度统计: " + ", ".join(
                f"{k}({v}/{total})" for k, v in bias_counts.most_common()
            )

        prompt = f"""{self.FIRST_PERSON_CONTEXT}

基于以下丰富信息，深度分析人物"{character_name}"的性格特点：

## 主要事件（客观行为）
{chr(10).join(events_summary[:25])}

## 代表性台词（原话）
{chr(10).join(quotes[:8]) if quotes else "（暂无记录）"}

## 情感状态变化
{chr(10).join(emotional_states[:15]) if emotional_states else "（暂无记录）"}

## 关键时刻
{chr(10).join(key_moments[:10]) if key_moments else "（暂无记录）"}

## 叙述者偏见分析
{bias_summary if bias_summary else "（暂无数据）"}

请以 JSON 格式返回：
{{
    "description": "人物客观简介（80-150字）。像第三人称旁白一样描述，不带张成的主观色彩。要包含：身份背景、主要特点、在故事中的作用",
    "personality": [
        "性格特点1（必须有多次行为支撑）",
        "性格特点2",
        "性格特点3",
        "最多5个，按显著程度排序"
    ],
    "role": "protagonist/antagonist/supporting/minor",
    "role_basis": "角色定位的判断依据（一句话）"
}}

**性格分析原则**：
1. 只采纳有**多次行为模式**支撑的性格特点
2. 情感状态的变化规律能反映深层性格
3. 关键时刻的选择最能体现真实性格
4. 对话风格和用词习惯是客观证据
5. 忽略张成的单次主观评价
6. role 判断基于叙事功能，不是道德评价
"""
        result = await chat_json(
            prompt,
            system="你是专业的文学分析师，擅长从第一人称叙述中客观还原人物性格画像。"
        )

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
        """深度分析人物，生成完整画像和分析元数据"""
        # 收集丰富素材
        all_events = []
        all_quotes = []
        key_moments = []
        emotional_journey = []
        high_significance_chapters = []

        for app in appearances:
            # 事件
            for event in app.events:
                all_events.append(f"第{app.chapter_index + 1}章: {event}")
            # 台词
            if app.quote:
                all_quotes.append(f"「{app.quote}」（第{app.chapter_index + 1}章）")
            # 关键时刻
            if app.key_moment:
                key_moments.append(f"第{app.chapter_index + 1}章: {app.key_moment}")
            # 情感历程
            if app.emotional_state:
                emotional_journey.append(f"第{app.chapter_index + 1}章: {app.emotional_state}")
            # 高重要性章节
            if app.chapter_significance == "high":
                high_significance_chapters.append(app.chapter_index + 1)

        # 人物关系汇总
        relations_text = "\n".join([
            f"- {r.target_name}({r.relation_type}): {r.description}"
            + (f" [演变: {r.relation_evolution}]" if r.relation_evolution and r.relation_evolution != "稳定" else "")
            for r in relations
        ])

        # 汇总所有发现的关联人物
        discovered_characters: set[str] = set()
        for app in appearances:
            for char in app.mentioned_characters:
                if char and char != character_name:
                    discovered_characters.add(char)
            for interaction in app.interactions:
                if interaction.character and interaction.character != character_name:
                    discovered_characters.add(interaction.character)

        prompt = f"""{self.FIRST_PERSON_CONTEXT}

基于以下丰富信息，对人物"{character_name}"进行**终极深度分析**：

## 基本信息
简介：{description}
性格：{', '.join(personality)}
已分析章节数：{len(appearances)}
高重要性章节：{high_significance_chapters[:10] if high_significance_chapters else '无'}

## 人物关系网络
{relations_text if relations_text else '暂无关系数据'}

## 主要事件轨迹
{chr(10).join(all_events[:35])}

## 情感历程
{chr(10).join(emotional_journey[:20]) if emotional_journey else '（数据不足）'}

## 关键时刻集锦
{chr(10).join(key_moments[:15]) if key_moments else '（数据不足）'}

## 代表性台词
{chr(10).join(all_quotes[:12]) if all_quotes else '（暂无台词）'}

请以 JSON 格式返回**完整深度分析**：
{{
    "summary": "一句话客观概括（20-40字），像百科词条开头，不带任何情感色彩",
    "growth_arc": "人物成长轨迹（150-300字）。分阶段描述：早期→中期→后期的变化。只描述客观行为模式的演变，不是张成印象的变化",
    "core_traits": [
        {{
            "trait": "核心性格特征",
            "description": "该特征的具体表现（一句话）",
            "evidence": "最有力的证据（具体章节的行为或对话原文）"
        }}
    ],
    "strengths": ["客观优点1（能力/品质）", "优点2", "优点3"],
    "weaknesses": ["客观缺点1（性格缺陷/能力短板）", "缺点2"],
    "notable_quotes": [
        "最能代表该人物的经典语录1",
        "语录2",
        "语录3（必须是该人物原话，从上面的台词中选择或提炼）"
    ],
    "analysis_confidence": "high/medium/low",
    "analysis_limitations": "分析局限性说明（如：样本时间跨度、张成与该人物的关系偏差、缺失的信息等）"
}}

**终极分析原则**：
1. summary 是最重要的输出，要像维基百科一样客观精准
2. growth_arc 要有时间线感，描述从A到B的变化过程
3. core_traits 最多5个，必须有明确的行为证据
4. strengths/weaknesses 基于实际表现，不是张成的评价
5. notable_quotes 必须是该人物说的话，选择最能体现性格的
6. analysis_confidence 基于：样本量、信息客观性、覆盖全面性
7. analysis_limitations 诚实说明分析的局限和可能偏差
"""
        result = await chat_json(
            prompt,
            system="你是顶级的文学分析师，擅长从第一人称叙述中还原人物的客观全貌。要求精准、深刻、客观。"
        )

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
            # 新增：分析元数据
            "analysis_confidence": result.get("analysis_confidence", ""),
            "analysis_limitations": result.get("analysis_limitations", ""),
            "discovered_characters": list(discovered_characters),
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

        # 2. 智能采样分析章节（覆盖全书范围）
        chapters_to_analyze = self._smart_sample_chapters(
            search_result.found_in_chapters, max_chapters
        )

        # 3. FIXED: 并行分析每个章节，使用信号量控制并发数
        semaphore = asyncio.Semaphore(settings.analysis_concurrency)

        async def analyze_with_limit(idx: int) -> CharacterAppearance:
            async with semaphore:
                chapter = book.chapters[idx]
                content = book.content[chapter.start:chapter.end + 1]
                return await self.analyze_chapter_appearance(
                    character_name, idx, chapter.title, content
                )

        logger.info(f"Starting parallel analysis for {len(chapters_to_analyze)} chapters")
        tasks = [analyze_with_limit(idx) for idx in chapters_to_analyze]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤成功的结果
        appearances = []
        for idx, result in zip(chapters_to_analyze, results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to analyze chapter {idx}: {result}")
            else:
                appearances.append(result)

        logger.info(f"Completed analysis: {len(appearances)}/{len(chapters_to_analyze)} chapters")

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
            # 新增：分析元数据
            analysis_confidence=deep_profile.get("analysis_confidence", ""),
            analysis_limitations=deep_profile.get("analysis_limitations", ""),
            discovered_characters=deep_profile.get("discovered_characters", []),
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

        # 2. 智能采样章节
        chapters = self._smart_sample_chapters(
            search_result.found_in_chapters, max_chapters
        )
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
                "analysis_confidence": deep_profile.get("analysis_confidence", ""),
                "analysis_limitations": deep_profile.get("analysis_limitations", ""),
                "discovered_characters": deep_profile.get("discovered_characters", []),
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
            # 新增：分析元数据
            analysis_confidence=deep_profile.get("analysis_confidence", ""),
            analysis_limitations=deep_profile.get("analysis_limitations", ""),
            discovered_characters=deep_profile.get("discovered_characters", []),
        )

        yield {"event": "completed", "data": result.model_dump()}

    async def analyze_continue(
        self,
        book: Book,
        existing: DetailedCharacter,
        additional_chapters: int = 30,
        refresh_summary: bool = False,
    ) -> AsyncGenerator[dict, None]:
        """继续分析更多章节，基于已有分析结果

        Args:
            book: 书籍对象
            existing: 已有的分析结果
            additional_chapters: 要继续分析的章节数
            refresh_summary: 是否刷新总结字段（relations, personality, deep_profile）
        """
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
                "refresh_summary": refresh_summary,
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
                        "chapters_to_analyze": len(chapters_to_analyze),
                    },
                }
            except Exception as e:
                yield {
                    "event": "chapter_error",
                    "data": {"chapter_index": idx, "error": str(e)},
                }

        # 6. 合并所有已分析章节（只统计实际成功分析的章节）
        successfully_analyzed = [a.chapter_index for a in appearances]
        all_analyzed = sorted(set(existing.analyzed_chapters) | set(successfully_analyzed))

        # 7. 根据 refresh_summary 决定是否重新分析总结字段
        if refresh_summary:
            # 重新分析关系
            relations = await self.analyze_relations(character_name, appearances)
            yield {
                "event": "relations_analyzed",
                "data": {"relations": [r.model_dump() for r in relations]},
            }

            # 重新分析性格
            description, personality, role = await self.analyze_personality(
                character_name, appearances
            )
            yield {
                "event": "personality_analyzed",
                "data": {"description": description, "personality": personality, "role": role},
            }

            # 深度分析
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
                    "analysis_confidence": deep_profile.get("analysis_confidence", ""),
                    "analysis_limitations": deep_profile.get("analysis_limitations", ""),
                    "discovered_characters": deep_profile.get("discovered_characters", []),
                },
            }

            # 返回完整更新的结果
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
                # 新增：分析元数据
                analysis_confidence=deep_profile.get("analysis_confidence", ""),
                analysis_limitations=deep_profile.get("analysis_limitations", ""),
                discovered_characters=deep_profile.get("discovered_characters", []),
            )
        else:
            # 保留原有总结字段，只更新 appearances 和 analyzed_chapters
            yield {
                "event": "summary_skipped",
                "data": {"message": "总结字段保持不变，仅更新章节分析"},
            }

            # 即使不刷新总结，也要从新 appearances 中收集 discovered_characters
            discovered_characters: set[str] = set(existing.discovered_characters)
            for app in appearances:
                for char in app.mentioned_characters:
                    if char and char != character_name:
                        discovered_characters.add(char)
                for interaction in app.interactions:
                    if interaction.character and interaction.character != character_name:
                        discovered_characters.add(interaction.character)

            result = DetailedCharacter(
                name=character_name,
                aliases=existing.aliases,
                description=existing.description,
                role=existing.role,
                personality=existing.personality,
                summary=existing.summary,
                growth_arc=existing.growth_arc,
                core_traits=existing.core_traits,
                strengths=existing.strengths,
                weaknesses=existing.weaknesses,
                notable_quotes=existing.notable_quotes,
                appearances=appearances,
                first_appearance=search_result.found_in_chapters[0],
                last_appearance=search_result.found_in_chapters[-1],
                total_chapters=len(search_result.found_in_chapters),
                total_analyzed_chapters=len(all_analyzed),
                relations=existing.relations,
                analysis_status="completed",
                analyzed_chapters=all_analyzed,
                # 保留/更新元数据
                analysis_confidence=existing.analysis_confidence,
                analysis_limitations=existing.analysis_limitations,
                discovered_characters=list(discovered_characters),
            )

        yield {"event": "completed", "data": result.model_dump()}
