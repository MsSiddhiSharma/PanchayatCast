# Spatial Database Architecture — PanchayatCast (SIH26074)

## 1. Database Selection

We use **PostgreSQL 16** with the **PostGIS 3.4** extension.
- **Rationale:** PostGIS is the industry-standard geospatial relational database. It enables native spatial indexing (R-Tree `GIST`), spatial joins (e.g., finding which Panchayat polygon contains an AWS station or raster centroid), and spatial projections (EPSG:4326 WGS84 to EPSG:3857 Web Mercator) directly in SQL.

---

## 2. Entity-Relationship Overview

```text
[ states ]
    │ 1:N
    ▼
[ districts ]
    │ 1:N
    ▼
[ blocks ]
    │ 1:N
    ▼
[ panchayats ] ◄── (1:1) ── [ panchayat_geometries (PostGIS MULTIPOLYGON) ]
    │
    ├── (1:N) ──> [ weather_observations ] (Point ground-truth from AWS/ARG)
    ├── (1:N) ──> [ historical_weather ]   (Interpolated reanalysis & station daily series)
    └── (1:N) ──> [ panchayat_predictions ]
                         ▲
                         │ (N:1)
                  [ model_runs ] ◄── (N:1) ── [ model_registry ]
                         │
                         ├── (1:1) ──> [ prediction_uncertainty ] (P10, P50, P90, confidence)
                         └── (1:N) ──> [ advisory_runs ] ◄── (N:1) ── [ advisory_rules ]
```

---

## 3. Core Database Entities

### 3.1 Spatial & Administrative Entities
- `states`: State code, state name.
- `districts`: District LGD code, district name, foreign key to state.
- `blocks`: Block LGD code, block name, foreign key to district.
- `panchayats`: Gram Panchayat LGD code, name, parent block foreign key, static physiographic attributes (elevation mean, slope, aspect, LULC shares).
- `panchayat_geometries`: Foreign key to `panchayats`, PostGIS `GEOMETRY(MultiPolygon, 4326)` with `GIST` spatial index.

### 3.2 Meteorological & Downscaling Entities
- `data_sources`: Source provenance records (e.g. "IMD_GKMS", "ERA5_LAND", "SRTM_DEM").
- `weather_observations`: Station point records (station id, observation timestamp, observed rainfall, observed Tmax, QC flags).
- `forecasts`: Block-level numerical weather predictions issued by IMD (block id, issue timestamp, target date, lead time, forecast rainfall, forecast Tmax).
- `panchayat_predictions`: Downscaled predictions (panchayat id, target date, lead time, model run id, predicted value, delta from block).
- `prediction_uncertainty`: Uncertainty quantification bounds ($P_{10}$, $P_{50}$, $P_{90}$, coverage probability, interval width).

### 3.3 Model Governance & Experiment Tracking Entities
- `model_registry`: Approved models with statuses (`experimental`, `validated`, `candidate`, `production`).
- `experiments`: Detailed experiment tracking (run ID, hyperparameter JSON, spatial split definition, git commit hash).
- `model_runs`: Concrete execution instances of a model producing batch predictions.
- `evaluation_metrics`: Benchmark metric scores (MAE, RMSE, Bias, POD, FAR, CSI, F1) on held-out validation sets.

### 3.4 Agro-Meteorological Advisory Entities
- `advisory_rules`: Declarative rules linking weather conditions, crop type, and crop stage to recommendations.
- `advisory_runs`: Dispatched advisories referencing the triggering panchayat prediction and rule ID.

---

## 4. Key Indexes & Performance Optimization

- **Spatial Indexes:** `CREATE INDEX idx_panchayat_geom ON panchayat_geometries USING GIST (geom);`
- **Forecast Lookup Index:** Composite index on `forecasts (block_id, target_date, lead_time_hours)`.
- **Panchayat Prediction Index:** Composite index on `panchayat_predictions (panchayat_id, target_date, variable)`.
- **Temporal Station Index:** `weather_observations (station_id, observation_date)`.

---

## 5. Migration Strategy

- Schema definition is maintained in [database/schema.sql](file:///Users/siddhisharma/Desktop/PanchayatCast/database/schema.sql).
- Versioned migrations are tracked using **Alembic** under `database/migrations/`.
- To apply initial schema locally:
  ```bash
  psql -h localhost -U panchayat_user -d panchayatcast_db -f database/schema.sql
  ```
