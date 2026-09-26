# Random Forest Downscaling Model — PanchayatCast

## 1. Why Random Forest is Being Evaluated
Random Forest (RF) is an ensemble of bagging decision trees. In meteorological downscaling, RF serves as an essential machine learning benchmark because:
- It handles non-linear interactions between terrain, elevation, and atmospheric moisture without strong parametric assumptions.
- It is robust to outliers and less prone to severe overfitting on moderately sized spatial datasets than deep neural networks.
- It provides built-in Gini / permutation feature importance, revealing whether the model genuinely relies on elevation and slope rather than memorizing location IDs.

> [!NOTE]
> Random Forest is an experimental candidate model. It is **not** assumed to be the final or best model until empirically validated against baselines and gradient boosting models on held-out stations.

---

## 2. Expected Inputs & Features
Features align with the [Common Data Contract](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/data-contract.md):
- **Predictors:** `block_forecast_rainfall`, `block_forecast_tmax`, `panchayat_elevation_mean`, `elevation_diff_from_block`, `panchayat_slope_mean`, `aspect_sin`, `aspect_cos`, `lulc_forest_pct`, `lulc_agriculture_pct`, `rain_lag_1d`, `rain_lag_3d`, `rain_lag_7d`, `day_of_year`.
- **Target:** `observed_rainfall` (mm) or `observed_tmax` (°C).

---

## 3. Training & Validation Procedure
- Separate models are trained for Rainfall and $T_{max}$ at 24h and 48h lead times.
- **Cross-Validation:** GroupKFold on `panchayat_id` or spatial cluster holdout to ensure no data leakage from training stations to validation stations.
- **Uncertainty Estimation:** Derived from tree variance (inter-tree prediction spread across the forest) or Quantile Random Forests (QRF).

---

## 4. Key Hyperparameters
- `n_estimators`: 100 to 500 trees.
- `max_depth`: 8 to 20 (regularized to prevent memorizing micro-geographies).
- `min_samples_split`: 5 to 10.
- `min_samples_leaf`: 2 to 6.
- `max_features`: `"sqrt"` or `0.6` of total feature space.

---

## 5. Experiment Naming & Artifacts
- Experiments are versioned as `EXP-RF-<YYMMDD>-<SEQ>` under `experiments/`.
- Trained models are serialized to `models/rf_<variable>_<lead_time>_<version>.joblib`.
- Metrics are logged to `results/`.

---

## 6. Known Limitations
- Cannot extrapolate beyond the range of training observations (e.g. unprecedented historical cloudbursts).
- May underestimate peak rainfall extremes due to tree averaging.
- Higher memory footprint than gradient boosted trees for large tree ensembles.
