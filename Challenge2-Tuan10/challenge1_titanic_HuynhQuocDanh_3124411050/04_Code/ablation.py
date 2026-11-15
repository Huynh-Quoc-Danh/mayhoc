"""Ablation (HistGradientBoosting, stratified 5-fold macro-F1): đóng góp của từng nhóm đặc trưng."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from music_genre_pipeline import load, get_models, run_cv, scores, SEED
from sklearn.model_selection import StratifiedKFold
from sklearn.base import clone
data, out = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("../data", "../outputs")
tr, te = load(data); y = tr["Class"].values
hgb = {"HistGB": get_models()["HistGB"]}
rows = []
# A: dữ liệu thô (cột số gốc, duration chưa sửa, điền median)
raw = ["Popularity", "danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness",
       "instrumentalness", "liveness", "valence", "tempo", "duration_raw", "time_signature"]
X = tr[raw].fillna(tr[raw].median()).values; oof = np.zeros((len(y), 11))
for a, b in StratifiedKFold(5, shuffle=True, random_state=SEED).split(X, y):
    oof[b] = clone(hgb["HistGB"]).fit(X[a], y[a]).predict_proba(X[b])
rows.append(("A. Raw audio features (median imputation)", scores(y, oof.argmax(1))))
for name, txt, art in [("B. + cleaning (duration units, missing flags, one-hot, logs)", False, False),
                       ("C. + text features (script, keywords)", True, False),
                       ("D. + artist target encoding (full)", True, True)]:
    o, *_ = run_cv(tr, y, hgb, use_text=txt, use_artist=art, verbose=False)
    rows.append((name, scores(y, o["HistGB"].argmax(1))))
df = pd.DataFrame([{"config": n, **s} for n, s in rows]); print(df.to_string(index=False))
df.to_csv(f"{out}/ablation.csv", index=False)
