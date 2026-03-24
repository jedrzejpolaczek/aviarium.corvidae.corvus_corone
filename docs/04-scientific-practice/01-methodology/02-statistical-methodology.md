# Statistical Methodology Guide

<!--
STORY ROLE: The "scientific rigor chapter". Defines HOW results are interpreted.
This document is what separates this system from ad-hoc benchmarking.
Without it, the same data can support contradictory conclusions.

NARRATIVE POSITION:
  MANIFESTO Principles 13, 15 → Statistical Methodology → (how we analyze and report)
  → methodology/benchmarking-protocol.md §Step 6: the protocol invokes this guide there

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md Principles 13, 15 : directly operationalized by this document
  ← docs/02-design/01-software-requirement-specification/SRS.md NFR-STAT-01 : non-functional requirement for statistical validity
  → docs/03-technical-contracts/metric-taxonomy.md    : metric properties (distribution, bounds) guide test selection here
  → docs/03-technical-contracts/interface-contracts.md §4 : Analyzer interface implements this methodology
  → docs/03-technical-contracts/data-format.md §2.7   : Result Aggregate fields store uncertainty information defined here
  → docs/04_scientific_practice/methodology/benchmarking-protocol.md : protocol's analysis step (Step 6) references this guide
  → docs/GLOSSARY.md            : terms like "Effect Size", "Anytime Performance" are defined there

NOTE: This document describes methodology — what to do and why.
Implementation details (which library, which function call) belong in code and docstrings.
-->

---

## 1. The Three-Level Analysis Framework

The three-level framework is mandated by MANIFESTO Principle 13:

> *"We conduct each analysis in three steps: **Exploratory data analysis** (visualization, pattern recognition), **Confirmatory analysis** (statistical tests, formal conclusions), **Practical significance analysis** (effect size, practical utility of differences)."*

**Why all three levels are required — and why each alone is insufficient:**

| Level alone | What it misses |
|---|---|
| Exploratory only | Patterns in data are not conclusions — they need formal testing to distinguish signal from noise |
| Confirmatory only | A statistically significant difference may be negligibly small in practice; p-values depend on sample size |
| Practical only | Effect sizes without significance testing may reflect noise rather than real differences |

**The critical sequencing rule:**

```
Level 1 (Exploratory) → Level 2 (Confirmatory) → Level 3 (Practical)
```

Hypotheses tested in Level 2 **MUST be pre-specified in the Study plan** (`docs/03-technical-contracts/data-format.md` §2.3 `pre_registered_hypotheses`) **before** Level 1 analysis begins. This is non-negotiable.

Post-hoc hypothesis selection — choosing what to test after seeing the data — is a form of p-hacking. It inflates the false positive rate without appearing to do so. MANIFESTO Principle 16 requires that experimental design precedes data collection; this extends to analysis design.

**What each level produces:**

| Level | Name | Input | Output |
|---|---|---|---|
| 1 | Exploratory Data Analysis | Raw Run data and Performance Records | Observations, anomaly flags, and **candidate hypotheses for future studies** |
| 2 | Confirmatory Analysis | Pre-registered hypotheses + Level 1 data | Formal accept/reject decisions with quantified uncertainty (p-values, confidence intervals) |
| 3 | Practical Significance | Level 2 results | Effect sizes and practitioner-readable interpretation of whether differences matter |

> **`REF-TASK-0019`** — Level 1 required visualizations specified. See
> `docs/02-design/02-architecture/03-c4-leve2-containers/03-report-format-spec.md`
> (§Mandatory Visualizations): VIZ-L1-01 box plot, VIZ-L1-02 convergence curves,
> VIZ-L1-03 ECDF (`plt.step(where='post')`), VIZ-L1-04 violin (n > 50). All are
> auto-generated from Run data with no researcher configuration.

> **`REF-TASK-0020`** — Test selection procedure and multiple testing correction documented in §3.

---

## 2. Level 1: Exploratory Data Analysis

*Implements MANIFESTO Principle 13 (three-level analysis). All visualizations are auto-generated
by the Reporting Engine (`docs/02-design/02-architecture/03-c4-leve2-containers/03-report-format-spec.md`
§Mandatory Visualizations) without researcher configuration.*

