# Benchmark thô - Lab 07 (Quy định QNU)

> File sinh tự động bởi `python bench.py`; không sửa số liệu bằng tay.

- Backend embedding: **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**
- Corpus: `data/qnu_regulations` (5 tài liệu)
- Chấm ở mức chunk: đúng `doc_id` **và** chứa chuỗi bằng chứng đặc trưng.
- Agent benchmark là agent trích xuất xác định: chỉ dùng chunk hạng 1, không được cung cấp gold answer.

## 1. Tổng hợp strategy

| Strategy | Số chunk | Điểm /10 | Query có bằng chứng trong top-3 | Agent đúng từ top-1 |
|---|---:|---:|---:|---:|
| `sentence(3)` | 18 | **6/10** | 4/5 | 2/5 |
| `recursive(400)` | 36 | **4/10** | 3/5 | 1/5 |
| `heading(600)` | 22 | **5/10** | 3/5 | 2/5 |
| `fixed(800/150)` | 17 | **5/10** | 3/5 | 3/5 |

## 2. Top-3, chunk coherence và grounding

### Strategy `sentence(3)`

#### Q1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 bao lâu, từ ngày nào và học lại khi nào?

Gold answer: Nghỉ 03 tuần từ 09/02/2026 đến hết 01/03/2026 và học lại từ 02/03/2026.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien::chunk_0` | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | `all` | 0.7437 | CÓ | CÓ | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sin… |
| 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6138 | không | không | Đối với ngành Toán giải tích, thực hiện chương trình đào tạo Học kỳ 3 (Đợt 3) cùng với ngành Toán giải tích khóa 28A (8/2025-2027). Thời gian học tập… |
| 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_2` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.5509 | không | không | Thời gian nộp, mức thu học phí Học kỳ 2 (Đợt 2): - Thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026. - Mức thu học phí: thực hiện theo… |

- Precision: chunk chứa bằng chứng ở hạng **1**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **1**.
- Agent answer: Trích xuất từ chunk hạng 1: # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên {1} ##LOC[OK]## {1} ##LOC[OK]## ##LOC[Cancel]## {1} ##LOC[OK]## ##LOC[Cancel]## 02 Th02 TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên 15:54:11 \| Số 209/TB-ĐHQN Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên Ngày phát hành: Gia Lai, ngày 02 tháng 02 năm 2026 Căn…
- Grounding/điểm: agent đủ bằng chứng; **2/2**.

#### Q2. Quy chế tuyển sinh đại học ban hành kèm QĐ1401 có hiệu lực khi nào và thay thế quyết định nào?; filter `{'audience': 'student'}`

Gold answer: Có hiệu lực từ ngày ký và thay thế Quyết định 1455/QĐ-ĐHQN ngày 21/5/2025.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.7936 | không | không | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Số: 1401/QĐ - ĐHQN Ban hành Quy chế tuyển sinh trình độ đại học Ngày phát hành: Gia Lai, Ngày… |
| 2 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.7920 | CÓ | CÓ | Điều 2. Quyết định này có hiệu lực kể từ ngày ký và thay thế Quyết định số 1455/QĐ-ĐHQN ngày 21/5/2025 về ban hành Quy chế tuyển sinh đại học của Hiệ… |
| 3 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.6771 | không | không | Trưởng Phòng Đào tạo, các Trưởng đơn vị, viên chức, người lao động của Trường Đại học Quy Nhơn; các đơn vị, tổ chức và cá nhân liên quan chịu trách n… |

- Precision: chunk chứa bằng chứng ở hạng **2**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **2**.
- Agent answer: Trích xuất từ chunk hạng 1: # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Số: 1401/QĐ - ĐHQN Ban hành Quy chế tuyển sinh trình độ đại học Ngày phát hành: Gia Lai, Ngày 18/5/2026 HIỆU TRƯỞNG TRƯỜNG ĐẠI HỌC QUY NHƠN Căn cứ Quyết định số 1842/QĐ ngày 21 tháng 12 năm 1977 của Bộ trưởng Bộ Giáo dục về thành lập cơ sở Đại học Sư phạm Quy Nhơn; Quyết định 02/HĐBT ngày 13 tháng 7 năm 1981 về thành lập Trường Đại học Sư phạm Quy Nhơn; Quyết định số 221/2003/QĐ-TTg ngày 30 tháng 10 năm 2003 của…
- Grounding/điểm: agent thiếu bằng chứng; **1/2**.

#### Q3. Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào?

Gold answer: Áp dụng cho đào tạo đại học từ xa tuyển sinh tháng 2/2026 đợt 1 và có hiệu lực từ ngày ký.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.7749 | không | không | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |
| 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_5` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6983 | không | không | Mọi thắc mắc về học phí liên hệ SĐT: (0256)3 546 882 (Phòng Kế hoạch-Tàchính) trong giờ hành chính. Nhà trường đề nghị học viên cao học khóa 28B thực… |
| 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_2` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6907 | không | không | Thời gian nộp, mức thu học phí Học kỳ 2 (Đợt 2): - Thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026. - Mức thu học phí: thực hiện theo… |

