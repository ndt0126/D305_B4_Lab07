from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    # Cắt SAU dấu kết câu (. ! ?) khi theo sau là khoảng trắng/xuống dòng.
    # Lookbehind giữ lại dấu câu ở cuối câu thay vì nuốt mất nó.
    _SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])[ \t]*(?:\n+|\s)")

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def split_sentences(self, text: str) -> list[str]:
        """Tách văn bản thành danh sách câu đã strip, bỏ phần tử rỗng."""
        if not text or not text.strip():
            return []
        raw_sentences = self._SENTENCE_BOUNDARY.split(text)
        return [sentence.strip() for sentence in raw_sentences if sentence and sentence.strip()]

    def chunk(self, text: str) -> list[str]:
        sentences = self.split_sentences(text)
        if not sentences:
            return []

        chunks: list[str] = []
        size = self.max_sentences_per_chunk
        for start in range(0, len(sentences), size):
            group = sentences[start : start + size]
            chunk = " ".join(group).strip()
            if chunk:
                chunks.append(chunk)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        pieces = self._split(text, list(self.separators))
        return [piece for piece in pieces if piece and piece.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        """Đệ quy: thử dấu phân cách ưu tiên cao nhất, xuống dần khi đoạn vẫn quá dài."""
        if not current_text:
            return []

        # Base case 1: đoạn đã đủ nhỏ -> giữ nguyên (đây là điểm dừng mong muốn).
        if len(current_text) <= self.chunk_size:
            return [current_text]

        # Base case 2: hết dấu phân cách (hoặc gặp separator rỗng "") -> cắt cứng theo ký tự.
        if not remaining_separators or remaining_separators[0] == "":
            return self._hard_split(current_text)

        separator = remaining_separators[0]
        rest = remaining_separators[1:]

        # Dấu phân cách này không xuất hiện -> thử ngay dấu ưu tiên kế tiếp.
        if separator not in current_text:
            return self._split(current_text, rest)

        # Gộp tham lam (greedy merge): nối lại các mảnh nhỏ cho tới sát chunk_size
        # để không tạo ra hàng loạt chunk vụn (ví dụ khi separator là " ").
        chunks: list[str] = []
        buffer = ""
        for piece in current_text.split(separator):
            candidate = piece if not buffer else buffer + separator + piece
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue

            if buffer:
                chunks.append(buffer)
                buffer = ""

            if len(piece) > self.chunk_size:
                # Mảnh đơn lẻ vẫn quá dài -> đệ quy với dấu phân cách mịn hơn.
                chunks.extend(self._split(piece, rest))
            else:
                buffer = piece

        if buffer:
            chunks.append(buffer)
        return chunks

    def _hard_split(self, text: str) -> list[str]:
        """Cắt cứng theo chunk_size khi không còn ranh giới ngôn ngữ nào để dựa vào."""
        size = max(1, self.chunk_size)
        return [text[start : start + size] for start in range(0, len(text), size)]


class HeadingChunker:
    """
    Chiến lược tùy chỉnh cho K3 — chia theo tiêu đề/mục của văn bản quy định.

    Lý do thiết kế: tài liệu dịch vụ/quy định đại học (đăng ký học phần, thư viện,
    học phí…) được viết theo mục có tiêu đề Markdown. Mỗi mục là một "đơn vị trả lời"
    trọn vẹn, nên cắt theo ranh giới tiêu đề giữ được đủ điều kiện + ngoại lệ + thời hạn
    trong cùng một chunk, thay vì cắt ngang giữa câu như fixed-size.

    Cơ chế:
        1. Tách văn bản tại các dòng bắt đầu bằng '#' (H1..H6).
        2. Ghim (prefix) tiêu đề của mục vào đầu mỗi chunk con -> chunk nào cũng
           tự mang ngữ cảnh "đang nói về mục nào" khi được embed.
        3. Mục dài hơn max_chars được cắt tiếp bằng RecursiveChunker (theo đoạn/câu).
        4. Mục quá ngắn (< min_chars) được gộp với mục kế tiếp để tránh chunk vụn.
    """

    _HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)

    def __init__(self, max_chars: int = 600, min_chars: int = 120) -> None:
        self.max_chars = max_chars
        self.min_chars = min_chars

    def _sections(self, text: str) -> list[tuple[str, str]]:
        """Trả về danh sách (tiêu đề, nội dung) theo thứ tự xuất hiện."""
        matches = list(self._HEADING.finditer(text))
        if not matches:
            return [("", text)]

        sections: list[tuple[str, str]] = []
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.append(("", preamble))

        for index, match in enumerate(matches):
            title = match.group(2).strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            sections.append((title, text[start:end].strip()))
        return sections

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        splitter = RecursiveChunker(chunk_size=self.max_chars)
        chunks: list[str] = []
        pending = ""  # bộ đệm gộp các mục quá ngắn

        for title, body in self._sections(text):
            block = f"{title}\n{body}".strip() if title else body.strip()
            if not block:
                continue

            block = f"{pending}\n\n{block}".strip() if pending else block
            pending = ""

            if len(block) < self.min_chars:
                pending = block  # quá ngắn -> chờ gộp với mục sau
                continue

            if len(block) <= self.max_chars:
                chunks.append(block)
                continue

            # Mục dài: cắt tiếp nhưng vẫn ghim tiêu đề vào từng mảnh.
            prefix = f"{title}\n" if title else ""
            for piece in splitter.chunk(block):
                piece = piece.strip()
                if not piece:
                    continue
                chunks.append(piece if piece.startswith(title) and title else f"{prefix}{piece}".strip())

        if pending:
            if chunks:
                chunks[-1] = f"{chunks[-1]}\n\n{pending}".strip()
            else:
                chunks.append(pending)
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b:
        return 0.0

    dot_product = _dot(vec_a, vec_b)
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))

    # Bảo vệ chia cho 0: vector rỗng/vector không -> quy ước trả về 0.0
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        """Chạy cả 3 chiến lược có sẵn trên cùng một văn bản và trả về thống kê.

        Trả về dict dạng:
            {
              "fixed_size":   {"count": int, "avg_length": float,
                               "min_length": int, "max_length": int, "chunks": [...]},
              "by_sentences": {...},
              "recursive":    {...},
            }
        """
        overlap = max(0, chunk_size // 10)  # 10% overlap để so sánh công bằng
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=overlap),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        comparison: dict = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            lengths = [len(chunk) for chunk in chunks]
            comparison[name] = {
                "count": len(chunks),
                "avg_length": (sum(lengths) / len(lengths)) if lengths else 0.0,
                "min_length": min(lengths) if lengths else 0,
                "max_length": max(lengths) if lengths else 0,
                "chunks": chunks,
            }
        return comparison
