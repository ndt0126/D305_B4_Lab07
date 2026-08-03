# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Điền tên nhóm]
**Thành viên:** Vinh — [điền các thành viên còn lại]
**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

> **Điều kiện chạy & giới hạn của bản báo cáo này (đọc trước):**
> 1. Corpus hiện tại là **2 tài liệu khởi động** kèm theo repo (`data/k3_university/`), chưa đạt yêu cầu 5–10 tài liệu; `source_url` vẫn là `example.edu` (dữ liệu mẫu, chưa phải nguồn công khai thật).
> 2. Backend nhúng = **mock** (MD5 → vector), **không mang ngữ nghĩa**.
> 3. Cả 4 chiến lược dưới đây đều do **một người** chạy trên cùng corpus/cùng bộ câu hỏi; khi nộp theo nhóm, hãy gán mỗi cấu hình cho một thành viên phụ trách.
>
> Toàn bộ số liệu là kết quả đo thật, sinh tự động bởi `scripts/run_benchmark.py`, lưu nguyên văn ở `report/benchmark_raw.md`. Các kết luận về *thứ hạng* chiến lược vì vậy được ghi kèm mức độ tin cậy.

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy định **đăng ký học phần** (học vụ) + **dịch vụ thư viện** — hai mảng sinh viên tra cứu nhiều nhất và có ranh giới đối tượng (`audience`) khác nhau, thuận lợi để thử nghiệm lọc metadata.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký học phần (`course-registration.md`) | `https://example.edu/hoc-vu/dang-ky-hoc-phan` *(mẫu — cần thay bằng nguồn thật)* | 2026-08-02 / `2026.1` | 646 (phần nội dung) | `doc_id`, `title`, `audience=student`, `department=academic-affairs`, `language=vi`, `source_url`, `retrieved_at`, `document_version` |
| 2 | Dịch vụ thư viện (`library-services.md`) | `https://example.edu/thu-vien/dich-vu` *(mẫu — cần thay bằng nguồn thật)* | 2026-08-02 / `2026.1` | 481 (phần nội dung) | `doc_id`, `title`, `audience=all`, `department=library`, `language=vi`, `source_url`, `retrieved_at`, `document_version` |
| 3 | — *(còn thiếu: học phí)* | | | | |
| 4 | — *(còn thiếu: học bổng)* | | | | |
| 5 | — *(còn thiếu: ký túc xá)* | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. *(Hai file hiện tại là dữ liệu mẫu do lab cung cấp — an toàn, nhưng chưa phải nguồn thật.)*
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. *(Đủ trường; giá trị `source_url` còn là placeholder `example.edu`.)*
- [ ] **Chưa đạt:** đủ 5–10 tài liệu từ nguồn công khai thật, `sources.csv` khớp 1-1 với nguồn thật (`license_or_permission` hiện là `example-template-replace-me`).

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string (slug) | `k3-course-registration` | Khóa ổn định để `delete_document()` xóa trọn tài liệu và để truy vết chunk → tài liệu gốc |
| `audience` | enum | `student` / `faculty` / `staff` / `all` | **Bắt buộc theo K3.** Lọc trước bằng trường này loại thẳng tài liệu sai đối tượng khỏi top-k (xem Q5) |
| `department` | enum | `academic-affairs`, `library` | Thu hẹp theo phòng ban khi câu hỏi đã rõ đơn vị phụ trách; hữu ích khi corpus lớn dần |
| `source_url` | URL | `https://example.edu/hoc-vu/...` | In kèm trong prompt của agent → người đọc kiểm chứng được câu trả lời (grounding) |
| `retrieved_at` | date | `2026-08-02` | Đánh giá độ mới; phân biệt hai phiên bản của cùng một quy định |
| `document_version` | string | `2026.1` | Chọn đúng phiên bản đang hiệu lực khi quy định được cập nhật theo học kỳ |
| `language` | enum | `vi` | Lọc theo ngôn ngữ khi corpus có cả bản tiếng Anh |
| `chunk_index` | int *(do `ingest.py` tự gắn)* | `0`, `1`, `2` | Khôi phục thứ tự gốc, ghép lại các chunk liền kề khi cần ngữ cảnh rộng hơn |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

