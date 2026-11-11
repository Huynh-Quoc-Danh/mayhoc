"""Gộp các log CSV thành results/experiment_log.xlsx (Nhật ký thực nghiệm) + experiment_log.csv"""
import json

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from common import RES_DIR

cls = pd.read_csv(RES_DIR / "experiment_log_classification.csv")
clu = pd.read_csv(RES_DIR / "experiment_log_clustering.csv")
best = json.load(open(RES_DIR / "best_model.json"))["best_id"]
eda = json.load(open(RES_DIR / "eda_summary.json", encoding="utf-8"))

CMAP = {"exp_id": "Mã TN", "date": "Ngày chạy", "task": "Nhánh", "model": "Mô hình", "features": "Đặc trưng",
        "params": "Siêu tham số", "split": "Cách chia dữ liệu", "n_train": "Số mẫu Train", "n_test": "Số mẫu Test",
        "cv_folds": "Số fold CV", "cv_accuracy_mean": "CV Accuracy (TB)", "cv_f1_macro_mean": "CV Macro-F1 (TB)",
        "cv_f1_macro_std": "CV Macro-F1 (Std)", "cv_time_s": "Thời gian CV (s)", "train_time_s": "Thời gian train (s)",
        "infer_ms_per_1k": "Suy luận (ms/1000 mẫu)", "test_accuracy": "Test Accuracy",
        "test_precision_macro": "Test Macro-Precision", "test_recall_macro": "Test Macro-Recall",
        "test_f1_macro": "Test Macro-F1", "test_f1_weighted": "Test Weighted-F1",
        "silhouette_cosine": "Silhouette (cosine, mẫu 10k)", "davies_bouldin": "Davies-Bouldin",
        "ari_vs_category": "ARI (vs Category)", "nmi_vs_category": "NMI (vs Category)",
        "v_measure_vs_category": "V-measure", "notes": "Ghi chú / Nhận xét", "comment": "Nhận xét"}

# nhận xét viết tay sau khi xem kết quả (cập nhật trong build)
COMMENTS = json.load(open(RES_DIR / "experiment_comments.json", encoding="utf-8")) \
    if (RES_DIR / "experiment_comments.json").exists() else {}
cls["comment"] = cls.exp_id.map(COMMENTS).fillna("")
clu["comment"] = clu.exp_id.map(COMMENTS).fillna("")

pd.concat([cls, clu], ignore_index=True).to_csv(RES_DIR / "experiment_log.csv", index=False, encoding="utf-8-sig")

out = RES_DIR / "experiment_log.xlsx"
guide = pd.DataFrame({
    "Mục": ["Đề tài", "Nhóm", "Dữ liệu", "Chia dữ liệu", "Chống rò rỉ", "Độ đo chính", "Mô hình tốt nhất (giữa kỳ)",
            "Ghi chú XGBoost", "Mã nguồn", "Sheet"],
    "Nội dung": ["Product Classification and Clustering (PriceRunner, UCI #837)",
                 "Nhóm 06 – Môn Máy học – ĐH Sài Gòn",
                 f"{eda['n_rows']:,} mẫu, {eda['n_categories']} ngành, {eda['n_merchants']} merchant, {eda['n_clusters']:,} cụm thực thể",
                 "Stratified 80/20 theo Category (random_state=42); 5-Fold Stratified CV trên Train; thêm GroupShuffle 80/20 theo Cluster ID",
                 "TF-IDF/SVD/Scaler/Merchant prior nằm trong sklearn Pipeline → chỉ fit trên Train/fold",
                 "Macro-F1 (phân loại); NMI/ARI/Silhouette (phân cụm)",
                 best,
                 "Môi trường chạy không có xgboost → E08 dùng HistGradientBoostingClassifier (cùng họ GBDT histogram); code tự dùng XGBoost nếu được cài",
                 "src/train_baselines.py, src/cluster_baseline.py",
                 "Classification · Clustering · PerClass_F1 · ConfusionMatrix_best · EDA_summary"]})
with pd.ExcelWriter(out, engine="openpyxl") as w:
    guide.to_excel(w, "Huong_dan", index=False)
    cls.rename(columns=CMAP).to_excel(w, "Classification", index=False)
    clu.drop(columns=[c for c in clu.columns if clu[c].isna().all()]).rename(columns=CMAP).to_excel(w, "Clustering", index=False)
    pd.read_csv(RES_DIR / "per_class_f1_all_models.csv", index_col=0).to_excel(w, "PerClass_F1")
    pd.read_csv(RES_DIR / f"confusion_matrix_{best}.csv", index_col=0).to_excel(w, "ConfusionMatrix_best")
    pd.DataFrame(list(eda.items()), columns=["Chỉ số", "Giá trị"]).to_excel(w, "EDA_summary", index=False)

wb = load_workbook(out)
hdr = PatternFill("solid", fgColor="1F4E79"); thin = Side(style="thin", color="BFBFBF")
for ws in wb.worksheets:
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = hdr
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[1].height = 36
    ws.freeze_panes = "B2"
    for col in ws.columns:
        L = get_column_letter(col[0].column)
        width = max(len(str(c.value)) if c.value is not None else 0 for c in col[1:] or col)
        ws.column_dimensions[L].width = min(max(10, width * 0.9), 55)
        for c in col[1:]:
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if isinstance(c.value, float):
                c.number_format = "0.0000" if abs(c.value) < 10 else "0.00"
ws = wb["Classification"]
hl = PatternFill("solid", fgColor="E2EFDA")
for row in ws.iter_rows(min_row=2):
    if row[0].value == best:
        for c in row: c.fill = hl
wb["Huong_dan"].column_dimensions["B"].width = 110
wb.save(out)
print("saved", out)
