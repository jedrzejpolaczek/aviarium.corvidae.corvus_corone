# RELIABILITY-SUCCESS_RATE

> Index: [01-metric-taxonomy.md](01-metric-taxonomy.md)

**Display name:** Success Rate at Target

**Definition:** The proportion of Runs (out of all repetitions) in which the algorithm achieves an objective value at or better than a pre-specified target $\tau$ within the given Budget.

*Formally:* let $N$ be the total number of Runs and $S(\tau)$ be the number of Runs that reach target $\tau$. Then:
$$\text{RELIABILITY-SUCCESS\_RATE}(\tau) = \frac{S(\tau)}{N}$$

**Unit and scale:** Proportion in $[0, 1]$. A value of 1.0 means all Runs succeeded; 0.0 means none did.

**Interpretation:** Higher is better. Captures how reliably an algorithm achieves acceptable performance — distinct from how well it performs when it does succeed.

**Required inputs:** `QUALITY-BEST_VALUE_AT_BUDGET` for each Run plus the target $\tau$. Minimum: 10+ Runs recommended for stable proportion estimates.

**Statistical treatment:** Binomial distribution — appropriate tests are binomial tests or Fisher's exact test for comparison. Effect size: Cohen's h or odds ratio. See `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §3.

**When to use:** When reliability matters as much as peak performance — e.g., for practitioners who need an algorithm that consistently reaches an acceptable solution, not just occasionally finds an excellent one.

**Limitations:** Binary threshold creates a cliff effect. An algorithm that reaches 99% of the target on all Runs scores 0.0 while one that reaches 101% on one Run scores 1/N. Pair with `QUALITY-BEST_VALUE_AT_BUDGET` to see the full picture.

**Statistics keys in `AggregateValue.statistics`:**

| Key | Description |
|---|---|
| `success_rate` | Proportion of Runs that reached target $\tau$ (range $[0, 1]$) |
| `ci_low` | Lower bound of the 95% confidence interval for `success_rate` |
| `ci_high` | Upper bound of the 95% confidence interval for `success_rate` |

Note: `n_successful` is already a required top-level field in `AggregateValue` and is not repeated here.

**Related metrics:**
- *Complements:* `QUALITY-BEST_VALUE_AT_BUDGET`, `TIME-EVALUATIONS_TO_TARGET`
- *Do not use alone:* Always report the target $\tau$ value explicitly alongside this metric.
