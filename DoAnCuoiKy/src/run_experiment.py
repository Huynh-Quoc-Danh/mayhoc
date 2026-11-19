"""Chạy MỘT thí nghiệm phân loại với cấu hình do người chạy chọn, rồi TỰ ĐỘNG ghi nhật ký.

Mục đích: mỗi thành viên thay đổi tham số, chạy từng lần một (không chạy một lèo),
mỗi lần chạy sinh một dòng trong experiments/<thanh_vien>/experiment_log.csv
kèm thời điểm chạy, commit git hiện tại, tham số, độ đo. Cột "nhan_xet" để TRỐNG
- người chạy tự điền nhận xét / rút ra được gì sau khi xem kết quả.

Ví dụ (chạy từ thư mục gốc repo):
    python src/run_experiment.py --member loc --model nb --features word --param alpha=0.5
    python src/run_experiment.py --member danh --model svc --features hybrid --param C=0.3 --cv
    python src/run_experiment.py --member nhan --model xgb --features svd --svd 100 --param max_depth=4
    python src/run_experiment.py --member danh --model svc --features full --split group

Trong notebook: from run_experiment import run; run(member="loc", model="nb", ...)
"""
from __future__ import annotations

import argparse
import ast
import shlex
import sys
import time

from sklearn.compose import ColumnTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.base import clone
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import GroupShuffleSplit, StratifiedKFold, train_test_split
from sklearn.naive_bayes import ComplementNB, MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from common import RANDOM_STATE, ROOT, MerchantPrior, MorphFeatures, clean_title, load_data
from exp_logger import _git_commit, log_run
from run_artifacts import RunLog, save_classification_run
from train_baselines import TOKEN, metrics

# ---------------------------------------------------------------- 1. Mô hình
# Mỗi khóa là tên ngắn dùng trên dòng lệnh; giá trị là hàm tạo mô hình từ dict tham số.
# Tham số không truyền vào sẽ dùng giá trị mặc định của scikit-learn.
MODELS = {
    "nb": lambda p: MultinomialNB(**p),                       # alpha: độ làm trơn Laplace
    "cnb": lambda p: ComplementNB(**p),                       # biến thể NB cho dữ liệu lệch lớp
    "lr": lambda p: LogisticRegression(max_iter=3000, **p),   # C: nghịch đảo cường độ phạt L2
    "svc": lambda p: LinearSVC(**p),                          # C, class_weight="balanced"
    "dt": lambda p: DecisionTreeClassifier(random_state=RANDOM_STATE, **p),  # max_depth, min_samples_leaf
    "rf": lambda p: RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1, **p),
    "hgb": lambda p: HistGradientBoostingClassifier(random_state=RANDOM_STATE, **p),
}


def _xgb(p):
    """XGBoost thật (cần `pip install xgboost`). Nhãn chuỗi được mã hóa bên trong."""
    from train_baselines import boosting
    name, model, _ = boosting()
    if not name.startswith("XGBoost"):
        raise SystemExit("Máy này chưa cài xgboost: chạy `pip install xgboost` rồi thử lại.")
    return model.set_params(**p)


MODELS["xgb"] = _xgb


# ---------------------------------------------------------------- 2. Đặc trưng
def build_features(kind: str, word_ngram=(1, 2), char_ngram=(3, 5), min_df=2, svd=150):
    """Trả về ColumnTransformer biến đổi DataFrame (clean, merchant_id) thành ma trận đặc trưng.

    kind:
      word   - chỉ TF-IDF theo từ
      char   - chỉ TF-IDF theo n-gram ký tự (char_wb)
      hybrid - word + char
      full   - hybrid + 5 đặc trưng hình thái + P(ngành | merchant)
      svd    - full nhưng phần văn bản được nén bằng TruncatedSVD (cho mô hình cây)
    """
    word = TfidfVectorizer(ngram_range=word_ngram, min_df=min_df, sublinear_tf=True, token_pattern=TOKEN)
    char = TfidfVectorizer(analyzer="char_wb", ngram_range=char_ngram, min_df=max(min_df, 3),
                           sublinear_tf=True, max_features=200_000)
    if kind == "word":
        return ColumnTransformer([("txt", word, "clean")])
    if kind == "char":
        return ColumnTransformer([("txt", char, "clean")])
    text = FeatureUnion([("word", word), ("char", char)])
    if kind == "hybrid":
        return ColumnTransformer([("txt", text, "clean")])
    if kind == "svd":
        text = Pipeline([("tfidf", text), ("svd", TruncatedSVD(svd, random_state=RANDOM_STATE))])
    parts = [("txt", text, "clean"), ("morph", MorphFeatures(), "clean"), ("merch", MerchantPrior(), ["merchant_id"])]
    return ColumnTransformer(parts, sparse_threshold=0.0 if kind == "svd" else 0.3)


