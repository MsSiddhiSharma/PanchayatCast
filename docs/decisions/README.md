# Architecture Decision Records (ADRs) — PanchayatCast

This directory records significant architectural, meteorological, and algorithmic decisions made during the project lifecycle.

---

## ADR Index

| ADR # | Title | Date | Status | Summary |
| :--- | :--- | :--- | :--- | :--- |
| **ADR-001** | Use PostgreSQL 16 + PostGIS for spatial data | 2026-09-26 | Accepted | Native vector polygon operations and standard spatial indexing. |
| **ADR-002** | Decoupled ML directory structure per model | 2026-09-26 | Accepted | Enables teammates to train models independently without git conflicts. |
| **ADR-003** | Mandatory Block-Copy baseline benchmarking | 2026-09-26 | Accepted | Prevents deploying complex models that fail to beat the null hypothesis. |
| **ADR-004** | Quantile regression ($P_{10}, P_{50}, P_{90}$) for uncertainty | 2026-09-26 | Accepted | Delivers actionable risk intervals for agricultural decision-making. |
| **ADR-005** | FastAPI dynamic model registry loader | 2026-09-26 | Accepted | Backend is agnostic to specific ML frameworks (PyTorch vs Scikit-learn vs XGBoost). |

---

## ADR Template

```markdown
# ADR-XXX: [Title]

## Context
What is the problem or architectural choice being addressed?

## Decision
What is the specific technical decision made?

## Consequences
What are the positive benefits and potential trade-offs/liabilities of this choice?
```
