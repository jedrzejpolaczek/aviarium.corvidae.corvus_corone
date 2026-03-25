# ROBUSTNESS-RESULT_STABILITY

> Index: [01-metric-taxonomy.md](01-metric-taxonomy.md)

**Display name:** Result Stability Across Runs

**Definition:** The interquartile range (IQR) of `QUALITY-BEST_VALUE_AT_BUDGET` across all Runs of the same (Algorithm Instance, Problem Instance) combination. Lower IQR indicates more stable, predictable results.

*Formally:* let $q_1, \ldots, q_N$ be the `QUALITY-BEST_VALUE_AT_BUDGET` values across $N$ Runs. Then:
$$\text{ROBUSTNESS-RESULT\_STABILITY} = Q_{75}(q_1,\ldots,q_N) - Q_{25}(q_1,\ldots,q_N)$$

**Unit and scale:** Same unit as the objective function. Scale-dependent; for cross-problem comparison, normalization may be needed.

**Interpretation:** Lower is better. An algorithm with low stability is unpredictable — users cannot rely on it to consistently deliver similar results.

**Required inputs:** Minimum 10 Runs recommended for stable IQR estimates (MANIFESTO Principle 16 — specify repetitions before execution).

**Statistical treatment:** IQR is a non-parametric dispersion measure; Levene's or Brown–Forsythe test for comparing dispersion across algorithms. See `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §3.

**When to use:** When the research question concerns result stability (MANIFESTO Principle 12: "result stability"). Especially important for practitioners who need reliable algorithm behavior.

**Statistics keys in `AggregateValue.statistics`:**

| Key | Description |
|---|---|
| `iqr` | Interquartile range ($Q_{75} - Q_{25}$) — the primary value for this metric |
| `q25` | 25th percentile of `QUALITY-BEST_VALUE_AT_BUDGET` across Runs (component of IQR) |
| `q75` | 75th percentile of `QUALITY-BEST_VALUE_AT_BUDGET` across Runs (component of IQR) |

**Related metrics:**
- *Complements:* `QUALITY-BEST_VALUE_AT_BUDGET` (central tendency), `RELIABILITY-SUCCESS_RATE`
- *Do not use alone:* Always report alongside the central tendency metric.

**Implementation reference:** Pending IMPL-011 — `corvus_corone/analysis/metrics.py` → `compute_robustness_result_stability(performance_records)`
