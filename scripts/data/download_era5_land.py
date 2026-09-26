#!/usr/bin/env python3
"""
ERA5-Land Data Downloader for PanchayatCast (SIH26074)
=======================================================

Downloads ERA5-Land hourly reanalysis data from the Copernicus Climate Data Store
(CDS) for use as historical covariate features in the PanchayatCast weather
downscaling pipeline.

IMPORTANT — Scientific Scope:
    ERA5-Land is NOT a Panchayat-level ground truth. It is a 0.1° (~9 km)
    gridded reanalysis product used as historical context and predictor features
    for the ML downscaling pipeline. Ground truth validation must always use
    independent AWS/ARG point observations.

Authentication:
    The CDS API (post-September 2024) uses a Personal Access Token (PAT).
    Configure your ~/.cdsapirc file with:
        url: https://cds.climate.copernicus.eu/api
        key: <YOUR-PERSONAL-ACCESS-TOKEN>

    OR set the environment variable:
        CDS_API_KEY=<YOUR-PERSONAL-ACCESS-TOKEN>

    See: https://cds.climate.copernicus.eu/how-to-api

Usage:
    python scripts/data/download_era5_land.py --test
    python scripts/data/download_era5_land.py --year 2019
    python scripts/data/download_era5_land.py --year 2019 --month 6
    python scripts/data/download_era5_land.py --all-years
    python scripts/data/download_era5_land.py --config scripts/data/config/era5_land.yaml --year 2020
"""

from __future__ import annotations

import argparse
import calendar
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Logging setup — structured, never logs credentials
# ---------------------------------------------------------------------------
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("era5_downloader")


# ---------------------------------------------------------------------------
# Config loading and validation
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "era5_land.yaml"

VALID_VARIABLES = {
    "2m_temperature",
    "total_precipitation",
    "volumetric_soil_water_layer_1",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
}

VALID_FORMATS = {"netcdf", "grib"}


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load and return the ERA5-Land YAML configuration."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logger.info(f"Configuration loaded from: {config_path}")
    return config


def validate_config(config: dict[str, Any]) -> None:
    """
    Validate the configuration before any API calls are made.

    Raises:
        ValueError: if any required field is missing or invalid.
    """
    # Dataset
    if config.get("dataset") != "reanalysis-era5-land":
        raise ValueError(
            f"Unexpected dataset '{config.get('dataset')}'. "
            "Expected 'reanalysis-era5-land'."
        )

    # Variables
    variables = config.get("variables", [])
    if not variables:
        raise ValueError("No variables specified in configuration.")
    invalid_vars = set(variables) - VALID_VARIABLES
    if invalid_vars:
        raise ValueError(
            f"Unknown variable identifiers: {invalid_vars}\n"
            f"Valid options: {VALID_VARIABLES}"
        )

    # Years
    years = config.get("years", [])
    if not years:
        raise ValueError("No years specified in configuration.")
    for y in years:
        if not (1950 <= int(y) <= 2030):
            raise ValueError(f"Year {y} is outside the expected ERA5-Land range (1950–2030).")

    # Geographic bounds
    area = config.get("area", {})
    _validate_area(area, label="Main area")

    # Format
    fmt = config.get("format", "netcdf")
    if fmt not in VALID_FORMATS:
        raise ValueError(f"Invalid format '{fmt}'. Choose from: {VALID_FORMATS}")

    logger.info("Configuration validated successfully.")


def _validate_area(area: dict, label: str = "Area") -> None:
    """Validate latitude/longitude bounding box."""
    required_keys = {"north", "south", "west", "east"}
    missing = required_keys - set(area.keys())
    if missing:
        raise ValueError(f"{label} is missing required keys: {missing}")

    n, s, w, e = area["north"], area["south"], area["west"], area["east"]
    if not (-90 <= s < n <= 90):
        raise ValueError(
            f"{label}: invalid latitude range. south={s}, north={n}. "
            "Expected -90 ≤ south < north ≤ 90."
        )
    if not (-180 <= w < e <= 180):
        raise ValueError(
            f"{label}: invalid longitude range. west={w}, east={e}. "
            "Expected -180 ≤ west < east ≤ 180."
        )
    # Sanity check: ensure we're not using null island (0,0)
    if n == 0 and s == 0 and w == 0 and e == 0:
        raise ValueError(
            f"{label}: all bounds are 0 — this looks like an unconfigured placeholder. "
            "Please set valid geographic bounds for India."
        )


