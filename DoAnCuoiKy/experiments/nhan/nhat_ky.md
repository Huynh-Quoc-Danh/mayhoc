# Nhật ký làm việc – nhan

> Mỗi ngày viết 3 dòng bằng lời của mình. Ghi run_id để đối chiếu với experiment_log.csv.

| Ngày | Đã làm (run_id / commit) | Kết quả chính | Nhận xét – rút ra – ngày mai làm gì |
|---|---|---|---|
| 12/11 | Cài môi trường, tạo nhánh nhan. Chạy tai_lap_E02 (nhan_20261112_141200), dt_depth50 (nhan_20261112_153041), dt_leaf3 (nhan_20261112_153114), xgb_lan_dau (nhan_20261112_153316) | E02 chạy lại ra 0.9408, đúng giữa kỳ. depth 50 ra 0.918, leaf 3 ra 0.932. XGBoost ra 0.9771 | Giới hạn cây đều làm tệ hơn. XGBoost hơn cây đơn nhiều. Bị lỗi pandas 3 nên phải cài lại pandas bản 2. Mai thử Random Forest. |
| 13/11 | Notebook 06: dt_d20 (nhan_20261113_212725), dt_d100 (nhan_20261113_212916), dt_dNone (nhan_20261113_213047), rf_100 (nhan_20261113_214140), rf_300 (nhan_20261113_214408). Dùng đặc trưng svd 150 | Cây: depth 20 ra 0.932, depth 100 và None ra 0.9406. Random Forest: 100 cây ra 0.9716, 300 cây ra 0.9732 | depth 100 với None giống nhau vì cây chỉ sâu khoảng 37 tầng. Random Forest hơn cây đơn khoảng 3 điểm, 300 cây không hơn 100 bao nhiêu. Mai chỉnh XGBoost và thử max_features cho Random Forest. |
| 14/11 | Chỉnh XGBoost: xgb_d3 (nhan_20261114_170832), xgb_d6 (nhan_20261114_170957), xgb_d9 (nhan_20261114_171244), xgb_lr005 (nhan_20261114_171419), xgb_lr03 (nhan_20261114_171516), xgb_svd150 (nhan_20261114_171811). Vẽ hình so sánh 3 mô hình cây (mục 7 notebook 06, nhan_so_sanh_mo_hinh_cay.png) | depth 3 = 0.969, depth 6 = 0.9771, depth 9 = 0.9778; lr 0.05 = 0.9757, lr 0.3 = 0.9776; svd 150 = 0.9783 (tốt nhất) | XGBoost hơn Random Forest (0.9732) khoảng 0,5 điểm nhưng vẫn thua SVM (0.9929). Cây sâu hơn thì tốt hơn, lr 0.1 là vừa. Mai làm phân tích lỗi (mục 4). |
| 15/11 | Quét số cây XGBoost: xgb_n100 (nhan_20261115_180610), xgb_n400 (nhan_20261115_180737). CV 5-fold: cv_xgb_best (nhan_20261115_181114). Làm mục 8 notebook 06: bảng và hình tổng hợp cả nhóm | 100 cây = 0.9761, 400 cây = 0.9789 (tốt nhất). CV = 0.9754 ± 0.0015. Xếp hạng cả nhóm: SVM 0.9930 > LR 0.9909 > NB 0.9869 > CNB 0.9857 > XGB 0.9789 > RF 0.9732 > DT 0.9408 | Thêm cây có giúp. XGBoost vẫn thua SVM khoảng 1,5 điểm kể cả khi CV. 3 ngành làm lạnh khó với mọi mô hình. |
| 16/11 | Họp nhóm 1: trình bày phần mô hình cây (XGBoost tốt nhất 0.9789, CV 0.9754, xếp hạng 7 mô hình). Mục 9 notebook 06: chạy lại svm_doi_chieu (nhan_20261116_160058) và xgb_doi_chieu (nhan_20261116_160135), so lỗi, phân loại 30 mẫu (loi_xgb_30_mau.csv), vẽ hình đầu vào đầu ra | SVM sai 47, XGBoost sai 147. Cả hai sai 38, chỉ XGBoost sai 109, chỉ SVM sai 9. Trong 30 mẫu: chỉ có mã model 18, có từ khóa mà vẫn sai 5, tiếng Đức lỗi dấu 6, nhãn sai 1 | XGBoost thua SVM chủ yếu vì SVD làm mất mã model. Nhầm giữa 3 ngành lạnh vẫn nhiều nhất. |
| 17/11 | Vẽ sơ đồ XGBoost bằng draw.io (docs/hinh_ve_tay/nhan_so_do_xgboost.jpg): quy trình và so sánh boosting với bagging. Viết mục 10 notebook 06 tổng kết nhánh mô hình cây. Bắt đầu báo cáo report/nhap/BaoCao_Nhan.docx, viết xong 6.1 và 6.2 | Bảng 6.1: SVM 0.9930 > LR 0.9909 > NB 0.9869 > CNB 0.9857 > XGB 0.9789 > RF 0.9732 > DT 0.9408, có run_id từng dòng | Freezers chỉ thấp nhất ở SVM, LR, CNB; mô hình cây và NB thì Fridges thấp nhất. Mai viết tiếp 6.3, 6.4 và mục 4.3. |
| 18/11 | Viết nốt báo cáo report/nhap/BaoCao_Nhan.docx: mục 4.3 (DT, RF, XGBoost, bagging vs boosting, bảng tinh chỉnh) và 6.3-6.5 (47 lỗi mô hình cuối, so lỗi SVM 47 / XGBoost 147, tổng kết). Sửa sơ đồ draw.io: TF-IDF khoảng 90.000 cột chứ không phải 68.000, bỏ tên trên tiêu đề hình. Danh chốt dùng draw.io nên không vẽ tay | Báo cáo đủ 4.3 và 6.1-6.5, không còn chữ xám, số nào cũng có run_id | Lỗi của mô hình cuối chủ yếu do dữ liệu (mã model, nhãn sai, tiếng Đức mất dấu), đổi mô hình khó cải thiện thêm. |

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