- Precision: chunk chứa bằng chứng ở hạng **không có**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **không có**.
- Agent answer: Trích xuất từ chunk hạng 1: # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển sinh năm 2024 Số: 828/QyĐ-ĐHQN Quy định về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024 Ngày phát hành: Bình Định, ngày 19 tháng 03 năm 2025 Căn cứ quy định về quyền hạn, trách nhiệm của Hiệu trưởng theo Quy chể tổ c…
- Grounding/điểm: agent thiếu bằng chứng; **0/2**.

#### Q4. Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào?

Gold answer: Nộp từ 15/5/2026 đến hết 02/8/2026, qua cổng https://e-bills.vn/pay/qnu hoặc QR Code.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_5` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6800 | không | không | Mọi thắc mắc về học phí liên hệ SĐT: (0256)3 546 882 (Phòng Kế hoạch-Tàchính) trong giờ hành chính. Nhà trường đề nghị học viên cao học khóa 28B thực… |
| 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_0` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6102 | không | không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học Khóa 28B (12/2025-2027) Số: 1525/TB-ĐHQN Về thời gian học tậ… |
| 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_2` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.5943 | CÓ | CÓ | Thời gian nộp, mức thu học phí Học kỳ 2 (Đợt 2): - Thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026. - Mức thu học phí: thực hiện theo… |

- Precision: chunk chứa bằng chứng ở hạng **3**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **3**.
- Agent answer: Trích xuất từ chunk hạng 1: Mọi thắc mắc về học phí liên hệ SĐT: (0256)3 546 882 (Phòng Kế hoạch-Tàchính) trong giờ hành chính. Nhà trường đề nghị học viên cao học khóa 28B thực hiện đúng thời gian học, thi kết thúc học phần và nộp học phí theo đúng các mốc thời gian được quy định trong Thông báo này. Học viên không nộp học phí đúng thời gian quy định sẽ không có tên trong danh sách dự thi kết thúc học phần và không được đăng ký học phần ở học kỳ tiếp theo của khoá học.
- Grounding/điểm: agent thiếu bằng chứng; **1/2**.

#### Q5. QyĐ828 về học phí năm học 2024-2025 áp dụng cho hệ đào tạo, khóa và ngành nào?

Gold answer: Áp dụng cho hệ vừa làm vừa học khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.8118 | CÓ | CÓ | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |
| 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_2` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.7327 | không | không | Thời gian nộp, mức thu học phí Học kỳ 2 (Đợt 2): - Thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026. - Mức thu học phí: thực hiện theo… |
| 3 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_0` | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | `student` | 0.6997 | không | không | # QyĐ474 - Về mức thu học phí đào tạo đại học từ xa tuyền sinh tháng 2 năm 2026 (Đợt 1) Số: 474/QyĐ-ĐHQN Về mức thu học phí đào tạo đại học từ xa tuy… |

- Precision: chunk chứa bằng chứng ở hạng **1**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **1**.
- Agent answer: Trích xuất từ chunk hạng 1: # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển sinh năm 2024 Số: 828/QyĐ-ĐHQN Quy định về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024 Ngày phát hành: Bình Định, ngày 19 tháng 03 năm 2025 Căn cứ quy định về quyền hạn, trách nhiệm của Hiệu trưởng theo Quy chể tổ c…
- Grounding/điểm: agent đủ bằng chứng; **2/2**.

### Strategy `recursive(400)`

#### Q1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 bao lâu, từ ngày nào và học lại khi nào?

