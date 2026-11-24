# Mô hình đã huấn luyện

`final_svc_hybrid24_C3.joblib` – mô hình cuối của nhóm: Pipeline (clean_title → TF-IDF từ (1,2) + TF-IDF ký tự char_wb (2,4) → LinearSVC C = 3), huấn luyện trên 80% dữ liệu (Stratified, random_state 42).

- Test Macro-F1 0.9929, Accuracy 0.9933 (7.063 mẫu) – cùng cấu hình với run danh_20261113_170944 và danh_20261119_151251.
- Lưu bằng scikit-learn 1.9.1, Python 3. Phiên bản scikit-learn khác có thể báo cảnh báo hoặc không nạp được; khi đó tạo lại bằng:

```
python src/run_experiment.py --member <ten> --model svc --features hybrid --char-ngram 2,4 --param C=3.0 --name final_model --save-model
```
rồi đổi tên file `models/<run_id>.joblib` thành `models/final_svc_hybrid24_C3.joblib`.

Web demo dùng file này: `python -m streamlit run app/streamlit_app.py --server.fileWatcherType none`.