**Purpose:** Understand the data before drawing any conclusions. Identify patterns,
anomalies, and observations that motivate hypotheses for future studies. The output of
Level 1 is **observations, not conclusions**.

---

### 2.1 Mandatory Visualizations

The following four visualizations are generated for every completed Experiment. They are
defined in the Report Output Format Specification and reproduced here for analysis guidance.

---

#### VIZ-L1-01: Box Plot of Final Quality

**What it shows:** Distribution of `QUALITY-BEST_VALUE_AT_BUDGET` across repetitions, one
box per (algorithm, problem) cell. Shows median, IQR, whiskers (1.5×IQR), and outliers as
individual points.

**When most useful:** Comparing endpoint quality across algorithms when repetitions are
moderate (5–50). Immediately reveals spread and any extreme outlier Runs.

**How to interpret:**
- Box width = IQR; narrower box → more consistent results
- Overlapping boxes → no clearly separable quality difference at this budget
- An outlier point far from the box → investigate whether that Run failed or hit an unusual
  basin; do not silently exclude it
- The y-axis direction matters: for minimization, lower is better

**Conditional replacement:** When `Study.repetitions > 50` or more than 6 algorithms are
compared, VIZ-L1-04 (violin) replaces this plot.

**Appears in:** Researcher report §Level 1 EDA only.

---

#### VIZ-L1-02: Convergence Curves

**What it shows:** Best-so-far objective value vs. evaluation number for each algorithm.
Solid line = median over repetitions; shaded band = IQR (25th–75th percentile). One figure
per problem instance; all algorithms overlaid with distinct colors.

**When most useful:** Diagnosing anytime behavior — when does each algorithm converge? Does
one algorithm front-load improvement while another continues improving late?

**How to interpret:**
- A curve that reaches its minimum early and flattens has good early convergence; whether
  this is an advantage depends on the practitioner's actual budget
- Crossing curves — algorithm A better at low budget, B better at high budget — make
  any global comparison invalid; conclusions must be budget-scoped (see §3.9 `conclusion_scope`)
- A wide IQR band → high run-to-run variance; investigate whether this is structural or
  due to a few outlier Runs (cross-reference VIZ-L1-01)
- X-axis is log scale when `budget > 100` — gaps in the curve may be artefacts of the
  log-scale schedule; interpolation is LOCF (ADR-003), not smoothing

**Appears in:** Researcher report §Level 1 EDA; Practitioner report §Visualizations.

---

#### VIZ-L1-03: ECDF (Empirical Cumulative Distribution Function)

**What it shows:** For each algorithm, the fraction of Runs that achieved a given quality
target or better, plotted as a step function. Aggregated across all problem instances.

**Implementation requirement:** `matplotlib.pyplot.step(x, y, where='post')` — the
`where='post'` parameter is mandatory so the step fires at the exact quality threshold.

**When most useful:** Summarizing anytime performance across the full quality range in a
single figure. Especially informative when algorithms have different failure modes (one
consistently mediocre vs. one bimodal — often or almost never succeeds).

**How to interpret:**
- A curve shifted **left and up** dominates — more Runs achieve better quality
- A **flatter** curve → high variability; the algorithm's success depends heavily on
  the specific run
- A curve that never reaches fraction 1.0 → some Runs failed to reach any improvement;
  cross-reference `RELIABILITY-SUCCESS_RATE`
- The area under the ECDF curve over the normalized quality range corresponds directly to
  the `ANYTIME-ECDF_AREA` metric (§7 of `07-anytime-ecdf-area.md`)

**Appears in:** Researcher report §Level 1 EDA; Practitioner report §Visualizations.

---

#### VIZ-L1-04: Violin Plot [conditional]

**When generated:** `Study.repetitions > 50`, or more than 6 algorithms are compared.
Replaces VIZ-L1-01 in those cases.

**What it shows:** Kernel density estimate of the `QUALITY-BEST_VALUE_AT_BUDGET`
distribution per (algorithm, problem) cell. Inner box shows IQR; center line shows median.

**When most useful:** Large-sample studies where distribution shape (multimodality, skew,
heavy tails) carries scientific information that a box plot would suppress.

**How to interpret:**
- A narrow violin → concentrated results; the algorithm is reliable
- A bimodal violin (two bumps) → two distinct performance regimes; the algorithm probably
  has a structural failure mode on this problem; investigate Runs in each mode separately
