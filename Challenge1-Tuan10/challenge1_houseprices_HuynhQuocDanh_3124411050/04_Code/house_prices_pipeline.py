"""
Challenge 1 - Kaggle: House Prices - Advanced Regression Techniques
Author : Huynh Quoc Danh - 3124411050 - Saigon University
Usage  : python house_prices_pipeline.py --data ../data --out ../outputs

Pipeline (theo quy trình Data Science trong "Beginner's Guide to Data Science"
và "Next Level Data Science"):
  1. EDA: phân phối SalePrice, tương quan, missing values, outliers
  2. Preprocessing: loại outlier, log1p target, điền missing theo ngữ nghĩa,
     sửa skewness (Box-Cox), feature engineering, one-hot encoding
  3. Modeling: Ridge, Lasso, ElasticNet, Kernel Ridge, SVR, RandomForest,
     GradientBoosting, HistGradientBoosting  -> 5-fold CV RMSE (log)
  4. Ensemble: Stacking (meta = Lasso) + Weighted Blending
  5. Sinh submission.csv cho Kaggle
"""
import argparse, json, os, time, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from scipy import stats
from scipy.special import boxcox1p
from scipy.stats import boxcox_normmax

from sklearn.model_selection import KFold, cross_val_score, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.kernel_ridge import KernelRidge
from sklearn.svm import SVR
from sklearn.ensemble import (RandomForestRegressor, GradientBoostingRegressor,
                              HistGradientBoostingRegressor, StackingRegressor)
from sklearn.metrics import mean_squared_error

warnings.filterwarnings("ignore")
SEED = 42
np.random.seed(SEED)

# ---------------------------------------------------------------- style
PAL = {"blue": "#1f4e79", "orange": "#e07b39", "grey": "#8c8c8c", "green": "#2e8b57"}
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold"})


def savefig(fig, out, name):
    p = os.path.join(out, "figures", name)
    fig.tight_layout(); fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


# ---------------------------------------------------------------- 1. EDA
def eda(train, out):
    info = {}
    y = train["SalePrice"]
    info["n_train"], info["n_features_raw"] = train.shape[0], train.shape[1] - 2
    info["price_mean"], info["price_median"] = float(y.mean()), float(y.median())
    info["price_skew"], info["price_kurt"] = float(y.skew()), float(y.kurt())
    info["logprice_skew"] = float(np.log1p(y).skew())

    # Fig 1: SalePrice vs log
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))
    ax[0].hist(y, bins=50, color=PAL["blue"], alpha=.85)
    ax[0].set_title(f"SalePrice (skew = {y.skew():.2f})"); ax[0].set_xlabel("thousand USD"); ax[0].xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f"{v/1000:.0f}"))
    ax[1].hist(np.log1p(y), bins=50, color=PAL["orange"], alpha=.85)
    ax[1].set_title(f"log(1+SalePrice) (skew = {np.log1p(y).skew():.2f})")
    savefig(fig, out, "fig1_target_distribution.png")

    # Fig 2: top correlations
    num = train.select_dtypes(include=np.number).drop(columns=["Id"])
    corr = num.corr()["SalePrice"].drop("SalePrice").sort_values(ascending=False)
    info["top_corr"] = {k: round(float(v), 3) for k, v in corr.head(10).items()}
    top = corr.head(10).index.tolist() + ["SalePrice"]
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    c = num[top].corr()
    im = ax.imshow(c, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(top))); ax.set_xticklabels(top, rotation=60, ha="right")
    ax.set_yticks(range(len(top))); ax.set_yticklabels(top)
    for i in range(len(top)):
        for j in range(len(top)):
            ax.text(j, i, f"{c.iloc[i, j]:.2f}", ha="center", va="center", fontsize=6,
                    color="white" if c.iloc[i, j] > .6 else "black")
    fig.colorbar(im, fraction=.046); ax.set_title("Top-10 features correlated with SalePrice")
    savefig(fig, out, "fig2_correlation_heatmap.png")

    # Fig 3: missing values
    miss = (train.isnull().mean() * 100).sort_values(ascending=False)
    miss = miss[miss > 0]
    info["n_cols_missing"] = int(len(miss))
    info["top_missing"] = {k: round(float(v), 1) for k, v in miss.head(8).items()}
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar(miss.index, miss.values, color=PAL["blue"])
    ax.set_ylabel("% missing"); ax.set_title(f"Missing values ({len(miss)} columns)")
    plt.setp(ax.get_xticklabels(), rotation=70, ha="right", fontsize=7)
    savefig(fig, out, "fig3_missing_values.png")

    # Fig 4: outliers GrLivArea
    out_mask = (train.GrLivArea > 4000) & (train.SalePrice < 300000)
    info["n_outliers"] = int(out_mask.sum())
    fig, ax = plt.subplots(figsize=(5, 3.4))
    ax.scatter(train.GrLivArea[~out_mask], y[~out_mask], s=6, color=PAL["blue"], alpha=.5, label="normal")
    ax.scatter(train.GrLivArea[out_mask], y[out_mask], s=40, color=PAL["orange"], marker="x", label="outlier (removed)")
    ax.set_xlabel("GrLivArea (sq ft)"); ax.set_ylabel("SalePrice"); ax.legend()
    ax.set_title("Outlier detection: GrLivArea vs SalePrice")
    savefig(fig, out, "fig4_outliers.png")

    # Fig 5: OverallQual boxplot
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    groups = [y[train.OverallQual == q] for q in sorted(train.OverallQual.unique())]
    ax.boxplot(groups, tick_labels=sorted(train.OverallQual.unique()), patch_artist=True,
               boxprops=dict(facecolor="#cfe0f1", color=PAL["blue"]), medianprops=dict(color=PAL["orange"]),
               flierprops=dict(markersize=2))
    ax.set_xlabel("OverallQual"); ax.set_ylabel("SalePrice"); ax.set_title("SalePrice by OverallQual")
    savefig(fig, out, "fig5_overallqual_box.png")
    return info, out_mask


