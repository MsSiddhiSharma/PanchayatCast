# Documentation Index — PanchayatCast (SIH26074)

This directory contains research foundations, architectural designs, team role definitions, and architecture decision records (ADRs) for the project.

---

## 1. Directory Overview

- [team-roles.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/team-roles.md) — Exact responsibility mapping and isolated folder assignments for each teammate.
- **[architecture/](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/)** — System architecture, data flow diagrams, ML pipeline flow, API designs, and data contracts.
  - [system-architecture.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/system-architecture.md) — High-level multi-tier component architecture.
  - [data-flow.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/data-flow.md) — Step-by-step path of weather data from coarse forecasts to downscaled panchayat advisories.
  - [ml-pipeline.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/ml-pipeline.md) — Training, spatial cross-validation, and inference lifecycle.
  - [api-architecture.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/api-architecture.md) — RESTful endpoints, service architecture, and error handling.
  - [data-contract.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/data-contract.md) — Standardized input/output feature schema for all ML models.
- **[research/](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/research/)** — Scientific foundation and literature backing.
  - [problem-statement.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/research/problem-statement.md) — Deep dive into the SIH26074 problem statement and resolution gap.
  - [datasets.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/research/datasets.md) — Breakdown of IMD, AWS, DEM, LULC, and ERA5 datasets.
  - [model-comparison.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/research/model-comparison.md) — Evaluation metric formulas and benchmark protocol.
  - [mvp.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/research/mvp.md) — Scope boundary and pilot implementation plan.
  - [usp.md](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/research/usp.md) — Unique selling propositions and competitive differentiation.
- **[decisions/](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/decisions/)** — Architecture Decision Records (ADRs) tracking key architectural choices.
