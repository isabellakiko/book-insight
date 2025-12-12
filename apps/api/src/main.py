"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import books, analysis, rag

app = FastAPI(
    title="Book Insight API",
    description="AI-powered book analysis backend",
    version="0.1.0",
)

# CORS - 限制为实际使用的方法和头部
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Routers
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    # Ensure directories exist
    settings.books_dir.mkdir(parents=True, exist_ok=True)
    settings.analysis_dir.mkdir(parents=True, exist_ok=True)
    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
