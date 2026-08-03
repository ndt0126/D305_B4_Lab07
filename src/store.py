from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.

    Ghi chú thiết kế:
        Kể cả khi ChromaDB có sẵn, mọi bản ghi vẫn được giữ song song trong
        ``self._store`` (in-memory mirror). Nhờ vậy search/filter/delete cho kết quả
        xác định (deterministic) và giống hệt nhau ở mọi máy — điều kiện cần để
        so sánh chiến lược chunking giữa các thành viên trong nhóm là công bằng.
        ChromaDB chỉ đóng vai trò lớp lưu trữ bổ sung; nếu bất kỳ thao tác nào
        với Chroma lỗi, store vẫn chạy bình thường bằng bộ nhớ trong.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # Client tạm thời (in-process, không ghi đĩa) để mỗi store là một
            # không gian tên độc lập, tránh dính state giữa các lần chạy test.
            client = chromadb.EphemeralClient()
            self._collection = client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    # ------------------------------------------------------------------ helpers

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Chuẩn hóa một Document thành bản ghi lưu trữ (đã kèm embedding).

        - ``doc_id`` luôn có mặt trong metadata (mặc định = ``doc.id``) để
          ``delete_document()`` và lọc theo tài liệu hoạt động kể cả khi người dùng
          không tự gán trường này.
        - ``_index`` giữ thứ tự nạp, dùng để phá thế hòa điểm một cách ổn định.
        """
        metadata = dict(doc.metadata or {})
        metadata.setdefault("doc_id", doc.id)

        record: dict[str, Any] = {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
            "_index": self._next_index,
        }
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """Xếp hạng ``records`` theo tích vô hướng với embedding của ``query``."""
        if top_k <= 0 or not records:
            return []

        query_embedding = self._embedding_fn(query)
        scored: list[dict[str, Any]] = []
        for record in records:
            scored.append(
                {
                    "id": record["id"],
                    "content": record["content"],
                    "metadata": record["metadata"],
                    "score": _dot(query_embedding, record["embedding"]),
                }
            )

        # Sắp xếp giảm dần theo score; hòa điểm thì giữ thứ tự nạp ban đầu.
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    # --------------------------------------------------------------- public API

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return

        new_records = [self._make_record(doc) for doc in docs]
        self._store.extend(new_records)

        if self._use_chroma and self._collection is not None:
            try:
                self._collection.add(
                    ids=[record["id"] for record in new_records],
                    documents=[record["content"] for record in new_records],
                    embeddings=[record["embedding"] for record in new_records],
                    # Chroma không nhận metadata rỗng -> luôn có ít nhất doc_id.
                    metadatas=[
                        {key: value for key, value in record["metadata"].items() if value is not None}
                        for record in new_records
                    ],
                )
            except Exception:
                # Lỗi phía Chroma không được làm hỏng lab: quay về in-memory.
                self._use_chroma = False

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.

        Pre-filter (lọc trước khi tính similarity) giúp các chunk sai đối tượng
        (ví dụ ``audience=faculty``) không bao giờ chiếm chỗ trong top-k.
        """
        if not metadata_filter:
            return self._search_records(query, self._store, top_k)

        candidates = [
            record
            for record in self._store
            if all(str(record["metadata"].get(key)) == str(value) for key, value in metadata_filter.items())
        ]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        remaining = [record for record in self._store if record["metadata"].get("doc_id") != doc_id]
        removed = len(self._store) - len(remaining)
        if removed == 0:
            return False

        self._store = remaining

        if self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(where={"doc_id": doc_id})
            except Exception:
                self._use_chroma = False

        return True
