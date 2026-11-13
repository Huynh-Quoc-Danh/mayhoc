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

## 12/11/2026 (tối) – Lộc: notebook 04, mục 2–7
- Mục 2 (ngram): (1,1) 0.9555 · (1,2) **0.9663** · (1,3) 0.9658, chọn (1,2).
- Mục 3 (min_df): 1 → **0.9773** · 2 → 0.9663 (mặc định) · 5 → 0.9499, chọn min_df=1.
- Mục 4 (alpha, min_df=1): 0.01 → **0.9800** · 0.03 → 0.9789 · 0.1 → 0.9773 · 0.3 → 0.9702 · 1.0 → 0.9501.
- Mục 5 (LR): tốt nhất C=30 → 0.9676; class_weight='balanced' không giúp ích.
- Mục 6: hình figures/loc_nb_alpha_lr_C.png.
- **Kết luận:** NB + ngram (1,2) + min_df=1 + alpha=0.01, Macro-F1 = 0.980 (+0.014 so với giữa kỳ).
- **Ngày mai:** kiểm tra lại bằng chia train/test theo cluster_id; thử alpha 0.001 và 0.003; chạy cross-validation cho cấu hình tốt nhất.

## 13/11/2026 – Lộc
- Chạy lại EDA (`python src/eda.py`) và giải thích số liệu trong notebook 04 mục 1 (nguồn: results/eda_summary.json).
- loc_20261113_144358 – cnb_alpha01: ComplementNB word, F1 = 0.9674 (≈ MultinomialNB 0.9663).
- loc_20261113_144410 – nb_hybrid: NB word + n-gram ký tự, F1 = **0.9851** (+1,9 điểm).
- loc_20261113_144424 – lr_hybrid: LR hybrid C=10, F1 = **0.9890** (+2,2 điểm), tốt nhất của Lộc.
- **Nhận xét:** NB và LR đều hưởng lợi từ n-gram ký tự gần bằng SVM (+2,45 điểm), khớp với EDA (87,9% tiêu đề có mã chữ-số, 18,7% không có từ khóa ngành). SVM hybrid của Danh vẫn tốt nhất (0.9924).
- **Ghi chú cho nhóm:** cột test_f1_macro trong experiments/danh/experiment_log.csv đang bị nhân 1000 lần (967.909 thay vì 0.967909), có thể do lưu CSV bằng Excel.
- **Ngày mai:** thử NB hybrid với alpha=0.01, min_df=1; quét C cho LR hybrid; kiểm tra bằng chia train/test theo cluster_id.
