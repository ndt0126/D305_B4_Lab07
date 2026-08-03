# Kết quả đo thô — Lab 07 (K3), Giai đoạn 2

> File này do `scripts/run_benchmark.py` sinh tự động. Không sửa tay.

- Backend nhúng: **mock embeddings fallback**
- Thư mục dữ liệu: `data/k3_university`
- Số tài liệu trong corpus: **2**

> **CẢNH BÁO PHƯƠNG PHÁP:** mock embedding là hàm băm MD5 -> vector, **không mang ngữ nghĩa**. Mọi điểm số dưới đây là thật nhưng chỉ dùng để kiểm chứng đường ống (pipeline) chạy đúng, KHÔNG dùng để kết luận chiến lược chunking nào tốt hơn về mặt ngữ nghĩa. Đặt `EMBEDDING_PROVIDER=local` để đo lại.

## A. Baseline — ChunkingStrategyComparator

| Tài liệu | Số ký tự | Chiến lược | count | avg_length | min | max |
|---|---|---|---|---|---|---|
| k3-course-registration | 646 | `fixed_size` | 3 | 235.3 | 106 | 300 |
| k3-course-registration | 646 | `by_sentences` | 2 | 321.5 | 277 | 366 |
| k3-course-registration | 646 | `recursive` | 3 | 214.0 | 167 | 294 |
| k3-library-services | 481 | `fixed_size` | 2 | 255.5 | 211 | 300 |
| k3-library-services | 481 | `by_sentences` | 2 | 239.0 | 115 | 363 |
| k3-library-services | 481 | `recursive` | 2 | 239.5 | 202 | 277 |
| chunking_experiment_report (văn bản dài để đối chiếu) | 2282 | `fixed_size` | 9 | 280.2 | 122 | 300 |
| chunking_experiment_report (văn bản dài để đối chiếu) | 2282 | `by_sentences` | 5 | 454.6 | 336 | 620 |
| chunking_experiment_report (văn bản dài để đối chiếu) | 2282 | `recursive` | 15 | 150.2 | 11 | 294 |

## B. 5 câu hỏi đánh giá x 4 chiến lược (top-3)

### Chiến lược `fixed_size(300/50)` — 5 chunk

| # | Câu hỏi | Hạng | doc_id | score | Liên quan? | Trích chunk |
|---|---|---|---|---|---|---|
| 1 | Sinh viên đăng ký học phần ở đâu và theo lịch nào? | 1 | k3-course-registration | 0.213 | CÓ | ark. # Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần… |
| 1 |  | 2 | k3-course-registration | 0.077 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 1 |  | 3 | k3-library-services | 0.020 | không | học tập cho sinh viên, giảng viên và nhân viên. Người dùng cần mang th… |
| 1 | **điểm câu này** | | | | **2/2** | |
| 2 | Khi gặp lỗi trùng lịch thì sinh viên phải xử lý thế nào? | 1 | k3-course-registration | 0.151 | CÓ | ark. # Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần… |
| 2 |  | 2 | k3-library-services | 0.121 | không | học tập cho sinh viên, giảng viên và nhân viên. Người dùng cần mang th… |
| 2 |  | 3 | k3-course-registration | 0.094 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 2 | **điểm câu này** | | | | **2/2** | |
| 3 | Yêu cầu ngoại lệ về học vụ được gửi qua kênh nào? | 1 | k3-library-services | 0.320 | không | > Khối metadata phía trên là **template mẫu** cho K3 — thay `source_ur… |
| 3 |  | 2 | k3-course-registration | 0.177 | không | ark. # Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần… |
| 3 |  | 3 | k3-course-registration | 0.103 | CÓ | h, sinh viên điều chỉnh lớp học phần trước thời hạn điều chỉnh được cô… |
| 3 | **điểm câu này** | | | | **1/2** | |
| 4 | Cần mang theo giấy tờ gì khi mượn tài liệu ở thư viện? | 1 | k3-course-registration | 0.133 | không | ark. # Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần… |
| 4 |  | 2 | k3-course-registration | 0.040 | không | h, sinh viên điều chỉnh lớp học phần trước thời hạn điều chỉnh được cô… |
| 4 |  | 3 | k3-library-services | -0.027 | không | > Khối metadata phía trên là **template mẫu** cho K3 — thay `source_ur… |
| 4 | **điểm câu này** | | | | **0/2** | |
| 5 | Quy định về học phần tiên quyết áp dụng cho sinh viên là gì? | 1 | k3-course-registration | -0.012 | không | h, sinh viên điều chỉnh lớp học phần trước thời hạn điều chỉnh được cô… |
| 5 |  | 2 | k3-course-registration | -0.024 | CÓ | ark. # Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần… |
| 5 |  | 3 | k3-course-registration | -0.043 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 5 | **điểm câu này** | | | | **1/2** | |

