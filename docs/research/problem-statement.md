# Research: Problem Statement Analysis — SIH26074

## 1. Official Problem Statement
> **Title:** Downscaling of Weather Forecast from Block Level to Panchayat Level for Agro-Meteorological Advisory Services.  
> **Category:** Agriculture & Rural Development / Deep Tech  
> **Target End-User:** Smallholder farmers, Krishi Vigyan Kendras (KVKs), Block Agriculture Officers, State Agriculture Departments.

---

## 2. Background and Context

In India, the **India Meteorological Department (IMD)** operates the Gramin Krishi Mausam Sewa (GKMS) program, which disseminates bi-weekly weather-based Agromet Advisory Bulletins (AAB) at the **District** and **Block** levels.

While block-level forecasts represent a significant milestone over historical district-level advisories, a critical resolution mismatch remains:
- An administrative **Block** covers an area ranging from 150 to $1,000\text{ km}^2$, containing between 20 and 80 **Gram Panchayats**.
- Agricultural microclimates vary substantially within a single block due to:
  1. **Topographic Variance:** Elevation gradients of several hundred meters causing adiabatic lapse rate cooling and valley temperature inversions.
  2. **Orographic Precipitation:** Slopes facing prevailing monsoon moisture streams receive intensified rainfall, whereas leeward panchayats fall into rain-shadow zones.
  3. **Vegetation and Soil Moisture Feedback:** Panchayats with heavy canopy cover or irrigated valley floors exhibit lower diurnal temperature swings than rocky or barren uplands.

---

## 3. The Core Challenge of Downscaling

Downscaling numerical weather predictions to the Panchayat level presents distinct scientific hurdles:
1. **Sparsity of Observational Ground Truth:** Not every Gram Panchayat has an automated weather station (AWS). Models must generalize spatially to unmonitored panchayats using physiographic covariates.
2. **Extreme Value Distribution of Rainfall:** Rainfall is heavily skewed with high zero-frequency and sharp heavy-tail distributions. Standard regression models easily underestimate extremes or overpredict false drizzle.
3. **Operational Robustness:** Advisory dissemination requires predictions to execute reliably within minutes of IMD forecast release, ruling out computationally prohibitive multi-day atmospheric simulations at runtime.
