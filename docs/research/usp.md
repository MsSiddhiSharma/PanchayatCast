# Research: Unique Selling Propositions (USPs) — PanchayatCast

## 1. Zero AI Hype / Scientific Baseline Discipline

Most hackathon projects jump directly into complex deep learning (e.g. ConvLSTM, GANs) without demonstrating that the model actually outperforms simpler approaches. 
**PanchayatCast mandates benchmarking against a Block-Copy baseline.** If a complex neural model does not achieve lower error than a simple elevation adjustment or XGBoost on held-out stations, it is rejected.

---

## 2. Transparent Physical Explainability: The "Evidence Card"

Black-box predictions are dangerous in agriculture. PanchayatCast provides an **Evidence Card** for every downscaled prediction explaining *why* the microclimate deviates from the parent block:
- **Elevation differential ($\Delta z$):** e.g., "Panchayat is 340m higher than block centroid $\rightarrow$ -2.2°C temperature adjustment."
- **Slope & Aspect:** e.g., "South-West facing slope enhances orographic rainfall during monsoon."
- **Land Cover:** e.g., "Dense forest canopy reduces diurnal temperature fluctuations by 1.1°C."

---

## 3. Calibrated Predictive Intervals ($P_{10}$, $P_{50}$, $P_{90}$)

Farmers make economic decisions under uncertainty. Point forecasts ("Tomorrow it will rain 12mm") create false confidence. 
PanchayatCast delivers:
- **$P_{10}$ (Dry scenario):** Safe window for harvesting or threshing.
- **$P_{50}$ (Expected median):** Standard planning.
- **$P_{90}$ (Worst-case heavy rain):** Flash flood, waterlogging, or pest-spray wash-off risk.

---

## 4. Source-Linked Farmer Advisories

Rather than generating generic AI text, advisories are **grounded in established agricultural extension rules** (KVK/ICAR bulletins) tied directly to crop phenology and verified weather thresholds.
