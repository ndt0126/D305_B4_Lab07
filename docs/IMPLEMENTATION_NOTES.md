# Nhật Ký Hoàn Thành Lab 07 (K3) — Làm gì, làm thế nào, và tại sao

Tài liệu này ghi lại **toàn bộ** những gì đã được thực hiện để hoàn thành Lab 07, theo thứ tự thời gian, kèm lý do cho từng quyết định thiết kế. Mục đích: người đọc (bạn, bạn cùng nhóm, hoặc giảng viên) có thể tái lập từng bước và hiểu vì sao code được viết như vậy, chứ không chỉ thấy nó chạy qua test.

- **Ngày thực hiện:** 2026-08-03
- **Môi trường chạy:** Python 3.10.12 (chuẩn lab là 3.11 — mã nguồn không dùng cú pháp riêng của 3.11 nên chạy được ở cả hai; xem mục 8.1)
- **Backend nhúng dùng để đo:** `mock` (theo lựa chọn khi bắt đầu)
- **Corpus dùng để đo:** 2 tài liệu khởi động trong `data/k3_university/` (giữ nguyên, không thu thập thêm)
- **Kết quả:** `pytest tests/ -v` → **42 passed**

---

## 0. Bản đồ thay đổi

| File | Trạng thái | Nội dung |
|---|---|---|
| `src/chunking.py` | **Sửa** | Hoàn thành `SentenceChunker`, `RecursiveChunker` (+ `_split`), `compute_similarity`, `ChunkingStrategyComparator`; **thêm mới** `HeadingChunker` |
| `src/store.py` | **Sửa** | Hoàn thành toàn bộ `EmbeddingStore` (8 phương thức/TODO) |
| `src/agent.py` | **Sửa** | Hoàn thành `KnowledgeBaseAgent.__init__` + `answer`; thêm `build_context()` |
| `src/__init__.py` | **Sửa** | Export thêm `HeadingChunker` |
| `scripts/run_benchmark.py` | **Thêm mới** | Kịch bản đo Giai đoạn 2 (không được chấm điểm, chỉ sinh số liệu) |
| `report/benchmark_raw.md` | **Thêm mới (tự sinh)** | Kết quả đo thô, do script ở trên ghi ra |
| `report/REPORT_CANHAN.md` | **Điền** | Báo cáo cá nhân, số liệu lấy từ `benchmark_raw.md` |
| `report/REPORT_NHOM.md` | **Điền** | Báo cáo nhóm, số liệu lấy từ `benchmark_raw.md` |
| `docs/IMPLEMENTATION_NOTES.md` | **Thêm mới** | Chính là file này |
| `data/**`, `tests/**`, `ingest.py`, `main.py`, `README.md` | **Không đổi** | Giữ nguyên theo yêu cầu |

---

## 1. Quy trình đã áp dụng

1. **Đọc trước, code sau.** Đọc `README.md`, `exercises.md`, `K3_VARIANT.md`, `docs/SCORING.md`, `docs/DATA_COLLECTION.md`, `docs/EVALUATION.md` và **đọc kỹ `tests/test_solution.py`** trước khi viết dòng code đầu tiên. Bộ test là đặc tả chính xác nhất của bài — ví dụ nó tiết lộ rằng `compare()` trả về dict mà **mọi khóa cấp 1 đều phải là một chiến lược** (vì test lặp `for name, stats in result.items()` rồi đòi `stats['count']`), nên không được nhét thêm khóa metadata ở cấp 1.
2. **Đọc code mẫu đã cho.** `Document` và `FixedSizeChunker` là mẫu về phong cách: type hint đầy đủ, docstring nêu rõ quy tắc, xử lý edge case ngay đầu hàm. Toàn bộ code viết thêm bám theo phong cách này.
3. **Code theo thứ tự phụ thuộc:** `chunking.py` (không phụ thuộc ai) → `store.py` (dùng `_dot` từ chunking) → `agent.py` (dùng store).
4. **Chạy test sau mỗi module**, không viết một mạch rồi mới chạy.
5. **Đo đạc bằng script, không bằng tay.** Mọi con số trong hai báo cáo đều do `scripts/run_benchmark.py` sinh ra, để có thể tái lập và không có chỗ cho số liệu bịa.
6. **Viết báo cáo cuối cùng**, dán số liệu thật vào.

