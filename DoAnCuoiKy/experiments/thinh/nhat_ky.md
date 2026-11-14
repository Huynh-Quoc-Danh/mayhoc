# Nhật ký làm việc 12/11
## 1. Kết quả quét các giá trị K (K-Means)
- **K = 8:** 
  - Silhouette: 0.2675
  - ARI: 0.4554
  - NMI: 0.6509
- **K = 10:** 
  - Silhouette: 0.2936
  - ARI: 0.5636
  - NMI: 0.7026
- **K = 12:** 
  - Silhouette: 0.3051
  - ARI: 0.5136
  - NMI: 0.6848

---

## 2. Trả lời câu hỏi tự luận
- **Silhouette, ARI, NMI thay đổi thế nào khi K tăng?**
  - Khi $K$ tăng (từ 8 lên 10 rồi 12):
    - Chỉ số **Silhouette** có sự biến động tăng nhẹ (từ ~0.267 lên ~0.305).
    - Các chỉ số đánh giá so với nhãn thật (**ARI** và **NMI**) đạt giá trị cao nhất tại $K = 10$ (với NMI $\approx 0.7026$, ARI $\approx 0.5636$) rồi sau đó giảm xuống khi $K = 12$. Điều này cho thấy $K = 10$ là điểm cân bằng phù hợp nhất với cấu trúc số lượng ngành thực tế của dữ liệu.

- **Chỉ số nào nên dùng để chọn K, vì sao?**
  - Nên dùng **NMI (Normalized Mutual Information)** làm chỉ số chính để chọn $K$ vì bài toán có sẵn nhãn ground-truth (nhãn ngành hàng), giúp đo lường chính xác mức độ khớp và khả năng khôi phục cấu trúc phân loại thực tế của dữ liệu văn bản. Kết hợp thêm **Silhouette** để kiểm tra độ tách rời về mặt hình học.
### Nhật ký ngày 12/11/2026

- **Đã làm:** chạy K-Means K=10, 8, 12 trên SVD-50 (run_id: thinh_20261112_184246, thinh_20261112_185129, thinh_20261112_185303); điền nhận xét vào cluster_log.csv; xuất HTML notebook 07 (runs/07_Thinh_20261112.html).
- **Kết quả chính:** NMI 0.703 / 0.651 / 0.685; ARI 0.564 / 0.455 / 0.514; Silhouette 0.294 / 0.268 / 0.305 (K=10 / 8 / 12).
- **Nhận xét:** K=10 tốt nhất vì bằng đúng số ngành. Silhouette tăng theo K (cụm nhỏ thì chặt hơn) nên không dùng để chọn K, phải dựa vào NMI/ARI. NMI thấp hơn giữa kỳ (0.73) do TF-IDF trong notebook thiếu min_df=2, sublinear_tf=True và token_pattern giữ mã model.
- **Ngày mai:** sửa TF-IDF giống bản giữa kỳ, quét K từ 6 đến 20, thử SVD 100 và 150.
# Nhật ký thí nghiệm - Nguyễn Vĩnh Thịnh
## Ngày 13/11/2026

### 1. Công việc đã thực hiện (Run ID & Tasks)
- **Mở môi trường và cập nhật code:** Chuyển sang nhánh `thinh`, pull code mới nhất và kích hoạt môi trường ảo Python thành công.
- **Sửa lỗi TF-IDF trong notebook 07:** 
  - Bổ sung tham số `token_pattern=r"(?u)\b[\w\-\.\+]+\b"` vào `TfidfVectorizer` trong notebook `07_Thinh_PhanCum.ipynb` để giữ nguyên định dạng các mã model (như `lwf28441w`, `5.5`, `a+`).
  - Đính chính nhận xét ngày 12/11: Khác biệt duy nhất với bản giữa kỳ là thiếu `token_pattern`.
- **Chạy kiểm tra và quét K-Means:** 
  - Chạy lại mô hình với $K=10$ để đối chiếu.
  - Thực hiện quét vòng lặp K từ 6 đến 20 (bước nhảy 2) với SVD-50 (`thinh_20261113_...`).
- **Trực quan hóa và lưu kết quả:** 
  - Vẽ đồ thị biểu diễn các chỉ số Silhouette, ARI, và NMI theo các giá trị $K$.
  - Lưu hình ảnh vào thư mục `figures\thinh_kmeans_quet_K.png` và cập nhật cột ý nghĩa vào `figures\FIGURE_INDEX.csv`.
- **Tổng kết & Báo cáo:** Cập nhật nhật ký thí nghiệm lên Google Sheets, xuất file HTML báo cáo (`07_Thinh_PhanCum_20261113.html`), thực hiện git commit/push và tạo Pull Request lên GitHub.

### 2. Kết quả chính
- **Phục hồi chỉ số NMI:** Sau khi sửa xong `token_pattern` cho TF-IDF, giá trị NMI tại $K=10$ đã tăng lên và đạt đúng mức **`0.7318`**, khôi phục chính xác kết quả của bản giữa kỳ.
- **Xác định K tối ưu:** Qua biểu đồ quét $K$ từ 6 đến 20, $K=10$ là giá trị tối ưu nhất khi đạt đỉnh NMI (`0.7318`) và ARI (`0.622`).

### 3. Nhận xét & Rút ra
- **Động thái của các chỉ số:** Chỉ số NMI và ARI đạt đỉnh ở khoảng $K=10$ rồi giảm dần khi $K$ lớn hơn do hiện tượng phân rã cụm quá mức (over-segmentation) so với nhãn gốc. Ngược lại, chỉ số Silhouette tiếp tục tăng dần khi $K$ lớn (đạt cao nhất ở $K=20$), do đặc trưng không gian văn bản thưa thớt ưa chuộng các cụm nhỏ gọn về mặt khoảng cách hình học.
- **Quyết định:** Khẳng định lựa chọn $K=10$ làm tham số chuẩn cho các bước phân cụm tiếp theo.

### 4. Kế hoạch ngày mai
- Tiếp tục thực hiện các bước phân cụm nâng cao tiếp theo theo phân công của nhóm.
## Nhật ký ngày 14/11/2026
- **Đã làm:** Đẩy notebook 07 và hình quét K còn thiếu của ngày 13/11 lên GitHub; chạy thực nghiệm so sánh số chiều SVD (50, 100, 150) giữa K-Means và MiniBatch K-Means (K=10); chạy thực nghiệm Agglomerative Clustering với 3 kiểu liên kết (ward, average, complete) trên mẫu 6.000 điểm.
- **Kết quả chính:** Với K-Means, SVD 50 đạt NMI cao nhất (0.7318), giảm dần khi tăng chiều lên 100 (0.6916) và 150 (0.6692). MiniBatch K-Means cho tốc độ nhanh hơn với kết quả tương đương. Ở Agglomerative Clustering, liên kết `average` đạt NMI tốt nhất (0.6532), kế đến là `ward` (0.6126), còn `complete` thấp nhất (0.2478).
- **Nhận xét:** Không gian giảm chiều SVD 50 giữ lại đặc trưng cô đọng nhất cho dữ liệu văn bản, việc tăng thêm chiều đưa thêm nhiễu làm giảm NMI. Thuật toán K-Means với SVD 50 vẫn vượt trội hoàn toàn so với Agglomerative Clustering trên tập dữ liệu này.
- **Ngày mai:** Thử nghiệm thuật toán phân cụm dựa trên mật độ DBSCAN/HDBSCAN (Mục 3) để kiểm tra khả năng phát hiện cụm tự nhiên và lọc nhiễu.