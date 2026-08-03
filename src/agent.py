from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(
        self,
        question: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> str:
        if metadata_filter:
            results = self.store.search_with_filter(
                question,
                top_k=top_k,
                metadata_filter=metadata_filter,
            )
        else:
            results = self.store.search(question, top_k=top_k)
        self.last_results = results
        if not results:
            return "Không tìm thấy thông tin phù hợp trong kho tri thức."

        context_parts = []
        for idx, r in enumerate(results, start=1):
            doc_id = r.get("metadata", {}).get("doc_id", r.get("id", "doc"))
            content = r.get("content", "")
            context_parts.append(f"[{idx}] (doc_id: {doc_id}): {content}")

        context = "\n\n".join(context_parts)

        prompt = (
            f"Instruction: Chỉ sử dụng thông tin trong ngữ cảnh dưới đây để trả lời câu hỏi. "
            f"Nếu ngữ cảnh không đủ thông tin, hãy nêu rõ.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )

        return self.llm_fn(prompt)
