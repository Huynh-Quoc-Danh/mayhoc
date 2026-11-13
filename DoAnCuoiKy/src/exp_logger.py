"""Ghi nhật ký thí nghiệm tự động.

Mỗi lần chạy thêm 1 dòng vào experiments/<member>/experiment_log.csv gồm:
  run_id, thoi_diem_chay (ngày giờ máy thực tế), may_chay, git_commit, ten_thi_nghiem,
  cấu hình, độ đo, và hai cột để TRỐNG cho người chạy tự điền: nhan_xet, rut_ra.
Đồng thời lưu bản đầy đủ dạng JSON ở experiments/<member>/runs/<run_id>.json.

Không có hàm nào cho phép sửa thời điểm chạy: nhật ký phải phản ánh đúng lúc chạy thật.
"""
from __future__ import annotations

import csv
import json
import platform
import subprocess
from datetime import datetime

from common import ROOT

COLUMNS = ["run_id", "thoi_diem_chay", "may_chay", "git_commit", "ten_thi_nghiem", "model", "features",
           "params", "split", "word_ngram", "char_ngram", "min_df", "svd", "n_train", "n_test",
           "cv_f1_macro_mean", "cv_f1_macro_std", "test_accuracy", "test_f1_macro", "test_f1_weighted",
           "f1_Fridges", "f1_Freezers", "f1_Fridge_Freezers", "train_time_s", "nhan_xet", "rut_ra"]


def _git_commit() -> str:
    """Mã commit hiện tại (+ dấu * nếu còn thay đổi chưa commit) để biết kết quả chạy từ phiên bản code nào."""
    try:
        h = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True,
                                    stderr=subprocess.DEVNULL).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "src"], cwd=ROOT, text=True).strip()
        return h + ("*" if dirty else "")
    except Exception:
        return "chua_co_git"


def _ensure_trailing_newline(path):
    """File CSV tải về từ Google Sheets thường KHÔNG có ký tự xuống dòng ở cuối.
    Nếu ghi nối tiếp ngay, dòng mới sẽ dính vào dòng cuối cũ -> hỏng file.
    Hàm này thêm '\\n' vào cuối file nếu còn thiếu."""
    if path.exists() and path.stat().st_size > 0:
        with open(path, "rb+") as f:
            f.seek(-1, 2)
            if f.read(1) not in (b"\n", b"\r"):
                f.write(b"\r\n")


def log_run(member: str, config: dict, results: dict, n_train: int, n_test: int, exp_name: str = "") -> str:
    folder = ROOT / "experiments" / member
    (folder / "runs").mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    run_id = f"{member}_{now:%Y%m%d_%H%M%S}"
    row = {c: "" for c in COLUMNS}
    row.update(run_id=run_id, thoi_diem_chay=now.strftime("%Y-%m-%d %H:%M:%S"), may_chay=platform.node(),
               git_commit=_git_commit(), ten_thi_nghiem=exp_name, n_train=n_train, n_test=n_test,
               **{k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list, tuple)) else v)
                  for k, v in config.items()})
    row.update({k: round(v, 6) for k, v in results.items() if k in COLUMNS})
    path = folder / "experiment_log.csv"
    new = not path.exists()
    _ensure_trailing_newline(path)
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new:
            w.writeheader()
        w.writerow(row)
    json.dump({"run_id": run_id, "time": row["thoi_diem_chay"], "config": config, "results": results},
              open(folder / "runs" / f"{run_id}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1,
              default=str)
    return run_id


def log_generic(member: str, log_name: str, row: dict) -> str:
    """Nhật ký dạng tự do (dùng cho phân cụm, EDA...). Thêm thời điểm chạy + commit,
    các cột nhan_xet / rut_ra để trống cho người chạy tự điền."""
    folder = ROOT / "experiments" / member
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    run_id = f"{member}_{now:%Y%m%d_%H%M%S}"
    full = {"run_id": run_id, "thoi_diem_chay": now.strftime("%Y-%m-%d %H:%M:%S"), "git_commit": _git_commit(),
            **{k: (round(v, 6) if isinstance(v, float) else v) for k, v in row.items()}, "nhan_xet": "", "rut_ra": ""}
    path = folder / f"{log_name}.csv"
    cols = list(full)
    if path.exists():  # giữ thứ tự cột cũ, thêm cột mới (nếu có) vào cuối
        with open(path, encoding="utf-8-sig") as f:
            old = next(csv.reader(f))
        cols = old + [c for c in cols if c not in old]
        if cols != old:
            rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    _ensure_trailing_newline(path)
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if not path.exists() or path.stat().st_size == 0:
            w.writeheader()
        w.writerow(full)
    # Lưu bản JSON gốc (số liệu chính xác) để khôi phục nếu file CSV bị sửa hỏng
    (folder / "runs").mkdir(exist_ok=True)
    json.dump(full, open(folder / "runs" / f"{run_id}.json", "w", encoding="utf-8"), ensure_ascii=False,
              indent=1, default=str)
    return run_id
