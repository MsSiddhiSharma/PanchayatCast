# XGBoost Downscaling Model — PanchayatCast

## 1. Why XGBoost is Being Evaluated
XGBoost (eXtreme Gradient Boosting) is an industry-standard gradient boosting library offering second-order gradient optimization and strong regularization:
- **Residual Learning:** Specifically configured to predict the spatial residual ($\delta = Y_{\text{panchayat}} - F_{\text{block}}$) rather than raw absolute values, centering the baseline on the physical NWP forecast.
- **Two-Stage Modeling for Rainfall:**
  - *Classifier:* Predicts wet/dry probability ($P(\text{Rain} \ge 0.1\text{ mm})$) using `binary:logistic`.
  - *Regressor:* Predicts rainfall intensity on wet days using `reg:squarederror` or Tweedie deviance (`reg:tweedie`).
- **Temperature Regression:** High-precision regression on $T_{max}$ residuals using elevation differentials and aspect.
- **Quantile Regression:** Direct support for `reg:quantileerror` at $\alpha \in \{0.10, 0.50, 0.90\}$ to output well-calibrated prediction intervals.

---

## 2. Expected Inputs & Tabular Features
- Conforms strictly to [Common Data Contract](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/data-contract.md).
- Inputs include block forecast, spatial physiographic derivatives ($\Delta z$, slope, aspect), antecedent precipitation indices, and reanalysis stability variables (CAPE, PWAT).

---

## 3. Key Hyperparameters
- `learning_rate` ($\eta$): 0.02 to 0.08.
- `max_depth`: 4 to 8.
- `subsample`: 0.7 to 0.9.
- `colsample_bytree`: 0.7 to 0.9.
- `reg_alpha` ($L_1$) and `reg_lambda` ($L_2$): Tuned to prevent memorizing small clusters.
- `objective`: `reg:squarederror`, `reg:quantileerror`, or `binary:logistic`.

---

## 4. Experiment Naming & Artifacts
- Experiments logged under `experiments/EXP-XGB-<YYMMDD>-<SEQ>/`.
- Models saved as `models/xgb_<variable>_<lead_time>_<version>.joblib` or `.json`.
- Performance metrics logged to `results/`.
