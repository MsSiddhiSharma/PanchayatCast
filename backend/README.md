# Backend Application — PanchayatCast (SIH26074)

## 1. Overview & Responsibilities

The backend service is an asynchronous Python application powered by **FastAPI** and **SQLAlchemy**. It is responsible for:
- Serving high-speed RESTful APIs for location hierarchies, forecasts, and geospatial boundary data.
- Connecting to the **PostgreSQL/PostGIS** database to execute spatial queries (`ST_Within`, `ST_Intersects`).
- Dynamically executing **ML model inference** across multiple model families without hardcoded dependencies.
- Calculating microclimatic spatial differences ($\Delta = \text{Panchayat} - \text{Block}$).
- Running the **Agro-Meteorological Advisory Rule Engine** linking weather thresholds to crop phenology.
- Managing model versioning, execution telemetry, structured logging, and robust error handling.

---

## 2. Technology Stack

- **Framework:** FastAPI 0.111+ (ASGI high-concurrency server)
- **Data Validation & Schemas:** Pydantic v2
- **ORM & Database Client:** SQLAlchemy 2.0+ (asyncpg / psycopg2) with GeoAlchemy2
- **Database:** PostgreSQL 16 + PostGIS 3.4
- **Serialization & ML Loading:** Joblib, ONNX Runtime, PyTorch (lazy-loaded)

---

## 3. Directory & Service Architecture

```text
backend/
├── app/
│   ├── api/                   # API route controllers (v1 router endpoints)
│   │   ├── locations.py       # State, District, Block, Panchayat endpoints
│   │   ├── forecast.py        # Block & downscaled forecast endpoints
│   │   ├── validation.py      # Station comparison and metric queries
│   │   ├── models.py          # Model registry inspection
│   │   └── advisory.py        # Agro-met advisory generation
│   │
│   ├── services/              # Business logic layer
│   │   ├── forecast_service.py # Orchestrates block-vs-panchayat computations
│   │   ├── validation_service.py # Aggregates station observations vs predictions
│   │   └── advisory_service.py # Evaluates advisory rules against predictions
│   │
│   ├── models/                # SQLAlchemy database ORM entities
│   │   ├── location.py        # State, District, Block, Panchayat tables
│   │   ├── weather.py         # Forecasts, observations, and predictions
│   │   └── advisory.py        # Rules, crops, and advisory history
│   │
│   ├── schemas/               # Pydantic request and response models
│   │   ├── forecast.py
│   │   ├── location.py
│   │   └── advisory.py
│   │
│   ├── repositories/          # Data access layer (SQLAlchemy queries)
│   │   ├── location_repo.py
│   │   └── forecast_repo.py
│   │
│   ├── ml/                    # Dynamic ML inference engine
│   │   ├── loader.py          # Loads model weights dynamically from registry
│   │   ├── adapter.py         # Standardizes input features to model tensors/arrays
│   │   └── registry_client.py # Reads ml/model_registry/registry.json
│   │
│   ├── advisory/              # Rule evaluation engine
│   │   ├── rule_evaluator.py  # Executes threshold condition checks
│   │   └── crop_calendar.py   # Crop phenology stages mapping
│   │
│   └── core/                  # Core application infrastructure
│       ├── config.py          # Environment settings (Pydantic Settings)
│       ├── database.py        # Database session engine
│       └── logging.py         # Structured logging configuration
│
├── tests/                     # Backend test suite (pytest)
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project build configuration
└── README.md                  # This file
```

---

## 4. How a Trained ML Model Becomes Available to the Backend

> [!IMPORTANT]
> **Decoupled Model Dependency Rule:** The backend **never** hardcodes or imports a specific model class (e.g. `from ml.xgboost import my_xgb`). Doing so would break the server if an ML teammate updates their private experimental code.

Instead, a trained model enters the backend through the **Model Registry Pattern**:

```
[ ML Teammate in ml/xgboost/ ]
              │
              ├── 1. Trains model and validates on held-out test set
              ├── 2. Exports serialised artifact (.joblib or .onnx) to ml/xgboost/models/
              └── 3. Registers artifact in ml/model_registry/registry.json
                           │
                           ▼
            [ ml/model_registry/registry.json ]
            {
              "model_name": "xgboost",
              "model_version": "v1.0.0",
              "variable": "rainfall",
              "lead_time": 24,
              "artifact_path": "ml/xgboost/models/xgb_rainfall_24h_v1.joblib",
              "format": "joblib",
              "status": "candidate"
            }
                           │
                           ▼
          [ Backend Dynamic Inference Engine ]
          backend/app/ml/loader.py
```

### Dynamic Invocation via Request Parameters

When a client queries the backend:
```http
GET /api/forecast?block_id=BLK-4102&model_name=xgboost&model_version=v1.0.0&variable=rainfall&lead_time=24
```

The backend dynamically:
1. Validates `model_name`, `model_version`, `variable`, and `lead_time` against the registry.
2. Checks its local in-memory cache for the loaded artifact (lazy load on first call).
3. Gathers the precomputed physiographic and antecedent weather features for all Panchayats in the block.
4. Invokes `model.predict(features)` through the uniform adapter.
5. Returns formatted predictions with $P_{10}$, $P_{50}$, $P_{90}$ intervals and difference $\Delta$.

---

## 5. Local Setup & Execution

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).
