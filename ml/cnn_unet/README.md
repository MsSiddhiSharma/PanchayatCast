# CNN / U-Net Super-Resolution Model — PanchayatCast

## 1. Why CNN / U-Net is Being Evaluated (Challenger Model)
U-Net is an encoder-decoder convolutional network with skip connections that preserve high-frequency spatial details:
- **Spatial Super-Resolution:** In downscaling, the low-resolution coarse NWP block forecast is treated as a low-resolution image, while high-resolution terrain rasters (DEM elevation, slope, aspect, water body masks) act as high-frequency conditioning channels.
- **Skip Connections:** Allows the network to retain global atmospheric synoptic context while reconstructing sharp local topographic microclimates.

> [!CAUTION]
> **Strict Scientific Governance:** Like ConvLSTM, CNN / U-Net is a **challenger model**. CNNs can suffer from edge artifacts and over-smoothing in precipitation fields. It must be evaluated using the exact same metrics and independent station observations as tree-based models.

---

## 2. Architecture & Input/Output Grids
- **Input Channels ($C_{in}$):**
  1. Low-resolution Block Forecast grid (interpolated to target grid).
  2. High-resolution DEM elevation (SRTM 30m/90m).
  3. High-resolution Topographic Slope.
  4. LULC Forest / Vegetation canopy fraction.
- **Output Channels ($C_{out}$):**
  - High-resolution downscaled weather field (1 km grid).
- **Zonal Extraction:**
  - Raster output values are spatially averaged over each Gram Panchayat polygon via `rasterio` / `exactextract` to generate final tabular Panchayat predictions.

---

## 3. Key Hyperparameters & Loss
- `encoder_channels`: `[32, 64, 128, 256]`.
- `decoder_channels`: `[128, 64, 32]`.
- `loss`: Mixed MSE + SSIM (Structural Similarity Index) or Quantile Pinball loss.
- `optimizer`: AdamW with Cosine Annealing learning rate schedule.

---

## 4. Experiment Naming & Artifacts
- Experiments logged in `experiments/EXP-UNET-<YYMMDD>-<SEQ>/`.
- Weights saved in `models/unet_<variable>_<version>.pt`.
- Validation scores logged in `results/`.
