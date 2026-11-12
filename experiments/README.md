# experiments/ – Nhật ký thí nghiệm

```
experiments/
  danh/  loc/  nhan/  thinh/
    experiment_log.csv   # tự sinh: mỗi lần chạy run_experiment.py = 1 dòng
    cluster_log.csv      # (Thịnh) tự sinh bởi log_generic
    runs/                # JSON chi tiết từng lần chạy + HTML xuất notebook theo ngày
    nhat_ky.md           # nhật ký làm việc hằng ngày – tự viết
  bien_ban_hop.md        # biên bản họp nhóm (16/11, 19/11, 21/11)
```

## Các cột tự động
`run_id`, `thoi_diem_chay` (giờ máy lúc chạy), `may_chay`, `git_commit` (phiên bản code; dấu `*` = code đang sửa chưa commit), cấu hình, độ đo.

## Hai cột tự viết sau mỗi lần chạy
- `nhan_xet` – thấy gì? (tăng/giảm bao nhiêu so với lần trước, lớp nào thay đổi)
- `rut_ra` – kết luận / lần sau thử gì

## Đưa lên Google Sheets
`python scripts/gop_nhat_ky.py` → `experiments/TONG_HOP_NHAT_KY.csv` (gộp 4 người).
Trên Google Sheets: **File → Import → Upload** file đó → *Replace current sheet* ở sheet "TongHop".
Mỗi người cũng có thể import file `experiment_log.csv` của mình vào sheet tên mình.
