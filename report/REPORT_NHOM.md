# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** D305_B4_Lab07
**Thành viên:**

- Nguyễn Đức Trung - ndt0126 (Thành viên 1 - Leader & SentenceChunker)
- Nguyễn Tuấn Nam - tnaw04 (Thành viên 2 - Data Curator & RecursiveChunker)
- Nguyễn Quang Vinh - aetrna300bpm (Thành viên 3 - Benchmark Owner & HeaderChunker)
- Đinh Quang Minh - minh20003 (Thành viên 4 - Tech & FixedSizeChunker)

**Ngày:** 3/8/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
Nhóm tập trung vào các dịch vụ & quy định học vụ, học phí, học bổng, thư viện, KTX và dịch vụ thẻ dành cho sinh viên, giảng viên và cán bộ nhân viên đại học.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|---|---|---|---|---|
| 1 | Quy định Đăng ký Học phần và Điều chỉnh Lịch học | https://mybk.hcmut.edu.vn | 2026-08-03 / 2026.1 | 1,250 | `doc_id: course-registration`, `audience: student`, `department: academic-affairs`, `category: academic-regulation` |
| 2 | Quy định Sử dụng Dịch vụ Thư viện và Gia hạn Tài liệu | https://lib.hcmut.edu.vn | 2026-08-03 / 2026.1 | 1,180 | `doc_id: library-services`, `audience: all`, `department: library`, `category: library-policy` |
| 3 | Quy chế Xét trao Học bổng Khuyến khích Học tập | https://ctsv.hcmut.edu.vn | 2026-08-03 / 2026.1 | 1,320 | `doc_id: scholarship-policy`, `audience: student`, `department: student-affairs`, `category: financial-aid` |
| 4 | Quy định Nộp Học phí và Tạm hoãn Nộp Học phí | https://student.ueh.edu.vn | 2026-08-03 / 2026.1 | 1,280 | `doc_id: tuition-fee-policy`, `audience: student`, `department: finance-planning`, `category: financial-aid` |
| 5 | Nội quy Lưu trú và Quy trình Đăng ký Ký túc xá | https://ktx.vnuhcm.edu.vn | 2026-08-03 / 2026.1 | 1,150 | `doc_id: dormitory-regulations`, `audience: student`, `department: dormitory-management`, `category: housing-policy` |
| 6 | Thủ tục Cấp lại Thẻ Cán bộ Sinh viên và Giấy Xác nhận | https://ctt.hust.edu.vn | 2026-08-03 / 2026.1 | 1,100 | `doc_id: student-card-services`, `audience: staff`, `department: student-affairs`, `category: student-services` |
| 7 | Quy chế Hướng dẫn Giảng viên Nhập điểm Học lại và Cải thiện | https://daotao.ueh.edu.vn | 2026-08-03 / 2026.1 | 1,220 | `doc_id: retake-and-improvement`, `audience: faculty`, `department: academic-affairs`, `category: academic-regulation` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|---|---|---|---|
| `doc_id` | string | `course-registration` | Định danh duy nhất tài liệu, dùng để lọc hoặc xóa toàn bộ chunk thuộc văn bản |
| `audience` | string | `student`, `faculty`, `staff`, `all` | Lọc đúng đối tượng áp dụng quy định (tránh sinh viên lấy nhầm quy định giảng viên) |
| `department` | string | `academic-affairs`, `library`, `financial-aid` | Lọc thông tin theo từng phòng ban chức năng trong trường đại học |
| `category` | string | `academic-regulation`, `financial-aid`, `housing-policy` | Phân loại mảng dịch vụ giúp thu hẹp phạm vi tìm kiếm |
| `source_url` | string | `https://mybk.hcmut.edu.vn` | Giúp truy vết nguồn trích dẫn thông tin chính xác |
| `document_version` | string | `2026.1` | Kiểm tra tính hiệu lực và cập nhật của văn bản quy định |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|---|---|---|---|---|
| Quy định Đăng ký Học phần | FixedSizeChunker (`fixed_size`) | 3 | 410 | Trung bình (cắt giữa câu ở ranh giới chunk) |
| Quy định Đăng ký Học phần | SentenceChunker (`by_sentences`) | 4 | 312 | Tốt (giữ nguyên từng câu hoàn chỉnh) |
| Quy định Đăng ký Học phần | RecursiveChunker (`recursive`) | 3 | 415 | Rất tốt (chia ưu tiên theo đoạn `\n\n` và mục) |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Đức Trung**

- **Loại chiến lược:** SentenceChunker (`max_sentences=3`)
- **Mô tả & lý do chọn cho chủ đề này:** Tách các câu văn bản theo ranh giới câu (`.`, `!`, `?`) và gom 3 câu thành một chunk. Lý do: Quy định đại học thường diễn đạt rõ ràng theo từng câu ngắn, việc giữ nguyên câu giúp giữ trọn vẹn ngữ nghĩa từng quy định.

**Thành viên 2 — Nguyễn Tuấn Nam**

- **Loại chiến lược:** RecursiveChunker (`chunk_size=400`, `overlap=50`, separators=`["\n\n", "\n", ". ", " "]`)
- **Mô tả & lý do chọn:** Chia nhỏ đệ quy ưu tiên giữ lại các đoạn văn (`\n\n`), sau đó mới đến dòng (`\n`) và câu. Lý do: Giữ cấu trúc đoạn văn của văn bản quy định giúp câu trả lời RAG mạch lạc hơn.

**Thành viên 3 — Nguyễn Quang Vinh**

- **Loại chiến lược:** Header/Section-based Chunker (chia theo `#`, `##`)
- **Mô tả & lý do chọn:** Tách chunk theo từng mục điều khoản (Section 1, Section 2...). Lý do: Mỗi mục trong sổ tay quy định đại học tập trung vào 1 chủ đề độc lập (như Điều chỉnh môn, Rút môn, Trùng lịch...).

