# Nhật ký làm việc – nhan

> Mỗi ngày viết 3 dòng bằng lời của mình. Ghi run_id để đối chiếu với experiment_log.csv.

| Ngày | Đã làm (run_id / commit) | Kết quả chính | Nhận xét – rút ra – ngày mai làm gì |
|---|---|---|---|
| 12/11 | Cài môi trường, tạo nhánh nhan. Chạy tai_lap_E02 (nhan_20261112_141200), dt_depth50 (nhan_20261112_153041), dt_leaf3 (nhan_20261112_153114), xgb_lan_dau (nhan_20261112_153316) | E02 chạy lại ra 0.9408, đúng giữa kỳ. depth 50 ra 0.918, leaf 3 ra 0.932. XGBoost ra 0.9771 | Giới hạn cây đều làm tệ hơn. XGBoost hơn cây đơn nhiều. Bị lỗi pandas 3 nên phải cài lại pandas bản 2. Mai thử Random Forest. |
| 13/11 | Notebook 06: dt_d20 (nhan_20261113_212725), dt_d100 (nhan_20261113_212916), dt_dNone (nhan_20261113_213047), rf_100 (nhan_20261113_214140), rf_300 (nhan_20261113_214408). Dùng đặc trưng svd 150 | Cây: depth 20 ra 0.932, depth 100 và None ra 0.9406. Random Forest: 100 cây ra 0.9716, 300 cây ra 0.9732 | depth 100 với None giống nhau vì cây chỉ sâu khoảng 37 tầng. Random Forest hơn cây đơn khoảng 3 điểm, 300 cây không hơn 100 bao nhiêu. Mai chỉnh XGBoost và thử max_features cho Random Forest. |
| 14/11 | Chỉnh XGBoost: xgb_d3 (nhan_20261114_170832), xgb_d6 (nhan_20261114_170957), xgb_d9 (nhan_20261114_171244), xgb_lr005 (nhan_20261114_171419), xgb_lr03 (nhan_20261114_171516), xgb_svd150 (nhan_20261114_171811). Vẽ hình so sánh 3 mô hình cây (mục 7 notebook 06, nhan_so_sanh_mo_hinh_cay.png) | depth 3 = 0.969, depth 6 = 0.9771, depth 9 = 0.9778; lr 0.05 = 0.9757, lr 0.3 = 0.9776; svd 150 = 0.9783 (tốt nhất) | XGBoost hơn Random Forest (0.9732) khoảng 0,5 điểm nhưng vẫn thua SVM (0.9929). Cây sâu hơn thì tốt hơn, lr 0.1 là vừa. Mai làm phân tích lỗi (mục 4). |

## Câu hỏi tự trả lời

**12/11 – Giới hạn độ sâu làm cây tốt hơn hay kém hơn? Vì sao?**

Kém hơn. Cây mặc định được 0.9408, đặt max_depth 50 còn 0.918, min_samples_leaf 3 còn 0.932. Lúc đầu em nghĩ giới hạn sẽ đỡ học thuộc, nhưng xem điểm trên tập train thì depth 50 chỉ còn khoảng 0.94, tức là cây chưa học đủ. Đặc trưng word có hơn 30 nghìn cột, mỗi lần tách cây chỉ hỏi tiêu đề có chữ nào đó hay không, nên phải hỏi rất nhiều lần (cây sâu tới hơn 200 tầng) mới phân loại được. Cắt ngắn thì nhiều mẫu bị đoán sai.

**12/11 – Vì sao cây đơn kém hơn SVM trên dữ liệu văn bản?**

SVM xét tất cả các chữ trong tiêu đề cùng lúc, chữ nào cũng có trọng số rồi cộng lại. Cây thì đi từng bước, mỗi bước chỉ xét 1 chữ nên bỏ qua nhiều thông tin. Dữ liệu chữ có rất nhiều cột mà mỗi tiêu đề chỉ có vài chữ, cây dễ bị học thuộc mấy chữ hiếm. Mấy lớp tủ lạnh lại có nhiều chữ giống nhau nên cần xét nhiều chữ một lúc mới phân biệt được.

**12/11 – XGBoost so với HistGradientBoosting giữa kỳ?**

XGBoost được 0.9771, thua HGB giữa kỳ (0.9793) một chút. Hai cái đều là boosting nên ra gần nhau. Em chạy XGBoost 200 cây và nén còn 100 chiều nên chắc bị mất bớt thông tin.

**13/11 – Giới hạn độ sâu có giúp cây tránh quá khớp không?**

Không giúp. Với svd 150 chiều, depth 20 còn tệ hơn (0.932) so với không giới hạn (0.9406). depth 100 và None ra giống hệt vì cây tự mọc chỉ sâu khoảng 37 tầng.

**13/11 – Ghép nhiều cây (Random Forest) cải thiện bao nhiêu so với một cây?**

Khoảng 3 điểm: từ 0.9406 lên 0.9716 (100 cây) và 0.9732 (300 cây). Mấy lớp tủ lạnh lên nhiều nhất, Fridges với Freezers từ khoảng 0.84-0.86 lên khoảng 0.93. Lý do là mỗi cây học trên một phần dữ liệu khác nhau rồi bỏ phiếu, cây sai thì cây khác bù.

**14/11 – XGBoost tốt nhất đạt bao nhiêu, có vượt Random Forest và bắt kịp SVM không?**

XGBoost tốt nhất là 0.9783 (depth 9, lr 0.1, svd 150). Có vượt Random Forest (0.9732) nhưng chỉ khoảng 0,5 điểm, còn so với SVM (0.9929) thì vẫn thua khoảng 1,5 điểm. Em nghĩ lý do là mô hình cây phải dùng SVD nén chữ lại, làm mất mấy chi tiết nhỏ như mã model, mà mấy lớp tủ lạnh lại cần đúng mấy chi tiết đó để phân biệt. SVM dùng thẳng n-gram nên giữ được.
