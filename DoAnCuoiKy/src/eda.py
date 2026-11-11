"""01 - Khám phá dữ liệu (EDA). Chạy: python src/eda.py
Xuất biểu đồ vào figures/ và bảng thống kê vào results/eda_*.csv
"""
from collections import Counter
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import chi2

from common import FIG_DIR, RES_DIR, clean_title, load_data, morph_features

sns.set_theme(style="whitegrid", font_scale=0.95)
FIG_DIR.mkdir(exist_ok=True); RES_DIR.mkdir(exist_ok=True)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG_DIR / name, dpi=160)
    plt.close(fig)


def main():
    df = load_data()
    df["clean"] = df["title"].map(clean_title)
    stats = {
        "n_rows": len(df), "n_cols": df.shape[1] - 1,
        "n_categories": df["category_label"].nunique(),
        "n_merchants": df["merchant_id"].nunique(),
        "n_clusters": df["cluster_id"].nunique(),
        "missing_total": int(df.isna().sum().sum()),
        "dup_rows": int(df.duplicated(subset=["title", "merchant_id", "category_label"]).sum()),
        "dup_titles": int(df["title"].str.lower().duplicated().sum()),
        "singleton_clusters": int((df["cluster_id"].value_counts() == 1).sum()),
    }
    # Tiêu đề trùng nhưng khác nhãn ngành -> nhiễu nhãn
    g = df.groupby(df["clean"])["category_label"].nunique()
    stats["titles_with_conflicting_labels"] = int((g > 1).sum())

    # 1. Phân phối lớp
    cnt = df["category_label"].value_counts()
    cnt.rename("count").to_frame().assign(pct=lambda d: (d["count"] / len(df) * 100).round(2)) \
        .to_csv(RES_DIR / "eda_class_distribution.csv")
    stats["imbalance_ratio"] = round(cnt.max() / cnt.min(), 2)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(x=cnt.values, y=cnt.index, ax=ax, color="#3b6fb6")
    for i, v in enumerate(cnt.values):
        ax.text(v + 50, i, f"{v:,} ({v/len(df):.1%})", va="center", fontsize=8)
    ax.set(xlabel="Số mẫu", ylabel="", title="Phân phối 10 ngành hàng (Category Label)")
    save(fig, "eda_01_class_distribution.png")

    # 2. Độ dài tiêu đề theo ngành
    mf = morph_features(df["title"])
    mf["category"] = df["category_label"]
    mf.groupby("category").agg(["mean", "median"]).round(2).to_csv(RES_DIR / "eda_title_length_by_class.csv")
    stats.update({
        "words_mean": round(mf["n_words"].mean(), 2), "words_median": float(mf["n_words"].median()),
        "words_min": int(mf["n_words"].min()), "words_max": int(mf["n_words"].max()),
        "chars_mean": round(mf["n_chars"].mean(), 2),
        "pct_titles_with_alnum": round((mf["n_alnum"] > 0).mean() * 100, 2),
    })
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    order = cnt.index
    sns.boxplot(data=mf, y="category", x="n_words", order=order, ax=axes[0], color="#8fb3e0", fliersize=1)
    axes[0].set(title="Số từ trong tiêu đề theo ngành", xlabel="Số từ", ylabel="")
    sns.boxplot(data=mf, y="category", x="n_alnum", order=order, ax=axes[1], color="#f0b27a", fliersize=1)
    axes[1].set(title="Số token chữ-số (mã model) theo ngành", xlabel="Số token alphanumeric", ylabel="")
    save(fig, "eda_02_title_length_by_class.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(mf["n_words"], bins=range(0, int(mf["n_words"].max()) + 2), ax=ax, color="#3b6fb6")
    ax.set(title="Phân phối số từ / tiêu đề", xlabel="Số từ", ylabel="Số mẫu")
    save(fig, "eda_03_title_length_hist.png")

    # 3. Từ khóa đặc trưng theo ngành (Chi-square)
    cv = CountVectorizer(ngram_range=(1, 2), min_df=5, binary=True, token_pattern=r"(?u)\b[\w\-\.\+]+\b")
    X = cv.fit_transform(df["clean"])
    vocab = np.array(cv.get_feature_names_out())
    rows = []
    fig, axes = plt.subplots(2, 5, figsize=(18, 7.5))
    for ax, c in zip(axes.ravel(), order):
        yb = (df["category_label"] == c).values
        sc, _ = chi2(X, yb)
        sc = np.nan_to_num(sc)
        pos = np.asarray(X[yb].mean(0)).ravel() > np.asarray(X[~yb].mean(0)).ravel()
        sc[~pos] = 0
        top = np.argsort(sc)[::-1][:10]
        rows += [{"category": c, "rank": r + 1, "ngram": vocab[i], "chi2": round(sc[i], 1)} for r, i in enumerate(top)]
        ax.barh(vocab[top][::-1], sc[top][::-1], color="#3b6fb6")
        ax.set_title(c, fontsize=10); ax.tick_params(labelsize=8)
    fig.suptitle("Top-10 n-gram đặc trưng từng ngành (Chi-square, one-vs-rest)")
    save(fig, "eda_04_top_ngrams_chi2.png")
    pd.DataFrame(rows).to_csv(RES_DIR / "eda_top_ngrams_chi2.csv", index=False)

    # Top unigram toàn tập
    uni = Counter(w for t in df["clean"] for w in t.split())
    pd.DataFrame(uni.most_common(50), columns=["token", "freq"]).to_csv(RES_DIR / "eda_top_unigrams.csv", index=False)

    # 4. Chồng lấn từ vựng giữa các lớp (Jaccard trên tập từ có tần suất >= 5)
    voc = {c: {w for w, n in Counter(w for t in df.loc[df.category_label == c, "clean"] for w in t.split()).items() if n >= 5}
           for c in order}
    jac = pd.DataFrame([[len(voc[a] & voc[b]) / len(voc[a] | voc[b]) for b in order] for a in order], index=order, columns=order)
    jac.round(3).to_csv(RES_DIR / "eda_vocab_jaccard.csv")
    fig, ax = plt.subplots(figsize=(8.5, 7))
    sns.heatmap(jac, annot=True, fmt=".2f", cmap="Blues", ax=ax, cbar=False, annot_kws={"size": 8})
    ax.set(title="Độ chồng lấn từ vựng giữa các ngành (Jaccard)", xlabel="", ylabel="")
    save(fig, "eda_05_vocab_overlap.png")

    # 5. Merchant
    mc = df["merchant_id"].value_counts()
    stats.update({"merchant_offers_median": float(mc.median()), "merchant_offers_max": int(mc.max()),
                  "top20_merchant_share_pct": round(mc.head(20).sum() / len(df) * 100, 2)})
    ncat = df.groupby("merchant_id")["category_label"].nunique()
    stats["merchants_single_category"] = int((ncat == 1).sum())
    purity = df.groupby("merchant_id")["category_label"].agg(lambda s: s.value_counts(normalize=True).iloc[0])
    stats["merchant_purity_weighted"] = round(float((purity * mc.reindex(purity.index)).sum() / len(df)), 4)
    top = mc.head(30).index
    ct = pd.crosstab(df.loc[df.merchant_id.isin(top), "merchant_id"], df["category_label"]).reindex(top)[order]
    fig, ax = plt.subplots(figsize=(10, 9))
    sns.heatmap(ct, cmap="YlGnBu", ax=ax, cbar_kws={"label": "Số mẫu"})
    ax.set(title="Ma trận Merchant (top-30) × Ngành hàng", xlabel="", ylabel="Merchant ID")
    save(fig, "eda_06_merchant_category_heatmap.png")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(ncat, bins=range(1, 12), discrete=True, ax=ax, color="#3b6fb6")
    ax.set(title="Số ngành hàng mỗi merchant kinh doanh", xlabel="Số ngành", ylabel="Số merchant")
    save(fig, "eda_07_merchant_ncategories.png")

    # 6. Cụm thực thể
    cs = df["cluster_id"].value_counts()
    stats.update({"cluster_size_mean": round(cs.mean(), 2), "cluster_size_median": float(cs.median()),
                  "cluster_size_max": int(cs.max())})
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(cs.clip(upper=30), bins=30, ax=ax, color="#3b6fb6")
    ax.set(title="Kích thước cụm thực thể (Cluster ID), cắt ở 30", xlabel="Số offer / cụm", ylabel="Số cụm")
    save(fig, "eda_08_cluster_size.png")

    # 7. Tiêu đề KHÔNG chứa từ khóa hiển nhiên của ngành (chỉ có hãng + mã model, hoặc tiếng Đức)
    kw = {"Fridge Freezers": "fridge|freezer", "Fridges": "fridge|larder|hlschrank|refrigerator|cooler",
          "Freezers": "freezer|gefrier", "Mobile Phones": "phone|sim|smartphone|mobile",
          "TVs": r"\btv|television|led|oled|qled", "CPUs": "processor|cpu|intel|amd",
          "Dishwashers": "dishwasher|geschirr", "Washing Machines": "wash|washer",
          "Digital Cameras": "camera|kamera", "Microwaves": "microwave|mikrowelle|oven"}
    low = df["title"].str.lower()
    nokw = {c: float((~low[df.category_label == c].str.contains(k)).mean()) for c, k in kw.items()}
    pd.Series(nokw, name="pct_no_keyword").mul(100).round(1).to_csv(RES_DIR / "eda_titles_without_keyword.csv")
    stats["pct_titles_without_category_keyword"] = round(
        sum(nokw[c] * cnt[c] for c in kw) / len(df) * 100, 1)

    with open(RES_DIR / "eda_summary.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(df[["title", "clean", "category_label"]].sample(8, random_state=1).to_string())


if __name__ == "__main__":
    main()
