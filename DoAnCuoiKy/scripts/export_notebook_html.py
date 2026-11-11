"""Chạy lại notebook từ đầu và xuất bản HTML có ngày giờ -> nhật ký chạy.

    python scripts/export_notebook_html.py notebooks/04_Loc_TienXuLy.ipynb loc

Kết quả: experiments/<member>/runs/<ten_notebook>_<YYYYmmdd_HHMM>.html
(Mỗi lần chạy là một file HTML mới, KHÔNG ghi đè, để thấy được quá trình.)
Cần: pip install nbconvert ipykernel
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

nb, member = Path(sys.argv[1]), sys.argv[2]
root = Path(__file__).resolve().parents[1]
out_dir = root / "experiments" / member / "runs"
out_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M")
out = f"{nb.stem}_{stamp}"
subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", "--execute",
                "--ExecutePreprocessor.timeout=3600", "--output-dir", str(out_dir), "--output", out, str(nb)],
               check=True, cwd=nb.parent)
print("Nhật ký chạy:", out_dir / f"{out}.html")
