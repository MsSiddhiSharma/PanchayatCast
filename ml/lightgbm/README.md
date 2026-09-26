# LightGBM Downscaling Model — PanchayatCast

## 1. Why LightGBM is Being Evaluated
LightGBM (Light Gradient Boosting Machine) implements leaf-wise (best-first) tree growth with Histogram-based optimization and Gradient-based One-Side Sampling (GOSS):
- **Computational Efficiency:** 5–10x faster training iterations than standard XGBoost/Random Forest, facilitating rapid feature exploration and extensive cross-validation sweeps across seasons.
- **Native Categorical Support:** Handles categorical soil, agro-climatic zone, and land cover classes directly without high-cardinality one-hot explosion.
- **Quantile Objective:** Built-in fast quantile regression (`objective='quantile'`) allowing simultaneous generation of $P_{10}$, $P_{50}$, and $P_{90}$ predictive bounds.

---

## 2. Expected Inputs & Features
- Conforms to the [Common Data Contract](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/data-contract.md).
- Efficiently processes high-dimensional tabular Panchayat feature sets.

---

## 3. Key Hyperparameters
- `num_leaves`: 31 to 63 (primary complexity control in leaf-wise growth).
- `learning_rate`: 0.02 to 0.05.
- `min_data_in_leaf`: 20 to 50 (prevents leaf overfitting on small spatial clusters).
- `feature_fraction`: 0.7 to 0.85.
- `bagging_fraction`: 0.8.
- `lambda_l1` and `lambda_l2`: Regularization penalties.

---

## 4. Experiment Naming & Artifacts
- Experiments recorded in `experiments/EXP-LGBM-<YYMMDD>-<SEQ>/`.
- Serialized models stored in `models/lgbm_<variable>_<lead_time>_<version>.joblib` or `.txt`.
- Performance scores saved in `results/`.
