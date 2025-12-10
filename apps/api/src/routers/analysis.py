"""Analysis routes."""

import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..core.book import BookManager
from ..ai.tasks.chapter import ChapterAnalyzer
from ..ai.tasks.character_analyzer import CharacterOnDemandAnalyzer
from ..knowledge.models import ChapterAnalysis, CharacterSearchResult, DetailedCharacter

router = APIRouter()


class AnalyzeChapterRequest(BaseModel):
    """Request to analyze a chapter."""
    chapter_index: int


class AnalyzeBatchRequest(BaseModel):
    """Request to analyze multiple chapters."""
    start_chapter: int = 0
    end_chapter: int | None = None
    parallel: int = 3


class CharacterSearchRequest(BaseModel):
    """Request to search character."""
    name: str


class CharacterAnalyzeRequest(BaseModel):
    """Request to analyze character."""
    name: str
    max_chapters: int = 30


# ===== 章节分析端点 =====

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


# ===== 人物按需分析端点 =====

@router.post("/{book_id}/characters/search")
async def search_character(
    book_id: str,
    request: CharacterSearchRequest,
) -> CharacterSearchResult:
    """搜索人物出现的章节（快速，纯文本搜索）"""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    analyzer = CharacterOnDemandAnalyzer()
    result = analyzer.search(book, request.name)
    return result


@router.post("/{book_id}/characters/analyze")
async def analyze_character(
    book_id: str,
    request: CharacterAnalyzeRequest,
) -> DetailedCharacter:
    """分析单个人物（同步，可能耗时较长）"""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # 检查是否已有缓存
    cached = BookManager.get_detailed_character(book_id, request.name)
    if cached and cached.analysis_status == "completed":
        return cached

    analyzer = CharacterOnDemandAnalyzer()
    result = await analyzer.analyze_full(book, request.name, request.max_chapters)

    # 保存结果
    if result.analysis_status == "completed" and not result.error_message:
        BookManager.save_detailed_character(book_id, result)

    return result


@router.get("/{book_id}/characters/stream")
async def analyze_character_stream(book_id: str, name: str):
    """流式分析人物（SSE，推荐用于前端）"""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    async def event_generator():
        analyzer = CharacterOnDemandAnalyzer()
        result = None

        async for event in analyzer.analyze_stream(book, name):
            event_type = event["event"]
            data = json.dumps(event["data"], ensure_ascii=False)
            yield f"event: {event_type}\ndata: {data}\n\n"

            # 保存最终结果
            if event_type == "completed" and "error" not in event["data"]:
                result = DetailedCharacter(**event["data"])

        # 保存到文件
        if result and result.analysis_status == "completed":
            BookManager.save_detailed_character(book_id, result)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{book_id}/characters/detailed/{character_name}")
async def get_detailed_character(
    book_id: str,
    character_name: str,
) -> DetailedCharacter | None:
    """获取已分析的人物详情"""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return BookManager.get_detailed_character(book_id, character_name)


@router.get("/{book_id}/characters/detailed")
async def list_detailed_characters(book_id: str) -> list[DetailedCharacter]:
    """列出所有已分析的人物"""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return BookManager.get_detailed_characters(book_id)


class CharacterContinueRequest(BaseModel):
    """Request to continue analyzing character."""
    name: str
    additional_chapters: int = 30


@router.get("/{book_id}/characters/continue")
async def continue_analyze_character_stream(
    book_id: str,
    name: str,
    additional_chapters: int = 30,
):
    """继续分析人物更多章节（SSE 流式）"""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # 获取已有分析结果
    existing = BookManager.get_detailed_character(book_id, name)
    if not existing:
        raise HTTPException(status_code=404, detail="Character not found. Please analyze first.")

    async def event_generator():
        analyzer = CharacterOnDemandAnalyzer()
        result = None

        async for event in analyzer.analyze_continue(book, existing, additional_chapters):
            event_type = event["event"]
            data = json.dumps(event["data"], ensure_ascii=False)
            yield f"event: {event_type}\ndata: {data}\n\n"

            if event_type == "completed" and "error" not in event["data"]:
                result = DetailedCharacter(**event["data"])

        # 保存更新后的结果
        if result and result.analysis_status == "completed":
            BookManager.save_detailed_character(book_id, result)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