# ---------------------------------------------------------------- 2. Preprocess
def preprocess(train, test, out_mask, fe=True, skewfix=True):
    train = train[~out_mask].reset_index(drop=True)
    y = np.log1p(train["SalePrice"]).values
    test_ids = test["Id"]
    allx = pd.concat([train.drop(columns=["SalePrice"]), test]).reset_index(drop=True)
    allx = allx.drop(columns=["Id"])

    # numeric-coded categoricals
    for col in ["MSSubClass", "YrSold", "MoSold"]:
        allx[col] = allx[col].astype(str)

    # "None" means absence of the feature (theo data_description.txt)
    none_cols = ["PoolQC", "MiscFeature", "Alley", "Fence", "FireplaceQu", "GarageType",
                 "GarageFinish", "GarageQual", "GarageCond", "BsmtQual", "BsmtCond",
                 "BsmtExposure", "BsmtFinType1", "BsmtFinType2", "MasVnrType"]
    for c in none_cols:
        allx[c] = allx[c].fillna("None")
    zero_cols = ["GarageYrBlt", "GarageArea", "GarageCars", "BsmtFinSF1", "BsmtFinSF2",
                 "BsmtUnfSF", "TotalBsmtSF", "BsmtFullBath", "BsmtHalfBath", "MasVnrArea"]
    for c in zero_cols:
        allx[c] = allx[c].fillna(0)
    allx["LotFrontage"] = allx.groupby("Neighborhood")["LotFrontage"].transform(lambda s: s.fillna(s.median()))
    allx["Functional"] = allx["Functional"].fillna("Typ")
    allx = allx.drop(columns=["Utilities"])  # gần như hằng số
    for c in allx.columns:
        if pd.api.types.is_numeric_dtype(allx[c]):
            allx[c] = allx[c].fillna(allx[c].median())
        else:
            allx[c] = allx[c].fillna(allx[c].mode()[0])

    # ordinal quality maps
    qmap = {"None": 0, "Po": 1, "Fa": 2, "TA": 3, "Gd": 4, "Ex": 5}
    for c in ["ExterQual", "ExterCond", "BsmtQual", "BsmtCond", "HeatingQC", "KitchenQual",
              "FireplaceQu", "GarageQual", "GarageCond", "PoolQC"]:
        allx[c + "_ord"] = allx[c].map(qmap).fillna(0)

    # feature engineering
    if not fe:
        allx = allx.drop(columns=[c for c in allx.columns if c.endswith("_ord")])
    if fe:
        allx["TotalSF"] = allx["TotalBsmtSF"] + allx["1stFlrSF"] + allx["2ndFlrSF"]
        allx["TotalBath"] = (allx["FullBath"] + .5 * allx["HalfBath"] +
                             allx["BsmtFullBath"] + .5 * allx["BsmtHalfBath"])
        allx["TotalPorchSF"] = (allx["OpenPorchSF"] + allx["EnclosedPorch"] + allx["3SsnPorch"] +
                                allx["ScreenPorch"] + allx["WoodDeckSF"])
        allx["HouseAge"] = allx["YrSold"].astype(int) - allx["YearBuilt"]
        allx["RemodAge"] = allx["YrSold"].astype(int) - allx["YearRemodAdd"]
        allx["QualxSF"] = allx["OverallQual"] * allx["TotalSF"]
        allx["QualxGrLiv"] = allx["OverallQual"] * allx["GrLivArea"]
        for c, src in [("HasPool", "PoolArea"), ("Has2ndFlr", "2ndFlrSF"), ("HasGarage", "GarageArea"),
                       ("HasBsmt", "TotalBsmtSF"), ("HasFireplace", "Fireplaces")]:
            allx[c] = (allx[src] > 0).astype(int)

    # skew fix (Box-Cox 1p) for numeric features with |skew|>0.75
    num_cols = allx.select_dtypes(include=np.number).columns
    skew = allx[num_cols].apply(lambda s: stats.skew(s)).abs()
    nonneg = [c for c in num_cols if allx[c].min() >= 0]
    skewed = skew[(skew > .75) & skew.index.isin(nonneg)].index
    for c in (skewed if skewfix else []):  # Box-Cox(1+x), lambda=0.15 (ổn định số học, tránh giá trị cực lớn)
        allx[c] = boxcox1p(allx[c], 0.15)
    n_engineered = 7 + 5 + 10
    allx = pd.get_dummies(allx).astype(float)
    ntr = len(y)
    X, Xt = allx.iloc[:ntr].values, allx.iloc[ntr:].values
    meta = {"n_after_outlier": int(ntr), "n_test": int(len(Xt)), "n_features_final": int(allx.shape[1]),
            "n_skewed_fixed": int(len(skewed)), "n_engineered": n_engineered}
    return X, y, Xt, test_ids, allx.columns.tolist(), meta


