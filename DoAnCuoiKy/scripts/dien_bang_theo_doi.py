"""Điền experiments/BangTheoDoi_ThiNghiem_GoogleSheets.xlsx từ nhật ký CSV của 4 thành viên
và bảng đóng góp trong experiments/quyet_dinh_nhom.md. Chạy lại được: python scripts/dien_bang_theo_doi.py"""
from pathlib import Path
import re
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

EXP = Path(__file__).resolve().parents[1] / "experiments"
XLSX = EXP / "BangTheoDoi_ThiNghiem_GoogleSheets.xlsx"
wb = load_workbook(XLSX)

def read(member, name):
    f = EXP / member / name
    return pd.read_csv(f, encoding="utf-8-sig", dtype={"git_commit": str}) if f.exists() else pd.DataFrame()

def fill(ws, df):
    ws.delete_rows(2, ws.max_row)
    heads = [c.value for c in ws[1]]
    for i, row in enumerate(df.itertuples(index=False), start=2):
        rec = dict(zip(df.columns, row))
        for j, h in enumerate(heads, start=1):
            if h is None or h not in rec:
                continue
            v = rec[h]
            if isinstance(v, float) and pd.isna(v):
                continue
            ws.cell(i, j, v.item() if hasattr(v, "item") else v)
    ws.freeze_panes = "A2"
    return len(df)

sheets = {"Danh": "danh", "Loc": "loc", "Nhan": "nhan", "Thinh": "thinh"}
tong = []
for sh, m in sheets.items():
    d = read(m, "experiment_log.csv")
    print(sh, fill(wb[sh], d))
    if len(d):
        d = d.copy(); d.insert(0, "thanh_vien", m); d.insert(1, "file_nhat_ky", f"{m}/experiment_log.csv"); tong.append(d)
if wb["Thinh"].max_row < 2:
    wb["Thinh"].cell(2, 1, "Thịnh phụ trách phân cụm, không chạy mô hình phân loại – xem sheet Thinh_PhanCum")
c = read("thinh", "cluster_log.csv")
print("Thinh_PhanCum", fill(wb["Thinh_PhanCum"], c))
if len(c):
    c = c.copy(); c.insert(0, "thanh_vien", "thinh"); c.insert(1, "file_nhat_ky", "thinh/cluster_log.csv"); tong.append(c)
t = pd.concat(tong, ignore_index=True).sort_values("thoi_diem_chay")
print("TongHop", fill(wb["TongHop"], t))

# Bảng đóng góp
md = (EXP / "quyet_dinh_nhom.md").read_text(encoding="utf-8")
rows = [r for r in re.findall(r"^\| ([^|*][^|]*) \| (\d{10}) \| ([^|]*) \| ([^|]*) \| ([^|]*) \|$", md, re.M)]
ws = wb["DongGop"]
for i, (ten, mssv, vt, phan, pct) in enumerate(rows, start=2):
    for j, v in enumerate([ten.strip(), mssv, vt.strip(), phan.strip(), pct.strip()], start=1):
        ws.cell(i, j, v).alignment = Alignment(wrap_text=True, vertical="top")
ws.cell(len(rows) + 2, 1, "Tổng"); ws.cell(len(rows) + 2, 5, "100%")
ws.column_dimensions["D"].width = 90
print("DongGop", len(rows))
wb.save(XLSX)