**Tổng điểm truy xuất `fixed_size(300/50)`: 6/10**

*Ví dụ câu trả lời agent (Q1):* [DEMO LLM] Trả lời dựa trên 3 đoạn ngữ cảnh: [1] (nguồn: https://example.edu/hoc-vu/dang-ky-hoc-phan | score=0.213) ark. # Đăng ký học phần (dữ liệu khởi động) Sinh …

### Chiến lược `by_sentences(2)` — 5 chunk

| # | Câu hỏi | Hạng | doc_id | score | Liên quan? | Trích chunk |
|---|---|---|---|---|---|---|
| 1 | Sinh viên đăng ký học phần ở đâu và theo lịch nào? | 1 | k3-course-registration | 0.043 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 1 |  | 2 | k3-library-services | 0.041 | không | Người dùng cần mang thẻ định danh hợp lệ khi sử dụng dịch vụ mượn. Nhó… |
| 1 |  | 3 | k3-course-registration | 0.026 | CÓ | # Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần tron… |
| 1 | **điểm câu này** | | | | **1/2** | |
| 2 | Khi gặp lỗi trùng lịch thì sinh viên phải xử lý thế nào? | 1 | k3-library-services | -0.013 | không | Người dùng cần mang thẻ định danh hợp lệ khi sử dụng dịch vụ mượn. Nhó… |
| 2 |  | 2 | k3-library-services | -0.056 | không | > Khối metadata phía trên là **template mẫu** cho K3 — thay `source_ur… |
| 2 |  | 3 | k3-course-registration | -0.079 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 2 | **điểm câu này** | | | | **0/2** | |
| 3 | Yêu cầu ngoại lệ về học vụ được gửi qua kênh nào? | 1 | k3-library-services | 0.084 | không | > Khối metadata phía trên là **template mẫu** cho K3 — thay `source_ur… |
| 3 |  | 2 | k3-course-registration | 0.079 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 3 |  | 3 | k3-course-registration | -0.055 | CÓ | Khi gặp lỗi trùng lịch, sinh viên điều chỉnh lớp học phần trước thời h… |
| 3 | **điểm câu này** | | | | **1/2** | |
| 4 | Cần mang theo giấy tờ gì khi mượn tài liệu ở thư viện? | 1 | k3-course-registration | 0.413 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 4 |  | 2 | k3-library-services | 0.334 | CÓ | Người dùng cần mang thẻ định danh hợp lệ khi sử dụng dịch vụ mượn. Nhó… |
| 4 |  | 3 | k3-course-registration | 0.199 | không | Khi gặp lỗi trùng lịch, sinh viên điều chỉnh lớp học phần trước thời h… |
| 4 | **điểm câu này** | | | | **1/2** | |
| 5 | Quy định về học phần tiên quyết áp dụng cho sinh viên là gì? | 1 | k3-course-registration | -0.100 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 5 |  | 2 | k3-course-registration | -0.120 | CÓ | # Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần tron… |
| 5 |  | 3 | k3-course-registration | -0.123 | không | Khi gặp lỗi trùng lịch, sinh viên điều chỉnh lớp học phần trước thời h… |
| 5 | **điểm câu này** | | | | **1/2** | |

**Tổng điểm truy xuất `by_sentences(2)`: 4/10**

*Ví dụ câu trả lời agent (Q1):* [DEMO LLM] Trả lời dựa trên 3 đoạn ngữ cảnh: [1] (nguồn: https://example.edu/hoc-vu/dang-ky-hoc-phan | score=0.043) > Khối metadata phía trên là **template mẫu** cho…

### Chiến lược `recursive(300)` — 5 chunk

| # | Câu hỏi | Hạng | doc_id | score | Liên quan? | Trích chunk |
|---|---|---|---|---|---|---|
| 1 | Sinh viên đăng ký học phần ở đâu và theo lịch nào? | 1 | k3-course-registration | 0.240 | CÓ | Sinh viên đăng ký học phần trong cổng học vụ theo lịch của từng học kỳ… |
| 1 |  | 2 | k3-course-registration | 0.066 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 1 |  | 3 | k3-library-services | -0.058 | không | Thư viện cung cấp mượn tài liệu và không gian học tập cho sinh viên, g… |
| 1 | **điểm câu này** | | | | **2/2** | |
| 2 | Khi gặp lỗi trùng lịch thì sinh viên phải xử lý thế nào? | 1 | k3-course-registration | 0.220 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 2 |  | 2 | k3-library-services | 0.077 | không | > Khối metadata phía trên là **template mẫu** cho K3 — thay `source_ur… |
| 2 |  | 3 | k3-library-services | 0.058 | không | Thư viện cung cấp mượn tài liệu và không gian học tập cho sinh viên, g… |
| 2 | **điểm câu này** | | | | **0/2** | |
| 3 | Yêu cầu ngoại lệ về học vụ được gửi qua kênh nào? | 1 | k3-library-services | 0.203 | không | Thư viện cung cấp mượn tài liệu và không gian học tập cho sinh viên, g… |
| 3 |  | 2 | k3-library-services | 0.146 | không | > Khối metadata phía trên là **template mẫu** cho K3 — thay `source_ur… |
| 3 |  | 3 | k3-course-registration | 0.132 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 3 | **điểm câu này** | | | | **0/2** | |
| 4 | Cần mang theo giấy tờ gì khi mượn tài liệu ở thư viện? | 1 | k3-course-registration | 0.264 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 4 |  | 2 | k3-course-registration | 0.199 | không | Khi gặp lỗi trùng lịch, sinh viên điều chỉnh lớp học phần trước thời h… |
| 4 |  | 3 | k3-course-registration | 0.171 | không | Sinh viên đăng ký học phần trong cổng học vụ theo lịch của từng học kỳ… |
| 4 | **điểm câu này** | | | | **0/2** | |
| 5 | Quy định về học phần tiên quyết áp dụng cho sinh viên là gì? | 1 | k3-course-registration | -0.088 | CÓ | Sinh viên đăng ký học phần trong cổng học vụ theo lịch của từng học kỳ… |
| 5 |  | 2 | k3-course-registration | -0.123 | không | Khi gặp lỗi trùng lịch, sinh viên điều chỉnh lớp học phần trước thời h… |
| 5 |  | 3 | k3-course-registration | -0.135 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 5 | **điểm câu này** | | | | **2/2** | |

**Tổng điểm truy xuất `recursive(300)`: 4/10**

*Ví dụ câu trả lời agent (Q1):* [DEMO LLM] Trả lời dựa trên 3 đoạn ngữ cảnh: [1] (nguồn: https://example.edu/hoc-vu/dang-ky-hoc-phan | score=0.240) Sinh viên đăng ký học phần trong cổng học vụ theo…

### Chiến lược `heading(max=600)` — 4 chunk

| # | Câu hỏi | Hạng | doc_id | score | Liên quan? | Trích chunk |
|---|---|---|---|---|---|---|
| 1 | Sinh viên đăng ký học phần ở đâu và theo lịch nào? | 1 | k3-course-registration | 0.043 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 1 |  | 2 | k3-library-services | -0.088 | không | > Khối metadata phía trên là **template mẫu** cho K3 — thay `source_ur… |
| 1 |  | 3 | k3-library-services | -0.100 | không | Dịch vụ thư viện (dữ liệu khởi động) Thư viện cung cấp mượn tài liệu v… |
| 1 | **điểm câu này** | | | | **0/2** | |
| 2 | Khi gặp lỗi trùng lịch thì sinh viên phải xử lý thế nào? | 1 | k3-course-registration | 0.134 | CÓ | Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần trong … |
| 2 |  | 2 | k3-course-registration | -0.079 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 2 |  | 3 | k3-library-services | -0.203 | không | > Khối metadata phía trên là **template mẫu** cho K3 — thay `source_ur… |
| 2 | **điểm câu này** | | | | **2/2** | |
| 3 | Yêu cầu ngoại lệ về học vụ được gửi qua kênh nào? | 1 | k3-course-registration | 0.086 | CÓ | Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần trong … |
| 3 |  | 2 | k3-library-services | 0.084 | không | > Khối metadata phía trên là **template mẫu** cho K3 — thay `source_ur… |
| 3 |  | 3 | k3-course-registration | 0.079 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 3 | **điểm câu này** | | | | **2/2** | |
| 4 | Cần mang theo giấy tờ gì khi mượn tài liệu ở thư viện? | 1 | k3-course-registration | 0.413 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 4 |  | 2 | k3-course-registration | 0.096 | không | Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần trong … |
| 4 |  | 3 | k3-library-services | -0.051 | CÓ | Dịch vụ thư viện (dữ liệu khởi động) Thư viện cung cấp mượn tài liệu v… |
| 4 | **điểm câu này** | | | | **1/2** | |
| 5 | Quy định về học phần tiên quyết áp dụng cho sinh viên là gì? | 1 | k3-course-registration | -0.020 | CÓ | Đăng ký học phần (dữ liệu khởi động) Sinh viên đăng ký học phần trong … |
| 5 |  | 2 | k3-course-registration | -0.100 | không | > Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audie… |
| 5 | **điểm câu này** | | | | **2/2** | |

**Tổng điểm truy xuất `heading(max=600)`: 7/10**

*Ví dụ câu trả lời agent (Q1):* [DEMO LLM] Trả lời dựa trên 3 đoạn ngữ cảnh: [1] (nguồn: https://example.edu/hoc-vu/dang-ky-hoc-phan | score=0.043) > Khối metadata phía trên là **template mẫu** cho…

### Tổng hợp

| Chiến lược | Điểm truy xuất /10 |
|---|---|
| `fixed_size(300/50)` | 6 |
| `by_sentences(2)` | 4 |
| `recursive(300)` | 4 |
| `heading(max=600)` | 7 |

## C. search() vs search_with_filter() — cùng câu hỏi Q5

**search() — KHÔNG lọc** — điểm câu này: 1/2

| Hạng | doc_id | audience | score | Liên quan? |
|---|---|---|---|---|
| 1 | k3-library-services | all | 0.003 | không |
| 2 | k3-library-services | all | -0.081 | không |
| 3 | k3-course-registration | student | -0.088 | CÓ |

**search_with_filter(audience="student")** — điểm câu này: 2/2

| Hạng | doc_id | audience | score | Liên quan? |
|---|---|---|---|---|
| 1 | k3-course-registration | student | -0.088 | CÓ |
| 2 | k3-course-registration | student | -0.123 | không |
| 3 | k3-course-registration | student | -0.135 | không |

## D. Dự đoán độ tương tự cosine (5 cặp câu)

| Cặp | Câu A | Câu B | Dự đoán | compute_similarity | Đúng dự đoán? |
|---|---|---|---|---|---|
| 1 | Sinh viên đăng ký học phần trong cổng học vụ. | Việc đăng ký môn học được thực hiện trên cổng thông tin… | CAO | -0.1328 | SAI |
| 2 | Thư viện cho mượn tài liệu và cung cấp không gian học t… | Người dùng cần mang thẻ định danh hợp lệ khi mượn tài l… | CAO | 0.0153 | SAI |
| 3 | Sinh viên đăng ký học phần trong cổng học vụ. | Thư viện cho mượn tài liệu và cung cấp không gian học t… | THẤP | 0.0683 | Đúng |
| 4 | Học phần tiên quyết phải được hoàn thành trước. | Hôm nay trời mưa rất to ở khu ký túc xá. | THẤP | 0.0467 | Đúng |
| 5 | Sinh viên đăng ký học phần trong cổng học vụ. | Sinh viên đăng ký học phần trong cổng học vụ. | CAO (=1.0) | 1.0000 | Đúng |

## E. Vòng đời store — size / delete_document

- Số chunk ban đầu: **5**
- `delete_document('k3-library-services')` -> `True`; còn lại **3** chunk
- `delete_document('khong-ton-tai')` -> `False` (đúng kỳ vọng: không xóa gì)
