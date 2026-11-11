"""Tiện ích dùng chung: đọc dữ liệu, làm sạch tiêu đề, trích xuất đặc trưng.

Nhóm 06 - Product Classification and Clustering (PriceRunner, UCI #837).
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.base import BaseEstimator, TransformerMixin

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "pricerunner_aggregate.csv"
FIG_DIR = ROOT / "figures"
RES_DIR = ROOT / "results"
MODEL_DIR = ROOT / "models"
RANDOM_STATE = 42

COLS = ["product_id", "title", "merchant_id", "cluster_id",
        "cluster_label", "category_id", "category_label"]

# Chuẩn hóa đơn vị đo lường: "55 inch" -> "55inch", "64 gb" -> "64gb", ...
_UNITS = r"(inch|in|gb|tb|mb|ghz|mhz|kg|g|rpm|w|kw|l|litre|liter|mp|cm|mm|hz|cores?)"
_UNIT_RE = re.compile(rf"(\d+(?:\.\d+)?)\s*(?:\"|''|-)?\s*{_UNITS}\b")
_NONWORD_RE = re.compile(r"[^a-z0-9\.\-\+ ]+")
_SPACE_RE = re.compile(r"\s+")
_ALNUM_RE = re.compile(r"\b(?=\w*\d)(?=\w*[a-z])[\w\-]+\b")
_NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def load_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Đọc CSV gốc và chuẩn hóa tên cột (file gốc có khoảng trắng đầu tên cột)."""
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    rename = dict(zip(df.columns, COLS)) if len(df.columns) == 7 else {}
    df = df.rename(columns=rename)
    df["title"] = df["title"].astype(str)
    df["category_label"] = df["category_label"].astype(str).str.strip()
    return df


def clean_title(text: str) -> str:
    """Chữ thường, chuẩn hóa đơn vị, bỏ ký tự đặc biệt; GIỮ NGUYÊN số và mã chữ-số."""
    t = str(text).lower()
    t = t.replace("”", '"').replace("″", '"')
    t = _UNIT_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}", t)
    t = _NONWORD_RE.sub(" ", t)
    t = _SPACE_RE.sub(" ", t).strip()
    return t


def morph_features(titles: pd.Series) -> pd.DataFrame:
    """06 đặc trưng hình thái học (5 từ tiêu đề; đặc trưng merchant xử lý riêng)."""
    s = titles.astype(str)
    words = s.str.split()
    return pd.DataFrame({
        "n_chars": s.str.len(),
        "n_words": words.str.len(),
        "n_numeric": s.apply(lambda x: len(_NUM_RE.findall(x))),
        "n_alnum": s.apply(lambda x: len(_ALNUM_RE.findall(x))),
        "avg_word_len": words.apply(lambda w: np.mean([len(x) for x in w]) if w else 0.0),
    }, index=titles.index)


class MorphFeatures(BaseEstimator, TransformerMixin):
    """Transformer sklearn: trả về 5 đặc trưng hình thái học đã chuẩn hóa (fit trên train)."""

    def fit(self, X, y=None):
        f = morph_features(pd.Series(X))
        self.mean_ = f.mean().values
        self.std_ = f.std().replace(0, 1).values
        return self

    def transform(self, X):
        f = morph_features(pd.Series(X)).values
        return sparse.csr_matrix((f - self.mean_) / self.std_)


class MerchantPrior(BaseEstimator, TransformerMixin):
    """Xác suất tiên nghiệm P(category | merchant) ước lượng CHỈ trên tập train
    (làm trơn Laplace) -> 10 cột. Merchant mới -> phân phối chung."""

    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha

    def fit(self, X, y):
        m = np.asarray(X).ravel()
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        ct = pd.crosstab(m, y).reindex(columns=self.classes_, fill_value=0)
        self.table_ = (ct + self.alpha).div(ct.sum(axis=1) + self.alpha * len(self.classes_), axis=0)
        glob = pd.Series(y).value_counts(normalize=True).reindex(self.classes_).values
        self.global_ = glob
        return self

    def transform(self, X):
        m = np.asarray(X).ravel()
        out = self.table_.reindex(m).to_numpy(copy=True)
        miss = np.isnan(out).any(axis=1)
        out[miss] = self.global_
        return sparse.csr_matrix(out)
