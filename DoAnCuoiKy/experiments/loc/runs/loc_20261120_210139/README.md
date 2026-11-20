# loc_20261120_210139

Chạy lại đúng lần chạy này (từ thư mục DoAnCuoiKy):

```
python src/run_experiment.py --member loc --model nb --features hybrid --char-ngram 2,4 --param alpha=0.03 --cv --name nb_best_full
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
