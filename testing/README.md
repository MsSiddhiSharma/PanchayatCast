# Comprehensive Testing Framework — PanchayatCast (SIH26074)

## 1. Testing Strategy Overview

To ensure high scientific validity and production robustness during SIH evaluation, testing is divided into six specialized tiers:

```text
testing/
├── README.md                      # Testing guidelines and test commands (this file)
├── unit/                          # Unit tests for isolated functions
├── data_validation/               # Data integrity, physical sanity, and anti-leakage tests
├── ml/                            # ML model regression, shape, reproducibility, and interface tests
├── api/                           # FastAPI endpoint response and schema validation tests
├── frontend/                      # UI component, map layer, and chart rendering tests
└── integration/                   # End-to-end integration tests (Frontend -> API -> DB -> ML)
```

---

## 2. Test Tiers & Responsibilities

### 2.1 Unit Testing (`testing/unit/`)
- Preprocessing routines (imputation, normalizers).
- Feature engineering math (lapse rate formulas, slope/aspect conversions, temporal lags).
- Metric formulas (verifying MAE, RMSE, CSI, POD, FAR against analytical hand-calculated examples).

### 2.2 Data Validation Testing (`testing/data_validation/`)
- **Missing Value Checks:** Asserting zero unexpected NaNs in critical predictor columns.
- **Physical Feasibility Bounds:**
  - Rainfall: $0.0 \le \text{Rain} \le 1200.0\text{ mm/day}$. Flag any negative rainfall as fatal.
  - Temperature: $-15.0 \le T_{max} \le 58.0\text{ °C}$.
- **Geospatial Integrity:** Validating polygon geometry validity (`geom.is_valid`), CRS matching `EPSG:4326`, and zero orphaned Panchayat IDs.
- **Anti-Leakage Verification:** Verifying all feature timestamps are strictly $\le$ `forecast_issue_time`.

### 2.3 Machine Learning Testing (`testing/ml/`)
- **Interface Compliance:** Verifying every model implements `train()`, `predict()`, `evaluate()`, `save_model()`, and `load_model()`.
- **Input Shape & Column Invariance:** Ensuring models reject feature vectors missing required columns.
- **Prediction Bounds:** Verifying $P_{10} \le P_{50} \le P_{90}$ for every row.
- **Reproducibility:** Ensuring fixed seeds yield identical predictions on the same test input.

### 2.4 API Testing (`testing/api/`)
- Endpoint status codes: `200 OK` on valid queries, `404 Not Found` for invalid Panchayat/Block IDs, `422 Unprocessable Entity` for bad date formats.
- OpenAPI schema conformity.
- Dynamic model selection handling (`model_name`, `model_version`).

### 2.5 Frontend Testing (`testing/frontend/`)
- State/District/Block hierarchy filter rendering.
- Vector choropleth map initialization.
- Evidence Card popover click interactions.
- Graceful API error boundary rendering.

### 2.6 Integration Testing (`testing/integration/`)
- End-to-End Test: Simulates user browsing to a Panchayat $\rightarrow$ API query $\rightarrow$ PostGIS geometry fetch $\rightarrow$ Model inference dispatch $\rightarrow$ Output payload validation.

---

## 3. Running Test Suites

```bash
# Run all Python tests (Unit, Data Validation, ML, API, Integration)
pytest testing/ -v

# Run only Data Validation tests
pytest testing/data_validation/ -v

# Run ML interface contract tests
pytest testing/ml/ -v

# Run API tests
pytest testing/api/ -v
```