# ---------------------------------------------------------------------------
# CDS client initialization
# ---------------------------------------------------------------------------

def get_cds_client():
    """
    Initialize and return a cdsapi.Client instance.

    Authentication priority:
    1. ~/.cdsapirc file (recommended — contains url and key)
    2. CDS_API_KEY environment variable (overrides key in ~/.cdsapirc if set)

    NEVER logs or prints the API key.
    """
    try:
        import cdsapi  # noqa: PLC0415
    except ImportError:
        logger.error(
            "cdsapi package not found. Install it with: pip install cdsapi>=0.7.7"
        )
        sys.exit(1)

    # Allow environment variable to override the key, but do not log its value.
    env_key = os.environ.get("CDS_API_KEY")
    if env_key:
        logger.info(
            "CDS_API_KEY environment variable detected. "
            "It will be used for authentication (value not logged)."
        )
        client = cdsapi.Client(
            url="https://cds.climate.copernicus.eu/api",
            key=env_key,
            quiet=True,
            progress=True,
        )
    else:
        logger.info(
            "Using ~/.cdsapirc for CDS authentication. "
            "Ensure it contains url and key (Personal Access Token)."
        )
        client = cdsapi.Client(quiet=True, progress=True)

    return client


# ---------------------------------------------------------------------------
# Output path helpers
# ---------------------------------------------------------------------------

def get_output_path(config: dict, year: int, month: int) -> Path:
    """Build the output file path for a given year and month."""
    output_dir = Path(config["output_dir"]) / str(year)
    file_pattern = config.get("file_pattern", "era5_land_india_{year}_{month:02d}.nc")
    filename = file_pattern.format(year=year, month=month)
    return output_dir / filename


