# Baseline 2: Spatial Elevation & Climatological Baseline

## Concept
The **Spatial baseline** incorporates physics-based atmospheric adjustments using digital elevation model (DEM) variations and spatial interpolation.

---

## 1. Temperature Lapse Rate Formulation
In the troposphere, temperature decreases with altitude. For maximum temperature ($T_{max}$):

$$\hat{T}_{\text{panchayat}} = T_{\text{block}} - \Gamma \cdot \Delta z$$

Where:
- $\Delta z = z_{\text{panchayat}} - z_{\text{block centroid}}$ (Elevation difference in meters).
- $\Gamma = 0.0065\text{ °C/m}$ (Environmental lapse rate) or seasonally calibrated dry/moist adiabatic lapse rate.

---

## 2. Rainfall Orographic Scaling & IDW
For rainfall downscaling:
- Calculates elevation difference and windward/leeward exposure relative to prevailing monsoon low-level winds.
- Applies inverse distance weighting (IDW) from neighboring block centroids to enforce spatial continuity across administrative boundaries.

---

## Assumptions & Limitations
- Assumes a constant linear lapse rate which can break down during nocturnal valley temperature inversions.
- Does not capture non-linear convective cloud dynamics or localized land cover thermal inertia.
