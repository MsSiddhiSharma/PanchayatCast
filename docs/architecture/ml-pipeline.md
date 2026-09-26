# Machine Learning Pipeline Architecture — PanchayatCast (SIH26074)

## 1. Machine Learning Strategy

The ML pipeline is architected around the scientific principle of **residual learning and spatial transferability**.

Rather than learning absolute weather values from scratch, tabular models learn the residual correction $\delta$ between the coarse block forecast $F_{\text{block}}$ and the true local condition $Y_{\text{panchayat}}$:

$$\hat{Y}_{\text{panchayat}} = F_{\text{block}} + f_{\theta}(\mathbf{X}_{\text{physiographic}}, \mathbf{X}_{\text{antecedent}}, \mathbf{X}_{\text{forecast\_context}})$$

Where:
- $\mathbf{X}_{\text{physiographic}}$ includes elevation difference $\Delta z = z_{\text{panchayat}} - z_{\text{block}}$, slope, aspect, and LULC fractions.
- $\mathbf{X}_{\text{antecedent}}$ includes recent 1-day, 3-day, and 7-day cumulative rainfall and temperature lags.
- $\mathbf{X}_{\text{forecast\_context}}$ includes coarse convective available potential energy (CAPE), humidity, or wind components from ERA5/NWP.

---

## 2. Cross-Validation Protocol

To simulate real-world deployment where a model must predict for panchayats that have no AWS station:

```
[ All Available Station-Panchayat Pairs ]
                   │
    ┌──────────────┴──────────────┐
    ▼                             ▼
[ Spatial Training Cluster ]   [ Spatial Holdout Cluster (30%) ]
  (Panchayats A, B, C...)        (Panchayats X, Y, Z - Unseen)
    │                             │
    ├── Temporal Train (2018-2022)│
    ├── Temporal Val   (2023)     │
    ▼                             ▼
[ Model Fit & Hyperparameter ] ───> [ Final Generalization Test (2024) ]
                                    (True test of downscaling skill)
```

---

## 3. Two-Stage Modeling for Rainfall

Daily rainfall exhibits zero-inflation (many dry days with 0mm, few extreme wet days). Models handle this via:
1. **Occurrence Stage (Classification):** Predicting probability of rainfall ($P(\text{Rain} \ge 0.1\text{ mm})$).
2. **Amount Stage (Regression / Quantile):** Predicting rainfall depth conditioned on rain occurring.

---

## 4. Quantified Uncertainty

Every model output produces three values:
- **$P_{10}$**: 10th percentile (conservative lower bound).
- **$P_{50}$**: Median expected value.
- **$P_{90}$**: 90th percentile (high-impact risk threshold, vital for flash flood or pest alerts).
