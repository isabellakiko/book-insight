"""Analysis routes."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ..core.book import BookManager
from ..ai.tasks.chapter import ChapterAnalyzer
from ..ai.tasks.character import CharacterExtractor
from ..knowledge.models import ChapterAnalysis, Character

router = APIRouter()


class AnalyzeChapterRequest(BaseModel):
    """Request to analyze a chapter."""
    chapter_index: int


class AnalyzeBatchRequest(BaseModel):
    """Request to analyze multiple chapters."""
    start_chapter: int = 0
    end_chapter: int | None = None
    parallel: int = 3


@router.get("/{book_id}/chapters")
async def get_chapter_analyses(book_id: str) -> list[ChapterAnalysis]:
    """Get all chapter analyses for a book."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    analyses = BookManager.get_analyses(book_id)
    return analyses


@router.get("/{book_id}/chapters/{chapter_index}")
async def get_chapter_analysis(book_id: str, chapter_index: int) -> ChapterAnalysis | None:
    """Get analysis for a specific chapter."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    analysis = BookManager.get_chapter_analysis(book_id, chapter_index)
    return analysis


@router.post("/{book_id}/chapters/{chapter_index}")
async def analyze_chapter(book_id: str, chapter_index: int) -> ChapterAnalysis:
    """Analyze a single chapter."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if chapter_index < 0 or chapter_index >= len(book.chapters):
        raise HTTPException(status_code=404, detail="Chapter not found")

    analyzer = ChapterAnalyzer()
    chapter = book.chapters[chapter_index]
    content = book.content[chapter.start:chapter.end + 1]

    analysis = await analyzer.analyze(chapter_index, chapter.title, content)
    BookManager.save_chapter_analysis(book_id, analysis)

    return analysis


@router.post("/{book_id}/batch")
async def analyze_batch(
    book_id: str,
    request: AnalyzeBatchRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Start batch analysis of chapters."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    end = request.end_chapter or len(book.chapters)

    # Add to background tasks
    background_tasks.add_task(
        _run_batch_analysis,
        book_id,
        request.start_chapter,
        end,
        request.parallel,
    )

    return {
        "status": "started",
        "start_chapter": request.start_chapter,
        "end_chapter": end,
    }


async def _run_batch_analysis(
    book_id: str,
    start: int,
    end: int,
    parallel: int,
):
    """Run batch analysis in background."""
    book = BookManager.get_book(book_id)
    if not book:
        return

    analyzer = ChapterAnalyzer()

    for i in range(start, end):
        # Skip if already analyzed
        existing = BookManager.get_chapter_analysis(book_id, i)
        if existing:
            continue

        chapter = book.chapters[i]
        content = book.content[chapter.start:chapter.end + 1]

        try:
            analysis = await analyzer.analyze(i, chapter.title, content)
            BookManager.save_chapter_analysis(book_id, analysis)
        except Exception as e:
            print(f"Error analyzing chapter {i}: {e}")


@router.get("/{book_id}/characters")
async def get_characters(book_id: str) -> list[Character]:
    """Get extracted characters."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    characters = BookManager.get_characters(book_id)
    return characters


@router.post("/{book_id}/characters/extract")
async def extract_characters(book_id: str) -> list[Character]:
    """Extract characters from book."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    extractor = CharacterExtractor()
    characters = await extractor.extract(book)
    BookManager.save_characters(book_id, characters)

    return characters
