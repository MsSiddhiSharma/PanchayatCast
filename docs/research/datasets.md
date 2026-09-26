# Research: Datasets & Meteorological Sources — PanchayatCast (SIH26074)

This document formalizes the scientific role, source provenance, and limitations of every dataset utilized in the project.

---

## 1. Primary Datasets Classification

| Dataset | Provider | Spatial Resolution | Temporal Extent | Primary Role in PanchayatCast |
| :--- | :--- | :--- | :--- | :--- |
| **IMD Block Forecast** | IMD GKMS | Block polygon (~10–25 km) | Operational daily (1–5 day lead) | **Downscaling Source Input** |
| **IMD AWS / ARG Stations** | IMD | Point locations (~3,000+ pan-India) | Hourly / Daily cumulative | **Independent Validation Ground Truth** |
| **IMD 0.25° Gridded Rainfall** | IMD National Climate Centre | 0.25° $\times$ 0.25° (~27 km) | Historical daily (1901–present) | **Regional Historical Context & Predictor** |
| **ERA5-Land Reanalysis** | ECMWF / Copernicus CDS | 0.1° $\times$ 0.1° (~9 km) | 1950–present (Hourly/Daily) | **Atmospheric Covariates & Lags** |
| **SRTM DEM** | NASA / USGS | 1 arc-second (30m) & 90m | Static elevation | **Physiographic Terrain Predictor** |
| **Bhuvan LULC** | ISRO / NRSC | 1:50,000 scale (~30m–250m) | Annual / Static | **Surface Roughness & Land Cover Predictor** |
| **Panchayat Boundaries** | Survey of India / MoPR / LGD | Vector polygons | Census 2011 / LGD Updated | **Target Downscaling Geography** |

---

## 2. Critical Scientific Distinctions

> [!CAUTION]
> **Ground Truth Rule:** Coarse gridded datasets (such as IMD 0.25° rainfall or ERA5-Land 0.1°) are **regional context and historical predictors**, NOT Panchayat-scale ground truth.
> 
> A 0.25° grid box averages rainfall over roughly $700\text{ km}^2$. In a hilly terrain, one panchayat in that grid box might receive 80 mm while another receives 5 mm. Validating a panchayat model against 0.25° gridded data would be circular and invalid.
> 
> True validation must always be conducted against independent **point-scale station observations (AWS/ARG)**.
