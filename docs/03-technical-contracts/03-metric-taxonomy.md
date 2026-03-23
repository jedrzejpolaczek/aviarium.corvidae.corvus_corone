# Performance Metric Taxonomy

<!--
STORY ROLE: The "dictionary of measurement". Every metric used anywhere in the system
is defined here and only here. Prevents the silent disagreements that undermine science:
two studies using "success rate" that mean different things.

NARRATIVE POSITION:
  MANIFESTO Principle 12 (Multidimensionality) → Metric Taxonomy → (what we can measure)
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md : which metrics get which statistical treatment
  → docs/03-technical-contracts/01-data-format.md §2.7 : metric names in Result Aggregates MUST match names here
  → docs/03-technical-contracts/interface-contracts.md §4 : Analyzer interface validates metric names against here

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md Principle 12 : "multiple aspects of performance" — this document is the inventory
  ← docs/02-design/01-software-requirement-specification/SRS.md §4.4 : Measurement & Analysis Engine requirements
  → docs/03-technical-contracts/01-data-format.md §2.7 : ResultAggregate.metrics keys must be valid metric IDs from here
  → docs/03-technical-contracts/interface-contracts.md §4 : Analyzer.compute_metrics() validates against this taxonomy
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md : statistical treatment varies by metric type
  → docs/GLOSSARY.md           : terms used here (Budget, Run, Anytime Performance, etc.) are defined there
  → Docstrings                 : analysis code references metric IDs from this document

METRIC ID FORMAT: [CATEGORY]-[NAME] in UPPER_SNAKE_CASE
  Example: QUALITY-BEST_VALUE_AT_BUDGET, TIME-EVALUATIONS_TO_TARGET
  Metric IDs are the stable identifiers. Metric display names may change; IDs must not.
  Once an ID is assigned and used in any published study, it is permanent.
-->

---

## 1. Taxonomy Overview

The five metric categories below are derived directly from MANIFESTO Principle 12:

> *"We measure multiple aspects of performance: **solution quality at fixed budget**, **time to reach target**, **success probability**, **noise robustness**, **result stability**."*

MANIFESTO Principle 14 adds a sixth dimension:

> *"We report not only final values, but **full performance curves over time** (anytime behavior)."*

| Category | Metric ID Prefix | What it captures | Directly from Principle |
|---|---|---|---|
| QUALITY | `QUALITY-` | Best solution value achieved at a fixed Budget | Principle 12: "solution quality at fixed budget" |
| TIME | `TIME-` | Evaluations or time required to reach a target objective value | Principle 12: "time to reach target" |
| RELIABILITY | `RELIABILITY-` | Probability of success and consistency across Runs | Principle 12: "success probability" |
| ROBUSTNESS | `ROBUSTNESS-` | Sensitivity to noise and parameter variations | Principle 12: "noise robustness", "result stability" |
| ANYTIME | `ANYTIME-` | Full performance curve shape and dynamics | Principle 14: "full performance curves over time" |

**Guidance on scope:** Each category should contain 2–5 defined metrics. More metrics dilute analytical focus; fewer miss important performance aspects. The current set reflects the minimum required by the MANIFESTO.

> **`TODO: REF-TASK-0014`** — Review and extend metric definitions once the first real studies
> are conducted. Add domain-specific metrics (e.g., for categorical/mixed search spaces) as they
> are identified. Owner: methodology lead. Acceptance: each new metric follows the definition
> template below and is added to §4 Metric Selection Guide.

---

## 2. Metric Definitions

### QUALITY-BEST_VALUE_AT_BUDGET

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

> **`TODO: REF-TASK-0015`** — Add implementation reference once the analysis module is built.

---

### TIME-EVALUATIONS_TO_TARGET

**Display name:** Evaluations to Reach Target Value

**Definition:** The number of objective function evaluations required for a Run to first achieve an objective value at or better than a pre-specified target $\tau$. If the target is never reached within the Budget, the value is recorded as $B + 1$ (one beyond budget) to enable aggregate statistics.

*Formally:* let $f^* = \tau$ be the target. Then:
$$\text{TIME-EVALUATIONS\_TO\_TARGET}(\tau) = \min\{k : f(x_k) \leq \tau\} \quad \text{(minimization)}$$
If $\min_k f(x_k) > \tau$, the value is $B + 1$.

**Unit and scale:** Number of evaluations (integer). Budget-dependent: only comparable across Runs and studies using the same total Budget.

**Interpretation:** Lower is better. Captures the efficiency of the algorithm — how quickly it finds a solution of acceptable quality.

**Required inputs:** Full sequence of Performance Records with `objective_value` and `evaluation_number` fields. Requires a pre-specified target $\tau$, which must be defined in the Study plan before data collection.

