"""03 - Baseline nhánh Phân cụm: K-Means (K=10) trên không gian LSA chuẩn hóa L2.
Chạy: python src/cluster_baseline.py
Ghi results/experiment_log_clustering.csv và figures/clu_*.png
"""
import json
import time
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (adjusted_rand_score, davies_bouldin_score, normalized_mutual_info_score,
                             silhouette_score, v_measure_score)
from sklearn.preprocessing import Normalizer

from common import FIG_DIR, RANDOM_STATE, RES_DIR, clean_title, load_data

TOKEN = r"(?u)\b[\w\-\.\+]+\b"


def main():
    df = load_data(); df["clean"] = df["title"].map(clean_title)
    y = df["category_label"].values
    tf = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, token_pattern=TOKEN)
    Xt = tf.fit_transform(df["clean"])
    rows, store = [], {}
    rng = np.random.RandomState(RANDOM_STATE)
    sidx = rng.choice(len(df), size=min(10000, len(df)), replace=False)  # silhouette trên mẫu 10k
    for i, (m, algo) in enumerate([(50, "KMeans"), (100, "KMeans"), (150, "KMeans"), (100, "MiniBatchKMeans")]):
        t = time.time()
        Z = TruncatedSVD(m, random_state=RANDOM_STATE).fit_transform(Xt)
        Z = Normalizer().fit_transform(Z)
        km = (KMeans(10, n_init=10, random_state=RANDOM_STATE) if algo == "KMeans"
              else MiniBatchKMeans(10, n_init=10, batch_size=2048, random_state=RANDOM_STATE))
        lab = km.fit_predict(Z)
        row = dict(exp_id=f"C0{i+1}", date=str(date.today()), task="Clustering", model=algo,
                   features=f"Word TF-IDF(1,2) -> SVD-{m} -> L2", params=json.dumps({"K": 10, "n_init": 10, "svd": m}),
                   split="Toàn bộ 35.311 mẫu (không dùng nhãn khi huấn luyện)", n_train=len(df), n_test=0,
                   silhouette_cosine=silhouette_score(Z[sidx], lab[sidx], metric="cosine"),
                   davies_bouldin=davies_bouldin_score(Z, lab),
                   ari_vs_category=adjusted_rand_score(y, lab), nmi_vs_category=normalized_mutual_info_score(y, lab),
                   v_measure_vs_category=v_measure_score(y, lab), train_time_s=time.time() - t,
                   notes="Baseline phân cụm vĩ mô (Proposal: K-Means K=10)")
        rows.append(row); store[row["exp_id"]] = (Z, lab)
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items() if k not in ("params",)}, flush=True)
    log = pd.DataFrame(rows); log.to_csv(RES_DIR / "experiment_log_clustering.csv", index=False)

    best = log.sort_values("nmi_vs_category", ascending=False).iloc[0]["exp_id"]
    Z, lab = store[best]
    ct = pd.crosstab(pd.Series(y, name="Ngành thực tế"), pd.Series(lab, name="Cụm K-Means"))
    ct.to_csv(RES_DIR / f"cluster_contingency_{best}.csv")
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(ct.div(ct.sum(axis=1), axis=0), annot=ct.values, fmt="d", cmap="Blues", ax=ax, cbar=False, annot_kws={"size": 7})
    ax.set_title(f"Bảng đối chiếu Ngành thực tế × Cụm K-Means ({best})")
    fig.tight_layout(); fig.savefig(FIG_DIR / "clu_01_contingency.png", dpi=160); plt.close(fig)

    # Elbow + silhouette theo K (SVD-100)
    Z100 = store["C02"][0]
    ks, inert, sil = list(range(4, 21, 2)), [], []
    for k in ks:
        kmk = KMeans(k, n_init=5, random_state=RANDOM_STATE).fit(Z100)
        inert.append(kmk.inertia_); sil.append(silhouette_score(Z100[sidx], kmk.labels_[sidx], metric="cosine"))
    pd.DataFrame({"K": ks, "inertia": inert, "silhouette": sil}).to_csv(RES_DIR / "cluster_elbow.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4.5)); ax2 = ax.twinx()
    ax.plot(ks, inert, "o-", color="#3b6fb6", label="Inertia"); ax2.plot(ks, sil, "s--", color="#e07b39", label="Silhouette")
    ax.set(xlabel="K", ylabel="Inertia", title="Elbow & Silhouette theo số cụm K (SVD-100)"); ax2.set_ylabel("Silhouette (cosine)")
    fig.legend(loc="upper right", bbox_to_anchor=(0.88, 0.85)); fig.tight_layout()
    fig.savefig(FIG_DIR / "clu_02_elbow_silhouette.png", dpi=160); plt.close(fig)

    # Chiếu 2D (2 thành phần SVD đầu) để minh họa – t-SNE/UMAP để giai đoạn cuối kỳ
    P = TruncatedSVD(2, random_state=RANDOM_STATE).fit_transform(Z100)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, c, t in [(axes[0], y, "Màu theo ngành thực tế"), (axes[1], store[best][1].astype(str), "Màu theo cụm K-Means")]:
        sns.scatterplot(x=P[sidx, 0], y=P[sidx, 1], hue=np.asarray(c)[sidx], s=4, linewidth=0, ax=ax, palette="tab10", legend=ax is axes[0])
        ax.set(title=t, xlabel="SVD-1", ylabel="SVD-2")
    axes[0].legend(fontsize=7, markerscale=3, loc="best")
    fig.tight_layout(); fig.savefig(FIG_DIR / "clu_03_svd2d.png", dpi=160); plt.close(fig)
    print("best", best)


if __name__ == "__main__":
    main()
