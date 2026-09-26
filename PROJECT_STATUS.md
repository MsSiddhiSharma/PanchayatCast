# Project Status — SIH26074 (PanchayatCast)

**Current Milestone:** Phase 0 — Collaborative Repository Architecture & Design Contracts Complete  
**Date:** September 2026  
**Status:** In Progress (Clean Architecture Foundation Established)

---

## 1. Project Phase Summary

| Phase | Description | Status | Target Date |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Repository Structure & Collaboration Contracts** | **COMPLETED** | Day 1 |
| **Phase 1** | **GIS Boundaries & Pilot Area Ingestion (1 State/District/Block)** | In Progress | Week 1 |
| **Phase 2** | **Baseline Models (Block-Copy, Spatial Lapse-Rate)** | Pending | Week 2 |
| **Phase 3** | **Tabular ML Models (Random Forest, XGBoost, LightGBM)** | Pending | Week 3 |
| **Phase 4** | **Spatial/Temporal Challenger Models (ConvLSTM, CNN/U-Net)** | Pending | Week 4 |
| **Phase 5** | **Independent Validation & Model Comparison Benchmark** | Pending | Week 5 |
| **Phase 6** | **FastAPI Backend & PostGIS Integration** | Pending | Week 6 |
| **Phase 7** | **Interactive Frontend Map, Evidence Cards & Advisory Dashboard** | Pending | Week 7 |
| **Phase 8** | **End-to-End Integration, Testing & SIH Evaluation Preparation** | Pending | Week 8 |

---

## 2. MVP Focus Scope (Strictly Scoped — No Overbuilding)

To ensure high scientific rigor and avoid premature overengineering:
- **Pilot Geography**: Exactly 1 State → 1 District → 1 Block → All constituent Gram Panchayats.
- **Variables**:
  1. **Daily Rainfall (mm)**
  2. **Daily Maximum Temperature ($T_{max}$ in °C)**
- **Lead Time**: 24-hour ahead (Day 1) and 48-hour ahead (Day 2) forecasts.
- **Model Portfolio**:
  - Baseline 1: Block-Copy (Identity)
  - Baseline 2: Spatial Lapse-Rate / IDW
  - Model 1: Random Forest
  - Model 2: XGBoost
  - Model 3: LightGBM
  - Model 4: ConvLSTM (Challenger)
  - Model 5: CNN/U-Net (Challenger)
- **Validation**: Independent ground truth evaluation against AWS/ARG station observations with spatial holdouts.
- **Deliverable**: Web interface showing Block Forecast vs Downscaled Panchayat Forecast with uncertainty bounds, difference heatmaps, error metrics, and crop-specific advisory.

---

## 3. Explicit "Do Not Build" Directives for MVP

The team is strictly instructed NOT to build:
- ❌ Microservices / Kubernetes clusters
- ❌ Cloud-heavy distributed streaming architectures (Kafka / Flink)
- ❌ Real-time radar Doppler feeds
- ❌ IoT hardware sensor nodes
- ❌ All-India raster ingestion at scale before single block validation
- ❌ Generic LLM chatbots without grounded agro-met rules
- ❌ Complex user auth / RBAC (unless explicitly needed for jury login)
