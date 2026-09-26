# Agro-Meteorological Advisory Engine — PanchayatCast (SIH26074)

## 1. Purpose

The advisory engine translates downscaled meteorological forecasts into **timely, actionable, crop-specific agricultural guidance** for local farmers and extension workers.

---

## 2. Directory Hierarchy

```text
advisory/
├── README.md                      # Advisory specifications and logic (this file)
├── rules/                         # Declarative threshold condition rules (JSON / YAML)
├── crops/                         # Crop phenological stages, heat units, moisture requirements
└── templates/                     # Multilingual farmer advisory message templates (English, Hindi, Marathi)
```

---

## 3. Advisory Logic Architecture

Advisories are triggered by declarative rules combining:
1. **Downscaled Weather Condition:** Rain probability, $P_{50}$ rain depth, $P_{90}$ extreme risk, or $T_{max}$ heat stress.
2. **Crop Phenology Stage:** Sowing, Vegetative, Flowering, Grain Filling, or Harvesting.
3. **Agronomic Intervention:** Irrigation scheduling, fungicide/pesticide application, field drainage, or post-harvest storage.

### Example Trigger Logic
```text
IF Crop == "Soybean"
AND Stage == "Flowering"
AND (Prediction_P50_Rainfall > 25mm OR Prediction_P90_Rainfall > 40mm)
THEN
  Action: "Postpone chemical spraying and foliar fertilizer application."
  Reason: "Heavy precipitation within 24 hours will wash off chemical active ingredients."
  Severity: "WARNING"
  Source: "ICAR-IISR Agromet Advisory Bulletin"
```
