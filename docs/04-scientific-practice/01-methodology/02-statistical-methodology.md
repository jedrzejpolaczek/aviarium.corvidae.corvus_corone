# Statistical Methodology Guide

<!--
STORY ROLE: The "scientific rigor chapter". Defines HOW results are interpreted.
This document is what separates this system from ad-hoc benchmarking.
Without it, the same data can support contradictory conclusions.

NARRATIVE POSITION:
  MANIFESTO Principles 13, 15 → Statistical Methodology → (how we analyze and report)
  → docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md §Step 6: the protocol invokes this guide there

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md Principles 13, 15 : directly operationalized by this document
  ← docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md NFR-STAT-01 : non-functional requirement for statistical validity
  → docs/03-technical-contracts/03-metric-taxonomy/01-index.md    : metric properties (distribution, bounds) guide test selection here
  → docs/03-technical-contracts/02-interface-contracts/01-index.md §4 : Analyzer interface implements this methodology
  → docs/03-technical-contracts/01-data-format/08-result-aggregate.md   : Result Aggregate fields store uncertainty information defined here
  → docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md : protocol's analysis step (Step 6) references this guide
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

Hypotheses tested in Level 2 **MUST be pre-specified in the Study plan** (`docs/03-technical-contracts/01-data-format/01-index.md` §2.3 `pre_registered_hypotheses`) **before** Level 1 analysis begins. This is non-negotiable.

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
| Is the distribution shape strongly skewed or multi-modal? | VIZ-L1-01 / VIZ-L1-04 symmetry | Not a test-selection question in V1 — §3.3 is non-parametric throughout — but it belongs in the Report: a bimodal or heavily skewed distribution changes how the median and the effect size should be read |
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

Only hypotheses listed in `Study.pre_registered_hypotheses` (docs/03-technical-contracts/01-data-format/04-study.md) may be
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
How many Algorithm Instances does the hypothesis compare?
│
├── 2 algorithms, paired  →  Wilcoxon signed-rank test              [§3.4]
│
└── > 2 algorithms        →  Kruskal-Wallis test (omnibus)          [§3.5]
                               → if omnibus p < α: pairwise Wilcoxon signed-rank
                                 with Holm-Bonferroni correction    [§3.6]
