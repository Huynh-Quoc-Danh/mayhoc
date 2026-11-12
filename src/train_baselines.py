"""02 - Huấn luyện và đánh giá các mô hình baseline (nhánh Phân loại).
Chạy: python src/train_baselines.py [--fast]

- Chia 80/20 Stratified theo Category (random_state=42) + 5-Fold Stratified CV trên tập Train.
- Mọi bước biến đổi (TF-IDF, SVD, scaler, merchant prior) nằm trong Pipeline -> chỉ fit trên Train/fold.
- Kết quả ghi vào results/experiment_log.csv; hình vào figures/.
"""
import argparse
import json
import time
from datetime import date

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score)
from sklearn.model_selection import (GroupShuffleSplit, StratifiedKFold, cross_validate,
                                     train_test_split)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from common import (FIG_DIR, MODEL_DIR, RANDOM_STATE, RES_DIR, MerchantPrior, MorphFeatures,
                    clean_title, load_data)

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:  # môi trường không có xgboost -> dùng HistGradientBoosting (cùng họ GBDT histogram)
    HAS_XGB = False

TOKEN = r"(?u)\b[\w\-\.\+]+\b"


# ----------------------------------------------------------------------------- features
def word_tfidf():
    return TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, token_pattern=TOKEN)


def char_tfidf():
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True,
                           max_features=200_000)


def hybrid_tfidf():
    return FeatureUnion([("word", word_tfidf()), ("char", char_tfidf())])


def text_only(vec):
    return ColumnTransformer([("txt", vec, "clean")])


def full_sparse():
    """Hybrid TF-IDF + 5 đặc trưng hình thái + P(category|merchant)."""
    return ColumnTransformer([
        ("txt", hybrid_tfidf(), "clean"),
        ("morph", MorphFeatures(), "clean"),
        ("merch", MerchantPrior(), ["merchant_id"]),
    ])


def full_dense(n_comp=150):
    """LSA (SVD trên Hybrid TF-IDF) + hình thái + merchant prior -> ma trận đặc (cho cây/boosting)."""
    return ColumnTransformer([
        ("txt", Pipeline([("tfidf", hybrid_tfidf()),
                          ("svd", TruncatedSVD(n_comp, random_state=RANDOM_STATE))]), "clean"),
        ("morph", MorphFeatures(), "clean"),
        ("merch", MerchantPrior(), ["merchant_id"]),
    ], sparse_threshold=0.0)


def boosting():
    if HAS_XGB:
        from sklearn.base import BaseEstimator, ClassifierMixin

        class XGBWrap(BaseEstimator, ClassifierMixin):
            def __init__(self, n_estimators=300, max_depth=6, learning_rate=0.1):
                self.n_estimators, self.max_depth, self.learning_rate = n_estimators, max_depth, learning_rate

            def fit(self, X, y):
                self.le_ = LabelEncoder().fit(y); self.classes_ = self.le_.classes_
                self.m_ = XGBClassifier(n_estimators=self.n_estimators, max_depth=self.max_depth,
                                        learning_rate=self.learning_rate, tree_method="hist",
                                        n_jobs=-1, random_state=RANDOM_STATE, eval_metric="mlogloss")
                self.m_.fit(X, self.le_.transform(y)); return self

            def predict(self, X):
                return self.le_.inverse_transform(self.m_.predict(X))
        return "XGBoost", XGBWrap(), {"n_estimators": 300, "max_depth": 6, "learning_rate": 0.1}
    return ("HistGradientBoosting (thay XGBoost)",
            HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, max_leaf_nodes=31,
                                           early_stopping=False, random_state=RANDOM_STATE),
            {"max_iter": 300, "learning_rate": 0.1, "max_leaf_nodes": 31})


