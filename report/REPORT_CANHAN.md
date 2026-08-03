# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vinh
**Nhóm:** [Điền tên nhóm]
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

> **Điều kiện chạy của báo cáo này:** backend nhúng = `mock embeddings fallback` (MD5 → vector), corpus = 2 tài liệu khởi động trong `data/k3_university/`. Mọi con số trong báo cáo là kết quả đo thật, sinh tự động bởi `scripts/run_benchmark.py` và lưu ở `report/benchmark_raw.md`. Vì mock **không mang ngữ nghĩa**, các nhận định về chất lượng truy xuất được diễn giải một cách thận trọng — xem Phần 5.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector chỉ về **cùng một hướng** trong không gian nhúng, tức là hai đoạn văn bản nói về cùng một chủ đề / cùng một ý. Cosine chỉ quan tâm tới hướng, không quan tâm tới độ dài vector, nên "cao" nghĩa là *giống nhau về nội dung*, không phải *dài bằng nhau*.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký học phần trong cổng học vụ."
- Câu B: "Việc đăng ký môn học được thực hiện trên cổng thông tin học vụ."
- Tại sao tương đồng: cùng chủ thể (sinh viên), cùng hành động (đăng ký môn/học phần), cùng kênh thực hiện (cổng học vụ). Từ vựng khác nhau ("môn học" vs "học phần") nhưng một embedder ngữ nghĩa sẽ ánh xạ chúng về gần nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Học phần tiên quyết phải được hoàn thành trước."
- Câu B: "Hôm nay trời mưa rất to ở khu ký túc xá."
- Tại sao khác: khác miền chủ đề hoàn toàn (quy chế học vụ vs thời tiết), không chia sẻ thực thể hay hành động nào; vector gần như trực giao → cosine ≈ 0.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Vì độ dài (norm) của vector nhúng phần lớn phản ánh **độ dài văn bản / tần suất từ**, không phản ánh nội dung. Euclid phạt sự chênh lệch độ lớn, nên một đoạn dài và một câu ngắn cùng chủ đề sẽ bị coi là "xa nhau"; cosine chuẩn hóa độ lớn đi và chỉ so hướng, nên so sánh được truy vấn ngắn với chunk dài — đúng bài toán RAG. Ngoài ra cosine luôn nằm trong [-1, 1] nên dễ đặt ngưỡng, còn Euclid không có biên trên.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* bước nhảy (step) = `chunk_size - overlap` = 500 − 50 = 450.
> `số chunk = ceil((10000 − 50) / 450) = ceil(9950 / 450) = ceil(22.11) = 23`
> *Đáp án:* **23 chunks** — đã kiểm chứng bằng code: `FixedSizeChunker(chunk_size=500, overlap=50).chunk("x"*10000)` trả về đúng **23**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `ceil((10000 − 100) / 400) = ceil(24.75) = 25` chunk — tăng từ 23 lên **25** (kiểm chứng bằng code: đúng 25). Overlap lớn hơn ⇒ bước nhảy nhỏ hơn ⇒ nhiều chunk hơn, tốn thêm chi phí nhúng và lưu trữ. Đổi lại, một câu/quy định nằm vắt qua ranh giới chunk sẽ **xuất hiện trọn vẹn ở ít nhất một chunk**, nên không bị mất ngữ cảnh — rất quan trọng với văn bản quy định, nơi điều kiện và ngoại lệ thường nằm ở hai câu liền kề.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])[ \t]*(?:\n+|\s)` — *lookbehind* để cắt **sau** dấu kết câu mà vẫn giữ lại dấu câu trong câu (nếu dùng `split(". ")` thì dấu chấm bị nuốt mất). Sau khi tách, tôi `strip()` từng câu, loại phần tử rỗng, rồi gom theo lô `max_sentences_per_chunk` bằng vòng lặp `range(0, n, size)`. Edge case xử lý: chuỗi rỗng / chỉ có khoảng trắng → trả `[]`; nhiều khoảng trắng liên tiếp hoặc xuống dòng sau dấu chấm → vẫn nhận là một ranh giới câu; `max_sentences_per_chunk` được ép `max(1, ...)` để không bao giờ chia cho 0 hoặc lặp vô hạn.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `_split` thử dấu phân cách theo thứ tự ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Có **hai base case**: (1) `len(text) <= chunk_size` → trả `[text]`, đây là điểm dừng mong muốn; (2) hết separator hoặc gặp separator rỗng `""` → cắt cứng theo ký tự (`_hard_split`). Nếu separator hiện tại không có trong text thì bỏ qua, gọi đệ quy với danh sách separator còn lại. Điểm tôi thấy quan trọng nhất là **gộp tham lam (greedy merge)**: sau khi `split(separator)` tôi nối các mảnh lại cho tới sát `chunk_size` thay vì trả về từng mảnh rời — nếu không, tách theo `" "` sẽ sinh ra hàng trăm chunk một-từ. Mảnh nào tự nó đã dài hơn `chunk_size` thì đệ quy xuống separator mịn hơn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hóa thành một bản ghi `{id, content, metadata, embedding, _index}` trong `_make_record`; embedding được tính **ngay lúc nạp** (một lần) nên khi search chỉ phải nhúng câu truy vấn. `metadata.setdefault("doc_id", doc.id)` đảm bảo luôn có `doc_id` kể cả khi người dùng truyền `metadata={}` — đây là điều kiện để `delete_document()` và lọc theo tài liệu hoạt động. `search` nhúng truy vấn rồi tính **tích vô hướng** với từng embedding đã lưu (`_dot`), sắp xếp giảm dần và cắt `top_k`; vì các embedder trong lab đều trả vector đã chuẩn hóa nên tích vô hướng ≡ cosine. Tôi cũng khởi tạo ChromaDB nếu có, nhưng **luôn giữ bản sao trong bộ nhớ** làm nguồn sự thật để kết quả xác định như nhau trên mọi máy; mọi lỗi phía Chroma đều bị bắt và tự động lùi về in-memory.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> **Lọc trước, tìm sau (pre-filter)**: tôi lọc danh sách bản ghi theo `metadata_filter` (so khớp `==` trên tất cả cặp khóa-giá trị, ép `str()` để `"2026.1"` và `2026.1` không bị lệch kiểu) rồi mới cho vào cùng một hàm xếp hạng `_search_records`. Hậu-lọc (post-filter) sẽ sai vì các chunk lạc đối tượng có thể chiếm hết top-k trước khi bị loại. `metadata_filter` rỗng/`None` được coi là không lọc, nên `search_with_filter` trả về đúng bằng `search`. `delete_document` xây lại danh sách bỏ mọi bản ghi có `metadata["doc_id"]` khớp, so sánh độ dài trước/sau để trả `True/False`, và xóa tương ứng bên Chroma bằng `where={"doc_id": ...}`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Ba bước rõ ràng: (1) `store.search(question, top_k)`; (2) `build_context()` ghép các chunk thành khối có **đánh số `[1] [2] [3]` kèm nguồn và score**; (3) đổ vào `PROMPT_TEMPLATE` có chỉ dẫn *chỉ trả lời dựa trên ngữ cảnh, nếu không đủ thông tin thì nói không tìm thấy, và phải trích số hiệu nguồn*. Việc đánh số + in kèm `source_url` chính là thứ giúp chấm **grounding quality**: đọc câu trả lời là truy ngược được chunk nào sinh ra nó. Tôi lưu `self.last_results` để có thể kiểm tra lại ngữ cảnh sau khi gọi, và có hằng `NO_CONTEXT` cho trường hợp store rỗng để agent không bao giờ ném lỗi.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ python3 -m pytest tests/ -v
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: .../D305_B4_Lab07
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists          PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist   PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists    PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::...                       (7 tests) PASSED
tests/test_solution.py::TestSentenceChunker::...                        (4 tests) PASSED
tests/test_solution.py::TestRecursiveChunker::...                       (4 tests) PASSED
tests/test_solution.py::TestEmbeddingStore::...                         (8 tests) PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::...                     (2 tests) PASSED
tests/test_solution.py::TestComputeSimilarity::...                      (4 tests) PASSED
tests/test_solution.py::TestCompareChunkingStrategies::...              (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::...         (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::...           (3 tests) PASSED

============================== 42 passed in 0.29s ==============================
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

Ngoài pytest, tôi kiểm tra thêm hai đường chạy thật:
- `python3 ingest.py` → `ingest self-check OK: parse được 4 khóa metadata, tạo 18 chunk`
- `python3 main.py "Sinh viên đăng ký học phần ở đâu?"` → chạy trọn pipeline nạp → search → agent, không lỗi.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chạy `compute_similarity()` với backend **mock** (`scripts/run_benchmark.py`, mục D).

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần trong cổng học vụ. | Việc đăng ký môn học được thực hiện trên cổng thông tin học vụ. | cao | **−0.1328** | SAI |
| 2 | Thư viện cho mượn tài liệu và cung cấp không gian học tập. | Người dùng cần mang thẻ định danh hợp lệ khi mượn tài liệu. | cao | **0.0153** | SAI |
| 3 | Sinh viên đăng ký học phần trong cổng học vụ. | Thư viện cho mượn tài liệu và cung cấp không gian học tập. | thấp | **0.0683** | Đúng |
| 4 | Học phần tiên quyết phải được hoàn thành trước. | Hôm nay trời mưa rất to ở khu ký túc xá. | thấp | **0.0467** | Đúng |
| 5 | Sinh viên đăng ký học phần trong cổng học vụ. | (câu giống hệt câu A) | cao = 1.0 | **1.0000** | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 1: hai câu **gần như đồng nghĩa** lại cho điểm **âm** (−0.13), trong khi cặp 3 (hai câu khác chủ đề hẳn) lại **cao hơn** (0.07). Nguyên nhân không phải lỗi công thức mà là bản chất của backend: `MockEmbedder` băm **toàn bộ chuỗi** bằng MD5 rồi sinh vector giả ngẫu nhiên, nên chỉ cần đổi một ký tự là vector đổi hoàn toàn — nó chỉ bảo toàn *tính đồng nhất chuỗi* (cặp 5 = 1.0 tuyệt đối), chứ không bảo toàn *ý nghĩa*. Bài học rút ra: cosine similarity chỉ tốt bằng đúng không gian nhúng đứng sau nó; toàn bộ "trí thông minh ngữ nghĩa" của RAG nằm ở embedder, không nằm ở phép đo. Với `EMBEDDING_PROVIDER=local` (paraphrase-multilingual-MiniLM), tôi kỳ vọng cặp 1 lên khoảng 0.8–0.9, cặp 2 khoảng 0.5–0.6, cặp 3–4 xuống gần 0.0–0.2, tức là khớp lại với dự đoán theo ngữ nghĩa.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chiến lược cá nhân của tôi: **`HeadingChunker(max_chars=600, min_chars=120)`** — chia theo tiêu đề/mục (yêu cầu riêng của K3). Corpus: `data/k3_university/` (2 tài liệu → **4 chunk**). Câu Q5 chạy kèm `metadata_filter={"audience": "student"}`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên đăng ký học phần ở đâu và theo lịch nào? | Chunk ghi chú front matter ("Khối metadata phía trên là template mẫu…") | 0.043 | **Không** (chunk đúng không có trong top-3) | Agent trả lời từ 3 đoạn nhiễu → không có căn cứ |
| 2 | Khi gặp lỗi trùng lịch thì sinh viên phải xử lý thế nào? | "Đăng ký học phần — … Khi gặp lỗi trùng lịch, sinh viên điều chỉnh lớp học phần trước thời hạn…" | 0.134 | **Có** (top-1) | Trả lời có căn cứ: điều chỉnh trước thời hạn công bố |
| 3 | Yêu cầu ngoại lệ về học vụ được gửi qua kênh nào? | Cùng chunk "Đăng ký học phần" (chứa câu "gửi qua kênh hỗ trợ học vụ chính thức") | 0.086 | **Có** (top-1) | Trả lời có căn cứ: kênh hỗ trợ học vụ chính thức |
| 4 | Cần mang theo giấy tờ gì khi mượn tài liệu ở thư viện? | Chunk ghi chú front matter của tài liệu đăng ký học phần | 0.413 | Không ở top-1, **có ở hạng 3** ("thẻ định danh hợp lệ") | Ngữ cảnh có chứa đáp án nhưng bị đẩy xuống cuối |
| 5 | Quy định về học phần tiên quyết áp dụng cho sinh viên? *(có lọc `audience=student`)* | "Đăng ký học phần — … học phần có thể yêu cầu học phần tiên quyết…" | −0.020 | **Có** (top-1) | Trả lời có căn cứ: phải kiểm tra điều kiện trước khi xác nhận |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **4 / 5**
**Điểm truy xuất theo `docs/SCORING.md` (2/1/0 mỗi câu):** 0 + 2 + 2 + 1 + 2 = **7 / 10**

Đối chiếu với các cấu hình khác trên **cùng corpus, cùng 5 câu hỏi, cùng backend mock**:

| Chiến lược | Số chunk | Điểm /10 | Số câu có chunk liên quan trong top-3 |
|---|---|---|---|
| `heading(max=600)` — **của tôi** | 4 | **7** | 4/5 |
| `fixed_size(300/50)` | 5 | 6 | 4/5 |
| `by_sentences(2)` | 5 | 4 | 4/5 |
| `recursive(300)` | 5 | 4 | 2/5 |

> **Diễn giải trung thực:** với mock embedding, thứ hạng giữa các chiến lược **không phải là bằng chứng về chất lượng ngữ nghĩa** — chênh lệch 7 vs 4 ở đây phần lớn là nhiễu của hàm băm. Điều *có* ý nghĩa và lặp lại được là hai quan sát mang tính cấu trúc: (a) chiến lược tạo **ít chunk to, mỗi chunk trọn một mục** thì mỗi lần trúng sẽ trúng đúng chỗ có đáp án (heading: 3/5 câu có chunk vàng ngay top-1); (b) chunk càng vụn thì đáp án càng dễ bị tách khỏi từ khóa của câu hỏi. Để kết luận chắc chắn cần chạy lại với `EMBEDDING_PROVIDER=local` và corpus 5–10 tài liệu.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Bài học lớn nhất khi so 4 cấu hình trên cùng bộ dữ liệu: **rác trong corpus gây hại nhiều hơn tham số chunking**. Cả 4 chiến lược đều có câu bị chính đoạn ghi chú front matter ("Khối metadata phía trên là template mẫu…") chiếm top-1 — nhiều nhất là `by_sentences` với 4/5 câu — nó không phải nội dung quy định nhưng lại dày đặc từ khóa. Chunk có sạch thì mọi chiến lược đều tốt lên; chunk bẩn thì không tham số nào cứu được. Bài học thứ hai là `search_with_filter` đưa Q5 từ 1/2 lên 2/2 chỉ bằng một trường metadata — lọc trước rẻ hơn nhiều so với đi tinh chỉnh chunk_size.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **56 / 60** |

> Tự trừ điểm ở mục Kết quả truy xuất vì corpus mới có 2/5–10 tài liệu và benchmark chạy trên mock; đây là hai việc cần làm trước khi nộp bản chính thức (xem `docs/IMPLEMENTATION_NOTES.md`, mục "Việc còn lại").
