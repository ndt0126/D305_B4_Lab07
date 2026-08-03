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

`sources.csv` có ánh xạ 1–1 với năm tệp Markdown. Trường `audience` có **4 giá trị khác nhau** (`student`, `staff`, `faculty`, `all`) nên bộ lọc metadata thực sự có tập để loại. Giới hạn dữ liệu cần ghi nhận: văn bản `qyd474_2022_qnu` chưa chứa bảng mức thu học phí gốc; `tb209_2024_qnu` còn vài marker giao diện do crawl. Hai điểm này ảnh hưởng trực tiếp đến recall và độ sạch context.

## 2. Các chiến lược chunking

Tất cả chiến lược chạy cùng LocalEmbedder `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

| Thành viên | Strategy | Cấu hình | Số chunk | Điểm chunk-level (/10) |
|---|---|---:|---:|---:|
| Nguyễn Đức Trung | SentenceChunker | 3 câu/chunk | 18 | 6 |
| Nguyễn Tuấn Nam | RecursiveChunker | 400 ký tự, overlap 50 | 36 | 4 |
| Nguyễn Quang Vinh | HeadingChunker | tối đa 600 ký tự | 22 | 5 |
| Đinh Quang Minh | FixedSizeChunker | 800 ký tự, overlap 150 | 17 | 5 |

Bốn chiến lược **không trùng nhau** và chỉ khác nhau ở dòng chọn chunker; corpus, bộ query và embedder giữ nguyên để so sánh công bằng. SentenceChunker đạt điểm tổng cao nhất trong lần chạy này, nhưng không có chiến lược nào đúng tuyệt đối. Chênh lệch cho thấy điểm cosine cao chỉ phản ánh thứ hạng ngữ nghĩa, không chứng minh chunk chứa dữ kiện trả lời.

## 3. Benchmark ở mức chunk

### 5 benchmark query và gold answer

Nhóm chốt đúng 5 query trước khi chạy bất kỳ strategy nào, và **không sửa query sau khi đã xem kết quả**. Mỗi gold answer trích trực tiếp từ corpus, kèm tài liệu và chuỗi bằng chứng dùng để chấm.

| # | Query | Gold answer | Tài liệu / evidence | Loại |
|---|---|---|---|---|
| 1 | Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 bao lâu, từ ngày nào và học lại khi nào? | Nghỉ 03 tuần từ 09/02/2026 đến hết 01/03/2026 và học lại từ 02/03/2026. | `tb209_2024_qnu` — mốc thời gian nghỉ | Số liệu / thời gian |
| 2 | Quy chế tuyển sinh đại học ban hành kèm QĐ1401 có hiệu lực khi nào và thay thế quyết định nào? **(bắt buộc dùng `metadata_filter={"audience": "student"}`)** | Có hiệu lực từ ngày ký và thay thế Quyết định 1455/QĐ-ĐHQN ngày 21/5/2025. | `qd1401_2022_qnu` — chuỗi "thay thế 1455/QĐ" | Điều kiện / hiệu lực |
| 3 | Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào? | Áp dụng cho đào tạo đại học từ xa tuyển sinh tháng 2/2026 đợt 1 và có hiệu lực từ ngày ký. | `qyd474_2022_qnu` — phạm vi áp dụng | Phạm vi / ngoại lệ |
| 4 | Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào? | Nộp từ 15/5/2026 đến hết 02/8/2026, qua cổng https://e-bills.vn/pay/qnu hoặc QR Code. | `tb1525_2023_qnu` — ngày nộp và URL | Quy trình |
| 5 | QyĐ828 về học phí năm học 2024-2025 áp dụng cho hệ đào tạo, khóa và ngành nào? | Áp dụng cho hệ vừa làm vừa học khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024. | `qyd828_2023_qnu` — lớp/ngành áp dụng | Liệt kê |

### Cách chấm và kết quả

Mỗi query được chấm theo rubric: **2 điểm** khi top-3 có chunk chứa evidence và câu trả lời trích từ chunk top-1 chứa đủ đáp án; **1 điểm** khi evidence có ở top-3 nhưng không đứng top-1/context chưa đủ; **0 điểm** khi top-3 không có evidence. Evidence được kiểm bằng chuỗi đặc trưng trong nội dung chunk, không chỉ bằng `doc_id`.

| Query | Evidence cần có | Kết quả tốt nhất | Nhận xét |
|---|---|---:|---|
| Nghỉ Tết 2026 theo TB209 | mốc thời gian nghỉ | 2/2 | SentenceChunker đưa đúng chunk evidence lên top-1. |
| Hiệu lực QĐ1401 (filter `audience=student`) | "thay thế 1455/QĐ" | 2/2 | Heading/Fixed đưa đúng section lên top-1; Sentence đưa cùng tài liệu nhưng evidence ở rank 2. |
| Hiệu lực/phạm vi QĐ474 | nội dung QĐ474 | 1/2 | FixedSize có evidence ở rank 3; các strategy khác không có evidence trong top-3. |
| Thời hạn và đường dẫn trong TB1525 | ngày nộp và URL | 1/2 | Sentence có evidence ở rank 3; context top-1 không đủ. |
| Đối tượng áp dụng QĐ828 | lớp/ngành áp dụng | 2/2 | Sentence đưa evidence lên top-1. |

Chi tiết từng top-3 (chunk id, score, relevance, context và câu trả lời agent) được lưu trong `report/benchmark_raw.md`, có thể tái tạo bằng `EMBEDDING_PROVIDER=local python bench.py`.

### A/B metadata filter

Với query QĐ1401, chạy cả bốn strategy hai lần: có và không có `metadata_filter={"audience": "student"}`. Top-3 và điểm không đổi ở cả bốn strategy (Sentence 1/1, Recursive 1/1, Heading 2/2, Fixed 2/2). Điều này không chứng minh filter vô dụng nói chung: query quá đặc hiệu và corpus không có tài liệu cạnh tranh gần nghĩa. Trong tập hiện tại, filter không tạo thêm utility đo được cho query này.

Đánh đổi recall cần nêu rõ: `audience` trong corpus có 4 giá trị, nên nếu áp nhầm `audience=student` cho một câu hỏi về học phí cao học (`tb1525_2023_qnu` mang `faculty`) thì tài liệu chứa đáp án sẽ **bị loại sạch** và câu hỏi trở nên không thể trả lời. Bộ lọc phải bám theo ý định của câu hỏi, không nên bật mặc định.

## 4. Failure analysis

**Failure chính — QĐ474:** query hỏi hiệu lực/phạm vi QĐ474. Với SentenceChunker, top-3 lần lượt là chunk của QĐ828 và TB1525 (score cao nhất 0.7749), không có evidence QĐ474 nên đạt 0/2. FixedSize chỉ tìm thấy evidence tại rank 3. Nguyên nhân là các văn bản cùng chủ đề "quy định/quyết định" có ngữ nghĩa bề mặt gần nhau, trong khi nguồn QĐ474 thiếu bảng/nội dung chi tiết giúp phân biệt. Cách sửa: crawl lại bản đầy đủ/bảng gốc của QĐ474, chuẩn hoá dữ liệu crawl, thêm metadata `program_type`/`effective_date`, và thử query expansion theo số quyết định.

**Failure thứ hai — đúng tài liệu nhưng sai section:** ở QĐ1401 với SentenceChunker, top-1 là phần mở đầu (0.7936), còn câu "thay thế 1455/QĐ" nằm ở chunk rank 2 (0.7920). Nếu chỉ chấm `doc_id`, trường hợp này bị tính nhầm là đúng; chấm theo evidence chunk cho kết quả 1/2. Chia theo heading hoặc tăng overlap giúp thông tin điều kiện và hiệu lực ở cùng context hơn.

**Failure thứ ba — HeadingChunker ở Q4 (0/2):** top-1 là `tb1525...::chunk_6` (0.6756) — đúng tài liệu nhưng là mục "đề nghị học viên thực hiện đúng thời gian", không phải mục chứa mốc ngày và URL cổng thanh toán. Đây là giới hạn của chunk theo section: khi một văn bản có nhiều mục cùng chủ đề, ranh giới tiêu đề không đủ để phân biệt mục nào chứa dữ kiện. Cách sửa: hạ `max_chars` để mục dài tách theo tiểu mục, hoặc bổ sung trường metadata theo loại nội dung.

Kết luận: cần báo cáo provenance theo chunk, không suy diễn nội dung đúng từ score cao hoặc từ việc tài liệu gold xuất hiện trong top-k.

## 5. Demo (6–8 phút)

| Thời lượng | Nội dung | Người trình bày |
|---|---|---|
| 1 phút | Phạm vi corpus QNU, nguồn và metadata schema (`audience` 4 giá trị, provenance đủ 3 trường) | Nguyễn Tuấn Nam (Data Curator) |
| 2 phút | Mỗi thành viên giải thích strategy của mình và lý do chọn cho văn bản quy định | Cả 4 thành viên |
| 3 phút | So sánh kết quả: bảng điểm 4 strategy, A/B metadata filter, và failure case QĐ474 kèm bằng chứng top-3 | Nguyễn Quang Vinh (Benchmark Owner) |
| 1–2 phút | Chạy live một query trên terminal đã mở sẵn `bench.py` | Đinh Quang Minh (Tech) |

**Ba câu hỏi nhóm chuẩn bị sẵn cho phần hỏi đáp:**

1. *Strategy nào tái dùng được khi đổi domain?* — `HeadingChunker` phụ thuộc vào việc nguồn có cấu trúc tiêu đề; với văn bản quy định thì tốt, với văn bản thô không heading thì thoái hoá thành một chunk lớn. `FixedSizeChunker` là lựa chọn an toàn nhất khi chưa biết cấu trúc dữ liệu.
2. *Filter giảm nhiễu ở đâu?* — Chỉ khi bảng xếp hạng chưa lọc thật sự chứa chunk sai đối tượng. Trong tập hiện tại query quá đặc hiệu nên filter không đổi kết quả; nhóm nêu rõ đây là hạn chế của bộ query chứ không phải kết luận về filter.
3. *Đánh đổi recall thế nào?* — Lọc quá tay nguy hiểm hơn không lọc: áp `audience=student` cho câu hỏi cao học sẽ loại mất tài liệu `faculty` chứa đáp án.

## 6. Checklist Checkpoint 7

- [x] `python -m pytest tests -v` pass toàn bộ **42 test**
- [x] `src/` giữ nguyên public interface của starter code, không còn `NotImplementedError`
- [x] Corpus 5 tài liệu công khai, metadata đủ `source_url`, `retrieved_at`, `document_version`, không chứa dữ liệu cá nhân
- [x] `sources.csv` khớp một–một với corpus
- [x] Đúng 5 query kèm gold answer, query 2 dùng field filter bắt buộc của lớp K3 (`audience`)
- [x] Có thành viên chunk theo heading/section (Nguyễn Quang Vinh — `HeadingChunker`)
- [x] Hai report điền đủ, có output thật từ `bench.py` và **ba** failure case có bằng chứng từ top-k
- [x] Các thành viên chung corpus và query, nhưng strategy, kết quả và phản ánh không trùng nhau
- [x] Không commit `.env`, API key, `.venv/` hay database local
- [ ] Đã nộp link repo vào vlearn *(mỗi thành viên tự nộp repo cá nhân)*

**Báo cáo cá nhân của từng thành viên** nằm ở `report/REPORT_CANHAN.md` trên nhánh riêng của mỗi người (`Trung_01725`, `Nguyễn_Tuấn_Nam_2A202602039`, `Vinh`, `Đinh-Quang-Minh-2A202601347`).

## 7. Tự đánh giá phần nhóm

| Tiêu chí | Tự đánh giá |
|---|---:|
| Lựa chọn tài liệu và provenance | 8 / 10 |
| Thiết kế, so sánh chiến lược | 14 / 15 |
| Chất lượng truy xuất và failure analysis | 8 / 10 |
| Demo / khả năng tái tạo | 5 / 5 |
| **Tổng** | **35 / 40** |

> Tự trừ điểm ở **Lựa chọn tài liệu** vì `qyd474_2022_qnu` crawl thiếu bảng gốc và `tb209_2024_qnu` còn marker giao diện — đây cũng chính là nguyên nhân trực tiếp của failure case số 1. Trừ ở **Chất lượng truy xuất** vì không strategy nào vượt 6/10 và bộ query chưa đủ khó để chứng minh giá trị của metadata filter.
