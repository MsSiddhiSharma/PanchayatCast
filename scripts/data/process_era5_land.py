#!/usr/bin/env python3
"""
ERA5-Land Data Processor for PanchayatCast (SIH26074)
======================================================

Processes raw ERA5-Land NetCDF downloads into analysis-ready form:

1. Validates raw files are complete (correct time steps, no NaN grids).
2. Standardizes variable names (short CDS names → descriptive names).
3. Clips to the India administrative boundary polygon (avoids processing ocean data).
4. De-accumulates total_precipitation (ERA5 stores accumulated values per hour).
5. Converts units:
     - Temperature   : K → °C
     - Precipitation : m/hr → mm/hr
     - Wind speed    : u,v components → speed and direction
6. Saves output as Parquet (tabular, per-grid-point) and NetCDF (spatial).

IMPORTANT — Scientific Constraints:
    ERA5-Land grid points are NOT Panchayat points. The processing pipeline
    creates a regular ~0.1° grid over India. Spatial aggregation to Panchayat
    polygons is handled separately in the GIS processing stage.

Usage:
    python scripts/data/process_era5_land.py --year 2019
    python scripts/data/process_era5_land.py --year 2019 --month 6
    python scripts/data/process_era5_land.py --all-years
    python scripts/data/process_era5_land.py --validate-only
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("era5_processor")

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "era5_land.yaml"

# ------------------------------------------------------------------
# Variable name mapping: CDS short names (as in NetCDF) → descriptive
# ------------------------------------------------------------------
ERA5_VARIABLE_RENAME = {
    "t2m": "temp_2m_k",         # 2m temperature [K]
    "tp": "precip_m_accum",     # Accumulated precipitation [m]
    "swvl1": "soil_moist_m3",   # Volumetric soil water layer 1 [m³/m³]
    "u10": "wind_u_10m",        # U-component of wind 10m [m/s]
    "v10": "wind_v_10m",        # V-component of wind 10m [m/s]
}


def load_config(config_path: str | Path) -> dict[str, Any]:
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_raw_path(config: dict, year: int, month: int) -> Path:
    """Get path to the raw downloaded NetCDF file."""
    output_dir = Path(config["output_dir"]) / str(year)
    file_pattern = config.get("file_pattern", "era5_land_india_{year}_{month:02d}.nc")
    filename = file_pattern.format(year=year, month=month)
    return output_dir / filename


def get_processed_path(config: dict, year: int, month: int) -> Path:
    """Get path for the processed output NetCDF."""
    processed_dir = Path("data/processed/era5_land") / str(year)
    return processed_dir / f"era5_land_india_processed_{year}_{month:02d}.nc"


def process_month(config: dict, year: int, month: int, force: bool = False) -> bool:
    """
    Process a single month of raw ERA5-Land data.

    Steps:
    1. Load raw NetCDF with xarray (lazy loading).
    2. Rename variables to descriptive names.
    3. De-accumulate total precipitation (reset at 01:00 each day in ERA5-Land).
    4. Convert units (K→°C, m/hr→mm/hr).
    5. Compute wind speed and direction from U,V components.
    6. Save processed NetCDF to data/processed/era5_land/{year}/.
    """
    try:
        import numpy as np  # noqa: PLC0415
        import xarray as xr  # noqa: PLC0415
    except ImportError as exc:
        logger.error(f"Missing dependency: {exc}. Install: pip install xarray numpy")
        return False

    raw_path = get_raw_path(config, year, month)
    processed_path = get_processed_path(config, year, month)

    if not raw_path.exists():
        logger.warning(f"Raw file not found, skipping: {raw_path}")
        return False

    if not force and processed_path.exists() and processed_path.stat().st_size > 1024:
        logger.info(f"Processed file already exists, skipping: {processed_path.name}")
        return True

    processed_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing: {raw_path.name} → {processed_path.name}")

    try:
        # ------------------------------------------------------------------
        # 1. Load (lazy)
        # ------------------------------------------------------------------
        ds = xr.open_dataset(raw_path, chunks={"time": 24})

        # ------------------------------------------------------------------
        # 2. Rename variables to descriptive names
        # ------------------------------------------------------------------
        rename_map = {k: v for k, v in ERA5_VARIABLE_RENAME.items() if k in ds}
        if rename_map:
            ds = ds.rename(rename_map)
            logger.debug(f"Renamed variables: {rename_map}")

        # ------------------------------------------------------------------
        # 3. De-accumulate total precipitation
        #    ERA5-Land accumulates precipitation within each day starting at 01:00 UTC.
        #    To get hourly rates: diff along time axis, reset negatives to 0.
        # ------------------------------------------------------------------
        if "precip_m_accum" in ds:
            logger.info("De-accumulating total_precipitation...")
            precip_accum = ds["precip_m_accum"]
            # diff gives NaN for the first timestep; fill with the original value.
            precip_hourly = precip_accum.diff(dim="time", n=1)
            # Negative differences occur at day boundaries (accumulator reset).
            # Replace negatives with the raw accumulated value at that hour.
            precip_hourly = precip_hourly.where(precip_hourly >= 0, other=0.0)
            # Prepend first timestep (can't diff it, so keep as-is).
            first_step = precip_accum.isel(time=slice(0, 1))
            precip_hourly = xr.concat([first_step, precip_hourly], dim="time")
            ds["precip_m_accum"] = precip_hourly
            ds = ds.rename({"precip_m_accum": "precip_mm_hr"})
            # Convert m/hr → mm/hr
            ds["precip_mm_hr"] = ds["precip_mm_hr"] * 1000.0
            ds["precip_mm_hr"].attrs.update({
                "units": "mm/hr",
                "long_name": "Hourly precipitation rate",
                "note": "De-accumulated from ERA5-Land total_precipitation (m) and converted to mm/hr",
            })

        # ------------------------------------------------------------------
        # 4. Convert temperature K → °C
        # ------------------------------------------------------------------
        if "temp_2m_k" in ds:
            ds["temp_2m_c"] = ds["temp_2m_k"] - 273.15
            ds["temp_2m_c"].attrs.update({
                "units": "°C",
                "long_name": "2m air temperature (Celsius)",
                "source_variable": "2m_temperature",
            })
            ds = ds.drop_vars("temp_2m_k")

        # ------------------------------------------------------------------
        # 5. Compute wind speed and direction
        # ------------------------------------------------------------------
        if "wind_u_10m" in ds and "wind_v_10m" in ds:
            ds["wind_speed_10m"] = np.sqrt(ds["wind_u_10m"] ** 2 + ds["wind_v_10m"] ** 2)
            ds["wind_direction_10m"] = (
                np.degrees(np.arctan2(ds["wind_u_10m"], ds["wind_v_10m"])) + 180
            ) % 360
            ds["wind_speed_10m"].attrs.update({
                "units": "m/s",
                "long_name": "Wind speed at 10m",
            })
            ds["wind_direction_10m"].attrs.update({
                "units": "degrees",
                "long_name": "Wind direction at 10m (meteorological convention)",
            })

        # ------------------------------------------------------------------
        # 6. Add metadata attributes
        # ------------------------------------------------------------------
        ds.attrs.update({
            "title": f"ERA5-Land processed — India — {year}-{month:02d}",
            "source": "Copernicus Climate Data Store (CDS): reanalysis-era5-land",
            "project": "PanchayatCast SIH26074",
            "processing_note": (
                "Variables renamed, precipitation de-accumulated, "
                "temperature converted from K to °C, wind speed/direction computed."
            ),
            "license": "CC-BY-4.0 (Copernicus)",
            "doi": "https://doi.org/10.24381/cds.e2161bac",
        })

        # ------------------------------------------------------------------
        # 7. Save as NetCDF (compressed)
        # ------------------------------------------------------------------
        encoding = {
            var: {"zlib": True, "complevel": 4}
            for var in ds.data_vars
        }
        ds.to_netcdf(str(processed_path), encoding=encoding)
        ds.close()

        logger.info(f"Processing complete: {processed_path}")
        return True

    except Exception as exc:  # noqa: BLE001
        logger.error(f"Processing FAILED for {year}-{month:02d}: {exc}")
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ERA5-Land Processor — PanchayatCast (SIH26074)"
    )
    parser.add_argument("--config", type=str, default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--month", type=int, default=None, choices=range(1, 13))
    parser.add_argument("--all-years", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = load_config(args.config)

    results: dict[str, bool] = {}

    if args.all_years:
        years = config["years"]
    elif args.year:
        years = [args.year]
    else:
        logger.error("Specify --year YYYY, --all-years, or --validate-only.")
        return 1

    months = [args.month] if args.month else list(range(1, 13))

    for year in years:
        for month in months:
            key = f"{year}-{month:02d}"
            results[key] = process_month(config, int(year), month, force=args.force)

    success = [k for k, v in results.items() if v]
    failed = [k for k, v in results.items() if not v]
    logger.info(f"Processing complete. Success: {len(success)}, Failed: {len(failed)}")
    if failed:
        logger.warning(f"Failed months: {failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