**Thành viên 4 — Đinh Quang Minh**

- **Loại chiến lược:** FixedSizeChunker (`chunk_size=800`, `overlap=150`)
- **Mô tả & lý do chọn:** Dùng chunk size lớn hơn với overlap cao để đảm bảo không bị mất ngữ cảnh giữa các đoạn thông tin liên quan đến phí phạt và quy trình.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|
| Nguyễn Đức Trung | SentenceChunker | 9/10 | Chunk gọn, chính xác từng câu quy định | Có thể thiếu ngữ cảnh nếu điều kiện nằm ở câu trước |
| Nguyễn Tuấn Nam | RecursiveChunker | 9.5/10 | Giữ cấu trúc đoạn mạch lạc, truy xuất chính xác | Chunk kích thước không đều |
| Nguyễn Quang Vinh | Header-based Chunker | 9/10 | Chunk theo đúng logic điều khoản | Kích thước chunk phụ thuộc độ dài mục |
| Đinh Quang Minh | FixedSizeChunker | 7.5/10 | Phủ đủ ngữ cảnh dài | Cắt giữa câu, chứa thông tin thừa |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
`RecursiveChunker` và `Header-based Chunker` cho kết quả truy xuất tốt nhất đối với quy định đại học. Vì các văn bản quy định được cấu trúc theo mục và đoạn văn bản rõ ràng; việc phân chia theo ranh giới tự nhiên này giữ trọn vẹn ngữ cảnh của từng chính sách.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|---|---|---|
| 1 | Sinh viên được đăng ký tối thiểu và tối đa bao nhiêu tín chỉ trong một học kỳ chính? | Số tín chỉ tối thiểu cho một học kỳ chính là 12 tín chỉ, tối đa là 24 tín chỉ đối với sinh viên có học lực bình thường. | `course-registration::chunk_0` |
| 2 | Phí phạt khi trả sách thư viện quá hạn là bao nhiêu và khi nào tài khoản bị khóa? | Trả sách quá hạn chịu phí phạt 5.000 VNĐ / 1 tài liệu / 1 ngày quá hạn. Tài khoản bị khóa tự động nếu tiền phạt chưa nộp vượt quá 50.000 VNĐ. | `library-services::chunk_2` |
| 3 | (Filter `audience: student`) Điều kiện về GPA và điểm rèn luyện để đạt học bổng Khuyến khích loại Xuất sắc là gì? | Điểm GPA từ 3.60 trở lên và điểm rèn luyện (DRL) từ 90 điểm trở lên. Giá trị học bổng bằng 120% học phí học kỳ. | `scholarship-policy::chunk_0` |
| 4 | Thời gian xin gia hạn nộp học phí tối đa là bao lâu và cần những hồ sơ gì? | Thời gian gia hạn tối đa 60 ngày kể từ hạn nộp chính thức. Hồ sơ gồm Đơn xin gia hạn có xác nhận địa phương (hoặc minh chứng y tế) và bảng điểm học kỳ gần nhất. | `tuition-fee-policy::chunk_1` |
| 5 | Ký túc xá mở cửa và đóng cửa vào khung giờ nào hàng ngày? | KTX mở cửa từ 05:00 và đóng cửa lúc 23:00 hàng ngày. Sinh viên về sau 23:00 phải có giấy xác nhận lý do hoặc đơn bảo lãnh của phụ huynh. | `dormitory-regulations::chunk_1` |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---|---|---|---|
| 1 | Đăng ký tín chỉ tối thiểu / tối đa | RecursiveChunker | Có (Top 1) | Trả về chính xác điều 1 |
| 2 | Phí phạt trả sách thư viện quá hạn | SentenceChunker | Có (Top 1) | Trả về đúng mức phạt 5.000đ |
| 3 | Điều kiện học bổng Xuất sắc | HeaderChunker (Filter `audience: student`) | Có (Top 1) | Loại bỏ tài liệu dành cho giảng viên/staff |
| 4 | Gia hạn nộp học phí | RecursiveChunker | Có (Top 1) | Trả về chính xác 60 ngày & hồ sơ |
| 5 | Giờ đóng mở cửa KTX | SentenceChunker | Có (Top 1) | Trả về đúng khung giờ 05:00 - 23:00 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Lọc bằng metadata rất hiệu quả ở Câu hỏi 3 (`metadata_filter={"audience": "student"}`). Bộ lọc giúp loại bỏ các văn bản hướng dẫn nhập điểm của Giảng viên (`faculty`) hoặc cấp thẻ Cán bộ (`staff`), thu hẹp phạm vi truy xuất chính xác vào chính sách dành cho sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. Lọc bằng Metadata (`audience`, `department`) giúp tăng Precision của RAG rõ rệt khi truy xuất tập tài liệu đa đối tượng.
2. Với văn bản quy định có cấu trúc, `RecursiveChunker` và chia theo Heading/Section vượt trội hơn `FixedSizeChunker` vì giữ trọn vẹn từng điều khoản độc lập.

**Bài học rút ra khi so sánh trong nhóm:**
Cùng một bộ tài liệu, nếu cắt `FixedSize` quá cứng nhắc sẽ bị vỡ câu ở ranh giới chunk, làm giảm điểm Cosine Similarity của câu hỏi. Ngược lại, chunking theo ngữ nghĩa (câu/đoạn) giúp Vector Embedding nắm bắt trọn vẹn ngữ nghĩa tốt hơn nhiều.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
Nhóm sẽ bổ sung thêm các trường metadata chi tiết hơn như `effective_date` và `semester` để hỗ trợ lọc các quy định áp dụng theo từng năm học cụ thể.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|---|---|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
