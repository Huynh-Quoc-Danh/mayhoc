# experiments/ – Nhật ký thí nghiệm

```
experiments/
  danh/  loc/  nhan/  thinh/
    experiment_log.csv   # tự sinh: mỗi lần chạy run_experiment.py = 1 dòng
    cluster_log.csv      # (Thịnh) tự sinh bởi log_generic
    runs/                # JSON chi tiết từng lần chạy + HTML xuất notebook theo ngày
      <run_id>/          # (từ 20/11) THƯ MỤC KẾT QUẢ ĐẦY ĐỦ của 1 lần chạy – xem bên dưới
    nhat_ky.md           # nhật ký làm việc hằng ngày – tự viết
  quyet_dinh_nhom.md     # quyết định chung của nhóm + bảng đóng góp
```

## Thư mục kết quả của mỗi lần chạy (từ 20/11)
`src/run_experiment.py` (phân loại) và `src/run_cluster.py` (phân cụm) tự tạo `runs/<run_id>/`:

| File | Nội dung |
|---|---|
| `params_cfg.json` | cấu hình, commit, máy, dữ liệu, random_state, kích thước Train/Test |
| `metrics_folds.csv` / `metrics_seeds.csv` | điểm **từng fold** của 5-fold CV (phân loại) / từng seed K-Means (phân cụm) |
| `metrics_cv_mean.json` / `metrics_seeds_mean.json` | trung bình ± độ lệch chuẩn |
| `metrics_test.json` / `metrics.json` | điểm trên tập Test / điểm phân cụm chính |
| `classification_report.csv`, `confusion_matrix.csv` | precision/recall/F1 từng ngành, ma trận nhầm lẫn |
| `predictions_test.csv` | từng mẫu Test: tiêu đề, nhãn thật, dự đoán, đúng/sai |
| `cluster_labels.csv`, `cluster_vs_category.csv`, `cluster_purity.csv` | (phân cụm) cụm của từng tiêu đề, bảng cụm × ngành, độ thuần |
| `train.log.txt` | log quá trình chạy có giờ phút giây |
| `README.md` | lệnh chạy lại đúng lần chạy đó |

Mô hình (`.joblib`) không đưa lên GitHub; thêm `--save-model` để lưu ra `models/<run_id>.joblib` trên máy.

## Các cột tự động
`run_id`, `thoi_diem_chay` (giờ máy lúc chạy), `may_chay`, `git_commit` (phiên bản code; dấu `*` = code đang sửa chưa commit), cấu hình, độ đo.

## Hai cột tự viết sau mỗi lần chạy
- `nhan_xet` – thấy gì? (tăng/giảm bao nhiêu so với lần trước, lớp nào thay đổi)
- `rut_ra` – kết luận / lần sau thử gì

## Đưa lên Google Sheets
`python scripts/gop_nhat_ky.py` → `experiments/TONG_HOP_NHAT_KY.csv` (gộp 4 người).
Trên Google Sheets: **File → Import → Upload** file đó → *Replace current sheet* ở sheet "TongHop".
Mỗi người cũng có thể import file `experiment_log.csv` của mình vào sheet tên mình.
