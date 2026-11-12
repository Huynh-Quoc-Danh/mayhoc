"""Tạo 3 notebook (01_EDA, 02_Classification_Baselines, 03_Clustering_Baseline).
Các ô code gọi lại đúng các script trong src/; output (bảng + hình) được nhúng từ lần chạy thực tế."""
import base64
import json

import pandas as pd

from common import FIG_DIR, RES_DIR, ROOT

NB = ROOT / "notebooks"; NB.mkdir(exist_ok=True)


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code(src, outputs=()):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "source": src, "outputs": list(outputs)}


def txt(s):
    return {"output_type": "stream", "name": "stdout", "text": s}


def img(name):
    b = base64.b64encode((FIG_DIR / name).read_bytes()).decode()
    return {"output_type": "display_data", "metadata": {}, "data": {"image/png": b, "text/plain": f"<{name}>"}}


def table(csv, **kw):
    df = pd.read_csv(RES_DIR / csv, **kw)
    return {"output_type": "display_data", "metadata": {},
            "data": {"text/plain": df.to_string(), "text/html": df.to_html(float_format=lambda x: f"{x:.4f}")}}


def save(name, cells):
    nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                       "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    json.dump(nb, open(NB / name, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


SETUP = "import sys, json, pandas as pd\nsys.path.append('../src')\nfrom IPython.display import Image, display\n"

eda = json.load(open(RES_DIR / "eda_summary.json", encoding="utf-8"))
save("01_EDA.ipynb", [
    md("# 01 – Khám phá dữ liệu (EDA) – PriceRunner\nNhóm 06 – Product Classification and Clustering. Notebook gọi `src/eda.py`; output bên dưới là kết quả lần chạy thực tế."),
    code(SETUP + "import eda\neda.main()", [txt(json.dumps(eda, ensure_ascii=False, indent=2))]),
    md("## Phân phối lớp"), code("pd.read_csv('../results/eda_class_distribution.csv')", [table("eda_class_distribution.csv")]),
    code("display(Image('../figures/eda_01_class_distribution.png'))", [img("eda_01_class_distribution.png")]),
    md("## Độ dài tiêu đề & mã chữ-số"),
    code("display(Image('../figures/eda_02_title_length_by_class.png'))", [img("eda_02_title_length_by_class.png")]),
    code("display(Image('../figures/eda_03_title_length_hist.png'))", [img("eda_03_title_length_hist.png")]),
    md("## Từ khóa đặc trưng (Chi-square) và chồng lấn từ vựng"),
    code("display(Image('../figures/eda_04_top_ngrams_chi2.png'))", [img("eda_04_top_ngrams_chi2.png")]),
    code("display(Image('../figures/eda_05_vocab_overlap.png'))", [img("eda_05_vocab_overlap.png")]),
    md("## Merchant và cụm thực thể"),
    code("display(Image('../figures/eda_06_merchant_category_heatmap.png'))", [img("eda_06_merchant_category_heatmap.png")]),
    code("display(Image('../figures/eda_07_merchant_ncategories.png'))", [img("eda_07_merchant_ncategories.png")]),
    code("display(Image('../figures/eda_08_cluster_size.png'))", [img("eda_08_cluster_size.png")]),
])

best = json.load(open(RES_DIR / "best_model.json"))["best_id"]
log = open(RES_DIR / "train_stdout.log", encoding="utf-8").read()
log = "\n".join(l for l in log.splitlines() if "Warning" not in l and "warn" not in l)
save("02_Classification_Baselines.ipynb", [
    md("# 02 – Baseline phân loại đa lớp\nStratified 80/20 + 5-Fold CV trên Train; thêm GroupShuffle theo Cluster ID. Gọi `src/train_baselines.py`."),
    code(SETUP + "import train_baselines\ntrain_baselines.main(fast=False)", [txt(log)]),
    code("pd.read_csv('../results/experiment_log_classification.csv')", [table("experiment_log_classification.csv")]),
    code("display(Image('../figures/res_01_model_comparison.png'))", [img("res_01_model_comparison.png")]),
    code("display(Image('../figures/res_02_confusion_matrix_best.png'))", [img("res_02_confusion_matrix_best.png")]),
    code("display(Image('../figures/res_03_per_class_f1.png'))", [img("res_03_per_class_f1.png")]),
    code("display(Image('../figures/res_04_f1_vs_time.png'))", [img("res_04_f1_vs_time.png")]),
    code(f"pd.read_csv('../results/top_confusions_{best}.csv')", [table(f"top_confusions_{best}.csv")]),
])

clog = open(RES_DIR / "cluster_stdout.log", encoding="utf-8").read()
save("03_Clustering_Baseline.ipynb", [
    md("# 03 – Baseline phân cụm (K-Means, K=10, LSA + L2)\nGọi `src/cluster_baseline.py`."),
    code(SETUP + "import cluster_baseline\ncluster_baseline.main()", [txt(clog)]),
    code("pd.read_csv('../results/experiment_log_clustering.csv')", [table("experiment_log_clustering.csv")]),
    code("display(Image('../figures/clu_01_contingency.png'))", [img("clu_01_contingency.png")]),
    code("display(Image('../figures/clu_02_elbow_silhouette.png'))", [img("clu_02_elbow_silhouette.png")]),
    code("display(Image('../figures/clu_03_svd2d.png'))", [img("clu_03_svd2d.png")]),
])
print("notebooks ok")
