"""Reproducible chunk-level benchmark for Lab 07 (QNU regulations).

Run with local multilingual embeddings when available::

    set EMBEDDING_PROVIDER=local
    python bench.py

The script falls back to the deterministic mock embedder and records that
limitation in the generated report. Results are written to
``report/benchmark_raw.md``.
"""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from ingest import build_knowledge_base, load_documents
from src import (
    FixedSizeChunker,
    HeadingChunker,
    KnowledgeBaseAgent,
    LocalEmbedder,
    RecursiveChunker,
    SentenceChunker,
    _mock_embed,
)


REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data" / "qnu_regulations"
OUTPUT_PATH = REPO_ROOT / "report" / "benchmark_raw.md"


@dataclass(frozen=True)
class BenchmarkCase:
    id: int
    query: str
    gold_answer: str
    gold_doc: str
    evidence_marker: str
    answer_markers: tuple[str, ...]
    metadata_filter: dict[str, str] | None = None


STRATEGIES = {
    "sentence(3)": SentenceChunker(max_sentences_per_chunk=3),
    "recursive(400)": RecursiveChunker(chunk_size=400),
    "heading(600)": HeadingChunker(max_chars=600),
    "fixed(800/150)": FixedSizeChunker(chunk_size=800, overlap=150),
}

BENCHMARK = (
    BenchmarkCase(
        1,
        "Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 bao lâu, từ ngày nào và học lại khi nào?",
        "Nghỉ 03 tuần từ 09/02/2026 đến hết 01/03/2026 và học lại từ 02/03/2026.",
        "quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien",
        "sinh viên nghỉ tết nguyên đán bính ngọ năm 2026 là 03 tuần",
        ("03 tuần", "09 tháng 02 năm 2026", "01 tháng 03 năm 2026", "02 tháng 3 năm 2026"),
    ),
    BenchmarkCase(
        2,
        "Quy chế tuyển sinh đại học ban hành kèm QĐ1401 có hiệu lực khi nào và thay thế quyết định nào?",
        "Có hiệu lực từ ngày ký và thay thế Quyết định 1455/QĐ-ĐHQN ngày 21/5/2025.",
        "quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc",
        "quyết định này có hiệu lực kể từ ngày ký",
        ("có hiệu lực kể từ ngày ký", "1455/QĐ-ĐHQN", "21/5/2025"),
        {"audience": "student"},
    ),
    BenchmarkCase(
        3,
        "Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào?",
        "Áp dụng cho đào tạo đại học từ xa tuyển sinh tháng 2/2026 đợt 1 và có hiệu lực từ ngày ký.",
        "quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1",
        "đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026",
        ("đào tạo từ xa", "đợt 1", "có hiệu lực kể từ ngày ký"),
    ),
    BenchmarkCase(
        4,
        "Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào?",
        "Nộp từ 15/5/2026 đến hết 02/8/2026, qua cổng https://e-bills.vn/pay/qnu hoặc QR Code.",
        "quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027",
        "thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026",
        ("15/5/2026", "02/8/2026", "e-bills.vn/pay/qnu"),
    ),
    BenchmarkCase(
        5,
        "QyĐ828 về học phí năm học 2024-2025 áp dụng cho hệ đào tạo, khóa và ngành nào?",
        "Áp dụng cho hệ vừa làm vừa học khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024.",
        "quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024",
        "mức thu học phí năm học 2024-2025 áp dụng cho hệ đào tạo vừa làm vừa học khóa 34",
        ("2024-2025", "vừa làm vừa học", "quản lý đất đai"),
    ),
)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold()


def contains_all(text: str, markers: tuple[str, ...]) -> bool:
    normalized = normalize(text)
    return all(normalize(marker) in normalized for marker in markers)


def is_relevant(result: dict, case: BenchmarkCase) -> bool:
    return (
        result.get("metadata", {}).get("doc_id") == case.gold_doc
        and normalize(case.evidence_marker) in normalize(result.get("content", ""))
    )


def extractive_llm(prompt: str) -> str:
    """Return only the first retrieved chunk, without injecting gold answers."""
    try:
        context = prompt.split("Context:\n", 1)[1].split("\n\nQuestion:", 1)[0]
        first = re.split(r"\n\n\[2\]", context, maxsplit=1)[0]
        content = first.split("): ", 1)[1]
        return "Trích xuất từ chunk hạng 1: " + " ".join(content.split())
    except (IndexError, ValueError):
        return "Không đủ ngữ cảnh để trả lời."


