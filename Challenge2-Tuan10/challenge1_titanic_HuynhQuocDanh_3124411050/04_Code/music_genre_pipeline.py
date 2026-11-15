"""
Challenge – Kaggle: Music Genre Classification (shai-music-genre-classification)
Author : Huynh Quoc Danh - 3124411050 - Saigon University
Usage  : python music_genre_pipeline.py --data ../data --out ../outputs

Quy trình (theo "Beginner's Guide to Data Science" & "Next-Level Data Science"):
  1. EDA: phân phối lớp, missing values, lỗi đơn vị duration, đặc trưng âm thanh theo thể loại
  2. Tiền xử lý: sửa đơn vị duration, điền thiếu + cờ thiếu, one-hot key/time_signature
  3. Feature engineering: target encoding nghệ sĩ (out-of-fold, có làm trơn),
     tần suất nghệ sĩ, cờ ký tự (Hebrew/Devanagari), từ khóa tên bài (feat/live/remaster...)
  4. Mô hình: LogisticRegression, KNN, DecisionTree, RandomForest, ExtraTrees,
     HistGradientBoosting, MLP  -> Stratified 5-fold, macro-F1 / weighted-F1 / accuracy
  5. Ensemble: soft voting + stacking (meta = Logistic Regression)
  6. Sinh submission.csv (Id, Class)
"""
import argparse, json, os, re, time, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix, classification_report
from sklearn.base import clone

warnings.filterwarnings("ignore")
SEED = 42
GENRES = ["Acoustic/Folk", "Alt_Music", "Blues", "Bollywood", "Country", "HipHop",
          "Indie", "Instrumental", "Metal", "Pop", "Rock"]
AUDIO = ["Popularity", "danceability", "energy", "key", "loudness", "mode", "speechiness",
         "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"]
PAL = {"blue": "#1f4e79", "orange": "#e07b39", "grey": "#8c8c8c"}
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold"})


def savefig(fig, out, name):
    fig.tight_layout(); fig.savefig(os.path.join(out, "figures", name), bbox_inches="tight"); plt.close(fig)


def load(data):
    tr = pd.read_csv(os.path.join(data, "train.csv"))
    te = pd.read_csv(os.path.join(data, "test.csv"))
    for d in (tr, te):
        d.rename(columns={"duration_in min/ms": "duration_raw"}, inplace=True)
        # Lỗi đơn vị: giá trị < 30 là PHÚT, còn lại là mili-giây
        d["dur_in_minutes"] = (d["duration_raw"] < 30).astype(int)
        d["duration_ms"] = np.where(d["duration_raw"] < 30, d["duration_raw"] * 60000, d["duration_raw"])
        d["Artist Name"] = d["Artist Name"].fillna("").astype(str)
        d["Track Name"] = d["Track Name"].fillna("").astype(str)
    return tr, te


