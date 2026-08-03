from __future__ import annotations

import hashlib
import html
import os
import re
from pathlib import Path
from typing import Any, Callable

# Avoid the optional TensorFlow/Keras path used by transformers on some
# Windows installations. The local sentence-transformers backend uses PyTorch.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

import streamlit as st

from ingest import build_knowledge_base, load_documents
from src import (
    FixedSizeChunker,
    HeadingChunker,
    KnowledgeBaseAgent,
    LocalEmbedder,
    RecursiveChunker,
    SentenceChunker,
)
from src.embeddings import LOCAL_EMBEDDING_MODEL, _mock_embed


APP_ROOT = Path(__file__).resolve().parent
DATA_ROOT = APP_ROOT / "data"

BACKENDS = {
    "Local đa ngữ · khuyến nghị": "local",
    "Mock · chạy nhanh": "mock",
}

STRATEGIES = {
    "Theo tiêu đề": "heading",
    "Đệ quy": "recursive",
    "Kích thước cố định": "fixed",
    "Theo câu": "sentence",
}

PRESET_QUERIES = [
    "Quyết định 1401 có hiệu lực khi nào và thay thế quyết định nào?",
    "QyĐ474 quy định mức học phí cho hệ đào tạo đại học từ xa tuyển sinh đợt nào?",
    "Quy định 828 áp dụng mức học phí cho khóa và ngành nào?",
    "Học viên cao học khóa 28B phải nộp học phí Học kỳ 2 đến khi nào?",
    "Sinh viên Trường Đại học Quy Nhơn nghỉ Tết Nguyên đán 2026 từ ngày nào đến ngày nào?",
]

STOPWORDS = {
    "ai", "bao", "bị", "các", "cho", "có", "của", "đâu", "đến", "được",
    "gì", "khi", "là", "nào", "những", "phải", "quy", "sinh", "theo",
    "thì", "từ", "và", "về", "viên",
}