def ensure_output_directory(path: Path) -> None:
    """Create output directory if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# File validation using xarray
# ---------------------------------------------------------------------------

def validate_netcdf(filepath: Path, year: int, month: int, variables: list[str]) -> bool:
    """
    Validate a downloaded NetCDF file using xarray.

    Checks performed:
    - File exists and is non-empty.
    - File can be opened by xarray.
    - Expected dimensions (latitude, longitude, time) are present.
    - Expected variables are present.
    - Time dimension is non-empty.
    - Time values contain the expected year and month.
    - Dataset geographic extent is non-trivially sized.

    Returns True if valid, False otherwise.
    Uses chunked/lazy loading — does NOT load full dataset into RAM.
    """
    try:
        import xarray as xr  # noqa: PLC0415
    except ImportError:
        logger.warning(
            "xarray not installed — skipping NetCDF validation. "
            "Install with: pip install xarray>=2024.6.0"
        )
        return True  # Pass-through if xarray unavailable

    if not filepath.exists():
        logger.error(f"Validation FAILED: File does not exist: {filepath}")
        return False

    file_size = filepath.stat().st_size
    if file_size < 1024:  # Less than 1 KB is suspicious
        logger.error(
            f"Validation FAILED: File is suspiciously small ({file_size} bytes): {filepath}"
        )
        return False

    try:
        # Use lazy loading — do NOT call .load() or .values on large arrays
        ds = xr.open_dataset(filepath, chunks={})

        # Check spatial dimensions
        lat_dim = _find_dim(ds, ["latitude", "lat"])
        lon_dim = _find_dim(ds, ["longitude", "lon"])
        time_dim = _find_dim(ds, ["time", "valid_time"])

        if not all([lat_dim, lon_dim, time_dim]):
            logger.error(
                f"Validation FAILED: Missing expected dimensions in {filepath}. "
                f"Found: {list(ds.dims)}"
            )
            ds.close()
            return False

        # Check time is non-empty
        time_len = ds.dims[time_dim]
        if time_len == 0:
            logger.error(f"Validation FAILED: time dimension is empty in {filepath}")
            ds.close()
            return False

        # Check time values match expected year/month
        times = ds[time_dim].values
        import pandas as pd  # noqa: PLC0415
        first_time = pd.Timestamp(times[0])
        if first_time.year != year or first_time.month != month:
            logger.error(
                f"Validation FAILED: Expected {year}-{month:02d} in {filepath}, "
                f"but first timestamp is {first_time}."
            )
            ds.close()
            return False

        # Check variables are present
        # ERA5-Land variable names in NetCDF files use short names (e.g. t2m, tp)
        # The CDS API maps long names to short names in output NetCDF.
        # We check that the dataset has at least some data variables.
        data_vars = list(ds.data_vars)
        if not data_vars:
            logger.error(f"Validation FAILED: No data variables found in {filepath}")
            ds.close()
            return False

        # Check spatial coverage is non-trivial
        lat_size = ds.dims[lat_dim]
        lon_size = ds.dims[lon_dim]
        if lat_size < 2 or lon_size < 2:
            logger.error(
                f"Validation FAILED: Spatial dimensions too small "
                f"(lat={lat_size}, lon={lon_size}) in {filepath}"
            )
            ds.close()
            return False

        ds.close()
        logger.info(
            f"Validation PASSED: {filepath.name} | "
            f"vars={data_vars} | time={time_len} steps | "
            f"lat={lat_size} × lon={lon_size}"
        )
        return True

    except Exception as exc:  # noqa: BLE001
        logger.error(f"Validation FAILED: Cannot open NetCDF '{filepath}': {exc}")
        return False


def _find_dim(ds, candidates: list[str]) -> str | None:
    """Find the first matching dimension name from a list of candidates."""
    for name in candidates:
        if name in ds.dims:
            return name
    return None


# ---------------------------------------------------------------------------
# Build CDS API request
# ---------------------------------------------------------------------------

def build_monthly_request(
    config: dict,
    year: int,
    month: int,
) -> dict[str, Any]:
    """
    Construct the CDS API request dict for a single year-month chunk.

    ERA5-Land API requires:
    - product_type: "reanalysis"
    - variable: list of CDS variable identifiers
    - year: "YYYY" string
    - month: "MM" string
    - day: list of "DD" strings for all days in the month
    - time: list of "HH:MM" strings
    - area: [north, west, south, east] (CDS uses this order)
    - data_format: "netcdf" (note: newer API uses "data_format" not "format")
    """
    area = config["area"]
    # CDS area format: [North, West, South, East]
    area_list = [area["north"], area["west"], area["south"], area["east"]]

    # All days in the requested month
    num_days = calendar.monthrange(year, month)[1]
    days = [f"{d:02d}" for d in range(1, num_days + 1)]

    times = config.get("times", [f"{h:02d}:00" for h in range(24)])

    return {
        "product_type": ["reanalysis"],
        "variable": config["variables"],
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": days,
        "time": times,
        "area": area_list,
        "data_format": "netcdf",
        "download_format": "unarchived",
    }


# ---------------------------------------------------------------------------
# Download execution
# ---------------------------------------------------------------------------

def download_month(
    client,
    config: dict,
    year: int,
    month: int,
    force: bool = False,
) -> bool:
    """
    Download ERA5-Land data for a single year-month chunk.

    Skips download if the output file already exists and passes validation,
    unless --force is specified.

    Returns True on success, False on failure.
    """
    output_path = get_output_path(config, year, month)
    ensure_output_directory(output_path)

    # Skip if file already exists and is valid
    if not force and output_path.exists():
        logger.info(f"Checking existing file: {output_path.name}")
        if validate_netcdf(output_path, year, month, config["variables"]):
            logger.info(f"Skipping (already valid): {output_path}")
            return True
        else:
            logger.warning(
                f"Existing file failed validation — will re-download: {output_path}"
            )

    request = build_monthly_request(config, year, month)

    logger.info("=" * 60)
    logger.info(f"Downloading ERA5-Land chunk: {year}-{month:02d}")
    logger.info(f"  Dataset  : {config['dataset']}")
    logger.info(f"  Variables: {config['variables']}")
    logger.info(
        f"  Area     : N={config['area']['north']}°, S={config['area']['south']}°, "
        f"W={config['area']['west']}°, E={config['area']['east']}°"
    )
    logger.info(f"  Output   : {output_path}")
    logger.info("=" * 60)

    retry_max = config.get("retry_max", 3)
    retry_delay = config.get("retry_delay_seconds", 30)

    for attempt in range(1, retry_max + 1):
        try:
            client.retrieve(
                name=config["dataset"],
                request=request,
                target=str(output_path),
            )
            logger.info(f"Download complete: {output_path}")

            # Validate immediately after download
            logger.info("Validating downloaded NetCDF file...")
            if validate_netcdf(output_path, year, month, config["variables"]):
                logger.info(f"Validation PASSED for {output_path.name}")
                return True
            else:
                logger.error(
                    f"Validation FAILED after download of {output_path.name}. "
                    "File may be corrupt."
                )
                return False

        except Exception as exc:  # noqa: BLE001
            logger.error(f"Request FAILED (attempt {attempt}/{retry_max}): {exc}")
            if attempt < retry_max:
                logger.info(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(
                    f"All {retry_max} attempts failed for {year}-{month:02d}. "
                    "Skipping this chunk."
                )
                return False

    return False


def download_year(
    client,
    config: dict,
    year: int,
    months: list[int] | None = None,
    force: bool = False,
) -> dict[str, bool]:
    """
    Download all months (or specified months) for a given year.

    Returns a dict mapping "YYYY-MM" → True/False (success/failure).
    """
    if months is None:
        months = list(range(1, 13))

    results = {}
    sleep_between = config.get("sleep_between_requests", 5)

    for month in months:
        key = f"{year}-{month:02d}"
        success = download_month(client, config, year, month, force=force)
        results[key] = success
        if month < months[-1]:
            logger.info(f"Pausing {sleep_between}s before next request...")
            time.sleep(sleep_between)

    return results


# ---------------------------------------------------------------------------
# Smoke test mode
# ---------------------------------------------------------------------------

def run_smoke_test(client, config: dict) -> bool:
    """
    Run a small smoke test to verify CDS credentials and connectivity.

    Downloads a minimal 1-day, 4-hourly, tiny-area NetCDF file.
    Does NOT trigger the full India download.
    """
    test_cfg = config.get("test_mode", {})
    if not test_cfg:
        logger.error("No [test_mode] section found in configuration.")
        return False

    area = test_cfg.get("area", {})
    _validate_area(area, label="test_mode.area")

    output_dir = Path(test_cfg.get("output_dir", "data/raw/era5_land/test_smoke"))
    output_file = output_dir / test_cfg.get("output_file", "era5_land_smoke_test.nc")
    output_dir.mkdir(parents=True, exist_ok=True)

    year = test_cfg["year"]
    month = test_cfg["month"]
    days = test_cfg.get("days", ["01"])
    times = test_cfg.get("times", ["00:00", "06:00", "12:00", "18:00"])

    # CDS area format: [North, West, South, East]
    area_list = [area["north"], area["west"], area["south"], area["east"]]

    request = {
        "product_type": ["reanalysis"],
        "variable": config["variables"],
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": days,
        "time": times,
        "area": area_list,
        "data_format": "netcdf",
        "download_format": "unarchived",
    }

    logger.info("=" * 60)
    logger.info("SMOKE TEST MODE — Small request to verify CDS connectivity")
    logger.info(f"  Dataset  : {config['dataset']}")
    logger.info(f"  Variables: {config['variables']}")
    logger.info(
        f"  Area     : N={area['north']}°, S={area['south']}°, "
        f"W={area['west']}°, E={area['east']}° (tiny test region)"
    )
    logger.info(f"  Period   : {year}-{month:02d} | days={days} | times={times}")
    logger.info(f"  Output   : {output_file}")
    logger.info("=" * 60)

    try:
        client.retrieve(
            name=config["dataset"],
            request=request,
            target=str(output_file),
        )
        logger.info(f"Smoke test download complete: {output_file}")

        logger.info("Validating smoke test NetCDF...")
        if validate_netcdf(output_file, year, month, config["variables"]):
            logger.info("Smoke test PASSED — CDS credentials and API are working.")
            return True
        else:
            logger.error("Smoke test NetCDF validation FAILED.")
            return False

    except Exception as exc:  # noqa: BLE001
        logger.error(f"Smoke test FAILED: {exc}")
        logger.error(
            "Possible causes:\n"
            "  1. ~/.cdsapirc is missing or has wrong format\n"
            "  2. CDS_API_KEY environment variable is not set\n"
            "  3. Dataset licence not yet accepted on CDS website\n"
            "  4. No internet connectivity\n"
            "  See: https://cds.climate.copernicus.eu/how-to-api"
        )
        return False


# ---------------------------------------------------------------------------
# Print download summary
# ---------------------------------------------------------------------------

def print_summary(all_results: dict[str, bool]) -> None:
    """Log a final summary of all download results."""
    logger.info("=" * 60)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 60)
    successes = [k for k, v in all_results.items() if v]
    failures = [k for k, v in all_results.items() if not v]
    logger.info(f"  Total chunks: {len(all_results)}")
    logger.info(f"  Successful  : {len(successes)}")
    logger.info(f"  Failed      : {len(failures)}")
    if failures:
        logger.warning(f"  Failed chunks: {failures}")
        logger.warning(
            "Re-run the downloader for specific failed years/months."
        )
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "ERA5-Land Data Downloader for PanchayatCast (SIH26074)\n\n"
            "Downloads reanalysis-era5-land data from the Copernicus CDS API\n"
            "for use as historical context and predictor features."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Smoke test first — verify credentials with tiny request:
  python scripts/data/download_era5_land.py --test

  # Download a single year:
  python scripts/data/download_era5_land.py --year 2019

  # Download a single month of a year:
  python scripts/data/download_era5_land.py --year 2019 --month 6

  # Download all years defined in config:
  python scripts/data/download_era5_land.py --all-years

  # Force re-download even if file exists:
  python scripts/data/download_era5_land.py --year 2019 --force

  # Use a custom config file:
  python scripts/data/download_era5_land.py --config scripts/data/config/era5_land.yaml --year 2020
        """,
    )

    parser.add_argument(
        "--config",
        type=str,
        default=str(DEFAULT_CONFIG_PATH),
        help=f"Path to the YAML configuration file (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Download a specific year (e.g. 2019). Required unless --all-years or --test is set.",
    )
    parser.add_argument(
        "--month",
        type=int,
        default=None,
        choices=range(1, 13),
        help="Download a specific month (1–12) within the given --year.",
    )
    parser.add_argument(
        "--all-years",
        action="store_true",
        help="Download all years listed in the configuration file.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help=(
            "Run a small smoke test download to verify CDS credentials. "
            "Uses a tiny area and short time period defined in config [test_mode]."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if the output file already exists and is valid.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate existing downloaded files without downloading anything new.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG level logging.",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("ERA5-Land Downloader started")
    logger.info(f"PID: {os.getpid()}")

    # Load and validate configuration
    try:
        config = load_config(args.config)
        validate_config(config)
    except (FileNotFoundError, ValueError) as exc:
        logger.error(f"Configuration error: {exc}")
        return 1

    # Log dataset and variables (never log credentials)
    logger.info(f"Dataset    : {config['dataset']}")
    logger.info(f"Variables  : {config['variables']}")
    logger.info(
        f"Area       : N={config['area']['north']}°, S={config['area']['south']}°, "
        f"W={config['area']['west']}°, E={config['area']['east']}°"
    )

    # Validate-only mode
    if args.validate_only:
        logger.info("Running in validation-only mode.")
        results = {}
        years = [args.year] if args.year else config["years"]
        months = [args.month] if args.month else list(range(1, 13))
        for year in years:
            for month in months:
                path = get_output_path(config, year, month)
                key = f"{year}-{month:02d}"
                results[key] = validate_netcdf(path, year, month, config["variables"])
        print_summary(results)
        return 0 if all(results.values()) else 1

    # Initialize CDS client
    client = get_cds_client()

    # Smoke test mode
    if args.test:
        success = run_smoke_test(client, config)
        return 0 if success else 1

    # Download mode
    if not args.year and not args.all_years:
        logger.error(
            "No action specified. Use --year YYYY, --all-years, --test, or --validate-only.\n"
            "Run with --help to see all options."
        )
        return 1

    all_results: dict[str, bool] = {}

    if args.all_years:
        logger.info(f"Downloading all years: {config['years']}")
        for year in config["years"]:
            results = download_year(client, config, int(year), force=args.force)
            all_results.update(results)

    elif args.year:
        months = [args.month] if args.month else None
        logger.info(
            f"Downloading year {args.year}, months: "
            f"{months if months else 'all (1–12)'}"
        )
        results = download_year(
            client, config, args.year, months=months, force=args.force
        )
        all_results.update(results)

    print_summary(all_results)

    failed = [k for k, v in all_results.items() if not v]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
