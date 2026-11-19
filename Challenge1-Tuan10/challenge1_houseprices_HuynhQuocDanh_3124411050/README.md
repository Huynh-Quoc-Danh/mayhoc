# Challenge 1 – Kaggle House Prices: Advanced Regression Techniques

**Bài nộp:** Tuan10/TH10 – Bài tập lớn 15%
**Nhóm trưởng / Người nộp:** Huỳnh Quốc Danh – MSSV 3124411050 – Trường Đại học Sài Gòn
**Cuộc thi:** https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques
**Tài liệu tham khảo:** V. Chugani, *The Beginner's Guide to Data Science* và *Next-Level Data Science* (MachineLearningMastery, 2024)

## Nội dung
| Thư mục | Nội dung |
|---|---|
| 01_Paper  | Báo cáo dạng paper (.docx + .pdf) |
| 02_Slide  | Slide thuyết trình (.pptx + .pdf) |
| 03_Poster | Poster (.pptx + .pdf + .png) |
| 04_Code   | `house_prices_pipeline.py` (pipeline đầy đủ), `ablation.py` (thí nghiệm ablation), `requirements.txt` |
| 05_MinhChung | `submission.csv` (file nộp Kaggle), `run_log.txt` (log chạy), `cv_results.csv`, `ablation.csv`, `results.json`, `figures/`, ảnh chụp Kaggle |

## Kết quả chính (5-fold CV, RMSE trên log SalePrice)
| Mô hình | CV RMSE |
|---|---|
| **Stacking (meta = Lasso)** | **0.1072** |
| Blending (file nộp) | 0.1076 |
| Lasso | 0.1101 |
| ElasticNet | 0.1102 |
| SVR | 0.1104 |
| Gradient Boosting | 0.1118 |
| Ridge | 0.1124 |
| Kernel Ridge | 0.1165 |
| HistGB | 0.1223 |
| Random Forest | 0.1305 |

## Cách chạy lại
1. Tải dữ liệu từ trang Data của cuộc thi, giải nén `train.csv`, `test.csv` vào thư mục `data/`.
2. `pip install -r 04_Code/requirements.txt`
3. `cd 04_Code && python house_prices_pipeline.py --data ../data --out ../outputs` (khoảng 8 phút trên CPU 2 nhân)
4. `python ablation.py ../data ../outputs`

Dữ liệu Kaggle không kèm trong file nén theo quy định của cuộc thi.