`ChunkingStrategyComparator().compare(text, chunk_size=300)` trên 3 văn bản (2 tài liệu corpus + 1 văn bản dài để thấy hành vi khi quy mô tăng):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `k3-course-registration` (646 ký tự) | FixedSizeChunker (`fixed_size`) | 3 | 235.3 (min 106 / max 300) | Kém — cắt giữa câu ("…trước khi xác nhận đăng ký" bị tách khỏi vế điều kiện) |
| `k3-course-registration` | SentenceChunker (`by_sentences`) | 2 | 321.5 (min 277 / max 366) | Tốt — mỗi chunk trọn 3 câu, đọc được |
| `k3-course-registration` | RecursiveChunker (`recursive`) | 3 | 214.0 (min 167 / max 294) | Khá — cắt theo đoạn trước, không cắt giữa từ |
| `k3-library-services` (481 ký tự) | FixedSizeChunker (`fixed_size`) | 2 | 255.5 (min 211 / max 300) | Kém — ranh giới rơi giữa câu |
| `k3-library-services` | SentenceChunker (`by_sentences`) | 2 | 239.0 (min 115 / max 363) | Tốt nhưng độ dài lệch nhau (115 vs 363) |
| `k3-library-services` | RecursiveChunker (`recursive`) | 2 | 239.5 (min 202 / max 277) | Tốt — hai đoạn tự nhiên |
| `chunking_experiment_report` (2282 ký tự) | FixedSizeChunker (`fixed_size`) | 9 | 280.2 (min 122 / max 300) | Đều đặn nhưng cắt ngang ý |
| `chunking_experiment_report` | SentenceChunker (`by_sentences`) | 5 | 454.6 (min 336 / max 620) | Mạch lạc nhất, **nhưng vượt xa chunk_size=300** |
| `chunking_experiment_report` | RecursiveChunker (`recursive`) | 15 | 150.2 (min 11 / max 294) | Bám cấu trúc, **nhưng sinh chunk vụn 11 ký tự** (dòng tiêu đề) |

**Ba quan sát rút ra từ baseline:**

1. `by_sentences` **không tôn trọng `chunk_size`** — nó tính theo *số câu*, nên với văn xuôi tiếng Việt câu dài, chunk phình lên 620 ký tự (gấp đôi ngân sách). Đây là rủi ro thật: chunk quá dài làm loãng vector nhúng.
2. `recursive` bám cấu trúc tốt nhưng khi văn bản có nhiều dòng tiêu đề Markdown ngắn, nó sinh ra **chunk 11 ký tự** — chunk vụn vừa vô nghĩa vừa chiếm chỗ trong top-k.
3. `fixed_size` là chiến lược duy nhất cho độ dài **dự đoán được**, đổi lại là chỗ cắt tệ nhất về mặt ngữ nghĩa.

