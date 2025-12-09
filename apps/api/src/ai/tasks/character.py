"""Character extraction task."""

import uuid
from ..client import chat_json
from ...knowledge.models import Character
from ...core.book import Book


CHARACTER_EXTRACTION_PROMPT = """分析以下小说片段，提取所有出现的人物角色。

内容：
{content}

请以 JSON 格式返回人物列表：
{{
    "characters": [
        {{
            "name": "人物姓名",
            "aliases": ["别名/外号列表"],
            "description": "人物简介（50-100字）",
            "role": "角色定位：protagonist/antagonist/supporting/minor",
            "first_chapter": "该人物首次出现的章节标题（如：第一章 xxx）"
        }}
    ]
}}

注意：
1. 只提取明确出现的人物，不要推测
2. 同一人物的不同称呼应合并
3. 简要描述人物特点
4. first_chapter 必须是上面内容中实际出现的章节标题
"""


class CharacterExtractor:
    """Extract characters from book."""

    async def extract(self, book: Book, sample_chapters: list[int] | None = None) -> list[Character]:
        """Extract characters from book.

        Args:
            book: The book to analyze
            sample_chapters: Optional list of chapter indices to sample.
                           If None, samples beginning, middle, and end.
        """
        # Determine which chapters to sample
        if sample_chapters is None:
            total = len(book.chapters)
            sample_chapters = [
                0,                    # Beginning
                total // 4,           # Quarter
                total // 2,           # Middle
                total * 3 // 4,       # Three quarters
                total - 1,            # End
            ]
            # Remove duplicates and out of range
            sample_chapters = sorted(set(
                i for i in sample_chapters
                if 0 <= i < len(book.chapters)
            ))

        # Build chapter title to index mapping
        chapter_title_to_index = {}
        for idx in sample_chapters:
            chapter = book.chapters[idx]
            chapter_title_to_index[chapter.title] = idx

        # Extract content from sample chapters
        sample_content = ""
        for idx in sample_chapters:
            chapter = book.chapters[idx]
            content = book.content[chapter.start:chapter.end + 1]
            # Truncate each chapter
            if len(content) > 5000:
                content = content[:5000]
            sample_content += f"\n\n--- {chapter.title} ---\n{content}"

        # Truncate total if needed
        if len(sample_content) > 30000:
            sample_content = sample_content[:30000]

        prompt = CHARACTER_EXTRACTION_PROMPT.format(content=sample_content)

        result = await chat_json(
            prompt,
            system="你是一个专业的小说分析助手。请仔细识别文本中的人物角色。",
        )

        characters = []
        for char_data in result.get("characters", []):
            # Find first appearance chapter index
            first_chapter_title = char_data.get("first_chapter", "")
            first_appearance = 0

            # Try to match chapter title
            for title, idx in chapter_title_to_index.items():
                if first_chapter_title and (first_chapter_title in title or title in first_chapter_title):
                    first_appearance = idx
                    break

            characters.append(Character(
                id=str(uuid.uuid4())[:8],
                name=char_data.get("name", ""),
                aliases=char_data.get("aliases", []),
                description=char_data.get("description", ""),
                role=char_data.get("role", "minor"),
                first_appearance=first_appearance,
            ))

        return characters
