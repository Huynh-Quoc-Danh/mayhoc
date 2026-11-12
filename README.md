# Nhóm 06 – Product Classification and Clustering

Môn Máy học – Trường Đại học Sài Gòn. Đề tài: phân loại đa lớp (10 ngành hàng) và phân cụm sản phẩm thương mại điện tử trên bộ dữ liệu PriceRunner (UCI #837).

## Cấu trúc thư mục

```
data/                 pricerunner_aggregate.csv (35.311 dòng) + LINK.txt
src/common.py         đọc dữ liệu, làm sạch tiêu đề, MorphFeatures, MerchantPrior
src/eda.py            01 – EDA: thống kê + 8 biểu đồ (figures/eda_*.png)
src/train_baselines.py 02 – 9 thí nghiệm phân loại + 4 thí nghiệm Group split
src/cluster_baseline.py 03 – baseline K-Means (K=10) trên LSA
notebooks/            01_EDA.ipynb, 02_Classification_Baselines.ipynb, 03_Clustering_Baseline.ipynb
results/              experiment_log.xlsx (nhật ký thực nghiệm), các CSV kết quả, log chạy
figures/              toàn bộ hình gốc (EDA, pipeline, kết quả)
models/               mô hình tốt nhất đã huấn luyện (.joblib)
report/               Báo cáo giữa kỳ (.docx) và Slide (.pptx)
```

## Cài đặt & chạy lại

```bash
pip install -r requirements.txt
cd src
python eda.py               # ~30 s
python train_baselines.py   # ~10-15 phút (có 5-fold CV); thêm --fast để bỏ CV
python cluster_baseline.py  # ~2 phút
```

Mọi thí nghiệm dùng `random_state=42`; chia 80/20 Stratified theo Category Label. Toàn bộ bước biến đổi (TF-IDF, SVD, chuẩn hóa, merchant prior) nằm trong `sklearn.Pipeline` nên chỉ được fit trên tập Train / từng fold → không rò rỉ dữ liệu.

**Ghi chú về XGBoost:** `train_baselines.py` dùng `xgboost.XGBClassifier` nếu thư viện có sẵn; nếu không, tự động dùng `HistGradientBoostingClassifier` (scikit-learn). Kết quả giữa kỳ trong báo cáo được chạy bằng **HistGradientBoosting** (môi trường chạy không có xgboost). Cài `xgboost` rồi chạy lại để có số liệu XGBoost thật.

## Dữ liệu

Nguồn: https://archive.ics.uci.edu/dataset/837/product+classification+and+clustering (DOI 10.24432/C5M91Z). Đặt file vào `data/pricerunner_aggregate.csv`.

## Sử dụng mô hình đã huấn luyện

```python
import joblib, pandas as pd, sys; sys.path.append("src")
from common import clean_title
m = joblib.load("models/best_E06.joblib")   # tên file theo results/best_model.json
X = pd.DataFrame({"clean": [clean_title("Samsung UE55NU7100 55\" 4K Smart TV")], "merchant_id": [1]})
print(m.predict(X))
```

## Giai đoạn cuối kỳ (12/11 – 22/11)

- Kế hoạch và phân công: `KE_HOACH_CUOI_KY.docx`
- Chạy **một** thí nghiệm, tự ghi nhật ký: `python src/run_experiment.py --member <ten> --model svc --features full --param C=0.5`
  (`python src/run_experiment.py -h` để xem các lựa chọn)
- Notebook từng thành viên: `notebooks/04_…` (Lộc), `05_…` (Danh), `06_…` (Nhân), `07_…` (Thịnh)
- Nhật ký: `experiments/<ten>/experiment_log.csv` (tự sinh) + `nhat_ky.md` (tự viết); gộp: `python scripts/gop_nhat_ky.py`
- Xuất HTML nhật ký chạy notebook: `python scripts/export_notebook_html.py notebooks/<nb>.ipynb <ten>`
- Nguồn gốc hình: `figures/FIGURE_INDEX.csv` (sinh bởi `src/figlog.save_fig`)
- GitHub: `docs/HUONG_DAN_GIT.md`; ôn vấn đáp: `docs/CAU_HOI_ON_TAP.md`
