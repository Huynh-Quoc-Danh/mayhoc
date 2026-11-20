# nhan_20261120_224512

Chạy lại đúng lần chạy này (từ thư mục DoAnCuoiKy):

```
python src/run_experiment.py --member nhan --model xgb --features svd --svd 100 --char-ngram 3,5 --param n_estimators=400 --param max_depth=9 --param learning_rate=0.1 --cv --name xgb_best_full
```

Các file trong thư mục:

- `classification_report.csv`
- `confusion_matrix.csv`
- `metrics_cv_mean.json`
- `metrics_folds.csv`
- `metrics_test.json`
- `params_cfg.json`
- `predictions_test.csv`
- `train.log.txt`
- `README.md`
