"""Book management module."""

import hashlib
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import chardet

from ..config import settings
from ..knowledge.models import Chapter, ChapterAnalysis, Character, DetailedCharacter


@dataclass
class Book:
    """Book data structure."""
    id: str
    title: str
    author: str
    content: str
    chapters: list[Chapter] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class BookManager:
    """Book management utilities."""

    # Cache loaded books
    _cache: dict[str, Book] = {}

    @classmethod
    def list_books(cls) -> list[Book]:
        """List all available books."""
        books = []
        books_dir = settings.books_dir

        if not books_dir.exists():
            return books

        for file_path in books_dir.glob("*.txt"):
            book_id = cls._file_to_id(file_path.name)
            book = cls.get_book(book_id)
            if book:
                books.append(book)

        return books

    @classmethod
    def get_book(cls, book_id: str) -> Optional[Book]:
        """Get a book by ID."""
        if book_id in cls._cache:
            return cls._cache[book_id]

        # Find the file
        books_dir = settings.books_dir
        for file_path in books_dir.glob("*.txt"):
            if cls._file_to_id(file_path.name) == book_id:
                book = cls._load_book(file_path)
                cls._cache[book_id] = book
                return book

        return None

    @classmethod
    async def import_book(cls, content: bytes, filename: str) -> Book:
        """Import a book from bytes content."""
        # Detect encoding
        detected = chardet.detect(content)
        encoding = detected.get("encoding", "utf-8") or "utf-8"

        # Decode
        text = content.decode(encoding, errors="replace")

        # Generate ID
        book_id = cls._file_to_id(filename)

        # Save to file
        file_path = settings.books_dir / filename
        file_path.write_text(text, encoding="utf-8")

        # Parse
        book = cls._parse_book(book_id, filename, text)
        cls._cache[book_id] = book

        return book

    @classmethod
    def delete_book(cls, book_id: str) -> bool:
        """Delete a book."""
        books_dir = settings.books_dir
        for file_path in books_dir.glob("*.txt"):
            if cls._file_to_id(file_path.name) == book_id:
                file_path.unlink()
                cls._cache.pop(book_id, None)

                # Also delete analysis
                analysis_dir = settings.analysis_dir / book_id
                if analysis_dir.exists():
                    import shutil
                    shutil.rmtree(analysis_dir)

                return True
        return False

    @classmethod
    def _load_book(cls, file_path: Path) -> Book:
        """Load a book from file."""
        content = file_path.read_text(encoding="utf-8")
        book_id = cls._file_to_id(file_path.name)
        return cls._parse_book(book_id, file_path.name, content)

    @classmethod
    def _parse_book(cls, book_id: str, filename: str, content: str) -> Book:
        """Parse book content."""
        # Extract title and author
        title, author = cls._extract_book_info(content)
        if not title:
            title = cls._extract_title_from_filename(filename)

        # Detect chapters
        chapters = cls._detect_chapters(content)

        return Book(
            id=book_id,
            title=title,
            author=author,
            content=content,
            chapters=chapters,
            metadata={
                "filename": filename,
                "total_characters": len(content),
            },
        )

    @classmethod
    def _file_to_id(cls, filename: str) -> str:
        """Convert filename to book ID."""
        name = filename.replace(".txt", "")
        return hashlib.md5(name.encode()).hexdigest()[:12]

    @classmethod
    def _extract_title_from_filename(cls, filename: str) -> str:
        """Extract title from filename."""
        name = filename.replace(".txt", "")
        # Remove common prefixes/suffixes
        name = re.sub(r"^\[.*?\]", "", name)
        name = re.sub(r"【.*?】", "", name)
        name = re.sub(r"\(.*?\)", "", name)
        name = re.sub(r"（.*?）", "", name)
        return name.strip() or filename

    @classmethod
    def _extract_book_info(cls, content: str) -> tuple[str, str]:
        """Extract title and author from content."""
        header = content[:5000]
        title = ""
        author = ""

        # 『书名/作者:xxx』格式
        match = re.search(r"『([^/]+)/作者[:：]([^』]+)』", header)
        if match:
            return match.group(1).strip(), match.group(2).strip()

        # 书名：xxx 格式
        match = re.search(r"书名[：:]\s*(.+)", header)
        if match:
            title = match.group(1).strip()

        # 作者：xxx 格式
        match = re.search(r"作者[：:]\s*(.+)", header)
        if match:
            author = match.group(1).strip()

        return title, author

    @classmethod
    def _detect_chapters(cls, content: str) -> list[Chapter]:
        """Detect chapters in content."""
        chapters = []

        # Chapter patterns
        # 支持：第X章、第X掌（错别字）、第X （缺少"章"字）
        # 注意：
        #   - 中文数字包含"两"（如"第两千章"）、"份"（"千"的错别字）
        #   - "地"是"第"的常见错别字（如"地五千五百零七章"）
        patterns = [
            r"^[第地][0-9]+[章掌][：:\s]?.*",
            r"^[第地][零一二三四五六七八九十百千万两份]+[章掌][：:\s]?.*",
            r"^[第地][0-9]+\s+\S+",  # 第123 标题（缺少章字）
            r"^[第地][零一二三四五六七八九十百千万两份]+\s+\S+",  # 第一百二十三 标题
            r"^Chapter\s+\d+[：:\s]?.*",
        ]

        combined = "|".join(f"({p})" for p in patterns)
        pattern = re.compile(combined, re.MULTILINE | re.IGNORECASE)

        for match in pattern.finditer(content):
            title = match.group(0).strip()
            if title:
                if chapters:
                    chapters[-1] = Chapter(
                        index=chapters[-1].index,
                        title=chapters[-1].title,
                        start=chapters[-1].start,
                        end=match.start() - 1,
                    )

                chapters.append(Chapter(
                    index=len(chapters),
                    title=title,
                    start=match.start(),
                    end=len(content) - 1,
                ))

        return chapters

    # Analysis storage methods

    @classmethod
    def get_analyses(cls, book_id: str) -> list[ChapterAnalysis]:
        """Get all chapter analyses."""
        analysis_dir = settings.analysis_dir / book_id / "chapters"
        if not analysis_dir.exists():
            return []

        analyses = []
        for file_path in sorted(analysis_dir.glob("*.json")):
            data = json.loads(file_path.read_text())
            analyses.append(ChapterAnalysis(**data))

        return analyses

    @classmethod
    def get_chapter_analysis(cls, book_id: str, chapter_index: int) -> Optional[ChapterAnalysis]:
        """Get analysis for a specific chapter."""
        file_path = settings.analysis_dir / book_id / "chapters" / f"{chapter_index:04d}.json"
        if not file_path.exists():
            return None

        data = json.loads(file_path.read_text())
        return ChapterAnalysis(**data)

    @classmethod
    def save_chapter_analysis(cls, book_id: str, analysis: ChapterAnalysis) -> None:
        """Save chapter analysis."""
        analysis_dir = settings.analysis_dir / book_id / "chapters"
        analysis_dir.mkdir(parents=True, exist_ok=True)

        file_path = analysis_dir / f"{analysis.chapter_index:04d}.json"
        file_path.write_text(analysis.model_dump_json(indent=2))

    @classmethod
    def get_characters(cls, book_id: str) -> list[Character]:
        """Get extracted characters."""
        file_path = settings.analysis_dir / book_id / "characters.json"
        if not file_path.exists():
            return []

        data = json.loads(file_path.read_text())
        return [Character(**c) for c in data]

    @classmethod
    def save_characters(cls, book_id: str, characters: list[Character]) -> None:
        """Save extracted characters."""
        analysis_dir = settings.analysis_dir / book_id
        analysis_dir.mkdir(parents=True, exist_ok=True)

        file_path = analysis_dir / "characters.json"
        file_path.write_text(
            json.dumps([c.model_dump() for c in characters], ensure_ascii=False, indent=2)
        )

    # ===== 详细人物分析存储方法 =====
    # 统一使用新格式: characters/{name}/profile.json

    @classmethod
    def save_detailed_character(cls, book_id: str, character: DetailedCharacter) -> None:
        """保存详细人物分析到 characters/{name}/profile.json"""
        char_dir = settings.analysis_dir / book_id / "characters" / character.name
        char_dir.mkdir(parents=True, exist_ok=True)

        profile_path = char_dir / "profile.json"
        profile_path.write_text(
            character.model_dump_json(indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # 同步更新 characters.json 索引
        cls._sync_character_index(book_id, character)

    @classmethod
    def _sync_character_index(cls, book_id: str, character: DetailedCharacter) -> None:
        """同步更新 characters.json 索引"""
        index_path = settings.analysis_dir / book_id / "characters.json"

        # 读取现有索引
        characters = []
        if index_path.exists():
            characters = json.loads(index_path.read_text(encoding="utf-8"))

        # 查找并更新或添加
        found = False
        for i, c in enumerate(characters):
            if c.get("name") == character.name:
                characters[i] = {
                    "name": character.name,
                    "aliases": character.aliases,
                    "description": character.description,
                    "first_appearance": character.first_appearance,
                    "role": character.role,
                }
                found = True
                break

        if not found:
            characters.append({
                "name": character.name,
                "aliases": character.aliases,
                "description": character.description,
                "first_appearance": character.first_appearance,
                "role": character.role,
            })

        # 保存索引
        index_path.write_text(
            json.dumps(characters, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    @classmethod
    def get_detailed_character(cls, book_id: str, character_name: str) -> Optional[DetailedCharacter]:
        """获取详细人物分析"""
        profile_path = settings.analysis_dir / book_id / "characters" / character_name / "profile.json"

        if not profile_path.exists():
            return None

        data = json.loads(profile_path.read_text(encoding="utf-8"))

        # 确保 analysis_status 字段存在
        if "analysis_status" not in data:
            data["analysis_status"] = "completed"

        return DetailedCharacter(**data)

    @classmethod
    def get_detailed_characters(cls, book_id: str) -> list[DetailedCharacter]:
        """获取所有详细人物分析"""
        characters = []
        chars_dir = settings.analysis_dir / book_id / "characters"

        if not chars_dir.exists():
            return characters

        for char_dir in chars_dir.iterdir():
            if char_dir.is_dir():
                profile_path = char_dir / "profile.json"
                if profile_path.exists():
                    data = json.loads(profile_path.read_text(encoding="utf-8"))
                    if "analysis_status" not in data:
                        data["analysis_status"] = "completed"
                    characters.append(DetailedCharacter(**data))

        return characters

    # ===== 章节独立存储方法 =====

    @classmethod
    def split_book_to_chapters(cls, book_id: str) -> int:
        """将书籍拆分为独立章节文件"""
        book = cls.get_book(book_id)
        if not book:
            raise ValueError(f"Book {book_id} not found")

        # 创建章节目录
        chapters_dir = settings.books_dir / book_id / "chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        # 保存元信息
        meta_path = settings.books_dir / book_id / "meta.json"
        meta_path.write_text(json.dumps({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "total_chapters": len(book.chapters),
            "total_characters": len(book.content),
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        # 拆分章节
        for chapter in book.chapters:
            content = book.content[chapter.start:chapter.end + 1]
            chapter_data = {
                "index": chapter.index,
                "title": chapter.title,
                "content": content,
            }
            file_path = chapters_dir / f"{chapter.index + 1:04d}.json"
            file_path.write_text(
                json.dumps(chapter_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

        return len(book.chapters)

    @classmethod
    def get_chapter_file(cls, book_id: str, chapter_index: int) -> Optional[dict]:
        """从独立文件读取章节"""
        file_path = settings.books_dir / book_id / "chapters" / f"{chapter_index + 1:04d}.json"
        if not file_path.exists():
            return None
        return json.loads(file_path.read_text(encoding="utf-8"))

    @classmethod
    def has_chapter_files(cls, book_id: str) -> bool:
        """检查是否已拆分章节文件"""
        chapters_dir = settings.books_dir / book_id / "chapters"
        return chapters_dir.exists() and any(chapters_dir.glob("*.json"))
