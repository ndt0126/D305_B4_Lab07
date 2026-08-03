# UI Demo — QNU Retrieval Lab

UI Streamlit hỗ trợ phần trình diễn nhóm: truy vấn RAG, metadata filter, xem
top-k chunks có score và nguồn, so sánh bốn chiến lược, và kiểm kê corpus.

## Cài đặt

```powershell
python -m pip install -r requirements-ui.txt
```

## Chạy

```powershell
python -m streamlit run demo_ui.py
```

Streamlit sẽ in URL local, thường là `http://localhost:8501`.

## Luồng demo đề xuất

1. Chọn corpus `qnu_regulations` và backend **Local đa ngữ**.
2. Ở tab **Tra cứu RAG**, chọn một câu hỏi mẫu và bấm **Tìm kiếm & trả lời**.
3. Chỉ ra top-3, score, `doc_id`, metadata, nội dung chunk và URL nguồn.
4. Bật một metadata filter ở sidebar rồi chạy lại để so sánh.
5. Sang tab **So sánh chiến lược**, chạy cùng câu hỏi trên bốn chunker.
6. Sang tab **Corpus & metadata** để chứng minh đủ số tài liệu và khả năng truy vết.

## Lưu ý

- Backend local dùng model `paraphrase-multilingual-MiniLM-L12-v2`; lần đầu có
  thể cần tải model và khởi tạo lâu hơn.
- Backend mock chỉ phù hợp kiểm tra luồng UI/unit test, không dùng để kết luận
  chất lượng ngữ nghĩa.
- Câu trả lời hiển thị là extractive grounded answer lấy trực tiếp từ context
  top-k, không cần API key và không phải câu trả lời sinh bởi LLM bên ngoài.
