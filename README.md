# PanchayatCast (SIH26074)

> **Smart India Hackathon Problem Statement SIH26074:**  
> *Downscaling of Weather Forecast from Block Level to Panchayat Level for Agro-Meteorological Advisory Services.*

[![Status](https://img.shields.io/badge/Project%20Status-Phase%200%20(Architecture%20Setup)-blue.svg)](file:///Users/siddhisharma/Desktop/PanchayatCast/PROJECT_STATUS.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](file:///Users/siddhisharma/Desktop/PanchayatCast/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](file:///Users/siddhisharma/Desktop/PanchayatCast/backend)
[![TypeScript](https://img.shields.io/badge/TypeScript-Next.js-blue.svg)](file:///Users/siddhisharma/Desktop/PanchayatCast/frontend)
[![PostGIS](https://img.shields.io/badge/Spatial%20DB-PostgreSQL%20%2B%20PostGIS-informational.svg)](file:///Users/siddhisharma/Desktop/PanchayatCast/database)

---

## 1. Executive Summary & Problem Solved

### The Agricultural Weather Resolution Gap
In India, the **India Meteorological Department (IMD)** issues high-value weather forecasts at the **Block level** (~10–25 km spatial scale) through the Agromet Advisory Services (AAS) and Gramin Krishi Mausam Sewa (GKMS). However, farm operations occur at the **Gram Panchayat (village cluster) level** (typically 2–5 km scale). 

In complex terrain (hills, river valleys, coastal fringes, micro-watersheds), weather varies dramatically within a single block:
- A valley panchayat may experience morning frost and temperature inversions while a ridge panchayat stays mild.
- Local orographic lift and convective clouds cause localized cloudbursts or dry rain-shadows spanning only 3–5 km.
- When farmers receive a generic block-level advisory that fails locally, trust in agromet advisories erodes, resulting in preventable crop loss, misapplied chemical sprays, and suboptimal irrigation.

### What PanchayatCast Does
**PanchayatCast** bridges this spatial resolution gap using a scientifically grounded, multi-model downscaling pipeline. It takes block-level numerical weather predictions and fuses them with high-resolution physical terrain (SRTM DEM elevation, slope, aspect), Land Use/Land Cover (LULC), historical reanalysis (ERA5-Land), and station observations (AWS/ARG) to generate calibrated, **Panchayat-level daily rainfall and maximum temperature ($T_{max}$)** forecasts accompanied by **confidence/uncertainty intervals** and actionable, **source-linked agro-meteorological advisories**.

---

## 2. High-Level Architecture

The end-to-end processing pipeline flows as follows:

```
[ IMD / Coarse Block Forecast ]
              │
              ▼
    [ Data Ingestion Engine ]  <─── [ SRTM DEM / Bhuvan LULC / ERA5-Land / AWS Obs ]
              │
              ▼
   [ Data Preprocessing ] (CRS alignment, spatial joins, QC & outlier removal)
              │
              ▼
  [ Feature Engineering ] (Lapse rates, orographic index, aspect, spatial lags)
              │
              ▼
   [ Model Execution & Benchmarking ]
   ├── Baseline 1: Block-Copy (Null Hypothesis)
   ├── Baseline 2: Spatial Elevation Lapse-Rate / IDW
   ├── Model 1:    Random Forest Regressor/Classifier
   ├── Model 2:    XGBoost Residual Downscaler
   ├── Model 3:    LightGBM Tabular Downscaler
   ├── Model 4:    ConvLSTM Spatio-Temporal Challenger
   └── Model 5:    CNN / U-Net Super-Resolution Challenger
              │
              ▼
 [ Panchayat Predictions (P50, P10, P90 Quantiles) ]
              │
              ▼
  [ Independent Validation Engine ] (Holdout AWS/ARG vs Block vs ML)
              │
              ▼
    [ FastAPI Backend API ]  <─── [ PostGIS Spatial Database ]
              │
              ▼
  [ Next.js Map Dashboard ] (Choropleths, Difference Heatmaps, Evidence Cards)
              │
              ▼
[ Source-Linked Agromet Advisory ] (Crop-specific, condition-triggered rules)
```

---

## 3. Minimum Viable Product (MVP) Scope

To guarantee deliverability, scientific validity, and rapid iteration during the hackathon, the MVP is strictly scoped:
- **Geography:** One Pilot State $\rightarrow$ One District $\rightarrow$ One Block $\rightarrow$ Constituent Gram Panchayats (e.g., 20–35 Panchayats).
- **Target Weather Variables:**
  1. **Daily Rainfall (mm/day)** — Classification (rain/no-rain) & Quantitative Regression.
  2. **Daily Maximum Temperature ($T_{max}$ in °C)** — Quantitative Regression.
- **Lead Time:** Day 1 (24-hour ahead) and Day 2 (48-hour ahead).
- **Core Comparisons:**
  1. *Block-Copy baseline* (every panchayat receives the raw block value).
  2. *Spatial baseline* (elevation lapse-rate adjustment).
  3. *Candidate ML models* (Tree-based & Deep Learning).
- **Evaluation Criteria:** Verification against actual independent station observations (AWS/ARG).

---

## 4. Unique Selling Propositions (USPs)

1. **Evidence-Based Downscaling (Zero AI Hype):** We explicitly benchmark against a **Block-Copy baseline**. If an ML model does not beat the simple baseline on spatial holdouts, it is not used.
2. **Quantified Uncertainty:** Rather than a misleading single-point estimate, forecasts provide $P_{10}$, $P_{50}$, and $P_{90}$ predictive intervals.
3. **Difference-from-Block Explainability:** The frontend visualizes the delta ($\Delta = \text{Panchayat} - \text{Block}$) alongside an **Evidence Card** explaining *why* the microclimate differs (e.g., "+320m elevation above block centroid, 45% forest canopy").
4. **Actionable, Source-Linked Advisories:** Direct links from weather thresholds to crop growth stages (e.g., "Do not spray copper oxychloride if rain probability $>60\%$ in flowering phase").

---

## 5. Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, MapLibre GL / Leaflet, Lucide Icons | High-performance interactive geospatial rendering with vector choropleths |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy | Asynchronous, auto-generating OpenAPI schemas, native Python ML integration |
| **Database** | PostgreSQL 16 + PostGIS 3.4 | Industry-standard spatial database supporting `ST_Intersects`, `ST_Within`, raster operations |
| **Data & GIS** | GeoPandas, Shapely, Rasterio, Xarray, NetCDF4, GDAL | Comprehensive raster/vector spatial feature engineering |
| **ML Frameworks** | Scikit-Learn, XGBoost, LightGBM, PyTorch / PyTorch Lightning | Tabular gradient boosting + Spatio-temporal deep learning |
| **Experimentation** | File-based experiment records, JSON metrics schema, Pytest | Lightweight, zero-lockin, completely reproducible |

---

## 6. Repository Organization

```text
PanchayatCast/
├── README.md                          # Main project documentation (this file)
├── LICENSE                            # Apache 2.0 Open Source License
├── .gitignore                         # Comprehensive ignore rules for data, models, env
├── .env.example                       # Template for local environment variables
├── docker-compose.yml                 # PostGIS, Backend, Frontend local containers
├── CONTRIBUTING.md                    # Git workflow, PR rules, team practices
├── PROJECT_STATUS.md                  # Milestone progress and MVP definition
│
├── docs/                              # Project documentation & research papers
│   ├── README.md                      # Index of all docs
│   ├── team-roles.md                  # Specific duties and assigned folders per member
│   ├── architecture/                  # Architecture specifications
│   │   ├── system-architecture.md     # High-level architecture details
│   │   ├── data-flow.md               # End-to-end data pipeline
│   │   ├── ml-pipeline.md             # Training, cross-validation, inference
│   │   ├── api-architecture.md        # FastAPI REST structure
│   │   └── data-contract.md           # Standard input/output schema for ML models
│   ├── research/                      # Scientific rationale
│   │   ├── problem-statement.md       # SIH26074 background
│   │   ├── datasets.md                # Data source inventory & roles
│   │   ├── model-comparison.md        # Metric formulas and benchmarking protocol
│   │   ├── mvp.md                     # Minimum viable product specifications
│   │   └── usp.md                     # Innovation & competitive advantages
│   └── decisions/                     # Architecture Decision Records (ADRs)
│       └── README.md
│
├── frontend/                          # Next.js web application
│   └── README.md                      # UI structure, state, map components, API client
│
├── backend/                           # FastAPI application
│   ├── README.md                      # Service architecture, model loading, endpoints
│   ├── app/                           # Modular application package
│   │   ├── api/                       # REST endpoint routers
│   │   ├── services/                  # Business logic (forecast, validation, advisory)
│   │   ├── models/                    # SQLAlchemy database ORM models
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── repositories/              # Database data access layer
│   │   ├── ml/                        # Dynamic model loader & inference engine
│   │   ├── advisory/                  # Rule engine linking weather to crop guidance
│   │   └── core/                      # Config, logging, security
│   └── tests/                         # Pytest backend test suite
│
├── database/                          # Spatial database management
│   ├── README.md                      # ER diagram, PostGIS schema, indexing, migrations
│   ├── schema.sql                     # Full relational schema with PostGIS geometries
│   └── migrations/                    # Alembic / SQL versioned migration files
│
├── ml/                                # Machine Learning models (ISOLATED WORKSPACES)
│   ├── README.md                      # Universal ML guide, interfaces, evaluation protocol
│   ├── COLLABORATION.md               # Strict boundaries & rules for ML teammates
│   ├── common/                        # SHARED ML utilities (preprocessing, metrics, utils)
│   │   ├── README.md
│   │   ├── preprocessing/             # Imputation, scaling, alignment
│   │   ├── feature_engineering/       # Terrain extraction, temporal lags
│   │   ├── evaluation/                # MAE, RMSE, CSI, POD, FAR, F1, R2
│   │   ├── visualization/             # Parity plots, error maps, SHAP
│   │   ├── uncertainty/               # Conformal prediction, quantile regression
│   │   └── utils/                     # Seed setting, I/O helpers
│   ├── baselines/                     # Reference benchmarks
│   │   ├── README.md
│   │   ├── block_copy/                # Raw block identity baseline
│   │   └── spatial_baseline/          # Elevation lapse-rate / IDW baseline
│   ├── random_forest/                 # Teammate workspace: Random Forest
│   ├── xgboost/                       # Teammate workspace: XGBoost
│   ├── lightgbm/                      # Teammate workspace: LightGBM
│   ├── convlstm/                      # Teammate workspace: ConvLSTM (Challenger)
│   ├── cnn_unet/                      # Teammate workspace: CNN / U-Net (Challenger)
│   ├── model_comparison/              # Common benchmarking runner & results aggregation
│   └── model_registry/                # Catalog of validated and candidate models
│
├── data/                              # Data catalog & local directory structure (gitignored)
│   ├── README.md                      # Data governance, download guides, schemas
│   ├── raw/                           # Raw downloaded NetCDF, TIFF, CSV
│   ├── processed/                     # Cleaned, standardized arrays & tables
│   ├── features/                      # Engineered feature tables per Panchayat
│   ├── external/                      # Auxiliary geographical files
│   └── sample/                        # Small sample CSVs for testing (git-tracked)
│
├── gis/                               # Spatial vector and raster assets
│   ├── README.md                      # GIS processing guide, CRS standards, boundary sources
│   ├── boundaries/                    # Raw administrative boundary files
│   ├── panchayats/                    # Gram Panchayat GeoJSON / Shapefiles
│   ├── blocks/                        # Block boundaries
│   ├── districts/                     # District boundaries
│   ├── raster/                        # DEM GeoTIFFs, LULC rasters
│   └── processed/                     # Merged spatial feature tables
│
├── advisory/                          # Agro-Meteorological Advisory Engine
│   ├── README.md                      # Rule specifications, crop calendars
│   ├── rules/                         # Declarative weather threshold rules (JSON/YAML)
│   ├── crops/                         # Crop-specific phenological profiles
│   └── templates/                     # Multilingual farmer advisory message templates
│
├── testing/                           # Comprehensive test suites
│   ├── README.md                      # Testing strategy, pytest configurations
│   ├── unit/                          # Unit tests for functions and classes
│   ├── integration/                   # End-to-end pipeline integration tests
│   ├── ml/                            # ML model regression and interface tests
│   ├── api/                           # FastAPI test client integration
│   ├── frontend/                      # Jest / React Testing Library specs
│   └── data_validation/               # Great Expectations / schema integrity tests
│
├── scripts/                           # Automation scripts
│   ├── README.md
│   ├── data/                          # Download and fetch routines
│   ├── preprocessing/                 # Batch clipping, raster sampling
│   ├── training/                      # Model training runners
│   ├── evaluation/                    # Batch evaluation runners
│   └── deployment/                    # Container build & check scripts
│
└── notebooks/                         # Exploratory analysis notebooks
    ├── README.md                      # Notebook guidelines
    ├── data_exploration/              # Station observation & DEM distributions
    ├── feature_analysis/              # Feature correlation and mutual information
    └── visualization/                 # Map and spatial plot prototypes
```

---

## 7. Data Sources Overview

| Dataset | Provider | Spatial Resolution | Temporal Resolution | Project Role |
| :--- | :--- | :--- | :--- | :--- |
| **IMD Block Forecast** | IMD GKMS | Block-level (~10–25 km) | Daily (Day 1 to Day 5) | **Input Source** to be downscaled |
| **IMD AWS / ARG Stations** | IMD | Point observations | Hourly / Daily | **Independent Validation Ground Truth** |
| **SRTM DEM** | NASA / USGS | 30m / 90m | Static | Elevation, Slope, Aspect, Topographic Index |
| **Bhuvan LULC** | ISRO / NRSC | 250m / 50m | Annual / Static | Land cover fractions (% crop, forest, water) |
| **ERA5-Land Reanalysis** | ECMWF / Copernicus | 0.1° (~9 km) | Hourly / Daily | Historical training features & lapse context |
| **Gram Panchayat GeoJSON**| Survey of India / MoPR | Vector Polygons | Official Census 2011/LGD | **Target Downscaling Geography** |

> [!IMPORTANT]
> **Data Ground Truth Rule:** Coarse gridded datasets (e.g. IMD 0.25° or ERA5 0.1°) are **predictors and historical context**, NOT Panchayat-scale ground truth. Validation must always prioritize independent point observations (AWS/ARG).

---

## 8. ML Models & Baselines Portfolio

1. **Baselines (Required First Step):**
   - `ml/baselines/block_copy/`: Assigns the block forecast directly to every panchayat. (Proves whether downscaling provides positive skill).
   - `ml/baselines/spatial_baseline/`: Adjusts block forecast using standard environmental lapse rate (-6.5°C / 1000m for $T_{max}$, orographic elevation scaling for rain).
2. **Tabular ML Downscalers:**
   - `ml/random_forest/`: Non-linear ensemble model capturing complex terrain-weather interactions without overfitting small datasets.
   - `ml/xgboost/`: Gradient boosted decision trees learning residual corrections ($\text{Observed} - \text{Block}$).
   - `ml/lightgbm/`: Leaf-wise gradient boosting optimized for rapid hyperparameter sweeps on tabular panchayat features.
3. **Deep Learning Challengers (Evaluated Rigorously — Never Assumed Better):**
   - `ml/convlstm/`: Models joint spatial features (convolution) and temporal weather lag sequences (LSTM).
   - `ml/cnn_unet/`: Encoder-decoder architecture treating coarse weather grids as low-resolution images and outputting high-resolution fields.

---

## 9. Validation Strategy

All models are subjected to strict, identical scientific benchmarking:
1. **Spatial Holdout Cross-Validation:** We test models on panchayats *never seen during training* to evaluate spatial generalizability.
2. **Temporal Split:** Training on past seasons (e.g., 2018–2022), validating on 2023, testing on held-out 2024 monsoon/summer.
3. **Dual Metric Evaluation:**
   - **Daily Rainfall:** Mean Absolute Error (MAE), Root Mean Square Error (RMSE), Bias, Critical Success Index (CSI), Probability of Detection (POD), False Alarm Ratio (FAR), Wet-Day F1 Score.
   - **Daily $T_{max}$:** MAE, RMSE, Mean Bias Error (MBE), Coefficient of Determination ($R^2$).
   - **Uncertainty Calibration:** Prediction Interval Coverage Probability (PICP) for 80% and 95% intervals, Mean Prediction Interval Width (MPIW).

---

## 10. How Teammates Collaborate Without Conflicts

To avoid blocking each other, our workflow is partitioned by domains:

```
[ Frontend Dev ]   ───────> works in frontend/        (speaks to Backend via REST API Contract)
[ Backend Dev ]    ───────> works in backend/         (reads Models via Model Registry Interface)
[ Database Dev ]   ───────> works in database/        (maintains schema.sql & PostGIS tables)
[ ML Dev: RF ]     ───────> works in ml/random_forest/
[ ML Dev: XGB ]    ───────> works in ml/xgboost/
[ ML Dev: LGBM ]   ───────> works in ml/lightgbm/
[ ML Dev: ConvLSTM]───────> works in ml/convlstm/
[ ML Dev: CNN ]    ───────> works in ml/cnn_unet/
[ Testing / QA ]   ───────> works in testing/
```

- Read [CONTRIBUTING.md](file:///Users/siddhisharma/Desktop/PanchayatCast/CONTRIBUTING.md) for Git branch workflows.
- Read [ml/COLLABORATION.md](file:///Users/siddhisharma/Desktop/PanchayatCast/ml/COLLABORATION.md) for strict rules governing ML tracks.
- Read [docs/team-roles.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/team-roles.md) for assigned duties per team member.

---

## 11. Quickstart Guide (Local Development)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-org/PanchayatCast.git
cd PanchayatCast
cp .env.example .env
```

### 2. Launch Local Database & Services via Docker
```bash
docker compose up -d db
```
This spins up PostgreSQL 16 with PostGIS 3.4 on port 5432 and initializes `database/schema.sql`.

### 3. Setup Python Backend & ML Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 4. Run Backend Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation will be available at: [http://localhost:8000/docs](http://localhost:8000/docs).

### 5. Run Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
Frontend interface will be available at: [http://localhost:3000](http://localhost:3000).

---

## 12. Model Governance & Decision Policy

We adhere strictly to evidence-based science:
> **The winner is the model with the lowest validated error on held-out stations, not the one with the most complex neural layers.**

If an XGBoost or Random Forest model outperforms ConvLSTM in spatial holdout MAE and CSI, it will be promoted to production candidate. ConvLSTM or U-Net must earn their place through demonstrable metrics recorded in `ml/model_comparison/results/`.
