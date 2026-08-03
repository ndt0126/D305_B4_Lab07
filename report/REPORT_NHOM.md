# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Điền tên nhóm]

**Ngày:** 2026-08-03

### Thành viên và phân công

| STT | Họ và tên | Vai trò | Chiến lược phụ trách |
|---:|---|---|---|
| 1 | **Nguyễn Đức Trung** | Trưởng nhóm (Leader) | `SentenceChunker(3)` |
| 2 | **Nguyễn Tuấn Nam** | Phụ trách dữ liệu (Data Curator) | `RecursiveChunker(600)` |
| 3 | **Nguyễn Quang Vinh** | Phụ trách benchmark (Benchmark Owner) | `HeadingChunker(min_level=1, max_level=3)` |
| 4 | **Đinh Quang Minh** | Phụ trách kỹ thuật (Tech) | `FixedSizeChunker(500, overlap=80)` |

> Nộp 1 bản/nhóm. Số liệu dưới đây được sinh bởi `scripts/run_benchmark.py` với model local `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; kết quả chi tiết nằm trong `report/benchmark_raw.md`.

## 1. Lựa chọn tài liệu — 10 điểm

### Phạm vi

Nhóm xây dựng cơ sở tri thức về **quy định và thông báo dành cho người học của Trường Đại học Quy Nhơn**, đúng chủ đề dịch vụ/quy định đại học của lớp K3. Corpus có 5 trang công khai, không chứa thông tin đăng nhập hay dữ liệu cá nhân. Nội dung đã được làm sạch khỏi menu, hộp thoại và phần lặp do crawl; không tự bổ sung dữ kiện pháp lý bị thiếu.

### Danh sách tài liệu

| # | Tài liệu | Nội dung chính | Nguồn công khai | Ký tự |
|---:|---|---|---|---:|
| 1 | QĐ1401 | Quy chế tuyển sinh đại học | [QNU](https://www.qnu.edu.vn/vi/dai-hoc-chinh-quy-1764/qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc) | 1.379 |
| 2 | QyĐ474 | Học phí đào tạo từ xa, đợt 1 tháng 2/2026 | [QNU](https://www.qnu.edu.vn/vi/tuyen-sinh-1763/qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1) | 1.340 |
| 3 | QyĐ828 | Học phí hệ vừa làm vừa học khóa 34 | [QNU](https://www.qnu.edu.vn/vi/tuyen-sinh-1763/qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024) | 1.486 |
| 4 | TB1525 | Lịch học và nộp học phí cao học khóa 28B | [QNU](https://www.qnu.edu.vn/vi/hoc-phi-quy-dinh/tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027) | 3.514 |
| 5 | TB209 | Lịch nghỉ Tết Bính Ngọ 2026 của sinh viên | [QNU](https://www.qnu.edu.vn/vi/tuyen-sinh-1763/tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien) | 1.794 |

Bảng `data/qnu_regulations/sources.csv` ánh xạ 1–1 giữa `doc_id`, file, URL, ngày lấy `2026-08-03`, phiên bản và quyền sử dụng `public-page`.

### Metadata schema

| Trường | Ví dụ | Vai trò |
|---|---|---|
| `doc_id` | `quy-dinh-05-...` | Truy vết chunk và xóa toàn bộ tài liệu |
| `source_url` | URL QNU | Kiểm chứng nguồn câu trả lời |
| `retrieved_at` | `2026-08-03` | Theo dõi thời điểm lấy dữ liệu |
| `document_version` | `not-stated` | Không bịa phiên bản khi trang nguồn không nêu |
| `audience` | `student` | Trường bắt buộc K3; dùng ở Q5 |
| `department` | `finance` | Thu hẹp theo đơn vị nghiệp vụ |
| `program` | `part-time` | Phân biệt hệ đào tạo; dùng ở Q3 |
| `topic` | `tuition` | Phân loại ý định truy vấn |
| `category`, `language`, `university` | `regulation`, `vi`, `Trường Đại học Quy Nhơn` | Lọc và quản trị corpus |
| `chunk_index` | `0` | Được `ingest.py` gắn để giữ thứ tự chunk |

Checklist dữ liệu: 5/5 tài liệu có đủ `source_url`, `retrieved_at`, `document_version`, `audience` và ít nhất hai trường hữu ích khác; 5/5 URL là nguồn công khai thật.

## 2. Thiết kế chiến lược — 15 điểm

### Baseline trên ba tài liệu

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=500)`:

| Tài liệu | Fixed: count/avg | Sentence: count/avg | Recursive: count/avg |
|---|---:|---:|---:|
| QĐ1401 (1.379 ký tự) | 3 / 493,0 | 3 / 454,3 | 4 / 342,2 |
| QyĐ474 (1.340 ký tự) | 3 / 480,0 | 2 / 665,5 | 3 / 444,3 |
| QyĐ828 (1.486 ký tự) | 4 / 409,0 | 2 / 740,5 | 4 / 369,2 |

Quan sát: Fixed giữ ngân sách ổn định nhưng có thể cắt ngang ý; Sentence giữ câu nguyên vẹn nhưng tạo chunk rất lệch (tối đa 1.356 ký tự); Recursive ưu tiên ranh giới tự nhiên nhưng tạo nhiều chunk hơn. Vì văn bản quy định có tiêu đề rõ, nhóm bổ sung đối chứng Heading.

### Các cấu hình được so sánh

| Người/cấu hình | Chiến lược | Lý do và đánh đổi |
|---|---|---|
| **Nguyễn Đức Trung — Leader** | `SentenceChunker(3)` | Chunk dễ đọc và nguyên câu; không đảm bảo giới hạn ký tự. |
| **Nguyễn Tuấn Nam — Data Curator** | `RecursiveChunker(600)` | Ưu tiên đoạn/dòng/câu; phù hợp văn bản hỗn hợp nhưng có thể tách đáp án khỏi tiêu đề. |
| **Nguyễn Quang Vinh — Benchmark Owner** | `HeadingChunker(min_level=1, max_level=3)` | Giữ trọn mục và tiêu đề — đơn vị trả lời tự nhiên của văn bản quy định. Corpus hiện chỉ có ít heading nên chunk lớn; có thể loãng ngữ nghĩa khi tài liệu dài. Đáp ứng yêu cầu K3 về heading/section chunking. |
| **Đinh Quang Minh — Tech** | `FixedSizeChunker(500, overlap=80)` | Kích thước dự đoán được; overlap cứu thông tin ở ranh giới, đổi lại có mảnh đầu/cuối câu. |

> Bốn cấu hình đã được chạy đầy đủ trên cùng corpus, cùng năm câu hỏi và cùng local embedding model. Vai trò và chiến lược ở bảng trên đã được gán theo phân công chính thức của nhóm.

### Kết quả so sánh

| Chiến lược | Số chunk | Gold ở top-1 | Điểm retrieval |
|---|---:|---:|---:|
| Heading level 1–3 | 6 | **5/5** | **10/10** |
| Sentence, 3 câu | 18 | 4/5 | 9/10 |
| Fixed 500/80 | 25 | 3/5 | 8/10 |
| Recursive 600 | 23 | 4/5 | 8/10 |

Heading thắng vì mỗi tài liệu ngắn tương ứng gần với một đơn vị quy định hoàn chỉnh: từ khóa định danh văn bản và bằng chứng trả lời nằm cùng chunk. Với tài liệu dài hơn, nhóm sẽ kết hợp Heading với Recursive để tránh chunk quá lớn.

## 3. Bộ câu hỏi đánh giá và chất lượng truy xuất — 10 điểm

### Đúng 5 benchmark queries

| # | Câu hỏi | Gold answer | Tài liệu/cụm bằng chứng | Filter |
|---:|---|---|---|---|
| 1 | Quyết định 1401 có hiệu lực khi nào và thay thế quyết định nào? | Có hiệu lực từ ngày ký; thay thế QĐ1455/QĐ-ĐHQN ngày 21/5/2025. | QĐ1401 — “có hiệu lực kể từ ngày ký và thay thế…” | — |
| 2 | QyĐ474 quy định mức học phí cho hệ đào tạo đại học từ xa tuyển sinh đợt nào? | Tháng 2/2026, Đợt 1. | QyĐ474 — “tuyển sinh tháng 2 năm 2026 (Đợt 1)” | — |
| 3 | Quy định 828 áp dụng mức học phí cho khóa và ngành nào? | Khóa 34, ngành Quản lý đất đai, tuyển sinh 2024. | QyĐ828 — “khóa 34 ngành Quản lý đất đai…” | `program=part-time` |
| 4 | Học viên cao học khóa 28B phải nộp học phí Học kỳ 2 đến khi nào? | Từ 15/5/2026 đến hết 02/8/2026. | TB1525 — dòng “Thời gian nộp học phí” | `program=graduate` |
| 5 | Sinh viên Trường Đại học Quy Nhơn nghỉ Tết Nguyên đán 2026 từ ngày nào đến ngày nào? | Từ 09/02/2026 đến hết 01/03/2026. | TB209 — mục 1 | `audience=student` **(bắt buộc K3)** |

