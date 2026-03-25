# ROBUSTNESS-NOISE_SENSITIVITY

> Index: [01-metric-taxonomy.md](01-metric-taxonomy.md)

**Display name:** Performance Degradation Under Noise

**Definition:** The ratio of `QUALITY-BEST_VALUE_AT_BUDGET` on a noisy version of a Problem Instance to `QUALITY-BEST_VALUE_AT_BUDGET` on the noiseless version of the same instance. Values close to 1.0 indicate the algorithm is insensitive to noise; values far from 1.0 indicate sensitivity.

*Formally:* let $q_0$ be the quality achieved on the noiseless instance and $q_\sigma$ on the noisy instance with noise level $\sigma$. Then:
$$\text{ROBUSTNESS-NOISE\_SENSITIVITY}(\sigma) = \frac{q_\sigma}{q_0}$$

**Unit and scale:** Dimensionless ratio. Defined only when both a noiseless and noisy version of the same Problem Instance exist.

**Interpretation:** Closer to 1.0 is better. Quantifies how much noise degrades the algorithm's solution quality.

**Required inputs:** Runs on matched pairs of Problem Instances (noiseless and noisy variants at one or more noise levels $\sigma$). Requires Problem Instance design to include noise variants — must be planned in the Study.

**Statistical treatment:** Distribution of ratios may be skewed; non-parametric approaches recommended.

**When to use:** When the research question concerns noise robustness (MANIFESTO Principle 12: "noise robustness"). Requires Problem Instances to be designed as noise-paired sets.

**Limitations:** Requires explicit noise variants in the benchmark set. Cannot be computed post-hoc if noise levels were not varied during the Study. Also see `TODO: REF-TASK-0014` for additional robustness metrics (parameter sensitivity).

**Statistics keys in `AggregateValue.statistics`:**

| Key | Description |
|---|---|
| `mean` | Mean noise sensitivity ratio across Run pairs |
| `std` | Standard deviation across Run pairs |
| `median` | Median ratio (preferred for skewed distributions) |

**Related metrics:**
- *Complements:* `RELIABILITY-SUCCESS_RATE` (captures run-to-run variance from noise)
- *Do not use alone:* Always report the noise level $\sigma$ used.

**Implementation reference:** Pending IMPL-011 — `corvus_corone/analysis/metrics.py` → `compute_robustness_noise_sensitivity(noiseless_records, noisy_records)`
