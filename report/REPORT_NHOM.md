# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** D305_B4_Lab07

**Thành viên:** Nguyễn Đức Trung (Leader & SentenceChunker), Nguyễn Tuấn Nam (Data Curator & RecursiveChunker), Nguyễn Quang Vinh (Benchmark Owner & HeadingChunker), Đinh Quang Minh (Tech & FixedSizeChunker)
**Ngày:** 03/08/2026

> Phạm vi báo cáo này chỉ sử dụng corpus `data/qnu_regulations`; không dùng corpus minh hoạ nào khác cho kết quả, kết luận hoặc benchmark.

## 1. Corpus và metadata

Corpus gồm 5 văn bản quy định công khai của QNU. Mỗi văn bản có `source_url`, `retrieved_at`, `document_version`, cùng các trường `doc_id`, `audience`, `department`, `category` để truy vết provenance và lọc theo đối tượng.

| doc_id | Văn bản | audience | category |
|---|---|---|---|
| `qd1401_2022_qnu` | Quyết định 1401/QĐ-ĐHQN năm 2022 | student | regulation |
| `qyd474_2022_qnu` | Quyết định 474/QĐ-ĐHQN năm 2022 | student | regulation |
| `qyd828_2023_qnu` | Quyết định 828/QĐ-ĐHQN năm 2023 | staff | regulation |
| `tb1525_2023_qnu` | Thông báo 1525/TB-ĐHQN năm 2023 | faculty | regulation |
| `tb209_2024_qnu` | Thông báo 209/TB-ĐHQN năm 2024 | all | regulation |

`sources.csv` có ánh xạ 1–1 với năm tệp Markdown. Giới hạn dữ liệu cần ghi nhận: văn bản `qyd474_2022_qnu` chưa chứa bảng mức thu học phí gốc; `tb209_2024_qnu` còn vài marker giao diện do crawl. Hai điểm này ảnh hưởng trực tiếp đến recall và độ sạch context.

## 2. Các chiến lược chunking

Tất cả chiến lược chạy cùng LocalEmbedder `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

| Thành viên | Strategy | Cấu hình | Số chunk | Điểm chunk-level (/10) |
|---|---|---:|---:|---:|
| Nguyễn Đức Trung | SentenceChunker | 3 câu/chunk | 18 | 6 |
| Nguyễn Tuấn Nam | RecursiveChunker | 400 ký tự, overlap 50 | 36 | 4 |
| Nguyễn Quang Vinh | HeadingChunker | tối đa 600 ký tự | 22 | 5 |
| Đinh Quang Minh | FixedSizeChunker | 800 ký tự, overlap 150 | 17 | 5 |

SentenceChunker đạt điểm tổng cao nhất trong lần chạy này, nhưng không có chiến lược nào đúng tuyệt đối. Chênh lệch cho thấy điểm cosine cao chỉ phản ánh thứ hạng ngữ nghĩa, không chứng minh chunk chứa dữ kiện trả lời.

## 3. Benchmark ở mức chunk

Mỗi query được chấm theo rubric: **2 điểm** khi top-3 có chunk chứa evidence và câu trả lời trích từ chunk top-1 chứa đủ đáp án; **1 điểm** khi evidence có ở top-3 nhưng không đứng top-1/context chưa đủ; **0 điểm** khi top-3 không có evidence. Evidence được kiểm bằng chuỗi đặc trưng trong nội dung chunk, không chỉ bằng `doc_id`.

| Query | Evidence cần có | Kết quả tốt nhất | Nhận xét |
|---|---|---:|---|
| Nghỉ Tết 2024 theo TB209 | mốc thời gian nghỉ | 2/2 | SentenceChunker đưa đúng chunk evidence lên top-1. |
| Hiệu lực QĐ1401 (filter `audience=student`) | “thay thế 1455/QĐ” | 2/2 | Heading/Fixed đưa đúng section lên top-1; Sentence đưa cùng tài liệu nhưng evidence ở rank 2. |
| Hiệu lực/phạm vi QĐ474 | nội dung QĐ474 | 1/2 | FixedSize có evidence ở rank 3; các strategy khác không có evidence trong top-3. |
| Thời hạn và đường dẫn trong TB1525 | ngày nộp và URL | 1/2 | Sentence có evidence ở rank 3; context top-1 không đủ. |
| Đối tượng áp dụng QĐ828 | lớp/ngành áp dụng | 2/2 | Sentence đưa evidence lên top-1. |

Chi tiết từng top-3 (chunk id, score, relevance, context và câu trả lời agent) được lưu trong `report/benchmark_raw.md`, có thể tái tạo bằng `EMBEDDING_PROVIDER=local python bench.py`.

### A/B metadata filter

Với query QĐ1401, chạy cả bốn strategy hai lần: có và không có `metadata_filter={"audience": "student"}`. Top-3 và điểm không đổi ở cả bốn strategy (Sentence 1/1, Recursive 1/1, Heading 2/2, Fixed 2/2). Điều này không chứng minh filter vô dụng nói chung: query quá đặc hiệu và corpus không có tài liệu cạnh tranh gần nghĩa. Trong tập hiện tại, filter không tạo thêm utility đo được cho query này.

## 4. Failure analysis

**Failure chính — QĐ474:** query hỏi hiệu lực/phạm vi QĐ474. Với SentenceChunker, top-3 lần lượt là chunk của QĐ828 và TB1525 (score cao nhất 0.7749), không có evidence QĐ474 nên đạt 0/2. FixedSize chỉ tìm thấy evidence tại rank 3. Nguyên nhân là các văn bản cùng chủ đề “quy định/quyết định” có ngữ nghĩa bề mặt gần nhau, trong khi nguồn QĐ474 thiếu bảng/nội dung chi tiết giúp phân biệt. Cách sửa: crawl lại bản đầy đủ/bảng gốc của QĐ474, chuẩn hoá dữ liệu crawl, thêm metadata `program_type`/`effective_date`, và thử query expansion theo số quyết định.

**Failure thứ hai — đúng tài liệu nhưng sai section:** ở QĐ1401 với SentenceChunker, top-1 là phần mở đầu (0.7936), còn câu “thay thế 1455/QĐ” nằm ở chunk rank 2 (0.7920). Nếu chỉ chấm `doc_id`, trường hợp này bị tính nhầm là đúng; chấm theo evidence chunk cho kết quả 1/2. Chia theo heading hoặc tăng overlap giúp thông tin điều kiện và hiệu lực ở cùng context hơn.

Kết luận: cần báo cáo provenance theo chunk, không suy diễn nội dung đúng từ score cao hoặc từ việc tài liệu gold xuất hiện trong top-k.

## 5. Tự đánh giá phần nhóm

| Tiêu chí | Tự đánh giá |
|---|---:|
| Lựa chọn tài liệu và provenance | 8 / 10 |
| Thiết kế, so sánh chiến lược | 14 / 15 |
| Chất lượng truy xuất và failure analysis | 8 / 10 |
| Demo / khả năng tái tạo | 5 / 5 |
| **Tổng** | **35 / 40** |