# ---------------------------------------------------------------- 1. EDA
def eda(tr, out):
    info = {"n_train": int(len(tr)), "n_classes": 11}
    vc = tr["Class"].value_counts().sort_index()
    info["class_counts"] = {GENRES[i]: int(v) for i, v in vc.items()}
    info["imbalance_ratio"] = round(float(vc.max() / vc.min()), 1)
    miss = (tr.isnull().mean() * 100); miss = miss[miss > 0].sort_values(ascending=False)
    info["missing_pct"] = {k: round(float(v), 1) for k, v in miss.items()}
    info["n_duration_minutes"] = int(tr["dur_in_minutes"].sum())
    info["n_artists"] = int(tr["Artist Name"].nunique())
    a = tr.groupby("Artist Name")["Class"].nunique()
    info["artist_single_class_pct"] = round(float((a == 1).mean() * 100), 1)

    # Fig1 class distribution
    fig, ax = plt.subplots(figsize=(7, 3.2))
    cols = [PAL["orange"] if v in (vc.max(), vc.min()) else PAL["blue"] for v in vc.values]
    ax.bar([GENRES[i] for i in vc.index], vc.values, color=cols)
    for i, v in enumerate(vc.values): ax.text(i, v + 40, str(v), ha="center", fontsize=7)
    ax.set_title(f"Class distribution (imbalance ratio {info['imbalance_ratio']}:1)"); ax.set_ylabel("tracks")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    savefig(fig, out, "fig1_class_distribution.png")

    # Fig2 missing + duration unit issue
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))
    ax[0].bar(miss.index, miss.values, color=PAL["blue"]); ax[0].set_title("Missing values (%)")
    for i, v in enumerate(miss.values): ax[0].text(i, v + .4, f"{v:.1f}%", ha="center", fontsize=7)
    ax[1].hist(np.log10(tr["duration_raw"]), bins=60, color=PAL["blue"])
    ax[1].axvline(np.log10(30), color=PAL["orange"], ls="--")
    ax[1].text(np.log10(30) + .1, ax[1].get_ylim()[1] * .8, f"{info['n_duration_minutes']} rows\nin minutes", color=PAL["orange"], fontsize=7)
    ax[1].set_title("duration_in min/ms: mixed units"); ax[1].set_xlabel("log10(raw value)")
    savefig(fig, out, "fig2_missing_duration.png")

    # Fig3 audio features by genre (median heatmap, z-scored)
    feats = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness",
             "liveness", "valence", "tempo", "Popularity"]
    med = tr.groupby("Class")[feats].median()
    z = (med - med.mean()) / med.std()
    fig, ax = plt.subplots(figsize=(7, 4.2))
    im = ax.imshow(z.values, cmap="RdBu_r", vmin=-2.5, vmax=2.5, aspect="auto")
    ax.set_yticks(range(11)); ax.set_yticklabels(GENRES); ax.set_xticks(range(len(feats)))
    ax.set_xticklabels(feats, rotation=45, ha="right")
    for i in range(11):
        for j in range(len(feats)):
            ax.text(j, i, f"{med.values[i, j]:.2f}" if feats[j] not in ("tempo", "Popularity", "loudness") else f"{med.values[i, j]:.0f}",
                    ha="center", va="center", fontsize=5.5, color="white" if abs(z.values[i, j]) > 1.4 else "black")
    fig.colorbar(im, fraction=.035, label="z-score of class median")
    ax.set_title("Audio profile per genre (median values)")
    savefig(fig, out, "fig3_genre_profile.png")

    # Fig4 boxplots of discriminative features
    fig, axs = plt.subplots(1, 3, figsize=(9, 3.2))
    for ax, f in zip(axs, ["energy", "acousticness", "speechiness"]):
        ax.boxplot([tr.loc[tr.Class == c, f].dropna() for c in range(11)], tick_labels=[g[:6] for g in GENRES],
                   patch_artist=True, boxprops=dict(facecolor="#cfe0f1", color=PAL["blue"]),
                   medianprops=dict(color=PAL["orange"]), flierprops=dict(markersize=1))
        ax.set_title(f); plt.setp(ax.get_xticklabels(), rotation=70, fontsize=6)
    savefig(fig, out, "fig4_feature_boxplots.png")

    # Fig5 correlation
    num = tr[AUDIO].corr()
    fig, ax = plt.subplots(figsize=(5.8, 5))
    im = ax.imshow(num, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(AUDIO))); ax.set_xticklabels(AUDIO, rotation=70, ha="right", fontsize=7)
    ax.set_yticks(range(len(AUDIO))); ax.set_yticklabels(AUDIO, fontsize=7)
    for i in range(len(AUDIO)):
        for j in range(len(AUDIO)):
            ax.text(j, i, f"{num.iloc[i, j]:.1f}", ha="center", va="center", fontsize=5)
    fig.colorbar(im, fraction=.046); ax.set_title("Correlation of audio features")
    savefig(fig, out, "fig5_correlation.png")
    return info


# ---------------------------------------------------------------- 2-3. Features
HEB = re.compile(r"[֐-׿]"); DEV = re.compile(r"[ऀ-ॿ]"); ARB = re.compile(r"[؀-ۿ]")
KW = {"kw_feat": r"\bfeat|\bft\.|\bwith\b", "kw_live": r"\blive\b", "kw_remaster": r"remaster", "kw_remix": r"remix|mix\b",
      "kw_version": r"version|edit|acoustic", "kw_from": r"from \"|soundtrack|ost\b", "kw_op": r"\bop\.|no\.|concerto|sonata|symphony|bwv|allegro|adagio|andante"}


