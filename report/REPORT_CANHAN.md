# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đinh Quang Minh
**Nhóm:** D305_B4_Lab07
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector đại diện cho hai đoạn văn bản có cùng hướng trong không gian embedding đa chiều, thể hiện sự tương đồng về ngữ nghĩa giữa hai đoạn văn bản đó bất kể độ dài văn bản khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên tiến hành đăng ký học phần trên cổng thông tin."
- Câu B: "Hướng dẫn đăng ký môn học trực tuyến dành cho sinh viên."
- Tại sao tương đồng: Cùng diễn đạt ý định đăng ký môn học trực tuyến của sinh viên bằng các từ ngữ đồng nghĩa.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Hôm nay thời tiết Hà Nội nắng đẹp và lộng gió."
- Câu B: "Hệ quản trị cơ sở dữ liệu vector lưu trữ các chuỗi embedding."
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn độc lập, không có sự liên quan về ngữ nghĩa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Độ tương tự cosine chỉ đo góc giữa 2 vector (hướng ngữ nghĩa) mà không bị ảnh hưởng bởi độ lớn/độ dài của vector. Trong khi đó, khoảng cách Euclid bị biến dạng khi hai văn bản cùng nội dung nhưng một văn bản dài gấp nhiều lần văn bản kia.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> $$\text{Số chunk} = \left\lceil \frac{\text{Độ dài tài liệu} - \text{Overlap}}{\text{Chunk size} - \text{Overlap}} \right\rceil = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \left\lceil 22.11 \right\rceil = 23$$
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước dịch chuyển nhỏ lại còn 400 ký tự, làm số lượng chunk tăng lên 25 chunks ($\lceil \frac{9900}{400} \rceil = 25$). Tăng overlap giúp hạn chế việc mất mát ngữ cảnh quan trọng nằm tại ranh giới cắt giữa các chunk liên tiếp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng biểu thức chính quy `re.split(r'(?<=[.!?])\s+', text)` để tách văn bản tại dấu câu kết thúc câu (`.`, `!`, `?`). Sau đó tiến hành strip làm sạch và nhóm tối đa `max_sentences_per_chunk` câu lại với nhau bằng khoảng trắng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Sử dụng thuật toán đệ quy thử lần lượt các separator theo ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Nếu đoạn văn vượt quá `chunk_size`, tiếp tục chia nhỏ theo separator cấp thấp hơn; trường hợp không còn separator thì cắt theo kích thước cố định `FixedSizeChunker`.

**`compute_similarity` và `ChunkingStrategyComparator`** — hướng tiếp cận:
> `compute_similarity` tính cosine bằng tích vô hướng chia cho tích hai chuẩn Euclid, đồng thời trả về `0.0` nếu một vector có độ lớn bằng 0 để tránh lỗi chia cho 0. `ChunkingStrategyComparator` chạy FixedSize, Sentence và Recursive trên cùng đầu vào, sau đó tổng hợp số chunk, độ dài trung bình và nội dung chunk để so sánh công bằng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Trong `add_documents`, tính vector embedding cho từng Document bằng `embedding_fn` và lưu vào bộ nhớ. Trong `search`, tính vector của `query`, sau đó gọi `compute_similarity` tính Cosine Similarity với tất cả các chunk lưu trữ và trả về top-k chunk điểm cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Trong `search_with_filter`, thực hiện lọc trước (pre-filtering) các chunk khớp với `metadata_filter`, sau đó mới tìm kiếm cosine similarity trong tập đã lọc. Trong `delete_document`, lọc bỏ tất cả record có `id` hoặc `metadata['doc_id']` trùng với `doc_id` cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Gọi `store.search` hoặc `store.search_with_filter` khi có `metadata_filter` để lấy `top_k` chunk liên quan nhất. Gộp nội dung các chunk làm ngữ cảnh (`context`), dựng prompt yêu cầu chỉ dùng context rồi truyền cho `llm_fn` để sinh câu trả lời RAG. Agent lưu `last_results` để benchmark có thể kiểm tra provenance của top-3.

### Xác nhận hoàn thành Tasks 1–3