# ----------------------------------------------------------------------------- experiments
def experiments():
    bname, bmodel, bparams = boosting()
    E = [
        dict(id="E01", model="Multinomial Naive Bayes", feats="Word TF-IDF (1,2)",
             pipe=Pipeline([("f", text_only(word_tfidf())), ("clf", MultinomialNB(alpha=0.1))]),
             params={"alpha": 0.1}, note="Baseline tham chiếu (Proposal)"),
        dict(id="E02", model="Decision Tree", feats="Word TF-IDF (1,2)",
             pipe=Pipeline([("f", text_only(word_tfidf())),
                            ("clf", DecisionTreeClassifier(criterion="gini", random_state=RANDOM_STATE))]),
             params={"criterion": "gini", "max_depth": None}, note="Baseline cây đơn"),
        dict(id="E03", model="Logistic Regression", feats="Word TF-IDF (1,2)",
             pipe=Pipeline([("f", text_only(word_tfidf())),
                            ("clf", LogisticRegression(C=10, max_iter=2000))]),
             params={"C": 10, "penalty": "l2", "solver": "lbfgs"}, note=""),
        dict(id="E04", model="LinearSVC (SVM)", feats="Word TF-IDF (1,2)",
             pipe=Pipeline([("f", text_only(word_tfidf())), ("clf", LinearSVC(C=1.0))]),
             params={"C": 1.0, "loss": "squared_hinge"}, note="Baseline SVM"),
        dict(id="E05", model="LinearSVC (SVM)", feats="Hybrid TF-IDF (word 1-2 + char_wb 3-5)",
             pipe=Pipeline([("f", text_only(hybrid_tfidf())), ("clf", LinearSVC(C=1.0))]),
             params={"C": 1.0}, note="RQ1: thêm char n-grams"),
        dict(id="E06", model="LinearSVC (SVM)", feats="Hybrid TF-IDF + Morph(5) + Merchant prior(10)",
             pipe=Pipeline([("f", full_sparse()), ("clf", LinearSVC(C=1.0))]),
             params={"C": 1.0}, note="RQ1: thêm đặc trưng hình thái + merchant"),
        dict(id="E07", model="Decision Tree", feats="SVD-150 (Hybrid TF-IDF) + Morph + Merchant prior",
             pipe=Pipeline([("f", full_dense()),
                            ("clf", DecisionTreeClassifier(random_state=RANDOM_STATE, min_samples_leaf=2))]),
             params={"svd": 150, "min_samples_leaf": 2}, note="Cây trên không gian LSA"),
        dict(id="E08", model=bname, feats="SVD-150 (Hybrid TF-IDF) + Morph + Merchant prior",
             pipe=Pipeline([("f", full_dense()), ("clf", bmodel)]),
             params={"svd": 150, **bparams}, note="Gradient boosting (thay LightGBM/XGBoost)"),
        dict(id="E09", model="Random Forest", feats="SVD-150 (Hybrid TF-IDF) + Morph + Merchant prior",
             pipe=Pipeline([("f", full_dense()),
                            ("clf", RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=RANDOM_STATE))]),
             params={"svd": 150, "n_estimators": 300}, note="Ensemble bagging"),
    ]
    return E


def metrics(y, p):
    return dict(accuracy=accuracy_score(y, p),
                precision_macro=precision_score(y, p, average="macro", zero_division=0),
                recall_macro=recall_score(y, p, average="macro", zero_division=0),
                f1_macro=f1_score(y, p, average="macro"),
                f1_weighted=f1_score(y, p, average="weighted"))


