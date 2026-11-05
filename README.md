# Credit Card Retention Analytics

> Case study Phân tích Dữ liệu (DA) & Nghiệp vụ Kinh doanh (BA) cho bài toán khách hàng thẻ tín dụng rời bỏ dịch vụ (Customer Retention & Churn Analytics).

[![Validate analysis](https://github.com/imluxius/credit-card-retention-analytics/actions/workflows/validate.yml/badge.svg)](https://github.com/imluxius/credit-card-retention-analytics/actions/workflows/validate.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Power BI Desktop](https://img.shields.io/badge/Power_BI-Report-F2C811?logo=powerbi&logoColor=black)](credit-card-retention-analytics.pbix)
[![Zero Dependency](https://img.shields.io/badge/dependencies-0_external_packages-success.svg)](requirements.txt)

---

## 1. Bài toán Nghiệp vụ (Business Problem)

Một danh mục khách hàng thẻ tín dụng đang đối mặt với tình trạng rời bỏ dịch vụ (`Attrited Customer`). Đội ngũ Quản lý Giữ chân Khách hàng (Retention & CRM) cần một công cụ phân tích và báo cáo quản trị để:
1. **Đo lường quy mô và tốc độ rời bỏ:** Tỷ lệ rời bỏ tổng thể và theo từng phân khúc khách hàng là bao nhiêu?
2. **Xác định nhóm hành vi cảnh báo sớm:** Khách hàng giảm sút giao dịch, không hoạt động dài ngày hoặc liên hệ CSKH nhiều lần có tỷ lệ rời bỏ ra sao?
3. **Đề xuất kế hoạch hành động giữ chân (Actionable Plan):** Ưu tiên can thiệp nhóm khách hàng nào vừa có tỷ lệ rời bỏ cao, vừa có quy mô số lượng đủ lớn để tối ưu chi phí retention?
4. **Kiểm toán chất lượng dữ liệu & Giới hạn phân tích:** Reconcile toàn bộ mẫu số, loại bỏ rủi ro rò rỉ mục tiêu (target leakage) và nêu rõ các biến số cần thu thập thêm trước khi triển khai chiến dịch can thiệp thực tế.

---

## 2. Kết quả Phân tích Chính (Executive Summary)

* **Tổng quy mô danh mục:** 10.127 khách hàng trong snapshot.
* **Số lượng rời bỏ:** 1.627 khách hàng được gắn nhãn `Attrited Customer`, tương đương **tỷ lệ rời bỏ danh mục là 16,07%**.
* **Nhóm cảnh báo giao dịch thấp (<40 giao dịch):** Có 1.802 khách hàng với tỷ lệ rời bỏ lên tới **30,08%** (chiếm 33,31% tổng số khách hàng rời bỏ của toàn bộ danh mục).
* **Mức độ suy giảm hoạt động:** Nhóm khách hàng rời bỏ chỉ thực hiện trung bình **44,9 giao dịch/năm**, thấp hơn đáng kể so với mức **68,7 giao dịch/năm** ở nhóm khách hàng đang duy trì (`Existing Customer`).
* **Thời gian ngưng hoạt động:** Tỷ lệ rời bỏ tăng tỷ lệ thuận với số tháng không hoạt động: từ **5,08%** (nhóm 0–1 tháng không hoạt động) tăng vọt lên **24,56%** (nhóm 4+ tháng không hoạt động).
* **Friction tại điểm chạm dịch vụ:** Khách hàng có từ 4 lần liên hệ trở lên có tỷ lệ rời bỏ đạt **26,39%** (gấp đôi nhóm 0-1 lần liên hệ).

---

## 3. Các Sản phẩm Cốt lõi trong Dự án

Dự án được tái cấu trúc tinh gọn theo chuẩn **Lean DA/BA Portfolio**, không lồng ghép thư mục rườm rà:

```text
credit-card-retention-analytics/
├── README.md                           # Báo cáo tổng thể và tài liệu nghiệp vụ
├── credit-card-retention-analytics.pbix # Dashboard Power BI chính (chuẩn 4 trang, sidebar tiện ích)
├── dashboard.html                      # Dashboard Web tương tác (mở xem ngay trên trình duyệt)
├── pipeline.py                         # Pipeline xử lý dữ liệu, nạp SQLite & kiểm toán (Zero dependencies)
├── test_pipeline.py                    # Bộ 16 test cases tự động kiểm tra data integrity & SQL
├── requirements.txt                    # Tối giản, chạy trực tiếp trên thư viện chuẩn Python 3.11+
├── .gitignore                          # Cấu hình git
│
├── data/                               # Dữ liệu nguồn và database
│   ├── BankChurners.csv                # Snapshot 10.127 khách hàng (đã ghim mã SHA-256)
│   └── retention.sqlite                # Cơ sở dữ liệu SQLite đã được chuẩn hóa và lập chỉ mục
│
├── sql/                                # 5 truy vấn SQL phân tích nghiệp vụ chuyên sâu
│   ├── 01_schema.sql                   # Khởi tạo bảng và ràng buộc miền giá trị
│   ├── 02_overview.sql                 # Tính toán KPI tổng quan cấp C-Level
│   ├── 03_segments.sql                 # Phân tích lát cắt phân khúc nhân khẩu học
│   ├── 04_behavior.sql                 # Phân tích dải hành vi giao dịch và tiếp xúc
│   └── 05_investigation_cohort.sql     # Truy vấn trích xuất cohort ưu tiên can thiệp
│
├── notebooks/                          # Jupyter Notebook phục vụ trình diễn EDA
│   └── 01_exploration.ipynb
│
└── reports/                            # Các bảng số liệu kết xuất tự động từ Pipeline
    ├── analysis.md                     # Báo cáo kết quả phân tích sinh tự động
    ├── dashboard-preview.png           # Ảnh chụp mẫu dashboard tổng quan
    ├── segments.csv                    # Thống kê phân khúc
    ├── behavior.csv                    # Thống kê hành vi
    ├── cohorts.csv                     # Dữ liệu cohort
    ├── metrics.json                    # Toàn bộ chỉ số định lượng
    └── quality.json                    # Báo cáo kiểm định chất lượng dữ liệu
```

---

## 4. Power BI Dashboard (`credit-card-retention-analytics.pbix`)

Dashboard được thiết kế theo chuẩn nhận diện **Corporate Banking / Financial Analytics** (tone màu Slate `#1E293B`, Emerald `#0D7A57`, Light Neutral `#F8FAFC`) với **Left Filter Sidebar** chuyên dụng, bao gồm 4 trang:

1. **Executive Overview:** 4 thẻ KPI số lớn, biểu đồ cột dải giao dịch, donut chart trạng thái khách hàng, biểu đồ ngang khách hàng rời bỏ theo thu nhập và bảng tổng hợp hiệu suất hạng thẻ.
2. **Trends And Behavior:** Ma trận 2 chiều giao dịch & không hoạt động, 3 biểu đồ tỷ lệ attrition % và 3 biểu đồ quy mô khách hàng theo từng dải liên hệ.
3. **Retention Action & Offers:** Bảng phân bổ ma trận rủi ro chi tiết, biểu đồ cột phân loại theo số tháng không hoạt động và biểu đồ phân bổ khách hàng rời bỏ theo hạng thẻ tín dụng.
4. **Data Quality & Audit:** Bảng đối soát toàn diện đa chiều (Thu nhập, Hạng thẻ, Giới tính, Tình trạng hôn nhân) kiểm toán mẫu số 10.127 khách hàng và bảo đảm không có ô dữ liệu trống.

> **Trải nghiệm nhanh:** Nếu chưa cài đặt Power BI Desktop, bạn có thể nhấp đúp mở ngay file [dashboard.html](dashboard.html) trên bất kỳ trình duyệt nào để trải nghiệm toàn bộ giao diện dashboard tương tác trực tiếp!

---

## 5. Hướng dẫn Chạy & Kiểm thử Tự động

Dự án sử dụng 100% thư viện chuẩn của Python (Standard Library), không cần cài đặt thêm thư viện ngoài:

```bash
# 1. Chạy pipeline xử lý dữ liệu và xuất báo cáo:
python pipeline.py

# 2. Chạy bộ 16 test cases kiểm toán dữ liệu và logic SQL:
python -m unittest test_pipeline.py -v
```

---

## 6. Góc nhìn Phỏng vấn cho Vị trí DA / BA (Interview Talking Points)

Khi trình bày dự án này với nhà tuyển dụng:

* **Tư duy Nghiệp vụ (Business-oriented):** *"Tôi không chỉ nhìn vào tỷ lệ phần trăm rời bỏ (tỷ lệ cao nhưng mẫu quá nhỏ sẽ gây lãng phí chi phí can thiệp). Tôi kết hợp cả tỷ lệ và quy mô tuyệt đối: ví dụ nhóm thẻ Blue chiếm tới 93,36% lượng khách hàng rời bỏ dù tỷ lệ chỉ 16,1%, do đó các chiến dịch retention diện rộng phải hướng vào nhóm này."*
* **Tính Kỷ luật Dữ liệu (Data Governance):** *"Tôi chủ động loại bỏ 2 cột đầu ra của mô hình Naive Bayes có sẵn trong dataset gốc để tránh rò rỉ mục tiêu (target leakage). Đồng thời tôi bảo lưu giá trị 'Unknown' thay vì tự ý điền khuyết (imputation) để phản ánh đúng thực tế thu thập dữ liệu ngân hàng."*
* **Thận trọng trong Suy luận (Causal vs Association):** *"Vì dữ liệu là snapshot cắt ngang (cross-sectional) thiếu mốc thời gian sự kiện, tôi chỉ đưa ra nhận định về mặt tương quan (association). Trước khi ngân hàng chi ngân sách cho chiến dịch giữ chân, tôi đề xuất chạy thử nghiệm ngẫu nhiên có đối chứng (A/B testing hoặc randomized pilot) để đo lường mức độ nâng tỷ lệ giữ chân thực tế (retention uplift)."*

---

## 7. Nguồn Dữ liệu

* Bộ dữ liệu: [Credit Card Customers trên Kaggle](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers) do tác giả Sakshi Goyal chia sẻ.
* Checksum SHA-256: `c91b525a2a6755a1b0b80dad1d0d008ca97ec4df34552c8f47ffa12b6184b779`.
