# Contributing to PanchayatCast (SIH26074)

Welcome to the team! This repository is organized specifically so that **Frontend, Backend, Database, ML Models, Testing, Documentation, and GIS/Data pipelines** can be developed independently without merge conflicts or overlapping codebases.

---

## 1. Core Collaboration Principles

1. **Strict Folder Isolation**: Each teammate works almost exclusively in their assigned directory (e.g., `frontend/`, `backend/`, `ml/xgboost/`, `database/`).
2. **Explicit Contracts**: Cross-boundary integration is governed by interfaces:
   - Frontend and Backend communicate strictly through the [REST API Contract](file:///Users/siddhisharma/Desktop/PanchayatCast/frontend/README.md#backend-api-contract).
   - Backend and ML communicate strictly through the [ML Model Interface](file:///Users/siddhisharma/Desktop/PanchayatCast/ml/README.md#common-interface).
   - Data Preprocessing and Models communicate through the [Common Data Contract](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/data-contract.md).
3. **No Fake Numbers or Overstated Claims**: We do not invent accuracy figures. A model is only marked as superior or candidate after documented evaluation on held-out test sets.
4. **Zero Uncommitted Secrets & Zero Large Files**: Never commit `.env`, API keys, database credentials, raster TIFFs, NetCDF files, or model weights (`.pt`, `.pkl`, `.onnx`).

---

## 2. Git Branching Strategy

We follow a structured Git branching workflow based on feature and ML tracks:

```text
main (production-ready releases)
  └── develop (shared integration branch)
        ├── feature/frontend-map
        ├── feature/backend-api
        ├── feature/database-schema
        ├── ml/random-forest
        ├── ml/xgboost
        ├── ml/lightgbm
        ├── ml/convlstm
        ├── ml/cnn-unet
        ├── testing/api-tests
        └── data/gis-boundaries
```

### Branch Conventions

| Branch Name | Purpose | Assigned Scope |
| :--- | :--- | :--- |
| `main` | Production code, verified demo milestones | Protected branch. Merged only via reviewed PRs from `develop`. |
| `develop` | Integration branch for tested components | Shared integration branch. |
| `feature/frontend-map` | Next.js UI, Leaflet/MapLibre map, charts | `frontend/` |
| `feature/backend-api` | FastAPI endpoints, services, schemas | `backend/` |
| `feature/database-schema` | PostGIS schemas, Alembic migrations | `database/` |
| `ml/random-forest` | Random Forest baseline & training | `ml/random_forest/` |
| `ml/xgboost` | XGBoost residual & direct downscaler | `ml/xgboost/` |
| `ml/lightgbm` | LightGBM fast tabular downscaler | `ml/lightgbm/` |
| `ml/convlstm` | ConvLSTM spatio-temporal challenger | `ml/convlstm/` |
| `ml/cnn-unet` | CNN / U-Net spatial challenger | `ml/cnn_unet/` |
| `testing/api-tests` | Automated pytest, QA verification | `testing/` |

---

## 3. The 10 Commandments of PanchayatCast

1. **Never directly push experimental code into `main` or `develop`.** Always branch off `develop` and submit a Pull Request.
2. **Each teammate works primarily in their assigned directory.** Do not edit files in another person's directory without approval.
3. **Shared preprocessing changes must be discussed beforehand.** `ml/common/` is shared across all ML tracks. Any change to `ml/common/` impacts all models.
4. **Never commit raw or processed datasets.** Place raw files in your local `data/raw/` (ignored by git).
5. **Never commit API keys or passwords.** Use `.env` with values populated from `.env.example`.
6. **Every experiment must have a unique Run ID.** Follow the format `EXP-<model>-<YYMMDD>-<seq>` (e.g., `EXP-XGB-261001-01`).
7. **Every model artifact must have a semantic version.** Format: `v1.0.0` or `v0.1-exp`.
8. **Never overwrite another teammate's trained model or experiment record.**
9. **Record evaluation metrics in standard JSON schema.** Use `ml/model_comparison/results/summary_template.json`.
10. **Review before merging.** Every Pull Request to `develop` must have at least one peer approval and passing automated tests.

---

## 4. How to Submit a Pull Request

1. Pull the latest `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   ```
2. Create your isolated feature or model branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b ml/your-model-name
   ```
3. Make your commits with descriptive messages:
   ```bash
   git commit -m "feat(ml-xgb): add spatial cross-validation pipeline"
   ```
4. Run local tests:
   ```bash
   pytest testing/unit
   ```
5. Push to remote and open a Pull Request targeting `develop`. Include:
   - What component was changed.
   - Any new dependencies added to `requirements.txt`.
   - Test results or run ID (for ML).

---

## 5. Adding Dependencies

- **Backend**: Add only required libraries into [requirements.txt](file:///Users/siddhisharma/Desktop/PanchayatCast/backend/requirements.txt).
- **Frontend**: Run `npm install <package> --save` inside `frontend/`.
- **ML Tracks**: If a specific model requires special packages (e.g. PyTorch for ConvLSTM), document it in your model's README and avoid polluting the lightweight backend requirements.
