# Automation & Pipeline Scripts — PanchayatCast (SIH26074)

This directory contains executable automation scripts for data harvesting, preprocessing, model training, evaluation benchmarking, and container deployment.

---

## Directory Hierarchy

- **`scripts/data/`**: Scripts to fetch IMD forecast bulletins, download SRTM DEM tiles via USGS/NASA APIs, and pull ERA5-Land reanalysis from the Copernicus Climate Data Store (CDS).
- **`scripts/preprocessing/`**: Batch routines to clip DEM rasters to block boundaries, compute slope and aspect GeoTIFFs, and execute zonal statistics.
- **`scripts/training/`**: Batch training orchestration scripts (e.g. `train_all_tabular.py`, `train_deep_challengers.py`).
- **`scripts/evaluation/`**: Benchmark runners comparing model checkpoints against held-out station observations and generating JSON metric summaries.
- **`scripts/deployment/`**: Scripts for database migration execution (`run_migrations.sh`), Docker container health checks, and test runner verification.
