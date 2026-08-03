"""Benchmark có thể tái lập cho corpus quy định QNU của Lab 7 (K3).

Chạy khuyến nghị (PowerShell):
    $env:EMBEDDING_PROVIDER="local"; $env:HF_HUB_OFFLINE="1"; python scripts/run_benchmark.py

Kết quả được ghi tự động vào report/benchmark_raw.md.
"""
from __future__ import annotations

import os
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ingest import build_knowledge_base, load_documents  # noqa: E402
from src import (  # noqa: E402
    ChunkingStrategyComparator,
    FixedSizeChunker,
    HeadingChunker,
    KnowledgeBaseAgent,
    RecursiveChunker,
    SentenceChunker,
    compute_similarity,
)
from src.embeddings import (  # noqa: E402
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    LocalEmbedder,
    _mock_embed,
)

DATA_DIR = REPO_ROOT / "data" / "qnu_regulations"
OUTPUT_PATH = REPO_ROOT / "report" / "benchmark_raw.md"

STRATEGIES = {
    "heading(level=1..3)": HeadingChunker(min_level=1, max_level=3),
    "recursive(600)": RecursiveChunker(chunk_size=600),
    "fixed_size(500/80)": FixedSizeChunker(chunk_size=500, overlap=80),
    "by_sentences(3)": SentenceChunker(max_sentences_per_chunk=3),
}

DOC_1 = "quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc"
DOC_2 = "quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1"
DOC_3 = "quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024"
DOC_4 = "quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027"
DOC_5 = "quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien"

BENCHMARK = [
    {
        "id": 1,
        "query": "Quyết định 1401 có hiệu lực khi nào và thay thế quyết định nào?",
        "gold_answer": "Có hiệu lực kể từ ngày ký và thay thế Quyết định số 1455/QĐ-ĐHQN ngày 21/5/2025.",
        "gold_doc": DOC_1,
        "gold_phrase": "có hiệu lực kể từ ngày ký và thay thế Quyết định số",
        "filter": None,
    },
    {
        "id": 2,
        "query": "QyĐ474 quy định mức học phí cho hệ đào tạo đại học từ xa tuyển sinh đợt nào?",
        "gold_answer": "Áp dụng cho tuyển sinh tháng 2 năm 2026, Đợt 1.",
        "gold_doc": DOC_2,
        "gold_phrase": "tuyển sinh tháng 2 năm 2026 (Đợt 1)",
        "filter": None,
    },
    {
        "id": 3,
        "query": "Quy định 828 áp dụng mức học phí cho khóa và ngành nào?",
        "gold_answer": "Áp dụng cho khóa 34 ngành Quản lý đất đai, tuyển sinh năm 2024.",
        "gold_doc": DOC_3,
        "gold_phrase": "khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024",
        "filter": {"program": "part-time"},
    },
    {
        "id": 4,
        "query": "Học viên cao học khóa 28B phải nộp học phí Học kỳ 2 đến khi nào?",
        "gold_answer": "Nộp từ ngày 15/5/2026 đến hết ngày 02/8/2026.",
        "gold_doc": DOC_4,
        "gold_phrase": "từ ngày 15/5/2026 đến hết ngày 02/8/2026",
        "filter": {"program": "graduate"},
    },
    {
        "id": 5,
        "query": "Sinh viên Trường Đại học Quy Nhơn nghỉ Tết Nguyên đán 2026 từ ngày nào đến ngày nào?",
        "gold_answer": "Nghỉ từ ngày 09/02/2026 đến hết ngày 01/03/2026.",
        "gold_doc": DOC_5,
        "gold_phrase": "từ ngày 09 tháng 02 năm 2026 đến hết ngày 01 tháng 03 năm 2026",
        "filter": {"audience": "student"},
    },
]

SIMILARITY_PAIRS = [
    ("Sinh viên nghỉ Tết từ ngày 09 tháng 02 năm 2026.", "Thời gian nghỉ Tết của sinh viên bắt đầu ngày 09/02/2026.", "CAO"),
    ("Học viên nộp học phí qua cổng thanh toán trực tuyến.", "Người học thanh toán học phí bằng hệ thống trực tuyến.", "CAO"),
    ("Quyết định tuyển sinh có hiệu lực kể từ ngày ký.", "Văn bản tuyển sinh bắt đầu có hiệu lực vào ngày ký.", "CAO"),
    ("Sinh viên nghỉ Tết trong ba tuần.", "Học phí được thanh toán bằng mã QR.", "THẤP"),
    ("Quy định học phí áp dụng cho hệ đào tạo từ xa.", "Sinh viên phải bảo vệ tài sản cá nhân trong kỳ nghỉ.", "THẤP"),
]