---

## 2. `src/chunking.py`

### 2.1 `SentenceChunker.chunk`

**Yêu cầu:** tách câu theo `". "`, `"! "`, `"? "`, `".\n"`, gom tối đa `max_sentences_per_chunk` câu/chunk, strip khoảng trắng thừa.

**Cách làm:**

```python
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])[ \t]*(?:\n+|\s)")
```

- **Vì sao dùng lookbehind `(?<=[.!?])` chứ không `text.split(". ")`?** `split` sẽ **nuốt mất dấu chấm**, khiến chunk trả về là "Sinh viên đăng ký học phần" (mất dấu câu) — vừa xấu khi hiển thị, vừa làm lệch embedding so với văn bản gốc. Lookbehind cắt *sau* dấu câu nên dấu câu được giữ lại ở cuối câu.
- **`[ \t]*(?:\n+|\s)`** gộp cả bốn trường hợp trong đề bài vào một biểu thức: dấu chấm + khoảng trắng, dấu chấm + xuống dòng, và cả trường hợp có khoảng trắng thừa trước khi xuống dòng.
- Tách xong thì `strip()` từng câu và **loại phần tử rỗng** — đây là chỗ dễ sinh chunk `""` nếu văn bản kết thúc bằng dấu chấm.
- Gom nhóm bằng `range(0, len(sentences), size)` — đơn giản, không cần biến đếm thủ công.
- `max(1, max_sentences_per_chunk)` trong `__init__` (đã có sẵn) chặn giá trị 0/âm gây lặp vô hạn.

**Hàm phụ `split_sentences()`** được tách riêng (public) để script benchmark và người học có thể kiểm tra riêng bước tách câu.

### 2.2 `RecursiveChunker.chunk` / `_split`

**Yêu cầu:** đệ quy theo thứ tự ưu tiên `["\n\n", "\n", ". ", " ", ""]`.

**Thuật toán trong `_split(current_text, remaining_separators)`:**

| Bước | Điều kiện | Hành động |
|---|---|---|
| Base case 1 | `len(text) <= chunk_size` | Trả `[text]` — **đây là điểm dừng mong muốn** |
| Base case 2 | Hết separator, hoặc separator hiện tại là `""` | `_hard_split()` — cắt cứng theo ký tự |
| Bỏ qua | Separator không xuất hiện trong text | Gọi đệ quy với `remaining_separators[1:]` |
| Trường hợp chính | Separator có trong text | `split()` rồi **gộp tham lam** |

**Chi tiết quan trọng nhất — gộp tham lam (greedy merge):** sau khi `text.split(separator)`, code **không** trả về từng mảnh mà nối chúng lại (kèm separator) cho tới sát `chunk_size`:

```python
candidate = piece if not buffer else buffer + separator + piece
if len(candidate) <= self.chunk_size:
    buffer = candidate            # còn chỗ -> gộp tiếp
else:
    chunks.append(buffer)         # đầy -> chốt chunk
    ...
```

Không có bước này, khi rơi xuống separator `" "` thì mỗi từ sẽ thành một chunk — với `LONG_TEXT = "word " * 200` sẽ ra **200 chunk 4 ký tự** thay vì 10 chunk ~99 ký tự. Test `test_chunks_within_size_when_possible` (đòi >80% chunk có độ dài ≤110 khi `chunk_size=100`) chính là bài kiểm tra cho hành vi này.

Mảnh nào **tự nó** đã dài hơn `chunk_size` thì được đệ quy xuống separator mịn hơn (`self._split(piece, rest)`) — đây là chỗ "recursive" thực sự xảy ra.

**Xử lý `separators=[]`:** test `test_empty_separators_falls_back_gracefully` truyền danh sách rỗng. Base case 2 lo việc này: hết separator → cắt cứng. Với text ngắn hơn `chunk_size` thì base case 1 bắt trước và trả nguyên văn bản.

### 2.3 `compute_similarity`

```python
dot / (||a|| * ||b||)
```

