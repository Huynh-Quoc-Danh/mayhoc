# Biên bản họp nhóm

## Họp 1 – 18/11/2026 (họp qua tin nhắn nhóm Zalo, dời từ 16/11)
- Thời gian: khoảng 21:35 ngày 18/11/2026 – Hình thức: nhóm trưởng gửi số liệu và 4 đề xuất vào nhóm Zalo, các thành viên trả lời bằng tin nhắn – Tham gia: Danh, Lộc, Nhân, Thịnh
- Lý do dời: chưa sắp xếp được lịch họp ngày 16/11 (laptop nhóm trưởng bị hỏng).

Cấu hình tốt nhất của mỗi người (số liệu lấy từ nhật ký thí nghiệm):

| Thành viên | Nhánh mô hình | Cấu hình tốt nhất | run_id | Kết quả |
|---|---|---|---|---|
| Danh | LinearSVC | hybrid word (1,2) + char (2,4), C=3 | danh_20261113_170944 | Test F1 0.9929; CV 0.9909 ± 0.0013; Group 0.9875 |
| Lộc | Logistic Regression | hybrid char (2,4), C=100 | loc_20261114_175918 | Test F1 0.9909; CV 0.9875 ± 0.0016; Group 0.9851 |
| Lộc | MultinomialNB | hybrid char (2,4), alpha=0.03 | loc_20261114_175845 | Test F1 0.9869; CV 0.9861 ± 0.0014; Group 0.9819 |
| Nhân | XGBoost | SVD 100, 400 cây, depth 9, lr 0.1 | nhan_20261115_181114 | Test F1 0.9789; CV 0.9754 ± 0.0015 |
| Thịnh | K-Means | SVD 50, K=10 | thinh_20261113_214111 | NMI 0.7318; ARI 0.623 |
| Thịnh | DBSCAN / HDBSCAN | eps 0.5, min_samples 5 / min_cluster_size 100 | thinh_20261115_232258 / thinh_20261115_232435 | NMI 0.554 / 0.533 |

- Ý kiến: cả 4 thành viên đồng ý cả 4 đề xuất, không có ý kiến khác.
- **Quyết định mô hình phân loại cuối:** LinearSVC C=3, đặc trưng hybrid TF-IDF word (1,2) + char (2,4) (danh_20261113_170944) – 4/4 đồng ý.
- **Quyết định thuật toán phân cụm:** K-Means trên SVD 50 chiều, K=10 (thinh_20261113_214111) – 4/4 đồng ý.
- Việc tiếp theo: báo cáo viết chung trên Google Docs, mỗi người viết đúng chương của mình theo docs/DAN_Y_BAO_CAO.md, xong nháp trước 20/11; họp 2 ngày 19/11 để đọc chéo (Danh đọc Ch.2–3 của Lộc, Lộc đọc Ch.6 của Nhân, Nhân đọc Ch.7 của Thịnh, Thịnh đọc Ch.5 của Danh).
- Minh chứng: ảnh chụp tin nhắn nhóm Zalo – docs/bien_ban/hop1_zalo.png (nhóm trưởng bổ sung).

## Họp 2 – 19/11/2026 (đọc chéo báo cáo)

## Họp 3 – 21/11/2026 (tập vấn đáp, chốt % đóng góp)
| Thành viên | MSSV | Vai trò | Phần đã làm | % đóng góp |
|---|---|---|---|---|
| Huỳnh Quốc Danh | 3124411050 | Nhóm trưởng | | |
| Huỳnh Tấn Lộc | | | | |
| Mai Tấn Thiện Nhân | | | | |
| Nguyễn Vĩnh Thịnh | | | | |
| **Tổng** | | | | **100%** |
