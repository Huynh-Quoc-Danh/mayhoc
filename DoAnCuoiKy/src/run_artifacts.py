"""Lưu THƯ MỤC KẾT QUẢ đầy đủ cho mỗi lần chạy: experiments/<member>/runs/<run_id>/

    params_cfg.json          cấu hình + thông tin môi trường (commit, máy, ngày giờ, kích thước tập)
    metrics_folds.csv        điểm từng fold của 5-fold CV (nếu chạy --cv) / từng seed (phân cụm)
    metrics_cv_mean.json     trung bình ± độ lệch chuẩn qua các fold
    metrics_test.json        điểm trên tập Test
    classification_report.csv  precision / recall / F1 / support từng ngành
    confusion_matrix.csv     ma trận nhầm lẫn (hàng = nhãn thật, cột = dự đoán)
    predictions_test.csv     từng mẫu Test: tiêu đề, nhãn thật, dự đoán, đúng/sai
    train.log.txt            log quá trình chạy (có giờ phút giây)
    README.md                lệnh để chạy lại đúng lần chạy này

Không lưu file mô hình vào GitHub (nặng). Dùng --save-model để lưu ra models/<run_id>.joblib trên máy.
"""
from __future__ import annotations

import json
from datetime import datetime

import numpy as np
import pandas as pd

from common import ROOT


class RunLog:
    """Ghi log có dấu thời gian, vừa in ra màn hình vừa giữ lại để lưu train.log.txt."""

    def __init__(self):
        self.lines = []

    def __call__(self, msg: str, show: bool = False):
        line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
        self.lines.append(line)
        if show:
            print(line)


def _r(v):
    return round(float(v), 6) if isinstance(v, (float, np.floating)) else v


def run_dir(member: str, run_id: str):
    d = ROOT / "experiments" / member / "runs" / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_classification_run(member, run_id, params_cfg, test_metrics, folds, y_true, y_pred, test_frame,
                            log: RunLog, command: str):
    from sklearn.metrics import classification_report, confusion_matrix
    d = run_dir(member, run_id)
    json.dump(params_cfg, open(d / "params_cfg.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    json.dump({k: _r(v) for k, v in test_metrics.items()}, open(d / "metrics_test.json", "w", encoding="utf-8"), indent=1)
    if folds:
        fd = pd.DataFrame(folds)
        fd.round(6).to_csv(d / "metrics_folds.csv", index=False, encoding="utf-8-sig")
        num = fd.drop(columns=["fold"]).select_dtypes("number")
        mean = {f"{c}_mean": _r(num[c].mean()) for c in num} | {f"{c}_std": _r(num[c].std(ddof=0)) for c in num}
        json.dump(mean, open(d / "metrics_cv_mean.json", "w", encoding="utf-8"), indent=1)
    labels = sorted(set(y_true))
    rep = classification_report(y_true, y_pred, labels=labels, digits=6, output_dict=True)
    pd.DataFrame(rep).T.round(6).rename_axis("nganh").to_csv(d / "classification_report.csv", encoding="utf-8-sig")
    pd.DataFrame(confusion_matrix(y_true, y_pred, labels=labels), index=labels, columns=labels) \
        .rename_axis("that \\ du_doan").to_csv(d / "confusion_matrix.csv", encoding="utf-8-sig")
    out = test_frame.copy()
    out["nhan_that"], out["du_doan"] = y_true, y_pred
    out["dung"] = out.nhan_that == out.du_doan
    out.to_csv(d / "predictions_test.csv", index=False, encoding="utf-8-sig")
    _finish(d, log, command)
    return d


def save_cluster_run(member, run_id, params_cfg, metrics, seeds, labels_frame, crosstab, log: RunLog, command: str):
    d = run_dir(member, run_id)
    json.dump(params_cfg, open(d / "params_cfg.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    json.dump({k: _r(v) for k, v in metrics.items()}, open(d / "metrics.json", "w", encoding="utf-8"), indent=1)
    if seeds:
        sd = pd.DataFrame(seeds)
        sd.round(6).to_csv(d / "metrics_seeds.csv", index=False, encoding="utf-8-sig")
        num = sd.drop(columns=["seed"]).select_dtypes("number")
        mean = {f"{c}_mean": _r(num[c].mean()) for c in num} | {f"{c}_std": _r(num[c].std(ddof=0)) for c in num}
        json.dump(mean, open(d / "metrics_seeds_mean.json", "w", encoding="utf-8"), indent=1)
    labels_frame.to_csv(d / "cluster_labels.csv", index=False, encoding="utf-8-sig")
    crosstab.to_csv(d / "cluster_vs_category.csv", encoding="utf-8-sig")
    purity = pd.DataFrame({"nganh_da_so": crosstab.idxmax(axis=1), "so_mau": crosstab.sum(axis=1),
                           "do_thuan": (crosstab.max(axis=1) / crosstab.sum(axis=1)).round(4)})
    purity.to_csv(d / "cluster_purity.csv", encoding="utf-8-sig")
    _finish(d, log, command)
    return d


def _finish(d, log, command):
    log(f"Đã lưu thư mục kết quả: {d.relative_to(ROOT)}")
    (d / "train.log.txt").write_text("\n".join(log.lines) + "\n", encoding="utf-8")
    files = sorted(p.name for p in d.iterdir() if p.name != "README.md") + ["README.md"]
    (d / "README.md").write_text(
        f"# {d.name}\n\nChạy lại đúng lần chạy này (từ thư mục DoAnCuoiKy):\n\n```\n{command}\n```\n\n"
        "Các file trong thư mục:\n\n" + "\n".join(f"- `{f}`" for f in files) + "\n", encoding="utf-8")