Ba lớp bảo vệ, theo đúng thứ tự:
1. `if not vec_a or not vec_b: return 0.0` — vector rỗng (không phải vector-không).
2. Tính norm bằng `sqrt(_dot(v, v))` — tái sử dụng `_dot` đã có sẵn thay vì viết lại vòng lặp.
3. `if norm_a == 0.0 or norm_b == 0.0: return 0.0` — **bảo vệ chia cho 0** theo đúng yêu cầu docstring; test `test_zero_vector_returns_0` kiểm tra chính điểm này.

Không dùng `numpy` vì `requirements.txt` chỉ có `pytest` + `python-dotenv`; bài này không cần tốc độ.

### 2.4 `ChunkingStrategyComparator.compare`

Trả về đúng ba khóa mà test đòi: `fixed_size`, `by_sentences`, `recursive`; mỗi khóa có `count`, `avg_length`, `chunks` (bắt buộc) và thêm `min_length`, `max_length` (hữu ích cho báo cáo — chính hai trường này giúp phát hiện `recursive` sinh chunk 11 ký tự và `by_sentences` sinh chunk 620 ký tự).

**Quyết định thiết kế:** `overlap = chunk_size // 10` (10%) cho `FixedSizeChunker` để so sánh công bằng — nếu để `overlap=0`, fixed-size sẽ bị thiệt một cách nhân tạo. `SentenceChunker` dùng mặc định 3 câu/chunk vì nó **không nhận tham số ký tự** (một phát hiện được ghi lại trong báo cáo nhóm: `by_sentences` không tôn trọng `chunk_size`).

Phòng hờ chia cho 0: `avg_length` trả `0.0` khi danh sách chunk rỗng.

### 2.5 `HeadingChunker` — chiến lược tùy chỉnh (thêm mới)

**Tại sao phải có:** `K3_VARIANT.md` yêu cầu *"ít nhất một thành viên thử chia nhỏ theo tiêu đề/mục của sổ tay hoặc quy định học vụ"*, và `exercises.md` (Bài tập 3.1) yêu cầu mỗi người có một chiến lược riêng.

**Lý do thiết kế:** văn bản quy định đại học được viết theo mục có tiêu đề, và **mỗi mục là một đơn vị trả lời trọn vẹn** (điều kiện + ngoại lệ + thời hạn nằm cùng nhau). Cắt theo ranh giới tiêu đề giữ nguyên đơn vị đó.

Bốn cơ chế, mỗi cơ chế xử lý một điểm yếu đã quan sát được từ baseline:

| Cơ chế | Sửa điểm yếu nào |
|---|---|
| Tách tại `^#{1,6}\s+` (H1..H6), giữ cả phần mở đầu trước tiêu đề đầu tiên | `fixed_size` cắt mù ngữ nghĩa |
| **Ghim tiêu đề vào đầu mỗi chunk con** | Chunk con của một mục dài mất ngữ cảnh "đang nói về mục nào" |
| Mục dài hơn `max_chars` → giao cho `RecursiveChunker` | Không viết lại logic cắt (tái sử dụng) |
| Mục ngắn hơn `min_chars` → gộp với mục kế tiếp | `recursive` sinh chunk vụn 11 ký tự |

Được export trong `src/__init__.py` để `scripts/run_benchmark.py` và báo cáo dùng được. **Không** đụng vào bộ test có sẵn — đây là phần thêm, không thay thế.

> Đánh đổi đã ghi nhận (và đã đưa vào phần Phân tích lỗi của báo cáo nhóm): cơ chế gộp mục ngắn khiến đoạn ghi chú front matter bị gộp chung với nội dung tốt, làm `heading` trượt câu Q1. Đây là hệ quả thiết kế, không phải bug.

---

## 3. `src/store.py` — `EmbeddingStore`

### 3.1 Quyết định kiến trúc lớn nhất: ChromaDB + bản sao trong bộ nhớ

TODO gốc gợi ý "khởi tạo chromadb client + collection" nếu import được. Lựa chọn đã thực hiện: **khởi tạo Chroma nếu có, nhưng luôn giữ danh sách bản ghi trong `self._store` làm nguồn sự thật duy nhất cho search/filter/delete.**