Gold answer: Nghỉ 03 tuần từ 09/02/2026 đến hết 01/03/2026 và học lại từ 02/03/2026.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien::chunk_2` | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | `all` | 0.8939 | CÓ | CÓ | 1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 là 03 tuần, từ ngày 09 tháng 02 năm 2026 đến hết ngày 01 tháng 03 năm 2026. Từ ngày 02 tháng 3 năm… |
| 2 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien::chunk_1` | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | `all` | 0.8525 | không | không | Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên Ngày phát hành: Gia Lai, ngày 02 tháng 02 năm 2026 Căn cứ Kế hoạch đào tạo đại h… |
| 3 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien::chunk_0` | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | `all` | 0.7437 | không | không | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sin… |

- Precision: chunk chứa bằng chứng ở hạng **1**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **1**.
- Agent answer: Trích xuất từ chunk hạng 1: 1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 là 03 tuần, từ ngày 09 tháng 02 năm 2026 đến hết ngày 01 tháng 03 năm 2026. Từ ngày 02 tháng 3 năm 2026 sinh viên tiếp tục học tập, thực tập sư phạm 2, thực tập tốt nghiệp theo Kế hoạch đào tạo đại học hệ chính quy năm học 2025-2026.
- Grounding/điểm: agent đủ bằng chứng; **2/2**.

#### Q2. Quy chế tuyển sinh đại học ban hành kèm QĐ1401 có hiệu lực khi nào và thay thế quyết định nào?; filter `{'audience': 'student'}`

Gold answer: Có hiệu lực từ ngày ký và thay thế Quyết định 1455/QĐ-ĐHQN ngày 21/5/2025.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.8062 | không | không | Căn cứ Luật Giáo dục đại học số 125/2025/QH15; Căn cứ Thông tư số 06/2026/TT-BGDĐT ngày 15/02/2026 ban hành Quy chế tuyển sinh các ngành đào tạo trìn… |
| 2 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_3` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.7847 | CÓ | CÓ | Điều 2. Quyết định này có hiệu lực kể từ ngày ký và thay thế Quyết định số 1455/QĐ-ĐHQN ngày 21/5/2025 về ban hành Quy chế tuyển sinh đại học của Hiệ… |
| 3 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_4` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.7765 | không | không | Quy chế tuyển sinh trình độ đại học |

- Precision: chunk chứa bằng chứng ở hạng **2**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **2**.
- Agent answer: Trích xuất từ chunk hạng 1: Căn cứ Luật Giáo dục đại học số 125/2025/QH15; Căn cứ Thông tư số 06/2026/TT-BGDĐT ngày 15/02/2026 ban hành Quy chế tuyển sinh các ngành đào tạo trình độ đại học và ngành Giáo dục Mầm non trình độ cao đẳng; Theo đề nghị của Trưởng Phòng Đào tạo. QUYẾT ĐỊNH: Điều 1. Ban hành kèm theo Quyết định này Quy chế tuyển sinh trình độ đại học của Trường Đại học Quy Nhơn.
- Grounding/điểm: agent thiếu bằng chứng; **1/2**.

#### Q3. Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào?

Gold answer: Áp dụng cho đào tạo đại học từ xa tuyển sinh tháng 2/2026 đợt 1 và có hiệu lực từ ngày ký.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.7928 | không | không | Căn cứ Kế hoạch đào tạo trình độ thạc sĩ khoá 28B (12/2025-2027) được ban hành kèm theo Quyết định số 2363/QĐ-ĐHQN ngày 21/8/2025 của Hiệu trưởng; Ch… |
| 2 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.7765 | không | không | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |
| 3 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_3` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.7449 | không | không | Hiệu trưởng Trường Đại học Quy Nhơn quy định mức thu học phí năm học 2024-2025 áp dụng cho hệ đào tạo vừa làm vừa học khóa 34 tô chức tại Trường như … |

- Precision: chunk chứa bằng chứng ở hạng **không có**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **không có**.
- Agent answer: Trích xuất từ chunk hạng 1: Căn cứ Kế hoạch đào tạo trình độ thạc sĩ khoá 28B (12/2025-2027) được ban hành kèm theo Quyết định số 2363/QĐ-ĐHQN ngày 21/8/2025 của Hiệu trưởng; Chương trình đào tạo trình độ thạc sĩ của khóa 28B; Quy định số 2114/QyĐ-ĐHQN ngày 25/7/2025 của Hiệu trưởng về mức thu học phí năm học 2025-2026 đối với đào tạo trình độ thạc sĩ và mức thu học phí tạm tính từ năm học 2025-2026 đối với đào tạo trình độ
- Grounding/điểm: agent thiếu bằng chứng; **0/2**.

#### Q4. Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào?

Gold answer: Nộp từ 15/5/2026 đến hết 02/8/2026, qua cổng https://e-bills.vn/pay/qnu hoặc QR Code.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_11` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6504 | không | không | Nhà trường đề nghị học viên cao học khóa 28B thực hiện đúng thời gian học, thi kết thúc học phần và nộp học phí theo đúng các mốc thời gian được quy … |
| 2 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_3` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.6150 | không | không | Hiệu trưởng Trường Đại học Quy Nhơn quy định mức thu học phí năm học 2024-2025 áp dụng cho hệ đào tạo vừa làm vừa học khóa 34 tô chức tại Trường như … |
| 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_2` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6015 | không | không | tiến sĩ khoá 14 tuyển sinh trong năm 2025, Nhà trường thông báo thời gian học tập Học kỳ 2 (Đợt 2) của khoá 28A, cụ thể như sau: |

- Precision: chunk chứa bằng chứng ở hạng **không có**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **không có**.
- Agent answer: Trích xuất từ chunk hạng 1: Nhà trường đề nghị học viên cao học khóa 28B thực hiện đúng thời gian học, thi kết thúc học phần và nộp học phí theo đúng các mốc thời gian được quy định trong Thông báo này. Học viên không nộp học phí đúng thời gian quy định sẽ không có tên trong danh sách dự thi kết thúc học phần và không được đăng ký học phần ở học kỳ tiếp theo của khoá học.
- Grounding/điểm: agent thiếu bằng chứng; **0/2**.

