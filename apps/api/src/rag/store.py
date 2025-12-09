"""Vector store for RAG."""

from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from ..config import settings
from ..core.book import Book


@dataclass
class SearchResult:
    """Search result from vector store."""
    chapter_index: int
    chapter_title: str
    content: str
    score: float


class VectorStore:
    """Vector store for a single book."""

    def __init__(self, book_id: str):
        self.book_id = book_id
        self.collection_name = f"book_{book_id}"

        # Initialize ChromaDB
        persist_dir = settings.vector_store_dir / book_id
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )

    def is_indexed(self) -> bool:
        """Check if the book is indexed."""
        try:
            collection = self.client.get_collection(self.collection_name)
            return collection.count() > 0
        except Exception:
            return False

    async def index(
        self,
        book: Book,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> int:
        """Index a book for RAG queries.

        Returns the number of chunks indexed.
        """
        # Delete existing collection if exists
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass

        # Create new collection
        collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"book_id": self.book_id},
        )

        # Split text by chapters, then by chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "],
        )

        all_chunks = []
        all_metadatas = []
        all_ids = []

        for chapter in book.chapters:
            chapter_content = book.content[chapter.start:chapter.end + 1]
            chunks = splitter.split_text(chapter_content)

            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    "chapter_index": chapter.index,
                    "chapter_title": chapter.title,
                    "chunk_index": i,
                })
                all_ids.append(f"{chapter.index:04d}_{i:04d}")

        # Batch embed and add
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i + batch_size]
            batch_metadatas = all_metadatas[i:i + batch_size]
            batch_ids = all_ids[i:i + batch_size]

            # Get embeddings
            embeddings = self.embeddings.embed_documents(batch_chunks)

            collection.add(
                documents=batch_chunks,
                embeddings=embeddings,
                metadatas=batch_metadatas,
                ids=batch_ids,
            )

        return len(all_chunks)

    async def query(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[SearchResult]:
        """Query the vector store."""
        collection = self.client.get_collection(self.collection_name)

        # Get query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Query
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        # Convert to SearchResult
        search_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if results["distances"] else 0

                search_results.append(SearchResult(
                    chapter_index=metadata["chapter_index"],
                    chapter_title=metadata["chapter_title"],
                    content=doc,
                    score=1 - distance,  # Convert distance to similarity
                ))

        return search_results
