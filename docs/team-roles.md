# Team Roles & Responsibilities — PanchayatCast (SIH26074)

To prevent merge conflicts and ensure independent velocity, every team member has clearly defined ownership boundaries.

---

## Team Responsibility Matrix

| Role | Primary Directory | Git Branch | Core Responsibilities |
| :--- | :--- | :--- | :--- |
| **Frontend Developer** | `frontend/` | `feature/frontend-map` | Next.js UI, MapLibre/Leaflet maps, choropleth rendering, difference views, Evidence Cards, Charts. |
| **Backend Developer** | `backend/` | `feature/backend-api` | FastAPI application, REST endpoints, model inference adapter, database repository wiring, CORS, error handling. |
| **Database & GIS Developer** | `database/` & `gis/` | `feature/database-schema` | PostGIS database schema, spatial indexes, boundary GeoJSON ingestion, DEM raster zonal statistics extraction. |
| **ML Developer — Random Forest** | `ml/random_forest/` | `ml/random-forest` | RF regression & classification pipelines, feature importance, spatial CV, hyperparameter tuning. |
| **ML Developer — XGBoost** | `ml/xgboost/` | `ml/xgboost` | Gradient boosting residual downscaling, rain/Tmax models, quantile loss for prediction intervals. |
| **ML Developer — LightGBM** | `ml/lightgbm/` | `ml/lightgbm` | High-speed gradient boosting, categorical land cover handling, rapid feature engineering validation. |
| **ML Developer — ConvLSTM** | `ml/convlstm/` | `ml/convlstm` | Spatio-temporal grid tensor prep, ConvLSTM sequence modeling, PyTorch training pipelines. |
| **ML Developer — CNN / U-Net** | `ml/cnn_unet/` | `ml/cnn-unet` | Spatial super-resolution grids, U-Net architecture, grid-to-panchayat zonal extraction. |
| **QA / Testing Specialist** | `testing/` | `testing/api-tests` | Pytest fixtures, data validation (missing/outlier checks), model inference contract tests, integration test suite. |

---

## Detailed Role Breakdowns

### 1. Frontend Developer
- **Domain:** [frontend/](file:///Users/siddhisharma/Desktop/PanchayatCast/frontend/)
- **Core Deliverables:**
  - Administrative selector hierarchy: State $\rightarrow$ District $\rightarrow$ Block.
  - Interactive Panchayat map showing:
    1. *Block-Copy Forecast view* (uniform value across block).
    2. *Downscaled ML Forecast view* (micro-climatic variance).
    3. *Difference-from-Block view* ($\Delta = \text{Panchayat} - \text{Block}$).
  - Panchayat **Evidence Card**: Popover showing elevation, slope, LULC %, and rationale behind prediction.
  - Uncertainty range visualization ($P_{10}$ to $P_{90}$ bar/fan chart).
  - Validation tab comparing observed AWS/ARG vs Model vs Block.
  - Agromet advisory presentation tailored to selected Panchayat.
- **Contract:** Communicates with backend strictly through [API Contract](file:///Users/siddhisharma/Desktop/PanchayatCast/frontend/README.md#backend-api-contract).

### 2. Backend Developer
- **Domain:** [backend/](file:///Users/siddhisharma/Desktop/PanchayatCast/backend/)
- **Core Deliverables:**
  - FastAPI application structure (`app/api`, `app/services`, `app/schemas`).
  - Asynchronous data access via SQLAlchemy connecting to PostGIS.
  - ML Inference Service: Generic model loader capable of loading candidate models dynamically without hardcoding model classes.
  - Advisory rule trigger engine (`app/advisory/`).
  - OpenAPI documentation (`/docs`) and comprehensive error logging.
- **Contract:** Reads models via [Model Registry](file:///Users/siddhisharma/Desktop/PanchayatCast/ml/model_registry/README.md) and serves Frontend endpoints.

### 3. Database & GIS Developer
- **Domain:** [database/](file:///Users/siddhisharma/Desktop/PanchayatCast/database/) & [gis/](file:///Users/siddhisharma/Desktop/PanchayatCast/gis/)
- **Core Deliverables:**
  - PostGIS schema creation with spatial indices (`GIST`) on panchayat geometries.
  - Ingestion scripts for administrative boundaries (State, District, Block, Panchayat).
  - Processing raster DEMs (SRTM) and LULC to compute mean elevation, slope, and land cover fractions per Panchayat.
  - Preserving **stable, immutable Panchayat IDs** across all tables.

### 4. ML Developers (RF, XGBoost, LightGBM, ConvLSTM, CNN/U-Net)
- **Domain:** Isolated under `ml/<assigned_model>/`
- **Core Deliverables:**
  - Implement standard interface methods: `train()`, `predict()`, `evaluate()`, `save_model()`, `load_model()`.
  - Perform spatial cross-validation (holding out panchayats).
  - Produce uncertainty intervals ($P_{10}$, $P_{50}$, $P_{90}$).
  - Save all run configs, metrics, and models in `experiments/` and `results/`.
- **Contract:** Adhere to [Common Data Contract](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/data-contract.md) and [ml/COLLABORATION.md](file:///Users/siddhisharma/Desktop/PanchayatCast/ml/COLLABORATION.md).

### 5. Testing & QA Specialist
- **Domain:** [testing/](file:///Users/siddhisharma/Desktop/PanchayatCast/testing/)
- **Core Deliverables:**
  - Data validation tests (detecting spatial coordinate errors, negative rainfall, physical impossibility).
  - Data leakage prevention tests (verifying features only use info available prior to forecast issue time).
  - Unit tests for common preprocessing routines.
  - End-to-end integration test: Frontend $\rightarrow$ Backend $\rightarrow$ Database $\rightarrow$ ML Inference.