#### Q5. QyĐ828 về học phí năm học 2024-2025 áp dụng cho hệ đào tạo, khóa và ngành nào?

Gold answer: Áp dụng cho hệ vừa làm vừa học khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.8125 | không | không | Căn cứ Kế hoạch đào tạo trình độ thạc sĩ khoá 28B (12/2025-2027) được ban hành kèm theo Quyết định số 2363/QĐ-ĐHQN ngày 21/8/2025 của Hiệu trưởng; Ch… |
| 2 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.8104 | không | CÓ | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |
| 3 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_3` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.7664 | CÓ | không | Hiệu trưởng Trường Đại học Quy Nhơn quy định mức thu học phí năm học 2024-2025 áp dụng cho hệ đào tạo vừa làm vừa học khóa 34 tô chức tại Trường như … |

- Precision: chunk chứa bằng chứng ở hạng **3**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **2**.
- Agent answer: Trích xuất từ chunk hạng 1: Căn cứ Kế hoạch đào tạo trình độ thạc sĩ khoá 28B (12/2025-2027) được ban hành kèm theo Quyết định số 2363/QĐ-ĐHQN ngày 21/8/2025 của Hiệu trưởng; Chương trình đào tạo trình độ thạc sĩ của khóa 28B; Quy định số 2114/QyĐ-ĐHQN ngày 25/7/2025 của Hiệu trưởng về mức thu học phí năm học 2025-2026 đối với đào tạo trình độ thạc sĩ và mức thu học phí tạm tính từ năm học 2025-2026 đối với đào tạo trình độ
- Grounding/điểm: agent thiếu bằng chứng; **1/2**.

### Strategy `heading(600)`

#### Q1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 bao lâu, từ ngày nào và học lại khi nào?

Gold answer: Nghỉ 03 tuần từ 09/02/2026 đến hết 01/03/2026 và học lại từ 02/03/2026.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien::chunk_1` | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | `all` | 0.8553 | CÓ | CÓ | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên Căn cứ Kế hoạch đào tạo đại học hệ chính quy năm học 2025-2026 ban hàn… |
| 2 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien::chunk_4` | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | `all` | 0.7783 | không | không | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên https://eoffice.qnu.edu.vn/app/view-document?xuLyId=adde2cb5-8538-4ad7… |
| 3 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien::chunk_0` | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | `all` | 0.7437 | không | không | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sin… |

- Precision: chunk chứa bằng chứng ở hạng **1**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **1**.
- Agent answer: Trích xuất từ chunk hạng 1: # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên Căn cứ Kế hoạch đào tạo đại học hệ chính quy năm học 2025-2026 ban hành kèm theo Quyết định số 1817/QĐ-ĐHQN, ngày 25 tháng 6 năm 2025 của Hiệu trưởng Trường Đại học Quy Nhơn, Nhà trường thông báo thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên như sau: 1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 là 03 tuần, từ ngày 09 tháng 02 năm 2026 đến hết ngày 01 tháng 03 năm …
- Grounding/điểm: agent đủ bằng chứng; **2/2**.

#### Q2. Quy chế tuyển sinh đại học ban hành kèm QĐ1401 có hiệu lực khi nào và thay thế quyết định nào?; filter `{'audience': 'student'}`

Gold answer: Có hiệu lực từ ngày ký và thay thế Quyết định 1455/QĐ-ĐHQN ngày 21/5/2025.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.8169 | CÓ | CÓ | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Căn cứ Luật Giáo dục đại học số 125/2025/QH15; Căn cứ Thông tư số 06/2026/TT-BGDĐT ngày 15/02… |
| 2 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.7936 | không | không | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Số: 1401/QĐ - ĐHQN Ban hành Quy chế tuyển sinh trình độ đại học Ngày phát hành: Gia Lai, Ngày… |
| 3 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.7768 | không | không | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Điều 3. Trưởng Phòng Đào tạo, các Trưởng đơn vị, viên chức, người lao động của Trường Đại học… |

- Precision: chunk chứa bằng chứng ở hạng **1**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **1**.
- Agent answer: Trích xuất từ chunk hạng 1: # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Căn cứ Luật Giáo dục đại học số 125/2025/QH15; Căn cứ Thông tư số 06/2026/TT-BGDĐT ngày 15/02/2026 ban hành Quy chế tuyển sinh các ngành đào tạo trình độ đại học và ngành Giáo dục Mầm non trình độ cao đẳng; Theo đề nghị của Trưởng Phòng Đào tạo. QUYẾT ĐỊNH: Điều 1. Ban hành kèm theo Quyết định này Quy chế tuyển sinh trình độ đại học của Trường Đại học Quy Nhơn. Điều 2. Quyết định này có hiệu lực kể từ ngày ký và…
- Grounding/điểm: agent đủ bằng chứng; **2/2**.

