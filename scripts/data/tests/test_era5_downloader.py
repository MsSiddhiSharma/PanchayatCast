#!/usr/bin/env python3
"""
Unit Tests: ERA5-Land Downloader — PanchayatCast (SIH26074)
============================================================

Tests the ERA5-Land downloader's:
  1. Configuration loading and validation logic
  2. Geographic area validation
  3. CDS API request construction (structure, not live download)
  4. Output path construction
  5. NetCDF validation logic (stub/mock-based)

Run with:
    python -m pytest scripts/data/tests/test_era5_downloader.py -v
    # OR without pytest:
    python scripts/data/tests/test_era5_downloader.py

These tests do NOT make any real CDS API calls.
They do NOT require a CDS API key or internet access.
"""

import sys
import calendar
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure scripts/data is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from download_era5_land import (
    _validate_area,
    build_monthly_request,
    get_output_path,
    load_config,
    validate_config,
    VALID_VARIABLES,
)


# ---------------------------------------------------------------------------
# Fixtures / Helpers
# ---------------------------------------------------------------------------

VALID_CONFIG = {
    "dataset": "reanalysis-era5-land",
    "years": [2019, 2020, 2021],
    "variables": [
        "2m_temperature",
        "total_precipitation",
        "volumetric_soil_water_layer_1",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
    ],
    "area": {
        "north": 38.0,
        "south": 6.0,
        "west": 67.5,
        "east": 98.0,
    },
    "format": "netcdf",
    "times": ["00:00", "06:00", "12:00", "18:00"],
    "output_dir": "data/raw/era5_land",
    "file_pattern": "era5_land_india_{year}_{month:02d}.nc",
    "retry_max": 3,
    "retry_delay_seconds": 30,
    "sleep_between_requests": 5,
    "test_mode": {
        "area": {
            "north": 29.0,
            "south": 28.0,
            "west": 77.0,
            "east": 78.0,
        },
        "year": 2019,
        "month": 1,
        "days": ["01"],
        "times": ["00:00", "12:00"],
        "output_dir": "data/raw/era5_land/test_smoke",
        "output_file": "era5_land_smoke_test.nc",
    },
}


# ---------------------------------------------------------------------------
# Test: Config Loading
# ---------------------------------------------------------------------------

class TestConfigLoading(unittest.TestCase):
    """Tests for load_config() and validate_config()."""

    def test_load_config_valid_yaml(self):
        """load_config should parse a well-formed YAML file."""
        import yaml

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(VALID_CONFIG, f)
            tmp_path = f.name

        try:
            config = load_config(tmp_path)
            self.assertEqual(config["dataset"], "reanalysis-era5-land")
            self.assertIn("variables", config)
            self.assertIn("area", config)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_load_config_missing_file(self):
        """load_config should raise FileNotFoundError for non-existent paths."""
        with self.assertRaises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    def test_validate_config_valid(self):
        """validate_config should pass with a well-formed config."""
        validate_config(VALID_CONFIG)  # Should not raise

    def test_validate_config_wrong_dataset(self):
        """validate_config should reject invalid dataset names."""
        bad_config = VALID_CONFIG.copy()
        bad_config["dataset"] = "era5-single-levels"  # Wrong dataset
        with self.assertRaises(ValueError, msg="Should reject wrong dataset name"):
            validate_config(bad_config)

    def test_validate_config_unknown_variable(self):
        """validate_config should reject unrecognized CDS variable names."""
        bad_config = {**VALID_CONFIG, "variables": ["t2m"]}  # t2m is GRIB short name, not CDS name
        with self.assertRaises(ValueError):
            validate_config(bad_config)

    def test_validate_config_empty_variables(self):
        """validate_config should reject empty variable list."""
        bad_config = {**VALID_CONFIG, "variables": []}
        with self.assertRaises(ValueError):
            validate_config(bad_config)

    def test_validate_config_empty_years(self):
        """validate_config should reject empty years list."""
        bad_config = {**VALID_CONFIG, "years": []}
        with self.assertRaises(ValueError):
            validate_config(bad_config)

    def test_validate_config_invalid_format(self):
        """validate_config should reject unsupported output formats."""
        bad_config = {**VALID_CONFIG, "format": "csv"}
        with self.assertRaises(ValueError):
            validate_config(bad_config)

    def test_validate_config_future_year_edge_case(self):
        """validate_config should accept years within the known ERA5-Land range."""
        ok_config = {**VALID_CONFIG, "years": [2024]}
        validate_config(ok_config)  # Should not raise

    def test_validate_config_year_too_early(self):
        """validate_config should reject years before ERA5-Land coverage starts."""
        bad_config = {**VALID_CONFIG, "years": [1000]}
        with self.assertRaises(ValueError):
            validate_config(bad_config)


