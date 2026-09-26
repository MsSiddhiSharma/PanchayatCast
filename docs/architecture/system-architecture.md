# System Architecture — PanchayatCast (SIH26074)

## 1. High-Level Architecture Overview

PanchayatCast implements a decoupled multi-tier architecture separating data ingestion, spatial analysis, model training/inference, API delivery, and user presentation.

```mermaid
graph TB
    subgraph Data Sources
        IMD_FC["IMD Block Forecast (Daily 1-5 Days)"]
        AWS_OBS["IMD AWS / ARG Station Observations"]
        SRTM_DEM["SRTM 30m / 90m DEM Rasters"]
        LULC["ISRO Bhuvan LULC Rasters"]
        ERA5["ERA5-Land Reanalysis (Historical Context)"]
        BOUNDARIES["Survey of India / MoPR Panchayat Polygons"]
    end

    subgraph Data & GIS Pipeline
        INGEST["Data Ingestion & QC Engine"]
        ZONAL["Raster-to-Panchayat Zonal Statistics"]
        FEAT_ENG["Feature Engineering Pipeline"]
        DATA_STORE["Processed Parquet / GeoJSON"]
    end

    subgraph Machine Learning Subsystem
        BASELINES["Baselines (Block-Copy, Spatial Lapse-Rate)"]
        TABULAR["Tabular Models (RF, XGBoost, LightGBM)"]
        DEEP["Spatio-Temporal Challengers (ConvLSTM, CNN/U-Net)"]
        EVAL_BENCH["Model Comparison & Validation Benchmark"]
        REGISTRY["Model Registry & Versioned Artifacts"]
    end

    subgraph Backend Core
        FASTAPI["FastAPI REST Application"]
        INF_SVC["Dynamic Model Inference Service"]
        ADV_SVC["Agromet Advisory Rule Engine"]
        POSTGIS[("PostgreSQL 16 + PostGIS 3.4")]
    end

    subgraph Frontend Presentation
        NEXTJS["Next.js 14 + React Dashboard"]
        MAP_CHOR["MapLibre / Leaflet Map View"]
        DIFF_VIEW["Delta-from-Block Visualizer"]
        EVIDENCE["Panchayat Evidence Card"]
        ADVISORY_UI["Farmer Agromet Guidance Cards"]
    end

    IMD_FC & AWS_OBS & SRTM_DEM & LULC & ERA5 & BOUNDARIES --> INGEST
    INGEST --> ZONAL --> FEAT_ENG --> DATA_STORE
    DATA_STORE --> BASELINES & TABULAR & DEEP
    BASELINES & TABULAR & DEEP --> EVAL_BENCH
    EVAL_BENCH --> REGISTRY
    REGISTRY --> INF_SVC
    DATA_STORE --> POSTGIS
    POSTGIS <--> FASTAPI
    INF_SVC <--> FASTAPI
    ADV_SVC <--> FASTAPI
    FASTAPI <--> NEXTJS
    NEXTJS --> MAP_CHOR & DIFF_VIEW & EVIDENCE & ADVISORY_UI
```

---

## 2. Core Architectural Components

### 2.1 Geospatial & Feature Pipeline (`gis/` and `ml/common/`)
- Ingests official administrative boundaries down to the Gram Panchayat level.
- Computes static physiographic features for every Panchayat polygon:
  - Mean elevation, standard deviation of elevation (roughness).
  - Slope gradient and aspect (solar insolation index).
  - Land cover distribution fractions (% agricultural, % forest canopy, % water bodies, % built-up).
- Aligns dynamic weather variables (block forecast, antecedent rainfall lags, temperature trends) to Panchayat centroids.

### 2.2 Machine Learning & Evaluation Subsystem (`ml/`)
- Completely decoupled model workspaces.
- Standard input/output contracts so the backend does not care whether a prediction was produced by XGBoost or ConvLSTM.
- Independent spatial validation against physical AWS/ARG ground stations.

### 2.3 Relational & Spatial Database (`database/`)
- PostgreSQL 16 with PostGIS extension.
- Stores administrative hierarchies, geometries, daily forecasts, predictions, uncertainty intervals, model registries, and advisory rules.

### 2.4 Application Backend (`backend/`)
- High-concurrency asynchronous API written in FastAPI.
- Dynamically loads approved models from the model registry.
- Computes difference-from-block and evaluates advisory rules on demand or during batch forecast ingest.

### 2.5 Modern Frontend Dashboard (`frontend/`)
- Built with Next.js and TypeScript.
- Allows intuitive exploration of forecasts at State $\rightarrow$ District $\rightarrow$ Block $\rightarrow$ Panchayat level.
- Provides interactive visual verification of why downscaling matters.