→ Chính ba điểm yếu này là lý do nhóm thiết kế thêm một chiến lược tùy chỉnh theo **tiêu đề/mục** (bên dưới).

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Vinh** *(chiến lược tùy chỉnh — đáp ứng yêu cầu riêng của K3: "ít nhất một thành viên chia nhỏ theo tiêu đề/mục")*
- **Loại chiến lược:** custom — `HeadingChunker(max_chars=600, min_chars=120)`
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy định/dịch vụ đại học luôn được viết theo **mục có tiêu đề** ("Đăng ký học phần", "Gia hạn tài liệu", "Xử lý quá hạn"), và mỗi mục chính là một *đơn vị trả lời* trọn vẹn — đủ điều kiện, ngoại lệ và thời hạn. Cắt theo ranh giới tiêu đề vì thế giữ nguyên đơn vị này thay vì cắt ngang như fixed-size. Hai chi tiết thiết kế quan trọng: (a) **ghim tiêu đề vào đầu mỗi chunk con**, để chunk nào cũng tự mang ngữ cảnh "đang nói về mục nào" khi được nhúng — cực kỳ hữu ích khi một mục dài phải cắt tiếp; (b) **gộp mục ngắn hơn `min_chars` với mục kế tiếp**, để không lặp lại lỗi chunk-vụn-11-ký-tự của `recursive`. Mục dài hơn `max_chars` được giao lại cho `RecursiveChunker` xử lý (tái sử dụng, không viết lại logic cắt).
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    """Chia theo tiêu đề/mục của văn bản quy định (src/chunking.py)."""

    _HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)

    def __init__(self, max_chars: int = 600, min_chars: int = 120) -> None:
        self.max_chars = max_chars
        self.min_chars = min_chars

    def chunk(self, text: str) -> list[str]:
        splitter = RecursiveChunker(chunk_size=self.max_chars)
        chunks, pending = [], ""
        for title, body in self._sections(text):          # (1) tách theo H1..H6
            block = f"{title}\n{body}".strip() if title else body.strip()
            block = f"{pending}\n\n{block}".strip() if pending else block
            pending = ""
            if len(block) < self.min_chars:               # (2) mục quá ngắn -> chờ gộp
                pending = block
                continue
            if len(block) <= self.max_chars:
                chunks.append(block)
                continue
            prefix = f"{title}\n" if title else ""        # (3) ghim tiêu đề vào từng mảnh
            for piece in splitter.chunk(block):
                chunks.append(piece if title and piece.startswith(title) else f"{prefix}{piece}".strip())
        if pending:
            chunks[-1] = f"{chunks[-1]}\n\n{pending}".strip() if chunks else pending
        return chunks
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:** FixedSize — `FixedSizeChunker(chunk_size=300, overlap=50)`
- **Mô tả & lý do chọn:** Đường cơ sở "công bằng nhất": overlap ~17% để một quy định nằm vắt qua ranh giới vẫn xuất hiện trọn vẹn ở ít nhất một chunk. Ưu điểm là số chunk và chi phí nhúng dự đoán được, không phụ thuộc văn phong tài liệu; nhược điểm là ranh giới cắt hoàn toàn mù ngữ nghĩa.

**Thành viên 3 — [Tên]**
- **Loại chiến lược:** Sentence — `SentenceChunker(max_sentences_per_chunk=2)` / Recursive — `RecursiveChunker(chunk_size=300)`
- **Mô tả & lý do chọn:** `by_sentences(2)` tối ưu cho FAQ và quy định viết theo câu ngắn — mỗi chunk là một đơn vị đọc được, dễ kiểm tra thủ công. `recursive(300)` là lựa chọn "mặc định an toàn": ưu tiên cắt ở đoạn (`\n\n`), rồi dòng, rồi câu, chỉ cắt cứng khi bắt buộc.

### So Sánh Giữa Các Thành Viên

Cùng corpus (`data/k3_university/`, 2 tài liệu), cùng 5 câu hỏi đánh giá, cùng backend mock. Điểm chấm theo `docs/SCORING.md` (2 / 1 / 0 mỗi câu).

