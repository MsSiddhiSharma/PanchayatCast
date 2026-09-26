# Baseline 1: Block-Copy Baseline

## Concept
The **Block-Copy baseline** assigns the parent block forecast value directly and identically to every constituent Gram Panchayat within that block.

$$\hat{Y}_{\text{panchayat}, i} = F_{\text{block}}$$

## Scientific Purpose
- Establishes the operational benchmark of existing weather advisory services.
- Serves as the negative control (Null Hypothesis).
- If any proposed ML model exhibits higher MAE or lower CSI than Block-Copy on held-out test data, that model causes degradation and will not be deployed.