# ---------------------------------------------------------------- 3. Models
def get_models():
    return {
        "Ridge": make_pipeline(RobustScaler(), Ridge(alpha=15.0)),
        "Lasso": make_pipeline(RobustScaler(), Lasso(alpha=0.0005, max_iter=50000, random_state=SEED)),
        "ElasticNet": make_pipeline(RobustScaler(), ElasticNet(alpha=0.0008, l1_ratio=.6, max_iter=50000, random_state=SEED)),
        "KernelRidge": make_pipeline(RobustScaler(), KernelRidge(alpha=0.6, kernel="polynomial", degree=2, coef0=2.5)),
        "SVR": make_pipeline(RobustScaler(), SVR(C=20, epsilon=0.008, gamma=0.0003)),
        "RandomForest": RandomForestRegressor(n_estimators=500, max_features=.3, min_samples_leaf=2, n_jobs=-1, random_state=SEED),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=2500, learning_rate=0.02, max_depth=4,
                                                      max_features="sqrt", min_samples_leaf=15, min_samples_split=10,
                                                      loss="huber", subsample=.8, random_state=SEED),
        "HistGB": HistGradientBoostingRegressor(max_iter=1500, learning_rate=0.03, max_leaf_nodes=15,
                                                min_samples_leaf=10, l2_regularization=1.0, random_state=SEED),
    }


def cv_oof(model, X, y, kf):
    """Trả về (RMSE từng fold, dự đoán out-of-fold) với 1 lần huấn luyện mỗi fold."""
    from sklearn.base import clone
    oof, scores = np.zeros(len(y)), []
    for tr, va in kf.split(X):
        m = clone(model).fit(X[tr], y[tr])
        oof[va] = m.predict(X[va])
        scores.append(np.sqrt(mean_squared_error(y[va], oof[va])))
    return np.array(scores), oof


