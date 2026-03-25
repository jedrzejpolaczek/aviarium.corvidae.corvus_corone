# QUALITY-BEST_VALUE_AT_BUDGET

> Index: [01-metric-taxonomy.md](01-metric-taxonomy.md)

**Display name:** Best Objective Value at Full Budget

**Definition:** The best (minimum for minimization, maximum for maximization) objective function value observed across all evaluations of a single Run, measured at the point when the full Budget is consumed.

*Formally:* let $f(x_1), f(x_2), \ldots, f(x_B)$ be the sequence of objective values observed during a Run with budget $B$. Then:
$$\text{QUALITY-BEST\_VALUE\_AT\_BUDGET} = \min_{i \in \{1,\ldots,B\}} f(x_i)$$
(for minimization; replace $\min$ with $\max$ for maximization problems).

**Unit and scale:** Same unit as the objective function. Not normalized unless the Problem Instance specifies a normalization; when comparing across problems, normalization must be stated explicitly.

**Interpretation:** Lower is better for minimization problems. Reflects the algorithm's ability to find good solutions given the full computational Budget.

**Required inputs:** All Performance Records for the Run; specifically the `objective_value` field of each record. Minimum: 1 completed Run.

**Statistical treatment:** Distribution is typically non-normal (bounded below by the true optimum if known, potentially multi-modal). Non-parametric statistical tests are generally appropriate. See `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §3.

**When to use:** When the primary research question is "which algorithm finds the best solution given the same total budget?" Use when Budget-constrained performance is the central concern.

**Limitations:** Measures only the endpoint — ignores how quickly good solutions are found. An algorithm that finds a near-optimal solution early and an algorithm that barely reaches it at the last evaluation are indistinguishable by this metric alone. Always pair with ANYTIME metrics or TIME-EVALUATIONS_TO_TARGET.

**Statistics keys in `AggregateValue.statistics`:**

| Key | Description |
|---|---|
| `mean` | Arithmetic mean across Runs |
| `std` | Standard deviation across Runs |
| `median` | Median across Runs |
| `q25` | 25th percentile |
| `q75` | 75th percentile |
| `min` | Minimum observed value |
| `max` | Maximum observed value |

**Related metrics:**
- *Complements:* `ANYTIME-ECDF_AREA` (captures dynamics), `TIME-EVALUATIONS_TO_TARGET` (efficiency)
- *Do not use alone:* Always report alongside at least one ANYTIME or TIME metric.

**Implementation reference:** Pending IMPL-011 — `corvus_corone/analysis/metrics.py` → `compute_quality_best_value_at_budget(performance_records)`
