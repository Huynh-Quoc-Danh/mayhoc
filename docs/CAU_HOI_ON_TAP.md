# Câu hỏi ôn tập vấn đáp – Nhóm 06

Mỗi người **tự viết câu trả lời bằng lời của mình** ngay dưới câu hỏi (hoặc vào sổ riêng), kèm chỗ chứng minh (notebook / run_id). Câu hỏi đánh dấu tên là người đó bắt buộc trả lời được; tất cả đều nên trả lời được câu ở mục A.

## A. Hiểu bài toán (cả nhóm)
1. Bài toán là gì? Input là gì, output là gì? Vì sao là phân loại đa lớp + phân cụm?
2. Một offer, một merchant, một cluster (sản phẩm thực) khác nhau thế nào? Cho ví dụ từ dữ liệu.
3. Vì sao dùng Macro-F1 làm độ đo chính chứ không phải Accuracy?
4. Kết quả cuối cùng của nhóm là bao nhiêu? Lấy ở đâu ra (run_id, notebook)?
5. Hệ thống này dùng thực tế để làm gì? Hạn chế lớn nhất là gì?

## B. Dữ liệu & EDA (Lộc chính)
1. Bộ dữ liệu có bao nhiêu mẫu, cột, lớp, merchant, cluster? Mỗi con số tính bằng ô code nào?
2. Lớp nào nhiều nhất / ít nhất? Tỷ lệ mất cân bằng bao nhiêu? Có cần cân bằng lại không, vì sao?
3. Vì sao có tiêu đề như "k hlschrank"? Ảnh hưởng gì đến mô hình?
4. Bao nhiêu % tiêu đề có mã model chữ-số? Điều đó gợi ý dùng đặc trưng gì?
5. Ma trận Jaccard nói lên điều gì? Nó dự báo đúng lỗi của mô hình không?
6. `clean_title` giữ lại gì, bỏ gì, vì sao không bỏ số?
7. Thay đổi min_df / n-gram ảnh hưởng thế nào trong thí nghiệm của bạn (dẫn run_id)?

## C. Đặc trưng & mô hình chọn (Danh chính)
1. TF-IDF là gì? `sublinear_tf` làm gì? N-gram ký tự `char_wb (3,5)` khác n-gram từ thế nào?
2. Ablation của bạn cho thấy đặc trưng nào giúp nhiều nhất? Bao nhiêu điểm? Vì sao?
3. Vì sao chọn LinearSVC (hoặc mô hình cuối của nhóm)? Tham số C có ý nghĩa gì, bạn chọn C bao nhiêu, dựa trên lần chạy nào?
4. Target encoding P(ngành | merchant) là gì? Rủi ro rò rỉ dữ liệu ở đâu và nhóm xử lý thế nào?
5. Group split theo Cluster ID là gì? Vì sao F1 giảm? Mô hình nào giảm nhiều nhất, vì sao?
6. Pipeline chống rò rỉ dữ liệu như thế nào (fit ở đâu, transform ở đâu)?

## D. Mô hình cây, boosting & lỗi (Nhân chính)
1. Vì sao Decision Tree kém trên TF-IDF? Vì sao phải nén bằng SVD trước khi dùng cây?
2. Random Forest và XGBoost khác nhau thế nào (bagging vs boosting)? Kết quả XGBoost thật của bạn so với HistGradientBoosting giữa kỳ?
3. Tham số max_depth / learning_rate / n_estimators ảnh hưởng ra sao trong nhật ký của bạn?
4. Lỗi còn lại của mô hình cuối rơi vào những lớp nào? Nguyên nhân chính (có đếm)?
5. Hình mẫu đầu vào → đầu ra trong slide sinh ra từ ô nào?

## E. Phân cụm (Thịnh chính)
1. Vì sao phải TF-IDF → SVD → chuẩn hóa L2 trước K-Means?
2. Silhouette, Davies-Bouldin, ARI, NMI đo cái gì? Giá trị của nhóm nghĩa là tốt hay xấu?
3. Vì sao K = 10? Elbow/Silhouette của bạn cho thấy gì?
4. DBSCAN/HDBSCAN cho bao nhiêu % điểm nhiễu? Vì sao Silhouette cao nhưng ARI thấp?
5. Hình t-SNE nói lên điều gì? Có kết luận được khoảng cách trên t-SNE không?

## F. Truy vết hình & số liệu (ai cũng phải làm được)
- Chỉ vào **bất kỳ hình nào** trong báo cáo/slide → nói được: file hình, notebook, ô code, ai chạy, ngày chạy, ý nghĩa (tra `figures/FIGURE_INDEX.csv`).
- Chỉ vào **bất kỳ con số nào** → mở được nhật ký / notebook chứa số đó.