- Wide tails → some Runs do dramatically better or worse; check whether these correlate
  with a specific seed or initialization

**Appears in:** Researcher report §Level 1 EDA (conditional).

---

### 2.2 What to look for

After generating the four visualizations, work through this checklist before proceeding
to Level 2:

| Question | Where to look | Why it matters |
|---|---|---|
| Are there outlier Runs with anomalous performance? | VIZ-L1-01 outlier points, VIZ-L1-02 wide IQR | Determine whether they are errors (exclude with disclosure) or informative (keep and note) |
| Is the distribution shape approximately normal? | VIZ-L1-01 / VIZ-L1-04 symmetry | Determines whether parametric or non-parametric tests apply in Level 2 (§3.3) |
| Do algorithms cross in performance at different budgets? | VIZ-L1-02 crossing curves | Conclusions must be budget-scoped; a single endpoint comparison is insufficient |
| Does relative performance differ across problems? | VIZ-L1-01/VIZ-L1-02 per-problem plots | Algorithm × problem interactions require per-problem scoping in Level 2 |
| Does any algorithm show a bimodal distribution? | VIZ-L1-04 (if generated) | Bimodality warrants investigation before aggregation; may indicate a structural failure mode |
| Are success rates materially different? | VIZ-L1-03 max y-value | Low success rate on one algorithm changes the appropriate test (§3.8 McNemar) |

---

### 2.3 What NOT to do at Level 1

- **Do not compute p-values** from exploratory visualizations — patterns in visualizations
  are not conclusions.
