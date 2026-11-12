# Nhật ký làm việc – thinh

Ngày 12/11
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
---

## 3. Nhật ký ngày 12/11/2026

- **Đã làm:** chạy K-Means K=10, 8, 12 trên SVD-50 (run_id: thinh_20261112_184246, thinh_20261112_185129, thinh_20261112_185303); điền nhận xét vào cluster_log.csv; xuất HTML notebook 07 (runs/07_Thinh_20261112.html).
- **Kết quả chính:** NMI 0.703 / 0.651 / 0.685; ARI 0.564 / 0.455 / 0.514; Silhouette 0.294 / 0.268 / 0.305 (K=10 / 8 / 12).
- **Nhận xét:** K=10 tốt nhất vì bằng đúng số ngành. Silhouette tăng theo K (cụm nhỏ thì chặt hơn) nên không dùng để chọn K, phải dựa vào NMI/ARI. NMI thấp hơn giữa kỳ (0.73) do TF-IDF trong notebook thiếu min_df=2, sublinear_tf=True và token_pattern giữ mã model.
- **Ngày mai:** sửa TF-IDF giống bản giữa kỳ, quét K từ 6 đến 20, thử SVD 100 và 150.
