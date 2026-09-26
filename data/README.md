# Data Management & Storage Architecture — PanchayatCast (SIH26074)

## 1. Primary Datasets Classification

| Dataset | Provider | Format | Role in Project |
| :--- | :--- | :--- | :--- |
| **Block Forecast** | IMD GKMS | JSON / CSV / API | **Downscaling Source** (Input to be refined) |
| **AWS / ARG Stations** | IMD | CSV / Table | **Independent Observation / Validation Ground Truth** |
| **IMD 0.25° Gridded Rainfall** | IMD NCC | NetCDF / Gridded binary | **Historical / Coarse Context** (Predictor, NOT ground truth) |
| **ERA5-Land Reanalysis** | ECMWF / Copernicus | NetCDF / GRIB | **Predictor / Context** (Atmospheric stability, moisture, wind) |
| **SRTM DEM** | NASA / USGS | GeoTIFF (30m / 90m) | **Terrain Features** (Elevation, slope, aspect, relief) |
| **Bhuvan LULC** | ISRO / NRSC | GeoTIFF / Shapefile | **Spatial Features** (Land cover fractions, roughness) |
| **Panchayat Boundaries** | Survey of India / MoPR / LGD | GeoJSON / Shapefile | **Target Geography** (Official downscaling polygons) |

> [!CAUTION]
> **Scientific Integrity Notice:** Do NOT describe IMD 0.25° gridded rainfall as Panchayat-scale ground truth. A 0.25° grid box averages weather over ~700 km². True ground-truth validation must always be conducted against independent **point-scale AWS/ARG station observations**.

---

## 2. Directory Hierarchy

```text
data/
├── README.md                      # Data governance and schemas (this file)
├── raw/                           # Unmodified source files (downloaded NetCDF, TIFFs, raw CSVs)
├── processed/                     # Cleaned, reprojection-aligned, and QC-filtered datasets
├── features/                      # Final tabular feature matrices per Panchayat
├── external/                      # Auxiliary lookup tables (LGD code maps, crop calendars)
└── sample/                        # Lightweight sample CSVs for unit testing and CI/CD
```

### What Belongs in Each Directory
- **`data/raw/`**: Exact raw downloads from external portals (e.g. `srtm_dem_block.tif`, `era5_land_2023.nc`). Strictly ignored by Git.
- **`data/processed/`**: Zonal statistics extractions, interpolated grids, merged station time series, outlier-flagged tables. Strictly ignored by Git.
- **`data/features/`**: Final model-ready Parquet tables (e.g. `panchayat_features_train.parquet`, `panchayat_features_test_heldout.parquet`). Conforms to Common Data Contract.
- **`data/sample/`**: Minimal, non-sensitive sample CSVs (e.g. 5 rows) committed to Git solely to allow test suites to run out-of-the-box in fresh clones.

---

## 3. Data Governance & Git Rules

1. **Never commit raw or large files to Git.** All `.nc`, `.tif`, `.parquet`, `.csv` in `raw/`, `processed/`, and `features/` are blocked by `.gitignore`.
2. **Stable Identifiers:** Every row in `features/` must use official, immutable Local Government Directory (LGD) Panchayat IDs.