Lý do:
- **Tính xác định.** Cả lab xoay quanh việc *so sánh chiến lược giữa các thành viên*. Nếu máy A có Chroma còn máy B không, hai người sẽ nhận kết quả xếp hạng khác nhau trên cùng dữ liệu và mọi so sánh trở nên vô nghĩa.
- **An toàn.** `chromadb.EphemeralClient()` (in-process, không ghi đĩa) tránh dính state giữa các lần chạy test — bộ test tạo nhiều store trùng tên collection (`"test_filter"`, `"test_delete"`).
- **Không bao giờ vỡ.** Mọi lệnh gọi Chroma nằm trong `try/except`; lỗi làm `_use_chroma = False` và store chạy tiếp bằng bộ nhớ trong.

### 3.2 `_make_record` — nơi đặt một quyết định âm thầm nhưng quan trọng

```python
metadata.setdefault("doc_id", doc.id)
```

Test `TestEmbeddingStoreDeleteDocument` tạo `Document("doc_to_delete", "...", {})` — **metadata rỗng, không có `doc_id`** — rồi gọi `delete_document("doc_to_delete")` và đòi `True`. Nếu chỉ tìm theo `metadata["doc_id"]` mà không có dòng `setdefault` này, phép xóa sẽ luôn trả `False`.

Dùng `setdefault` (chứ không phải gán đè) để **không phá pipeline của `ingest.py`**: ở đó chunk có `id = "parent::chunk_3"` nhưng `metadata["doc_id"] = "parent"`. Gán đè sẽ làm `delete_document("parent")` không xóa được gì.

Ngoài ra bản ghi mang thêm `_index` (thứ tự nạp) để phá thế hòa điểm một cách ổn định, và `dict(doc.metadata or {})` **sao chép** metadata để store không bị sửa ngầm từ bên ngoài.

### 3.3 `_search_records` — một hàm xếp hạng dùng chung

Cả `search()` và `search_with_filter()` đều gọi hàm này; chỉ khác nhau ở **tập ứng viên đưa vào**. Nhờ vậy hai đường không thể lệch nhau về cách tính điểm — chính là điều test `test_no_filter_returns_all_candidates` kiểm tra.

Điểm số = **tích vô hướng** (`_dot`) đúng theo docstring của đề. Với mọi embedder trong lab (mock chuẩn hóa thủ công, `LocalEmbedder` dùng `normalize_embeddings=True`, OpenAI trả vector đã chuẩn hóa), tích vô hướng **đồng nhất với cosine** — nên không mất mát gì so với `compute_similarity`.

`sort(key=..., reverse=True)` của Python là **sort ổn định**, nên khi điểm bằng nhau thứ tự nạp được giữ nguyên → kết quả tái lập được giữa các lần chạy (test `test_search_results_sorted_by_score_descending`).

### 3.4 `search_with_filter` — lọc TRƯỚC, không lọc SAU

```python
candidates = [r for r in self._store
              if all(str(r["metadata"].get(k)) == str(v) for k, v in metadata_filter.items())]
return self._search_records(query, candidates, top_k)
```

- **Vì sao pre-filter?** Nếu hậu-lọc (`search()` rồi bỏ kết quả sai), các chunk sai đối tượng đã chiếm hết top-k trước khi bị loại, và ta thường nhận về danh sách rỗng. Số liệu Q5 trong báo cáo nhóm chứng minh điều này: không lọc → chunk vàng ở hạng 3; có lọc → hạng 1.
- **Vì sao ép `str()` cả hai vế?** Front matter YAML có thể cho ra `2026.1` (float) hoặc `"2026.1"` (chuỗi) tùy có `pyyaml` hay không. So sánh trực tiếp sẽ trượt một cách khó hiểu; ép chuỗi làm bộ lọc bền với kiểu dữ liệu.
- **`metadata_filter` rỗng/`None` = không lọc**, đúng ngữ nghĩa "optional filter" và đúng test.

### 3.5 `delete_document`

Xây lại danh sách bằng list comprehension rồi so độ dài trước/sau để quyết định `True`/`False`. Cách này ngắn hơn và an toàn hơn việc xóa phần tử trong lúc đang duyệt danh sách (lỗi kinh điển). Bên Chroma xóa bằng `where={"doc_id": doc_id}`.

---

