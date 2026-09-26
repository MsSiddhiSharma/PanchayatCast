# Model Registry & Lifecycle Governance — PanchayatCast

## 1. Purpose of the Model Registry

The Model Registry serves as the **single source of truth** connecting machine learning model development to the backend serving layer.
The FastAPI backend reads this registry to dynamically load models without any hardcoded model dependencies.

---

## 2. Model Lifecycle States

Every model version progresses through four formal lifecycle states:

```
[ experimental ]
       │
       ▼ (Successfully completes cross-validation benchmark)
  [ validated ]
       │
       ▼ (Beats both baselines and peer models on held-out stations)
  [ candidate ]
       │
       ▼ (Approved by team consensus for operational deployment)
 [ production ]
```

| Lifecycle State | Criteria | Backend Serving Behavior |
| :--- | :--- | :--- |
| **`experimental`** | Initial training or exploratory tuning. Untested on held-out data. | Accessible only in internal testing mode via specific request flag. |
| **`validated`** | Evaluated on full test split with logged metrics. | Available in model comparison benchmark UI. |
| **`candidate`** | Demonstrates statistically significant improvement over Block-Copy and Spatial baselines on held-out stations. | Available for A/B testing and advisory pilot runs. |
| **`production`** | Formally selected as the primary operational model for a specific variable and lead time. | Default model queried by end-user frontend. |

> [!CAUTION]
> **Strict Governance:** No model is automatically marked `candidate` or `production`. Promotion requires logged benchmark metrics in `ml/model_comparison/results/`.
