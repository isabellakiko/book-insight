"""RAG (Retrieval-Augmented Generation) routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core.book import BookManager
from ..rag.store import VectorStore
from ..rag.retriever import RAGRetriever

router = APIRouter()


class QueryRequest(BaseModel):
    """RAG query request."""
    query: str
    top_k: int = 10


class QueryResult(BaseModel):
    """Single query result."""
    chapter_index: int
    chapter_title: str
    content: str
    score: float


class QueryResponse(BaseModel):
    """RAG query response."""
    query: str
    results: list[QueryResult]
    answer: str | None = None


class IndexRequest(BaseModel):
    """Request to index a book."""
    chunk_size: int = 500
    chunk_overlap: int = 100


@router.post("/{book_id}/index")
async def index_book(book_id: str, request: IndexRequest) -> dict:
    """Index a book for RAG queries."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    store = VectorStore(book_id)
    num_chunks = await store.index(
        book,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )

    return {
        "status": "indexed",
        "book_id": book_id,
        "num_chunks": num_chunks,
    }


@router.get("/{book_id}/status")
async def get_index_status(book_id: str) -> dict:
    """Check if a book is indexed."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    store = VectorStore(book_id)
    is_indexed = store.is_indexed()

    return {
        "book_id": book_id,
        "indexed": is_indexed,
    }


@router.post("/{book_id}/query")
async def query_book(book_id: str, request: QueryRequest) -> QueryResponse:
    """Query a book using RAG."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    store = VectorStore(book_id)
    if not store.is_indexed():
        raise HTTPException(
            status_code=400,
            detail="Book not indexed. Call /index first."
        )

    results = await store.query(request.query, top_k=request.top_k)

    return QueryResponse(
        query=request.query,
        results=[
            QueryResult(
                chapter_index=r.chapter_index,
                chapter_title=r.chapter_title,
                content=r.content,
                score=r.score,
            )
            for r in results
        ],
    )


@router.post("/{book_id}/ask")
async def ask_book(book_id: str, request: QueryRequest) -> QueryResponse:
    """Ask a question about the book (RAG + AI answer)."""
    book = BookManager.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    store = VectorStore(book_id)
    if not store.is_indexed():
        raise HTTPException(
            status_code=400,
            detail="Book not indexed. Call /index first."
        )

    retriever = RAGRetriever(store)
    results, answer = await retriever.ask(request.query, top_k=request.top_k)

    return QueryResponse(
        query=request.query,
        results=[
            QueryResult(
                chapter_index=r.chapter_index,
                chapter_title=r.chapter_title,
                content=r.content,
                score=r.score,
            )
            for r in results
        ],
        answer=answer,
    )