## 4. `src/agent.py` — `KnowledgeBaseAgent`

`answer()` đúng ba bước của mẫu RAG, nhưng có hai bổ sung phục vụ tiêu chí chấm **grounding quality** trong `docs/EVALUATION.md`:

1. **Ngữ cảnh có đánh số + nguồn + score.** Mỗi chunk vào prompt dưới dạng
   `[1] (nguồn: https://... | score=0.213)` + nội dung. Nhờ vậy đọc câu trả lời là **truy ngược được** chunk nào sinh ra nó — đúng tiêu chí "Source Traceability".
2. **Prompt có ràng buộc chống bịa.** Template chỉ thị rõ: chỉ trả lời dựa trên ngữ cảnh; nếu không đủ thông tin thì nói không tìm thấy; phải trích số hiệu nguồn. Đây là phần *thiết kế prompt* được chấm, không phải phần trang trí.

Thêm `self.last_results` để kiểm tra lại ngữ cảnh sau khi gọi (script benchmark dùng), và hằng `NO_CONTEXT` cho trường hợp store rỗng để agent không bao giờ ném lỗi. Trả về được ép `str()` phòng khi `llm_fn` trả kiểu khác.

Chọn `source_url` → `source` → `doc_id` theo thứ tự ưu tiên khi hiển thị nguồn, vì `ingest.py` gắn `source` (đường dẫn file) còn front matter K3 gắn `source_url` (URL thật) — ưu tiên cái có ý nghĩa với người đọc.

---

## 5. `scripts/run_benchmark.py` — cách các con số trong báo cáo được tạo ra

**Nguyên tắc:** không có số liệu nào trong báo cáo được gõ tay. Script chạy 5 phần:

| Phần | Nội dung | Dùng cho |
|---|---|---|
| A | `ChunkingStrategyComparator().compare()` trên 3 văn bản | REPORT_NHOM §2 (Baseline) |
| B | 5 câu hỏi × 4 chiến lược, ghi top-3 + chấm 2/1/0 | REPORT_NHOM §3, REPORT_CANHAN §5 |
| C | `search()` vs `search_with_filter()` trên cùng Q5 | REPORT_NHOM §3 (metadata utility) |
| D | 5 cặp câu, dự đoán vs `compute_similarity()` thực tế | REPORT_CANHAN §4 |
| E | `get_collection_size()` / `delete_document()` | Kiểm chứng vòng đời store |

**Điểm phương pháp quan trọng — nhãn "liên quan" được gán tự động:**

```python
def is_relevant(result, case) -> bool:
    return (result["metadata"].get("doc_id") == case["gold_doc"]
            and normalize(case["gold_phrase"]) in normalize(result["content"]))
```

Một chunk chỉ được tính là liên quan khi **đúng tài liệu vàng** VÀ **chứa cụm từ khóa vàng** (so khớp sau khi chuẩn hóa Unicode NFC + lowercase — bắt buộc với tiếng Việt có dấu). Không có đánh giá cảm tính, nên bất kỳ ai chạy lại script cũng nhận đúng những con số trong báo cáo.

Chấm điểm theo đúng `docs/SCORING.md`: liên quan ở top-1 = 2đ, liên quan trong top-3 = 1đ, không có = 0đ.

Script tự đọc `EMBEDDING_PROVIDER`, và **tự in cảnh báo phương pháp** lên đầu file kết quả khi backend là mock.

Chạy lại bất cứ lúc nào:

```bash
python3 scripts/run_benchmark.py                      # mock
EMBEDDING_PROVIDER=local python3 scripts/run_benchmark.py   # embedder ngữ nghĩa
```

---

## 6. Hai báo cáo

- `report/REPORT_CANHAN.md` — điền đủ 5 phần: giải thích cosine + toán chunking (đã kiểm chứng bằng code: 23 và 25 chunk), hướng tiếp cận từng hàm, kết quả pytest, bảng dự đoán độ tương tự, và kết quả truy xuất cá nhân với chiến lược `HeadingChunker`.
- `report/REPORT_NHOM.md` — điền đủ 4 phần: kiểm kê tài liệu + schema metadata, phân tích baseline + 4 chiến lược + so sánh, 5 câu hỏi đánh giá kèm gold answer, và **2 trường hợp phân tích lỗi** (Bài tập 3.5).

