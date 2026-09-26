# API Architecture — PanchayatCast (SIH26074)

## 1. Backend Service Layer Pattern

The backend utilizes FastAPI structured using the Repository-Service pattern to decouple database queries and ML inference from HTTP routing.

```
Incoming Request
      │
      ▼
[ API Routers (app/api/v1/) ]
      │ Validates request with Pydantic Schemas
      ▼
[ Services (app/services/) ]
      │ Orchestrates business logic, model inference, & advisory evaluation
      ├── Calls [ Repositories (app/repositories/) ] ──> PostGIS Database
      └── Calls [ ML Engine (app/ml/) ]             ──> Model Registry / Checkpoints
      │
      ▼
Response serialized via Pydantic Schema
```

---

## 2. Dynamic Model Inference Strategy

The backend **never hardcodes an ML model class**. Instead, `app/ml/inference_engine.py` reads `ml/model_registry/registry.json`:

```python
# Conceptual Inference Dispatcher
def get_prediction(panchayat_id: str, variable: str, lead_time: int, model_name: str, model_version: str):
    # 1. Resolve model artifact path from registry
    artifact_meta = model_registry.lookup(model_name, model_version, variable)
    # 2. Load model dynamically (joblib, onnx, or torch)
    model = model_loader.load(artifact_meta["model_path"])
    # 3. Fetch engineered feature vector for panchayat
    features = feature_repo.get_features_at_issue_time(panchayat_id, issue_time)
    # 4. Predict
    prediction = model.predict(features)
    return prediction
```

---

## 3. Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status and database connectivity |
| `GET` | `/api/locations/states` | List of supported states |
| `GET` | `/api/locations/districts?state_id={id}` | List of districts within a state |
| `GET` | `/api/locations/blocks?district_id={id}` | List of blocks within a district |
| `GET` | `/api/locations/panchayats?block_id={id}`| List & GeoJSON geometries of Panchayats in a block |
| `GET` | `/api/forecast` | Block-level vs Panchayat-level forecasts for all Panchayats in a block |
| `GET` | `/api/forecast/{panchayat_id}` | Detailed forecast for a single Panchayat (P10, P50, P90, timeline) |
| `GET` | `/api/validation` | Historical validation error comparison (Block-Copy vs Models vs AWS) |
| `GET` | `/api/models` | Available models in registry with validation statuses |
| `GET` | `/api/advisory` | Crop-specific agro-met advisory for given weather and crop stage |
