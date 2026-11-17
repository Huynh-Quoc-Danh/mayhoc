# Dàn ý báo cáo cuối kỳ – Nhóm 06 (bản nháp để nhóm rà lại)

Đề tài: Product Classification and Clustering (PriceRunner, UCI #837) – 35.311 tiêu đề sản phẩm, 10 ngành.

Bản nháp này chỉ chốt **ai viết chương nào, dùng số liệu và hình nào**. Nội dung các chương do người phụ trách **tự viết** từ notebook và nhật ký của mình. Nhóm sửa dàn ý ở họp 2 (19/11).

| Chương | Người viết | Nội dung chính | Số liệu (run_id / file) | Hình (thư mục `figures/`) |
|---|---|---|---|---|
| 1. Giới thiệu | Danh | Bài toán phân loại ngành từ tiêu đề; 2 câu hỏi nghiên cứu (đặc trưng nào giúp phân loại; dữ liệu có tự gom cụm theo ngành không); đóng góp của nhóm; bố cục báo cáo | – | – |
| 2. Dữ liệu và EDA | Lộc | Mô tả dữ liệu (cột, số mẫu, 10 ngành); độ dài tiêu đề; từ vựng chồng lấp giữa các ngành; merchant và Cluster ID | notebook 01_EDA | eda_01 → eda_08 |
| 3. Tiền xử lý và đặc trưng | Lộc | Hàm `clean_title`; TF-IDF word (1,2) và char_wb (2,4); so sánh word / char / hybrid / full; giải thích đặc trưng quan trọng (mã model KG/KI…) | loc_*, danh_20261112_* (ablation), lr_giai_thich (mục 10 notebook 04, PR #41) | method_pipeline.png, loc_so_do_tien_xu_ly.jpg (vẽ tay), loc_dac_trung_quan_trong.png |
| 4. Các mô hình | cả nhóm | 4.1 NB, LR (Lộc) · 4.2 LinearSVC (Danh) · 4.3 Cây quyết định, Random Forest, XGBoost (Nhân) · 4.4 K-Means, Agglomerative, DBSCAN, HDBSCAN (Thịnh). Mỗi mục: ý tưởng, tham số chính, ưu/nhược | – | – |
| 5. Thực nghiệm phân loại và chọn mô hình | Danh | Thiết kế thí nghiệm (Stratified 80/20, 5-fold CV, Group split theo Cluster ID); quét n-gram ký tự và C; mô hình cuối; đường cong học; thử chuẩn hóa từ mất dấu (không cải thiện) | danh_20261113_170944 (cuối), danh_20261113_231233 (group), danh_20261115_151800, learning_curve.csv | danh_cm_mo_hinh_cuoi.png, danh_learning_curve.png |
| 6. So sánh mô hình và phân tích lỗi | Nhân | Bảng 7 mô hình tốt nhất; F1 3 ngành làm lạnh; SVM 47 lỗi vs XGBoost 147 lỗi (38 lỗi chung); phân tích 47 lỗi của mô hình cuối (mục 8.1 notebook 05) và 30 lỗi của XGBoost | nhan_20261115_181114, loi_mo_hinh_cuoi.csv, loi_xgb_30_mau.csv | nhan_tong_hop_ca_nhom.png, nhan_so_sanh_mo_hinh_cay.png, nhan_dau_vao_dau_ra.png, loc_so_sanh_tuyen_tinh.png |
| 7. Phân cụm | Thịnh | Quét K, số chiều SVD; MiniBatch; Agglomerative; DBSCAN/HDBSCAN và bài học về Silhouette; t-SNE; cụm nào khớp ngành nào | cluster_log.csv (thinh_20261113_214111 tốt nhất) | thinh_kmeans_quet_K.png, thinh_so_sanh_svd.png, thinh_k_distance.png, thinh_so_sanh_thuat_toan.png (+ hình t-SNE, cụm–ngành khi có) |
| 8. Kết luận | Danh | Trả lời 2 câu hỏi nghiên cứu; hạn chế (nhãn nhiễu, tiêu đề chỉ có mã model, Freezers); hướng phát triển; web demo | – | demo_15-11.png (thư mục docs) |

## Quy ước chung

- Mọi con số trong báo cáo phải tra được run_id trong nhật ký `experiments/<tên>/`.
- Mọi hình phải có dòng trong `figures/FIGURE_INDEX.csv` (cột y_nghia đã điền).
- Hình vẽ tay chụp rõ, để trong `docs/hinh_ve_tay/`.
- Mỗi người tự viết phần của mình; Danh ghép và thống nhất định dạng.