def base_features(d, med):
    X = pd.DataFrame(index=d.index)
    for c in AUDIO:
        X[c] = d[c]
    for c in ["Popularity", "key", "instrumentalness"]:
        X[c + "_missing"] = d[c].isnull().astype(int)
    X["Popularity"] = X["Popularity"].fillna(med["Popularity"])
    X["key"] = X["key"].fillna(-1)
    X["instrumentalness"] = X["instrumentalness"].fillna(med["instrumentalness"])
    X["dur_in_minutes"] = d["dur_in_minutes"]
    X["log_duration"] = np.log1p(X.pop("duration_ms"))
    X["log_instrumental"] = np.log10(X["instrumentalness"] + 1e-6)
    X["log_speech"] = np.log10(X["speechiness"])
    X["log_acoustic"] = np.log10(X["acousticness"] + 1e-6)
    X["energy_x_loud"] = X["energy"] * X["loudness"]
    for k in range(-1, 12): X[f"key_{k}"] = (X["key"] == k).astype(int)
    for k in [1, 3, 4, 5]: X[f"ts_{k}"] = (X["time_signature"] == k).astype(int)
    X = X.drop(columns=["key", "time_signature"])
    return X


def text_features(d):
    X = pd.DataFrame(index=d.index)
    s = d["Artist Name"] + " " + d["Track Name"]
    X["has_hebrew"] = s.str.contains(HEB).astype(int)
    X["has_devanagari"] = s.str.contains(DEV).astype(int)
    X["has_arabic"] = s.str.contains(ARB).astype(int)
    X["non_ascii_ratio"] = s.apply(lambda x: sum(ord(c) > 127 for c in x) / max(len(x), 1))
    tl = d["Track Name"].str.lower()
    for k, p in KW.items(): X[k] = tl.str.contains(p, regex=True).astype(int)
    X["artist_many"] = d["Artist Name"].str.contains(",").astype(int)
    X["track_len"] = d["Track Name"].str.len()
    return X


def artist_te(tr_art, ytr, ap_art, m=2.0):
    """Target encoding nghệ sĩ: P(class | artist) làm trơn về prior với m pseudo-counts."""
    prior = np.bincount(ytr, minlength=11) / len(ytr)
    df = pd.DataFrame({"a": tr_art.values, "y": ytr})
    cnt = pd.crosstab(df.a, df.y).reindex(columns=range(11), fill_value=0)
    n = cnt.sum(1).values[:, None]
    enc = pd.DataFrame((cnt.values + m * prior) / (n + m), index=cnt.index)
    out = enc.reindex(ap_art.values)
    seen = out.notnull().all(1).values
    out = out.fillna(pd.Series(prior)).values
    freq = pd.Series(n.ravel(), index=cnt.index).reindex(ap_art.values).fillna(0).values
    return out, seen.astype(int), freq


def build(tr_df, ytr, ap_df, use_text=True, use_artist=True, inner_folds=5):
    """Ma trận đặc trưng cho tập train (OOF target-encoding) và tập áp dụng."""
    med = tr_df[["Popularity", "instrumentalness"]].median()
    Xtr, Xap = base_features(tr_df, med), base_features(ap_df, med)
    if use_text:
        Xtr = pd.concat([Xtr, text_features(tr_df)], axis=1); Xap = pd.concat([Xap, text_features(ap_df)], axis=1)
    if use_artist:
        te_tr = np.zeros((len(tr_df), 11)); seen_tr = np.zeros(len(tr_df)); f_tr = np.zeros(len(tr_df))
        ik = StratifiedKFold(inner_folds, shuffle=True, random_state=SEED + 1)
        for a, b in ik.split(tr_df, ytr):
            e, s, f = artist_te(tr_df["Artist Name"].iloc[a], ytr[a], tr_df["Artist Name"].iloc[b])
            te_tr[b], seen_tr[b], f_tr[b] = e, s, f
        te_ap, seen_ap, f_ap = artist_te(tr_df["Artist Name"], ytr, ap_df["Artist Name"])
        for k in range(11):
            Xtr[f"te_{k}"] = te_tr[:, k]; Xap[f"te_{k}"] = te_ap[:, k]
        Xtr["artist_seen"], Xap["artist_seen"] = seen_tr, seen_ap
        Xtr["artist_freq"], Xap["artist_freq"] = np.log1p(f_tr), np.log1p(f_ap)
    return Xtr.values.astype(float), Xap.values.astype(float), list(Xtr.columns)


