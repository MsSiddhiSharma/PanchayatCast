# Baseline Models — PanchayatCast (SIH26074)

## 1. Why Baselines are Mandatory

In machine learning for meteorology, complex algorithms frequently fit noise or reproduce the background field without adding genuine local predictive skill.

To prove that any ML downscaling model (XGBoost, Random Forest, ConvLSTM) provides genuine agricultural value, **it must statistically outperform these two baselines on independent held-out stations**.

---

## 2. Baseline Architecture

### Baseline 1: Block-Copy Baseline (`ml/baselines/block_copy/`)
- **Concept:** Represents the Null Hypothesis ($H_0$).
- **Rule:** For every Panchayat $p$ in Block $B$:
  $$\hat{Y}_{p} = F_{B}$$
- **Importance:** This reflects the current operational state of GKMS where every village in a block receives the same forecast. If an ML model cannot beat Block-Copy in MAE or CSI on test stations, the ML model has failed.

### Baseline 2: Spatial Elevation Lapse-Rate & IDW Baseline (`ml/baselines/spatial_baseline/`)
- **Concept:** Physics-grounded spatial adjustment using standard climatological lapse rates.
- **Formulation for $T_{max}$:**
  $$\hat{T}_{\text{panchayat}} = T_{\text{block}} - \Gamma_{\text{env}} \cdot (z_{\text{panchayat}} - z_{\text{block}})$$
  Where $\Gamma_{\text{env}} = 0.0065\text{ °C/m}$ (Standard Environmental Lapse Rate, 6.5°C per 1,000m ascent).
- **Formulation for Rainfall:**
  Local orographic elevation scaling and Inverse Distance Weighting (IDW) from adjacent coarse nodes:
  $$\hat{R}_{\text{panchayat}} = R_{\text{block}} \cdot \left(1 + \alpha \cdot \frac{z_{\text{panchayat}} - z_{\text{block}}}{1000}\right)$$
  Where $\alpha$ is a fitted orographic precipitation factor ($\sim 0.05\text{ to }0.15\text{ per km}$).
