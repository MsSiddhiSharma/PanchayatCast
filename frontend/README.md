# Frontend Web Application — PanchayatCast (SIH26074)

## 1. Purpose

The frontend is an interactive web dashboard designed for agricultural officers, KVK agronomists, and farmers to visualize and verify **Panchayat-level downscaled weather predictions**, inspect uncertainty bounds, review validation metrics against actual stations, and access localized agro-meteorological advisories.

---

## 2. Suggested Technology Stack

- **Framework:** Next.js 14 (App Router) + React 18
- **Language:** TypeScript
- **Styling:** Vanilla CSS / Tailwind CSS + Lucide React Icons
- **Geospatial Mapping:** MapLibre GL JS / Leaflet with GeoJSON vector layers
- **Data Visualization & Charts:** Recharts / Chart.js (for fan charts, quantile bounds, and time series)
- **State Management:** TanStack Query (React Query) for caching REST API responses

---

## 3. Frontend Responsibilities & Features

1. **Hierarchical Location Navigation:**
   - State selector $\rightarrow$ District selector $\rightarrow$ Block selector.
2. **Interactive Panchayat Map View:**
   - Visualizes all Gram Panchayat boundary polygons in the selected Block.
   - **Mode 1: Block-Copy View** — Demonstrates the uniform forecast value assigned by traditional block weather systems.
   - **Mode 2: ML Downscaled View** — Renders the fine-grained spatial microclimate variations across Panchayats.
   - **Mode 3: Difference-from-Block View** — Choropleth heatmap displaying $\Delta = \text{Panchayat} - \text{Block}$ (e.g. green for cooler valleys, orange/red for warmer plains).
3. **Panchayat Evidence Card:**
   - Clicking a Panchayat opens a detail card displaying:
     - Predicted values ($P_{50}$) alongside uncertainty intervals ($P_{10}$ to $P_{90}$).
     - Physiographic explanation (Elevation $\Delta z$, Slope, % Forest Cover).
     - Model provenance (Model Name, Version, Run ID).
4. **Validation Mode:**
   - Side-by-side comparison of past predictions vs ground-truth AWS/ARG station observations.
   - Real-time display of performance metrics (MAE, RMSE, CSI).
5. **Agro-Meteorological Advisory Display:**
   - Crop-specific advisory cards linked to the downscaled forecast (e.g. irrigation recommendation, pesticide spray warnings).

---

## 4. Backend API Contract

The frontend interacts with the backend strictly through the following REST API endpoints.

> [!NOTE]
> All payload examples below represent structural contracts. No fake responses are hardcoded.

### `GET /api/locations/states`
Returns list of available states.
```json
[
  { "state_id": "ST-27", "state_name": "Maharashtra" }
]
```

### `GET /api/locations/districts?state_id={state_id}`
Returns districts within the selected state.
```json
[
  { "district_id": "DIST-512", "district_name": "Pune", "state_id": "ST-27" }
]
```

### `GET /api/locations/blocks?district_id={district_id}`
Returns blocks within the selected district.
```json
[
  { "block_id": "BLK-4102", "block_name": "Haveli", "district_id": "DIST-512" }
]
```

### `GET /api/locations/panchayats?block_id={block_id}`
Returns GeoJSON FeatureCollection of Gram Panchayat polygons with physiographic properties.
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "GP-270101",
      "properties": {
        "panchayat_id": "GP-270101",
        "panchayat_name": "Khanapur",
        "elevation_mean": 645.0,
        "elevation_diff_block": 85.0
      },
      "geometry": { "type": "Polygon", "coordinates": [...] }
    }
  ]
}
```

### `GET /api/forecast?block_id={block_id}&variable={rainfall|tmax}&date={YYYY-MM-DD}&model_name={model}&lead_time={24|48}`
Returns comparative block forecast and downscaled predictions for all Panchayats in the block.
```json
{
  "block_id": "BLK-4102",
  "target_date": "2026-07-16",
  "variable": "rainfall",
  "lead_time_hours": 24,
  "block_forecast_value": 14.5,
  "panchayats": [
    {
      "panchayat_id": "GP-270101",
      "panchayat_name": "Khanapur",
      "prediction_p50": 19.2,
      "prediction_lower": 12.0,
      "prediction_upper": 28.5,
      "delta_from_block": 4.7
    }
  ]
}
```

### `GET /api/forecast/{panchayat_id}?variable={rainfall|tmax}`
Returns detailed multi-day forecast, hourly/daily trend, uncertainty bounds, and evidence features for a single Panchayat.

### `GET /api/validation?block_id={block_id}&variable={rainfall|tmax}&start_date={date}&end_date={date}`
Returns error metrics comparing Block-Copy baseline vs downscaled ML models against independent station observations.

### `GET /api/models`
Returns list of registered models, active versions, and deployment statuses (`experimental`, `validated`, `candidate`, `production`).

### `GET /api/advisory?panchayat_id={panchayat_id}&crop={crop_name}`
Returns agro-meteorological advisories generated from the downscaled forecast and crop growth stage.

---

## 5. Development Setup

```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.
