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

## 14/11/2026 – Lộc
- NB hybrid char(2,4): alpha 0.1 → 0.9851 (loc_20261114_174839), **0.03 → 0.9869** (loc_20261114_174908), 0.3 → 0.9799 (loc_20261114_174915).
- LR hybrid char(2,4): C=10 → 0.9902 (loc_20261114_174953), C=30 → 0.9895 (loc_20261114_175352), **C=100 → 0.9909** (loc_20261114_175809).
- CV 5-fold: NB alpha=0.03 → **0.9861 ± 0.0014** (loc_20261114_175845); LR C=100 → **0.9875 ± 0.0016** (loc_20261114_175918); SVM Danh → 0.9909 ± 0.0013 (danh_20261113_170944).
- **Nhận xét:** SVM hơn LR ≈ 2 độ lệch chuẩn và hơn NB ≈ 3 độ lệch chuẩn → khác biệt thật. LR và NB chênh ≈ 1 độ lệch chuẩn → coi như ngang nhau. NB kém do giả định độc lập (n-gram ký tự chồng lấn bị đếm trùng); SVM hơn LR nhờ tối đa lề (hinge loss).
- Hình: figures/loc_so_sanh_tuyen_tinh.png (notebook 04 mục 8).
- **Ngày mai:** kiểm tra NB/LR với chia train/test theo cluster_id; thử alpha < 0.03 cho NB hybrid.

## 15/11/2026 – Lộc
- loc_20261115_142029 – LR C=100 balanced: F1 0.9889 (không cân bằng 0.9909) → balanced không giúp.
- loc_20261115_142042/142049/142057 – ComplementNB alpha 0.03/0.1/0.3: 0.9857 / 0.9840 / 0.9817 → kém MultinomialNB (0.9869).
- loc_20261115_142102 – NB Group split: 0.9819 (−0.50 điểm); loc_20261115_142112 – LR Group split: 0.9851 (−0.58 điểm); SVM Danh Group split 0.9875 (−0.54 điểm).
- **Nhận xét:** dữ liệu chỉ lệch nhẹ nên cân bằng lớp và ComplementNB đều không có lợi. Chia theo sản phẩm làm cả 3 mô hình giảm khoảng 0.5 điểm, thứ hạng giữ nguyên: SVM > LR > NB; NB nhanh nhất.
- Notebook 04 mục 9: bảng + kết luận. Sơ đồ tiền xử lý: docs/hinh_ve_tay/loc_so_do_tien_xu_ly.jpg.
- **Ngày mai:** theo phân công của nhóm.

## 16/11/2026 – Lộc
- loc_20261116_193144 – lr_giai_thich: chạy lại LR hybrid char (2,4) C=100 để lấy hệ số, Test F1 0.9909 (trùng lr_h24_C100). Notebook 04 mục 10: hình 8 đặc trưng mạnh nhất mỗi ngành (figures/loc_dac_trung_quan_trong.png).
- **Nhận xét:** CPUs, Cameras, Dishwashers, Microwaves, TVs dựa vào từ khóa (intel, camera, dishwasher, geschirrsp ler, microwave, tv). Nhóm tủ lạnh dựa vào mảnh mã model Bosch/Siemens: ' kg' (Fridge Freezers), ' ki', 'ks' (Fridges), ' g' (Freezers), nên n-gram ký tự quan trọng nhất ở nhóm này. '14' ở Washing Machines là từ 1400 vòng/phút, 'sim' ở Mobile Phones là từ dual sim.
- **Họp nhóm 1:** trình bày kết quả NB/LR (LR C=100: Test 0.9909, CV 0.9875, Group 0.9851; NB: CV 0.9861), balanced và ComplementNB không giúp, đồng ý chọn SVM làm mô hình cuối.
- **Nhóm quyết định:** chọn SVM hybrid char (2,4), C=3 làm mô hình cuối (CV 0.9909, Group 0.9875); LR C=100 là mô hình tuyến tính tốt thứ hai, dùng để giải thích đặc trưng trong báo cáo.
- **Ngày mai:** theo phân công của nhóm.

## 17/11/2026 – Lộc
- Notebook 04 mục 11: bảng tổng kết 6 run (cv_nb_best, cv_lr_best, nb/lr_best_group, cnb_h24_a003, lr_h24_C100_bal) + đoạn tổng kết; chỉ đọc nhật ký, không chạy thí nghiệm mới.
- **Kết luận nhánh NB/LR:** LR C=100 (CV 0.9875, Test 0.9909, Group 0.9851) > NB alpha=0.03 (CV 0.9861, Test 0.9869, Group 0.9819); kém SVM 0.20–0.60 điểm Test, đổi lại NB nhanh nhất (~1,2 giây), LR dễ giải thích hệ số.
- Báo cáo report/nhap/BaoCao_Loc.docx: viết xong Chương 2 (2.1–2.5, 5 hình vẽ lại bằng draw.io từ dữ liệu thật), Chương 3 (3.1–3.4) và mục 4.1; mọi số liệu ghi run_id / nguồn.
- **Ngày mai:** rà lại báo cáo theo góp ý của nhóm ở họp 2 (19/11).

