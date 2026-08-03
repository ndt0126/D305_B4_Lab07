# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vinh
**Nhóm:** [Điền tên nhóm]
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Cosine similarity cao cho thấy hai vector embedding có hướng gần nhau. Vì embedding mã hóa nội dung thành vector, điều này thường phản ánh hai đoạn văn có ý nghĩa hoặc chủ đề tương tự.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên có thể gia hạn sách tại thư viện.
- Câu B: Người học được phép kéo dài thời hạn mượn sách.
- Tại sao tương đồng: Cả hai câu đều nói về việc gia hạn thời gian mượn sách, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên có thể gia hạn sách tại thư viện.
- Câu B: Hôm nay trời mưa rất lớn.
- Tại sao khác: Hai câu đề cập đến hai chủ đề không liên quan nên vector biểu diễn của chúng sẽ có hướng khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity so sánh góc giữa các vector, vì vậy chú trọng vào hướng biểu diễn ý nghĩa thay vì độ lớn của vector. Đây là đặc điểm phù hợp với text embedding, nơi hai văn bản cùng nghĩa có thể có độ lớn vector khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap = 100, số chunk là ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks. Overlap lớn hơn giúp giữ được ngữ cảnh tại ranh giới giữa các chunk, nhưng cũng làm tăng phần nội dung lặp lại và chi phí lưu trữ, tìm kiếm.

---
## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Tôi triển khai lần lượt các thành phần trong `src/chunking.py`, `src/store.py` và `src/agent.py`, sau đó chạy unit test theo từng nhóm chức năng trước khi chạy toàn bộ 42 test.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng đứng sau dấu kết thúc câu, sau đó loại câu rỗng và khoảng trắng thừa. Danh sách câu được nhóm theo từng lát có tối đa `max_sentences_per_chunk`; đầu vào rỗng hoặc chỉ chứa khoảng trắng trả về `[]`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử các separator theo thứ tự ưu tiên `"\n\n"`, `"\n"`, `". "`, `" "` rồi `""`, đồng thời ghép các phần nhỏ vào buffer nếu chưa vượt `chunk_size`. Base case là text rỗng, text đã ngắn hơn giới hạn, hoặc không còn separator; trường hợp cuối được cắt trực tiếp theo số ký tự. Phần nào vẫn quá dài được xử lý đệ quy bằng các separator còn lại.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hóa thành record gồm ID duy nhất, content, bản sao metadata và embedding; `doc_id` được bổ sung từ `Document.id` nếu metadata chưa có. Khi tìm kiếm trong bộ nhớ, truy vấn được nhúng một lần, tính dot product với từng record, sắp xếp score giảm dần và lấy tối đa `top_k`. Code cũng hỗ trợ ChromaDB nếu thư viện này khả dụng.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc tập ứng viên theo toàn bộ cặp key-value trong metadata trước khi tính similarity, nhờ đó kết quả sai đối tượng không chiếm top-k. `delete_document` xóa tất cả record có `metadata["doc_id"]` trùng ID yêu cầu và trả về `True` chỉ khi kích thước store thực sự giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent gọi `store.search()` để lấy top-k chunk, ghép nội dung các chunk thành context rồi tạo prompt gồm chỉ dẫn grounding, context, câu hỏi và vị trí trả lời. Prompt yêu cầu không suy đoán khi ngữ cảnh không đủ, sau đó được truyền cho `llm_fn` để giữ lớp agent độc lập với nhà cung cấp LLM cụ thể.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

**Lệnh đã chạy thực tế:** `pytest tests/ -v`

```text
> pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.12.5, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\VinUniLab\Lab7\D305_B4_Lab07
plugins: anyio-4.12.0, dash-3.2.0, langsmith-0.10.15, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== warnings summary ===============================
..\..\..\Users\Admin\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\cacheprovider.py:469
  C:\Users\Admin\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\cacheprovider.py:469: PytestCacheWarning: could not create cache path C:\VinUniLab\Lab7\D305_B4_Lab07\.pytest_cache\v\cache\nodeids: [WinError 5] Access is denied: 'C:\\VinUniLab\\Lab7\\D305_B4_Lab07\\.pytest_cache\\v\\cache'
    config.cache.set("cache/nodeids", sorted(self.cached_nodeids))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 42 passed, 1 warning in 0.08s ========================
```

Cảnh báo duy nhất là `PytestCacheWarning` do môi trường không có quyền ghi `.pytest_cache`; cảnh báo không ảnh hưởng kết quả kiểm thử.

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

