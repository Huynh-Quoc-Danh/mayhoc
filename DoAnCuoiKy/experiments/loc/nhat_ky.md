# Nhật ký làm việc – loc

> Mỗi ngày viết 3 dòng bằng lời của mình. Ghi run_id để đối chiếu với experiment_log.csv.

| Ngày | Đã làm (run_id / commit) | Kết quả chính | Nhận xét – rút ra – ngày mai làm gì |
|---|---|---|---|
| | | | |

## 12/11/2026 – Lộc
- Cài môi trường trên Mac (conda env nhom06, Python 3.12). Gặp 2 lỗi và đã sửa: XGBoost thiếu libomp (cài llvm-openmp) và pandas 3.x lỗi khi chia train/test (hạ về pandas 2.3.3). Đề nghị sửa requirements.txt thành pandas>=2.0,<3.
- loc_20261112_195345 – tai_lap_E01 (NB, alpha=0.1, ngram 1,2): F1 = 0.9663, khớp giữa kỳ.
- loc_20261112_195511 – alpha_1 (alpha=1.0): F1 = 0.9493.
- loc_20261112_195556 – ngram_11 (alpha=0.1, ngram 1,1): F1 = 0.9555.

**Alpha lớn hơn làm F1 tăng hay giảm?** Giảm (0.9663 -> 0.9493). Alpha là hệ số làm trơn Laplace: alpha lớn cộng thêm nhiều "đếm giả" cho mọi từ, nên các từ hiếm nhưng phân biệt tốt (tên model, từ riêng của tủ đông) bị giảm trọng số. Mô hình nghiêng về lớp đông nhất là Fridge Freezers, làm recall của Freezers tụt mạnh (0.889 -> 0.710).

**N-gram (1,1) so với (1,2)?** (1,1) kém hơn (0.9555 so với 0.9663). Chỉ dùng từ đơn thì mất thông tin cụm từ: "fridge freezer", "chest freezer" hay "built in" bị tách rời nên khó phân biệt Fridges / Freezers / Fridge Freezers. Bù lại (1,1) train nhanh hơn vì ít đặc trưng hơn.
