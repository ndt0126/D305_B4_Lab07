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

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        raw_sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        limit = self.max_sentences_per_chunk
        for i in range(0, len(sentences), limit):
            group = sentences[i : i + limit]
            chunks.append(" ".join(group))

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
        raw_chunks = self._split(text, self.separators)
        return [c.strip() for c in raw_chunks if c.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return FixedSizeChunker(chunk_size=self.chunk_size, overlap=0).chunk(current_text)

        sep = remaining_separators[0]
        next_separators = remaining_separators[1:]

        if sep == "":
            return FixedSizeChunker(chunk_size=self.chunk_size, overlap=0).chunk(current_text)

        if sep not in current_text:
            return self._split(current_text, next_separators)

        splits = current_text.split(sep)
        chunks: list[str] = []
        current_chunk = ""

        for piece in splits:
            if not piece:
                continue

            if len(piece) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                chunks.extend(self._split(piece, next_separators))
                continue

            if not current_chunk:
                current_chunk = piece
            elif len(current_chunk) + len(sep) + len(piece) <= self.chunk_size:
                current_chunk += sep + piece
            else:
                chunks.append(current_chunk)
                current_chunk = piece

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


class HeadingChunker:
    """Split Markdown documents by heading/section boundaries.

    Each returned chunk keeps its section heading. Oversized sections are
    delegated to ``RecursiveChunker`` so the strategy remains usable when one
    section contains several long paragraphs.
    """

    _HEADING = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)

    def __init__(self, max_chars: int = 600) -> None:
        self.max_chars = max(1, max_chars)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        matches = list(self._HEADING.finditer(text))
        if not matches:
            return RecursiveChunker(chunk_size=self.max_chars).chunk(text)

        sections: list[str] = []
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.append(preamble)

        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            section = text[match.start() : end].strip()
            if section:
                sections.append(section)

        chunks: list[str] = []
        splitter = RecursiveChunker(chunk_size=self.max_chars)
        for section in sections:
            if len(section) <= self.max_chars:
                chunks.append(section)
                continue

            heading = section.splitlines()[0].strip() if section.startswith("#") else ""
            for piece in splitter.chunk(section):
                piece = piece.strip()
                if not piece:
                    continue
                if heading and not piece.startswith(heading):
                    piece = f"{heading}\n{piece}"
                chunks.append(piece)

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_val = _dot(vec_a, vec_b)
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_val / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed = FixedSizeChunker(chunk_size=chunk_size, overlap=0).chunk(text)
        by_sent = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        rec = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        def stats(chunks: list[str]) -> dict:
            cnt = len(chunks)
            avg_len = sum(len(c) for c in chunks) / cnt if cnt > 0 else 0.0
            return {
                "count": cnt,
                "avg_length": avg_len,
                "chunks": chunks,
            }

        return {
            "fixed_size": stats(fixed),
            "by_sentences": stats(by_sent),
            "recursive": stats(rec),
        }
