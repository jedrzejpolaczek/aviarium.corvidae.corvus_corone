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

> **`TODO: REF-TASK-0019`** — Specify the exact required visualizations for Level 1 (box plots,
> violin plots, ECDFs, performance curves) once the reporting module is designed. Owner: analysis
> lead. Acceptance: system automatically generates all required Level 1 visualizations from
> Run data with no additional configuration from the researcher.

> **`TODO: REF-TASK-0020`** — Specify the statistical test selection procedure for Level 2
> (decision tree: parametric vs non-parametric, paired vs unpaired, multiple testing correction).
> Owner: methodology lead. Acceptance: documented in §3 of this file with references to
> Bartz-Beielstein et al. (2020) and implemented in the Analyzer interface.

---

## 2. Level 1: Exploratory Data Analysis

<!--
  Purpose:
    Understand the data before drawing conclusions.
    Identify patterns, anomalies, and potential hypotheses.
    Outputs of this level are OBSERVATIONS, not conclusions.

  Required visualizations:
    For each metric across all runs, produce:
    - [Visualization type 1]: what does it show? when is it most useful?
    - [Visualization type 2]: hint — box plots, violin plots, ECDFs are common choices
    - Performance curves: evolution of best objective value over evaluations
      → see specs/metric-taxonomy.md §2 ANYTIME metrics for curve-level metrics

  What to look for:
    - Outlier runs: are there runs with anomalous performance? Are they meaningful or errors?
    - Distribution shape: is the data symmetric, skewed, multimodal? (guides Level 2 test selection)
    - Budget sensitivity: does relative performance change at different evaluation counts?
    - Problem-level variation: do algorithms differ more within a problem or across problems?

  What NOT to do at this level:
    - Do not compute p-values from exploratory visualizations
    - Do not state conclusions — state observations that motivate hypotheses
    - Do not select which algorithms to compare post-hoc based on who looks good

  Output format:
    Exploratory analysis produces a narrative: observations + candidate hypotheses.
    → These become inputs to Level 2, where pre-registered hypotheses are tested.
-->

---

## 3. Level 2: Confirmatory Analysis

<!--
  Purpose:
    Formally test the pre-registered hypotheses using appropriate statistical tests.
    Outputs of this level are DECISIONS (reject / fail to reject hypothesis) with quantified uncertainty.

  ### Test Selection
  How to choose the right statistical test:

  Decision criteria:
    - Sample size: are there enough runs for parametric tests? (general guideline: n ≥ 30, but context-dependent)
    - Distribution: is the data approximately normal? (check from Level 1)
    - Data structure: are comparisons paired (same problem instances) or unpaired?
    - Number of groups: two algorithms, or multiple?

  Provide a decision tree or table:
    | Condition                          | Recommended test       | Alternative           |
    |------------------------------------|------------------------|-----------------------|
    | Two algorithms, paired, normal     | [test name]            | [non-parametric alt]  |
    | Two algorithms, paired, non-normal | [non-parametric test]  | [bootstrap method]    |
    | Multiple algorithms                | [omnibus test]         | [post-hoc adjustment] |

  Hint: in HPO benchmarking, distributions are often non-normal and sample sizes moderate.
  Non-parametric tests (Wilcoxon signed-rank, Friedman) are commonly appropriate.
  → Reference Bartz-Beielstein et al. (2020) for specific guidance.

  ### Multiple Testing Correction
  When is correction required?
    - When testing more than one hypothesis in a single study
    - When selecting the "best" algorithm from k > 2 candidates

  Which correction method to use?
    Hint: Bonferroni is conservative; Benjamini-Hochberg (BH/FDR) is less conservative.
    When to prefer each? → this is a methodological decision; document it explicitly.

  ### Significance Threshold
    What p-value threshold is used? (commonly α = 0.05, but justify your choice)
    Is the threshold adjusted for multiple testing before or after the test?
    → This must be declared in the Study's pre_registered_hypotheses before analysis.

  Output format:
    For each hypothesis: test name, test statistic, p-value, reject/fail-to-reject, correction applied.
    Conclusion scope: explicitly state for which problems, algorithms, and budgets this holds.
    → conclusion_scope field in StatisticalTestResult (specs/interface-contracts.md §4)
-->

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

**Prevention:** §3 Multiple Testing Correction — the system applies correction whenever more than one hypothesis is tested. The correction method must be declared in the Study plan.

> **`TODO: REF-TASK-0020`** — Specify which correction methods (Bonferroni, BH/FDR, etc.) are
> supported and when to prefer each. Reference §3 once filled.

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
