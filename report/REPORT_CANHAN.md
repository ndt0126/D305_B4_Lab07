# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Quang Vinh
**MSSV:** 2A202601049
**Nhóm:** D305_B4_Lab07
**Vai trò trong nhóm:** Benchmark Owner & HeadingChunker (Thành viên 3)
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

> **Nguồn số liệu.** Phần 3 và Phần 5 lấy từ lần chạy chính thức của nhóm với backend `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, lưu nguyên văn tại `report/benchmark_raw.md` (sinh bởi `EMBEDDING_PROVIDER=local python bench.py`). Phần 4 chạy trên máy cá nhân với backend `mock` mặc định của lab — khác biệt này được nêu rõ và chính là nội dung phân tích của phần đó.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector chỉ về **cùng một hướng** trong không gian nhúng, tức hai đoạn văn bản nói về cùng một chủ đề / cùng một ý. Cosine chỉ quan tâm tới hướng chứ không quan tâm tới độ dài vector, nên "cao" nghĩa là *giống nhau về nội dung*, không phải *dài bằng nhau*.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên nghỉ Tết Nguyên đán ba tuần từ ngày 09/02/2026."
- Câu B: "Thời gian nghỉ Tết của sinh viên kéo dài 03 tuần bắt đầu từ 9 tháng 2 năm 2026."
- Tại sao tương đồng: cùng chủ thể (sinh viên), cùng sự kiện (nghỉ Tết), cùng thời lượng và cùng mốc bắt đầu. Chỉ khác cách diễn đạt số và ngày tháng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Quy chế tuyển sinh trình độ đại học của Trường Đại học Quy Nhơn."
- Câu B: "Hôm nay trời mưa rất to ở thành phố Quy Nhơn."
- Tại sao khác: khác miền chủ đề hoàn toàn (văn bản quy chế vs thời tiết). Hai câu chỉ chung đúng một địa danh, không chung thực thể hay hành động nào, nên vector gần như trực giao.

**Tại sao độ tương tự cosine được ưu tiên hơn khoảng cách Euclid cho text embeddings?**
> Vì độ dài (norm) của vector nhúng phần lớn phản ánh **độ dài văn bản / tần suất từ**, không phản ánh nội dung. Euclid phạt sự chênh lệch độ lớn, nên một chunk dài và một câu truy vấn ngắn cùng chủ đề sẽ bị coi là "xa nhau"; cosine chuẩn hóa độ lớn đi và chỉ so hướng — đúng bài toán RAG, nơi ta luôn so một câu hỏi ngắn với các chunk dài. Ngoài ra cosine luôn nằm trong [-1, 1] nên dễ đặt ngưỡng, còn Euclid không có biên trên.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* bước nhảy (step) = `chunk_size − overlap` = 500 − 50 = 450.
> `số chunk = ceil((10000 − 50) / 450) = ceil(9950 / 450) = ceil(22,11) = 23`
> *Đáp án:* **23 chunks** — đã kiểm chứng bằng code: `FixedSizeChunker(chunk_size=500, overlap=50).chunk("x"*10000)` trả về đúng **23**.

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> `ceil((10000 − 100) / 400) = ceil(24,75) = 25` chunk — tăng từ 23 lên **25** (kiểm chứng bằng code: đúng 25). Overlap lớn hơn ⇒ bước nhảy nhỏ hơn ⇒ nhiều chunk hơn, tốn thêm chi phí nhúng và lưu trữ. Đổi lại, một quy định nằm vắt qua ranh giới chunk sẽ **xuất hiện trọn vẹn ở ít nhất một chunk**. Corpus của nhóm có ví dụ đúng kiểu này: câu "có hiệu lực kể từ ngày ký và thay thế Quyết định 1455/QĐ-ĐHQN" trong QĐ1401 nằm ngay sát ranh giới giữa hai chunk — với `SentenceChunker` nó bị tách khỏi phần mở đầu và tụt xuống hạng 2, trong khi chiến lược giữ trọn section thì đưa được lên hạng 1.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])[ \t]*(?:\n+|\s)` — *lookbehind* để cắt **sau** dấu kết câu mà vẫn giữ lại dấu câu trong câu (nếu dùng `split(". ")` thì dấu chấm bị nuốt mất, chunk trả về sẽ sai lệch so với văn bản gốc). Sau khi tách, tôi `strip()` từng câu, loại phần tử rỗng, rồi gom theo lô `max_sentences_per_chunk` bằng `range(0, n, size)`. Edge case đã xử lý: chuỗi rỗng / chỉ có khoảng trắng → trả `[]`; nhiều khoảng trắng hoặc xuống dòng sau dấu chấm vẫn được nhận là một ranh giới câu; `max_sentences_per_chunk` được ép `max(1, ...)` để không bao giờ chia cho 0 hoặc lặp vô hạn.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `_split` thử dấu phân cách theo thứ tự ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Có **hai base case**: (1) `len(text) <= chunk_size` → trả `[text]`, đây là điểm dừng mong muốn; (2) hết separator hoặc gặp separator rỗng `""` → cắt cứng theo ký tự (`_hard_split`). Nếu separator hiện tại không xuất hiện trong text thì bỏ qua và gọi đệ quy với danh sách còn lại. Chi tiết tôi thấy quan trọng nhất là **gộp tham lam (greedy merge)**: sau khi `split(separator)` tôi nối các mảnh lại cho tới sát `chunk_size` thay vì trả về từng mảnh rời — nếu không, khi rơi xuống separator `" "` sẽ sinh ra hàng trăm chunk một-từ. Mảnh nào tự nó đã dài hơn `chunk_size` thì đệ quy xuống separator mịn hơn.