| Thành viên | Chiến lược (Strategy) | Số chunk | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|---|----------------------|-----------|----------|
| Vinh | `heading(max=600, min=120)` | 4 | **7** | 3/5 câu có chunk vàng ở **top-1**; không sinh chunk vụn; mỗi chunk tự mang tiêu đề nên truy vết nguồn dễ | Với tài liệu **không có tiêu đề** thì thoái hóa thành một chunk khổng lồ; phụ thuộc chất lượng Markdown đầu vào |
| [TV2] | `fixed_size(300/50)` | 5 | 6 | Số chunk ổn định, overlap cứu được câu bị cắt ngang; 4/5 câu có chunk liên quan trong top-3 | Chunk mở đầu bằng mảnh cụt ("ark. # Đăng ký học phần…") — nhìn là biết cắt mù ngữ nghĩa |
| [TV3] | `by_sentences(2)` | 5 | 4 | Chunk mạch lạc nhất khi đọc bằng mắt | Không tôn trọng ngân sách ký tự; chunk dài ngắn lệch nhau nhiều |
| [TV3] | `recursive(300)` | 5 | 4 | Bám cấu trúc đoạn văn, an toàn cho tài liệu hỗn hợp | Sinh chunk vụn; ở corpus nhỏ này thua cả fixed_size |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Theo số đo, `heading` đứng đầu (7/10) và `fixed_size` bám sát (6/10) — nhưng **nhóm không coi khoảng cách 7 vs 4 là bằng chứng ngữ nghĩa**, vì mock embedding là hàm băm và chênh lệch vài điểm hoàn toàn có thể là nhiễu. Điều **có** cơ sở và lặp lại được là lập luận cấu trúc: với văn bản quy định, đơn vị trả lời tự nhiên là **một mục có tiêu đề**, nên chiến lược nào giữ trọn mục đó thì mỗi lần trúng sẽ trúng đúng chỗ chứa đáp án — thể hiện ở chỗ `heading` có 3/5 câu đưa chunk vàng lên **top-1**, trong khi `by_sentences` truy xuất được chunk liên quan ở 4/5 câu nhưng gần như luôn ở hạng 2–3 (tức là đúng tài liệu, sai vị trí). Ngược lại, `recursive` bị phạt nặng nhất vì cắt vụn: đáp án bị tách khỏi từ khóa của câu hỏi. **Kết luận nhóm:** chọn `heading` làm chiến lược mặc định cho corpus quy định đại học, `fixed_size(300/50)` làm đường lui khi tài liệu không có cấu trúc tiêu đề — và đánh dấu kết luận này là **tạm thời**, phải đo lại với `EMBEDDING_PROVIDER=local` trên corpus 5–10 tài liệu.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên đăng ký học phần ở đâu và theo lịch nào? | Đăng ký trong **cổng học vụ**, theo **lịch của từng học kỳ**. | `k3-course-registration`, chunk chứa cụm "cổng học vụ" |
| 2 | Khi gặp lỗi trùng lịch thì sinh viên phải xử lý thế nào? | **Điều chỉnh lớp học phần trước thời hạn điều chỉnh được công bố.** | `k3-course-registration`, chunk chứa cụm "trùng lịch" |
| 3 | Yêu cầu ngoại lệ về học vụ được gửi qua kênh nào? | Gửi qua **kênh hỗ trợ học vụ chính thức**. | `k3-course-registration`, chunk chứa cụm "kênh hỗ trợ học vụ" |
| 4 | Cần mang theo giấy tờ gì khi mượn tài liệu ở thư viện? | Phải mang **thẻ định danh hợp lệ** khi sử dụng dịch vụ mượn. | `k3-library-services`, chunk chứa cụm "thẻ định danh" |
| 5 | Quy định về học phần tiên quyết áp dụng cho sinh viên là gì? **← cần `metadata_filter={"audience": "student"}`** | Học phần **có thể yêu cầu học phần tiên quyết**; sinh viên phải **kiểm tra điều kiện trước khi xác nhận đăng ký**. | `k3-course-registration` (`audience=student`), chunk chứa cụm "tiên quyết" |

> **Tính đa dạng:** Q1 hỏi *nơi chốn + thời gian*, Q2 hỏi *quy trình xử lý sự cố*, Q3 hỏi *kênh liên hệ*, Q4 hỏi *điều kiện/giấy tờ* (và nằm ở tài liệu **khác**), Q5 hỏi *quy chế theo đối tượng* (cần lọc metadata).
> **Cách chấm liên quan:** nhãn "liên quan" được gán **tự động, khách quan** trong `scripts/run_benchmark.py` — một chunk chỉ được tính là liên quan nếu **đúng `doc_id` vàng** VÀ **chứa cụm từ khóa vàng**. Không có đánh giá cảm tính.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Đăng ký ở đâu, theo lịch nào | `fixed_size` (2/2) và `recursive` (2/2) | Có — 3/4 chiến lược | `heading` **trượt** (0/2): chunk ghi chú front matter chiếm hết top-3 |
| 2 | Xử lý trùng lịch | `fixed_size` (2/2), `heading` (2/2) | Có — 2/4 chiến lược | `by_sentences` và `recursive` đều 0/2 — câu chứa đáp án bị tách khỏi từ khóa truy vấn |
| 3 | Kênh gửi yêu cầu ngoại lệ | `heading` (2/2) | Có — 3/4 chiến lược | `heading` thắng vì cả mục "Đăng ký học phần" nằm trong **một** chunk nên chứa luôn câu về kênh hỗ trợ |
| 4 | Giấy tờ khi mượn thư viện | `by_sentences` (1/2), `heading` (1/2) | Chỉ 2/4 chiến lược | **Câu khó nhất** — không chiến lược nào đạt 2/2; xem Phần 4 (Phân tích lỗi) |
| 5 | Học phần tiên quyết *(có lọc metadata)* | `recursive` (2/2), `heading` (2/2) | Có — 4/4 chiến lược | Nhờ `search_with_filter`, mọi chiến lược đều có ít nhất 1/2 |