| Task | Bằng chứng hoàn thành |
|---|---|
| Task 1 — Khởi động | Mục 1 giải thích cosine, ví dụ cao/thấp và tính toán chunking 10.000 ký tự. |
| Task 2 — Core implementation | Đã triển khai SentenceChunker, RecursiveChunker, cosine similarity, comparator, EmbeddingStore và KnowledgeBaseAgent; `pytest tests -q` đạt 42/42. |
| Task 3 — So sánh retrieval | Đã dùng 5 query QNU, FixedSizeChunker cá nhân, local multilingual embedding, chấm top-3 theo evidence chunk, A/B filter và failure analysis ở Mục 4–5. |

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Thời gian nghỉ Tết Nguyên đán Bình Ngọ năm 2026 | Sinh viên được nghỉ Tết từ ngày nào và học lại khi nào? | cao | **0.5742** | Đúng tương đối |
| 2 | Quy chế tuyển sinh trình độ đại học | QĐ1401 ban hành quy chế tuyển sinh đại học | cao | **0.8977** | Đúng |
| 3 | Mức thu học phí đào tạo đại học từ xa | Dự báo thời tiết Quy Nhơn hôm nay | thấp | **0.8466** | Sai về độ lớn |
| 4 | Học viên cao học Khóa 28B nộp học phí | Quy định tuyển sinh đại học | thấp | **0.5602** | Đúng tương đối |
| 5 | Hệ vừa làm vừa học khóa 34 | Ngành Quản lý đất đai tuyển sinh năm 2024 | cao | **0.5196** | Đúng tương đối |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là cặp học phí/thời tiết vẫn đạt **0.8466** dù khác chủ đề. Các điểm trên được đo thật bằng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Điều này cho thấy cosine score chỉ có ý nghĩa **tương đối trong cùng tập ứng viên**; score cao là tín hiệu xếp hạng, không tự chứng minh nội dung chứa đáp án. Cặp 1 và 5 cùng chủ đề nhưng không đạt quá cao vì câu ngắn và chỉ trùng một phần điều kiện, cũng cho thấy cần đánh giá bằng chunk evidence thay vì chỉ nhìn score.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Kết quả dùng corpus `data/qnu_regulations`, `FixedSizeChunker(chunk_size=800, overlap=150)` và model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Agent benchmark chỉ trích xuất chunk hạng 1; bảng top-3 đầy đủ nằm trong `report/benchmark_raw.md`.

| # | Top-3 chunk (score) | Bằng chứng/độ mạch lạc | Agent và điểm |
|---|---|---|---|
| 1 | TB209 (0.9038); TB209 (0.7437); TB1525 (0.6109) | Mốc nghỉ 03 tuần, 09/02–01/03 và học lại 02/03 ở top-1 | Đủ căn cứ — **2/2** |
| 2 | QĐ1401 (0.8515); QĐ1401 (0.7936); QyĐ474 (0.6847) | Điều 2 có hiệu lực/thay thế QĐ1455 ở top-1 | Đủ căn cứ — **2/2** |
| 3 | QyĐ828 (0.7749); QĐ1401 (0.7069); QyĐ474 (0.6741) | Chunk QyĐ474 có evidence ở top-3 (rank 3), không phải top-1 | Agent thiếu căn cứ — **1/2** |
| 4 | TB1525 (0.6157); TB1525 (0.6102); QyĐ474 (0.5908) | Không có chunk giữ đồng thời mốc nộp và cổng thanh toán trong top-3 | Không grounded — **0/2** |
| 5 | QyĐ828 (0.8118); TB1525 (0.7427); QyĐ474 (0.7263) | Top-1 có nội dung gần đáp án nhưng không có chuỗi evidence đã khai báo; không tính là evidence theo rubric | Không grounded theo evidence marker — **0/2** |

**Kết quả cá nhân:** **5/10**; **3/5** query có chunk chứa bằng chứng trong top-3, agent trả lời đủ từ top-1 ở **2/5** query.

### A/B metadata filter

Q2 dùng `metadata_filter={"audience": "student"}`. Với FixedSizeChunker, top-3 và điểm **giống hệt** khi có/không có filter: 2/2. Query đã nêu rất rõ QĐ1401 nên ứng viên đứng đầu vốn đã là tài liệu phù hợp; filter đúng schema nhưng không tạo lợi ích đo được trong corpus này.

### Failure case cá nhân

Q4 là failure rõ nhất: cả top-3 đều nói về học phí hoặc học viên cao học, nhưng không chunk nào giữ đồng thời mốc nộp `15/5/2026–02/8/2026` và cổng `e-bills.vn/pay/qnu`, nên đạt **0/2**. Top-1 TB1525 có score **0.6157** nhưng chỉ chứa hướng dẫn thanh toán, thiếu thời hạn. Đây là lỗi coherence: FixedSize cắt tách hai phần đáp án. Đề xuất: tăng overlap, giảm `chunk_size`, hoặc dùng chunking theo heading/đoạn cho thông báo TB1525 rồi benchmark lại.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chấm theo chuỗi bằng chứng trong chunk mới phát hiện được đúng/sai thật sự. Đúng `doc_id` hoặc cosine cao chưa đủ để kết luận agent có căn cứ.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 5 / 10 |
| **Tổng phần cá nhân** | **55 / 60** |