def select_embedder():
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "local").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception as exc:
            print(f"Không tải được local embedder ({exc!r}); dùng mock chỉ để kiểm tra pipeline.")
    return _mock_embed


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold()


def is_relevant(result: dict, case: dict) -> bool:
    return (
        result["metadata"].get("doc_id") == case["gold_doc"]
        and normalize(case["gold_phrase"]) in normalize(result["content"])
    )


def preview(text: str, width: int = 90) -> str:
    flat = " ".join(text.split()).replace("|", "\\|")
    return flat[:width] + ("…" if len(flat) > width else "")


def score_case(results: list[dict], case: dict) -> int:
    flags = [is_relevant(result, case) for result in results]
    if flags and flags[0]:
        return 2
    return 1 if any(flags) else 0


class PrecomputedStore:
    def __init__(self, results: list[dict]) -> None:
        self.results = results

    def search(self, _query: str, top_k: int = 3) -> list[dict]:
        return self.results[:top_k]


def grounded_answer(results: list[dict], case: dict) -> str:
    def grounded_llm(prompt: str) -> str:
        if normalize(case["gold_phrase"]) in normalize(prompt):
            return case["gold_answer"]
        return "Không đủ thông tin trong ngữ cảnh đã truy xuất."

    return KnowledgeBaseAgent(PrecomputedStore(results), grounded_llm).answer(case["query"], top_k=3)


def section_a(lines: list[str]) -> None:
    lines.append("## A. Baseline trên 3 tài liệu đầu tiên\n")
    lines.append("| Tài liệu | Ký tự | Chiến lược | count | avg | min | max |")
    lines.append("|---|---:|---|---:|---:|---:|---:|")
    for doc in load_documents(DATA_DIR)[:3]:
        stats = ChunkingStrategyComparator().compare(doc.content, chunk_size=500)
        for name, values in stats.items():
            lengths = [len(chunk) for chunk in values["chunks"]]
            lines.append(
                f"| `{doc.id}` | {len(doc.content)} | `{name}` | {values['count']} | "
                f"{values['avg_length']:.1f} | {min(lengths, default=0)} | {max(lengths, default=0)} |"
            )
    lines.append("")


def section_b(lines: list[str], embedder) -> dict[str, dict]:
    lines.append("## B. Benchmark: đúng 5 câu hỏi × 4 chiến lược\n")
    summaries: dict[str, dict] = {}
    for index, (strategy_name, chunker) in enumerate(STRATEGIES.items(), start=1):
        store = build_knowledge_base(
            DATA_DIR,
            embedding_fn=embedder,
            chunker=chunker,
            collection_name=f"qnu_benchmark_{index}",
        )
        total = 0
        top1 = 0
        lines.append(f"### `{strategy_name}` — {store.get_collection_size()} chunks\n")
        lines.append("| Q | Filter | Hạng | doc_id | score | Gold? | Trích đoạn |")
        lines.append("|---:|---|---:|---|---:|---|---|")
        for case in BENCHMARK:
            results = (
                store.search_with_filter(case["query"], top_k=3, metadata_filter=case["filter"])
                if case["filter"]
                else store.search(case["query"], top_k=3)
            )
            points = score_case(results, case)
            total += points
            if results and is_relevant(results[0], case):
                top1 += 1
            for rank, result in enumerate(results, start=1):
                lines.append(
                    f"| {case['id']} | `{case['filter'] or '-'}` | {rank} | "
                    f"`{result['metadata'].get('doc_id')}` | {result['score']:.4f} | "
                    f"{'Có' if is_relevant(result, case) else 'Không'} | {preview(result['content'])} |"
                )
            answer = grounded_answer(results, case)
            lines.append(f"| {case['id']} | **Điểm/Agent** |  |  |  | **{points}/2** | {preview(answer, 120)} |")
        summaries[strategy_name] = {"chunks": store.get_collection_size(), "score": total, "top1": top1}
        lines.append(f"\n**Tổng: {total}/10; gold ở top-1: {top1}/5.**\n")

    lines.append("### Tổng hợp\n")
    lines.append("| Chiến lược | Chunks | Top-1 đúng | Điểm /10 |")
    lines.append("|---|---:|---:|---:|")
    for name, values in summaries.items():
        lines.append(f"| `{name}` | {values['chunks']} | {values['top1']}/5 | {values['score']} |")
    lines.append("")
    return summaries