**Tổng điểm theo chiến lược:** `heading` **7/10** · `fixed_size` 6/10 · `by_sentences` 4/10 · `recursive` 4/10.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Có, và đo được rõ ở Q5.** Chạy cùng câu hỏi trên cùng store (`recursive(300)`):
>
> | | Hạng 1 | Hạng 2 | Hạng 3 | Điểm |
> |---|---|---|---|---|
> | `search()` — không lọc | `k3-library-services` (audience=all) | `k3-library-services` | `k3-course-registration` ✅ | **1/2** |
> | `search_with_filter({"audience": "student"})` | `k3-course-registration` ✅ | `k3-course-registration` | `k3-course-registration` | **2/2** |
>
> Bộ lọc loại thẳng tài liệu thư viện (`audience=all`) khỏi tập ứng viên, đẩy chunk vàng từ **hạng 3 lên hạng 1** — tăng 1 điểm chỉ bằng một trường metadata, rẻ hơn nhiều so với đi tinh chỉnh `chunk_size`. Đây cũng là lý do phải **lọc trước rồi mới tính similarity**: nếu hậu-lọc, ba chunk sai đối tượng đã chiếm hết top-3 và bộ lọc chỉ còn cách trả về danh sách rỗng.
> **Mặt trái (recall trade-off):** với Q4 (thư viện), nếu vô ý áp `audience=student` thì tài liệu `audience=all` sẽ bị loại và câu hỏi trở nên **không thể trả lời**. Bộ lọc phải bám theo *ý định* của câu hỏi, không phải bật mặc định.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

1. **Rác trong corpus đắt hơn tham số chunking.** Đoạn ghi chú front matter ("Khối metadata phía trên là **template mẫu** cho K3…") không phải nội dung quy định, nhưng dày đặc từ khóa nên chiếm top-1 ở **cả 4 chiến lược** — nhiều nhất là `by_sentences` (**4/5 câu**), rồi `recursive` và `heading` (2/5), `fixed_size` (1/5). Đỉnh điểm: câu hỏi về **thư viện** lại trả về ghi chú của tài liệu **đăng ký học phần** với score 0.413 — điểm cao nhất toàn bài. Một lần dọn dữ liệu có giá trị hơn nhiều giờ chỉnh `chunk_size`.
2. **Cosine similarity chỉ tốt bằng đúng embedder đứng sau nó.** Hai câu gần như đồng nghĩa cho similarity **−0.13**, trong khi hai câu khác chủ đề hẳn cho **+0.07**. Mock chỉ bảo toàn tính đồng nhất chuỗi (câu giống hệt = 1.0000), không bảo toàn ý nghĩa.
3. **Lọc metadata là đòn bẩy rẻ nhất.** Q5: 1/2 → 2/2 chỉ nhờ `audience=student`, không đổi một dòng nào trong chiến lược chunking.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một corpus 2 tài liệu, cùng 5 câu hỏi, chỉ đổi cách cắt chunk mà điểm dao động 4 → 7 / 10. Khác biệt lớn nhất **không nằm ở số chunk** (4 vs 5, gần như bằng nhau) mà ở **ranh giới cắt**: `heading` giữ trọn một mục nên khi trúng là trúng ngay top-1; `recursive` cắt vụn nên đáp án bị tách khỏi từ khóa của câu hỏi và tụt hạng. Nói cách khác, chunking không quyết định *có tìm thấy hay không* nhiều bằng quyết định *tìm thấy ở hạng mấy* — mà top-1 mới là thứ LLM thực sự đọc kỹ.