# ---------------------------------------------------------------- 4. Models
def get_models():
    return {
        "LogisticRegression": make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=3000, class_weight="balanced")),
        "KNN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=25, weights="distance")),
        "DecisionTree": DecisionTreeClassifier(max_depth=10, min_samples_leaf=10, class_weight="balanced", random_state=SEED),
        "RandomForest": RandomForestClassifier(n_estimators=500, min_samples_leaf=2, max_features="sqrt",
                                               class_weight="balanced_subsample", n_jobs=-1, random_state=SEED),
        "ExtraTrees": ExtraTreesClassifier(n_estimators=500, min_samples_leaf=2, class_weight="balanced", n_jobs=-1, random_state=SEED),
        "HistGB": HistGradientBoostingClassifier(learning_rate=0.05, max_iter=400, max_leaf_nodes=31, min_samples_leaf=20,
                                                 l2_regularization=1.0, class_weight="balanced", random_state=SEED),
        "MLP": make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(128, 64), alpha=1e-3, early_stopping=True,
                                                             max_iter=300, random_state=SEED)),
    }


def scores(y, p):
    return {"macro_f1": float(f1_score(y, p, average="macro")), "weighted_f1": float(f1_score(y, p, average="weighted")),
            "accuracy": float(accuracy_score(y, p))}


def run_cv(tr, y, models, use_text=True, use_artist=True, folds=5, verbose=True):
    skf = StratifiedKFold(folds, shuffle=True, random_state=SEED)
    oof = {n: np.zeros((len(y), 11)) for n in models}; fold_f1 = {n: [] for n in models}; times = {n: 0. for n in models}
    for k, (a, b) in enumerate(skf.split(tr, y)):
        Xa, Xb, cols = build(tr.iloc[a].reset_index(drop=True), y[a], tr.iloc[b].reset_index(drop=True), use_text, use_artist)
        for n, m in models.items():
            t = time.time(); mm = clone(m).fit(Xa, y[a]); oof[n][b] = mm.predict_proba(Xb); times[n] += time.time() - t
            fold_f1[n].append(f1_score(y[b], oof[n][b].argmax(1), average="macro"))
        if verbose: print(f"  fold {k + 1}/{folds} done")
    return oof, fold_f1, times, cols


