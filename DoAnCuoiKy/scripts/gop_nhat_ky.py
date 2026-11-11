"""Gộp nhật ký thí nghiệm của 4 thành viên thành experiments/TONG_HOP_NHAT_KY.csv
(để import lên Google Sheets). Chạy: python scripts/gop_nhat_ky.py"""
from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parents[1] / "experiments"
frames = []
for member in ["danh", "loc", "nhan", "thinh"]:
    for f in sorted((root / member).glob("*_log.csv")):
        d = pd.read_csv(f, encoding="utf-8-sig")
        d.insert(0, "thanh_vien", member); d.insert(1, "file_nhat_ky", f"{member}/{f.name}")
        frames.append(d)
if not frames:
    raise SystemExit("Chưa có nhật ký nào.")
out = pd.concat(frames, ignore_index=True).sort_values("thoi_diem_chay")
out.to_csv(root / "TONG_HOP_NHAT_KY.csv", index=False, encoding="utf-8-sig")
thieu = out["nhan_xet"].isna().sum()
print(f"Đã gộp {len(out)} lần chạy -> experiments/TONG_HOP_NHAT_KY.csv; {thieu} dòng CHƯA có nhận xét.")
