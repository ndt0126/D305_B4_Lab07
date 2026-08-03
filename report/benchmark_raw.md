# Kết quả benchmark có thể tái lập — Lab 7 K3

> Sinh tự động bởi `scripts/run_benchmark.py`; không sửa tay.

- Backend: **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**
- Corpus: `data\qnu_regulations` — **5 tài liệu**
- Tổng ký tự phần body: **9513**

## A. Baseline trên 3 tài liệu đầu tiên

| Tài liệu | Ký tự | Chiến lược | count | avg | min | max |
|---|---:|---|---:|---:|---:|---:|
| `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 1379 | `fixed_size` | 3 | 493.0 | 479 | 500 |
| `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 1379 | `by_sentences` | 3 | 454.3 | 190 | 957 |
| `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 1379 | `recursive` | 4 | 342.2 | 206 | 424 |
| `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | 1340 | `fixed_size` | 3 | 480.0 | 440 | 500 |
| `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | 1340 | `by_sentences` | 2 | 665.5 | 256 | 1075 |
| `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | 1340 | `recursive` | 3 | 444.3 | 416 | 472 |
| `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 1486 | `fixed_size` | 4 | 409.0 | 136 | 500 |
| `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 1486 | `by_sentences` | 2 | 740.5 | 125 | 1356 |
| `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 1486 | `recursive` | 4 | 369.2 | 216 | 478 |

## B. Benchmark: đúng 5 câu hỏi × 4 chiến lược

### `heading(level=1..3)` — 6 chunks

| Q | Filter | Hạng | doc_id | score | Gold? | Trích đoạn |
|---:|---|---:|---|---:|---|---|
| 1 | `-` | 1 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.4893 | Có | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Số: 1401/QĐ - ĐHQN Ban hành Quy ch… |
| 1 | `-` | 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.3995 | Không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học K… |
| 1 | `-` | 3 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | 0.3240 | Không | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên **Số:** 209… |
| 1 | **Điểm/Agent** |  |  |  | **2/2** | Có hiệu lực kể từ ngày ký và thay thế Quyết định số 1455/QĐ-ĐHQN ngày 21/5/2025. |
| 2 | `-` | 1 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | 0.8007 | Có | # QyĐ474 - Về mức thu học phí đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026 (Đợt 1) Số… |
| 2 | `-` | 2 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.6562 | Không | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Số: 1401/QĐ - ĐHQN Ban hành Quy ch… |
| 2 | `-` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.6454 | Không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học K… |
| 2 | **Điểm/Agent** |  |  |  | **2/2** | Áp dụng cho tuyển sinh tháng 2 năm 2026, Đợt 1. |
| 3 | `{'program': 'part-time'}` | 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.6047 | Có | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức… |
| 3 | **Điểm/Agent** |  |  |  | **2/2** | Áp dụng cho khóa 34 ngành Quản lý đất đai, tuyển sinh năm 2024. |
| 4 | `{'program': 'graduate'}` | 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7628 | Có | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học K… |
| 4 | **Điểm/Agent** |  |  |  | **2/2** | Nộp từ ngày 15/5/2026 đến hết ngày 02/8/2026. |
| 5 | `{'audience': 'student'}` | 1 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | 0.7740 | Có | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên **Số:** 209… |
| 5 | `{'audience': 'student'}` | 2 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | 0.4562 | Không | # QyĐ474 - Về mức thu học phí đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026 (Đợt 1) Số… |
| 5 | `{'audience': 'student'}` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.4270 | Không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học K… |
| 5 | **Điểm/Agent** |  |  |  | **2/2** | Nghỉ từ ngày 09/02/2026 đến hết ngày 01/03/2026. |

**Tổng: 10/10; gold ở top-1: 5/5.**

### `recursive(600)` — 23 chunks

| Q | Filter | Hạng | doc_id | score | Gold? | Trích đoạn |
|---:|---|---:|---|---:|---|---|
| 1 | `-` | 1 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.5230 | Có | Căn cứ Luật Giáo dục đại học số 125/2025/QH15; Căn cứ Thông tư số 06/2026/TT-BGDĐT ngày 15… |
| 1 | `-` | 2 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.5055 | Không | Căn cứ quy định về quyền hạn, trách nhiệm của Hiệu trưởng theo Quy chể tổ chức và hoạt độn… |
| 1 | `-` | 3 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.4893 | Không | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Số: 1401/QĐ - ĐHQN Ban hành Quy ch… |
| 1 | **Điểm/Agent** |  |  |  | **2/2** | Có hiệu lực kể từ ngày ký và thay thế Quyết định số 1455/QĐ-ĐHQN ngày 21/5/2025. |
| 2 | `-` | 1 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | 0.8007 | Có | # QyĐ474 - Về mức thu học phí đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026 (Đợt 1) Số… |
| 2 | `-` | 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7053 | Không | Căn cứ Kế hoạch đào tạo trình độ thạc sĩ khoá 28B (12/2025-2027) được ban hành kèm theo Qu… |
| 2 | `-` | 3 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.7019 | Không | Căn cứ Luật Giáo dục đại học số 125/2025/QH15; Căn cứ Thông tư số 06/2026/TT-BGDĐT ngày 15… |
| 2 | **Điểm/Agent** |  |  |  | **2/2** | Áp dụng cho tuyển sinh tháng 2 năm 2026, Đợt 1. |
| 3 | `{'program': 'part-time'}` | 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.5970 | Có | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức… |
| 3 | `{'program': 'part-time'}` | 2 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.5816 | Không | I. Mức học phí đào tạo Liên thông vừa làm vừa học (hệ 2 năm - 3 năm) II. Hiệu lực thi hành… |
| 3 | `{'program': 'part-time'}` | 3 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.5596 | Không | Căn cứ Nghị định số 97/2023/NĐ-CP ngày 31/12/2023 của Thủ tướng Chính phủ sửa đổi, bổ sung… |
| 3 | **Điểm/Agent** |  |  |  | **2/2** | Áp dụng cho khóa 34 ngành Quản lý đất đai, tuyển sinh năm 2024. |
| 4 | `{'program': 'graduate'}` | 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7750 | Không | Nhà trường đề nghị học viên cao học khóa 28B thực hiện đúng thời gian học, thi kết thúc họ… |
| 4 | `{'program': 'graduate'}` | 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7271 | Không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học K… |
| 4 | `{'program': 'graduate'}` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.6778 | Không | Căn cứ Kế hoạch đào tạo trình độ thạc sĩ khoá 28B (12/2025-2027) được ban hành kèm theo Qu… |
| 4 | **Điểm/Agent** |  |  |  | **0/2** | Không đủ thông tin trong ngữ cảnh đã truy xuất. |
| 5 | `{'audience': 'student'}` | 1 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | 0.8627 | Có | 1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 trong 03 tuần, từ ngày 09 tháng 02 năm … |
| 5 | `{'audience': 'student'}` | 2 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | 0.7740 | Không | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên **Số:** 209… |
| 5 | `{'audience': 'student'}` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.5101 | Không | 2. Đối với ngành Toán giải tích, thực hiện chương trình đào tạo Học kỳ 3 (Đợt 3) cùng với … |
| 5 | **Điểm/Agent** |  |  |  | **2/2** | Nghỉ từ ngày 09/02/2026 đến hết ngày 01/03/2026. |

**Tổng: 8/10; gold ở top-1: 4/5.**

### `fixed_size(500/80)` — 25 chunks

| Q | Filter | Hạng | doc_id | score | Gold? | Trích đoạn |
|---:|---|---:|---|---:|---|---|
| 1 | `-` | 1 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.5696 | Có | QUYẾT ĐỊNH: Điều 1. Ban hành kèm theo Quyết định này Quy chế tuyển sinh trình độ đại học c… |
| 1 | `-` | 2 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.5155 | Không | ơn vị, tổ chức và cá nhân liên quan chịu trách nhiệm thi hành Quyết định này./. Quy chế tu… |
| 1 | `-` | 3 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.4893 | Không | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Số: 1401/QĐ - ĐHQN Ban hành Quy ch… |
| 1 | **Điểm/Agent** |  |  |  | **2/2** | Có hiệu lực kể từ ngày ký và thay thế Quyết định số 1455/QĐ-ĐHQN ngày 21/5/2025. |
| 2 | `-` | 1 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | 0.8007 | Có | # QyĐ474 - Về mức thu học phí đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026 (Đợt 1) Số… |
| 2 | `-` | 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7477 | Không | của Hiệu trưởng; Chương trình đào tạo trình độ thạc sĩ của khóa 28B; Quy định số 2114/QyĐ-… |
| 2 | `-` | 3 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | 0.7420 | Có | h giá dịch vụ đào tạo của Trường Đại học Quy Nhơn. Hiệu trưởng Trường Đại học Quy Nhơn quy… |
| 2 | **Điểm/Agent** |  |  |  | **2/2** | Áp dụng cho tuyển sinh tháng 2 năm 2026, Đợt 1. |
| 3 | `{'program': 'part-time'}` | 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.6521 | Không | ọc phí đối với cơ sở giáo dục thuộc hệ thống giáo dục quốc dân và chính sách miễn, giảm họ… |
| 3 | `{'program': 'part-time'}` | 2 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.6047 | Có | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức… |
| 3 | `{'program': 'part-time'}` | 3 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.5236 | Không | h về quyền hạn, trách nhiệm của Hiệu trưởng theo Quy chể tổ chức và hoạt động của Trường Đ… |
| 3 | **Điểm/Agent** |  |  |  | **1/2** | Áp dụng cho khóa 34 ngành Quản lý đất đai, tuyển sinh năm 2024. |
| 4 | `{'program': 'graduate'}` | 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7628 | Không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học K… |
| 4 | `{'program': 'graduate'}` | 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7380 | Không | của Hiệu trưởng; Chương trình đào tạo trình độ thạc sĩ của khóa 28B; Quy định số 2114/QyĐ-… |
| 4 | `{'program': 'graduate'}` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7357 | Có | ọc phí Học kỳ 2 (Đợt 2): - Thời gian nộp học phí: từ ngày 15/5/2026 đến hết ngày 02/8/2026… |
| 4 | **Điểm/Agent** |  |  |  | **1/2** | Nộp từ ngày 15/5/2026 đến hết ngày 02/8/2026. |
| 5 | `{'audience': 'student'}` | 1 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | 0.8547 | Có | ư sau: 1. Sinh viên nghỉ Tết Nguyên đán Bính Ngọ năm 2026 trong 03 tuần, từ ngày 09 tháng … |
| 5 | `{'audience': 'student'}` | 2 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | 0.7740 | Không | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên **Số:** 209… |
| 5 | `{'audience': 'student'}` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.5594 | Không | 8/2026 đến ngày 06/9/2026. 2. Đối với ngành Toán giải tích, thực hiện chương trình đào tạo… |
| 5 | **Điểm/Agent** |  |  |  | **2/2** | Nghỉ từ ngày 09/02/2026 đến hết ngày 01/03/2026. |

**Tổng: 8/10; gold ở top-1: 3/5.**

### `by_sentences(3)` — 18 chunks

| Q | Filter | Hạng | doc_id | score | Gold? | Trích đoạn |
|---:|---|---:|---|---:|---|---|
| 1 | `-` | 1 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.6857 | Có | Điều 2. Quyết định này có hiệu lực kể từ ngày ký và thay thế Quyết định số 1455/QĐ-ĐHQN ng… |
| 1 | `-` | 2 | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.4893 | Không | # QĐ1401 - Ban hành Quy chế tuyển sinh trình độ đại học Số: 1401/QĐ - ĐHQN Ban hành Quy ch… |
| 1 | `-` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.3995 | Không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học K… |
| 1 | **Điểm/Agent** |  |  |  | **2/2** | Có hiệu lực kể từ ngày ký và thay thế Quyết định số 1455/QĐ-ĐHQN ngày 21/5/2025. |
| 2 | `-` | 1 | `quy-dinh-02-qyd474-ve-muc-thu-hoc-phi-dao-tao-dai-hoc-tu-xa-tuyen-sinh-thang-2-nam-2026-dot-1` | 0.8007 | Có | # QyĐ474 - Về mức thu học phí đào tạo đại học từ xa tuyển sinh tháng 2 năm 2026 (Đợt 1) Số… |
| 2 | `-` | 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.6968 | Không | Thời gian nộp, mức thu học phí Học kỳ 2 (Đợt 2): - Thời gian nộp học phí: từ ngày 15/5/202… |
| 2 | `-` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.6742 | Không | Mọi thắc mắc về học phí liên hệ SĐT: (0256)3 546 882 (Phòng Kế hoạch-Tàchính) trong giờ hà… |
| 2 | **Điểm/Agent** |  |  |  | **2/2** | Áp dụng cho tuyển sinh tháng 2 năm 2026, Đợt 1. |
| 3 | `{'program': 'part-time'}` | 1 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.6047 | Có | # QyĐ828 - Về mức thu học phí năm học 2024-2025 đối với hệ đào tạo vừa làm vừa học tổ chức… |
| 3 | `{'program': 'part-time'}` | 2 | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.1147 | Không | Đăng nhập và xem trên E-Office 2.0: https://eoffice.qnu.edu.vn/app/view-document?xuLyId=b2… |
| 3 | **Điểm/Agent** |  |  |  | **2/2** | Áp dụng cho khóa 34 ngành Quản lý đất đai, tuyển sinh năm 2024. |
| 4 | `{'program': 'graduate'}` | 1 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7780 | Không | Mọi thắc mắc về học phí liên hệ SĐT: (0256)3 546 882 (Phòng Kế hoạch-Tàchính) trong giờ hà… |
| 4 | `{'program': 'graduate'}` | 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7628 | Không | # TB1525 - Về thời gian học tập và nộp học phí Học kỳ 2 (Đợt 2) đối với học viên cao học K… |
| 4 | `{'program': 'graduate'}` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.7374 | Có | Thời gian nộp, mức thu học phí Học kỳ 2 (Đợt 2): - Thời gian nộp học phí: từ ngày 15/5/202… |
| 4 | **Điểm/Agent** |  |  |  | **1/2** | Nộp từ ngày 15/5/2026 đến hết ngày 02/8/2026. |
| 5 | `{'audience': 'student'}` | 1 | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | 0.7740 | Có | # TB209 - Về thời gian nghỉ Tết Nguyên đán Bính Ngọ năm 2026 đối với sinh viên **Số:** 209… |
| 5 | `{'audience': 'student'}` | 2 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.5423 | Không | Đối với ngành Toán giải tích, thực hiện chương trình đào tạo Học kỳ 3 (Đợt 3) cùng với ngà… |
| 5 | `{'audience': 'student'}` | 3 | `quy-dinh-04-tb1525-ve-thoi-gian-hoc-tap-va-nop-hoc-phi-hoc-ky-2-dot-2-doi-voi-hoc-vien-cao-hoc-khoa-28b-12-2025-2027` | 0.4915 | Không | Thời gian nộp, mức thu học phí Học kỳ 2 (Đợt 2): - Thời gian nộp học phí: từ ngày 15/5/202… |
| 5 | **Điểm/Agent** |  |  |  | **2/2** | Nghỉ từ ngày 09/02/2026 đến hết ngày 01/03/2026. |

**Tổng: 9/10; gold ở top-1: 4/5.**

### Tổng hợp

| Chiến lược | Chunks | Top-1 đúng | Điểm /10 |
|---|---:|---:|---:|
| `heading(level=1..3)` | 6 | 5/5 | 10 |
| `recursive(600)` | 23 | 4/5 | 8 |
| `fixed_size(500/80)` | 25 | 3/5 | 8 |
| `by_sentences(3)` | 18 | 4/5 | 9 |

## C. Tác động của metadata filter

### Q3: `{'program': 'part-time'}`

| Chế độ | Top-1 doc | Top-1 score | Điểm |
|---|---|---:|---:|
| Không lọc | `quy-dinh-01-qd1401-ban-hanh-quy-che-tuyen-sinh-trinh-do-dai-hoc` | 0.6766 | 0/2 |
| Có lọc | `quy-dinh-03-qyd828-ve-muc-thu-hoc-phi-nam-hoc-2024-2025-doi-voi-he-dao-tao-vua-lam-vua-hoc-to-chuc-tai-truong-ap-dung-cho-khoa-34-nganh-quan-ly-dat-dai-tuyen-sinh-nam-2024` | 0.5970 | 2/2 |

### Q5: `{'audience': 'student'}`

| Chế độ | Top-1 doc | Top-1 score | Điểm |
|---|---|---:|---:|
| Không lọc | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | 0.8627 | 2/2 |
| Có lọc | `quy-dinh-05-tb209-ve-thoi-gian-nghi-tet-nguyen-dan-binh-ngo-nam-2026-doi-voi-sinh-vien` | 0.8627 | 2/2 |

> Q5 dùng đúng bộ lọc bắt buộc của K3 (`audience=student`). Vì cả 5 tài liệu hiện đều hướng tới người học, bộ lọc này chủ yếu xác nhận contract. Q3 dùng `program=part-time` để minh họa bộ lọc có tính phân biệt.

## D. Similarity cá nhân

| Cặp | Dự đoán | Score | Đúng? |
|---:|---|---:|---|
| 1 | CAO | 0.8670 | Có |
| 2 | CAO | 0.8451 | Có |
| 3 | CAO | 0.6158 | Có |
| 4 | THẤP | 0.0620 | Có |
| 5 | THẤP | 0.2119 | Có |

## E. Vòng đời store

- Trước xóa: **23** chunks.
- Xóa TB209: `True`; sau xóa: **18** chunks.
- Xóa ID không tồn tại: `False`.

## F. Failure case do thiếu dữ liệu nguồn

- Câu hỏi thử lỗi: **Mức học phí cụ thể theo khối ngành trong QyĐ474 là bao nhiêu?**
- Trang đã crawl có tiêu đề mục `I. Mức học phí theo khối ngành` nhưng bảng số tiền không xuất hiện trong phần văn bản công khai đã lấy. Vì vậy retrieval có thể tìm đúng tài liệu nhưng agent không thể tạo câu trả lời có căn cứ.
- Cải thiện: lấy tệp đính kèm/PDF công khai nếu được phép, trích xuất bảng và giữ nguyên `source_url`; không suy đoán hoặc tự điền mức tiền.