def run_one(e, Xtr, ytr, Xte, yte, split_name, cv, do_cv=True):
    pipe = e["pipe"]
    row = dict(exp_id=e["id"], date=str(date.today()), task="Classification", model=e["model"],
               features=e["feats"], params=json.dumps(e["params"], ensure_ascii=False),
               split=split_name, n_train=len(Xtr), n_test=len(Xte))
    if do_cv:
        t = time.time()
        r = cross_validate(pipe, Xtr, ytr, cv=cv, scoring=["accuracy", "f1_macro"], n_jobs=1)
        row.update(cv_folds=cv.get_n_splits(), cv_accuracy_mean=r["test_accuracy"].mean(),
                   cv_f1_macro_mean=r["test_f1_macro"].mean(), cv_f1_macro_std=r["test_f1_macro"].std(),
                   cv_time_s=time.time() - t)
    t = time.time(); pipe.fit(Xtr, ytr); row["train_time_s"] = time.time() - t
    t = time.time(); p = pipe.predict(Xte); row["infer_ms_per_1k"] = (time.time() - t) / len(Xte) * 1e6
    row.update({f"test_{k}": v for k, v in metrics(yte, p).items()})
    row["notes"] = e.get("note", "")
    print(f"{e['id']:4s} {e['model'][:28]:28s} {split_name:18s} "
          f"CV-F1={row.get('cv_f1_macro_mean', float('nan')):.4f} "
          f"Test Acc={row['test_accuracy']:.4f} F1m={row['test_f1_macro']:.4f} ({row['train_time_s']:.1f}s)", flush=True)
    return row, pipe, p


