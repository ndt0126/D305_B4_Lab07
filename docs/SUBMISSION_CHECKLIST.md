# Checklist hoàn thiện và nộp Lab 7

## Đã hoàn thành kỹ thuật

- [x] Hoàn thiện TODO trong `src/chunking.py`, `src/store.py`, `src/agent.py`.
- [x] Corpus có 5 tài liệu QNU công khai, đúng chủ đề K3.
- [x] `sources.csv` ánh xạ nguồn 1–1; mỗi tài liệu có metadata bắt buộc và metadata hữu ích.
- [x] Có ít nhất một chiến lược Heading/Section.
- [x] Có đúng 5 benchmark query và gold answer kiểm chứng được.
- [x] Q5 dùng `metadata_filter={"audience": "student"}`; Q3 chứng minh filter phân biệt bằng `program=part-time`.
- [x] So sánh 4 chiến lược bằng local multilingual embeddings.
- [x] Ghi top-3, score, grounding và kết quả theo rubric vào `report/benchmark_raw.md`.
- [x] Có failure analysis và phương án cải thiện không bịa dữ liệu.
- [x] Có UI Streamlit và hướng dẫn demo.
- [x] Hoàn thiện nội dung kỹ thuật `REPORT_CANHAN.md` và `REPORT_NHOM.md`.

## Kiểm tra cuối

```powershell
pytest tests/ -v
python ingest.py
$env:EMBEDDING_PROVIDER="local"
$env:USE_TF="0"
$env:TRANSFORMERS_NO_TF="1"
python scripts/run_benchmark.py
python -m streamlit run demo_ui.py
```

## Việc bắt buộc do người nộp/nhóm thực hiện

- [ ] Điền **tên nhóm** trong hai báo cáo.
- [x] Đã điền **đủ tên thành viên** trong `REPORT_NHOM.md`.
- [x] Đã gán bốn chiến lược theo đúng phân công thành viên.
- [ ] Sau buổi demo, Vinh điền 2–3 câu “điều học được từ thành viên/nhóm khác” trong `REPORT_CANHAN.md`.
- [ ] Nhóm chạy thử UI trên máy sẽ thuyết trình và thực hiện phần demo trực tiếp.
- [ ] Kiểm tra chính sách đặt tên/nén file của giảng viên trước khi nộp.

Không nên tự điền bốn mục đầu bằng thông tin giả; đây là các điểm duy nhất mã nguồn không thể tự hoàn tất.