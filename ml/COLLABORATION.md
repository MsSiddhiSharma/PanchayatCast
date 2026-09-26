# ML Team Collaboration & Experiment Rules — PanchayatCast

This guide defines the collaborative working protocol for machine learning teammates on the SIH26074 project.

---

## 1. Directory Isolation Rules

To prevent code churn, merge conflicts, and dependency collisions:

| Teammate Track | Assigned Directory | Isolated Git Branch |
| :--- | :--- | :--- |
| **Random Forest Track** | `ml/random_forest/` | `ml/random-forest` |
| **XGBoost Track** | `ml/xgboost/` | `ml/xgboost` |
| **LightGBM Track** | `ml/lightgbm/` | `ml/lightgbm` |
| **ConvLSTM Track** | `ml/convlstm/` | `ml/convlstm` |
| **CNN / U-Net Track** | `ml/cnn_unet/` | `ml/cnn-unet` |
| **Benchmarking & Registry** | `ml/model_comparison/`, `ml/model_registry/` | `ml/model-comparison` |

> [!WARNING]
> **Strict Isolation Rule:** Do NOT edit files inside another teammate's model folder. If you find a bug or have an optimization idea for another model, ping the teammate directly or open a GitHub Issue.

---

## 2. Shared Utilities in `ml/common/`

Shared code lives under `ml/common/`:
- `ml/common/preprocessing/`: Missing data imputation, scaling, data loaders.
- `ml/common/feature_engineering/`: Topographic index calculation, temporal weather lags.
- `ml/common/evaluation/`: Canonical implementations of MAE, RMSE, Bias, POD, FAR, CSI, F1.
- `ml/common/uncertainty/`: Quantile loss helpers and conformal prediction bounds.

> [!IMPORTANT]
> **Protocol for Modifying `ml/common/`:**
> Any change to `ml/common/` affects every ML model. You MUST:
> 1. Propose the change to the ML team first.
> 2. Ensure existing function signatures do NOT break backward compatibility.
> 3. Verify that unit tests in `testing/ml/` and `testing/unit/` pass before merging.

---

## 3. Mandatory Structure for Each Model Directory

Every model directory MUST contain the following 7 subdirectories:

```text
ml/<model_name>/
├── README.md               # Model-specific methodology, hypotheses & limitations
├── src/                    # Python training, prediction, and wrapper scripts
├── configs/                # Configuration files (config.example.yaml, config.yaml)
├── notebooks/              # Exploratory and prototyping Jupyter notebooks
├── experiments/            # Versioned experiment logs (EXP-XXX)
├── models/                 # Serialized weights (.joblib, .pt, .onnx) (gitignored)
└── results/                # Output evaluation metrics & prediction tables
```

---

## 4. Experiment Tracking Standard

Never record only a final scalar score in a notebook cell. Every formal training run must be logged in a dedicated experiment folder:

```text
ml/<model_name>/experiments/EXP-<MODEL>-<YYMMDD>-<SEQ>/
├── config.yaml             # Exact hyperparameters, features, and split parameters
├── metrics.json            # Full test evaluation metric scores
└── notes.md                # Qualitative observations, failure modes, conclusions
```

### Required Fields in `config.yaml`
```yaml
experiment_id: "EXP-XGB-260926-01"
model_family: "xgboost"
model_version: "v1.0.0"
target_variable: "rainfall"
lead_time_hours: 24

dataset:
  version: "v1-pilot-maharashtra"
  training_period: ["2018-01-01", "2022-12-31"]
  validation_period: ["2023-01-01", "2023-12-31"]
  test_period: ["2024-06-01", "2024-09-30"]
  spatial_split_strategy: "spatial_holdout_30pct_panchayats"

features:
  - block_forecast_rainfall
  - elevation_diff_from_block
  - panchayat_slope_mean
  - lulc_forest_pct
  - rain_lag_1d
  - rain_lag_3d

hyperparameters:
  n_estimators: 300
  learning_rate: 0.05
  max_depth: 6
  subsample: 0.8
  random_seed: 42
```

### Required Fields in `metrics.json`
```json
{
  "experiment_id": "EXP-XGB-260926-01",
  "evaluated_at": "2026-09-26T12:00:00Z",
  "MAE": null,
  "RMSE": null,
  "Bias": null,
  "Correlation": null,
  "CSI": null,
  "F1": null,
  "status": "experimental"
}
```
*(Values remain null until test evaluation on held-out data).*
