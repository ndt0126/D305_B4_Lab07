"""
run_benchmark.py — kịch bản đo đạc cho Giai đoạn 2 (Lab 07 / K3).

Chạy:
    python3 scripts/run_benchmark.py                 # dùng backend theo EMBEDDING_PROVIDER (mặc định mock)
    EMBEDDING_PROVIDER=local python3 scripts/run_benchmark.py

Kịch bản này KHÔNG được chấm điểm; nó chỉ sinh ra các con số thật để dán vào
report/REPORT_CANHAN.md và report/REPORT_NHOM.md. Toàn bộ kết quả được ghi ra
report/benchmark_raw.md.

Các phần đo:
    A. Baseline — ChunkingStrategyComparator trên 3 văn bản
    B. Benchmark — 5 câu hỏi x 4 chiến lược chunking, ghi top-3
    C. Metadata filter — search() vs search_with_filter() trên cùng câu hỏi
    D. Similarity — 5 cặp câu, dự đoán vs điểm thực tế
    E. Vòng đời store — get_collection_size() / delete_document()
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

DATA_DIR = REPO_ROOT / "data" / "k3_university"
OUTPUT_PATH = REPO_ROOT / "report" / "benchmark_raw.md"

# ---------------------------------------------------------------- cấu hình đo

STRATEGIES = {
    "fixed_size(300/50)": FixedSizeChunker(chunk_size=300, overlap=50),
    "by_sentences(2)": SentenceChunker(max_sentences_per_chunk=2),
    "recursive(300)": RecursiveChunker(chunk_size=300),
    "heading(max=600)": HeadingChunker(max_chars=600, min_chars=120),
}

# Mỗi câu hỏi kèm: tài liệu chứa đáp án (gold_doc), cụm từ khóa phải xuất hiện
# trong chunk thì chunk đó mới được tính là "liên quan" (nhãn tự động, khách quan).
BENCHMARK = [
    {
        "id": 1,
        "query": "Sinh viên đăng ký học phần ở đâu và theo lịch nào?",
        "gold_answer": "Đăng ký trong cổng học vụ, theo lịch của từng học kỳ.",
        "gold_doc": "k3-course-registration",
        "gold_phrase": "cổng học vụ",
        "filter": None,
    },
    {
        "id": 2,
        "query": "Khi gặp lỗi trùng lịch thì sinh viên phải xử lý thế nào?",
        "gold_answer": "Điều chỉnh lớp học phần trước thời hạn điều chỉnh được công bố.",
        "gold_doc": "k3-course-registration",
        "gold_phrase": "trùng lịch",
        "filter": None,
    },
    {
        "id": 3,
        "query": "Yêu cầu ngoại lệ về học vụ được gửi qua kênh nào?",
        "gold_answer": "Gửi qua kênh hỗ trợ học vụ chính thức.",
        "gold_doc": "k3-course-registration",
        "gold_phrase": "kênh hỗ trợ học vụ",
        "filter": None,
    },
    {
        "id": 4,
        "query": "Cần mang theo giấy tờ gì khi mượn tài liệu ở thư viện?",
        "gold_answer": "Phải mang thẻ định danh hợp lệ khi sử dụng dịch vụ mượn.",
        "gold_doc": "k3-library-services",
        "gold_phrase": "thẻ định danh",
        "filter": None,
    },
    {
        "id": 5,
        "query": "Quy định về học phần tiên quyết áp dụng cho sinh viên là gì?",
        "gold_answer": "Học phần có thể yêu cầu học phần tiên quyết; sinh viên phải kiểm tra điều kiện trước khi xác nhận đăng ký.",
        "gold_doc": "k3-course-registration",
        "gold_phrase": "tiên quyết",
        "filter": {"audience": "student"},
    },
]

SIMILARITY_PAIRS = [
    ("Sinh viên đăng ký học phần trong cổng học vụ.",
     "Việc đăng ký môn học được thực hiện trên cổng thông tin học vụ.", "CAO"),
    ("Thư viện cho mượn tài liệu và cung cấp không gian học tập.",
     "Người dùng cần mang thẻ định danh hợp lệ khi mượn tài liệu.", "CAO"),
    ("Sinh viên đăng ký học phần trong cổng học vụ.",
     "Thư viện cho mượn tài liệu và cung cấp không gian học tập.", "THẤP"),
    ("Học phần tiên quyết phải được hoàn thành trước.",
     "Hôm nay trời mưa rất to ở khu ký túc xá.", "THẤP"),
    ("Sinh viên đăng ký học phần trong cổng học vụ.",
     "Sinh viên đăng ký học phần trong cổng học vụ.", "CAO (=1.0)"),
]


# ------------------------------------------------------------------ tiện ích

def select_embedder():
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            print("!! Local embedder không sẵn sàng — quay về mock.")
    return _mock_embed


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).lower()


def is_relevant(result: dict, case: dict) -> bool:
    """Nhãn liên quan tự động: đúng tài liệu VÀ chunk có chứa cụm từ khóa vàng."""
    same_doc = result["metadata"].get("doc_id") == case["gold_doc"]
    has_phrase = normalize(case["gold_phrase"]) in normalize(result["content"])
    return same_doc and has_phrase


def preview(text: str, width: int = 90) -> str:
    flat = " ".join(text.split())
    return flat[:width] + ("…" if len(flat) > width else "")


def score_case(results: list[dict], case: dict) -> int:
    """Chấm theo docs/SCORING.md: 2 = liên quan ở top-1, 1 = liên quan trong top-3, 0 = không."""
    flags = [is_relevant(result, case) for result in results]
    if flags and flags[0]:
        return 2
    if any(flags):
        return 1
    return 0


def demo_llm(prompt: str) -> str:
    """LLM giả lập: trả lại chính ngữ cảnh đã truy xuất để kiểm tra grounding."""
    context = prompt.split("--- NGỮ CẢNH ---")[-1].split("--- HẾT NGỮ CẢNH ---")[0]
    return f"[DEMO LLM] Trả lời dựa trên {context.count('[')} đoạn ngữ cảnh: {preview(context, 120)}"


# ---------------------------------------------------------------- các phần đo

def section_a(lines: list[str]) -> None:
    lines.append("## A. Baseline — ChunkingStrategyComparator\n")
    texts = {doc.id: doc.content for doc in load_documents(DATA_DIR)}
    texts["chunking_experiment_report (văn bản dài để đối chiếu)"] = (
        REPO_ROOT / "data" / "chunking_experiment_report.md"
    ).read_text(encoding="utf-8")

    lines.append("| Tài liệu | Số ký tự | Chiến lược | count | avg_length | min | max |")
    lines.append("|---|---|---|---|---|---|---|")
    for name, text in texts.items():
        stats = ChunkingStrategyComparator().compare(text, chunk_size=300)
        for strategy, values in stats.items():
            lines.append(
                f"| {name} | {len(text)} | `{strategy}` | {values['count']} | "
                f"{values['avg_length']:.1f} | {values['min_length']} | {values['max_length']} |"
            )
    lines.append("")


def section_b(lines: list[str], embedder) -> dict[str, int]:
    lines.append("## B. 5 câu hỏi đánh giá x 4 chiến lược (top-3)\n")
    totals: dict[str, int] = {}

    for strategy_name, chunker in STRATEGIES.items():
        store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker)
        agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)
        total = 0

        lines.append(f"### Chiến lược `{strategy_name}` — {store.get_collection_size()} chunk\n")
        lines.append("| # | Câu hỏi | Hạng | doc_id | score | Liên quan? | Trích chunk |")
        lines.append("|---|---|---|---|---|---|---|")

        for case in BENCHMARK:
            if case["filter"]:
                results = store.search_with_filter(case["query"], top_k=3, metadata_filter=case["filter"])
            else:
                results = store.search(case["query"], top_k=3)

            points = score_case(results, case)
            total += points
            for rank, result in enumerate(results, start=1):
                lines.append(
                    f"| {case['id']} | {case['query'] if rank == 1 else ''} | {rank} | "
                    f"{result['metadata'].get('doc_id')} | {result['score']:.3f} | "
                    f"{'CÓ' if is_relevant(result, case) else 'không'} | {preview(result['content'], 70)} |"
                )
            lines.append(f"| {case['id']} | **điểm câu này** | | | | **{points}/2** | |")

        agent_answer = agent.answer(BENCHMARK[0]["query"], top_k=3)
        lines.append("")
        lines.append(f"**Tổng điểm truy xuất `{strategy_name}`: {total}/10**\n")
        lines.append(f"*Ví dụ câu trả lời agent (Q1):* {preview(agent_answer, 200)}\n")
        totals[strategy_name] = total

    lines.append("### Tổng hợp\n")
    lines.append("| Chiến lược | Điểm truy xuất /10 |")
    lines.append("|---|---|")
    for strategy_name, total in totals.items():
        lines.append(f"| `{strategy_name}` | {total} |")
    lines.append("")
    return totals


def section_c(lines: list[str], embedder) -> None:
    lines.append("## C. search() vs search_with_filter() — cùng câu hỏi Q5\n")
    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=RecursiveChunker(chunk_size=300))
    case = BENCHMARK[4]

    for label, results in (
        ("search() — KHÔNG lọc", store.search(case["query"], top_k=3)),
        (
            'search_with_filter(audience="student")',
            store.search_with_filter(case["query"], top_k=3, metadata_filter=case["filter"]),
        ),
    ):
        lines.append(f"**{label}** — điểm câu này: {score_case(results, case)}/2\n")
        lines.append("| Hạng | doc_id | audience | score | Liên quan? |")
        lines.append("|---|---|---|---|---|")
        for rank, result in enumerate(results, start=1):
            lines.append(
                f"| {rank} | {result['metadata'].get('doc_id')} | {result['metadata'].get('audience')} | "
                f"{result['score']:.3f} | {'CÓ' if is_relevant(result, case) else 'không'} |"
            )
        lines.append("")


def section_d(lines: list[str], embedder) -> None:
    lines.append("## D. Dự đoán độ tương tự cosine (5 cặp câu)\n")
    lines.append("| Cặp | Câu A | Câu B | Dự đoán | compute_similarity | Đúng dự đoán? |")
    lines.append("|---|---|---|---|---|---|")
    for index, (sentence_a, sentence_b, prediction) in enumerate(SIMILARITY_PAIRS, start=1):
        score = compute_similarity(embedder(sentence_a), embedder(sentence_b))
        expected_high = prediction.startswith("CAO")
        actually_high = score >= 0.5
        verdict = "Đúng" if expected_high == actually_high else "SAI"
        lines.append(
            f"| {index} | {preview(sentence_a, 55)} | {preview(sentence_b, 55)} | "
            f"{prediction} | {score:.4f} | {verdict} |"
        )
    lines.append("")


def section_e(lines: list[str], embedder) -> None:
    lines.append("## E. Vòng đời store — size / delete_document\n")
    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=RecursiveChunker(chunk_size=300))
    before = store.get_collection_size()
    deleted = store.delete_document("k3-library-services")
    after = store.get_collection_size()
    missing = store.delete_document("khong-ton-tai")
    lines.append(f"- Số chunk ban đầu: **{before}**")
    lines.append(f"- `delete_document('k3-library-services')` -> `{deleted}`; còn lại **{after}** chunk")
    lines.append(f"- `delete_document('khong-ton-tai')` -> `{missing}` (đúng kỳ vọng: không xóa gì)")
    lines.append("")


def main() -> int:
    embedder = select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)

    lines: list[str] = [
        "# Kết quả đo thô — Lab 07 (K3), Giai đoạn 2",
        "",
        "> File này do `scripts/run_benchmark.py` sinh tự động. Không sửa tay.",
        "",
        f"- Backend nhúng: **{backend}**",
        f"- Thư mục dữ liệu: `{DATA_DIR.relative_to(REPO_ROOT)}`",
        f"- Số tài liệu trong corpus: **{len(load_documents(DATA_DIR))}**",
        "",
    ]
    if backend == "mock embeddings fallback":
        lines += [
            "> **CẢNH BÁO PHƯƠNG PHÁP:** mock embedding là hàm băm MD5 -> vector, "
            "**không mang ngữ nghĩa**. Mọi điểm số dưới đây là thật nhưng chỉ dùng để "
            "kiểm chứng đường ống (pipeline) chạy đúng, KHÔNG dùng để kết luận chiến lược "
            "chunking nào tốt hơn về mặt ngữ nghĩa. Đặt `EMBEDDING_PROVIDER=local` để đo lại.",
            "",
        ]

    section_a(lines)
    section_b(lines, embedder)
    section_c(lines, embedder)
    section_d(lines, embedder)
    section_e(lines, embedder)

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Đã ghi kết quả vào {OUTPUT_PATH.relative_to(REPO_ROOT)} (backend: {backend})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