def main(a):
    os.makedirs(os.path.join(a.out, "figures"), exist_ok=True)
    train = pd.read_csv(os.path.join(a.data, "train.csv"))
    test = pd.read_csv(os.path.join(a.data, "test.csv"))
    print(f"train {train.shape}  test {test.shape}")

    info, out_mask = eda(train, a.out)
    X, y, Xt, test_ids, cols, meta = preprocess(train, test, out_mask)
    info.update(meta)
    print("Features:", meta)

    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    models = get_models()
    res, oof = {}, {}
    for name, m in models.items():
        t = time.time()
        s, oof[name] = cv_oof(m, X, y, kf)
        res[name] = {"rmse_mean": float(s.mean()), "rmse_std": float(s.std()), "time_s": round(time.time() - t, 1)}
        print(f"{name:18s} RMSE {s.mean():.4f} ± {s.std():.4f}  ({res[name]['time_s']}s)")

    # Stacking
    base = [(n, models[n]) for n in ["Lasso", "ElasticNet", "KernelRidge", "SVR", "GradientBoosting", "HistGB"]]
    stack = StackingRegressor(estimators=base, final_estimator=Lasso(alpha=0.0005, max_iter=50000),
                              cv=kf, n_jobs=-1, passthrough=False)
    t = time.time(); s, oof["Stacking"] = cv_oof(stack, X, y, kf)
    res["Stacking"] = {"rmse_mean": float(s.mean()), "rmse_std": float(s.std()), "time_s": round(time.time() - t, 1)}
    print(f"Stacking           RMSE {s.mean():.4f} ± {s.std():.4f}")

    # Weighted blending (weights chosen on OOF predictions)
    W = {"Stacking": .30, "Lasso": .15, "ElasticNet": .10, "KernelRidge": .10, "SVR": .10, "GradientBoosting": .15, "HistGB": .10}
    blend_oof = sum(w * oof[k] for k, w in W.items())
    res["Blending"] = {"rmse_mean": float(np.sqrt(mean_squared_error(y, blend_oof))), "rmse_std": None, "time_s": None}
    print(f"Blending (OOF)     RMSE {res['Blending']['rmse_mean']:.4f}")

    # Fit all on full data & predict test
    preds = {}
    for name in ["Lasso", "ElasticNet", "KernelRidge", "SVR", "GradientBoosting", "HistGB"]:
        preds[name] = models[name].fit(X, y).predict(Xt)
    preds["Stacking"] = stack.fit(X, y).predict(Xt)
    final = np.expm1(sum(w * preds[k] for k, w in W.items()))
    sub = pd.DataFrame({"Id": test_ids, "SalePrice": final})
    sub.to_csv(os.path.join(a.out, "submission.csv"), index=False)
    for name in ["Lasso", "Stacking"]:
        pd.DataFrame({"Id": test_ids, "SalePrice": np.expm1(preds[name])}).to_csv(
            os.path.join(a.out, f"submission_{name.lower()}.csv"), index=False)

    # Fig 6: model comparison
    names = list(res.keys())
    vals = [res[n]["rmse_mean"] for n in names]
    errs = [res[n]["rmse_std"] or 0 for n in names]
    order = np.argsort(vals)[::-1]
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    colors = [PAL["orange"] if names[i] in ("Stacking", "Blending") else PAL["blue"] for i in order]
    ax.barh([names[i] for i in order], [vals[i] for i in order], xerr=[errs[i] for i in order],
            color=colors, capsize=2, error_kw=dict(ecolor="#555555", lw=.8))
    for k, i in enumerate(order):
        ax.text(vals[i] + errs[i] + .001, k, f"{vals[i]:.4f}", va="center", fontsize=7)
    ax.set_xlabel("5-fold CV RMSE on log(SalePrice)  (lower is better)")
    ax.set_xlim(min(vals) * .9, max(v + e for v, e in zip(vals, errs)) * 1.06); ax.set_title("Model comparison")
    savefig(fig, out=a.out, name="fig6_model_comparison.png")

    # Fig 7: Lasso feature importance
    lasso = models["Lasso"].fit(X, y)[-1]
    coef = pd.Series(lasso.coef_, index=cols)
    info["lasso_nonzero"] = int((coef != 0).sum())
    imp = pd.concat([coef.sort_values().head(10), coef.sort_values().tail(10)])
    fig, ax = plt.subplots(figsize=(6, 4.6))
    ax.barh(imp.index, imp.values, color=[PAL["orange"] if v < 0 else PAL["blue"] for v in imp.values])
    ax.set_title(f"Lasso coefficients (top ±10; {info['lasso_nonzero']}/{len(cols)} non-zero)")
    savefig(fig, a.out, "fig7_lasso_coefficients.png")

    # Fig 8: predicted vs actual (OOF blend)
    fig, ax = plt.subplots(figsize=(4.2, 4))
    ax.scatter(np.expm1(y), np.expm1(blend_oof), s=5, alpha=.4, color=PAL["blue"])
    lim = [0, np.expm1(y).max()]; ax.plot(lim, lim, "--", color=PAL["orange"])
    ax.set_xlabel("Actual SalePrice"); ax.set_ylabel("Predicted (OOF blend)")
    ax.set_title("Predicted vs Actual")
    savefig(fig, a.out, "fig8_pred_vs_actual.png")

    # Fig 9: residuals
    r = y - blend_oof
    fig, ax = plt.subplots(1, 2, figsize=(7.5, 3))
    ax[0].scatter(blend_oof, r, s=4, alpha=.4, color=PAL["blue"]); ax[0].axhline(0, color=PAL["orange"])
    ax[0].set_xlabel("Predicted log price"); ax[0].set_ylabel("Residual"); ax[0].set_title("Residuals")
    stats.probplot(r, plot=ax[1]); ax[1].set_title("Q-Q plot of residuals")
    savefig(fig, a.out, "fig9_residuals.png")

    info["results"] = res; info["blend_weights"] = W
    json.dump(info, open(os.path.join(a.out, "results.json"), "w"), indent=2)
    pd.DataFrame(res).T.to_csv(os.path.join(a.out, "cv_results.csv"))
    print("Done ->", a.out)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="../data"); p.add_argument("--out", default="../outputs")
    main(p.parse_args())
