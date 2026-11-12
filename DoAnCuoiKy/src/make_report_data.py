"""Tổng hợp số liệu cho báo cáo/slide -> results/report_data.json (mọi con số đều lấy từ file kết quả)."""
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from common import RANDOM_STATE, RES_DIR, clean_title, load_data
import train_baselines as tb

cls = pd.read_csv(RES_DIR / "experiment_log_classification.csv").fillna({"notes": ""})
clu = pd.read_csv(RES_DIR / "experiment_log_clustering.csv").fillna({"notes": ""})
eda = json.load(open(RES_DIR / "eda_summary.json", encoding="utf-8"))
best = json.load(open(RES_DIR / "best_model.json"))["best_id"]

main = cls[cls.split == "Stratified 80/20"].copy()
short = {"Word TF-IDF (1,2)": "Word TF-IDF (1,2)",
         "Hybrid TF-IDF (word 1-2 + char_wb 3-5)": "Hybrid TF-IDF (word + char)",
         "Hybrid TF-IDF + Morph(5) + Merchant prior(10)": "Hybrid TF-IDF + Morph + Merchant",
         "SVD-150 (Hybrid TF-IDF) + Morph + Merchant prior": "SVD-150 + Morph + Merchant"}
main["features_short"] = main.features.map(short).fillna(main.features)

# Ablation: refit E04/E05/E06 để đếm lỗi trong nhóm 3 lớp tủ lạnh/tủ đông
df = load_data(); df["clean"] = df["title"].map(clean_title)
X, y = df[["clean", "merchant_id"]], df["category_label"].values
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
FR = {"Fridges", "Freezers", "Fridge Freezers"}
exps = {e["id"]: e for e in tb.experiments()}
names = {"E04": "Word TF-IDF (1,2)", "E05": "+ Char_wb TF-IDF (3,5)", "E06": "+ Morph(5) + Merchant prior(10)"}
abl, base = [], None
for k in ["E04", "E05", "E06"]:
    p = exps[k]["pipe"].fit(Xtr, ytr).predict(Xte)
    f = float(main.loc[main.exp_id == k, "test_f1_macro"].iloc[0])
    m = np.array([a in FR and b in FR and a != b for a, b in zip(yte, p)])
    base = f if base is None else base
    abl.append({"name": names[k], "f1": f, "delta": "–" if k == "E04" else f"{(f - base) * 100:+.2f} điểm %".replace(".", ","), "fridge_err": int(m.sum()),
                "total_err": int((yte != p).sum())})

grp = []
for _, r in cls[cls.split.str.startswith("Group")].iterrows():
    sid = r.exp_id.replace("-G", "")
    fs = float(main.loc[main.exp_id == sid, "test_f1_macro"].iloc[0])
    grp.append({"exp_id": r.exp_id, "model": r.model, "f1_strat": fs, "f1_group": r.test_f1_macro,
                "delta": f"{(r.test_f1_macro - fs) * 100:+.2f} điểm %".replace(".", ","), "n_test": int(r.n_test)})

tc = pd.read_csv(RES_DIR / f"top_confusions_{best}.csv")
top_conf = tc.values.tolist()[:8]
cdist = pd.read_csv(RES_DIR / "eda_class_distribution.csv", index_col=0)