**15/11 – Thêm cây có giúp XGBoost không? Xếp hạng cuối cùng và ngành nào khó với mọi mô hình?**

Có giúp: 100 cây được 0.9761, 200 cây 0.9778, 400 cây 0.9789. Thời gian tăng theo số cây nhưng 400 cây vẫn chỉ khoảng 33 giây nên đáng. Xếp hạng cả nhóm từ cao xuống: SVM, LR, NB, ComplementNB, XGBoost, Random Forest, Decision Tree, mô hình tuyến tính đều đứng trên mô hình cây. 3 ngành Fridges, Freezers, Fridge Freezers luôn thấp nhất ở mọi mô hình, vì tên ngành và từ ngữ trong tiêu đề trùng nhau nhiều.


**16/11 – Vì sao XGBoost thua SVM? Lỗi thêm nằm ở ngành nào, do đâu?**

Trên cùng tập test, XGBoost sai 147 mẫu, SVM sai 47. Gần hết mẫu SVM sai thì XGBoost cũng sai, còn XGBoost sai thêm 109 mẫu. Khoảng một nửa số lỗi thêm là nhầm qua lại giữa Fridges, Freezers, Fridge Freezers. Em đọc 30 mẫu thì hơn một nửa là tiêu đề chỉ có hãng với mã model. SVM dùng n-gram ký tự nên nhận ra được mã model, còn XGBoost chỉ thấy 100 chiều SVD nên mấy mã hiếm bị nén mất.

**17/11 – Khi nào nên dùng mô hình cây?**

Mô hình cây hợp với dữ liệu dạng bảng có ít cột số liệu như giá, kích thước, hoặc khi cần biết đặc trưng nào quan trọng. Với dữ liệu chữ ngắn có hàng chục nghìn cột thưa như bài này thì phải nén SVD mới chạy được, nén vậy mất thông tin nên thua mô hình tuyến tính khoảng 1,5 điểm mà còn chạy lâu hơn.

**18/11 – Lỗi còn lại của mô hình cuối chủ yếu do đâu?**

Mô hình cuối (LinearSVC) chỉ sai 47 trên 7.063 mẫu. Hơn một nửa là tiêu đề chỉ có hãng với mã model, người đọc cũng khó đoán. Khoảng 1/4 là nhãn gốc có vẻ sai, ở mấy mẫu này mô hình đoán còn hợp lý hơn nhãn. Phần còn lại là tiếng Đức bị mất dấu và vài phụ kiện lạ. Nên muốn tốt hơn nữa thì phải có thêm thông tin sản phẩm hoặc làm sạch nhãn, chứ đổi mô hình khó tăng thêm.