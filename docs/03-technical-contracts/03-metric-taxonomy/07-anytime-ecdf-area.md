# ANYTIME-ECDF_AREA

> Index: [01-metric-taxonomy.md](01-metric-taxonomy.md)

**Display name:** Area Under the ECDF Curve

**Definition:** The normalized area under the Empirical Cumulative Distribution Function (ECDF) of best objective values over the evaluation sequence, integrated across the Budget. Captures the full Anytime Performance profile in a single scalar — how quickly and how reliably the algorithm improves over time.

*Formally:* for a single Run, define the anytime best value $b(k) = \min_{i \leq k} f(x_i)$ at evaluation $k$. The ECDF at evaluation $k$ is $F_k(v) = P(b(k) \leq v)$ across Runs. The area under the ECDF integrated over $k \in [1, B]$ and normalized to $[0, 1]$ gives ANYTIME-ECDF_AREA.

**Unit and scale:** Normalized to $[0, 1]$ (empirical bounds; see ADR-007). Unitless.

**Interpretation:** Higher is better. An algorithm with high ANYTIME-ECDF_AREA reaches good solutions early and consistently across many budget levels.

**Required inputs:** Full sequence of Performance Records (`evaluation_number` and `objective_value`) for all Runs. This is the primary reason Performance Records must be stored at every evaluation, not just at the endpoint.