### Phân tích lỗi (Bài tập 3.5) — bắt buộc

**Trường hợp lỗi 1 — Q4 "Cần mang theo giấy tờ gì khi mượn tài liệu ở thư viện?": không chiến lược nào đạt 2/2, `fixed_size` và `recursive` đạt 0/2.**
- *Hiện tượng:* top-1 luôn là chunk của **tài liệu đăng ký học phần** (score 0.413 / 0.264) — sai cả tài liệu; chunk chứa "thẻ định danh hợp lệ" tụt xuống hạng 2–3 hoặc rơi khỏi top-3.
- *Nguyên nhân (3 lớp):* (a) **Embedder** — mock không có ngữ nghĩa nên "thư viện", "mượn tài liệu" trong câu hỏi không kéo được chunk thư viện lên; (b) **Chất lượng chunk** — chunk thắng lại là đoạn ghi chú template, tức là **nhiễu chưa được dọn khỏi corpus**; (c) **Kích thước corpus** — với 2 tài liệu và 4–5 chunk, mỗi thứ hạng dịch một bậc là điểm đổi ngay, phương sai rất lớn.
- *Đề xuất cải thiện:* (1) **xóa khối ghi chú template khỏi phần body** (hoặc đưa nó vào front matter/comment) để nó không bao giờ được nhúng — sửa rẻ nhất, tác động lớn nhất; (2) chạy lại với `EMBEDDING_PROVIDER=local`; (3) mở rộng corpus lên 5–10 tài liệu thật để mỗi câu hỏi có ít nhất 2 chunk ứng viên đúng chủ đề; (4) bổ sung `search_with_filter({"department": "library"})` cho các câu hỏi đã rõ đơn vị phụ trách.

**Trường hợp lỗi 2 — Q1 với `heading`: 0/2 dù `heading` là chiến lược tốt nhất tổng thể.**
- *Hiện tượng:* `heading` gộp mục ngắn (`min_chars=120`) nên đoạn ghi chú front matter bị **gộp chung** vào một chunk lớn, chunk đó cạnh tranh trực tiếp với chunk chứa "cổng học vụ" và thắng.
- *Nguyên nhân:* cơ chế gộp mục ngắn — vốn sinh ra để tránh chunk vụn — lại **khuếch đại nhiễu** khi nhiễu nằm ở một mục ngắn. Đây là đánh đổi thiết kế, không phải bug.
- *Đề xuất cải thiện:* lọc bỏ các khối `>` (blockquote) và dòng chú thích trước khi chunk; hoặc thêm bước hậu kiểm loại chunk không chứa câu văn hoàn chỉnh nào; hoặc hạ `min_chars` để mục nhiễu đứng riêng và không kéo theo nội dung tốt.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Ba việc, theo thứ tự ưu tiên: (1) **Dọn dữ liệu trước khi chunk** — mọi ghi chú, chú thích template, menu, footer phải bị loại khỏi body; đây là nguồn lỗi số một trong bài này. (2) **Đủ 5–10 tài liệu từ nguồn công khai thật** (học phí, học bổng, ký túc xá) với `source_url` thật và `sources.csv` khớp 1-1 — corpus 2 tài liệu khiến mọi kết luận thống kê đều mong manh. (3) **Chạy benchmark với embedder ngữ nghĩa (`local`) ngay từ đầu**, chỉ dùng mock cho unit test — vì như bài này cho thấy, dùng mock để so chiến lược là đang đo nhiễu của hàm băm chứ không đo chất lượng truy xuất.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 4 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **30 / 40** |

> Tự trừ điểm nặng nhất ở **Lựa chọn tài liệu**: corpus mới có 2/5–10 tài liệu và `source_url` vẫn là placeholder `example.edu`. Đây là hạng mục duy nhất cần bổ sung dữ liệu thật trước khi nộp — phần mã nguồn, chiến lược và quy trình đo đã sẵn sàng, chỉ cần thả thêm file `.md` vào `data/k3_university/` rồi chạy lại `python3 scripts/run_benchmark.py`.
