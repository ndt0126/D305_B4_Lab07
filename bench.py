"""
bench.py — Script chạy benchmark 5 câu hỏi đánh giá với chiến lược retrieval riêng.

Chạy lệnh:
    python bench.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from ingest import build_knowledge_base
from src.chunking import SentenceChunker, FixedSizeChunker, RecursiveChunker
from src.embeddings import _mock_embed, LocalEmbedder
from src.agent import KnowledgeBaseAgent

load_dotenv()

def get_embedder():
    provider = os.getenv("EMBEDDING_PROVIDER", "mock").lower()
    if provider == "local":
        try:
            return LocalEmbedder()
        except Exception as e:
            print(f"[Warning] Could not load LocalEmbedder ({e}), falling back to mock.")
            return _mock_embed
    return _mock_embed

def run_benchmark():
    embedding_fn = get_embedder()
    data_dir = "data/k3_university"
    
    # 1. Chọn chiến lược chunker cá nhân (Ví dụ: SentenceChunker với max_sentences_per_chunk=3)
    chunker = SentenceChunker(max_sentences_per_chunk=3)
    strategy_name = f"{chunker.__class__.__name__}(max_sentences={getattr(chunker, 'max_sentences_per_chunk', 3)})"
    
    print(f"==================================================")
    print(f"=== BENCHMARK STRATEGY: {strategy_name} ===")
    print(f"==================================================")
    
    # 2. Nạp toàn bộ kho dữ liệu
    store = build_knowledge_base(data_dir, embedding_fn, chunker=chunker)
    total_chunks = store.get_collection_size()
    print(f"--> Đã nạp thành công {total_chunks} chunks vào EmbeddingStore từ '{data_dir}'\n")
    
    # 3. Danh sách 5 Benchmark Queries thống nhất của nhóm
    queries = [
        {
            "id": 1,
            "query": "Sinh viên được đăng ký tối thiểu và tối đa bao nhiêu tín chỉ trong một học kỳ chính?",
            "filter": None,
        },
        {
            "id": 2,
            "query": "Phí phạt khi trả sách thư viện quá hạn là bao nhiêu và khi nào tài khoản bị khóa?",
            "filter": None,
        },
        {
            "id": 3,
            "query": "Điều kiện về GPA và điểm rèn luyện để đạt học bổng Khuyến khích loại Xuất sắc là gì?",
            "filter": {"audience": "student"},
        },
        {
            "id": 4,
            "query": "Thời gian xin gia hạn nộp học phí tối đa là bao lâu và cần những hồ sơ gì?",
            "filter": None,
        },
        {
            "id": 5,
            "query": "Ký túc xá mở cửa và đóng cửa vào khung giờ nào hàng ngày?",
            "filter": None,
        },
    ]

    agent = KnowledgeBaseAgent(store=store, llm_fn=lambda prompt: "Dựa trên ngữ cảnh: " + prompt.split("Context:\n")[1].split("\n\nQuestion:")[0].replace("\n", " ")[:200] + "...")

    # 4. Thực thi từng Query và in kết quả Top-3
    for q in queries:
        qid = q["id"]
        query_text = q["query"]
        metadata_filter = q["filter"]
        
        print(f"--------------------------------------------------")
        print(f"Query [{qid}]: \"{query_text}\"")
        if metadata_filter:
            print(f"Filter: {metadata_filter}")
            results = store.search_with_filter(query_text, top_k=3, metadata_filter=metadata_filter)
        else:
            results = store.search(query_text, top_k=3)
            
        print(f"Top-3 Chunks Trả về:")
        for rank, r in enumerate(results, start=1):
            doc_id = r.get("metadata", {}).get("doc_id", r.get("id"))
            score = r.get("score", 0.0)
            content_preview = r.get("content", "").replace("\n", " ")[:100]
            print(f"  [{rank}] Score: {score:.4f} | doc_id: {doc_id} | Preview: \"{content_preview}...\"")
            
        answer = agent.answer(query_text, top_k=3)
        print(f"Agent Answer (tóm tắt): {answer[:150]}...\n")

if __name__ == "__main__":
    run_benchmark()