def main(a):
    os.makedirs(os.path.join(a.out, "figures"), exist_ok=True)
    tr, te = load(a.data)
    y = tr["Class"].values
    info = eda(tr, a.out)
    print("EDA:", {k: info[k] for k in ["n_train", "imbalance_ratio", "n_duration_minutes", "n_artists"]})

    models = get_models()
    oof, ff1, times, cols = run_cv(tr, y, models)
    info["n_features"] = len(cols)
    res = {}
    for n in models:
        s = scores(y, oof[n].argmax(1)); s["macro_f1_std"] = float(np.std(ff1[n])); s["time_s"] = round(times[n], 1)
        res[n] = s; print(f"{n:20s} macroF1 {s['macro_f1']:.4f} ± {s['macro_f1_std']:.4f}  wF1 {s['weighted_f1']:.4f}  acc {s['accuracy']:.4f}")

    # Ensembles on OOF probabilities
    top = sorted(models, key=lambda n: -res[n]["macro_f1"])[:3]
    vote = np.mean([oof[n] for n in top], axis=0)
    res["SoftVoting"] = scores(y, vote.argmax(1)); res["SoftVoting"]["members"] = top
    # Stacking: meta-LR trên xác suất OOF, đánh giá bằng CV cấp 2
    Z = np.hstack([oof[n] for n in models]); stack_oof = np.zeros((len(y), 11))
    meta = make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=3000, class_weight="balanced"))
    for b_tr, b_va in StratifiedKFold(5, shuffle=True, random_state=SEED + 7).split(Z, y):
        stack_oof[b_va] = clone(meta).fit(Z[b_tr], y[b_tr]).predict_proba(Z[b_va])
    res["Stacking"] = scores(y, stack_oof.argmax(1))
    for n in ["SoftVoting", "Stacking"]:
        print(f"{n:20s} macroF1 {res[n]['macro_f1']:.4f}  wF1 {res[n]['weighted_f1']:.4f}  acc {res[n]['accuracy']:.4f}")
    best = max(["SoftVoting", "Stacking"] + list(models), key=lambda n: res[n]["macro_f1"])
    info["best_model"] = best
    best_oof = {"SoftVoting": vote, "Stacking": stack_oof}.get(best, oof.get(best))
    pred = best_oof.argmax(1)
    rep = classification_report(y, pred, target_names=GENRES, output_dict=True)
    info["per_class_f1"] = {g: round(rep[g]["f1-score"], 3) for g in GENRES}

    # --------- Fit on full train, predict test
    Xall, Xte, cols = build(tr, y, te)
    full = {n: clone(m).fit(Xall, y) for n, m in models.items()}
    P = {n: full[n].predict_proba(Xte) for n in models}
    if best == "Stacking":
        mfit = clone(meta).fit(Z, y); final = mfit.predict_proba(np.hstack([P[n] for n in models]))
    elif best == "SoftVoting":
        final = np.mean([P[n] for n in top], axis=0)
    else:
        final = P[best]
    sub = pd.DataFrame({"Id": te["Id"], "Class": final.argmax(1)})
    sub.to_csv(os.path.join(a.out, "submission.csv"), index=False)
    for n in ["HistGB", "RandomForest"]:
        pd.DataFrame({"Id": te["Id"], "Class": P[n].argmax(1)}).to_csv(os.path.join(a.out, f"submission_{n.lower()}.csv"), index=False)
    info["test_pred_dist"] = {GENRES[i]: int(v) for i, v in pd.Series(final.argmax(1)).value_counts().sort_index().items()}

    # --------- Figures
    names = list(res.keys()); vals = [res[n]["macro_f1"] for n in names]; o = np.argsort(vals)
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.barh([names[i] for i in o], [vals[i] for i in o], color=[PAL["orange"] if names[i] in ("Stacking", "SoftVoting") else PAL["blue"] for i in o])
    for k, i in enumerate(o): ax.text(vals[i] + .004, k, f"{vals[i]:.4f}", va="center", fontsize=7)
    ax.set_xlim(0, max(vals) * 1.15); ax.set_xlabel("Macro-F1 (5-fold stratified CV, out-of-fold)"); ax.set_title("Model comparison")
    savefig(fig, a.out, "fig6_model_comparison.png")

    cm = confusion_matrix(y, pred, normalize="true")
    fig, ax = plt.subplots(figsize=(6, 5.2))
    im = ax.imshow(cm, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(11)); ax.set_xticklabels(GENRES, rotation=60, ha="right"); ax.set_yticks(range(11)); ax.set_yticklabels(GENRES)
    for i in range(11):
        for j in range(11):
            if cm[i, j] >= .01: ax.text(j, i, f"{cm[i, j]:.2f}", ha="center", va="center", fontsize=5.5, color="white" if cm[i, j] > .5 else "black")
    ax.set_xlabel("Predicted"); ax.set_ylabel("True"); fig.colorbar(im, fraction=.046)
    ax.set_title(f"Normalized confusion matrix ({best})")
    savefig(fig, a.out, "fig7_confusion_matrix.png")

    pc = pd.Series(info["per_class_f1"]).sort_values()
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    ax.barh(pc.index, pc.values, color=[PAL["orange"] if v < .3 else PAL["blue"] for v in pc.values])
    for k, v in enumerate(pc.values): ax.text(v + .01, k, f"{v:.2f}", va="center", fontsize=7)
    ax.set_xlim(0, 1.05); ax.set_title(f"Per-class F1 ({best})"); ax.set_xlabel("F1")
    savefig(fig, a.out, "fig8_per_class_f1.png")

    rf = full["RandomForest"]; imp = pd.Series(rf.feature_importances_, index=cols).sort_values().tail(15)
    fig, ax = plt.subplots(figsize=(5.5, 4))
    ax.barh(imp.index, imp.values, color=[PAL["orange"] if c.startswith(("te_", "artist")) or c.startswith("has_") else PAL["blue"] for c in imp.index])
    ax.set_title("Top-15 feature importances (Random Forest)"); ax.set_xlabel("mean decrease in impurity")
    savefig(fig, a.out, "fig9_feature_importance.png")
    info["top_features"] = [c for c in imp.index[::-1]]

    info["results"] = res
    json.dump(info, open(os.path.join(a.out, "results.json"), "w"), indent=2, ensure_ascii=False)
    pd.DataFrame({k: {kk: vv for kk, vv in v.items() if kk != "members"} for k, v in res.items()}).T.to_csv(os.path.join(a.out, "cv_results.csv"))
    print("Best:", best, "| per-class F1:", info["per_class_f1"]); print("Done ->", a.out)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--data", default="../data"); p.add_argument("--out", default="../outputs")
    main(p.parse_args())