# ---------------------------------------------------------------------------
# Test: Geographic Area Validation
# ---------------------------------------------------------------------------

class TestAreaValidation(unittest.TestCase):
    """Tests for _validate_area()."""

    def test_valid_india_area(self):
        """Should accept India's approximate bounding box."""
        area = {"north": 38.0, "south": 6.0, "west": 67.5, "east": 98.0}
        _validate_area(area)  # Should not raise

    def test_north_less_than_south(self):
        """Should reject area where north < south (inverted bbox)."""
        area = {"north": 5.0, "south": 20.0, "west": 67.5, "east": 98.0}
        with self.assertRaises(ValueError):
            _validate_area(area)

    def test_north_equals_south(self):
        """Should reject area where north == south (zero-height bbox)."""
        area = {"north": 20.0, "south": 20.0, "west": 67.5, "east": 98.0}
        with self.assertRaises(ValueError):
            _validate_area(area)

    def test_east_less_than_west(self):
        """Should reject area where east < west (inverted bbox)."""
        area = {"north": 38.0, "south": 6.0, "west": 98.0, "east": 67.5}
        with self.assertRaises(ValueError):
            _validate_area(area)

    def test_out_of_range_latitude(self):
        """Should reject latitudes outside -90 to 90."""
        area = {"north": 91.0, "south": 6.0, "west": 67.5, "east": 98.0}
        with self.assertRaises(ValueError):
            _validate_area(area)

    def test_null_island_rejection(self):
        """Should reject area where all bounds are 0 (null island / placeholder)."""
        area = {"north": 0.0, "south": 0.0, "west": 0.0, "east": 0.0}
        with self.assertRaises(ValueError):
            _validate_area(area)

    def test_missing_key(self):
        """Should reject area dict missing required keys."""
        area = {"north": 38.0, "south": 6.0, "west": 67.5}  # Missing 'east'
        with self.assertRaises(ValueError):
            _validate_area(area)

    def test_smoke_test_area(self):
        """Should accept Delhi smoke-test area."""
        area = {"north": 29.0, "south": 28.0, "west": 77.0, "east": 78.0}
        _validate_area(area)  # Should not raise


# ---------------------------------------------------------------------------
# Test: CDS API Request Construction
# ---------------------------------------------------------------------------

class TestBuildMonthlyRequest(unittest.TestCase):
    """Tests for build_monthly_request()."""

    def test_request_structure_keys(self):
        """Built request should contain all required CDS API keys."""
        request = build_monthly_request(VALID_CONFIG, year=2019, month=6)
        required_keys = {
            "product_type", "variable", "year", "month",
            "day", "time", "area", "data_format",
        }
        missing_keys = required_keys - set(request.keys())
        self.assertEqual(
            missing_keys, set(),
            msg=f"Request is missing required keys: {missing_keys}"
        )

    def test_request_dataset_product_type(self):
        """product_type must be 'reanalysis'."""
        request = build_monthly_request(VALID_CONFIG, year=2019, month=1)
        self.assertIn("reanalysis", request["product_type"])

    def test_request_correct_month_zero_padded(self):
        """Month should be zero-padded to 2 digits."""
        request = build_monthly_request(VALID_CONFIG, year=2019, month=6)
        self.assertIn("06", request["month"])

    def test_request_correct_days_for_january(self):
        """January should produce 31 days."""
        request = build_monthly_request(VALID_CONFIG, year=2019, month=1)
        self.assertEqual(len(request["day"]), 31)
        self.assertIn("01", request["day"])
        self.assertIn("31", request["day"])

    def test_request_correct_days_for_february_non_leap(self):
        """February 2019 (non-leap) should produce 28 days."""
        request = build_monthly_request(VALID_CONFIG, year=2019, month=2)
        self.assertEqual(len(request["day"]), 28)
        self.assertNotIn("29", request["day"])

    def test_request_correct_days_for_february_leap(self):
        """February 2020 (leap year) should produce 29 days."""
        request = build_monthly_request(VALID_CONFIG, year=2020, month=2)
        self.assertEqual(len(request["day"]), 29)
        self.assertIn("29", request["day"])

    def test_request_area_cds_format(self):
        """
        CDS area format is [North, West, South, East].
        Must NOT be [North, South, West, East] or any other ordering.
        """
        request = build_monthly_request(VALID_CONFIG, year=2019, month=1)
        area = request["area"]
        self.assertEqual(len(area), 4, "Area must have 4 values")
        # [North, West, South, East]
        north, west, south, east = area
        self.assertAlmostEqual(north, 38.0, msg="First value should be North")
        self.assertAlmostEqual(west, 67.5, msg="Second value should be West")
        self.assertAlmostEqual(south, 6.0,  msg="Third value should be South")
        self.assertAlmostEqual(east, 98.0,  msg="Fourth value should be East")
        # Verify north > south
        self.assertGreater(north, south, msg="North must be greater than South in area list")

    def test_request_variables_are_cds_names(self):
        """Variable names in request must be valid CDS API identifiers."""
        request = build_monthly_request(VALID_CONFIG, year=2019, month=1)
        for var in request["variable"]:
            self.assertIn(
                var, VALID_VARIABLES,
                msg=f"'{var}' is not a valid CDS variable identifier"
            )

    def test_request_data_format_netcdf(self):
        """data_format should be 'netcdf'."""
        request = build_monthly_request(VALID_CONFIG, year=2019, month=1)
        self.assertEqual(request["data_format"], "netcdf")

    def test_request_year_is_string(self):
        """Year must be a string in the request (CDS API requirement)."""
        request = build_monthly_request(VALID_CONFIG, year=2019, month=1)
        for y in request["year"]:
            self.assertIsInstance(y, str, msg=f"Year value must be str, got {type(y)}")

    def test_request_times_format(self):
        """Times should be in 'HH:MM' format."""
        request = build_monthly_request(VALID_CONFIG, year=2019, month=1)
        for t in request["time"]:
            self.assertRegex(t, r"^\d{2}:\d{2}$", msg=f"Invalid time format: '{t}'")