st.set_page_config(
    page_title="QNU Retrieval Lab",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root {
        --ink: #15334a; --muted: #647586; --primary: #165d78;
        --accent: #0f9f8f; --paper: #ffffff; --line: #dbe5ec;
      }
      .stApp { background: #f4f7f9; color: var(--ink); }
      [data-testid="stSidebar"] { background: #eef4f6; border-right: 1px solid var(--line); }
      [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--ink); }
      .block-container { max-width: 1440px; padding-top: 1.35rem; padding-bottom: 3rem; }
      .demo-hero {
        padding: 1.25rem 1.4rem; border: 1px solid var(--line); border-radius: 18px;
        background: linear-gradient(120deg, #ffffff 0%, #edf8f7 100%);
        box-shadow: 0 10px 28px rgba(21, 51, 74, .06); margin-bottom: 1rem;
      }
      .demo-kicker { color: var(--accent); font-size: .78rem; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }
      .demo-title { color: var(--ink); font-size: 2rem; font-weight: 780; line-height: 1.15; margin: .3rem 0 .35rem; }
      .demo-subtitle { color: var(--muted); margin: 0; max-width: 820px; }
      .status-pill, .meta-pill {
        display: inline-block; border-radius: 999px; font-size: .76rem; font-weight: 650;
        padding: .24rem .58rem; margin: .12rem .25rem .12rem 0;
      }
      .status-pill { color: #0b675e; background: #dff5f1; border: 1px solid #bde9e1; }
      .meta-pill { color: #385266; background: #eef3f6; border: 1px solid #d9e3e9; }
      .result-rank { color: var(--accent); font-weight: 800; font-size: .8rem; letter-spacing: .06em; }
      div[data-testid="stMetric"] { background: var(--paper); border: 1px solid var(--line); padding: .8rem 1rem; border-radius: 14px; }
      div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255,255,255,.86); }
      .stButton > button, .stFormSubmitButton > button {
        border-radius: 10px; border-color: var(--primary); background: var(--primary);
        color: white; font-weight: 700;
      }
      .stButton > button:hover, .stFormSubmitButton > button:hover {
        border-color: var(--accent); background: var(--accent); color: white;
      }
      #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _discover_corpora() -> list[Path]:
    if not DATA_ROOT.exists():
        return []
    corpora = []
    for directory in sorted(path for path in DATA_ROOT.iterdir() if path.is_dir()):
        if any(path.suffix.lower() in {".md", ".txt"} for path in directory.rglob("*")):
            corpora.append(directory)
    return corpora


def _make_chunker(strategy: str, params: tuple[int, int]):
    first, second = params
    if strategy == "fixed":
        return FixedSizeChunker(chunk_size=first, overlap=second)
    if strategy == "sentence":
        return SentenceChunker(max_sentences_per_chunk=first)
    if strategy == "recursive":
        return RecursiveChunker(chunk_size=first)
    return HeadingChunker(min_level=first, max_level=second)


@st.cache_resource(show_spinner=False)
def _get_embedder(backend: str) -> tuple[Callable[[str], list[float]], str, str | None]:
    if backend == "mock":
        return _mock_embed, "Mock embeddings", None

    try:
        model_path = LOCAL_EMBEDDING_MODEL
        try:
            from huggingface_hub import snapshot_download

            model_path = snapshot_download(LOCAL_EMBEDDING_MODEL, local_files_only=True)
        except Exception:
            # On a fresh machine LocalEmbedder downloads the model normally.
            pass
        embedder = LocalEmbedder(model_name=model_path)
        return embedder, LOCAL_EMBEDDING_MODEL, None
    except Exception as exc:
        warning = f"Local embedder không sẵn sàng ({type(exc).__name__}); đã chuyển sang mock."
        return _mock_embed, "Mock fallback", warning


@st.cache_resource(show_spinner=False)
def _build_store_cached(
    data_dir: str,
    backend: str,
    strategy: str,
    params: tuple[int, int],
):
    embedder, backend_label, warning = _get_embedder(backend)
    chunker = _make_chunker(strategy, params)
    fingerprint = hashlib.md5(
        f"{data_dir}|{backend}|{strategy}|{params}".encode("utf-8")
    ).hexdigest()[:10]
    store = build_knowledge_base(
        data_dir,
        embedding_fn=embedder,
        chunker=chunker,
        collection_name=f"ui_{fingerprint}",
    )
    return store, backend_label, warning


def _tokens(text: str) -> set[str]:
    words = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    return {word for word in words if len(word) > 2 and word not in STOPWORDS}


def _extractive_llm(prompt: str) -> str:
    """Return grounded sentences from the retrieved context without an API key."""
    context_match = re.search(r"Ngữ cảnh:\s*(.*?)\s*Câu hỏi:", prompt, flags=re.DOTALL)
    question_match = re.search(r"Câu hỏi:\s*(.*?)\s*Trả lời:", prompt, flags=re.DOTALL)
    context = context_match.group(1).strip() if context_match else ""
    question = question_match.group(1).strip() if question_match else ""
    if not context:
        return "Không đủ thông tin trong ngữ cảnh truy xuất."

    query_tokens = _tokens(question)
    candidates = [
        sentence.strip(" \n\t-•")
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", context)
        if 30 <= len(sentence.strip()) <= 600
    ]
    def sentence_score(sentence: str) -> int:
        lowered_question = question.lower()
        lowered_sentence = sentence.lower()
        score = len(_tokens(sentence) & query_tokens) * 3
        if any(cue in lowered_question for cue in ("khi nào", "ngày nào", "đến khi nào")):
            if re.search(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", sentence):
                score += 8
            elif "ngày" in lowered_sentence:
                score += 3
        for cue in ("thay thế", "đợt", "mức học phí", "thời gian nộp"):
            if cue in lowered_question and cue in lowered_sentence:
                score += 5
        if "nộp học phí" in lowered_question and "thời gian nộp học phí" in lowered_sentence:
            score += 15
        if "nghỉ tết" in lowered_question and "nghỉ tết" in lowered_sentence:
            score += 8
        return score

    ranked = sorted(
        enumerate(candidates),
        key=lambda item: (sentence_score(item[1]), -len(item[1]), -item[0]),
        reverse=True,
    )
    selected = [sentence for _, sentence in ranked[:2] if sentence]
    if not selected:
        return "Không đủ thông tin trong ngữ cảnh truy xuất."
    return " ".join(selected)


class _PrecomputedResultsStore:
    """Adapter so KnowledgeBaseAgent uses the filtered UI results."""

    def __init__(self, results: list[dict[str, Any]]) -> None:
        self.results = results

    def search(self, _question: str, top_k: int = 3) -> list[dict[str, Any]]:
        return self.results[:top_k]


def _metadata_filter_widget(documents) -> dict[str, str]:
    st.sidebar.markdown("### Bộ lọc metadata")
    metadata_filter: dict[str, str] = {}
    for key, label in (
        ("audience", "Đối tượng"),
        ("program", "Hệ đào tạo"),
        ("department", "Đơn vị"),
        ("topic", "Chủ đề"),
        ("category", "Danh mục"),
        ("language", "Ngôn ngữ"),
        ("doc_id", "Tài liệu"),
    ):
        values = sorted({str(doc.metadata[key]) for doc in documents if doc.metadata.get(key)})
        if not values:
            continue
        choice = st.sidebar.selectbox(label, ["Tất cả", *values], key=f"filter_{key}")
        if choice != "Tất cả":
            metadata_filter[key] = choice
    return metadata_filter


def _render_result(result: dict[str, Any], rank: int) -> None:
    metadata = result.get("metadata", {})
    score = float(result.get("score", 0.0))
    title = metadata.get("title") or metadata.get("doc_id") or result.get("id", "Tài liệu")
    source_url = metadata.get("source_url")

    with st.container(border=True):
        heading_col, score_col = st.columns([5, 1])
        with heading_col:
            st.markdown(f'<div class="result-rank">KẾT QUẢ #{rank}</div>', unsafe_allow_html=True)
            st.markdown(f"#### {title}")
        with score_col:
            st.metric("Score", f"{score:.4f}")

        chips = []
        for key in (
            "doc_id", "audience", "program", "department", "topic",
            "category", "language", "chunk_index",
        ):
            if metadata.get(key) is not None:
                chips.append(
                    f'<span class="meta-pill">{html.escape(key)}: {html.escape(str(metadata[key]))}</span>'
                )
        st.markdown("".join(chips), unsafe_allow_html=True)
        st.write(result.get("content", ""))
        if source_url:
            st.markdown(f"[Mở nguồn gốc ↗]({source_url})")


corpora = _discover_corpora()
if not corpora:
    st.error("Không tìm thấy corpus .md/.txt trong thư mục data/.")
    st.stop()

default_corpus = next((path for path in corpora if path.name == "qnu_regulations"), corpora[0])

with st.sidebar:
    st.markdown("## ◈ Retrieval Lab")
    st.caption("Điều khiển pipeline demo")

    corpus_path = st.selectbox(
        "Corpus", corpora, index=corpora.index(default_corpus), format_func=lambda path: path.name
    )
    backend_label = st.radio(
        "Embedding backend",
        list(BACKENDS),
        index=1 if os.getenv("RAG_UI_DEFAULT_BACKEND", "local") == "mock" else 0,
    )
    strategy_label = st.selectbox("Chiến lược chunking", list(STRATEGIES))
    strategy = STRATEGIES[strategy_label]

    if strategy == "fixed":
        chunk_size = st.slider("Chunk size", 200, 1200, 500, 50)
        overlap = st.slider("Overlap", 0, min(300, chunk_size - 1), min(80, chunk_size - 1), 10)
        strategy_params = (chunk_size, overlap)
    elif strategy == "sentence":
        sentence_count = st.slider("Số câu mỗi chunk", 1, 8, 3)
        strategy_params = (sentence_count, 0)
    elif strategy == "recursive":
        recursive_size = st.slider("Chunk size", 200, 1200, 600, 50)
        strategy_params = (recursive_size, 0)
    else:
        min_level = st.slider("Heading nhỏ nhất", 1, 5, 1)
        max_level = st.slider("Heading lớn nhất", min_level, 6, 3)
        strategy_params = (min_level, max_level)

documents = load_documents(corpus_path)
metadata_filter = _metadata_filter_widget(documents)

with st.sidebar:
    top_k = st.slider("Số kết quả top-k", 1, 8, 3)
    if st.button("Làm mới cache", width="stretch"):
        st.cache_resource.clear()
        st.session_state.pop("last_search", None)
        st.session_state.pop("comparison", None)
        st.rerun()

st.markdown(
    """
    <section class="demo-hero">
      <div class="demo-kicker">Lab 07 · RAG demonstration</div>
      <div class="demo-title">QNU Retrieval Lab</div>
      <p class="demo-subtitle">Khám phá cách chunking, embedding và metadata filter thay đổi kết quả truy xuất trên bộ quy định đại học.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.spinner("Đang chuẩn bị knowledge base…"):
    store, active_backend, backend_warning = _build_store_cached(
        str(corpus_path), BACKENDS[backend_label], strategy, strategy_params
    )

if backend_warning:
    st.warning(backend_warning)

metric_cols = st.columns(4)
metric_cols[0].metric("Tài liệu", len(documents))
metric_cols[1].metric("Chunks", store.get_collection_size())
metric_cols[2].metric("Chiến lược", strategy_label)
metric_cols[3].metric("Top-k", top_k)
st.markdown(
    f'<span class="status-pill">● {html.escape(active_backend)}</span>'
    f'<span class="status-pill">Corpus: {html.escape(corpus_path.name)}</span>',
    unsafe_allow_html=True,
)

search_tab, compare_tab, corpus_tab = st.tabs(
    ["Tra cứu RAG", "So sánh chiến lược", "Corpus & metadata"]
)

with search_tab:
    st.subheader("Đặt câu hỏi cho knowledge base")
    preset = st.selectbox("Câu hỏi mẫu", ["Tự nhập", *PRESET_QUERIES])
    default_query = "" if preset == "Tự nhập" else preset
    query_key = "custom_query" if preset == "Tự nhập" else f"preset_{PRESET_QUERIES.index(preset)}"

    with st.form("search_form"):
        query = st.text_area(
            "Câu hỏi", value=default_query, key=query_key, height=92,
            placeholder="Ví dụ: Học viên cao học khóa 28B nộp học phí đến ngày nào?",
        )
        submitted = st.form_submit_button("Tìm kiếm & trả lời", width="stretch")

    if submitted:
        if not query.strip():
            st.warning("Hãy nhập một câu hỏi trước khi tìm kiếm.")
        else:
            with st.spinner("Đang nhúng truy vấn và xếp hạng chunks…"):
                if metadata_filter:
                    results = store.search_with_filter(
                        query.strip(), top_k=top_k, metadata_filter=metadata_filter
                    )
                else:
                    results = store.search(query.strip(), top_k=top_k)
                agent = KnowledgeBaseAgent(_PrecomputedResultsStore(results), _extractive_llm)
                answer = agent.answer(query.strip(), top_k=top_k)
                st.session_state["last_search"] = {
                    "query": query.strip(), "results": results,
                    "answer": answer, "filter": dict(metadata_filter),
                }

    last_search = st.session_state.get("last_search")
    if last_search:
        st.markdown("### Câu trả lời có căn cứ")
        st.info(last_search["answer"], icon="🔎")
        st.caption(
            "Agent trích xuất câu từ context top-k; không dùng API sinh văn bản. "
            f"Filter: {last_search['filter'] or 'không'}"
        )
        st.markdown(f"### {len(last_search['results'])} chunks được truy xuất")
        if not last_search["results"]:
            st.warning("Không có chunk nào khớp bộ lọc hiện tại.")
        for rank, result in enumerate(last_search["results"], start=1):
            _render_result(result, rank)
    else:
        st.caption("Chọn một câu hỏi mẫu hoặc nhập câu hỏi để bắt đầu demo.")

with compare_tab:
    st.subheader("Cùng một câu hỏi, bốn cách chunking")
    st.write("So sánh số chunk và top-1 trên cùng corpus, backend, câu hỏi và metadata filter.")
    comparison_query = st.text_input(
        "Câu hỏi dùng để so sánh",
        value=st.session_state.get("last_search", {}).get("query", PRESET_QUERIES[3]),
    )
    if st.button("Chạy so sánh", width="stretch"):
        comparison_configs = {
            "Theo tiêu đề": ("heading", (1, 3)),
            "Đệ quy 600": ("recursive", (600, 0)),
            "Fixed 500/80": ("fixed", (500, 80)),
            "Theo 3 câu": ("sentence", (3, 0)),
        }
        rows = []
        with st.spinner("Đang xây bốn knowledge base và chạy cùng truy vấn…"):
            for label, (key, params) in comparison_configs.items():
                candidate_store, _, candidate_warning = _build_store_cached(
                    str(corpus_path), BACKENDS[backend_label], key, params
                )
                if metadata_filter:
                    candidate_results = candidate_store.search_with_filter(
                        comparison_query, top_k=top_k, metadata_filter=metadata_filter
                    )
                else:
                    candidate_results = candidate_store.search(comparison_query, top_k=top_k)
                top = candidate_results[0] if candidate_results else {}
                top_meta = top.get("metadata", {})
                rows.append({
                    "Chiến lược": label,
                    "Số chunk": candidate_store.get_collection_size(),
                    "Top-1 score": round(float(top.get("score", 0.0)), 4),
                    "Top-1 doc": top_meta.get("doc_id", "—"),
                    "Backend": "fallback" if candidate_warning else active_backend,
                })
        st.session_state["comparison"] = rows

    if st.session_state.get("comparison"):
        st.dataframe(st.session_state["comparison"], width="stretch", hide_index=True)
        st.caption(
            "Score cao chưa đủ để kết luận: hãy mở tab Tra cứu RAG và kiểm tra nội dung chunk có thực sự chứa đáp án."
        )

with corpus_tab:
    st.subheader("Kiểm kê tài liệu và khả năng truy vết")
    required_metadata = {
        "doc_id", "title", "source_url", "retrieved_at",
        "document_version", "audience",
    }
    inventory = []
    missing_total = 0
    for document in documents:
        missing = sorted(key for key in required_metadata if not document.metadata.get(key))
        missing_total += len(missing)
        inventory.append({
            "doc_id": document.id,
            "Tiêu đề": document.metadata.get("title", "—"),
            "Ký tự": len(document.content),
            "audience": document.metadata.get("audience", "—"),
            "program": document.metadata.get("program", "—"),
            "department": document.metadata.get("department", "—"),
            "topic": document.metadata.get("topic", "—"),
            "category": document.metadata.get("category", "—"),
            "Phiên bản": document.metadata.get("document_version", "—"),
            "Thiếu metadata": ", ".join(missing) if missing else "Không",
            "Nguồn": document.metadata.get("source_url", "—"),
        })

    quality_cols = st.columns(3)
    quality_cols[0].metric(
        "Số tài liệu", len(documents),
        "Đạt 5–10" if 5 <= len(documents) <= 10 else "Cần kiểm tra",
    )
    quality_cols[1].metric("Trường metadata thiếu", missing_total)
    quality_cols[2].metric(
        "Có source URL", sum(bool(doc.metadata.get("source_url")) for doc in documents)
    )
    st.dataframe(inventory, width="stretch", hide_index=True)
    st.caption("Mọi kết quả ở tab Tra cứu đều hiển thị doc_id, metadata và URL để kiểm chứng grounding.")