#### Q3. Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào?

Gold answer: Áp dụng cho đào tạo đại học từ xa tuyển sinh tháng 2/2026 đợt 1 và có hiệu lực từ ngày ký.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_1` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.7855 | không | không | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |
| 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.7758 | không | không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học Khóa 28B (12/2025-2027) Căn cứ Kế hoạch đào tạo trình độ thạ… |
| 3 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.7718 | không | không | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |

- Precision: chunk chứa bằng chứng ở hạng **không có**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **không có**.
- Agent answer: Trích xuất từ chunk hạng 1: # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển sinh năm 2024 Căn cứ quy định về quyền hạn, trách nhiệm của Hiệu trưởng theo Quy chể tổ chức và hoạt động của Trường Đại học Quy Nhơn ban hành tại Nghị quyết số 11/NQ-HĐT ngày 29/3/2024 của Hội đồng trường Trường Đại học Quy Nhơn; Căn cứ Nghị định số 97/2023/NĐ-CP ngày 31/12/2023 của Thủ tướng Chính phủ sửa đổi, bổ sung…
- Grounding/điểm: agent thiếu bằng chứng; **0/2**.

#### Q4. Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào?

Gold answer: Nộp từ 15/5/2026 đến hết 02/8/2026, qua cổng https://e-bills.vn/pay/qnu hoặc QR Code.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_6` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6756 | không | không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học Khóa 28B (12/2025-2027) Nhà trường đề nghị học viên cao học … |
| 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_4` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6506 | không | không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học Khóa 28B (12/2025-2027) - Mức thu học phí: thực hiện theo Qu… |
| 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6466 | không | không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học Khóa 28B (12/2025-2027) Căn cứ Kế hoạch đào tạo trình độ thạ… |

- Precision: chunk chứa bằng chứng ở hạng **không có**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **không có**.
- Agent answer: Trích xuất từ chunk hạng 1: # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học Khóa 28B (12/2025-2027) Nhà trường đề nghị học viên cao học khóa 28B thực hiện đúng thời gian học, thi kết thúc học phần và nộp học phí theo đúng các mốc thời gian được quy định trong Thông báo này. Học viên không nộp học phí đúng thời gian quy định sẽ không có tên trong danh sách dự thi kết thúc học phần và không được đăng ký học phần ở học kỳ tiếp theo của khoá học. Trường Đại …
- Grounding/điểm: agent thiếu bằng chứng; **0/2**.

#### Q5. QyĐ828 về học phí năm học 2024-2025 áp dụng cho hệ đào tạo, khóa và ngành nào?

Gold answer: Áp dụng cho hệ vừa làm vừa học khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_1` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.8477 | không | không | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |
| 2 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_2` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.8303 | CÓ | không | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |
| 3 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.8083 | không | CÓ | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |

- Precision: chunk chứa bằng chứng ở hạng **2**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **3**.
- Agent answer: Trích xuất từ chunk hạng 1: # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển sinh năm 2024 Căn cứ quy định về quyền hạn, trách nhiệm của Hiệu trưởng theo Quy chể tổ chức và hoạt động của Trường Đại học Quy Nhơn ban hành tại Nghị quyết số 11/NQ-HĐT ngày 29/3/2024 của Hội đồng trường Trường Đại học Quy Nhơn; Căn cứ Nghị định số 97/2023/NĐ-CP ngày 31/12/2023 của Thủ tướng Chính phủ sửa đổi, bổ sung…
- Grounding/điểm: agent thiếu bằng chứng; **1/2**.

### Strategy `fixed(800/150)`

#### Q1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 bao lâu, từ ngày nào và học lại khi nào?

Gold answer: Nghỉ 03 tuần từ 09/02/2026 đến hết 01/03/2026 và học lại từ 02/03/2026.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien::chunk_1` | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | `all` | 0.9038 | CÓ | CÓ | ọc Quy Nhơn, Nhà trường thông báo thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên như sau: 1. Sinh viên nghỉ Tết Nguyên đán Bính Ng… |
| 2 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien::chunk_0` | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | `all` | 0.7437 | không | không | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sin… |
| 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_2` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6109 | không | không | ngành Toán giải tích, thực hiện chương trình đào tạo Học kỳ 3 (Đợt 3) cùng với ngành Toán giải tích khóa 28A (8/2025-2027). Thời gian học tập Học kỳ … |