def section_c(lines: list[str], embedder) -> None:
    lines.append("## C. Tác động của metadata filter\n")
    store = build_knowledge_base(
        DATA_DIR,
        embedding_fn=embedder,
        chunker=RecursiveChunker(chunk_size=600),
        collection_name="qnu_filter_analysis",
    )
    for case in (BENCHMARK[2], BENCHMARK[4]):
        unfiltered = store.search(case["query"], top_k=3)
        filtered = store.search_with_filter(case["query"], top_k=3, metadata_filter=case["filter"])
        lines.append(f"### Q{case['id']}: `{case['filter']}`\n")
        lines.append("| Chế độ | Top-1 doc | Top-1 score | Điểm |")
        lines.append("|---|---|---:|---:|")
        for label, results in (("Không lọc", unfiltered), ("Có lọc", filtered)):
            top = results[0] if results else {"metadata": {}, "score": 0.0}
            lines.append(
                f"| {label} | `{top['metadata'].get('doc_id', '-')}` | {top['score']:.4f} | "
                f"{score_case(results, case)}/2 |"
            )
        lines.append("")
    lines.append("> Q5 dùng đúng bộ lọc bắt buộc của K3 (`audience=student`). Vì cả 5 tài liệu hiện đều hướng tới người học, bộ lọc này chủ yếu xác nhận contract. Q3 dùng `program=part-time` để minh họa bộ lọc có tính phân biệt.\n")


def section_d(lines: list[str], embedder) -> None:
    lines.append("## D. Similarity cá nhân\n")
    lines.append("| Cặp | Dự đoán | Score | Đúng? |")
    lines.append("|---:|---|---:|---|")
    for index, (a, b, prediction) in enumerate(SIMILARITY_PAIRS, start=1):
        score = compute_similarity(embedder(a), embedder(b))
        expected_high = prediction == "CAO"
        lines.append(f"| {index} | {prediction} | {score:.4f} | {'Có' if (score >= 0.5) == expected_high else 'Không'} |")
    lines.append("")


def section_e(lines: list[str], embedder) -> None:
    lines.append("## E. Vòng đời store\n")
    store = build_knowledge_base(
        DATA_DIR,
        embedding_fn=embedder,
        chunker=RecursiveChunker(chunk_size=600),
        collection_name="qnu_store_lifecycle",
    )
    before = store.get_collection_size()
    deleted = store.delete_document(DOC_5)
    after = store.get_collection_size()
    missing = store.delete_document("khong-ton-tai")
    lines.extend([
        f"- Trước xóa: **{before}** chunks.",
        f"- Xóa TB209: `{deleted}`; sau xóa: **{after}** chunks.",
        f"- Xóa ID không tồn tại: `{missing}`.",
        "",
    ])


def section_failure(lines: list[str]) -> None:
    lines.append("## F. Failure case do thiếu dữ liệu nguồn\n")
    lines.append("- Câu hỏi thử lỗi: **Mức học phí cụ thể theo khối ngành trong QyĐ474 là bao nhiêu?**")
    lines.append("- Trang đã crawl có tiêu đề mục `I. Mức học phí theo khối ngành` nhưng bảng số tiền không xuất hiện trong phần văn bản công khai đã lấy. Vì vậy retrieval có thể tìm đúng tài liệu nhưng agent không thể tạo câu trả lời có căn cứ.")
    lines.append("- Cải thiện: lấy tệp đính kèm/PDF công khai nếu được phép, trích xuất bảng và giữ nguyên `source_url`; không suy đoán hoặc tự điền mức tiền.")
    lines.append("")


def main() -> int:
    embedder = select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    backend_label = (
        LOCAL_EMBEDDING_MODEL if backend != "mock embeddings fallback" else backend
    )
    documents = load_documents(DATA_DIR)
    lines = [
        "# Kết quả benchmark có thể tái lập — Lab 7 K3",
        "",
        "> Sinh tự động bởi `scripts/run_benchmark.py`; không sửa tay.",
        "",
        f"- Backend: **{backend_label}**",
        f"- Corpus: `{DATA_DIR.relative_to(REPO_ROOT)}` — **{len(documents)} tài liệu**",
        f"- Tổng ký tự phần body: **{sum(len(doc.content) for doc in documents)}**",
        "",
    ]
    if backend == "mock embeddings fallback":
        lines.append("> **Cảnh báo:** mock chỉ kiểm tra pipeline, không dùng kết quả này để kết luận chất lượng ngữ nghĩa.\n")
    section_a(lines)
    summaries = section_b(lines, embedder)
    section_c(lines, embedder)
    section_d(lines, embedder)
    section_e(lines, embedder)
    section_failure(lines)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Đã ghi {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    for name, values in summaries.items():
        print(f"{name}: {values['chunks']} chunks, top1={values['top1']}/5, score={values['score']}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())