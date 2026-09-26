# Model Comparison & Benchmarking System — PanchayatCast

## 1. Overview

The `ml/model_comparison/` module serves as the **impartial scientific benchmark** for the entire project. It evaluates all candidate downscaling models and baselines against identical held-out test splits and computes standardized performance metrics.

---

## 2. Models Compared

1. **`block_copy`** (Baseline 1: Null Hypothesis)
2. **`spatial_baseline`** (Baseline 2: Elevation Lapse Rate)
3. **`random_forest`**
4. **`xgboost`**
5. **`lightgbm`**
6. **`convlstm`** (Challenger)
7. **`cnn_unet`** (Challenger)

---

## 3. Metric Definitions

- **Rainfall:**
  - Continuous Error: `MAE`, `RMSE`, `Bias`, `Correlation`
  - Categorical Contingency: `POD` (Hits / (Hits + Misses)), `FAR` (False Alarms / (Hits + False Alarms)), `CSI` (Threat Score), `F1` (Harmonic Mean)
- **Maximum Temperature ($T_{max}$):**
  - `MAE`, `RMSE`, `Bias`, `R2`
- **Uncertainty Calibration:**
  - `PICP_80`: Prediction Interval Coverage Probability (nominal 80%)
  - `MPIW`: Mean Prediction Interval Width

---

## 4. Benchmark Workflow

```bash
# Run multi-model evaluation suite against held-out validation dataset
python scripts/evaluation/benchmark_all_models.py --config ml/model_comparison/configs/comparison_config.example.yaml
```

The script outputs aggregated metric comparison tables to `ml/model_comparison/results/` and updates the Model Registry.
