"""Book management module."""

import hashlib
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import chardet

from ..config import settings
from ..knowledge.models import Chapter, ChapterAnalysis, Character


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
        patterns = [
            r"^第[0-9]+章[：:\s]?.*",
            r"^第[零一二三四五六七八九十百千万]+章[：:\s]?.*",
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
