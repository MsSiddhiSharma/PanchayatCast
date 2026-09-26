# ConvLSTM Spatio-Temporal Model — PanchayatCast

## 1. Why ConvLSTM is Being Evaluated (Challenger Model)
ConvLSTM (Convolutional Long Short-Term Memory) replaces standard matrix multiplications in recurrent cells with 2D convolutional operators:
- **Spatial Structure Preservation:** Preserves 2D spatial adjacency and atmospheric gradients across adjacent grid cells.
- **Temporal Memory:** Captures multi-day weather evolution (e.g. monsoon depression propagation over 3–5 antecedent days).

> [!CAUTION]
> **Strict Scientific Governance:** ConvLSTM is a **challenger model**, NOT an assumed winner. Deep learning models often suffer from high data requirements, boundary artifacts, and blurry spatial outputs when trained on limited meteorological samples. ConvLSTM will only be considered for production if it empirically beats tree-based models on held-out station test metrics.

---

## 2. Expected Input: Spatio-Temporal Tensor Sequences
ConvLSTM expects a 5D tensor of shape:

$$\mathbf{X} \in \mathbb{R}^{B \times T \times C \times H \times W}$$

Where:
- $B$: Batch size
- $T$: Sequence length (e.g., $T=3$ or $T=5$ antecedent daily weather grids)
- $C$: Channels (e.g., coarse forecast rainfall, elevation DEM raster, ERA5 wind vectors, moisture)
- $H \times W$: Spatial grid dimensions covering the district or block boundary cluster

```text
[ Day T-2 Grid ] ──┐
[ Day T-1 Grid ] ──┼──> [ ConvLSTM Layers ] ──> [ Output Downscaled Grid (Day T) ]
[ Day T   Grid ] ──┘                                      │
                                                          ▼
                                            [ Zonal Mean per Panchayat ]
```

---

## 3. Training & Validation Setup
- **Loss Functions:** Masked MSE, Huber loss, or Continuous Ranked Probability Score (CRPS).
- **Framework:** PyTorch / PyTorch Lightning.
- **Zonal Aggregation:** Downscaled output raster fields are spatially aggregated over official Panchayat boundary polygons to produce tabular Panchayat predictions ($P_{50}$, bounds).
- **Hardware Requirement:** GPU required for training.

---

## 4. Experiment Naming & Artifacts
- Experiments logged in `experiments/EXP-CONVLSTM-<YYMMDD>-<SEQ>/`.
- PyTorch checkpoint weights stored in `models/convlstm_<variable>_<version>.pt`.
- Final metrics aggregated in `results/`.