def select_embedder():
    load_dotenv(override=False)
    requested = os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()
    if requested == "local":
        try:
            embedder = LocalEmbedder()
            return embedder, embedder._backend_name, ""
        except Exception as exc:
            warning = f"Local embedder không sẵn sàng ({type(exc).__name__}: {exc}); dùng mock."
            return _mock_embed, _mock_embed._backend_name, warning
    return _mock_embed, _mock_embed._backend_name, "Đã chọn mock bằng EMBEDDING_PROVIDER."


def retrieve(store, case: BenchmarkCase, use_filter: bool) -> list[dict]:
    if use_filter and case.metadata_filter:
        return store.search_with_filter(
            case.query,
            top_k=3,
            metadata_filter=case.metadata_filter,
        )
    return store.search(case.query, top_k=3)


def evaluate(store, agent: KnowledgeBaseAgent, case: BenchmarkCase, use_filter: bool) -> dict:
    results = retrieve(store, case, use_filter)
    relevant_ranks = [rank for rank, result in enumerate(results, 1) if is_relevant(result, case)]
    complete_ranks = [
        rank
        for rank, result in enumerate(results, 1)
        if result.get("metadata", {}).get("doc_id") == case.gold_doc
        and contains_all(result.get("content", ""), case.answer_markers)
    ]
    active_filter = case.metadata_filter if use_filter else None
    answer = agent.answer(case.query, top_k=3, metadata_filter=active_filter)
    agent_correct = contains_all(answer, case.answer_markers)

    if not relevant_ranks:
        score = 0
    elif agent_correct:
        score = 2
    else:
        score = 1

    return {
        "results": results,
        "relevant_ranks": relevant_ranks,
        "complete_ranks": complete_ranks,
        "answer": answer,
        "agent_correct": agent_correct,
        "score": score,
    }


def preview(text: str, limit: int = 150) -> str:
    compact = " ".join(text.split()).replace("|", "\\|")
    return compact if len(compact) <= limit else compact[: limit - 1] + "…"


def top3_signature(evaluation: dict) -> str:
    return ", ".join(
        f"{result['id']} ({result['score']:.3f})" for result in evaluation["results"]
    )


def render_result_rows(lines: list[str], evaluation: dict, case: BenchmarkCase) -> None:
    lines.append("| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |")
    lines.append("|---:|---|---|---|---:|---|---|---|")
    for rank, result in enumerate(evaluation["results"], 1):
        metadata = result.get("metadata", {})
        relevant = "CÓ" if is_relevant(result, case) else "không"
        complete = "CÓ" if (
            metadata.get("doc_id") == case.gold_doc
            and contains_all(result.get("content", ""), case.answer_markers)
        ) else "không"
        lines.append(
            f"| {rank} | `{result['id']}` | `{metadata.get('doc_id', '')}` | "
            f"`{metadata.get('audience', '')}` | {result['score']:.4f} | {relevant} | "
            f"{complete} | {preview(result.get('content', ''))} |"
        )


