"""
bench.py — Script chạy benchmark 5 câu hỏi đánh giá với bộ dữ liệu data/qnu_regulations
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from ingest import build_knowledge_base
from src.chunking import SentenceChunker
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
    data_dir = "data/qnu_regulations"
    
    chunker = SentenceChunker(max_sentences_per_chunk=3)
    strategy_name = f"{chunker.__class__.__name__}(max_sentences={getattr(chunker, 'max_sentences_per_chunk', 3)})"
    
    print(f"==================================================")
    print(f"=== BENCHMARK STRATEGY: {strategy_name} ===")
    print(f"=== DATASET: {data_dir} ===")
    print(f"==================================================")
    
    store = build_knowledge_base(data_dir, embedding_fn, chunker=chunker)
    total_chunks = store.get_collection_size()
    print(f"--> Đã nạp thành công {total_chunks} chunks vào EmbeddingStore từ '{data_dir}'\n")
    
    queries = [
        {
            "id": 1,
            "query": "Sinh viên được nghỉ Tết Nguyên đán Bính Ngọ năm 2026 trong thời gian bao lâu và bắt đầu từ ngày nào?",
            "filter": None,
        },
        {
            "id": 2,
            "query": "Quy chế tuyển sinh trình độ đại học của Trường Đại học Quy Nhơn ban hành kèm theo quyết định số bao nhiêu?",
            "filter": None,
        },
        {
            "id": 3,
            "query": "Mức thu học phí đào tạo đại học từ xa tuyển sinh đợt 1 tháng 2 năm 2026 là bao nhiêu?",
            "filter": {"audience": "student"},
        },
        {
            "id": 4,
            "query": "Thời gian học tập và nộp học phí Học kỳ 2 đợt 2 đối với học viên cao học Khóa 28B quy định thế nào?",
            "filter": None,
        },
        {
            "id": 5,
            "query": "Mức thu học phí ngành Quản lý đất đai khóa 34 tuyển sinh năm 2024 áp dụng cho hệ đào tạo nào?",
            "filter": None,
        },
    ]

    agent = KnowledgeBaseAgent(
        store=store, 
        llm_fn=lambda prompt: "Dựa trên ngữ cảnh: " + prompt.split("Context:\n")[1].split("\n\nQuestion:")[0].replace("\n", " ")[:200] + "..."
    )

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