**Statistical treatment:** Distribution depends on normalization; non-parametric tests generally appropriate. See `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §5 (Anytime Analysis).

**When to use:** As a primary metric for any study where optimization dynamics matter — i.e., almost always. This is the most information-dense single metric available because it captures quality, speed, and reliability in one number.

**Limitations:** Requires full Performance Record data. ECDF_AREA values are normalized to empirical bounds from the Study in which they were computed and are **not directly comparable to values from other Studies** (ADR-007). A cell with fewer than 2 Runs has undefined bounds; the Analyzer must raise an error.

---

## Exact Computation Procedure

This procedure is normative. Any two Analyzer implementations following these steps must
produce bit-identical results from the same PerformanceRecords.

Scope: one **Problem–Algorithm cell** (one Problem Instance × one Algorithm Instance). Run
the procedure independently for each cell; aggregate across problems as specified in §7.

### §1 — Reconstruct best-so-far curves

For each Run $r \in \{1, \ldots, n\}$, reconstruct the best-so-far value $b_r(k)$ at every
evaluation $k \in \{1, \ldots, B\}$ using **LOCF (ADR-003)**:

$$b_r(k) = \text{objective\_value of the most recent PerformanceRecord in Run } r
\text{ with evaluation\_number} \leq k$$

Because ADR-002 mandates a PerformanceRecord at evaluation 1 for every Run, no pre-first-record
gap exists and LOCF is defined for all $k \geq 1$.

Filter out any Run whose PerformanceRecords contain `NaN` or `inf` values before proceeding.

### §2 — Compute empirical normalization bounds (ADR-007)

$$y_{\max} = \max_{r} \, b_r(1) \qquad \text{(worst initial value across all Runs)}$$

$$y_{\min} = \min_{r} \, b_r(B) \qquad \text{(best final value across all Runs)}$$

**Precondition:** $y_{\max} > y_{\min}$. If $y_{\max} = y_{\min}$, all Runs started and ended
at the same value; the metric is undefined for this cell. The Analyzer must raise a
`MetricUndefinedError` rather than return 0 or 1.

### §3 — Build the common evaluation grid

Let $K = \{k_1, k_2, \ldots, k_m\}$ be the **union** of all `evaluation_number` values that
appear in any PerformanceRecord in the cell, sorted in ascending order, with $k_1 = 1$ and
$k_m = B$ (both are guaranteed by ADR-002).

### §4 — Compute per-evaluation mean best-so-far

For each grid point $k_i \in K$:

$$\bar{b}(k_i) = \frac{1}{n} \sum_{r=1}^{n} b_r(k_i)$$

where $b_r(k_i)$ is the LOCF-reconstructed value from §1.

### §5 — Compute the normalized area (left Riemann sum)

The ECDF at evaluation $k$ integrated over quality values equals $y_{\max} - \bar{b}(k)$
(standard CDF identity: $\int_{-\infty}^{y_{\max}} F_k(v)\,dv = y_{\max} - \mathbb{E}[b(k)]$
for bounded support). The normalized area is therefore:

$$\text{ECDF\_AREA} = \frac{1}{B \cdot (y_{\max} - y_{\min})} \sum_{i=1}^{m-1} (k_{i+1} - k_i) \cdot \bigl(y_{\max} - \bar{b}(k_i)\bigr)$$

This is a **left Riemann sum** over the step function defined by the LOCF grid. Because the
underlying curves are piecewise-constant (LOCF), this sum is exact — not an approximation.

The result lies in $[0, 1]$:
- $= 1$ if every Run achieves $y_{\min}$ from evaluation 1
- $= 0$ if every Run never improves from $y_{\max}$ throughout the entire Budget

### §6 — Per-Run ECDF_AREA (for distribution statistics)

To populate `AggregateValue.statistics`, compute a per-Run scalar using the same formula but
with $b_r(k_i)$ in place of $\bar{b}(k_i)$, holding bounds fixed at the cell-level $y_{\min}$
and $y_{\max}$ from §2:

$$\text{ECDF\_AREA}_r = \frac{1}{B \cdot (y_{\max} - y_{\min})} \sum_{i=1}^{m-1} (k_{i+1} - k_i) \cdot \bigl(y_{\max} - b_r(k_i)\bigr)$$

Collect $\{\text{ECDF\_AREA}_r\}_{r=1}^{n}$ and compute `mean`, `std`, `median`, `q25`, `q75`.

### §7 — Cross-problem aggregation

When a Study contains $P$ Problem Instances, compute ECDF_AREA independently for each
Problem–Algorithm cell per §1–§6. The **study-level ECDF_AREA** for an Algorithm Instance is
the **arithmetic mean** of its per-cell values:

$$\text{ECDF\_AREA}_{\text{study}} = \frac{1}{P} \sum_{p=1}^{P} \text{ECDF\_AREA}_{p}$$

Each problem contributes equally regardless of its objective scale, because per-cell
normalization (§2) already mapped each problem to $[0, 1]$ independently.

---

## Reference Test Case

The following case must be reproduced exactly by any compliant implementation.

**Inputs:** 1 problem, 2 algorithms, 2 Runs each, Budget $B = 4$.

PerformanceRecords for **Algorithm A** (minimization):

| Run | evaluation_number | objective_value |
|-----|-------------------|----------------|
| 1   | 1                 | 1.0            |
| 1   | 2                 | 0.8            |
| 1   | 4                 | 0.6            |
| 2   | 1                 | 1.0            |
| 2   | 3                 | 0.7            |
| 2   | 4                 | 0.7            |

LOCF reconstruction at $K = \{1, 2, 3, 4\}$:

| $k$ | $b_1(k)$ | $b_2(k)$ | $\bar{b}(k)$ |
|-----|----------|----------|--------------|
| 1   | 1.0      | 1.0      | 1.0          |
| 2   | 0.8      | 1.0      | 0.9          |
| 3   | 0.8      | 0.7      | 0.75         |
| 4   | 0.6      | 0.7      | 0.65         |

Bounds: $y_{\max} = 1.0$, $y_{\min} = 0.6$, so $(y_{\max} - y_{\min}) = 0.4$.

Left Riemann sum (interval widths are all 1):

$$\text{ECDF\_AREA} = \frac{1}{4 \times 0.4} \Bigl[(1.0 - 1.0) + (1.0 - 0.9) + (1.0 - 0.75)\Bigr]$$

$$= \frac{1}{1.6} \times [0.0 + 0.1 + 0.25] = \frac{0.35}{1.6} = 0.21875$$

**Expected output: `ECDF_AREA = 0.21875`**

Three intervals contribute to the sum: $[1,2]$, $[2,3]$, $[3,4]$. Each has width 1. The
sum uses the **left** endpoint value of $\bar{b}$ for each interval. Row $k=4$ ($\bar{b}=0.65$)
appears in the LOCF reconstruction table but does not contribute to the sum because it is the
**right** endpoint of the last interval — correctly excluded by the $i=1$ to $m-1$ range in the
formula.

---

**Statistics keys in `AggregateValue.statistics`:**

| Key | Description |
|---|---|
| `mean` | Mean ECDF area across Runs |
| `std` | Standard deviation across Runs |
| `median` | Median across Runs |
| `q25` | 25th percentile |
| `q75` | 75th percentile |

**Related metrics:**
- *Complements:* All other metrics — ANYTIME-ECDF_AREA is a summary; other metrics provide interpretable components
- *Recommended as default primary metric* for most research questions

**Normative references:**
- `ADR-003-anytime-curve-interpolation.md` — LOCF interpolation (§1 of computation procedure)
- `ADR-007-ecdf-area-normalization.md` — empirical min/max bounds (§2 of computation procedure)
