# Challenge – Kaggle: Music Genre Classification (SHAI)

> Lưu ý: tên file nén được đặt đúng theo đề (`challenge1_titanic_...`). Nội dung bài làm là cuộc thi
> **Music Genre Classification**: https://www.kaggle.com/competitions/shai-music-genre-classification

**Nhóm trưởng / Người nộp:** Huỳnh Quốc Danh – MSSV 3124411050 – Trường Đại học Sài Gòn
**Tài liệu tham khảo:** V. Chugani, *The Beginner's Guide to Data Science* và *Next-Level Data Science* (MachineLearningMastery, 2024)

## Nội dung
| Thư mục | Nội dung |
|---|---|
| 01_Paper  | Báo cáo dạng paper (.docx + .pdf) |
| 02_Slide  | Slide thuyết trình (.pptx + .pdf) |
| 03_Poster | Poster (.pptx + .pdf + .png) |
| 04_Code   | `music_genre_pipeline.py` (pipeline đầy đủ), `ablation.py`, `requirements.txt` |
| 05_MinhChung | `submission.csv` (file nộp Kaggle), `run_log.txt`, `cv_results.csv`, `ablation.csv`, `results.json`, `figures/`, ảnh chụp Kaggle |

## Kết quả (stratified 5-fold CV, out-of-fold)
| Mô hình | Macro-F1 | Weighted-F1 | Accuracy |
|---|---|---|---|
| **Stacking (meta = LogReg)** | **0.6907** | 0.6136 | 0.6141 |
| Soft Voting (HistGB+RF+ET) | 0.6878 | 0.6187 | 0.6270 |
| HistGradientBoosting | 0.6874 | 0.6068 | 0.6086 |
| Random Forest | 0.6741 | 0.6134 | 0.6270 |
| Extra Trees | 0.6689 | 0.6044 | 0.6148 |
| MLP | 0.6657 | 0.6085 | 0.6234 |
| Logistic Regression | 0.6577 | 0.5795 | 0.5857 |
| KNN | 0.6035 | 0.5569 | 0.5711 |
| Decision Tree | 0.5762 | 0.4937 | 0.5080 |

Nhãn lớp: 0 Acoustic/Folk · 1 Alt_Music · 2 Blues · 3 Bollywood · 4 Country · 5 HipHop · 6 Indie · 7 Instrumental · 8 Metal · 9 Pop · 10 Rock

## Cách chạy lại
1. Tải dữ liệu ở trang Data của cuộc thi, đổi tên thành `train.csv`, `test.csv` và đặt vào `data/`.
2. `pip install -r 04_Code/requirements.txt`
3. `cd 04_Code && python music_genre_pipeline.py --data ../data --out ../outputs` (khoảng 2–3 phút)
4. `python ablation.py ../data ../outputs`