Các câu hỏi đa dạng: hiệu lực văn bản, đối tượng tuyển sinh, hệ/ngành đào tạo, hạn nộp tiền và lịch nghỉ. Gold answer đều có cụm bằng chứng trực tiếp trong corpus, không suy đoán.

### Kết quả theo câu với chiến lược Heading của Nguyễn Quang Vinh

| Q | Top-1 | Score | Agent có đủ grounding? | Điểm |
|---:|---|---:|---|---:|
| 1 | QĐ1401 | 0,4893 | Có; trả lời đúng hiệu lực và văn bản thay thế | 2/2 |
| 2 | QyĐ474 | 0,8007 | Có; trả lời đúng tháng/đợt tuyển sinh | 2/2 |
| 3 | QyĐ828 | 0,6047 | Có; trả lời đúng khóa/ngành; dùng `program=part-time` | 2/2 |
| 4 | TB1525 | 0,7628 | Có; trả lời đúng hạn nộp; dùng `program=graduate` | 2/2 |
| 5 | TB209 | 0,7740 | Có; trả lời đúng khoảng nghỉ; dùng `audience=student` | 2/2 |

**Tổng Heading: 10/10; top-3 relevant: 5/5; top-1 relevant: 5/5.** Agent benchmark là hàm kiểm tra grounding xác định: chỉ trả gold answer khi top-3 thật sự chứa cụm bằng chứng, nếu không trả “Không đủ thông tin”.

### Tác động metadata filter

Với Recursive và Q3, không lọc trả nhầm QĐ1401 ở top-1 và không có chunk vàng trong top-3 (**0/2**). Khi lọc `program=part-time`, tập ứng viên chỉ còn QyĐ828 và chunk vàng lên top-1 (**2/2**). Q5 dùng đúng `audience=student`; do toàn corpus hiện hướng đến người học nên thứ hạng không đổi — đây là kết quả trung thực, không phóng đại tác dụng filter.

## 4. Demo, failure analysis và bài học — 5 điểm

### Luồng demo

UI Streamlit trong `demo_ui.py` cho phép:

1. Chọn corpus QNU, backend local/mock, chiến lược chunking và tham số.
2. Đặt `top_k`, nhập metadata filter rồi tìm kiếm.
3. Xem câu trả lời có grounding, top-k chunk, score, metadata và URL nguồn.
4. So sánh bốn chiến lược trên cùng câu hỏi và xem thống kê corpus.
5. Thử Q3 trước/sau `program=part-time`, sau đó Q5 với `audience=student`.

Chạy theo `docs/UI_DEMO.md`; bộ câu hỏi demo chính là năm benchmark ở trên.

### Failure case bắt buộc

**Câu hỏi:** “Mức học phí cụ thể theo khối ngành trong QyĐ474 là bao nhiêu?”

Retrieval tìm được đúng QyĐ474, nhưng bản HTML đã crawl chỉ còn tiêu đề `I. Mức học phí theo khối ngành`; bảng số tiền không xuất hiện trong phần text. Agent phải nói không đủ thông tin thay vì bịa số tiền. Nguyên nhân nằm ở **độ đầy đủ của nguồn**, không phải chỉ ở chunking. Cách cải thiện là lấy tệp đính kèm/PDF công khai nếu được phép, trích xuất bảng, giữ URL và phiên bản; sau đó thêm một gold answer mới vào benchmark khác, không thay đổi năm câu đang dùng để so sánh.

### Bài học

- Cấu trúc tài liệu quyết định chiến lược: Heading phù hợp corpus quy định ngắn, có tiêu đề; Sentence/Recursive là phương án tốt hơn khi section dài.
- Metadata filter có thể sửa lỗi sai tài liệu (Q3: 0/2 → 2/2), nhưng không sửa được thứ hạng sai giữa các chunk trong cùng tài liệu.
- Local multilingual embeddings cần cho kết luận ngữ nghĩa; mock chỉ phù hợp unit test.
- Grounding không thể bù dữ liệu nguồn bị thiếu. Khi không có bằng chứng, câu trả lời đúng là thừa nhận thiếu thông tin.

## Tự đánh giá phần nhóm

| Tiêu chí | Điểm |
|---|---:|
| Lựa chọn tài liệu | 10/10 |
| Thiết kế chiến lược | 15/15 |
| Chất lượng truy xuất | 10/10 |
| Demo đã chuẩn bị | 5/5 |
| **Tổng** | **40/40** |

> Trước khi nộp chỉ còn điền tên nhóm. Danh sách thành viên, vai trò và chiến lược đã được cập nhật; phần trình bày trực tiếp vẫn phải do nhóm thực hiện.