def main(fast=False):
    FIG_DIR.mkdir(exist_ok=True); RES_DIR.mkdir(exist_ok=True); MODEL_DIR.mkdir(exist_ok=True)
    df = load_data()
    df["clean"] = df["title"].map(clean_title)
    X, y = df[["clean", "merchant_id"]], df["category_label"].values
    Xtr, Xte, ytr, yte, itr, ite = train_test_split(X, y, df.index, test_size=0.2, stratify=y,
                                                    random_state=RANDOM_STATE)
    cv = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)
    split_name = "Stratified 80/20"
    rows, preds, pipes = [], {}, {}
    cache = RES_DIR / "cache"; cache.mkdir(exist_ok=True)  # lưu từng thí nghiệm để chạy tiếp nếu bị ngắt

    def cached(e, fn):
        rp, pp = cache / f"{e['id']}.json", cache / f"{e['id']}.npy"
        if rp.exists():
            print(f"{e['id']}: dùng kết quả đã lưu", flush=True)
            return json.load(open(rp, encoding="utf-8")), None, np.load(pp, allow_pickle=True)
        row, pipe, p = fn()
        json.dump(row, open(rp, "w", encoding="utf-8"), ensure_ascii=False, default=float)
        np.save(pp, np.asarray(p, dtype=object)); return row, pipe, p

    for e in experiments():
        row, pipe, p = cached(e, lambda e=e: run_one(e, Xtr, ytr, Xte, yte, split_name, cv, do_cv=not fast))
        rows.append(row); preds[e["id"]] = p; pipes[e["id"]] = pipe

    # Kịch bản Group-aware: cùng Cluster ID (cùng sản phẩm thực) không xuất hiện ở cả train và test
    gss = GroupShuffleSplit(1, test_size=0.2, random_state=RANDOM_STATE)
    gtr, gte = next(gss.split(X, y, groups=df["cluster_id"]))
    for e in experiments():
        if e["id"] not in ("E01", "E04", "E06", "E08"):
            continue
        e = dict(e, id=e["id"] + "-G", note="Group split theo Cluster ID (kiểm tra rò rỉ cùng sản phẩm)")
        row, _, _ = cached(e, lambda e=e: run_one(e, X.iloc[gtr], y[gtr], X.iloc[gte], y[gte], "GroupShuffle 80/20", cv, do_cv=False))
        rows.append(row)

    log = pd.DataFrame(rows)
    log.to_csv(RES_DIR / "experiment_log_classification.csv", index=False)

    # ---------------- Phân tích mô hình tốt nhất
    main_rows = log[log.split == split_name]
    best_id = main_rows.sort_values("test_f1_macro", ascending=False).iloc[0]["exp_id"]
    p = preds[best_id]
    labels = sorted(np.unique(y))
    rep = pd.DataFrame(classification_report(yte, p, labels=labels, output_dict=True, digits=4)).T
    rep.to_csv(RES_DIR / f"classification_report_{best_id}.csv")
    cm = confusion_matrix(yte, p, labels=labels)
    pd.DataFrame(cm, index=labels, columns=labels).to_csv(RES_DIR / f"confusion_matrix_{best_id}.csv")
    fig, ax = plt.subplots(figsize=(9, 7.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels, ax=ax, cbar=False)
    ax.set(xlabel="Dự đoán", ylabel="Thực tế", title=f"Confusion Matrix – {best_id} (tập Test)")
    plt.xticks(rotation=40, ha="right"); fig.tight_layout()
    fig.savefig(FIG_DIR / "res_02_confusion_matrix_best.png", dpi=160); plt.close(fig)

    err = df.loc[ite].assign(pred=p)
    err = err[err.category_label != err.pred][["product_id", "title", "merchant_id", "category_label", "pred"]]
    err.to_csv(RES_DIR / f"misclassified_{best_id}.csv", index=False)
    pairs = err.groupby(["category_label", "pred"]).size().sort_values(ascending=False).head(10)
    pairs.rename("count").to_csv(RES_DIR / f"top_confusions_{best_id}.csv")

    # Per-class F1 cho tất cả mô hình
    pcf = pd.DataFrame({k: f1_score(yte, v, labels=labels, average=None) for k, v in preds.items()}, index=labels)
    pcf.round(4).to_csv(RES_DIR / "per_class_f1_all_models.csv")
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.heatmap(pcf, annot=True, fmt=".3f", cmap="RdYlGn", vmin=pcf.values.min(), vmax=1, ax=ax,
                annot_kws={"size": 7.5}, cbar=False)
    ax.set_title("F1 từng ngành hàng theo mô hình (tập Test)")
    fig.tight_layout(); fig.savefig(FIG_DIR / "res_03_per_class_f1.png", dpi=160); plt.close(fig)

    # So sánh mô hình
    m = main_rows.assign(name=main_rows.exp_id + "\n" + main_rows.model.str.replace(" (thay XGBoost)", "*").str.slice(0, 22))
    fig, ax = plt.subplots(figsize=(12, 5))
    mm = m.melt(id_vars="name", value_vars=["test_accuracy", "test_f1_macro"], var_name="metric", value_name="score")
    mm["metric"] = mm.metric.map({"test_accuracy": "Accuracy", "test_f1_macro": "Macro F1"})
    sns.barplot(data=mm, x="name", y="score", hue="metric", ax=ax, palette=["#3b6fb6", "#f0a04b"])
    lo = max(0, mm.score.min() - 0.05)
    ax.set(ylim=(lo, 1.0), xlabel="", ylabel="Điểm", title="So sánh các mô hình baseline trên tập Test")
    for c in ax.containers:
        ax.bar_label(c, fmt="%.3f", fontsize=7, padding=2)
    plt.xticks(fontsize=8); fig.tight_layout()
    fig.savefig(FIG_DIR / "res_01_model_comparison.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for _, r in main_rows.iterrows():
        ax.scatter(r.train_time_s, r.test_f1_macro, s=60)
        ax.annotate(r.exp_id, (r.train_time_s, r.test_f1_macro), textcoords="offset points", xytext=(5, 3), fontsize=8)
    ax.set(xscale="log", xlabel="Thời gian huấn luyện (s, log)", ylabel="Macro F1 (Test)",
           title="Đánh đổi hiệu năng – thời gian huấn luyện")
    fig.tight_layout(); fig.savefig(FIG_DIR / "res_04_f1_vs_time.png", dpi=160); plt.close(fig)

    if pipes.get(best_id) is None:  # kết quả lấy từ cache -> huấn luyện lại mô hình tốt nhất để lưu
        pipes[best_id] = {e["id"]: e for e in experiments()}[best_id]["pipe"].fit(Xtr, ytr)
    joblib.dump(pipes[best_id], MODEL_DIR / f"best_{best_id}.joblib", compress=3)
    json.dump({"best_id": best_id, "has_xgboost": HAS_XGB}, open(RES_DIR / "best_model.json", "w"))
    print("Best:", best_id)
    print(pairs.to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--fast", action="store_true", help="bỏ qua 5-fold CV")
    main(**vars(ap.parse_args()))
