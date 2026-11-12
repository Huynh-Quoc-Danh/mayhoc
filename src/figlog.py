"""Lưu hình và ghi lại NGUỒN GỐC của hình (notebook nào, ai chạy, lúc nào).

Mọi hình trong báo cáo/slide phải lưu qua save_fig để figures/FIGURE_INDEX.csv
trả lời được câu hỏi: "Hình này ở notebook nào, code nào sinh ra, ý nghĩa là gì?"
Cột y_nghia do người vẽ tự viết (không để trống khi đưa hình vào báo cáo).
"""
import csv
from datetime import datetime

from common import FIG_DIR

INDEX = FIG_DIR / "FIGURE_INDEX.csv"
COLS = ["file", "notebook", "cell_hoac_ham", "nguoi_chay", "thoi_diem", "y_nghia"]


def save_fig(fig, name: str, notebook: str, member: str, cell: str = "", y_nghia: str = "", dpi: int = 160):
    """Ví dụ: save_fig(fig, "loc_cm_nb_alpha05", notebook="04_Loc_TienXuLy.ipynb", member="loc",
                        cell="Cell 7 - confusion matrix", y_nghia="...")"""
    FIG_DIR.mkdir(exist_ok=True)
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    new = not INDEX.exists()
    with open(INDEX, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerow(dict(file=path.name, notebook=notebook, cell_hoac_ham=cell, nguoi_chay=member,
                        thoi_diem=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), y_nghia=y_nghia))
    print(f"Đã lưu {path.name} (ghi nguồn vào figures/FIGURE_INDEX.csv)")
    return path
