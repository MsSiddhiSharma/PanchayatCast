# Common Machine Learning Library — PanchayatCast

This directory contains shared, model-agnostic utilities used across all ML tracks.

---

## Subdirectories

- **`preprocessing/`**: Handling missing station values, geographic coordinate alignment, temporal train/val/test splits, and spatial cluster cross-validation splitting.
- **`feature_engineering/`**: Terrain feature extraction (lapse rates, topographic wetness index, solar aspect radiation), temporal lag calculation (1d, 3d, 7d cumulative rainfall).
- **`evaluation/`**: Standardized metric implementations (MAE, RMSE, Bias, POD, FAR, CSI, F1 Score, $R^2$).
- **`visualization/`**: Parity plots ($y$ vs $\hat{y}$), spatial error choropleths, feature importance plots, residual distributions.
- **`uncertainty/`**: Quantile regression loss functions, conformal prediction calibration routines for $P_{10}$ / $P_{90}$ coverage.
- **`utils/`**: Deterministic random seed management, JSON/YAML I/O helpers, logging setup.

> [!IMPORTANT]
> All ML models import utilities from `ml.common`. Do NOT introduce model-specific logic here. Keep code generic, thoroughly typed, and covered by unit tests.