- Precision: chunk chứa bằng chứng ở hạng **1**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **1**.
- Agent answer: Trích xuất từ chunk hạng 1: ọc Quy Nhơn, Nhà trường thông báo thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên như sau: 1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 là 03 tuần, từ ngày 09 tháng 02 năm 2026 đến hết ngày 01 tháng 03 năm 2026. Từ ngày 02 tháng 3 năm 2026 sinh viên tiếp tục học tập, thực tập sư phạm 2, thực tập tốt nghiệp theo Kế hoạch đào tạo đại học hệ chính quy năm học 2025-2026. 2. Trong thời gian nghỉ Tết Nguyên đán, Nhà trường yêu cầu sinh viên chấp hàn…
- Grounding/điểm: agent đủ bằng chứng; **2/2**.

#### Q2. Quy chế tuyển sinh đại học ban hành kèm QĐ1401 có hiệu lực khi nào và thay thế quyết định nào?; filter `{'audience': 'student'}`

Gold answer: Có hiệu lực từ ngày ký và thay thế Quyết định 1455/QĐ-ĐHQN ngày 21/5/2025.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.8515 | CÓ | CÓ | tư số 06/2026/TT-BGDĐT ngày 15/02/2026 ban hành Quy chế tuyển sinh các ngành đào tạo trình độ đại học và ngành Giáo dục Mầm non trình độ cao đẳng; Th… |
| 2 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.7936 | không | không | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Số: 1401/QĐ - ĐHQN Ban hành Quy chế tuyển sinh trình độ đại học Ngày phát hành: Gia Lai, Ngày… |
| 3 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_1` | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | `student` | 0.6847 | không | không | Hội đồng Trường Trường Đại học Quy Nhơn; Căn cứ Nghị quyết số 63/NQ-HĐT ngày 20/12/2024 của Hội đồng trường Trường Đại học Quy Nhơn về việc ban hành … |

- Precision: chunk chứa bằng chứng ở hạng **1**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **1**.
- Agent answer: Trích xuất từ chunk hạng 1: tư số 06/2026/TT-BGDĐT ngày 15/02/2026 ban hành Quy chế tuyển sinh các ngành đào tạo trình độ đại học và ngành Giáo dục Mầm non trình độ cao đẳng; Theo đề nghị của Trưởng Phòng Đào tạo. QUYẾT ĐỊNH: Điều 1. Ban hành kèm theo Quyết định này Quy chế tuyển sinh trình độ đại học của Trường Đại học Quy Nhơn. Điều 2. Quyết định này có hiệu lực kể từ ngày ký và thay thế Quyết định số 1455/QĐ-ĐHQN ngày 21/5/2025 về ban hành Quy chế tuyển sinh đại học của Hiệu trưởng Trường Đạ…
- Grounding/điểm: agent đủ bằng chứng; **2/2**.

#### Q3. Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào?

Gold answer: Áp dụng cho đào tạo đại học từ xa tuyển sinh tháng 2/2026 đợt 1 và có hiệu lực từ ngày ký.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.7749 | không | không | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |
| 2 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1` | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | `student` | 0.7069 | không | không | tư số 06/2026/TT-BGDĐT ngày 15/02/2026 ban hành Quy chế tuyển sinh các ngành đào tạo trình độ đại học và ngành Giáo dục Mầm non trình độ cao đẳng; Th… |
| 3 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_1` | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | `student` | 0.6741 | CÓ | CÓ | Hội đồng Trường Trường Đại học Quy Nhơn; Căn cứ Nghị quyết số 63/NQ-HĐT ngày 20/12/2024 của Hội đồng trường Trường Đại học Quy Nhơn về việc ban hành … |

- Precision: chunk chứa bằng chứng ở hạng **3**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **3**.
- Agent answer: Trích xuất từ chunk hạng 1: # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển sinh năm 2024 Số: 828/QyĐ-ĐHQN Quy định về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024 Ngày phát hành: Bình Định, ngày 19 tháng 03 năm 2025 Căn cứ quy định về quyền hạn, trách nhiệm của Hiệu trưởng theo Quy chể tổ c…
- Grounding/điểm: agent thiếu bằng chứng; **1/2**.

#### Q4. Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào?

Gold answer: Nộp từ 15/5/2026 đến hết 02/8/2026, qua cổng https://e-bills.vn/pay/qnu hoặc QR Code.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_4` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6157 | không | không | n hành thanh toán. Lưu ý: Sau khi nộp tiền thành công hệ thống sẽ gạch nợ khoảng 2-3 phút; Hóa đơn điện tử sẽ được gửi về e-mail của học viên trong t… |
| 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_0` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.6102 | không | không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học Khóa 28B (12/2025-2027) Số: 1525/TB-ĐHQN Về thời gian học tậ… |
| 3 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_1` | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | `student` | 0.5908 | không | không | Hội đồng Trường Trường Đại học Quy Nhơn; Căn cứ Nghị quyết số 63/NQ-HĐT ngày 20/12/2024 của Hội đồng trường Trường Đại học Quy Nhơn về việc ban hành … |

