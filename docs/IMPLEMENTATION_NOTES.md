# Ghi chú triển khai hiện tại — Lab 7

Tài liệu này mô tả trạng thái mã nguồn ngày 2026-08-03. Kết quả thực nghiệm chính thức nằm ở `report/benchmark_raw.md`; báo cáo cá nhân và nhóm lần lượt ở `report/REPORT_CANHAN.md` và `report/REPORT_NHOM.md`.

## Thành phần đã triển khai

- `src/chunking.py`: FixedSize, Sentence, Recursive, Heading, cosine similarity và comparator.
- `src/store.py`: thêm tài liệu, tìm top-k, lọc metadata trước similarity, đếm collection và xóa toàn bộ chunk theo `doc_id`; dùng ChromaDB khi có, nếu không dùng bộ nhớ.
- `src/agent.py`: pipeline retrieve → ghép context → prompt grounding → gọi `llm_fn`.
- `ingest.py`: parse front matter, gắn metadata vào từng chunk và nạp store.
- `data/qnu_regulations/`: 5 tài liệu công khai QNU cùng `sources.csv`; mỗi tài liệu có metadata truy vết và metadata K3.
- `scripts/run_benchmark.py`: baseline 3 tài liệu, đúng 5 query, 4 chiến lược, top-3, filter, similarity, lifecycle store và failure case.
- `demo_ui.py`: UI Streamlit cho tìm kiếm, câu trả lời extractive có grounding, metadata filter, top-k và so sánh chiến lược.

## Cấu hình benchmark

- Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` chạy local.
- Corpus: `data/qnu_regulations`, 5 tài liệu, 9.513 ký tự nội dung sau làm sạch.
- Kết quả: Heading 10/10; Sentence 9/10; Fixed 8/10; Recursive 8/10.
- Q3 dùng `program=part-time`: Recursive tăng từ 0/2 lên 2/2 sau lọc.
- Q5 dùng `audience=student`, đáp ứng contract riêng của K3.

## Cách chạy tái lập

```powershell
pytest tests/ -v
python ingest.py
$env:EMBEDDING_PROVIDER="local"
$env:USE_TF="0"
$env:TRANSFORMERS_NO_TF="1"
python scripts/run_benchmark.py
python -m streamlit run demo_ui.py
```

Nếu máy không có mạng nhưng model đã được cache, đặt `LOCAL_EMBEDDING_MODEL` thành thư mục snapshot trong cache Hugging Face và `HF_HUB_OFFLINE=1`.

## Giới hạn được ghi nhận

- Toàn bộ corpus hiện có `audience=student`; Q5 kiểm tra đúng API filter nhưng filter không đổi thứ hạng. Trường `program` ở Q3 mới cho thấy tác động phân biệt rõ.
- Bảng số tiền trong QyĐ474 không xuất hiện trong HTML đã crawl. Không được suy đoán mức học phí; cần lấy PDF/tệp đính kèm công khai nếu muốn trả lời câu hỏi đó.
- Câu trả lời UI là extractive và không cần API key. Benchmark dùng hàm deterministic để kiểm tra rằng gold phrase thực sự có trong top-3 context; đây không phải đánh giá một LLM sinh văn bản bên ngoài.
- Tên nhóm, thành viên còn lại và phản ánh sau buổi demo là thông tin con người phải điền trước khi nộp.