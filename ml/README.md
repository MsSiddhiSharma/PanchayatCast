# Machine Learning Subsystem — PanchayatCast (SIH26074)

## 1. Modular Model Isolation Philosophy

In PanchayatCast, **ML development is strictly partitioned by model family**.
Different teammates develop, tune, and experiment with different models concurrently:
- Teammate A works in [ml/random_forest/](file:///Users/siddhisharma/Desktop/PanchayatCast/ml/random_forest/)
- Teammate B works in [ml/xgboost/](file:///Users/siddhisharma/Desktop/PanchayatCast/ml/xgboost/)
- Teammate C works in [ml/lightgbm/](file:///Users/siddhisharma/Desktop/PanchayatCast/ml/lightgbm/)
- Teammate D works in [ml/convlstm/](file:///Users/siddhisharma/Desktop/PanchayatCast/ml/convlstm/)
- Teammate E works in [ml/cnn_unet/](file:///Users/siddhisharma/Desktop/PanchayatCast/ml/cnn_unet/)

No teammate needs to edit, debug, or wait for another teammate's model pipeline.

```text
ml/
├── README.md                      # Universal ML guide and interfaces (this file)
├── COLLABORATION.md               # Strict team rules and boundary guidelines
├── common/                        # SHARED reusable modules (read-only for model devs)
│   ├── preprocessing/             # Imputation, scaling, spatial splits
│   ├── feature_engineering/       # Static terrain & temporal lag extraction
│   ├── evaluation/                # Official metric scoring functions
│   ├── visualization/             # Parity plots, error maps, residual plots
│   ├── uncertainty/               # Conformal prediction & quantile loss helpers
│   └── utils/                     # Reproducibility seeds and I/O helpers
│
├── baselines/                     # Standard of truth baselines
│   ├── block_copy/                # Baseline 1: Identity block copy
│   └── spatial_baseline/          # Baseline 2: Physics-based lapse rate
│
├── random_forest/                 # Isolated Random Forest workspace
├── xgboost/                       # Isolated XGBoost workspace
├── lightgbm/                      # Isolated LightGBM workspace
├── convlstm/                      # Isolated ConvLSTM spatio-temporal workspace
├── cnn_unet/                      # Isolated CNN / U-Net spatial super-res workspace
│
├── model_comparison/              # Multi-model benchmarking engine & results table
└── model_registry/                # Catalog of validated and candidate models
```

---

## 2. Common Model Interface Contract

Every model, regardless of whether it is an scikit-learn regressor, an XGBoost booster, or a PyTorch ConvLSTM module, must implement a Python wrapper class adhering to this conceptual interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd
import numpy as np

class BaseDownscalingModel(ABC):
    """Abstract Base Class for all Panchayat downscaling models."""

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: np.ndarray, config: Dict[str, Any]) -> None:
        """Trains the model on standardized features."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Generates predictions with uncertainty intervals.
        Returns a dictionary containing:
          - 'prediction_p50': np.ndarray (Median prediction)
          - 'prediction_lower': np.ndarray (10th percentile / lower bound)
          - 'prediction_upper': np.ndarray (90th percentile / upper bound)
        """
        pass

    @abstractmethod
    def evaluate(self, X_val: pd.DataFrame, y_val: np.ndarray) -> Dict[str, float]:
        """Evaluates model against official metrics (MAE, RMSE, CSI, etc.)."""
        pass

    @abstractmethod
    def save_model(self, output_dir: str, model_version: str) -> str:
        """Serializes model weights and configuration to disk."""
        pass

    @abstractmethod
    def load_model(self, artifact_path: str) -> None:
        """Loads serialized model weights for inference."""
        pass
```

---

## 3. Standardized Input & Output

### Input Format
Every model receives a tabular DataFrame (or equivalent spatial grid sequence for deep models) with columns defined in the [Common Data Contract](file:///Users/siddhisharma/Desktop/PanchayatCast/docs/architecture/data-contract.md):
- `panchayat_id`
- `target_date`
- `forecast_issue_time`
- `lead_time_hours`
- `block_forecast_rainfall` / `block_forecast_tmax`
- `panchayat_elevation_mean` & `elevation_diff_from_block`
- `panchayat_slope_mean` & `panchayat_aspect_sin` / `aspect_cos`
- `lulc_agriculture_pct` & `lulc_forest_pct`
- `rain_lag_1d`, `rain_lag_3d`, `rain_lag_7d`
- `era5_cape`, `era5_total_column_water`

### Output Format
Every model prediction must output the standard dictionary format:
```json
{
  "panchayat_id": "GP-270101",
  "variable": "rainfall",
  "target_date": "2026-07-16",
  "prediction_p50": 19.4,
  "prediction_lower": 12.1,
  "prediction_upper": 28.7,
  "model_name": "xgboost",
  "model_version": "v1.0.0",
  "run_id": "EXP-XGB-260926-01"
}
```

---

## 4. Model Governance & Evidence-Based Selection

- No model is considered "best" by default.
- Deep learning architectures (ConvLSTM, CNN/U-Net) are treated as **challengers**.
- All models must be evaluated on the same held-out test panchayats and test seasons using `ml/model_comparison/`.
- Only models that demonstrably beat both baselines on held-out stations will be promoted to `candidate` status.