**Cấu hình đo:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; quy ước score từ `0.5` trở lên là CAO.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên nghỉ Tết từ ngày 09 tháng 02 năm 2026. | Thời gian nghỉ Tết của sinh viên bắt đầu ngày 09/02/2026. | CAO | 0.8670 | Có |
| 2 | Học viên nộp học phí qua cổng thanh toán trực tuyến. | Người học thanh toán học phí bằng hệ thống trực tuyến. | CAO | 0.8451 | Có |
| 3 | Quyết định tuyển sinh có hiệu lực kể từ ngày ký. | Văn bản tuyển sinh bắt đầu có hiệu lực vào ngày ký. | CAO | 0.6158 | Có |
| 4 | Sinh viên nghỉ Tết trong ba tuần. | Học phí được thanh toán bằng mã QR. | THẤP | 0.0620 | Có |
| 5 | Quy định học phí áp dụng cho hệ đào tạo từ xa. | Sinh viên phải bảo vệ tài sản cá nhân trong kỳ nghỉ. | THẤP | 0.2119 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 khác mục đích nhưng vẫn có score 0.2119 thay vì gần 0 tuyệt đối, có thể vì cả hai cùng thuộc ngữ cảnh quy định dành cho sinh viên. Cặp 3 là hai cách diễn đạt gần nghĩa nhưng chỉ đạt 0.6158, thấp hơn hai cặp paraphrase còn lại; điều này cho thấy embedding nắm được ý nghĩa tổng quát nhưng điểm số vẫn chịu ảnh hưởng bởi cách dùng từ và mức độ trùng khớp ngữ cảnh.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Corpus:** 5 tài liệu công khai trong `data/qnu_regulations/`.

**Cấu hình:** `HeadingChunker(min_level=1, max_level=3)` tạo 6 chunk; embedding local `paraphrase-multilingual-MiniLM-L12-v2`; `top_k=3`. Q3 dùng `program=part-time`, Q4 dùng `program=graduate`, Q5 dùng `audience=student`. `llm_fn` trong phép đo là hàm kiểm tra grounding xác định: chỉ trả về gold answer khi top-3 context thực sự chứa cụm bằng chứng, nếu không sẽ trả lời “Không đủ thông tin”.

> Năm câu hỏi dưới đây là bộ benchmark đề xuất để chuyển nguyên sang `REPORT_NHOM.md`, bảo đảm kết quả cá nhân và kết quả nhóm dùng cùng câu hỏi.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Quyết định 1401 có hiệu lực khi nào và thay thế quyết định nào? | QĐ1401 — phần hiệu lực và văn bản bị thay thế | 0.4893 | Có — top-1 | Có hiệu lực từ ngày ký; thay thế QĐ1455/QĐ-ĐHQN ngày 21/5/2025. |
| 2 | QyĐ474 quy định mức học phí cho hệ đào tạo đại học từ xa tuyển sinh đợt nào? | QyĐ474 — học phí đại học từ xa tuyển sinh tháng 2/2026 | 0.8007 | Có — top-1 | Áp dụng cho tuyển sinh tháng 2 năm 2026, đợt 1. |
| 3 | Quy định 828 áp dụng mức học phí cho khóa và ngành nào? | QyĐ828 — hệ vừa làm vừa học khóa 34, ngành Quản lý đất đai | 0.6047 | Có — top-1 | Áp dụng cho khóa 34 ngành Quản lý đất đai, tuyển sinh năm 2024. |
| 4 | Học viên cao học khóa 28B phải nộp học phí Học kỳ 2 đến khi nào? | TB1525 — lịch học và nộp học phí của khóa 28B | 0.7628 | Có — top-1 | Nộp từ ngày 15/5/2026 đến hết ngày 02/8/2026. |
| 5 | Sinh viên Trường Đại học Quy Nhơn nghỉ Tết Nguyên đán 2026 từ ngày nào đến ngày nào? | TB209 — thời gian nghỉ Tết Bính Ngọ 2026 | 0.7740 | Có — top-1 | Nghỉ từ ngày 09/02/2026 đến hết ngày 01/03/2026. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5
**Bao nhiêu câu hỏi trả về chunk có liên quan ở top-1?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chưa thể ghi nhận trung thực trước khi phần demo nhóm diễn ra. Tôi sẽ bổ sung 2–3 câu vào mục này ngay sau khi nghe và đối chiếu chiến lược của các thành viên/nhóm khác.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |

> Lưu ý trước khi nộp: điền tên nhóm ở đầu báo cáo và bổ sung phần phản ánh sau demo; các số liệu code, similarity và retrieval ở trên đã được đo bằng mã nguồn hiện tại.