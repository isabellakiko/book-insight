"""Chapter analysis task."""

from ..client import chat_json
from ...knowledge.models import ChapterAnalysis


CHAPTER_ANALYSIS_PROMPT = """分析以下小说章节，提取关键信息。

章节标题：{title}

章节内容：
{content}

请以 JSON 格式返回以下信息：
{{
    "summary": "章节摘要（100-200字）",
    "characters": ["出场人物列表"],
    "events": ["关键事件列表，每个事件一句话描述"],
    "sentiment": "情感基调（如：紧张、轻松、悲伤、热血等）",
    "keywords": ["关键词列表，5-10个"]
}}
"""


class ChapterAnalyzer:
    """Analyze individual chapters."""

    async def analyze(
        self,
        chapter_index: int,
        title: str,
        content: str,
    ) -> ChapterAnalysis:
        """Analyze a single chapter."""
        # Truncate if too long (Claude context limit)
        if len(content) > 30000:
            content = content[:30000] + "\n\n[内容过长，已截断...]"

        prompt = CHAPTER_ANALYSIS_PROMPT.format(
            title=title,
            content=content,
        )

        result = await chat_json(
            prompt,
            system="你是一个专业的小说分析助手。请仔细分析章节内容，提取准确的信息。",
        )

        return ChapterAnalysis(
            chapter_index=chapter_index,
            title=title,
            summary=result.get("summary", ""),
            characters=result.get("characters", []),
            events=result.get("events", []),
            sentiment=result.get("sentiment", ""),
            keywords=result.get("keywords", []),
        )
