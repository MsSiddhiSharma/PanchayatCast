# Data Flow Architecture — PanchayatCast (SIH26074)

This document describes the exact end-to-end data lifecycle from external provider ingestion to end-user agromet advisory generation.

---

## 1. End-to-End Pipeline Stages

```text
[1. External Ingestion]
   ├── IMD Daily Block Forecast (Day 1-5 Rainfall & Tmax)
   ├── AWS/ARG Observations (Station Ground Truth)
   └── SRTM DEM / Bhuvan LULC Rasters
           │
           ▼
[2. Quality Control & Alignment]
   ├── Coordinate Reference System alignment to EPSG:4326 / EPSG:3857
   ├── Outlier filtering (flagging impossible values e.g. Tmax > 60°C or Rain < 0mm)
   └── Missing value imputation using temporal forward-fill or spatial neighbor median
           │
           ▼
[3. Zonal Aggregation & Feature Engineering]
   ├── Extract polygon-level static features (mean elevation, slope, LULC shares)
   ├── Compute dynamic spatial features (distance to ridge, orographic windward index)
   ├── Generate antecedent temporal features (Rain lag-1, lag-3, lag-7; Tmax 3-day trend)
   └── Assemble standardized Panchayat Feature Record (Data Contract compliant)
           │
           ▼
[4. Model Execution & Quantile Estimation]
   ├── Block-Copy Baseline generates null reference: Pred_null = Block_Forecast
   ├── Spatial Baseline applies lapse rate correction: Pred_lapse = Block - 0.0065 * ΔElevation
   └── Downscaling Model predicts median (P50) and prediction intervals (P10, P90)
           │
           ▼
[5. Uncertainty Calibration & Validation Benchmarking]
   ├── Quantile loss or conformal prediction calibrates coverage width
   └── Validation engine compares against independent AWS/ARG stations (calculating MAE, RMSE, CSI)
           │
           ▼
[6. Database Ingestion & API Serving]
   ├── PostGIS stores predictions, uncertainty bounds, and spatial delta: Δ = (P50 - Block)
   └── FastAPI serves endpoints: /api/forecast, /api/forecast/{panchayat_id}, /api/validation
           │
           ▼
[7. Agro-Meteorological Advisory Engine]
   ├── Advisory engine queries crop calendar & phenological stage for selected Panchayat
   ├── Weather triggers evaluated:
   │     e.g., IF (P50_Rainfall > 25mm OR P90_Rainfall > 40mm) AND (Crop == "Paddy") AND (Stage == "Harvest")
   │           THEN Action = "Postpone harvesting immediately; drain excess water from plots."
   └── Advisory payload delivered alongside forecast data
           │
           ▼
[8. Frontend Presentation]
   └── Interactive choropleth map, difference heatmaps, evidence popovers, and farmer advisory cards
```

---

## 2. Preventing Data Leakage (Strict Rule)

A critical failure mode in meteorological ML is **future information leakage**.

1. **Forecast Issue Time Constraint**: A model making a prediction for Day $T+1$ with issue time $T_{0}$ (e.g., 08:30 IST on Day $T$) **must strictly use features observed or known prior to $T_{0}$**.
2. **No Target Leakage**: Observed weather on Day $T+1$ is exclusively reserved as the training target and validation ground truth. Under no circumstance may actual observation on Day $T+1$ be used as a predictor.
3. **Spatial Separation**: Validation stations must be strictly excluded from the training split during spatial cross-validation.