def build_report(backend: str, warning: str, strategy_runs: dict) -> str:
    documents = load_documents(DATA_DIR)
    lines = [
        "# Benchmark thô - Lab 07 (Quy định QNU)",
        "",
        "> File sinh tự động bởi `python bench.py`; không sửa số liệu bằng tay.",
        "",
        f"- Backend embedding: **{backend}**",
        f"- Corpus: `{DATA_DIR.relative_to(REPO_ROOT).as_posix()}` ({len(documents)} tài liệu)",
        "- Chấm ở mức chunk: đúng `doc_id` **và** chứa chuỗi bằng chứng đặc trưng.",
        "- Agent benchmark là agent trích xuất xác định: chỉ dùng chunk hạng 1, không được cung cấp gold answer.",
    ]
    if warning:
        lines.append(f"- Cảnh báo: **{warning}**")
    if "mock" in backend.lower():
        lines.append("- Giới hạn: mock deterministic nhưng không biểu diễn ngữ nghĩa; score chỉ kiểm luồng kỹ thuật/xếp hạng giả, không dùng để kết luận chất lượng semantic.")

    lines.extend([
        "",
        "## 1. Tổng hợp strategy",
        "",
        "| Strategy | Số chunk | Điểm /10 | Query có bằng chứng trong top-3 | Agent đúng từ top-1 |",
        "|---|---:|---:|---:|---:|",
    ])
    for name, run in strategy_runs.items():
        evaluations = run["evaluations"]
        lines.append(
            f"| `{name}` | {run['chunk_count']} | **{sum(e['score'] for e in evaluations)}/10** | "
            f"{sum(bool(e['relevant_ranks']) for e in evaluations)}/5 | "
            f"{sum(e['agent_correct'] for e in evaluations)}/5 |"
        )

    lines.extend(["", "## 2. Top-3, chunk coherence và grounding", ""])
    for name, run in strategy_runs.items():
        lines.extend([f"### Strategy `{name}`", ""])
        for case, evaluation in zip(BENCHMARK, run["evaluations"]):
            filter_note = f"; filter `{case.metadata_filter}`" if case.metadata_filter else ""
            lines.extend([
                f"#### Q{case.id}. {case.query}{filter_note}",
                "",
                f"Gold answer: {case.gold_answer}",
                "",
            ])
            render_result_rows(lines, evaluation, case)
            evidence_rank = evaluation["relevant_ranks"][0] if evaluation["relevant_ranks"] else "không có"
            complete_rank = evaluation["complete_ranks"][0] if evaluation["complete_ranks"] else "không có"
            lines.extend([
                "",
                f"- Precision: chunk chứa bằng chứng ở hạng **{evidence_rank}**.",
                f"- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **{complete_rank}**.",
                f"- Agent answer: {preview(evaluation['answer'], 500)}",
                f"- Grounding/điểm: agent {'đủ' if evaluation['agent_correct'] else 'thiếu'} bằng chứng; **{evaluation['score']}/2**.",
                "",
            ])

    filter_case = next(case for case in BENCHMARK if case.metadata_filter)
    lines.extend([
        "## 3. A/B metadata filter trên mọi strategy",
        "",
        f"Query: **{filter_case.query}**",
        "",
        "| Strategy | Không filter: top-3 | Có filter: top-3 | Kết quả đổi? | Điểm không/có filter | Metadata utility |",
        "|---|---|---|---|---:|---|",
    ])
    for name, run in strategy_runs.items():
        without_filter = run["filter_ab"]["without"]
        with_filter = run["filter_ab"]["with"]
        sig_without = top3_signature(without_filter)
        sig_with = top3_signature(with_filter)
        changed = sig_without != sig_with
        if with_filter["score"] > without_filter["score"]:
            utility = "Tăng precision/điểm"
        elif with_filter["score"] < without_filter["score"]:
            utility = "Giảm recall hoặc loại nhầm"
        elif changed:
            utility = "Loại nhiễu nhưng không đổi điểm"
        else:
            utility = "Query/corpus không thực sự cần filter"
        lines.append(
            f"| `{name}` | {sig_without} | {sig_with} | {'Có' if changed else 'Không'} | "
            f"{without_filter['score']}/{with_filter['score']} | {utility} |"
        )

    lines.extend([
        "",
        "## 4. Failure candidates có bằng chứng top-k",
        "",
    ])
    failures = []
    for name, run in strategy_runs.items():
        for case, evaluation in zip(BENCHMARK, run["evaluations"]):
            if evaluation["score"] < 2:
                failures.append((name, case, evaluation))
    if not failures:
        lines.append("Không có query dưới 2 điểm; cần tạo stress query thay vì tuyên bố hệ thống không có failure.")
    else:
        for name, case, evaluation in failures:
            lines.extend([
                f"### `{name}` - Q{case.id} ({evaluation['score']}/2)",
                "",
                f"- Query: {case.query}",
                f"- Top-3: {top3_signature(evaluation)}",
                f"- Bằng chứng: chuỗi `{case.evidence_marker}` ở hạng "
                f"{evaluation['relevant_ranks'][0] if evaluation['relevant_ranks'] else 'không xuất hiện'}.",
                f"- Dấu hiệu: {'đúng tài liệu nhưng sai/thiếu section' if not evaluation['relevant_ranks'] else 'chunk đáp án không ở top-1 nên agent trích xuất sai/thiếu'}.",
                "- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.",
                "",
            ])

    return "\n".join(lines).rstrip() + "\n"


def run_benchmark() -> int:
    embedder, backend, warning = select_embedder()
    strategy_runs: dict[str, dict] = {}
    filter_case = next(case for case in BENCHMARK if case.metadata_filter)

    for name, chunker in STRATEGIES.items():
        store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker)
        agent = KnowledgeBaseAgent(store=store, llm_fn=extractive_llm)
        evaluations = [
            evaluate(store, agent, case, use_filter=bool(case.metadata_filter))
            for case in BENCHMARK
        ]
        strategy_runs[name] = {
            "chunk_count": store.get_collection_size(),
            "evaluations": evaluations,
            "filter_ab": {
                "without": evaluate(store, agent, filter_case, use_filter=False),
                "with": evaluate(store, agent, filter_case, use_filter=True),
            },
        }

    OUTPUT_PATH.write_text(build_report(backend, warning, strategy_runs), encoding="utf-8")
    print(f"Embedding backend: {backend}")
    if warning:
        print(f"Warning: {warning}")
    for name, run in strategy_runs.items():
        total = sum(evaluation["score"] for evaluation in run["evaluations"])
        print(f"{name}: {run['chunk_count']} chunks, {total}/10")
    print(f"Wrote: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_benchmark())
