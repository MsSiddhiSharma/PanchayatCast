# Research: Minimum Viable Product (MVP) Specification — PanchayatCast

## 1. MVP Objective

The primary objective of the MVP is to prove the end-to-end viability of **Panchayat-level weather downscaling** using an evidence-based pipeline that outperforms block forecasts on held-out station observations.

---

## 2. Pilot Geographical Unit

To ensure deep validation rather than superficial coverage:
- **Level 1:** One State (e.g., Maharashtra / Himachal Pradesh / Uttarakhand — featuring topographic microclimates).
- **Level 2:** One District.
- **Level 3:** One Block (containing 20–35 constituent Gram Panchayats).
- **Level 4:** All constituent Gram Panchayats with boundaries ingested from official LGD/Survey of India data.

---

## 3. Weather Target Variables

1. **Daily Rainfall (mm/24h):**
   - Critical for sowing, transplanting, chemical spraying, and harvesting decisions.
   - Evaluated as occurrence (yes/no) and precipitation depth.
2. **Daily Maximum Temperature ($T_{max}$ in °C):**
   - Critical for heat stress in wheat, evapotranspiration loss, and pest emergence.

---

## 4. MVP Functional Deliverables

1. **Baseline Benchmarks:** Block-Copy and Spatial Lapse-Rate models working as the standard of truth.
2. **Multiple ML Models:** Trained on identical data features under `ml/`.
3. **Automated Validation Table:** Head-to-head comparison of test metrics.
4. **FastAPI Endpoints:** Returning Panchayat forecasts, uncertainty intervals, and spatial deltas.
5. **Interactive Map Dashboard:** Choropleths, Difference-from-Block heatmaps, and Evidence Cards.
6. **Agromet Advisory Generation:** Triggering actionable farmer advisories based on downscaled weather.
