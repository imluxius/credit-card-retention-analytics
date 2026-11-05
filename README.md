# Credit Card Retention Analytics

Case study DA/BA cho bài toán khách hàng thẻ tín dụng rời bỏ dịch vụ.

## Bài toán nghiệp vụ

Một nhóm chăm sóc khách hàng muốn biết nhóm khách hàng nào có dấu hiệu ít tương tác và cần được điều tra trước khi thiết kế chương trình giữ chân. Dự án trả lời:

- Tỷ lệ khách hàng được gắn nhãn `Attrited Customer` là bao nhiêu?
- Nhóm nào có tỷ lệ và số lượng rời bỏ đáng chú ý?
- Hành vi giao dịch, không hoạt động và liên hệ khác nhau thế nào?
- Cần thêm dữ liệu gì trước khi triển khai một chương trình giữ chân?

## Kết quả chính

- 10.127 khách hàng trong dataset.
- 1.627 khách hàng được gắn nhãn rời bỏ, tương đương 16,07% trong snapshot.
- Nhóm 40–59 giao dịch có 2.134 khách hàng, tỷ lệ gắn nhãn rời bỏ 39,13%.
- Nhóm rời bỏ có trung bình 44,9 giao dịch, so với 68,7 ở nhóm còn lại.

Đây là phân tích mô tả trên một snapshot. Dữ liệu không có ngày sự kiện, phí, lý do đóng thẻ hay lịch sử từng giao dịch, nên chưa thể kết luận nguyên nhân hoặc dự đoán churn tương lai.

## Sản phẩm trong repo

- `sql/`: schema, KPI, phân khúc và cohort điều tra.
- `src/pipeline.py`: kiểm tra dữ liệu, nạp SQLite, chạy SQL và xuất báo cáo.
- `docs/business-analysis.md`: scope, stakeholder, quy trình, user story và acceptance criteria.
- `reports/analysis.md`: insight và đề xuất nghiệp vụ.
- `reports/dashboard-preview.png`: ảnh minh họa báo cáo tổng hợp.
- `notebooks/01_exploration.ipynb`: walkthrough để học và trình bày.
- `data/raw/BankChurners.csv`: dataset Kaggle đã ghim checksum.

## Chạy dự án

Yêu cầu Python 3.11+, không cần cài package ngoài.

```bash
python -m src.pipeline
python -m unittest discover -s tests -v
```

Các file kết quả được tạo trong `reports/`; SQLite trung gian nằm ở `data/processed/` và không commit.

## Dataset

Nguồn: [Credit Card Customers trên Kaggle](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers).

File được dùng trong repo có 10.127 dòng và SHA-256:

```text
c91b525a2a6755a1b0b80dad1d0d008ca97ec4df34552c8f47ffa12b6184b779
```

Nguồn dữ liệu thực tế và ngân hàng gốc chưa được xác minh. Không trình bày đây là dữ liệu vận hành của ngân hàng Việt Nam.

## Cách trình bày khi phỏng vấn

“Tôi phân tích dữ liệu khách hàng thẻ tín dụng bằng Python, SQLite và SQL. Tôi bắt đầu từ định nghĩa grain và KPI, kiểm tra chất lượng dữ liệu, so sánh các nhóm hành vi, rồi chuyển kết quả thành scope, user story và acceptance criteria cho một bài toán retention. Vì dữ liệu chỉ là snapshot, tôi chỉ trình bày association và nêu dữ liệu cần bổ sung trước khi triển khai.”

Dự án này là portfolio case study, không phải kinh nghiệm triển khai tại ngân hàng. Hãy chạy lại và hiểu các truy vấn trước khi đưa vào CV.
