"""Ablation study (Lasso, 5-fold CV RMSE trên log SalePrice) - đánh giá đóng góp từng bước tiền xử lý."""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from house_prices_pipeline import preprocess, get_models, cv_oof, SEED
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error

data, out = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("../data", "../outputs")
train, test = pd.read_csv(f"{data}/train.csv"), pd.read_csv(f"{data}/test.csv")
kf = KFold(5, shuffle=True, random_state=SEED)
lasso = get_models()["Lasso"]
mask_out = (train.GrLivArea > 4000) & (train.SalePrice < 300000)
none = pd.Series(False, index=train.index)
rows = []

# (A) Baseline: chỉ biến số, điền median, không log target
num = train.select_dtypes("number").drop(columns=["Id", "SalePrice"]).fillna(train.median(numeric_only=True))
from sklearn.linear_model import LinearRegression
y_raw = train.SalePrice.values; X0 = num.values
oof = np.zeros(len(y_raw))
for tr, va in kf.split(X0):
    oof[va] = LinearRegression().fit(X0[tr], y_raw[tr]).predict(X0[va])
rmse = np.sqrt(mean_squared_error(np.log1p(y_raw), np.log1p(np.clip(oof, 1e4, None))))
rows.append(("A. Baseline: LinearRegression, numeric only, raw target", rmse))

configs = [("B. + log1p target, full imputation, one-hot, Lasso", none, False, False),
           ("C. + outlier removal", mask_out, False, False),
           ("D. + Box-Cox skew correction", mask_out, False, True),
           ("E. + feature engineering (full pipeline)", mask_out, True, True)]
for name, m, fe, sk in configs:
    X, y, *_ = preprocess(train, test, m, fe=fe, skewfix=sk)
    s, _ = cv_oof(lasso, X, y, kf)
    rows.append((name, s.mean()))
for r in rows: print(f"{r[1]:.4f}  {r[0]}")
pd.DataFrame(rows, columns=["config", "cv_rmse_log"]).to_csv(f"{out}/ablation.csv", index=False)