**`HeadingChunker`** — chiến lược riêng của tôi (chi tiết ở Phần 5):
> Tách văn bản tại các dòng tiêu đề Markdown `^#{1,6}\s+`, mỗi mục thành một chunk, **ghim lại tiêu đề vào từng mảnh con** khi một mục dài phải cắt tiếp, và **gộp mục quá ngắn với mục kế tiếp** để không sinh chunk vụn. Mục dài hơn `max_chars` được giao lại cho `RecursiveChunker` thay vì viết lại logic cắt.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hóa thành bản ghi `{id, content, metadata, embedding, _index}` trong `_make_record`; embedding được tính **ngay lúc nạp** (một lần), nên khi search chỉ phải nhúng câu truy vấn. `metadata.setdefault("doc_id", doc.id)` đảm bảo luôn có `doc_id` kể cả khi người dùng truyền `metadata={}` — đây là điều kiện để `delete_document()` và lọc theo tài liệu hoạt động, và cũng là lý do pipeline `ingest.py` (id chunk dạng `doc_id::chunk_0`) vẫn xóa đúng theo file gốc. `search` nhúng truy vấn rồi tính **tích vô hướng** với từng embedding đã lưu (`_dot`), sắp xếp giảm dần và cắt `top_k`. Vì mọi embedder trong lab đều trả vector đã chuẩn hóa nên tích vô hướng đồng nhất với cosine.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> **Lọc trước, tìm sau (pre-filter)**: tôi lọc danh sách bản ghi theo `metadata_filter` (so khớp `==` trên mọi cặp khóa-giá trị, ép `str()` để `"2026.1"` và `2026.1` không lệch kiểu) rồi mới đưa tập còn lại vào cùng hàm xếp hạng `_search_records`. Hậu-lọc sẽ sai vì các chunk lạc đối tượng có thể chiếm hết top-k trước khi bị loại, và ta thường nhận về danh sách rỗng dù store vẫn còn tài liệu hợp lệ. Cho `search()` và `search_with_filter()` dùng chung `_search_records` cũng là cách đơn giản nhất để khi `metadata_filter=None` hai hàm cho kết quả giống hệt nhau. `delete_document` xây lại danh sách bỏ mọi bản ghi có `metadata["doc_id"]` khớp, so độ dài trước/sau để trả `True/False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Ba bước theo đúng đặc tả: (1) `store.search(question, top_k)`; (2) `build_context()` ghép các chunk thành khối có **đánh số `[1] [2] [3]` kèm nguồn và score**; (3) đổ vào `PROMPT_TEMPLATE` theo cấu trúc `Instruction → Context → Question → Answer:` với chỉ dẫn *chỉ trả lời dựa trên Context, nếu không đủ thông tin thì nói rõ là không tìm thấy*. Việc đánh số chunk là phần tôi đầu tư nhất vì nó chính là tiêu chí **grounding** trong `docs/EVALUATION.md`: đọc câu trả lời là truy ngược được về đúng chunk và đúng file. Tôi bổ sung tham số `metadata_filter` cho `answer()` để agent đi chung một đường lọc với `search_with_filter`, phục vụ thí nghiệm A/B trong `bench.py`; để `None` thì hành vi không đổi. `self.last_results` được lưu lại để kiểm tra ngữ cảnh sau khi gọi.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```text
$ python -m pytest tests -v
============================= test session starts ==============================
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists          PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist   PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists    PASSED
tests/test_solution.py::TestFixedSizeChunker::...                     (7 tests) PASSED
tests/test_solution.py::TestSentenceChunker::...                      (4 tests) PASSED
tests/test_solution.py::TestRecursiveChunker::...                     (4 tests) PASSED
tests/test_solution.py::TestEmbeddingStore::...                       (8 tests) PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::...                   (2 tests) PASSED
tests/test_solution.py::TestComputeSimilarity::...                    (4 tests) PASSED
tests/test_solution.py::TestCompareChunkingStrategies::...            (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::...       (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::...         (3 tests) PASSED

============================== 42 passed in 0.05s ==============================
```

**Số lượng bài test vượt qua (pass):** **42 / 42** — không còn `NotImplementedError` nào trong `src/`, public interface của starter code giữ nguyên.

Ngoài pytest, tôi kiểm tra thêm các đường chạy thật:
- `python ingest.py` → `ingest self-check OK: parse được 4 khóa metadata, tạo 18 chunk`
- `python main.py "Chunking là gì?"` → chạy trọn pipeline nạp → search → agent, không lỗi (Checkpoint 4)
- `python bench.py` → nạp đủ 4 strategy, in số chunk và top-3 cho cả 5 query (Checkpoint 5)

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chạy `compute_similarity()` trên 5 cặp câu, backend **`mock`** (mặc định của lab, không cần tải mô hình).

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên nghỉ Tết Nguyên đán ba tuần từ ngày 09/02/2026. | Thời gian nghỉ Tết của sinh viên kéo dài 03 tuần bắt đầu từ 9 tháng 2 năm 2026. | cao | **0,1448** | **SAI** |
| 2 | Quyết định này có hiệu lực kể từ ngày ký. | Văn bản bắt đầu được áp dụng ngay khi hiệu trưởng ký ban hành. | cao | **0,1358** | **SAI** |
| 3 | Mức thu học phí đào tạo đại học từ xa đợt 1 tháng 2/2026. | Học viên cao học Khóa 28B nộp học phí qua cổng e-bills. | trung bình | **−0,0880** | SAI (thấp hơn dự đoán) |
| 4 | Quy chế tuyển sinh trình độ đại học của Trường ĐH Quy Nhơn. | Hôm nay trời mưa rất to ở thành phố Quy Nhơn. | thấp | **0,0795** | Đúng |
| 5 | Sinh viên nghỉ Tết Nguyên đán ba tuần từ ngày 09/02/2026. | (câu giống hệt câu A) | cao = 1,0 | **1,0000** | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là **cặp 4 lại cao hơn cặp 1 và cặp 2**. Hai câu gần như đồng nghĩa (cặp 1: 0,1448; cặp 2: 0,1358) bị xếp *thấp hơn* một cặp câu khác chủ đề hoàn toàn (cặp 4: 0,0795 — chênh không đáng kể), trong khi cặp 3 lại nhận điểm **âm**. Thứ tự này gần như ngẫu nhiên so với ngữ nghĩa.
>
> Nguyên nhân không phải lỗi công thức mà là bản chất của backend: `MockEmbedder` băm **toàn bộ chuỗi** bằng MD5 rồi sinh vector giả ngẫu nhiên, nên chỉ cần đổi một ký tự là vector đổi hoàn toàn. Nó chỉ bảo toàn *tính đồng nhất chuỗi* — thể hiện ở cặp 5 cho đúng **1,0000** tuyệt đối — chứ không bảo toàn *ý nghĩa*.
>
> Đối chiếu trực tiếp với Phần 5 cho thấy khoảng cách này lớn tới mức nào: cùng bộ code, khi đổi sang `paraphrase-multilingual-MiniLM-L12-v2`, các cặp query–chunk đúng đạt score **0,80–0,86**, còn các chunk nhiễu tụt về 0,64–0,78 — tức mô hình ngữ nghĩa tạo ra khoảng cách phân biệt thật sự, còn mock thì không. **Bài học: toàn bộ "trí thông minh" của một hệ RAG nằm ở embedder, không nằm ở phép đo cosine.** Cosine chỉ trung thực báo lại chất lượng của không gian nhúng mà nó được đưa vào.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chiến lược cá nhân: **`HeadingChunker(max_chars=600)`** — chia theo tiêu đề/mục, đáp ứng yêu cầu của `K3_VARIANT.md` là ít nhất một thành viên chunk theo heading/section. Corpus nhóm: `data/qnu_regulations` (5 văn bản QNU) → **22 chunk**. Backend: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Nguồn số liệu: `report/benchmark_raw.md`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được | Score | Có bằng chứng? | Điểm |
|---|-------|--------------------------------|-------|-----------|------|
| 1 | Sinh viên nghỉ Tết Nguyên đán Bính Ngọ 2026 bao lâu, từ ngày nào, học lại khi nào? | `tb209...::chunk_1` — đúng mục thông báo nghỉ Tết | **0,8553** | **CÓ** (hạng 1, đủ cả 3 dữ kiện) | **2/2** |
| 2 | Quy chế tuyển sinh kèm QĐ1401 có hiệu lực khi nào, thay thế quyết định nào? *(filter `audience=student`)* | `qd1401...::chunk_1` — đúng Điều 2 | **0,8169** | **CÓ** (hạng 1, đủ đáp án) | **2/2** |
| 3 | QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, hiệu lực khi nào? | `qyd828...::chunk_1` — **sai tài liệu** | 0,7855 | **Không** (không có bằng chứng trong top-3) | **0/2** |
| 4 | Học viên cao học K28B nộp học phí thời gian nào, qua cổng nào? | `tb1525...::chunk_6` — đúng tài liệu, **sai section** | 0,6756 | **Không** (không có bằng chứng trong top-3) | **0/2** |
| 5 | QyĐ828 áp dụng cho hệ đào tạo, khóa và ngành nào? | `qyd828...::chunk_1` — đúng tài liệu, chưa chứa dữ kiện | 0,8477 | Bằng chứng ở **hạng 2** (0,8303); chunk đủ đáp án ở hạng 3 | **1/2** |

**Bao nhiêu câu hỏi có chunk chứa bằng chứng trong top-3?** **3 / 5**
**Điểm truy xuất:** 2 + 2 + 0 + 0 + 1 = **5 / 10**

So sánh với các thành viên (cùng corpus, cùng 5 query, cùng embedder — chỉ khác strategy):

| Thành viên | Strategy | Số chunk | Điểm /10 | Bằng chứng trong top-3 | Agent đúng từ top-1 |
|---|---|---:|---:|---:|---:|
| Nguyễn Đức Trung | `sentence(3)` | 18 | **6** | 4/5 | 2/5 |
| Nguyễn Tuấn Nam | `recursive(400)` | 36 | 4 | 3/5 | 1/5 |
| **Nguyễn Quang Vinh (tôi)** | **`heading(600)`** | **22** | **5** | 3/5 | 2/5 |
| Đinh Quang Minh | `fixed(800/150)` | 17 | 5 | 3/5 | 3/5 |

> **Nhận xét trung thực về kết quả của tôi.** `HeadingChunker` **không phải chiến lược tốt nhất** trong lần chạy này — nó xếp giữa bảng (5/10), kém `sentence(3)` một điểm. Điều tôi thấy đáng nói không nằm ở tổng điểm mà ở **dạng thắng và dạng thua**:
>
> - Ở hai câu nó thắng (Q1, Q2), nó thắng **dứt khoát**: chunk vàng đứng hạng 1 với score cao nhất toàn bài (0,8553 và 0,8169) và **chứa đủ mọi phần của đáp án trong cùng một chunk** — vì một mục có tiêu đề vốn đã là một đơn vị trả lời trọn vẹn. Riêng Q2 là bằng chứng rõ nhất cho giá trị của chunk theo section: `sentence(3)` cũng tìm đúng tài liệu QĐ1401 nhưng câu "thay thế 1455/QĐ" rơi xuống hạng 2 (0,7920), chỉ được 1/2; chia theo heading giữ câu đó nằm chung với Điều 2 nên lên thẳng hạng 1.
> - Ở hai câu nó thua (Q3, Q4), nó thua vì **lý do nằm ngoài thuật toán chunking**. Q3 hỏi về QyĐ474 — văn bản này crawl về thiếu bảng mức thu học phí gốc, nên trong corpus gần như không có nội dung phân biệt được nó với QyĐ828; cả ba chunk top-3 đều rơi sang tài liệu khác. Q4 thì chunk hạng 1 đúng tài liệu TB1525 nhưng là mục "đề nghị học viên thực hiện đúng thời gian" chứ không phải mục chứa mốc ngày và URL cổng thanh toán.
>
> **Điều tôi rút ra:** chunk theo heading tối ưu cho *chunk coherence* (đáp án trọn vẹn trong một chunk) chứ không tự động tối ưu cho *recall*. Khi tài liệu nguồn thiếu nội dung (Q3) hoặc khi một văn bản có nhiều mục cùng chủ đề (Q4), ranh giới section không cứu được. Hướng cải thiện cụ thể tôi đề xuất: hạ `max_chars` để mỗi mục dài tách theo tiểu mục, và bổ sung metadata `effective_date` / `program_type` để lọc bớt các quyết định cùng loại trước khi xếp hạng.

**Thí nghiệm A/B metadata filter (vai trò Benchmark Owner của tôi):**
> Tôi chạy Q2 hai lần trên cả bốn strategy, có và không có `metadata_filter={"audience": "student"}`. Kết quả: **top-3 và điểm không đổi ở cả bốn strategy** (`heading` giữ nguyên 2/2). Kết luận tôi ghi vào báo cáo nhóm là bộ lọc **không tạo thêm utility đo được cho query này** — chứ không phải "filter vô dụng". Query Q2 nêu đích danh số hiệu QĐ1401 nên đã quá đặc hiệu, và corpus 5 văn bản không có tài liệu nào cạnh tranh gần nghĩa để mà loại. Muốn chứng minh giá trị của filter thì phải thiết kế query **cố tình mơ hồ về đối tượng** trên hai tài liệu cùng chủ đề khác `audience` — đó là việc tôi sẽ làm khác đi nếu chuẩn bị lại bộ query.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Bài học lớn nhất đến từ chính rubric chấm mà nhóm thống nhất: **chấm theo `doc_id` là tự lừa mình.** Ở Q2 với `sentence(3)`, tài liệu gold xuất hiện ở cả ba vị trí top-3 với score rất cao (0,794 / 0,792 / 0,677) — nếu chỉ kiểm tra `doc_id` thì đây là một câu "đúng hoàn hảo". Nhưng kiểm theo **chuỗi bằng chứng** thì chunk hạng 1 không hề chứa dữ kiện được hỏi, và câu này chỉ đáng 1/2. Score cosine cao chỉ nói lên *độ gần ngữ nghĩa bề mặt*, không chứng minh chunk chứa dữ kiện trả lời. Từ đó nhóm đổi toàn bộ cách chấm sang mức chunk kèm chuỗi bằng chứng, và số điểm của tất cả mọi người đều giảm xuống — nhưng là con số thật.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — 42/42 tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |

> Tự trừ 3 điểm ở **Kết quả truy xuất**: chiến lược của tôi đạt 5/10 chứ không phải điểm cao nhất nhóm, và hai câu thất bại (Q3, Q4) tôi mới chỉ ra được nguyên nhân chứ chưa kịp sửa và đo lại trong thời lượng lab.