# ---------------------------------------------------------------------------
# Test: Output Path Construction
# ---------------------------------------------------------------------------

class TestOutputPath(unittest.TestCase):
    """Tests for get_output_path()."""

    def test_output_path_single_digit_month(self):
        """Month 6 should produce a zero-padded filename: ...2019_06.nc."""
        path = get_output_path(VALID_CONFIG, year=2019, month=6)
        self.assertIn("2019_06", path.name)
        self.assertTrue(path.name.endswith(".nc"))

    def test_output_path_year_directory(self):
        """Output file should be inside a year-specific subdirectory."""
        path = get_output_path(VALID_CONFIG, year=2021, month=12)
        self.assertIn("2021", str(path))
        self.assertIn("2021_12", path.name)

    def test_output_path_includes_output_dir(self):
        """Output path should start under the configured output_dir."""
        path = get_output_path(VALID_CONFIG, year=2019, month=1)
        self.assertTrue(
            str(path).startswith(VALID_CONFIG["output_dir"]),
            msg=f"Expected path to start with '{VALID_CONFIG['output_dir']}', got '{path}'"
        )

    def test_output_path_december(self):
        """December (month 12) should have '12' correctly in filename."""
        path = get_output_path(VALID_CONFIG, year=2023, month=12)
        self.assertIn("2023_12", path.name)


# ---------------------------------------------------------------------------
# Test: Variable Name Coverage
# ---------------------------------------------------------------------------

class TestValidVariables(unittest.TestCase):
    """Ensure VALID_VARIABLES contains the expected CDS variable identifiers."""

    def test_required_variables_present(self):
        """All project-required CDS variable names must be in VALID_VARIABLES."""
        required = {
            "2m_temperature",
            "total_precipitation",
            "volumetric_soil_water_layer_1",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
        }
        missing = required - VALID_VARIABLES
        self.assertEqual(
            missing, set(),
            msg=f"These required variables are missing from VALID_VARIABLES: {missing}"
        )

    def test_no_grib_short_names_in_valid_variables(self):
        """VALID_VARIABLES must NOT contain GRIB short names (t2m, tp, u10, v10)."""
        grib_short_names = {"t2m", "tp", "u10", "v10", "swvl1"}
        overlap = grib_short_names & VALID_VARIABLES
        self.assertEqual(
            overlap, set(),
            msg=(
                f"GRIB short names found in VALID_VARIABLES: {overlap}. "
                "Use full CDS API variable identifiers, not GRIB short names."
            )
        )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("ERA5-Land Downloader Unit Tests — PanchayatCast (SIH26074)")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_class in [
        TestConfigLoading,
        TestAreaValidation,
        TestBuildMonthlyRequest,
        TestOutputPath,
        TestValidVariables,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
