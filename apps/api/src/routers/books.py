"""Book management routes."""

from fastapi import APIRouter, UploadFile, HTTPException
from pydantic import BaseModel

from ..core.book import BookManager, Book

router = APIRouter()


class BookResponse(BaseModel):
    """Book response model."""
    id: str
    title: str
    author: str
    total_chapters: int
    total_characters: int


class ChapterResponse(BaseModel):
    """Chapter response model."""
    index: int
    title: str
    start: int
    end: int


@router.get("")
async def list_books() -> list[BookResponse]:
    """List all books."""
    books = BookManager.list_books()
    return [
        BookResponse(
            id=b.id,
            title=b.title,
            author=b.author,
            total_chapters=len(b.chapters),
            total_characters=len(b.content),
        )
        for b in books
    ]


@router.get("/{book_id}")
async def get_book(book_id: str) -> BookResponse:
    """Get book details."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        total_chapters=len(book.chapters),
        total_characters=len(book.content),
    )


@router.get("/{book_id}/chapters")
async def get_chapters(book_id: str) -> list[ChapterResponse]:
    """Get book chapters."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return [
        ChapterResponse(
            index=ch.index,
            title=ch.title,
            start=ch.start,
            end=ch.end,
        )
        for ch in book.chapters
    ]


@router.get("/{book_id}/chapters/{chapter_index}/content")
async def get_chapter_content(book_id: str, chapter_index: int) -> dict:
    """Get chapter content."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if chapter_index < 0 or chapter_index >= len(book.chapters):
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter = book.chapters[chapter_index]
    content = book.content[chapter.start:chapter.end + 1]
    return {
        "index": chapter.index,
        "title": chapter.title,
        "content": content,
    }


@router.post("/upload")
async def upload_book(file: UploadFile) -> BookResponse:
    """Upload a new book."""
    if not file.filename or not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    content = await file.read()
    book = await BookManager.import_book(content, file.filename)

    return BookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        total_chapters=len(book.chapters),
        total_characters=len(book.content),
    )


@router.delete("/{book_id}")
async def delete_book(book_id: str):
    """Delete a book."""
    success = BookManager.delete_book(book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"status": "deleted"}
