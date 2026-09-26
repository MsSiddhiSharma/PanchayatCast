# ERA5-Land: Reanalysis Dataset for PanchayatCast

## Table of Contents
1. [Dataset Overview](#dataset-overview)
2. [Role in PanchayatCast](#role-in-panchayatcast)
3. [Data Specifications](#data-specifications)
4. [Variable Reference](#variable-reference)
5. [Download Strategy](#download-strategy)
6. [Authentication Setup](#authentication-setup)
7. [De-accumulation of Precipitation](#de-accumulation-of-precipitation)
8. [Unit Conversions Applied](#unit-conversions-applied)
9. [Known Limitations and Caveats](#known-limitations-and-caveats)
10. [File Naming Convention](#file-naming-convention)
11. [Quick Start Workflow](#quick-start-workflow)
12. [References](#references)

---

## Dataset Overview

**ERA5-Land** is a high-resolution land-surface reanalysis dataset produced by the European Centre for Medium-Range Weather Forecasts (ECMWF) and distributed via the Copernicus Climate Data Store (CDS).

| Property | Value |
|---|---|
| **Dataset ID** | `reanalysis-era5-land` |
| **Temporal coverage** | January 1950 — present (updated monthly, ~5-day lag) |
| **Temporal resolution** | Hourly |
| **Spatial resolution** | 0.1° × 0.1° (~9 km at the equator) |
| **Spatial coverage** | Global |
| **Format** | NetCDF-4, GRIB2 |
| **License** | [CC-BY-4.0](https://spdx.org/licenses/CC-BY-4.0) |
| **DOI** | [10.24381/cds.e2161bac](https://doi.org/10.24381/cds.e2161bac) |
| **CDS Page** | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land |

ERA5-Land is produced by **replaying the land component** of the ECMWF ERA5 reanalysis forced with ERA5 atmospheric fields, with an additional lapse-rate correction applied to account for the higher grid resolution. It does not directly assimilate surface observations, but those observations influence the ERA5 atmospheric forcing.

---

## Role in PanchayatCast

> **CRITICAL SCIENTIFIC CONSTRAINT**
>
> ERA5-Land is used as **historical context / predictor features** for the ML downscaling models.
> It is **NOT** the Panchayat-level ground truth.
>
> The ERA5-Land native grid (~9 km) is still much coarser than the Panchayat-level target resolution (~1–5 km²). All model performance evaluation must use independent **AWS/ARG station observations**, never ERA5-Land values.

| Usage | Allowed? | Notes |
|---|---|---|
| Predictor feature for ML downscaling models | ✅ Yes | Core use |
| Historical context for temporal patterns | ✅ Yes | E.g. climatological normals |
| Ground truth for Panchayat-level validation | ❌ No | Use AWS/ARG stations only |
| Training labels / target variable | ❌ No | Must use observed station data |

In the PanchayatCast ML pipeline:
- **Block-level forecast** + **ERA5-Land climatological features** → ML model → **Panchayat-level downscaled forecast**
- ERA5-Land provides features such as: spatial temperature gradients, historical precipitation climatology, soil moisture context.
- Zonal statistics extracted from ERA5-Land onto Panchayat polygons are stored in `data/features/`.

---

## Data Specifications

### Coverage for PanchayatCast

We download ERA5-Land for **mainland India and its territories**:

| Bound | Value | Notes |
|---|---|---|
| North | 38.0°N | Ladakh/J&K + buffer |
| South | 6.0°N | Kanyakumari + island chain buffer |
| West | 67.5°E | Kutch/Gujarat western tip + buffer |
| East | 98.0°E | Arunachal Pradesh + buffer |

The 0.5° buffer is included to ensure complete spatial coverage when the ERA5-Land 0.1° grid is clipped to India's administrative boundary.

### Temporal Coverage (Initial Download)

| Period | Purpose |
|---|---|
| 2019–2021 | Training / historical calibration |
| 2022 | Validation year |
| 2023–2024 | Recent test / operational evaluation |

---

## Variable Reference

The following ERA5-Land variables are downloaded. **All variable names below are the exact CDS API identifiers** — they must not be confused with GRIB short names (e.g., `t2m`, `tp`) which are used in the output NetCDF files.

| CDS Variable Identifier | GRIB Short Name | Unit (raw) | Description |
|---|---|---|---|
| `2m_temperature` | `t2m` | K | Air temperature at 2m above surface |
| `total_precipitation` | `tp` | m (accumulated) | Accumulated precipitation since start of forecast/day |
| `volumetric_soil_water_layer_1` | `swvl1` | m³/m³ | Volumetric soil moisture, layer 1 (0–7 cm depth) |
| `10m_u_component_of_wind` | `u10` | m/s | Eastward wind component at 10m |
| `10m_v_component_of_wind` | `v10` | m/s | Northward wind component at 10m |

> **Variable naming warning:** The CDS API uses long descriptive names as input (e.g. `2m_temperature`). The output NetCDF files use the GRIB short names (e.g. `t2m`). This mapping is handled automatically by the processing script.

---

## Download Strategy

### Chunking

Data is downloaded in **monthly chunks** (one CDS API request per calendar month). This approach:

- Keeps individual request sizes manageable (~1–5 GB per month for the India domain)
- Allows clean resumption if a download fails mid-way
- Aligns with the ERA5-Land data structure (hourly within each month)

Each output file contains all 24 hours for all days in the requested month.

### Year-by-Year Execution

The recommended workflow is to run one year at a time:

```bash
python scripts/data/download_era5_land.py --year 2019
python scripts/data/download_era5_land.py --year 2020
# ... etc
```

Or all years at once (unattended):

```bash
python scripts/data/download_era5_land.py --all-years
```

### Skip Logic

The downloader checks for existing valid files before submitting a request. If a file already exists and passes the xarray validation checks, it is skipped. Use `--force` to override.

### Retry Logic

Each monthly request retries up to 3 times with a 30-second delay between attempts. CDS requests are queued server-side and can take minutes to hours depending on queue depth.

---

## Authentication Setup

> **Updated for CDS API migration (September 2024)**
>
> The Copernicus CDS migrated to ECMWF infrastructure in September 2024. The old `UID:API-KEY` format is no longer valid.

### Step 1 — Create a CDS account

Register at: https://cds.climate.copernicus.eu/

### Step 2 — Accept dataset terms

Visit the ERA5-Land dataset page and accept the licence:
https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land

This must be done manually via the browser for each dataset.

### Step 3 — Get your Personal Access Token

Log in → Profile → Copy your Personal Access Token (PAT). This is a single token string, NOT a `UID:KEY` pair.

### Step 4 — Configure authentication

**Method A (Recommended): `~/.cdsapirc` file**

```ini
url: https://cds.climate.copernicus.eu/api
key: <YOUR-PERSONAL-ACCESS-TOKEN>
```

**Method B: Environment variable**

```bash
export CDS_API_KEY=<YOUR-PERSONAL-ACCESS-TOKEN>
```

For the project, add to your local `.env` file (never commit this):
```
CDS_API_KEY=your_personal_access_token_here
```

The `.env` file is listed in `.gitignore` and will never be committed.

### Step 5 — Install cdsapi

```bash
pip install "cdsapi>=0.7.7"
```

---

## De-accumulation of Precipitation

ERA5-Land stores `total_precipitation` as an **accumulated value** (in metres), not as an instantaneous rate. The accumulation counter **resets at 01:00 UTC each day**.

This means:
- The value at `00:00` UTC represents the 1-hour accumulation from `00:00–01:00`.
- The value at `02:00` UTC represents accumulation since `01:00` that day.
- At `01:00` UTC the next day, the counter resets.

### De-accumulation formula applied in `process_era5_land.py`:

```
hourly_rate[t] = total_precip[t] - total_precip[t-1]
                 if result >= 0
                 else 0  (day boundary: accumulator reset)
```

The first timestep's value is kept as-is (no previous value to subtract).

After de-accumulation, precipitation is converted from **m/hr** → **mm/hr** (×1000).

**Reference:** [ECMWF ERA5-Land precipitation notes](https://confluence.ecmwf.int/display/CKB/ERA5-Land+documentation)

---

## Unit Conversions Applied

| Variable | Raw Unit | Processed Unit | Formula |
|---|---|---|---|
| `2m_temperature` | K (Kelvin) | °C (Celsius) | `T_C = T_K − 273.15` |
| `total_precipitation` | m (accumulated) | mm/hr | De-accumulate then × 1000 |
| `10m_u_component_of_wind` | m/s | m/s (kept) | — |
| `10m_v_component_of_wind` | m/s | m/s (kept) | — |
| Wind speed (derived) | — | m/s | `√(u² + v²)` |
| Wind direction (derived) | — | degrees (0–360°) | `arctan2(u, v) + 180°` mod 360 |
| `volumetric_soil_water_layer_1` | m³/m³ | m³/m³ (kept) | — |

---

## Known Limitations and Caveats

### 1. Resolution Mismatch
ERA5-Land is at 0.1° (~9 km). Indian Panchayats can be as small as 1–5 km². Direct assignment of ERA5-Land values to Panchayats introduces representativeness errors, which is exactly the problem the ML downscaling pipeline addresses.

### 2. No Direct Observation Assimilation
ERA5-Land does not directly assimilate surface weather observations. Its skill over complex terrain (Himalayan foothills, Western Ghats) is limited, especially for precipitation which is subject to strong orographic effects below the ERA5-Land grid scale.

### 3. Precipitation Bias
ERA5-Land systematically underestimates intense convective precipitation events common during Indian monsoon. Use precipitation features as **climatological context**, not as absolute values for validation.

### 4. Temporal Lag
ERA5-Land has a ~5-day processing lag. It is not suitable as a real-time data source. Use it only for historical climatological features.

### 5. No Data Leakage Guarantee Required Separately
The `forecast_issue_time` constraint must be enforced in the feature engineering pipeline. ERA5-Land dates used for predictor features must always predate the `forecast_issue_time` for any given forecast. This is NOT enforced by the downloader — it must be enforced by the ML feature pipeline.

### 6. Storage Requirements

Approximate storage for the India domain at full hourly resolution:

| Period | Approximate Size |
|---|---|
| 1 month (1 variable) | ~200–500 MB |
| 1 year (5 variables) | ~10–25 GB |
| 2019–2024 (5 variables) | ~60–150 GB |

Ensure sufficient local storage before starting a full download.

---

## File Naming Convention

### Raw Downloads

```
data/raw/era5_land/{YEAR}/era5_land_india_{YEAR}_{MONTH:02d}.nc
```

**Examples:**
```
data/raw/era5_land/2019/era5_land_india_2019_01.nc   ← January 2019
data/raw/era5_land/2019/era5_land_india_2019_06.nc   ← June 2019
data/raw/era5_land/2024/era5_land_india_2024_12.nc   ← December 2024
```

### Processed Outputs

```
data/processed/era5_land/{YEAR}/era5_land_india_processed_{YEAR}_{MONTH:02d}.nc
```

All raw `.nc` files are excluded from Git via `.gitignore`.

---

## Quick Start Workflow

### 0. Prerequisites

```bash
pip install "cdsapi>=0.7.7" xarray netCDF4 numpy pyyaml
```

Set up `~/.cdsapirc` (see [Authentication Setup](#authentication-setup)).

### 1. Smoke test — verify credentials

```bash
python scripts/data/download_era5_land.py --test
```

This downloads a small 1-day, 4-hour, tiny-area file and validates it. Takes ~2–5 minutes.

### 2. Run unit tests (no API key required)

```bash
python scripts/data/tests/test_era5_downloader.py
```

### 3. Download a single month

```bash
python scripts/data/download_era5_land.py --year 2019 --month 1
```

### 4. Download a full year

```bash
python scripts/data/download_era5_land.py --year 2019
```

### 5. Download all years (unattended)

```bash
python scripts/data/download_era5_land.py --all-years
```

### 6. Validate existing files without downloading

```bash
python scripts/data/download_era5_land.py --validate-only --year 2019
```

### 7. Process raw downloads

```bash
python scripts/data/process_era5_land.py --year 2019
```

---

## References

1. **ERA5-Land dataset documentation:**  
   https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land

2. **ERA5-Land documentation (ECMWF Confluence):**  
   https://confluence.ecmwf.int/display/CKB/ERA5-Land+documentation

3. **ERA5-Land DOI:**  
   Muñoz-Sabater, J., (2019): ERA5-Land hourly data from 1950 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS).  
   DOI: [10.24381/cds.e2161bac](https://doi.org/10.24381/cds.e2161bac)

4. **CDS API How-To Guide:**  
   https://cds.climate.copernicus.eu/how-to-api

5. **ERA5-Land precipitation accumulation:**  
   https://confluence.ecmwf.int/display/CKB/ERA5%3A+How+to+calculate+daily+total+precipitation

6. **India administrative boundary (Panchayat LGD codes):**  
   https://lgdirectory.gov.in/

7. **PanchayatCast Architecture Decision Records:**  
   See `docs/adr/` in this repository.
