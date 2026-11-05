# Hướng dẫn học và trình bày dự án

Dự án này được xây dựng với sự hỗ trợ của AI theo yêu cầu của bạn. Trước khi đưa vào CV, hãy tự chạy lại, kiểm tra và giải thích được các phần bên dưới. Không ghi kinh nghiệm làm việc tại ngân hàng hoặc kết quả tăng doanh thu/giảm churn chưa xảy ra.

## Thứ tự đọc

1. `data/README.md`: dữ liệu lấy ở đâu, có gì chưa xác minh.
2. `docs/data-dictionary.md`: mỗi dòng là một khách hàng, ý nghĩa các cột và KPI.
3. `sql/01_schema.sql`: bảng dữ liệu và cách chia nhóm.
4. `sql/02_overview.sql` và `03_segments.sql`: đếm, tính tỷ lệ, GROUP BY, CTE, window functions.
5. `reports/analysis.md`: phát hiện có số liệu và giới hạn của kết luận.
6. `dashboard/index.html`: thử bộ lọc và đối chiếu lại bằng SQL.
7. `docs/business-analysis.md`: phạm vi, quy trình giả định, yêu cầu và acceptance criteria.

## Những điểm phải hiểu

- **16,07%** là tỷ lệ nhãn đã rời bỏ trong một snapshot, không phải churn tháng này.
- **Tỷ lệ rời bỏ của nhóm** và **tỷ trọng trong toàn bộ người rời bỏ** có mẫu số khác nhau.
- Có 1.112 khách hàng ghi thu nhập Unknown; không có nghĩa thu nhập bằng 0.
- Giao dịch ít có liên hệ với nhãn rời bỏ, nhưng có thể do khách hàng đã rời đi nên ngừng dùng thẻ. Thiếu ngày để biết trình tự.
- Hai cột Naive Bayes có sẵn là đầu ra mô hình. Dùng chúng để dự đoán lại nhãn có thể gây rò rỉ thông tin.
- Không có phí, nguyên nhân đóng thẻ hay dữ liệu thử nghiệm; không được kết luận phí gây churn hoặc chiến dịch giữ chân có hiệu quả.
- Nhóm Platinum chỉ có 20 khách hàng. Tỷ lệ cao không tự động khiến nó thành nhóm nên ưu tiên nhất.

## Bài tập bạn nên tự làm

1. Tự viết lại truy vấn tính 10.127 khách hàng, 1.627 nhãn rời bỏ và tỷ lệ 16,07%.
2. Chọn nhóm Blue trong dashboard rồi dùng WHERE trong SQL để đối chiếu.
3. Giải thích tại sao nhóm 40–59 giao dịch có tỷ lệ rời bỏ cao hơn nhóm <40; không giả định mối quan hệ luôn tuyến tính.
4. Thử đổi cách chia nhóm giao dịch ở một bản sao, cập nhật cả SQL và dashboard, rồi mô tả kết luận thay đổi thế nào.
5. Viết một giả thuyết khác và liệt kê dữ liệu còn thiếu để kiểm tra.
6. Tự bổ sung một user story cùng ít nhất ba tiêu chí nghiệm thu có thể kiểm tra.

## Cách kể khi phỏng vấn

"Đây là dự án portfolio dùng dữ liệu Kaggle, không phải dự án triển khai cho ngân hàng. Tôi sử dụng SQL để phân tích trạng thái rời bỏ và hành vi dùng thẻ, rồi xây dashboard và đề xuất bước kiểm chứng. Dữ liệu chỉ là snapshot nên tôi không coi các mối liên hệ là nguyên nhân. Tôi có sử dụng AI hỗ trợ xây dựng; những phần tôi đã tự kiểm tra và có thể giải thích là ..."

Điền phần cuối bằng đúng những gì bạn thực sự đã làm. Có thể trình bày theo chuỗi: vấn đề → dữ liệu → kiểm tra chất lượng → KPI → phát hiện → giới hạn → đề xuất kiểm chứng.

## Gợi ý CV sau khi bạn đã tự kiểm tra

**DA:** Analyzed 10,127 credit-card customer records using SQLite; built a reproducible segmentation pipeline and interactive dashboard to investigate observed attrition patterns, with explicit data-quality and leakage checks.

**BA:** Authored a proposed retention-dashboard requirements package including scope, metric definitions, process flows, five user stories and testable acceptance criteria; linked requirements to dashboard functions and validation evidence.

Không ghi "reduced churn by X%", "saved X dollars", "deployed at a bank", hay "developed Power BI dashboard" — dự án hiện dùng HTML tương tác, chưa có can thiệp thực tế hoặc file PBIX.
