# loc_20261120_210027

Chạy lại đúng lần chạy này (từ thư mục DoAnCuoiKy):

```
python src/run_experiment.py --member loc --model lr --features hybrid --char-ngram 2,4 --param C=100 --cv --name lr_best_full
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