**Nguyên tắc viết:** mọi kết luận về *thứ hạng* chiến lược đều đi kèm mức độ tin cậy, vì đo bằng mock. Chỗ nào chưa đạt yêu cầu của đề (corpus 2/5–10 tài liệu, `source_url` còn là `example.edu`) thì **ghi thẳng ra và tự trừ điểm**, thay vì làm đẹp số liệu. Bảng tự đánh giá: cá nhân **56/60**, nhóm **30/40**.

Chỗ cần điền tay trước khi nộp được đánh dấu bằng `[Điền ...]`: tên nhóm, tên các thành viên còn lại.

---

## 7. Kiểm chứng đã thực hiện

| Kiểm chứng | Lệnh | Kết quả |
|---|---|---|
| Bộ test chính thức | `python3 -m pytest tests/ -v` | **42 passed** |
| Toán chunking trong báo cáo | `FixedSizeChunker(500, 50).chunk("x"*10000)` | 23 chunk (khớp công thức); overlap=100 → 25 (khớp) |
| Pipeline nạp dữ liệu | `python3 ingest.py` | `self-check OK: parse 4 khóa metadata, tạo 18 chunk` |
| Chạy đầu-cuối | `python3 main.py "Sinh viên đăng ký học phần ở đâu?"` | Nạp → search → agent, không lỗi |
| Số liệu báo cáo | `python3 scripts/run_benchmark.py` | Sinh `report/benchmark_raw.md`; mọi bảng trong 2 báo cáo đối chiếu khớp file này |

---

## 8. Những điểm cần biết & việc còn lại

### 8.1 Phiên bản Python

Chuẩn của lab là **3.11**; môi trường thực thi ở đây là 3.10.12. Mã nguồn không dùng cú pháp riêng của 3.11 và mọi module dùng `from __future__ import annotations` khi cần cú pháp `X | None`, nên chạy đúng ở cả hai. Khi nộp, vẫn nên tạo venv bằng `py -3.11` / `python3.11` theo README.

### 8.2 Việc còn lại trước khi nộp bản chính thức

1. **Bổ sung corpus lên 5–10 tài liệu thật** (học phí, học bổng, ký túc xá) từ nguồn công khai, thay `source_url` `example.edu` bằng URL thật, cập nhật `data/k3_university/sources.csv` (cột `license_or_permission` hiện là `example-template-replace-me`). Đây là hạng mục bị trừ điểm nhiều nhất (4/10).
2. **Dọn đoạn ghi chú template** trong hai file `.md` khởi động — chính đoạn `> Khối metadata phía trên là **template mẫu**…` là nguồn nhiễu số một trong toàn bộ kết quả đo (xem Phân tích lỗi ở REPORT_NHOM §4).
3. **Chạy lại benchmark với embedder ngữ nghĩa:**
   ```bash
   pip install -r requirements-local.txt
   EMBEDDING_PROVIDER=local python3 scripts/run_benchmark.py
   ```
   rồi cập nhật lại các bảng số trong hai báo cáo. Kết luận "chiến lược nào tốt hơn" chỉ có giá trị sau bước này.
4. **Điền tên nhóm và tên các thành viên** vào các chỗ `[Điền ...]`, gán mỗi cấu hình chiến lược cho một người phụ trách.

### 8.3 Những gì cố ý KHÔNG làm

- **Không sửa `tests/test_solution.py`** — bài kiểm thử là đặc tả, sửa nó là tự vô hiệu hóa phần chấm 30 điểm.
- **Không sửa `ingest.py`, `main.py`, `README.md`** — là phần "glue" đã được cung cấp sẵn, không thuộc phạm vi bài làm.
- **Không thêm thư viện ngoài `requirements.txt`** cho phần bắt buộc; `numpy`/`chromadb` chỉ được dùng khi *tình cờ* có sẵn, không bao giờ là điều kiện bắt buộc.
- **Không thu thập thêm tài liệu** — theo lựa chọn giữ nguyên corpus khi bắt đầu; hệ quả đã được ghi rõ ở mục 8.2 và trong phần tự đánh giá của báo cáo nhóm.
