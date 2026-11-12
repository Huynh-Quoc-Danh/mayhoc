# Nhật ký làm việc – danh

> Mỗi ngày viết 3 dòng làm việc. Ghi run_id để đối chiếu với experiment_log.csv.

| Ngày | Đã làm (run_id / commit) | Kết quả chính | Nhận xét – rút ra – ngày mai làm gì |
|12/11/2026|Cài môi trường, tạo nhánh danh. Chạy 6 thí nghiệm LinearSVC: word C=1 (danh_20261112_124307), hybrid char (2,4), full C=0.3 có CV, full balanced, full split group, full C=1 (danh_20261112_133323). Chạy notebook 05 mục 1, xuất HTML|word 0.9679 (khớp giữa kỳ); hybrid (2,4) 0.9924 (tốt nhất); full C=1 0.9920; full C=0.3 0.9900 (CV 0.9866 ± 0.001); balanced 0.9914; group 0.9868|N-gram ký tự là yếu tố chính (+2,45 điểm). Merchant + hình thái không giúp thêm. C=0.3 và balanced đều kém hơn. Chia theo sản phẩm chỉ giảm 0,5 điểm → mô hình tổng quát tốt. Freezers vẫn là lớp yếu nhất do trùng từ vựng với Fridges. Ngày mai: chạy CV cho hybrid và full với char (2,4), quét C = 1, 3, 10|
| | | | |