## 18/11/2026 – Lộc
- **Rà soát BaoCao_Loc.docx** (có dùng Claude hỗ trợ đối chiếu số liệu): đối chiếu mọi số ở Ch.2, Ch.3, mục 4.1 với experiments/loc/experiment_log.csv, results/eda_summary.json và dữ liệu gốc – tất cả khớp. Fit lại TF-IDF trên Train xác nhận 68.324 đặc trưng (từ 31.043 + char_wb (2,4) 37.281).
- **Đã sửa:** xóa 9 dòng Heading 2 rỗng (hiện thành dòng trống trong mục lục); viết lại 2.4 và 2.5 cho gọn, rõ; 2.5 sửa lại vai trò Group split cho khớp Ch.5 (chia chính là Stratified 80/20, Group split để kiểm tra) và thêm số: SVM 0.9929 → 0.9875, LR 0.9909 → 0.9851, NB 0.9869 → 0.9819; ghi rõ cách tính Hình 2.4 (200 từ phổ biến nhất, khác Jaccard trong eda_vocab_jaccard.csv); thống nhất χ², in đậm “Nhận xét:”, sửa bộ full = hình thái + cửa hàng ở 3.3.
- **Đã xử lý tồn đọng:** xuất lại Hình 2.5 (bỏ dấu chọn draw.io), commit scripts/loc_ve_drawio.py làm nguồn cho Hình 2.3–2.4.
- **Góp ý Ch.6 của Nhân** (report/nhap/GopY_Loc_cho_Ch6.docx, 14 comment, không sửa nội dung): SVM 0.9930 / CV 0.9910 lấy từ danh_20261115_151800 (norm_de_fr, nhóm không dùng) → nên là mô hình cuối danh_20261113_170944 (0.9929, CV 0.9909 ± 0.0013); “90.000 cột” ở 4.3 là char (3,5), cần ghi rõ để không lệch với 68.324 ở 3.2; số “57 mẫu” ở 6.4 chưa có nguồn; đoạn giải thích n-gram ký tự ở 6.1 và từ vựng chồng lấp ở 6.2 trùng mục 3.2–3.4 và 2.4 → dẫn chéo; hai con số 25/47 ở 6.3 dễ gây hiểu nhầm.
- **Phác slide** Dữ liệu – Tiền xử lý: report/nhap/Slide_Loc_nhap.docx, 6 slide. Slide 3 phải dùng Hình 2.4 bản draw.io, không dùng eda_05_vocab_overlap.png (Jaccard 21–27%, lệch số).
- **Ngày mai:** họp 2 (19/11) – nhận góp ý cho Ch.2–3.

## 19/11/2026 – Lộc
- **Dán bài lên báo cáo chung (Google Docs, tài khoản của Lộc):** Ch.2 (2.1–2.5), Ch.3 (3.1–3.4), mục 4.1, đủ 8 hình (2.1–2.5, 3.1, 3.2, 4.1) và 3 bảng (2.1, 3.1, 4.1), tiêu đề giữ kiểu Tiêu đề 1/2. Dùng bản report/nhap/BaoCao_Loc.docx mới nhất (có phần rà soát 18/11 và Hình 2.5 đã xuất lại) vì bản DanVaoDocs_Loc.docx là bản cũ.
- **Sau khi dán:** trả tiêu đề Chương 4 về "Chương 4. Các mô hình", sửa chú thích Hình 3.1 thành "vẽ bằng draw.io".
- **Đọc chéo Ch.6:** đến cuối buổi Nhân chưa dán Ch.6 lên Docs; đã chuẩn bị 6 bình luận (SVM 0.9930 → 0.9929 theo danh_20261113_170944; NB 0.9869 và LR 0.9909 khớp nhật ký, LR nên ghi loc_20261114_175918; dẫn chéo mục 3.2–3.4 và Hình 2.4; hai con số 25/47 ở 6.3; nguồn của "57 mẫu" ở 6.4) để đăng khi Nhân dán xong.
- **Góp ý của Danh cho Ch.2–3:** chưa có bình luận.
- **Ngày mai (20/11):** dựng slide phần Dữ liệu – Tiền xử lý từ report/nhap/Slide_Loc_nhap.docx vào khung report/slide/Nhom06_Slide_Khung.pptx; đăng bình luận Ch.6 khi Nhân dán.
