# Common Data Contract — PanchayatCast (SIH26074)

This document establishes the canonical data interface between data preparation pipelines and all machine learning models. Every ML model (Random Forest, XGBoost, LightGBM, ConvLSTM, CNN/U-Net) must accept features aligned with this contract.

---

## 1. Feature Vector Schema (Tabular Input Format)

Every sample row in the training/inference dataset represents a single **Panchayat at a specific Forecast Issue Time and Lead Time**.

| Column Name | Data Type | Units / Range | Description |
| :--- | :--- | :--- | :--- |
| `panchayat_id` | `VARCHAR(32)` | LGD Code / UUID | Unique stable Gram Panchayat identifier |
| `block_id` | `VARCHAR(32)` | LGD Code / UUID | Parent Block identifier |
| `target_date` | `DATE` | `YYYY-MM-DD` | Date for which the prediction is being made |
| `forecast_issue_time`| `TIMESTAMP` | ISO 8601 UTC | Exact time when the forecast was issued (e.g. `2026-07-15T03:00:00Z`) |
| `lead_time_hours` | `INT` | `24`, `48` | Forecast lead time in hours (24h = Day 1, 48h = Day 2) |
| `block_forecast_rainfall` | `FLOAT` | mm/day ($\ge 0$) | Numerical weather prediction rainfall for the parent block |
| `block_forecast_tmax` | `FLOAT` | °C (-10 to 55) | Numerical weather prediction max temperature for the block |
| `panchayat_centroid_lat` | `FLOAT` | Decimal degrees | Latitude of Panchayat polygon centroid |
| `panchayat_centroid_lon` | `FLOAT` | Decimal degrees | Longitude of Panchayat polygon centroid |
| `panchayat_elevation_mean`| `FLOAT` | Meters a.s.l. | Mean SRTM DEM elevation inside Panchayat polygon |
| `elevation_diff_from_block`| `FLOAT`| Meters | $\Delta z = \text{Elevation}_{\text{panchayat}} - \text{Elevation}_{\text{block}}$ |
| `panchayat_slope_mean` | `FLOAT` | Degrees (0 to 90) | Mean topographic slope |
| `panchayat_aspect_sin` | `FLOAT` | -1.0 to 1.0 | Sine of topographic aspect (North-South exposure) |
| `panchayat_aspect_cos` | `FLOAT` | -1.0 to 1.0 | Cosine of topographic aspect (East-West exposure) |
| `lulc_agriculture_pct` | `FLOAT` | 0.0 to 1.0 | Fraction of Panchayat covered by crop/cropland |
| `lulc_forest_pct` | `FLOAT` | 0.0 to 1.0 | Fraction of Panchayat covered by forest canopy |
| `lulc_water_pct` | `FLOAT` | 0.0 to 1.0 | Fraction of Panchayat covered by surface water |
| `rain_lag_1d` | `FLOAT` | mm ($\ge 0$) | Cumulative observed/reanalysis rainfall in preceding 24h prior to issue time |
| `rain_lag_3d` | `FLOAT` | mm ($\ge 0$) | Cumulative rainfall in preceding 72h prior to issue time |
| `rain_lag_7d` | `FLOAT` | mm ($\ge 0$) | Cumulative rainfall in preceding 7 days prior to issue time |
| `tmax_lag_1d` | `FLOAT` | °C | Observed $T_{max}$ on preceding day |
| `tmax_lag_3d_mean` | `FLOAT` | °C | Mean $T_{max}$ over preceding 3 days |
| `day_of_year` | `INT` | 1 to 366 | Temporal seasonality feature |
| `monsoon_season_flag` | `INT` | 0 or 1 | 1 if date falls in June-September monsoon period |
| `era5_cape` | `FLOAT` | J/kg | Convective Available Potential Energy (coarse stability index) |
| `era5_total_column_water`| `FLOAT`| $kg/m^2$ | Atmospheric moisture column content |

---

## 2. Target Variables Schema

| Target Name | Type | Units | Description |
| :--- | :--- | :--- | :--- |
| `observed_rainfall` | `FLOAT` | mm | Ground-truth daily rainfall from station or high-density gage network |
| `observed_tmax` | `FLOAT` | °C | Ground-truth daily maximum 2-meter air temperature |
| `rain_occurrence_flag`| `INT` | 0 or 1 | Binary indicator: 1 if `observed_rainfall` $\ge 0.1\text{ mm}$, else 0 |

---

## 3. Standard Model Prediction Output Schema

Every model prediction must conform to this JSON schema:

```json
{
  "panchayat_id": "2701001",
  "variable": "rainfall",
  "target_date": "2026-07-16",
  "lead_time_hours": 24,
  "prediction_p50": 18.4,
  "prediction_lower": 12.1,
  "prediction_upper": 27.8,
  "block_reference_value": 14.0,
  "delta_from_block": 4.4,
  "model_name": "xgboost",
  "model_version": "v1.0.0",
  "run_id": "EXP-XGB-260926-01"
}
```

---

## 4. Anti-Leakage Invariance Rule

> [!CAUTION]
> Under no circumstance may any predictor variable contain data stamped after `forecast_issue_time`.
> For example:
> - If `target_date` is `2026-07-16` and `forecast_issue_time` is `2026-07-15 03:00 UTC`, features like `rain_lag_1d` must strictly cover `2026-07-14 03:00` to `2026-07-15 03:00`.
> - Violating this rule invalidates the experiment and produces artificially high accuracy that collapses in operational deployment.