def _parse_params(items):
    """Đổi ["C=0.5", "class_weight='balanced'"] thành {"C": 0.5, "class_weight": "balanced"}."""
    out = {}
    for it in items or []:
        k, v = it.split("=", 1)
        try:
            out[k] = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            out[k] = v  # để nguyên chuỗi, ví dụ class_weight=balanced
    return out


# ---------------------------------------------------------------- 3. Chạy + ghi nhật ký
def run(member, model, features="word", params=None, split="strat", cv=False,
        word_ngram=(1, 2), char_ngram=(3, 5), min_df=2, svd=150, exp_name="", show_report=True,
        save_model=False, command=None):
    params = params or {}
    log = RunLog()
    log(f"Bắt đầu: member={member} model={model} features={features} params={params} split={split} cv={cv}")
    df = load_data()
    df["clean"] = df["title"].map(clean_title)
    X, y = df[["clean", "merchant_id"]], df["category_label"].values
    log(f"Đọc dữ liệu: {len(df)} tiêu đề, {df.category_label.nunique()} ngành")

    # Chia dữ liệu: strat = Stratified 80/20; group = không để cùng 1 sản phẩm (Cluster ID) ở cả 2 tập
    if split == "group":
        tr, te = next(GroupShuffleSplit(1, test_size=0.2, random_state=RANDOM_STATE).split(X, y, df["cluster_id"]))
        Xtr, Xte, ytr, yte = X.iloc[tr], X.iloc[te], y[tr], y[te]
    else:
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
    log(f"Chia dữ liệu ({split}): Train {len(Xtr)}, Test {len(Xte)}")

    pipe = Pipeline([("f", build_features(features, word_ngram, char_ngram, min_df, svd)),
                     ("clf", MODELS[model](params))])
    res, folds = {}, []
    if cv:  # 5-fold CV trên tập Train (chậm hơn, dùng khi muốn so sánh nghiêm túc) – ghi điểm TỪNG fold
        t0 = time.time()
        skf = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)
        for k, (a, b) in enumerate(skf.split(Xtr, ytr)):
            t = time.time(); m = clone(pipe).fit(Xtr.iloc[a], ytr[a]); tt = time.time() - t
            pv = m.predict(Xtr.iloc[b])
            folds.append(dict(fold=k, n_train=len(a), n_val=len(b), f1_macro=f1_score(ytr[b], pv, average="macro"),
                              accuracy=accuracy_score(ytr[b], pv), train_time_s=tt))
            log(f"Fold {k}: train {len(a)} / val {len(b)} – Macro-F1 {folds[-1]['f1_macro']:.4f}, "
                f"Accuracy {folds[-1]['accuracy']:.4f}, {tt:.1f}s")
        f1s = [f["f1_macro"] for f in folds]
        res.update(cv_f1_macro_mean=float(sum(f1s) / len(f1s)),
                   cv_f1_macro_std=float((sum((v - sum(f1s) / len(f1s)) ** 2 for v in f1s) / len(f1s)) ** 0.5),
                   cv_time_s=time.time() - t0)
        log(f"CV 5-fold: {res['cv_f1_macro_mean']:.4f} ± {res['cv_f1_macro_std']:.4f}")
    t = time.time(); pipe.fit(Xtr, ytr); res["train_time_s"] = time.time() - t
    log(f"Huấn luyện trên toàn bộ Train: {res['train_time_s']:.1f}s")
    p = pipe.predict(Xte)
    res.update({f"test_{k}": v for k, v in metrics(yte, p).items()})
    # F1 của 3 lớp dễ nhầm nhất - theo dõi riêng vì đây là trọng tâm cải tiến
    for c in ["Fridges", "Freezers", "Fridge Freezers"]:
        res[f"f1_{c.replace(' ', '_')}"] = f1_score(yte, p, labels=[c], average="macro")
    log(f"Test: Macro-F1 {res['test_f1_macro']:.4f}, Accuracy {res['test_accuracy']:.4f}, sai {int((p != yte).sum())}/{len(yte)} mẫu")

    config = dict(model=model, features=features, params=params, split=split, word_ngram=word_ngram,
                  char_ngram=char_ngram, min_df=min_df, svd=svd if features == "svd" else None)
    run_id = log_run(member, config, res, n_train=len(Xtr), n_test=len(Xte), exp_name=exp_name)
    log(f"run_id = {run_id} (đã thêm 1 dòng vào experiments/{member}/experiment_log.csv)")
    params_cfg = dict(run_id=run_id, member=member, ten_thi_nghiem=exp_name, git_commit=_git_commit(),
                      du_lieu="data/pricerunner_aggregate.csv", random_state=RANDOM_STATE, n_train=len(Xtr),
                      n_test=len(Xte), cv_folds=5 if cv else 0, **config)
    if save_model:
        import joblib
        (ROOT / "models").mkdir(exist_ok=True)
        mp = ROOT / "models" / f"{run_id}.joblib"
        joblib.dump(pipe, mp, compress=3)
        params_cfg["model_file"] = f"models/{mp.name} (không đưa lên GitHub)"
        log(f"Đã lưu mô hình: models/{mp.name}")
    cmd = command or (f"python src/run_experiment.py --member {member} --model {model} --features {features}"
                      + "".join(f" --param {k}={v!r}" if isinstance(v, str) else f" --param {k}={v}" for k, v in params.items())
                      + f" --split {split}" + (" --cv" if cv else "")
                      + f" --word-ngram {word_ngram[0]},{word_ngram[1]} --char-ngram {char_ngram[0]},{char_ngram[1]}"
                      + f" --min-df {min_df}" + (f" --svd {svd}" if features == "svd" else "")
                      + (f" --name {exp_name}" if exp_name else ""))
    test_frame = df.loc[Xte.index, ["product_id", "title"]] if "product_id" in df else df.loc[Xte.index, ["title"]]
    d = save_classification_run(member, run_id, params_cfg, res, folds, yte, p, test_frame, log, cmd)

    print(f"[{run_id}] {model}/{features} {params} split={split}")
    for k, v in res.items():
        print(f"   {k:28s} {v:.4f}")
    if show_report:
        print(classification_report(yte, p, digits=4))
    print(f"→ Đã ghi vào experiments/{member}/experiment_log.csv. Hãy mở file và điền cột nhan_xet.")
    print(f"→ Thư mục kết quả đầy đủ: {d.relative_to(ROOT)}")
    return res, pipe


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--member", required=True, choices=["danh", "loc", "thinh", "nhan"])
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--features", default="word", choices=["word", "char", "hybrid", "full", "svd"])
    ap.add_argument("--param", action="append", help="tham số mô hình dạng ten=giatri, lặp lại được")
    ap.add_argument("--split", default="strat", choices=["strat", "group"])
    ap.add_argument("--cv", action="store_true", help="chạy thêm 5-fold CV trên Train")
    ap.add_argument("--word-ngram", default="1,2"); ap.add_argument("--char-ngram", default="3,5")
    ap.add_argument("--min-df", type=int, default=2); ap.add_argument("--svd", type=int, default=150)
    ap.add_argument("--name", default="", help="tên ngắn cho thí nghiệm, ví dụ 'thu_alpha_nho'")
    ap.add_argument("--save-model", action="store_true", help="lưu mô hình ra models/<run_id>.joblib (không lên GitHub)")
    a = ap.parse_args()
    run(a.member, a.model, a.features, _parse_params(a.param), a.split, a.cv,
        tuple(map(int, a.word_ngram.split(","))), tuple(map(int, a.char_ngram.split(","))), a.min_df, a.svd, a.name,
        save_model=a.save_model, command="python " + " ".join(shlex.quote(x) for x in sys.argv))
