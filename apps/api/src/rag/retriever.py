"""RAG retriever with AI answer generation."""

from .store import VectorStore, SearchResult
from ..ai.client import chat


RAG_ANSWER_PROMPT = """基于以下小说片段，回答用户的问题。

相关片段：
{context}

用户问题：{query}

请基于提供的内容回答问题。如果片段中没有足够信息，请说明。
回答要简洁准确，可以引用原文作为依据。
"""


class RAGRetriever:
    """RAG retriever that combines search with AI answering."""

    def __init__(self, store: VectorStore):
        self.store = store

    async def ask(
        self,
        query: str,
        top_k: int = 10,
    ) -> tuple[list[SearchResult], str]:
        """Ask a question and get an AI-generated answer.

        Returns:
            Tuple of (search results, AI answer)
        """
        # Retrieve relevant chunks
        results = await self.store.query(query, top_k=top_k)

        if not results:
            return results, "未找到相关内容。"

        # Build context from results
        context_parts = []
        for r in results:
            context_parts.append(
                f"[第{r.chapter_index + 1}章 {r.chapter_title}]\n{r.content}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Generate answer
        prompt = RAG_ANSWER_PROMPT.format(
            context=context,
            query=query,
        )

        answer = await chat(
            prompt,
            system="你是一个专业的小说分析助手。基于提供的原文片段，准确回答问题。",
            max_tokens=2048,
            temperature=0.5,
        )

        return results, answer
