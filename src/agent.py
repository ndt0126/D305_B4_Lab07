from __future__ import annotations

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

    PROMPT_TEMPLATE = (
        "Bạn là trợ lý tra cứu quy định/dịch vụ đại học.\n"
        "Chỉ trả lời DỰA TRÊN ngữ cảnh được cung cấp bên dưới.\n"
        "Nếu ngữ cảnh không đủ thông tin, hãy nói rõ là không tìm thấy trong tài liệu.\n"
        "Khi trả lời, trích dẫn số hiệu nguồn dạng [1], [2]... để người đọc truy vết được.\n\n"
        "--- NGỮ CẢNH ---\n"
        "{context}\n"
        "--- HẾT NGỮ CẢNH ---\n\n"
        "Câu hỏi: {question}\n"
        "Trả lời:"
    )

    NO_CONTEXT = "(Không truy xuất được đoạn tài liệu nào liên quan.)"

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn
        self.last_results: list[dict] = []  # giữ lại để truy vết/đánh giá grounding

    def build_context(self, results: list[dict]) -> str:
        """Ghép các chunk truy xuất được thành khối ngữ cảnh có đánh số + nguồn."""
        if not results:
            return self.NO_CONTEXT

        blocks = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {}) or {}
            source = metadata.get("source_url") or metadata.get("source") or metadata.get("doc_id") or "unknown"
            score = result.get("score", 0.0)
            blocks.append(
                f"[{index}] (nguồn: {source} | score={score:.3f})\n{result.get('content', '').strip()}"
            )
        return "\n\n".join(blocks)

    def answer(
        self,
        question: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> str:
        """Truy xuất top-k chunk -> dựng prompt có ngữ cảnh -> gọi LLM.

        ``metadata_filter`` cho phép agent lọc trước theo metadata (ví dụ
        ``{"audience": "student"}``) trước khi xếp hạng, dùng chung một đường
        với ``EmbeddingStore.search_with_filter``. Để ``None`` thì hành vi
        giống hệt ``search`` thường.
        """
        if metadata_filter:
            results = self.store.search_with_filter(
                question, top_k=top_k, metadata_filter=metadata_filter
            )
        else:
            results = self.store.search(question, top_k=top_k)
        self.last_results = results

        prompt = self.PROMPT_TEMPLATE.format(
            context=self.build_context(results),
            question=question,
        )

        answer = self.llm_fn(prompt)
        return answer if isinstance(answer, str) else str(answer)
