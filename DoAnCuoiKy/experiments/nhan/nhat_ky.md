# Nhật ký làm việc – nhan

> Mỗi ngày viết 3 dòng bằng lời của mình. Ghi run_id để đối chiếu với experiment_log.csv.

| Ngày | Đã làm (run_id / commit) | Kết quả chính | Nhận xét – rút ra – ngày mai làm gì |
|---|---|---|---|
| 12/11 | Cài môi trường, tạo nhánh `nhan`. Chạy `tai_lap_E02`, `dt_depth50`, `dt_leaf3`, `xgb_lan_dau` (run_id xem trong experiment_log.csv) | E02 tái lập = **0.9408** (khớp giữa kỳ). depth50 = 0.9179, leaf3 = 0.9322. XGBoost (SVD 100, 200 cây) = **0.9771**, thấp hơn HGB E08 (0.9793) khoảng 0,2 điểm | Giới hạn cây đơn đều làm kém đi vì cây trên TF-IDF cần rất sâu. XGBoost hơn cây đơn 3,6 điểm. Gặp lỗi pandas 3 → cài `pandas<3`. Ngày mai: tinh chỉnh XGBoost (n_estimators, max_depth, learning_rate, số chiều SVD). |

## Câu hỏi tự trả lời (12/11)

**1. Giới hạn độ sâu làm cây tốt hơn hay kém hơn? Vì sao?**

Kém hơn. Cây mặc định đạt Macro-F1 0.9408; `max_depth=50` còn 0.9179, `min_samples_leaf=3` còn 0.9322.
Cây mặc định sâu tới 241 tầng với 1394 lá, độ chính xác trên train 0.992, tức là nó học gần như thuộc lòng.
Nhưng khi cắt xuống 50 tầng, độ chính xác trên train chỉ còn 0.938: cây bị *thiếu khớp* (underfit) chứ không phải bớt quá khớp.
Lý do là dữ liệu là TF-IDF rất thưa (~31.000 đặc trưng từ/cụm từ). Mỗi nút chỉ hỏi "tiêu đề có chứa từ X không?",
và mỗi từ chỉ xuất hiện ở một phần nhỏ mẫu, nên cây phải hỏi rất nhiều câu nối tiếp nhau mới tách hết được 10 lớp.
Chặn độ sâu thì nhiều mẫu rơi vào nhánh "không chứa từ nào trong các từ đã hỏi" và bị gán sai
(ví dụ Washing Machines: precision 0.996 nhưng recall tụt còn 0.878).
`min_samples_leaf=3` ít hại hơn, nhưng lại xóa các lá nhỏ chứa từ hiếm, nên lớp Freezers giảm rõ nhất (0.909 → 0.882).

**2. Vì sao cây đơn kém hơn SVM trên dữ liệu văn bản?**

- SVM tuyến tính **cộng dồn bằng chứng từ tất cả các từ cùng lúc**: mỗi từ có một trọng số, tiêu đề có nhiều từ gợi ý cùng một lớp thì điểm lớp đó cao. Cây chỉ đi theo một đường, mỗi bước xét một từ, nên bỏ qua phần lớn thông tin còn lại trong tiêu đề.
- Dữ liệu văn bản nhiều chiều và thưa: SVM xử lý tốt (dữ liệu gần như tách tuyến tính được), còn cây phải mọc rất sâu, dễ quá khớp và rất nhạy với vài từ hiếm (phương sai cao).
- Các lớp dễ nhầm (Fridges / Freezers / Fridge Freezers) chia sẻ nhiều từ chung; phân biệt chúng cần cân nhắc nhiều từ cùng lúc, đúng thế mạnh của mô hình tuyến tính.
- Vì vậy hướng cải thiện cho mô hình cây là **ensemble** (Random Forest, Gradient Boosting/XGBoost) và nén văn bản bằng SVD, chứ không phải chỉnh một cây đơn.

**3. XGBoost so với HistGradientBoosting giữa kỳ?**

XGBoost lần đầu đạt Macro-F1 0.9771, hơn cây đơn 3,6 điểm nhưng thấp hơn HGB giữa kỳ (E08: 0.9793) khoảng 0,2 điểm.
Hai mô hình cùng là boosting (nhiều cây nông, cây sau sửa lỗi cây trước) nên kết quả gần nhau; chênh lệch nhỏ có thể do
số cây (200 so với 300) và việc nén văn bản còn 100 chiều SVD làm mất bớt thông tin. Bước tiếp theo là tinh chỉnh tham số XGBoost.
