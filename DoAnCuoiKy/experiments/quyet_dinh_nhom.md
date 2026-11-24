# Quyết định của nhóm

Ghi lại các quyết định chung của Nhóm 06 và căn cứ số liệu (lấy từ nhật ký thí nghiệm của từng người).

## 1. Cấu hình tốt nhất của từng người

| Thành viên | Nhánh mô hình | Cấu hình tốt nhất | run_id | Kết quả |
|---|---|---|---|---|
| Danh | LinearSVC | hybrid word (1,2) + char (2,4), C=3 | danh_20261113_170944 | Test F1 0.9929; CV 0.9909 ± 0.0013; Group 0.9875 |
| Lộc | Logistic Regression | hybrid char (2,4), C=100 | loc_20261114_175918 | Test F1 0.9909; CV 0.9875 ± 0.0016; Group 0.9851 |
| Lộc | MultinomialNB | hybrid char (2,4), alpha=0.03 | loc_20261114_175845 | Test F1 0.9869; CV 0.9861 ± 0.0014; Group 0.9819 |
| Nhân | XGBoost | SVD 100, 400 cây, depth 9, lr 0.1 | nhan_20261115_181114 | Test F1 0.9789; CV 0.9754 ± 0.0015 |
| Thịnh | K-Means | SVD 50, K=10 | thinh_20261113_214111 | NMI 0.7318; ARI 0.623 |
| Thịnh | DBSCAN / HDBSCAN | eps 0.5, min_samples 5 / min_cluster_size 100 | thinh_20261115_232258 / thinh_20261115_232435 | NMI 0.554 / 0.533 |

## 2. Các quyết định đã chốt (18/11/2026)

- **Mô hình phân loại cuối:** LinearSVC C=3, đặc trưng hybrid TF-IDF word (1,2) + char (2,4) (danh_20261113_170944) – cả nhóm đồng ý.
- **Thuật toán phân cụm:** K-Means trên SVD 50 chiều, K=10 (thinh_20261113_214111) – cả nhóm đồng ý.
- **Báo cáo:** viết chung trên Google Docs, mỗi người viết đúng chương của mình theo docs/DAN_Y_BAO_CAO.md, xong nháp trước 20/11.
- **Đọc chéo:** Danh đọc Ch.2–3 của Lộc, Lộc đọc Ch.6 của Nhân, Nhân đọc Ch.7 của Thịnh, Thịnh đọc Ch.5 của Danh.

## 3. Bảng đóng góp (chốt trước khi nộp, tổng = 100%)

| Thành viên | MSSV | Vai trò | Phần đã làm | % đóng góp |
|---|---|---|---|---|
| Huỳnh Quốc Danh | 3124411050 | Nhóm trưởng; mô hình LinearSVC | Lập kế hoạch, phân công hằng ngày, merge PR; dựng khung code và ghi nhật ký thí nghiệm (run_experiment, thư mục kết quả runs/), notebook EDA và baseline giữa kỳ, web demo Streamlit; LinearSVC: ablation đặc trưng, quét n-gram ký tự và C, 5-fold CV, Group split, đường cong học, thử chuẩn hóa từ mất dấu, chốt mô hình cuối (Test Macro-F1 0.9929); sơ đồ tổng thể (draw.io); viết Ch.1, 4.2, Ch.5, Ch.8; rà soát, thống nhất định dạng báo cáo; slide 1, 2, 6, 7, 8, 15 | 25% |
| Huỳnh Tấn Lộc | 3124411158 | Tiền xử lý, Naive Bayes, Logistic Regression | Hàm làm sạch tiêu đề, TF-IDF từ và n-gram ký tự; Naive Bayes, ComplementNB, Logistic Regression (alpha, C, class_weight, 5-fold CV, Group split); giải thích đặc trưng quan trọng của LR; sơ đồ tiền xử lý (draw.io); viết Ch.2, Ch.3, 4.1; kiểm tra chạy lại từ bản clone mới và viết hướng dẫn chạy lại trong README; đọc chéo Ch.6; slide 3, 4, 5 | 25% |
| Mai Tấn Thiện Nhân | 3124411196 | Mô hình cây, XGBoost, phân tích lỗi | Decision Tree, Random Forest, XGBoost (SVD 100, 400 cây, depth 9: Test 0.9789, CV 0.9754); so sánh 7 mô hình; phân tích 47 lỗi của mô hình cuối và lỗi của XGBoost; sơ đồ XGBoost (draw.io); viết 4.3, Ch.6; tạo mô hình và quay video web demo; slide 9, 10, 11, 14 | 25% |
| Nguyễn Vĩnh Thịnh | 3124411292 | Phân cụm | K-Means (quét K, số chiều SVD, 5 seed), MiniBatch K-Means, Agglomerative, DBSCAN, HDBSCAN; t-SNE và độ thuần cụm theo ngành (K-Means K = 10: NMI 0.7318, ARI 0.623); sơ đồ phân cụm (draw.io); viết 4.4, Ch.7; slide 12, 13 | 25% |
| **Tổng** | | | | **100%** |
