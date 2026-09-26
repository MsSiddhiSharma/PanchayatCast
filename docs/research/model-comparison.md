# Research: Model Comparison Protocol — PanchayatCast (SIH26074)

## 1. Benchmarking Philosophy

Every downscaling model must be evaluated against the same datasets, feature sets, validation splits, and metrics.
No model is considered effective unless it demonstrates statistically significant improvement over both:
1. **Block-Copy Baseline** (Null Hypothesis: zero spatial variation inside block)
2. **Spatial Baseline** (Physics-based elevation lapse-rate adjustment)

---

## 2. Standard Evaluation Metrics

### 2.1 Daily Rainfall Metrics

Rainfall evaluation combines continuous regression error with categorical detection accuracy for rain events (threshold $\tau \ge 0.1\text{ mm}$ or heavy rain $\tau \ge 15.6\text{ mm}$):

| Metric | Formula | Goal | Description |
| :--- | :--- | :--- | :--- |
| **MAE** | $\frac{1}{N}\sum \|y_i - \hat{y}_i\|$ | Minimize | Mean Absolute Error on rainfall depth |
| **RMSE** | $\sqrt{\frac{1}{N}\sum (y_i - \hat{y}_i)^2}$ | Minimize | Root Mean Square Error (penalizes extreme misses) |
| **Mean Bias** | $\frac{1}{N}\sum (\hat{y}_i - y_i)$ | Near 0 | Systemic overprediction ($>0$) or underprediction ($<0$) |
| **Pearson Correlation ($r$)** | $\frac{\text{Cov}(y, \hat{y})}{\sigma_y \sigma_{\hat{y}}}$ | Maximize (1.0) | Linear association with ground truth |
| **Probability of Detection (POD)** | $\frac{\text{Hits}}{\text{Hits} + \text{Misses}}$ | Maximize (1.0) | Fraction of actual wet days correctly forecasted |
| **False Alarm Ratio (FAR)** | $\frac{\text{False Alarms}}{\text{Hits} + \text{False Alarms}}$ | Minimize (0.0) | Fraction of forecasted wet days that were actually dry |
| **Critical Success Index (CSI)** | $\frac{\text{Hits}}{\text{Hits} + \text{Misses} + \text{False Alarms}}$ | Maximize (1.0) | Threat score balancing hits vs misses & false alarms |
| **Wet-Day F1 Score** | $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$ | Maximize (1.0) | Harmonic mean of precision and recall for rain events |

### 2.2 Daily Maximum Temperature ($T_{max}$) Metrics

| Metric | Formula | Goal |
| :--- | :--- | :--- |
| **MAE** | $\frac{1}{N}\sum \|y_i - \hat{y}_i\|$ | Minimize |
| **RMSE** | $\sqrt{\frac{1}{N}\sum (y_i - \hat{y}_i)^2}$ | Minimize |
| **Mean Bias Error (MBE)** | $\frac{1}{N}\sum (\hat{y}_i - y_i)$ | Near 0.0 °C |
| **Coefficient of Determination ($R^2$)** | $1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$ | Maximize (1.0) |

### 2.3 Uncertainty Metrics

| Metric | Definition | Target |
| :--- | :--- | :--- |
| **Prediction Interval Coverage Probability (PICP)** | % of true observations falling between $P_{10}$ and $P_{90}$ | $\approx 80\%$ nominal coverage |
| **Mean Prediction Interval Width (MPIW)** | Mean difference between upper ($P_{90}$) and lower ($P_{10}$) bounds | Narrower is sharper / more informative |

---

## 3. Comparison Results Template

Results are recorded in standardized JSON format. All metrics remain `null` until experimental validation on held-out test data:

```json
{
  "model": "xgboost",
  "version": "v1.0.0",
  "variable": "rainfall",
  "test_period": "2024-06-01 to 2024-09-30",
  "spatial_split": "heldout_panchayats_30pct",
  "MAE": null,
  "RMSE": null,
  "Bias": null,
  "Correlation": null,
  "POD": null,
  "FAR": null,
  "CSI": null,
  "F1": null,
  "PICP_80": null,
  "MPIW": null,
  "status": "experimental"
}
```