**Statistical treatment:** Distribution is often right-skewed (many Runs reach target early; some never do). The censored values ($B+1$) require survival analysis methods or non-parametric tests. See `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §3.

**When to use:** When the research question is "which algorithm is most efficient?" or "which algorithm finds acceptable solutions fastest?" The target $\tau$ must be ecologically valid — chosen based on domain knowledge, not post-hoc.

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

---

### RELIABILITY-SUCCESS_RATE

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

---

### ROBUSTNESS-NOISE_SENSITIVITY

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

---

### ROBUSTNESS-RESULT_STABILITY

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

---

### ANYTIME-ECDF_AREA

**Display name:** Area Under the ECDF Curve

**Definition:** The normalized area under the Empirical Cumulative Distribution Function (ECDF) of best objective values over the evaluation sequence, integrated across the Budget. Captures the full Anytime Performance profile in a single scalar — how quickly and how reliably the algorithm improves over time.

*Formally:* for a single Run, define the anytime best value $b(k) = \min_{i \leq k} f(x_i)$ at evaluation $k$. The ECDF at evaluation $k$ is $F_k(v) = P(b(k) \leq v)$ across Runs. The area under the ECDF integrated over $k \in [1, B]$ and normalized to $[0, 1]$ gives ANYTIME-ECDF_AREA.

> **`TODO: REF-TASK-0016`** — Formalize the exact ECDF area computation procedure, including:
> normalization bounds (use known optimum or empirical bounds?), handling of censored data,
> and aggregation across problems. Owner: methodology lead. Acceptance: two independent
> implementations produce identical results on the same dataset.

**Unit and scale:** Normalized to $[0, 1]$ when bounds are available. Unitless.

**Interpretation:** Higher is better. An algorithm with high ANYTIME-ECDF_AREA reaches good solutions early and consistently across many budget levels.

**Required inputs:** Full sequence of Performance Records (`evaluation_number` and `objective_value`) for all Runs. This is the primary reason Performance Records must be stored at every evaluation, not just at the endpoint.

**Statistical treatment:** Distribution depends on normalization; non-parametric tests generally appropriate. See `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §5 (Anytime Analysis).

**When to use:** As a primary metric for any study where optimization dynamics matter — i.e., almost always. This is the most information-dense single metric available because it captures quality, speed, and reliability in one number.

**Limitations:** Requires full Performance Record data. Sensitive to the choice of normalization bounds — results are only comparable across studies that use identical normalization.

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

---

## 3. Standard Reporting Set

Every benchmarking study produced or exported by this system **MUST** include at minimum the following metrics. A researcher may report additional metrics but cannot report fewer. This enforces MANIFESTO Principle 29 (Objectivity over promotion) by preventing metric cherry-picking.

| Metric ID | Why Mandatory |
|---|---|
| `QUALITY-BEST_VALUE_AT_BUDGET` | Every study has a budget; final quality is the most basic outcome measure |
| `RELIABILITY-SUCCESS_RATE` | Reliability matters independently of peak quality; omitting it can hide fragile algorithms |
| `ROBUSTNESS-RESULT_STABILITY` | Spread across Runs is required by MANIFESTO Principle 15 ("not only averages, but spread") |
| `ANYTIME-ECDF_AREA` | Full performance curves required by MANIFESTO Principle 14; this is its scalar summary |

**Enforcement:** The Analyzer interface (`docs/03-technical-contracts/interface-contracts.md` §4) must validate that all four metrics are computed before producing any study report.

**Connection to protocol:** `docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md` Step 5 references this set as the non-negotiable minimum when specifying measurements.

> **`TODO: REF-TASK-0017`** — Consider whether TIME-EVALUATIONS_TO_TARGET should be added to the
> Standard Reporting Set. It requires a pre-specified target $\tau$, which adds planning burden.
> Owner: methodology lead. Acceptance: decision documented in an ADR with MANIFESTO principle rationale.

---

## 4. Metric Selection Guide

Use this guide when specifying measurements in Step 5 of the Benchmarking Protocol (`docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md`). Metric selection must happen **before** data collection (MANIFESTO Principle 16) to prevent post-hoc cherry-picking.

### Research question: "Which algorithm finds the best solutions given a fixed budget?"
- **Primary:** `QUALITY-BEST_VALUE_AT_BUDGET`
- **Required alongside:** `ROBUSTNESS-RESULT_STABILITY` (stability of that quality), `ANYTIME-ECDF_AREA` (dynamics)
- **Discouraged as sole metric:** `QUALITY-BEST_VALUE_AT_BUDGET` alone, without spread measures — violates Principle 15

### Research question: "Which algorithm reaches acceptable solutions fastest?"
- **Primary:** `TIME-EVALUATIONS_TO_TARGET`, `ANYTIME-ECDF_AREA`
- **Required alongside:** `RELIABILITY-SUCCESS_RATE` (what fraction of Runs reach the target at all)
- **Note:** Target $\tau$ must be pre-specified and ecologically justified

### Research question: "Which algorithm is most reliable and consistent?"
- **Primary:** `RELIABILITY-SUCCESS_RATE`, `ROBUSTNESS-RESULT_STABILITY`
- **Required alongside:** `QUALITY-BEST_VALUE_AT_BUDGET` (context for what level of quality is reliable)

### Research question: "How do algorithms perform under noisy evaluations?"
- **Primary:** `ROBUSTNESS-NOISE_SENSITIVITY`, `RELIABILITY-SUCCESS_RATE`
- **Required:** Problem Instances must include matched noisy/noiseless variants — must be designed into the Study
- **Required alongside:** `QUALITY-BEST_VALUE_AT_BUDGET` on noiseless instances as baseline

### Research question: "How do algorithms compare across different budget levels?"
- **Primary:** `ANYTIME-ECDF_AREA`, full ECDF curves at multiple budget checkpoints
- **Requires:** Full Performance Record data for all Runs
- **Note:** This is the only question type where a single metric (`ANYTIME-ECDF_AREA`) is nearly self-sufficient

> **`TODO: REF-TASK-0018`** — Add research question archetypes as they emerge from actual studies.
> Each archetype should link to a tutorial in `docs/06_tutorials/` demonstrating it end-to-end.
> Owner: methodology lead. Acceptance: each new archetype has a corresponding tutorial.

---

## 5. Deprecated Metrics

*No deprecated metrics at this time. This section will be populated as the taxonomy evolves.*

> Deprecated metrics are never removed from this document — existing studies may reference them.
> Deprecated metrics must not appear in the Standard Reporting Set (§3).
> Versioning policy: `docs/05_community/versioning-governance.md` §3.
