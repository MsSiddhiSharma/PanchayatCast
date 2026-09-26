-- =============================================================================
-- PanchayatCast (SIH26074) PostgreSQL + PostGIS Schema Definition
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- -----------------------------------------------------------------------------
-- 1. Administrative Hierarchy & Spatial Entities
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS states (
    state_id VARCHAR(32) PRIMARY KEY,
    state_name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS districts (
    district_id VARCHAR(32) PRIMARY KEY,
    state_id VARCHAR(32) NOT NULL REFERENCES states(state_id) ON DELETE CASCADE,
    district_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blocks (
    block_id VARCHAR(32) PRIMARY KEY,
    district_id VARCHAR(32) NOT NULL REFERENCES districts(district_id) ON DELETE CASCADE,
    block_name VARCHAR(100) NOT NULL,
    centroid_lat DOUBLE PRECISION,
    centroid_lon DOUBLE PRECISION,
    elevation_mean DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS panchayats (
    panchayat_id VARCHAR(32) PRIMARY KEY,
    block_id VARCHAR(32) NOT NULL REFERENCES blocks(block_id) ON DELETE CASCADE,
    panchayat_name VARCHAR(100) NOT NULL,
    centroid_lat DOUBLE PRECISION NOT NULL,
    centroid_lon DOUBLE PRECISION NOT NULL,
    elevation_mean DOUBLE PRECISION,
    elevation_diff_block DOUBLE PRECISION,
    slope_mean DOUBLE PRECISION,
    aspect_sin DOUBLE PRECISION,
    aspect_cos DOUBLE PRECISION,
    lulc_agriculture_pct DOUBLE PRECISION DEFAULT 0.0,
    lulc_forest_pct DOUBLE PRECISION DEFAULT 0.0,
    lulc_water_pct DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS panchayat_geometries (
    panchayat_id VARCHAR(32) PRIMARY KEY REFERENCES panchayats(panchayat_id) ON DELETE CASCADE,
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_panchayat_geom ON panchayat_geometries USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_panchayat_block_id ON panchayats(block_id);

-- -----------------------------------------------------------------------------
-- 2. Data Sources & Observational Ground Truth
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS data_sources (
    source_id VARCHAR(64) PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    description TEXT,
    update_frequency VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weather_observations (
    observation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id VARCHAR(64) NOT NULL,
    station_name VARCHAR(100),
    panchayat_id VARCHAR(32) REFERENCES panchayats(panchayat_id) ON DELETE SET NULL,
    observation_date DATE NOT NULL,
    rainfall_mm DOUBLE PRECISION,
    tmax_celsius DOUBLE PRECISION,
    tmin_celsius DOUBLE PRECISION,
    qc_passed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_station_obs UNIQUE (station_id, observation_date)
);

CREATE INDEX IF NOT EXISTS idx_obs_station_date ON weather_observations(station_id, observation_date);
CREATE INDEX IF NOT EXISTS idx_obs_panchayat_date ON weather_observations(panchayat_id, observation_date);

-- -----------------------------------------------------------------------------
-- 3. Block Forecasts (Input from IMD)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS forecasts (
    forecast_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    block_id VARCHAR(32) NOT NULL REFERENCES blocks(block_id) ON DELETE CASCADE,
    issue_time TIMESTAMP WITH TIME ZONE NOT NULL,
    target_date DATE NOT NULL,
    lead_time_hours INT NOT NULL,
    forecast_rainfall_mm DOUBLE PRECISION NOT NULL,
    forecast_tmax_celsius DOUBLE PRECISION NOT NULL,
    source_id VARCHAR(64) REFERENCES data_sources(source_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_block_forecast UNIQUE (block_id, issue_time, target_date, lead_time_hours)
);

CREATE INDEX IF NOT EXISTS idx_forecast_lookup ON forecasts(block_id, target_date, lead_time_hours);

-- -----------------------------------------------------------------------------
-- 4. Model Registry, Experiments & Model Runs
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS model_registry (
    model_id VARCHAR(64) PRIMARY KEY,
    model_name VARCHAR(64) NOT NULL,
    model_version VARCHAR(32) NOT NULL,
    variable VARCHAR(32) NOT NULL,
    artifact_path VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL CHECK (status IN ('experimental', 'validated', 'candidate', 'production')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_model_ver UNIQUE (model_name, model_version, variable)
);

CREATE TABLE IF NOT EXISTS experiments (
    run_id VARCHAR(64) PRIMARY KEY,
    model_id VARCHAR(64) NOT NULL REFERENCES model_registry(model_id),
    git_commit VARCHAR(64),
    features_json JSONB NOT NULL,
    hyperparameters_json JSONB NOT NULL,
    training_period VARCHAR(100),
    validation_period VARCHAR(100),
    spatial_split_strategy VARCHAR(100),
    random_seed INT DEFAULT 42,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluation_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id VARCHAR(64) NOT NULL REFERENCES experiments(run_id) ON DELETE CASCADE,
    test_split_name VARCHAR(64) NOT NULL,
    mae DOUBLE PRECISION,
    rmse DOUBLE PRECISION,
    bias DOUBLE PRECISION,
    r2 DOUBLE PRECISION,
    pod DOUBLE PRECISION,
    far DOUBLE PRECISION,
    csi DOUBLE PRECISION,
    f1 DOUBLE PRECISION,
    picp_80 DOUBLE PRECISION,
    mpiw DOUBLE PRECISION,
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_runs (
    model_run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    forecast_id UUID NOT NULL REFERENCES forecasts(forecast_id) ON DELETE CASCADE,
    model_id VARCHAR(64) NOT NULL REFERENCES model_registry(model_id),
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 5. Panchayat Predictions & Uncertainty
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS panchayat_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_run_id UUID NOT NULL REFERENCES model_runs(model_run_id) ON DELETE CASCADE,
    panchayat_id VARCHAR(32) NOT NULL REFERENCES panchayats(panchayat_id) ON DELETE CASCADE,
    target_date DATE NOT NULL,
    lead_time_hours INT NOT NULL,
    variable VARCHAR(32) NOT NULL CHECK (variable IN ('rainfall', 'tmax')),
    predicted_p50 DOUBLE PRECISION NOT NULL,
    delta_from_block DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_panchayat_pred UNIQUE (model_run_id, panchayat_id, target_date, variable)
);

CREATE INDEX IF NOT EXISTS idx_panchayat_pred ON panchayat_predictions(panchayat_id, target_date, variable);

CREATE TABLE IF NOT EXISTS prediction_uncertainty (
    prediction_id UUID PRIMARY KEY REFERENCES panchayat_predictions(prediction_id) ON DELETE CASCADE,
    predicted_p10 DOUBLE PRECISION NOT NULL,
    predicted_p90 DOUBLE PRECISION NOT NULL,
    interval_width DOUBLE PRECISION GENERATED ALWAYS AS (predicted_p90 - predicted_p10) STORED,
    confidence_level DOUBLE PRECISION DEFAULT 0.80
);

-- -----------------------------------------------------------------------------
-- 6. Agro-Meteorological Advisories
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS advisory_rules (
    rule_id VARCHAR(64) PRIMARY KEY,
    crop_name VARCHAR(64) NOT NULL,
    phenological_stage VARCHAR(64) NOT NULL,
    condition_expression TEXT NOT NULL,
    recommendation_en TEXT NOT NULL,
    recommendation_hi TEXT,
    severity VARCHAR(32) DEFAULT 'INFO' CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL')),
    source_reference VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS advisory_runs (
    advisory_run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID NOT NULL REFERENCES panchayat_predictions(prediction_id) ON DELETE CASCADE,
    rule_id VARCHAR(64) NOT NULL REFERENCES advisory_rules(rule_id),
    crop_name VARCHAR(64) NOT NULL,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
