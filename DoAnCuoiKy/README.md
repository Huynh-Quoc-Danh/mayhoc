# Nhóm 06 – Product Classification and Clustering

Môn Máy học – Trường Đại học Sài Gòn. Đề tài: phân loại đa lớp (10 ngành hàng) và phân cụm sản phẩm thương mại điện tử trên bộ dữ liệu PriceRunner (UCI #837).

## Cấu trúc thư mục

```
data/                  pricerunner_aggregate.csv (35.311 dòng) + LINK.txt
src/common.py          đọc dữ liệu, làm sạch tiêu đề (clean_title), MorphFeatures, MerchantPrior
src/run_experiment.py  chạy 1 thí nghiệm phân loại, tự ghi nhật ký + thư mục kết quả đầy đủ (cuối kỳ)
src/run_cluster.py     chạy 1 thí nghiệm phân cụm K-Means, tự ghi nhật ký + thư mục kết quả (cuối kỳ)
src/eda.py, train_baselines.py, cluster_baseline.py   script giữa kỳ (01–03)
notebooks/             01–03 (giữa kỳ), 04 Lộc, 05 Danh, 06 Nhân, 07 Thịnh (cuối kỳ)
experiments/<ten>/     experiment_log.csv, nhat_ky.md, runs/<run_id>/ của từng thành viên
app/streamlit_app.py   web demo dự đoán ngành từ tiêu đề
results/, figures/     kết quả và hình (nguồn gốc hình: figures/FIGURE_INDEX.csv)
scripts/               tiện ích: điền nhận xét, gộp nhật ký, xuất HTML notebook
models/                mô hình .joblib (KHÔNG có trên GitHub, tự tạo bằng --save-model)
report/                bản nháp báo cáo (report/nhap/) và slide (report/slide/)
```

## Cài đặt

Cần Python 3.11 hoặc 3.12. Trên macOS, XGBoost cần thêm thư viện OpenMP: `brew install libomp`.

```bash
git clone https://github.com/Huynh-Quoc-Danh/mayhoc.git
cd mayhoc/DoAnCuoiKy
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Mọi lệnh bên dưới chạy từ thư mục `DoAnCuoiKy/`.

## Chạy lại kết quả cuối kỳ

```bash
# Mô hình cuối: LinearSVC C=3, TF-IDF từ (1,2) + n-gram ký tự (2,4) – khoảng 10 giây
python src/run_experiment.py --member loc --model svc --features hybrid --char-ngram 2,4 --param C=3.0 --name kiem_tra_nop
# Kỳ vọng: Test Macro-F1 0.9929, Accuracy 0.9933

# Phân cụm: K-Means K=10 trên TF-IDF nén SVD 50 chiều – khoảng 15 giây
python src/run_cluster.py --member loc --k 10 --svd 50 --name kiem_tra_nop
# Kỳ vọng: seed 42 NMI 0.7318, ARI 0.6230; trung bình 5 seed NMI 0.7294 ± 0.0115
```

Mỗi lệnh in đường dẫn thư mục kết quả `experiments/<ten>/runs/<run_id>/` (cấu hình, điểm từng fold, classification report, ma trận nhầm lẫn, dự đoán, log) và thêm 1 dòng vào nhật ký của thành viên ghi ở `--member`. Thêm `--cv` để chạy 5-fold CV (CV kỳ vọng 0.9909 ± 0.0013); `python src/run_experiment.py -h` để xem các lựa chọn.

### Web demo

`models/` không có trên GitHub nên phải tạo mô hình trước:

```bash
python src/run_experiment.py --member loc --model svc --features hybrid --char-ngram 2,4 --param C=3.0 --name demo --save-model
ls models/                          # thấy models/<run_id>.joblib vừa tạo
cp models/<run_id>.joblib models/final_svc_hybrid24_C3.joblib
python -m streamlit run app/streamlit_app.py --server.fileWatcherType none
```

Trình duyệt mở tại http://localhost:8501; nhập một tiêu đề, ví dụ `bosch kgn39vwea fridge freezer 366l a++ white` → Fridge Freezers.

## Chạy lại kết quả giữa kỳ

```bash
cd src
python eda.py               # ~30 s
python train_baselines.py   # ~10-15 phút (có 5-fold CV); thêm --fast để bỏ CV
python cluster_baseline.py  # ~2 phút
```

Mọi thí nghiệm dùng `random_state=42`; chia 80/20 Stratified theo Category Label. Toàn bộ bước biến đổi (TF-IDF, SVD, chuẩn hóa, merchant prior) nằm trong `sklearn.Pipeline` nên chỉ được fit trên tập Train / từng fold → không rò rỉ dữ liệu.

**Ghi chú về XGBoost:** kết quả giữa kỳ từng phải dùng HistGradientBoosting vì môi trường lúc đó thiếu xgboost. Bản cuối kỳ dùng `xgboost.XGBClassifier` thật: tốt nhất Test 0.9789, CV 0.9754 (nhan_20261115_181114), chạy lại với thư mục kết quả đầy đủ ở nhan_20261120_224512.

## Dữ liệu

Nguồn: https://archive.ics.uci.edu/dataset/837/product+classification+and+clustering (DOI 10.24432/C5M91Z). Đặt file vào `data/pricerunner_aggregate.csv`.

## Sử dụng mô hình đã huấn luyện

Sau khi tạo `models/final_svc_hybrid24_C3.joblib` (mục Web demo):

```python
import joblib, pandas as pd, sys; sys.path.append("src")
from common import clean_title
m = joblib.load("models/final_svc_hybrid24_C3.joblib")
X = pd.DataFrame({"clean": [clean_title("Samsung UE55NU7100 55\" 4K Smart TV")], "merchant_id": [0]})
print(m.predict(X))   # ['TVs']
```

## Giai đoạn cuối kỳ 

- Kế hoạch và phân công: `KE_HOACH_CUOI_KY.docx`
- Chạy **một** thí nghiệm, tự ghi nhật ký: `python src/run_experiment.py --member <ten> --model svc --features full --param C=0.5`
  (`python src/run_experiment.py -h` để xem các lựa chọn)
- Notebook từng thành viên: `notebooks/04_…` (Lộc), `05_…` (Danh), `06_…` (Nhân), `07_…` (Thịnh)
- Nhật ký: `experiments/<ten>/experiment_log.csv` (tự sinh) + `nhat_ky.md` (tự viết); gộp: `python scripts/gop_nhat_ky.py`
- Xuất HTML nhật ký chạy notebook: `python scripts/export_notebook_html.py notebooks/<nb>.ipynb <ten>`
- Nguồn gốc hình: `figures/FIGURE_INDEX.csv` (sinh bởi `src/figlog.save_fig`)
- GitHub: `docs/HUONG_DAN_GIT.md`; ôn vấn đáp: `docs/CAU_HOI_ON_TAP.md`