```

Two leaves, and the `test_type` field of a pre-registered hypothesis takes the corresponding
value: `wilcoxon` or `kruskal`. A third value, `none`, declares the Study exploratory (ADR-021,
FR-31) and runs no test at all.

**Why there is no parametric branch.** Earlier revisions of this section offered one — paired
t-test, repeated-measures ANOVA, Tukey HSD — behind a normality check, while describing the
non-parametric path as the default to be used *unless normality is confirmed*. The branch was
removed from V1 for three reasons, and the first is the one that decides it.

The condition guarding it is almost never met. Confirming normality needs a positive result from
Level 1, and the guard itself said `n < 30 → assume non-normal`. A Study that satisfies the
ADR-009 diversity floor has five Problem Instances; the paired test operates on five per-problem
differences. Shapiro-Wilk on five observations has almost no power to reject, so a
"non-significant normality test" there is an absence of evidence, not evidence of normality —
and taking it as permission to use the parametric path is the inference the section warned
against two paragraphs below the tree that offered it.

HPO metric distributions are the second reason: bounded objectives, success-rate proportions and
ECDF areas near 0 or 1 are frequently skewed or multi-modal, so the non-parametric path is not
merely the safe default, it is usually the correct one.

The third is that the branch was not expressible. `paired_t_test`, `rm_anova` and `tukey_hsd`
appear in no contract, so no researcher could pre-register one, and ADR-021 makes pre-registration
the condition of locking a Study. A test that cannot be declared before data collection cannot be
run as confirmatory analysis in this system.

**Post-V1.** A parametric branch is a reasonable extension once studies exist with enough
Problem Instances for a normality check to mean something. It needs three new contracted
`test_type` values, Cohen's d alongside Cliff's delta in §4, and an ADR stating the evidence
threshold at which the guard opens. None of that is V1 work.

---

### 3.4 Wilcoxon signed-rank test (2 algorithms, paired)

**When:** 2 Algorithm Instances on the same Problem Instances. This is the whole of the two-algorithm case in V1; §3.3 has no parametric alternative to select against.

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

**Effect size:** Cliff's delta, with the thresholds of §4.2. Rank-biserial correlation is the
natural partner of the $W$ statistic and stood here through several revisions; §4.1 records why
one measure is reported across every pairwise comparison instead.

Report at Level 3 alongside the p-value (§4.3).

---

### 3.5 Kruskal-Wallis test (> 2 algorithms, omnibus)

**When:** More than 2 Algorithm Instances. This is the whole of the multi-algorithm case in V1.

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

**Effect size for omnibus:** $\eta^2$, which is not Cliff's delta and does not contradict §4.1:
delta is pairwise and has no omnibus form, so the omnibus carries $\eta^2$ and the pairwise
comparisons that follow carry delta. A `StatisticalTestResult` names its measure in
`effect_size_measure`, so a Report never presents the two on one scale.

$\eta^2 = \frac{H - k + 1}{N - k}$. Interpretation: $< 0.01$
negligible, $0.01$–$0.06$ small, $0.06$–$0.14$ medium, $> 0.14$ large.

#### 3.5.1 Post-hoc pairwise comparisons

Conduct pairwise Wilcoxon signed-rank tests for all $\binom{k}{2}$ algorithm pairs. Apply
**Holm-Bonferroni correction** (§3.6) to the resulting $m = \binom{k}{2}$ p-values.

Report each pairwise result with: uncorrected p-value, corrected p-value, Holm step applied,
reject/fail-to-reject at corrected α, and Cliff's delta with its magnitude label (§4.1). Earlier
revisions required rank-biserial correlation here and Cliff's delta in §4; one measure is reported,
for the reason given in §4.1.

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

**α has no default. It is a required part of every pre-registered hypothesis.**

FR-28 forbids a silent default on any parameter with methodological consequences, and a
significance threshold is the clearest case there is: a threshold the system supplies is a
threshold nobody chose, and one chosen after the data exists is not a threshold at all
(Pitfall 1). `test_config.alpha` is therefore declared in `pre_registered_hypotheses` before
data collection and locked with the Study, and the Analyzer refuses a comparison that has no
declared α rather than assuming one.

**0.05 is the conventional value and remains the recommendation**, which is a different thing
from a default: a researcher who wants 0.05 writes 0.05, and the record then says they chose
it. Choose a smaller threshold when a false positive is expensive — a claim that one algorithm
beats another on a published benchmark is hard to retract — and note that Holm-Bonferroni
(§3.6) already tightens the effective threshold as the hypothesis family grows.

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

> **Not yet reconciled with the contract.** `05-analyzer-interface.md` defines
> `StatisticalTestResult` with a different field set and different names — `p_value_adjusted`
> where this table has `corrected_p_value`, and `effect_size` with `effect_size_measure` as two
> fields where this table nests them. Under ADR-026 this document is authoritative for the
> procedure, not for field names, so the contract governs wherever the two differ. Which of the
> fields below the procedure needs and the contract lacks is open as REF-TASK-0055.

| Field | Description |
|---|---|
| `hypothesis_id` | Matches `pre_registered_hypotheses` ID from Study record |
| `test_name` | e.g., `wilcoxon_signed_rank`, `kruskal_wallis` |
| `n_problems` | Number of Problem Instances used in the test |
| `n_runs_per_algorithm` | Runs per algorithm (for within-cell aggregation if applicable) |
| `test_statistic` | Raw test statistic value |
| `p_value` | Uncorrected p-value |
| `correction_method` | `holm_bonferroni`, `bonferroni`, or `none` |
| `corrected_p_value` | After correction (equals `p_value` if `none`) |
| `alpha` | Declared significance threshold |
| `reject` | Boolean: `true` if `corrected_p_value ≤ alpha` |
| `effect_size` | Value and measure name (e.g., `{"measure": "cliffs_delta", "value": 0.42}`; §4.1) |
| `conclusion_scope` | Explicit scope: algorithm IDs, problem IDs, budget, metric ID |

`conclusion_scope` is the primary mechanism preventing over-generalization (Pitfall 4). It
must be populated for every result, not only significant ones.

---

*Reference: Bartz-Beielstein, T., Bossek, J., Lang, M., & Mersmann, O. (2020).
"Benchmarking in Optimization: Best Practice and Open Issues."
arXiv:2007.03488. §4 (Statistical Analysis of Benchmark Results).*

---

## 4. Level 3: Practical Significance Analysis

Level 2 answers whether a difference is detectable. Level 3 answers whether it is worth anything.
The two are independent, and a study that reports only the first is the failure MANIFESTO
Principle 13 exists to prevent: with thirty repetitions on five problems, a difference of 0.001 in
validation loss can reach p < 0.01 and mean nothing to anyone deploying the algorithm.

FR-15 makes this level mandatory. A report without effect sizes is not produced; the Analyzer
raises `AnalysisIncompleteError`.

---

### 4.1 The effect size is Cliff's delta

**Every pairwise comparison reports Cliff's delta**, including the pairwise Wilcoxon tests that
follow a significant Kruskal-Wallis omnibus (§3.5.1). One measure, one interpretation scale, one
implementation.

For two samples $A$ and $B$ of per-problem metric values,

$$\delta = \frac{\#\{(a,b) : a > b\} - \#\{(a,b) : a < b\}}{|A| \cdot |B|}$$

taken over all pairs. It is the probability that a randomly chosen value from $A$ exceeds one from
$B$, minus the probability of the reverse. $\delta \in [-1, 1]$; $0$ means complete overlap,
$\pm 1$ means the samples do not overlap at all.

**Why Cliff's delta and not a parametric measure.** It is a rank statistic, so it makes the same
distributional assumptions as the tests in §3 — none — and it is computable directly from the two
samples with no optional dependency. Cohen's d would assume the normality that §3.3 declines to
assume.

**Why not rank-biserial correlation for the post-hoc case.** Rank-biserial is the natural partner
of the Wilcoxon statistic and is defensible on its own. It was rejected because a Report that
carries two effect-size measures on two interpretation scales asks its reader to hold both, and
the reader is a Practitioner in half the cases. Earlier revisions of this document required
rank-biserial in §3.5.1 and Cliff's delta here, which is how the corpus came to specify both.

---

### 4.2 Interpretation thresholds

| $|\delta|$ | Magnitude |
|---|---|
| < 0.147 | negligible |
| 0.147 – 0.33 | small |
| 0.33 – 0.474 | medium |
| ≥ 0.474 | large |

These are the thresholds of Romano et al. (2006), derived by mapping Cohen's conventional d
values of 0.2, 0.5 and 0.8 onto the delta scale. They are conventions, not measurements, and this
document adopts them so that two studies in this system label the same difference the same way.

**A label is not a conclusion.** The scale says how separated two distributions are; it does not
say whether the separation matters, and it cannot, because that depends on the objective. A
"large" delta between two algorithms whose final validation losses differ by 0.0004 is a
statement about consistency, not about practical value. Both the magnitude label and the raw
difference in the objective's own units belong in the Report, and §4.3 is where the reader is
told how to combine them.

---

### 4.3 What the Report must say

Every comparison in a Researcher Report carries four things together, and the Practitioner Report
carries the first, third and fourth in prose:

1. the corrected p-value and the reject / fail-to-reject decision at the declared α;
2. Cliff's delta and its magnitude label;
3. the difference in the objective's own units, with the unit named;
4. the conditions under which the comparison holds — which Problem Instances, at which Budget.

**A recommendation requires more than significance.** A Report may state that one Algorithm
Instance outperformed another on the tested Problem Instances when the difference is statistically
detected *and* the effect size is at least small *and* the difference is meaningful in the
objective's units. Significance alone is not sufficient, and the Report says so where it applies:
a detected difference with a negligible effect size is reported as a detected difference with a
negligible effect size, not as a finding.

None of this is a ranking. FR-21 and CONST-SCI-01 forbid ranking output entirely, and a
recommendation scoped to the tested Problem Instances is not one — the scope statement is what
makes the difference, and it is mandatory.

---

## 5. Anytime Analysis

An algorithm that reaches a good solution at evaluation 200 and one that reaches a marginally
better solution at evaluation 10 000 are not the same algorithm, and a final-budget comparison
cannot tell them apart. MANIFESTO Principle 14 requires full performance curves, and this section
is how they are read.

---

### 5.1 The curve

For each Run, the anytime curve is `best_so_far` as a function of `evaluation_number`. It is
monotone in the objective's direction by construction, and it is defined at every evaluation in
`1 .. B` even though a Performance Record exists only where a trigger fired: the value between two
records is the value of the earlier one, because no improvement occurred in between — that is the
LOCF rule of ADR-003, and it reconstructs rather than approximates.

Curves are read from `best_so_far`, never from `objective_value`. The raw value of a single
evaluation may be worse than the best already seen, and carrying it forward would produce a curve
that is not monotone and not the algorithm's state (ADR-023).

---

### 5.2 Empirical cumulative distribution functions

An ECDF over a Problem–Algorithm cell answers: by evaluation $k$, what fraction of the observable
improvement range had the algorithm realised, averaged over its Runs?

The value axis is normalised to the cell's own empirical bounds — `y_max` the worst initial value
across its Runs, `y_min` the best final value (ADR-007). There is no known optimum to normalise
against for a real ML objective, so the observable range is the only well-defined reference frame
available, and it is a frame per cell rather than per study because two problems with objectives
on different scales would otherwise not contribute equally.

`ANYTIME-ECDF_AREA` is the area under that curve, normalised so that 1 would mean the cell sat at
`y_min` from the first evaluation. The integration domain is the whole Budget, treated as $B$
unit-width steps (ADR-024); the procedure and its reference case are in
[`03-metric-taxonomy/07-anytime-ecdf-area.md`](../../03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md).

**Values are not comparable across studies.** The bounds come from the Runs of one study, so two
studies differing in algorithm portfolio, repetition count or Budget produce different bounds on
the same Problem Instance. Every Report states this in its limitations section; ADR-007 makes it a
mandatory disclosure rather than a caveat the author may omit.

---

### 5.3 Comparing at more than one budget

An algorithm's advantage can reverse. Where two curves cross, "which is better" has no
budget-independent answer, and reporting one endpoint hides that entirely — Pitfall 6.

Read the convergence curves (VIZ-L1-02) for crossings before reporting any single-budget
comparison. Where a crossing is visible, the Report says so and scopes each conclusion to the
budget region where it holds.

**Testing at several budgets is testing several hypotheses.** Comparing two algorithms at
evaluations 100, 1 000 and 10 000 is three comparisons, and §3.6 applies to the family exactly as
it does to three pre-registered hypotheses. Choosing the budget after seeing the curves is
Pitfall 1 wearing different clothes: budget checkpoints are declared in the Study before data
collection, like everything else about the comparison.

---

## 6. Uncertainty Reporting Requirements

MANIFESTO Principle 15 requires spread, quantiles and success probabilities alongside averages.
A mean with no spread is not a result: with five Problem Instances and thirty repetitions, the
same mean can come from an algorithm that behaves identically every time and from one that
succeeds brilliantly half the time and fails the rest, and those are different algorithms.

---

### 6.1 What accompanies every reported metric value

| Required | Notes |
|---|---|
| A measure of spread | Interquartile range by default. Standard deviation only where the distribution is approximately symmetric, which VIZ-L1-01 and VIZ-L1-04 are what the reader checks |
| The number of Runs behind it | `ResultAggregate.n_runs`. A metric computed over three Runs and one computed over thirty are not comparable, and the Report must not present them as though they were |
| The number that succeeded | Where a Run can fail or a metric can be undefined for a Run, the count that contributed is stated. A mean over the Runs that happened to finish is a selected sample |
| The 95% confidence interval | For the median, computed by bootstrap over the Runs. 95% because it is the convention and a study that departs from it should say why |

These map onto `AggregateValue.statistics` in
[`01-data-format/08-result-aggregate.md`](../../03-technical-contracts/01-data-format/08-result-aggregate.md),
whose one required field is `n_successful`. A Result Aggregate missing them fails validation, and
a Report cannot be produced from an aggregate that failed validation.

---

### 6.2 Why the interval is bootstrapped and around the median

The tests in §3 are rank-based and make no distributional assumption, and an interval computed
from a normal approximation would reintroduce the assumption the whole of §3 declines to make.
The bootstrap needs none: resample the Runs with replacement, recompute the statistic, take the
2.5th and 97.5th percentiles of the resampled distribution.

**10 000 resamples, and the resampling is seeded.** The count is the conventional choice for a
percentile interval and is large enough that the Monte Carlo error in the 2.5th percentile is
small beside the sampling error the interval is measuring. The seed matters more: a bootstrap
is stochastic, so an unseeded one produces a different interval on every run and an analysis
that cannot be reproduced, which NFR-REPRO-01 forbids and which would be the one unseeded
random call in the system (`07-cross-cutting-contracts.md` § Randomness Isolation). The
Analyzer derives its generator from the Study's `root_seed`, so re-analysing an archived
Experiment reproduces the interval exactly, as it reproduces everything else.

The median rather than the mean, for the same reason §3 uses rank tests: HPO metric distributions
are frequently skewed, and the mean of a skewed distribution is not the value a reader thinks it
is.

**With few Runs, say so rather than widening quietly.** A bootstrap over five Runs produces an
interval, and the interval is nearly meaningless. Where `n_runs` is below ten the Report states
the count next to the interval so that the reader can discount it, rather than presenting a wide
interval as though width were the only consequence.

---

### 6.3 What is never reported alone

- A mean or median without spread.
- A metric value without the count of Runs behind it.
- A p-value without the effect size that accompanies it (§4.3).
- Any of the above without the scope conditions under which they hold.

Each of these is an omission that makes the number look stronger than it is, which is what
MANIFESTO Principle 29 identifies as the failure mode of benchmarking that serves promotion rather
than knowledge.

---

## 7. Common Methodological Pitfalls

A catalogue of mistakes this methodology is designed to prevent. Each entry states: what the mistake looks like in practice, why it is scientifically invalid, which MANIFESTO principle it violates, and which part of this guide or the system prevents it.

---

### Pitfall 1: Post-Hoc Hypothesis Selection (p-hacking)

**What it looks like:** Running the full analysis, visualizing results, noticing that Algorithm A beats Algorithm B on metric X, then reporting a hypothesis test of "Algorithm A > Algorithm B on metric X" as if it were pre-planned.

**Why it is wrong:** When you select hypotheses from data, the effective significance level is no longer α. With k metrics and m algorithm pairs, you can find a significant result by chance even if there are none. The stated p-value is mathematically invalid.

**MANIFESTO violation:** Principle 16 (planning precedes execution), Principle 29 (objectivity over promotion).

**How this system prevents it:** Hypotheses are stored in the Study record's `pre_registered_hypotheses` field (`docs/03-technical-contracts/01-data-format/01-index.md` §2.3) before any data collection begins. The Analyzer interface (`docs/03-technical-contracts/02-interface-contracts/01-index.md` §4) only tests pre-registered hypotheses in Level 2; post-hoc observations are labeled "exploratory" in the output.

---

### Pitfall 2: Reporting Only Means Without Spread

**What it looks like:** "Algorithm A achieved an average objective value of 0.95 vs. Algorithm B's 0.87" — without standard deviation, IQR, or run count.

**Why it is wrong:** Averages hide variance. An algorithm that achieves 0.95 on 1 run out of 10 and fails catastrophically on 9 others has the same mean as one that consistently achieves 0.95. The reader cannot distinguish them.

**MANIFESTO violation:** Principle 15 ("we report not only averages, but also spread, quantiles, success probabilities").

**Prevention:** §6 Uncertainty Reporting Requirements — the system enforces that `ROBUSTNESS-RESULT_STABILITY` and `RELIABILITY-SUCCESS_RATE` are always reported alongside `QUALITY-BEST_VALUE_AT_BUDGET` in the Standard Reporting Set (`docs/03-technical-contracts/03-metric-taxonomy/01-index.md` §3).

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

**Prevention:** Every system-generated conclusion includes an explicit scope statement: for which Problem Instances and Algorithm Instances the conclusion holds. Extrapolation is labeled and must be separately justified. See `docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md` Step 7 (Scope and Report Conclusions).

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

**Prevention:** `ANYTIME-ECDF_AREA` is mandatory in the Standard Reporting Set (`docs/03-technical-contracts/03-metric-taxonomy/01-index.md` §3). Full Performance Records are required to be stored for all Runs, enabling comparison at any budget level.
