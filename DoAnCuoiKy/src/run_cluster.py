"""Chạy MỘT cấu hình phân cụm K-Means và lưu thư mục kết quả đầy đủ (giống run_experiment.py).

Biểu diễn giống notebook 07: TF-IDF word (1,2) → TruncatedSVD → chuẩn hóa độ dài (L2).
Chạy K-Means với nhiều seed để xem độ ổn định (tương tự các fold của CV), rồi lưu:
    experiments/<member>/runs/<run_id>/
        params_cfg.json, metrics.json, metrics_seeds.csv, metrics_seeds_mean.json,
        cluster_labels.csv, cluster_vs_category.csv, cluster_purity.csv, train.log.txt, README.md
và thêm 1 dòng vào experiments/<member>/cluster_log.csv (cột nhan_xet, rut_ra để trống).

    python src/run_cluster.py --member thinh --k 10 --svd 50 --name kmeans_final
"""
from __future__ import annotations

import argparse
import shlex
import sys
import time

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score
from sklearn.preprocessing import Normalizer

from common import ROOT, clean_title, load_data
from exp_logger import _git_commit, log_generic
from run_artifacts import RunLog, save_cluster_run

TOKEN = r"(?u)\b[\w\-\.\+]+\b"


def _sil(Z, lab):
    s = np.random.RandomState(42).choice(len(Z), min(10000, len(Z)), replace=False)
    return silhouette_score(Z[s], lab[s], metric="cosine")


def run(member="thinh", k=10, svd=50, n_init=10, seeds=(42, 0, 1, 2, 3), exp_name="", command=None):
    log = RunLog()
    log(f"Bắt đầu: K-Means K={k}, SVD {svd}, n_init={n_init}, seeds={list(seeds)}")
    df = load_data(); df["clean"] = df.title.map(clean_title); y = df.category_label.values
    t = time.time()
    Xt = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, token_pattern=TOKEN).fit_transform(df.clean)
    Z = Normalizer().fit_transform(TruncatedSVD(svd, random_state=42).fit_transform(Xt))
    log(f"Biểu diễn: TF-IDF {Xt.shape[1]} cột → SVD {svd} chiều, {time.time() - t:.1f}s")

    rows, best = [], None
    for sd in seeds:
        t = time.time(); km = KMeans(k, n_init=n_init, random_state=sd).fit(Z); tt = time.time() - t
        r = dict(seed=sd, inertia=km.inertia_, silhouette=_sil(Z, km.labels_),
                 ari=adjusted_rand_score(y, km.labels_), nmi=normalized_mutual_info_score(y, km.labels_), fit_time_s=tt)
        rows.append(r)
        log(f"Seed {sd}: NMI {r['nmi']:.4f}, ARI {r['ari']:.4f}, Silhouette {r['silhouette']:.4f}, {tt:.1f}s")
        if sd == seeds[0]:
            best = km
    lab = best.labels_
    main = {kk: v for kk, v in rows[0].items() if kk != "seed"}
    log(f"Kết quả chính (seed {seeds[0]}): NMI {main['nmi']:.4f}, ARI {main['ari']:.4f}")
    nm = [r["nmi"] for r in rows]
    log(f"Độ ổn định qua {len(seeds)} seed: NMI {np.mean(nm):.4f} ± {np.std(nm):.4f}")

    run_id = log_generic(member, "cluster_log", dict(algo="kmeans", K=k, svd=svd, n_clusters=k, noise_pct=0.0,
                                                     silhouette=main["silhouette"], ari=main["ari"], nmi=main["nmi"],
                                                     n_sample=len(df), ten_thi_nghiem=exp_name))
    log(f"run_id = {run_id} (đã thêm 1 dòng vào experiments/{member}/cluster_log.csv)")
    params = dict(run_id=run_id, member=member, ten_thi_nghiem=exp_name, git_commit=_git_commit(),
                  du_lieu="data/pricerunner_aggregate.csv", n_mau=len(df), bieu_dien="TF-IDF word (1,2) + SVD + L2",
                  tfidf=dict(ngram_range=[1, 2], min_df=2, sublinear_tf=True, token_pattern=TOKEN),
                  svd=svd, algo="kmeans", K=k, n_init=n_init, seeds=list(seeds), seed_chinh=seeds[0])
    labels = df[["product_id", "title", "category_label"]].assign(cum=lab)
    ct = pd.crosstab(pd.Series(lab, name="cum"), pd.Series(y, name="nganh"))
    cmd = command or f"python src/run_cluster.py --member {member} --k {k} --svd {svd}" + (f" --name {exp_name}" if exp_name else "")
    d = save_cluster_run(member, run_id, params, main, rows, labels, ct, log, cmd)
    print("\n".join(log.lines))
    print(f"→ Thư mục kết quả đầy đủ: {d.relative_to(ROOT)}")
    return main, lab


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--member", default="thinh", choices=["danh", "loc", "thinh", "nhan"])
    ap.add_argument("--k", type=int, default=10); ap.add_argument("--svd", type=int, default=50)
    ap.add_argument("--n-init", type=int, default=10); ap.add_argument("--name", default="")
    a = ap.parse_args()
    run(a.member, a.k, a.svd, a.n_init, exp_name=a.name, command="python " + " ".join(shlex.quote(x) for x in sys.argv))
