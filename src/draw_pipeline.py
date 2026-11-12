"""Vẽ sơ đồ pipeline học máy -> figures/method_pipeline.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from common import FIG_DIR

fig, ax = plt.subplots(figsize=(14, 6.2))
ax.set_xlim(0, 14); ax.set_ylim(0, 6.2); ax.axis("off")


def box(x, y, w, h, text, fc, fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12", fc=fc, ec="#33475b", lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, weight="bold" if bold else None, wrap=True)


def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13, color="#33475b", lw=1.1))


B, G, O, P = "#dbe8f7", "#dff2e1", "#fde9d4", "#ece3f5"
box(0.2, 2.6, 1.9, 1.1, "PriceRunner CSV\n35.311 offers\n306 merchants", B, bold=True)
box(2.5, 2.6, 2.0, 1.1, "Tiền xử lý\nlowercase, chuẩn hóa\nđơn vị, giữ mã chữ-số", B)
box(4.9, 2.6, 1.9, 1.1, "Chia dữ liệu\nStratified 80/20\n(+ Group theo Cluster)", B)
arrow(2.1, 3.15, 2.5, 3.15); arrow(4.5, 3.15, 4.9, 3.15)

ax.text(10.1, 6.0, "Nhánh 1 – Phân loại (có giám sát, 5-Fold CV trên Train)", ha="center", fontsize=10, weight="bold", color="#1f4e79")
box(7.3, 4.6, 2.3, 1.0, "Word TF-IDF (1,2)\n+ Char_wb TF-IDF (3,5)", G)
box(7.3, 3.45, 2.3, 0.9, "Morph(5) + P(cat|merchant)\nfit chỉ trên Train", G)
box(10.0, 4.6, 3.8, 1.0, "Mô hình tuyến tính trên ma trận thưa:\nNaive Bayes · Logistic · LinearSVC · Decision Tree", O)
box(10.0, 3.45, 3.8, 0.9, "SVD-150 (LSA) → mô hình cây/ensemble:\nDecision Tree · HistGB (≈XGBoost) · Random Forest", O)
arrow(9.6, 5.1, 10.0, 5.1); arrow(9.6, 3.9, 10.0, 3.9)
arrow(6.8, 3.3, 7.3, 4.9); arrow(6.8, 3.2, 7.3, 3.9)

ax.text(10.1, 2.35, "Nhánh 2 – Phân cụm (không giám sát)", ha="center", fontsize=10, weight="bold", color="#5b2c83")
box(7.3, 1.0, 2.3, 1.0, "TF-IDF → SVD (50/100/150)\n→ chuẩn hóa L2", P)
box(10.0, 1.0, 3.8, 1.0, "K-Means / MiniBatch K-Means (K=10)\n[cuối kỳ: Agglomerative, DBSCAN]", P)
arrow(6.8, 3.0, 7.3, 1.5); arrow(9.6, 1.5, 10.0, 1.5)

box(10.0, 0.05, 3.8, 0.7, "Silhouette · Davies-Bouldin · ARI · NMI", "#f4f4f4", fs=8.5)
box(7.3, 0.05, 2.3, 0.7, "Acc · Macro P/R/F1 · CM 10×10", "#f4f4f4", fs=8.5)
ax.set_title("Pipeline học máy – Nhóm 06 (giai đoạn giữa kỳ)", fontsize=12, weight="bold")
fig.tight_layout(); fig.savefig(FIG_DIR / "method_pipeline.png", dpi=170)
