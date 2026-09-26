# Jupyter Notebooks — PanchayatCast (SIH26074)

This directory is designated for exploratory data analysis (EDA), prototype visualization, and feature investigation.

---

## Directory Hierarchy

- **`notebooks/data_exploration/`**: Examining distributions of station rainfall, analyzing missing observation rates, inspecting DEM elevation histograms, and examining microclimate gradients.
- **`notebooks/feature_analysis/`**: Evaluating feature-target correlations, mutual information scores, multicollinearity among terrain indices, and spatial autocorrelation (Moran's I).
- **`notebooks/visualization/`**: Prototyping static and interactive choropleth maps, difference heatmaps, and advisory card layouts.

---

## Collaboration Rules for Notebooks

1. **Keep Notebooks Clean:** Clear heavy output cells (especially interactive map widgets) before pushing to GitHub to prevent repository bloat.
2. **Do Not Store Core Logic Only in Notebooks:** Once an exploratory function is validated, refactor it into clean Python modules under `ml/common/` or `backend/app/`.
3. **Use Fixed Random Seeds:** Ensure all visualizations and sample data partitions are reproducible.
