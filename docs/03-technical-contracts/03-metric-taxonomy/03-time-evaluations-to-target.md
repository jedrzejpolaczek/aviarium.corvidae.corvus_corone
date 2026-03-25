# TIME-EVALUATIONS_TO_TARGET

> Index: [01-metric-taxonomy.md](01-metric-taxonomy.md)

**Display name:** Evaluations to Reach Target Value

**Definition:** The number of objective function evaluations required for a Run to first achieve an objective value at or better than a pre-specified target $\tau$. If the target is never reached within the Budget, the value is recorded as $B + 1$ (one beyond budget) to enable aggregate statistics.

*Formally:* let $f^* = \tau$ be the target. Then:
$$\text{TIME-EVALUATIONS\_TO\_TARGET}(\tau) = \min\{k : f(x_k) \leq \tau\} \quad \text{(minimization)}$$
If $\min_k f(x_k) > \tau$, the value is $B + 1$.

**Unit and scale:** Number of evaluations (integer). Budget-dependent: only comparable across Runs and studies using the same total Budget.

**Interpretation:** Lower is better. Captures the efficiency of the algorithm — how quickly it finds a solution of acceptable quality.

**Required inputs:** Full sequence of Performance Records with `objective_value` and `evaluation_number` fields. Requires a pre-specified target $\tau$, which must be defined in the Study plan before data collection.

**Statistical treatment:** Distribution is often right-skewed (many Runs reach target early; some never do). The censored values ($B+1$) require survival analysis methods or non-parametric tests. See `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §3.

**When to use:** When the research question is "which algorithm is most efficient?" or "which algorithm finds acceptable solutions fastest?" The target $\tau$ must be ecologically valid — chosen based on domain knowledge before data collection (Benchmarking Protocol Step 5), not post-hoc. This metric is **not** in the Standard Reporting Set (ADR-008); it is opt-in. When no ecologically valid τ is available, use `ANYTIME-ECDF_AREA` instead.

**Limitations:** Highly sensitive to the choice of target $\tau$. A single target may not capture algorithm behavior across the full quality range. Use alongside `ANYTIME-ECDF_AREA` for a target-free view.

**Statistics keys in `AggregateValue.statistics`:**

| Key | Description |
|---|---|
| `median` | Median evaluations to target across Runs (preferred over mean due to right-skewed / censored distribution) |
| `q25` | 25th percentile |
| `q75` | 75th percentile |
| `min` | Minimum evaluations to target observed |
| `max` | Maximum evaluations to target observed (may equal $B+1$ for all-censored Runs) |
| `mean` | Arithmetic mean; report alongside median to reveal skew |
| `n_censored` | Number of Runs where target was never reached (value recorded as $B+1$) |

**Related metrics:**
- *Complements:* `RELIABILITY-SUCCESS_RATE` (whether target is reached), `ANYTIME-ECDF_AREA`
- *Do not use alone:* Always report `RELIABILITY-SUCCESS_RATE` alongside this metric.

**Implementation reference:** Pending IMPL-011 — `corvus_corone/analysis/metrics.py` → `compute_time_evaluations_to_target(performance_records, target)`