- **Do not state conclusions** — write observations ("CMA-ES shows higher variance on
  problem P than Nelder-Mead") not claims ("CMA-ES is worse").
- **Do not select which algorithms to compare** post-hoc based on who looks best in the
  visualizations. All comparisons in Level 2 must come from `pre_registered_hypotheses`.
- **Do not exclude Runs** without logging them. Every excluded Run must be counted in the
  Run Summary and its exclusion reason stated in the Limitations section (FR-21).

---

### 2.4 Output of Level 1

Level 1 produces two artifacts:

1. **The four visualizations** (VIZ-L1-01 through VIZ-L1-04) embedded in the Researcher
   report §Level 1 EDA.

2. **An observations narrative** stored in `AnalysisReport.exploratory_observations`:
   a bulleted list of what was observed (not concluded) and, separately, candidate
   hypotheses that emerged from the exploration — for registration in **future** studies,
   never retrofitted into the current Study's pre-registered hypotheses.

---

## 3. Level 2: Confirmatory Analysis

### 3.1 Preconditions

Only hypotheses listed in `Study.pre_registered_hypotheses` (data-format.md §2.3) may be
tested here. The test name, α, and correction method must be declared before data collection;
they are locked with the Study record. Testing a hypothesis not in that list is a post-hoc
observation (Pitfall 1) and is automatically labeled "exploratory" in the Analyzer output.

---

### 3.2 Data structure in HPO benchmarking: always paired

HPO benchmarking evaluates all Algorithm Instances on the same set of Problem Instances. This
is a **paired (blocked) design**: for each Problem Instance $p$, both Algorithm A and
Algorithm B produce a metric value, and the scientifically relevant quantity is the
*difference* on that problem.

Ignoring the pairing and using independent-samples tests discards the problem-level blocking,
reduces statistical power, and inflates variance estimates. All test selection below assumes
the default paired structure. The unpaired path is included for completeness but requires
explicit justification if used.

---

### 3.3 Test selection decision tree

*Implements MANIFESTO Principle 15; reference: Bartz-Beielstein et al. (2020) §4.*

```
Is the distribution of per-problem metric differences approximately normal?
(Use Q-Q plots and Shapiro-Wilk from Level 1 to check. n < 30 → assume non-normal.)
│
├── YES — and n ≥ 30 runs per algorithm:
│   ├── 2 algorithms, paired  →  Paired t-test
│   └── > 2 algorithms        →  Repeated-measures ANOVA
│                                  → if omnibus p < α: Tukey HSD post-hoc (pairwise)
│
└── NO (non-normal) or unknown  [DEFAULT — use this path unless normality is confirmed]
    ├── 2 algorithms, paired  →  Wilcoxon signed-rank test           [§3.4]
    └── > 2 algorithms        →  Kruskal-Wallis test (omnibus)       [§3.5]
                                   → if omnibus p < α: pairwise Wilcoxon signed-rank
                                     with Holm-Bonferroni correction [§3.6]
```

**The default path is non-normal / non-parametric.** HPO metric distributions are
frequently skewed or multi-modal (bounded objectives, success-rate proportions, ECDF areas
near 0 or 1). Use the parametric path only when Level 1 provides positive evidence of
normality — not as the default.

---

### 3.4 Wilcoxon signed-rank test (2 algorithms, paired)

**When:** 2 Algorithm Instances, paired design (same Problem Instances), non-normal.

**Null hypothesis H₀:** The distribution of differences $d_p = m_A(p) - m_B(p)$ is
symmetric about zero, where $m_A(p)$ is the metric value of Algorithm A on Problem Instance
$p$.

**Procedure:**

1. For each Problem Instance $p \in \{1, \ldots, P\}$, compute $d_p = m_A(p) - m_B(p)$.
2. Exclude pairs where $d_p = 0$ (tied ranks); record the number excluded.
3. Rank the absolute differences $|d_p|$; assign average ranks to ties.
4. Compute $W^+$ (sum of ranks for positive differences) and $W^-$ (sum for negative).
5. Test statistic: $W = \min(W^+, W^-)$; compare to the Wilcoxon signed-rank distribution
   (exact for small $P$, normal approximation for $P \geq 25$).

**Minimum sample:** $P \geq 5$ Problem Instances. Below 5, the test lacks sufficient power
and the result must be labeled "exploratory" regardless of p-value.

**Effect size:** Rank-biserial correlation $r = 1 - \frac{2W}{\frac{P(P+1)}{2}}$.
Interpretation: $|r| < 0.1$ negligible, $0.1$–$0.3$ small, $0.3$–$0.5$ medium, $> 0.5$
large (Cohen 1988 thresholds adapted for rank correlations).

Report at Level 3 alongside the p-value.

---

### 3.5 Kruskal-Wallis test (> 2 algorithms, omnibus)

**When:** More than 2 Algorithm Instances, any pairing structure, non-normal.

**Null hypothesis H₀:** All $k$ algorithm metric distributions are identical.

**Procedure:**

1. Pool all $k \times P$ per-problem metric values into a single ranked list.
2. Compute $H = \frac{12}{N(N+1)} \sum_{i=1}^{k} \frac{R_i^2}{n_i} - 3(N+1)$
   where $N = kP$, $n_i = P$ (same number of problems per algorithm), $R_i$ is the rank sum
   for algorithm $i$.
3. Compare $H$ to $\chi^2$ with $k-1$ degrees of freedom.

**The omnibus test answers: "are these distributions different at all?"** — not which pair
differs. A non-significant omnibus result terminates Level 2 for that hypothesis set: do not
proceed to pairwise comparisons.

If omnibus $p < \alpha$: proceed to pairwise post-hoc tests (§3.5.1).

**Effect size for omnibus:** $\eta^2 = \frac{H - k + 1}{N - k}$. Interpretation: $< 0.01$
negligible, $0.01$–$0.06$ small, $0.06$–$0.14$ medium, $> 0.14$ large.

#### 3.5.1 Post-hoc pairwise comparisons

Conduct pairwise Wilcoxon signed-rank tests for all $\binom{k}{2}$ algorithm pairs. Apply
**Holm-Bonferroni correction** (§3.6) to the resulting $m = \binom{k}{2}$ p-values.

Report each pairwise result with: uncorrected p-value, corrected p-value, Holm step applied,
reject/fail-to-reject at corrected α, rank-biserial correlation effect size.

---

### 3.6 Multiple testing correction: Holm-Bonferroni (preferred)

**Required whenever $m > 1$ hypotheses are tested in the same study**, regardless of whether
they arise from post-hoc pairwise comparisons or from a pre-registered set of distinct
hypotheses.

**Holm-Bonferroni procedure** (Holm 1979):

1. Compute $m$ p-values $\{p_1, \ldots, p_m\}$. Sort ascending: $p_{(1)} \leq \cdots \leq p_{(m)}$.
2. For step $i = 1, \ldots, m$: compare $p_{(i)}$ to $\alpha / (m - i + 1)$.
   - If $p_{(i)} \leq \alpha / (m - i + 1)$: reject $H_{(i)}$ and continue.
   - If $p_{(i)} > \alpha / (m - i + 1)$: **stop** — fail to reject $H_{(i)}$ and all
     remaining hypotheses $H_{(i+1)}, \ldots, H_{(m)}$.

**Why Holm over Bonferroni:** Holm-Bonferroni controls the family-wise error rate (FWER) at
the same level as Bonferroni but is **uniformly more powerful** — it rejects at least as many
hypotheses. Bonferroni applies the same correction $\alpha/m$ to every p-value regardless of
rank; Holm relaxes the threshold for hypotheses tested after earlier rejections. The power
advantage grows with $m$. Bonferroni is acceptable only as a conservative worst-case bound
when $m$ is very small (2–3 hypotheses) and simplicity is paramount.

**Benjamini-Hochberg (BH/FDR) is not used here.** BH controls the false discovery rate,
not the family-wise error rate. For confirmatory analyses in this system — where each
hypothesis corresponds to a specific, pre-registered scientific claim — a single false
positive undermines a conclusion. FWER control is therefore the correct criterion. BH is
appropriate for exploratory screening (many hypotheses, high tolerance for some false
positives), which belongs in Level 1, not Level 2.

---

### 3.7 Significance threshold

The default α is **0.05**. Researchers may declare a different threshold but must do so
in `pre_registered_hypotheses` before data collection. Post-hoc threshold adjustment is
a form of p-hacking (Pitfall 1).

A result at $p = 0.048$ and a result at $p = 0.003$ are both "reject at α = 0.05" —
the system does not distinguish degrees of significance from the binary reject/fail-to-reject
decision. The effect size (§3.4, §3.5) carries the magnitude information.

---

### 3.8 Special cases

#### RELIABILITY-SUCCESS_RATE (proportion data)

`RELIABILITY-SUCCESS_RATE` is a proportion, not a continuous metric. The tests above do not
apply directly. Use:

- 2 algorithms: **McNemar's test** (paired binary outcomes per run)
- > 2 algorithms: **Cochran's Q test** (generalization of McNemar to $k$ groups)
- Effect size: Cohen's $h = 2 \arcsin\sqrt{p_A} - 2 \arcsin\sqrt{p_B}$

#### TIME-EVALUATIONS_TO_TARGET (censored data)

`TIME-EVALUATIONS_TO_TARGET` includes censored values ($B+1$ when target is never reached).
Applying Wilcoxon to censored data may be invalid if censoring rate differs across algorithms.
Use:

- **Log-rank test** when censoring rates differ substantially between algorithms
- Wilcoxon is valid when both algorithms have the same censoring pattern (all-or-none) or
  the censoring rate is below 10%

#### Small sample correction

When $P < 10$ Problem Instances, use exact Wilcoxon (permutation-based) rather than the
normal approximation. The `exact` option is available in standard scientific Python libraries.

---

### 3.9 Output format per hypothesis

The Analyzer must produce for each tested hypothesis:

| Field | Description |
|---|---|
| `hypothesis_id` | Matches `pre_registered_hypotheses` ID from Study record |
| `test_name` | e.g., `wilcoxon_signed_rank`, `kruskal_wallis`, `mccnemar` |
| `n_problems` | Number of Problem Instances used in the test |
| `n_runs_per_algorithm` | Runs per algorithm (for within-cell aggregation if applicable) |
| `test_statistic` | Raw test statistic value |
| `p_value` | Uncorrected p-value |
| `correction_method` | `holm_bonferroni`, `bonferroni`, or `none` |
| `corrected_p_value` | After correction (equals `p_value` if `none`) |
| `alpha` | Declared significance threshold |
| `reject` | Boolean: `true` if `corrected_p_value ≤ alpha` |
| `effect_size` | Value and measure name (e.g., `{"measure": "rank_biserial", "value": 0.42}`) |
| `conclusion_scope` | Explicit scope: algorithm IDs, problem IDs, budget, metric ID |

`conclusion_scope` is the primary mechanism preventing over-generalization (Pitfall 4). It
must be populated for every result, not only significant ones.

---

*Reference: Bartz-Beielstein, T., Bossek, J., Lang, M., & Mersmann, O. (2020).
"Benchmarking in Optimization: Best Practice and Open Issues."
arXiv:2007.03488. §4 (Statistical Analysis of Benchmark Results).*

---

## 4. Level 3: Practical Significance Analysis

<!--
  Purpose:
    Answer "does the difference matter in practice?" independently of statistical significance.
    A difference can be statistically significant but practically negligible, or vice versa.
    → MANIFESTO Principle 13 (three-level analysis), Principle 15 (practical utility)

  ### Effect Size Measures
  For each applicable test from Level 2, a corresponding effect size measure:

    | Test used           | Effect size measure    | Interpretation scale               |
    |---------------------|------------------------|------------------------------------|
    | [parametric test]   | Cohen's d              | small / medium / large thresholds  |
    | [non-parametric]    | Cliff's delta          | negligible / small / medium / large|

  How to interpret effect sizes in the HPO domain:
    Hint: a "large" statistical effect may be practically negligible if the objective
    function values are all near the optimum. Context matters.
    → Reference problem-specific baselines when interpreting effect sizes.

  ### Practical Recommendations
  When is it appropriate to recommend one algorithm over another?
    - Statistical significance alone is NOT sufficient
    - Effect size must exceed a threshold meaningful for practitioners
    - The recommendation must be scoped to the tested problem characteristics

  ### Reporting Practical Significance
    Every study report MUST include effect sizes alongside p-values.
    → Reporting without effect sizes violates SRS NFR-STAT.
-->

---

## 5. Anytime Analysis

<!--
  Why anytime analysis matters:
    Final-budget performance ignores optimization dynamics.
    An algorithm that reaches good solutions early may be preferable to one that
    barely edges ahead at the maximum budget. → MANIFESTO Principle 14.

  ### Empirical Cumulative Distribution Functions (ECDF)
    Definition: what does an ECDF show in this context?
    How to compute: [procedural definition]
    How to interpret: what does the area under the ECDF represent?
    Multiple algorithms: how to overlay ECDFs for comparison?

  ### Performance Profiles
    When to use performance profiles vs. ECDFs?
    How to interpret a performance profile gap between algorithms?

  ### Budget-Sensitive Comparison
    How to compare algorithms at multiple budget checkpoints?
    → requires PerformanceRecord data: data-format.md §2.6
    Statistical considerations: applying Level 2 tests at multiple budgets introduces
    multiple testing — how to handle?

  ### Detecting Performance Crossovers
    Sometimes algorithm A is better at low budget, B at high budget.
    How to detect and report crossovers?
    Why crossovers make global ranking impossible (connects to MANIFESTO Principle 2, NFL).
-->

---

## 6. Uncertainty Reporting Requirements

<!--
  What MUST accompany every reported metric value.
  Reporting only a mean without spread is prohibited (MANIFESTO Principle 15).

  Required alongside every aggregate metric:
    - Standard deviation OR interquartile range (depending on distribution shape)
    - Sample size (n_runs)
    - Success rate (if applicable — how many runs completed successfully)
    - Confidence interval (specify level: 95%? 99?)

  → These map directly to ResultAggregate fields in specs/data-format.md §2.7.
  If a ResultAggregate is missing any of these, it fails validation.
-->

---

## 7. Common Methodological Pitfalls

A catalogue of mistakes this methodology is designed to prevent. Each entry states: what the mistake looks like in practice, why it is scientifically invalid, which MANIFESTO principle it violates, and which part of this guide or the system prevents it.

---

### Pitfall 1: Post-Hoc Hypothesis Selection (p-hacking)

**What it looks like:** Running the full analysis, visualizing results, noticing that Algorithm A beats Algorithm B on metric X, then reporting a hypothesis test of "Algorithm A > Algorithm B on metric X" as if it were pre-planned.

**Why it is wrong:** When you select hypotheses from data, the effective significance level is no longer α. With k metrics and m algorithm pairs, you can find a significant result by chance even if there are none. The stated p-value is mathematically invalid.

**MANIFESTO violation:** Principle 16 (planning precedes execution), Principle 29 (objectivity over promotion).

**How this system prevents it:** Hypotheses are stored in the Study record's `pre_registered_hypotheses` field (`docs/03-technical-contracts/data-format.md` §2.3) before any data collection begins. The Analyzer interface (`docs/03-technical-contracts/interface-contracts.md` §4) only tests pre-registered hypotheses in Level 2; post-hoc observations are labeled "exploratory" in the output.

---

### Pitfall 2: Reporting Only Means Without Spread

**What it looks like:** "Algorithm A achieved an average objective value of 0.95 vs. Algorithm B's 0.87" — without standard deviation, IQR, or run count.

**Why it is wrong:** Averages hide variance. An algorithm that achieves 0.95 on 1 run out of 10 and fails catastrophically on 9 others has the same mean as one that consistently achieves 0.95. The reader cannot distinguish them.

**MANIFESTO violation:** Principle 15 ("we report not only averages, but also spread, quantiles, success probabilities").

**Prevention:** §6 Uncertainty Reporting Requirements — the system enforces that `ROBUSTNESS-RESULT_STABILITY` and `RELIABILITY-SUCCESS_RATE` are always reported alongside `QUALITY-BEST_VALUE_AT_BUDGET` in the Standard Reporting Set (`docs/03-technical-contracts/metric-taxonomy.md` §3).

---

### Pitfall 3: Ignoring Multiple Testing

**What it looks like:** Comparing 5 algorithms pairwise (10 pairs), reporting that 4 pairs are "statistically significant at p < 0.05" without correction.

**Why it is wrong:** At α = 0.05 with 10 independent tests, we expect 0.5 false positives by chance. With 4 "significant" results, the expected false positive count could be close to 0.5 — meaning some of the claimed significances are almost certainly noise.

**MANIFESTO violation:** Principle 15 (appropriate statistical methods), Principle 29 (objectivity).

**Prevention:** §3.6 Holm-Bonferroni correction — applied whenever $m > 1$ hypotheses are tested. The correction method must be declared in the Study plan. Holm-Bonferroni is the default; Bonferroni is accepted as a conservative alternative; BH/FDR is excluded from confirmatory analysis (§3.6 explains why).

---

### Pitfall 4: Over-Generalization from Few Problem Instances

**What it looks like:** Testing two algorithms on three Problem Instances and concluding "Algorithm A is better than Algorithm B."

**Why it is wrong:** Three instances cannot represent the diversity of HPO problem classes. The conclusion is valid only for those three instances. The No Free Lunch theorem (GLOSSARY: No Free Lunch) makes universal claims impossible.

**MANIFESTO violation:** Principle 3 (understanding before generalizing), Principle 30 (NFL limitations).

**Prevention:** Every system-generated conclusion includes an explicit scope statement: for which Problem Instances and Algorithm Instances the conclusion holds. Extrapolation is labeled and must be separately justified. See `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Step 7 (Scope and Report Conclusions).

---

### Pitfall 5: Conflating Statistical Significance with Practical Significance

**What it looks like:** "Algorithm A is significantly better (p = 0.001)" — without reporting the actual difference in objective value or an Effect Size.

**Why it is wrong:** With large sample sizes (many Runs), even trivially small differences become statistically significant. p = 0.001 with 10,000 Runs may correspond to an Effect Size of d = 0.01 — meaningless in practice.

**MANIFESTO violation:** Principle 13 (three-level analysis — practical significance is mandatory), Principle 15.

**Prevention:** Level 3 (Practical Significance) of the three-level framework (§1 above) is required — Effect Sizes are not optional. The system does not produce a final report without effect size values alongside significance test results. See §4 once filled.

---

### Pitfall 6: Comparing Algorithms at Only One Budget Level

**What it looks like:** Running algorithms for 200 evaluations and comparing only final results, without examining intermediate performance.

**Why it is wrong:** An algorithm that reaches near-optimal solutions at evaluation 50 and one that barely reaches them at evaluation 200 are indistinguishable by final-budget metrics alone. Practitioners often have smaller budgets than the study used; the comparison is uninformative for them.

**MANIFESTO violation:** Principle 14 (full performance curves, not just endpoints).

**Prevention:** `ANYTIME-ECDF_AREA` is mandatory in the Standard Reporting Set (`docs/03-technical-contracts/metric-taxonomy.md` §3). Full Performance Records are required to be stored for all Runs, enabling comparison at any budget level.