members = [
    dict(name="Huỳnh Quốc Danh", mssv="3124411050", role="Nhóm trưởng",
         task_mid="Điều phối; thiết kế pipeline TF-IDF/SVD chống rò rỉ; huấn luyện LinearSVC, Logistic, Gradient Boosting; tổng hợp báo cáo",
         done="Thiết kế kiến trúc pipeline (ColumnTransformer + Pipeline), cài đặt MerchantPrior; chạy E03–E06, E08 và 4 thí nghiệm Group split; tổng hợp experiment log, viết báo cáo",
         files="src/common.py, src/train_baselines.py, results/experiment_log.xlsx, báo cáo .docx", share="25%"),
    dict(name="Huỳnh Tấn Lộc", mssv="3124411158", role="Thành viên",
         task_mid="EDA (phân phối lớp, độ dài tiêu đề, Chi-square n-gram); tiền xử lý văn bản và đặc trưng hình thái học; baseline Naive Bayes",
         done="Viết hàm clean_title, morph_features; EDA mục 4.1–4.3 (biểu đồ eda_01–eda_05); chạy baseline Naive Bayes (E01)",
         files="src/eda.py, notebooks/01_EDA.ipynb, figures/eda_01…05", share="25%"),
    dict(name="Nguyễn Vĩnh Thịnh", mssv="3124411292", role="Thành viên",
         task_mid="EDA merchant & cluster; baseline phân cụm K-Means; huấn luyện cây quyết định/Random Forest; slide",
         done="EDA mục 4.4 (eda_06–eda_08); baseline K-Means C01–C04, Elbow/Silhouette; chạy E02, E07, E09; làm slide giữa kỳ",
         files="src/cluster_baseline.py, notebooks/03_Clustering_Baseline.ipynb, slide .pptx", share="25%"),
    dict(name="Mai Tấn Thiện Nhân", mssv="3124411196", role="Thành viên",
         task_mid="Thu thập/kiểm tra dữ liệu UCI; trích xuất Hybrid TF-IDF; đánh giá (confusion matrix, per-class F1, phân tích lỗi)",
         done="Tải và kiểm tra chất lượng dữ liệu (trùng lặp, nhãn mâu thuẫn); cấu hình Hybrid TF-IDF; phân tích lỗi mục 6.3 (confusion matrix, top nhầm lẫn, per-class F1)",
         files="data/, notebooks/02_Classification_Baselines.ipynb, results/misclassified_*.csv", share="25%"),
]
timeline = [
    dict(week="1", task="Khảo sát bài toán, kiểm tra dữ liệu, hoàn thiện Proposal", who="Cả nhóm", status="Hoàn thành"),
    dict(week="2", task="EDA: 10 ngành hàng, 306 merchants, độ dài tiêu đề, n-gram", who="Lộc, Thịnh", status="Hoàn thành"),
    dict(week="3", task="Pipeline tiền xử lý, Hybrid TF-IDF, đặc trưng hình thái, SVD", who="Nhân, Danh", status="Hoàn thành"),
    dict(week="4", task="Huấn luyện & so sánh mô hình phân loại (baseline)", who="Nhân, Thịnh, Danh", status="Hoàn thành bước baseline; còn tinh chỉnh siêu tham số"),
    dict(week="5", task="Phân cụm (K-Means, Agglomerative, DBSCAN), t-SNE, Web Demo", who="Lộc, Danh, Thịnh", status="Mới có baseline K-Means"),
    dict(week="6", task="Phân tích lỗi, báo cáo cuối kỳ, slide", who="Cả nhóm", status="Chưa thực hiện"),
]
attributes = [
    ["Product ID", "Integer", "Định danh (loại bỏ)", f"{len(df):,} giá trị duy nhất".replace(",", ".")],
    ["Product Title", "Text", "Đặc trưng chính (Input)", f"TB {eda['words_mean']} từ, {eda['chars_mean']} ký tự; {eda['pct_titles_with_alnum']}% có mã chữ-số"],
    ["Merchant ID", "Integer (định danh)", "Đặc trưng phụ (Input)", f"{eda['n_merchants']} merchant"],
    ["Cluster ID", "Integer", "Nhãn đối chiếu phân cụm; nhóm cho Group split", f"{eda['n_clusters']:,} cụm".replace(",", ".")],
    ["Cluster Label", "Text", "Tên chuẩn của cụm (không dùng làm đặc trưng)", f"{eda['n_clusters']:,} nhãn".replace(",", ".")],
    ["Category ID", "Integer", "Biến mục tiêu (dạng mã)", "10 giá trị (2612–2623)"],
    ["Category Label", "Categorical", "Biến mục tiêu", "10 lớp (Hình 1)"],
]
S = lambda n: f"{n:,}".replace(",", ".")
data_stats = [
    ["Số mẫu / số cột", f"{S(eda['n_rows'])} / 7"], ["Số ngành hàng (lớp)", "10"],
    ["Số merchant", str(eda["n_merchants"])], ["Số cụm thực thể (Cluster ID)", S(eda["n_clusters"])],
    ["Giá trị khuyết", str(eda["missing_total"])],
    ["Tiêu đề trùng lặp (sau lowercase)", S(eda["dup_titles"])],
    ["Bản ghi trùng (title, merchant, category)", S(eda["dup_rows"])],
    ["Tiêu đề trùng nhưng khác nhãn ngành", str(eda["titles_with_conflicting_labels"])],
    ["Tỷ lệ lớp lớn nhất / nhỏ nhất", f"{eda['imbalance_ratio']} (Fridge Freezers / Freezers)"],
    ["Số từ / tiêu đề: TB – trung vị – min – max", f"{eda['words_mean']} – {eda['words_median']:.0f} – {eda['words_min']} – {eda['words_max']}"],
    ["Cụm chỉ có 1 offer", S(eda["singleton_clusters"])],
    ["Kích thước cụm: TB – trung vị – max", f"{eda['cluster_size_mean']} – {eda['cluster_size_median']:.0f} – {eda['cluster_size_max']}"],
    ["Merchant chỉ bán 1 ngành", f"{eda['merchants_single_category']} / {eda['n_merchants']}"],
    ["Tỷ trọng offer của 20 merchant lớn nhất", f"{eda['top20_merchant_share_pct']}%"],
]
clu_rows = [dict(r, space=r["features"].replace("Word TF-IDF(1,2) -> ", "").replace(" -> ", " + ")) for r in clu.to_dict("records")]
best_clu = clu.sort_values("nmi_vs_category", ascending=False).iloc[0]["exp_id"]

out = dict(best_id=best, best_clu=best_clu, n_test=int(main.n_test.iloc[0]), n_train=int(main.n_train.iloc[0]),
           cls_main=main.to_dict("records"), ablation=abl, group=grp, top_conf=top_conf, clu=clu_rows,
           members=members, timeline=timeline, attributes=attributes, data_stats=data_stats, eda=eda,
           class_dist=cdist.reset_index().values.tolist())
json.dump(json.loads(json.dumps(out, default=float).replace("NaN", "null")), open(RES_DIR / "report_data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ["best_id", "ablation", "group", "top_conf"]}, ensure_ascii=False, indent=1, default=float))