- Precision: chunk chứa bằng chứng ở hạng **không có**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **không có**.
- Agent answer: Trích xuất từ chunk hạng 1: n hành thanh toán. Lưu ý: Sau khi nộp tiền thành công hệ thống sẽ gạch nợ khoảng 2-3 phút; Hóa đơn điện tử sẽ được gửi về e-mail của học viên trong tuần. Mọi thắc mắc về học phí liên hệ SĐT: (0256)3 546 882 (Phòng Kế hoạch-Tàchính) trong giờ hành chính. Nhà trường đề nghị học viên cao học khóa 28B thực hiện đúng thời gian học, thi kết thúc học phần và nộp học phí theo đúng các mốc thời gian được quy định trong Thông báo này. Học viên không nộp học phí đúng thời gian …
- Grounding/điểm: agent thiếu bằng chứng; **0/2**.

#### Q5. QyĐ828 về học phí năm học 2024-2025 áp dụng cho hệ đào tạo, khóa và ngành nào?

Gold answer: Áp dụng cho hệ vừa làm vừa học khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024.

| Hạng | chunk_id | doc_id | audience | score | Chứa bằng chứng? | Đủ đáp án trong cùng chunk? | Preview |
|---:|---|---|---|---:|---|---|---|
| 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0` | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | `staff` | 0.8118 | không | CÓ | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển… |
| 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1` | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | `faculty` | 0.7427 | không | không | học 2025-2026 đối với đào tạo trình độ tiến sĩ khoá 14 tuyển sinh trong năm 2025, Nhà trường thông báo thời gian học tập Học kỳ 2 (Đợt 2) của khoá 28… |
| 3 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_1` | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | `student` | 0.7263 | không | không | Hội đồng Trường Trường Đại học Quy Nhơn; Căn cứ Nghị quyết số 63/NQ-HĐT ngày 20/12/2024 của Hội đồng trường Trường Đại học Quy Nhơn về việc ban hành … |

- Precision: chunk chứa bằng chứng ở hạng **không có**.
- Chunk coherence: chunk chứa đủ các phần đáp án ở hạng **1**.
- Agent answer: Trích xuất từ chunk hạng 1: # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đát đai tuyển sinh năm 2024 Số: 828/QyĐ-ĐHQN Quy định về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức tại Trường áp dụng cho khóa 34 ngành Quản lý đất đai tuyển sinh năm 2024 Ngày phát hành: Bình Định, ngày 19 tháng 03 năm 2025 Căn cứ quy định về quyền hạn, trách nhiệm của Hiệu trưởng theo Quy chể tổ c…
- Grounding/điểm: agent đủ bằng chứng; **0/2**.

## 3. A/B metadata filter trên mọi strategy

Query: **Quy chế tuyển sinh đại học ban hành kèm QĐ1401 có hiệu lực khi nào và thay thế quyết định nào?**

| Strategy | Không filter: top-3 | Có filter: top-3 | Kết quả đổi? | Điểm không/có filter | Metadata utility |
|---|---|---|---|---:|---|
| `sentence(3)` | quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0 (0.794), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1 (0.792), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2 (0.677) | quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0 (0.794), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1 (0.792), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2 (0.677) | Không | 1/1 | Query/corpus không thực sự cần filter |
| `recursive(400)` | quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2 (0.806), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_3 (0.785), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_4 (0.777) | quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2 (0.806), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_3 (0.785), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_4 (0.777) | Không | 1/1 | Query/corpus không thực sự cần filter |
| `heading(600)` | quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1 (0.817), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0 (0.794), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2 (0.777) | quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1 (0.817), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0 (0.794), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2 (0.777) | Không | 2/2 | Query/corpus không thực sự cần filter |
| `fixed(800/150)` | quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1 (0.851), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0 (0.794), quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_1 (0.685) | quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1 (0.851), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0 (0.794), quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_1 (0.685) | Không | 2/2 | Query/corpus không thực sự cần filter |

## 4. Failure candidates có bằng chứng top-k

### `sentence(3)` - Q2 (1/2)

- Query: Quy chế tuyển sinh đại học ban hành kèm QĐ1401 có hiệu lực khi nào và thay thế quyết định nào?
- Top-3: quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_0 (0.794), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1 (0.792), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2 (0.677)
- Bằng chứng: chuỗi `quyết định này có hiệu lực kể từ ngày ký` ở hạng 2.
- Dấu hiệu: chunk đáp án không ở top-1 nên agent trích xuất sai/thiếu.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `sentence(3)` - Q3 (0/2)

- Query: Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào?
- Top-3: quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0 (0.775), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_5 (0.698), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_2 (0.691)
- Bằng chứng: chuỗi `đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026` ở hạng không xuất hiện.
- Dấu hiệu: đúng tài liệu nhưng sai/thiếu section.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `sentence(3)` - Q4 (1/2)

- Query: Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào?
- Top-3: quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_5 (0.680), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_0 (0.610), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_2 (0.594)
- Bằng chứng: chuỗi `thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026` ở hạng 3.
- Dấu hiệu: chunk đáp án không ở top-1 nên agent trích xuất sai/thiếu.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `recursive(400)` - Q2 (1/2)

- Query: Quy chế tuyển sinh đại học ban hành kèm QĐ1401 có hiệu lực khi nào và thay thế quyết định nào?
- Top-3: quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_2 (0.806), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_3 (0.785), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_4 (0.777)
- Bằng chứng: chuỗi `quyết định này có hiệu lực kể từ ngày ký` ở hạng 2.
- Dấu hiệu: chunk đáp án không ở top-1 nên agent trích xuất sai/thiếu.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `recursive(400)` - Q3 (0/2)

- Query: Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào?
- Top-3: quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1 (0.793), quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0 (0.777), quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_3 (0.745)
- Bằng chứng: chuỗi `đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026` ở hạng không xuất hiện.
- Dấu hiệu: đúng tài liệu nhưng sai/thiếu section.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `recursive(400)` - Q4 (0/2)

- Query: Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào?
- Top-3: quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_11 (0.650), quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_3 (0.615), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_2 (0.602)
- Bằng chứng: chuỗi `thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026` ở hạng không xuất hiện.
- Dấu hiệu: đúng tài liệu nhưng sai/thiếu section.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `recursive(400)` - Q5 (1/2)

- Query: QyĐ828 về học phí năm học 2024-2025 áp dụng cho hệ đào tạo, khóa và ngành nào?
- Top-3: quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1 (0.813), quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0 (0.810), quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_3 (0.766)
- Bằng chứng: chuỗi `mức thu học phí năm học 2024-2025 áp dụng cho hệ đào tạo vừa làm vừa học khóa 34` ở hạng 3.
- Dấu hiệu: chunk đáp án không ở top-1 nên agent trích xuất sai/thiếu.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `heading(600)` - Q3 (0/2)

- Query: Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào?
- Top-3: quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_1 (0.786), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1 (0.776), quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0 (0.772)
- Bằng chứng: chuỗi `đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026` ở hạng không xuất hiện.
- Dấu hiệu: đúng tài liệu nhưng sai/thiếu section.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `heading(600)` - Q4 (0/2)

- Query: Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào?
- Top-3: quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_6 (0.676), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_4 (0.651), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1 (0.647)
- Bằng chứng: chuỗi `thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026` ở hạng không xuất hiện.
- Dấu hiệu: đúng tài liệu nhưng sai/thiếu section.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `heading(600)` - Q5 (1/2)

- Query: QyĐ828 về học phí năm học 2024-2025 áp dụng cho hệ đào tạo, khóa và ngành nào?
- Top-3: quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_1 (0.848), quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_2 (0.830), quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0 (0.808)
- Bằng chứng: chuỗi `mức thu học phí năm học 2024-2025 áp dụng cho hệ đào tạo vừa làm vừa học khóa 34` ở hạng 2.
- Dấu hiệu: chunk đáp án không ở top-1 nên agent trích xuất sai/thiếu.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `fixed(800/150)` - Q3 (1/2)

- Query: Quy định học phí QyĐ474 áp dụng cho hệ đào tạo và đợt tuyển sinh nào, có hiệu lực khi nào?
- Top-3: quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0 (0.775), quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc::chunk_1 (0.707), quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_1 (0.674)
- Bằng chứng: chuỗi `đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026` ở hạng 3.
- Dấu hiệu: chunk đáp án không ở top-1 nên agent trích xuất sai/thiếu.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `fixed(800/150)` - Q4 (0/2)

- Query: Học viên cao học Khóa 28B nộp học phí trong thời gian nào và thanh toán qua cổng nào?
- Top-3: quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_4 (0.616), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_0 (0.610), quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_1 (0.591)
- Bằng chứng: chuỗi `thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026` ở hạng không xuất hiện.
- Dấu hiệu: đúng tài liệu nhưng sai/thiếu section.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.

### `fixed(800/150)` - Q5 (0/2)

- Query: QyĐ828 về học phí năm học 2024-2025 áp dụng cho hệ đào tạo, khóa và ngành nào?
- Top-3: quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024::chunk_0 (0.812), quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027::chunk_1 (0.743), quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1::chunk_1 (0.726)
- Bằng chứng: chuỗi `mức thu học phí năm học 2024-2025 áp dụng cho hệ đào tạo vừa làm vừa học khóa 34` ở hạng không xuất hiện.
- Dấu hiệu: đúng tài liệu nhưng sai/thiếu section.
- Thay đổi đề xuất: ưu tiên ranh giới section, thêm overlap khi cắt cứng, hoặc dùng metadata filter đúng ý định; sau đó chạy lại cùng query để kiểm chứng.
