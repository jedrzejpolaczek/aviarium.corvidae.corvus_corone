# Report Output Format Specification

<!--
STORY ROLE: The "what you receive" contract. Every section, visualization, and line
of text that a researcher or practitioner sees when they open a Corvus Corone report
has a documented specification here. A contributor extending the Reporting Engine reads
this document to understand the output contract. A CI test can verify that generated
reports are structurally complete against this spec.

NARRATIVE POSITION:
  C2 (container: Reporting Engine) → this document (output format detail)
  → 04-public-api-contract.md : cc.generate_reports() returns Report objects; artifact_reference
      points to the files described here
  → 02-statistical-methodology.md : three-level analysis that populates the researcher report
  → 03-metric-taxonomy/08-standard-reporting-set.md : the four mandatory metric IDs
  → 07-fr-4.6-reporting-and-visualization.md : FR-20, FR-21, FR-22 — report requirements

CONNECTS TO:
  ← docs/02-design/02-architecture/03-c4-leve2-containers/01-index.md (§ Reporting Engine)
  ← docs/03-technical-contracts/04-public-api-contract.md §CLI Command Surface corvus report
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md §1–§4 (three-level)
  → docs/03-technical-contracts/03-metric-taxonomy/08-standard-reporting-set.md (mandatory metrics)
  → docs/02-design/01-software-requirement-specification/03-functional-requirements/07-fr-4.6-reporting-and-visualization.md

REF-TASK: 0034 — Specify report output format — sections, visualizations, audience language
-->

---

## Design Decisions

### DD-1: Output format — HTML (V1)

**Decision:** Both report types are generated as UTF-8 HTML files using Jinja2 templates.

**Rationale:**
- Matplotlib visualizations embed naturally as SVG `<img>` elements or inline `<svg>`,
  requiring no separate file management.
- HTML is renderable in any browser without proprietary software — satisfies AP-5
  (no proprietary formats) and `CONST-COM-03`.
- Jinja2 templates are already a dependency of the Reporting Engine (IMPL-014); no
  additional build step is required.
- Unlike PDF, HTML is diff-able and inspectable by CI tooling.

**Not an ADR:** The choice follows directly from the existing IMPL-014 design (Jinja2
templates) and `04-public-api-contract.md` (`artifact_reference` returns an HTML path).
No decision record is needed for a choice made explicit in the implementation spec.

**V2 note:** PDF export can be added later by rendering the HTML template through a
headless browser (e.g., Playwright, WeasyPrint) without changing the report structure.

### DD-2: File naming

| Report type | File name pattern |
|---|---|
| `researcher` | `experiment-<experiment_id_prefix>-researcher.html` |
| `practitioner` | `experiment-<experiment_id_prefix>-practitioner.html` |

`<experiment_id_prefix>` is the first 8 characters of the experiment UUID (e.g.,
`3f2e1a00` for experiment ID `3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc`). Both files
are written to the same directory, which is the Reports directory inside the
`LocalFileRepository` root (see `10-file-formats.md §3.2`).

### DD-3: Embedded vs. external visualizations

All visualizations are embedded in the HTML as inline SVG. This keeps each report
a single self-contained file with no external assets to manage.

---

## Shared Requirements (Both Report Types)

The following requirements apply to **both** the Researcher and Practitioner reports.
Violation of any of these is a report generation error that MUST be caught at the
template level (FR-21).

### Scope Statement (MANDATORY)

Every report MUST begin with a scope statement in the following format, immediately
after the report header:

```
Scope: This report covers algorithm(s) [A1, A2, ...] evaluated on problem(s)
[P1, P2, ...] with budget [B] evaluations, [R] repetitions.
Conclusions in this report apply only to these conditions.
```

Where `[A1, A2, ...]` are the algorithm instance IDs, `[P1, P2, ...]` are the
problem instance IDs, `[B]` is the budget, and `[R]` is the repetition count —
all taken from the Study record.

### Limitations Section (MANDATORY)

Every report MUST contain a non-empty Limitations section. A report that reaches
the template rendering step without a limitations section MUST fail with a
`ValueError` (not silently produce a report with an empty section).

Required elements of the Limitations section:

| Element | Required when | Content |
|---|---|---|
| **Scope conditions** | Always | Restate the scope: which algorithms, problems, budgets, and repetition count. |
| **Excluded characteristics** | Always | Identify problem classes and conditions for which no data was collected (e.g., "no deterministic problems were tested", "no dimensionality > 20 was tested"). |
| **Failed run disclosure** | When any Run failed | Count and fraction of failed Runs; note that aggregates are computed over successful Runs only. |
| **Improvement epsilon** | When `Study.improvement_epsilon` is non-null | State the epsilon value and explain that it may suppress records of small improvements. |
| **Record cap** | When `Study.max_records_per_run` is set | State the cap value and note that early-budget behavior may be undersampled. |
| **Generalization warning** | Always | Standard text: "Do not extrapolate conclusions beyond the tested scope. The No Free Lunch theorem implies no universal claims are possible." |

### Prohibited Output (AP-1, AP-6)

Neither report type may contain:

- A global ranking table or "best algorithm" declaration.
- Recommendations unscoped to the tested problem instances.
- Phrases like "Algorithm X is the best", "Algorithm X is recommended for all
  HPO tasks", or any equivalent.
- A summary that presents only positive findings without the limitations section.

Violation detection: the Jinja2 template MUST include a validation step (or the
Reporting Engine MUST run a post-render check) that scans rendered output for
the prohibited patterns and raises a `ReportValidationError` if found.

---

## Researcher Report

**Audience:** Scientists and engineers conducting or reviewing benchmarking studies.
Statistical terminology is expected and appropriate.

**Generated by:** `cc.generate_reports(experiment_id)` → `Report(report_type="researcher")`

### Section Structure

The sections appear in the following order. All sections are mandatory unless
noted `[conditional]`.

| # | Section | Content summary |
|---|---|---|
| 1 | Header | Report title, experiment ID, generation timestamp, library version |
| 2 | Scope Statement | Algorithms, problems, budget, repetitions — see §Shared Requirements |
| 3 | Study Configuration | Study name, research question, seed strategy, sampling strategy, pre-registered hypotheses |
| 4 | Run Summary | Total runs, completed, failed; failed run IDs listed |
| 5 | Level 1: Exploratory Data Analysis | Mandatory visualizations VIZ-L1-01..04; observations |
| 6 | Level 2: Confirmatory Analysis | Statistical test results table; pre-registration labels |
| 7 | Level 3: Practical Significance | Effect size table; scoped conclusions |
| 8 | Standard Reporting Set | Metric table for all four mandatory metrics |
| 9 | Limitations | Mandatory — see §Shared Requirements |
| 10 | Reproducibility Metadata | [conditional] Git hash, platform, library version, all seeds |

### Section 3: Study Configuration

```
Research Question:  [study.research_question]
Study Name:         [study.name]
Budget:             [study.budget] evaluations per Run
Repetitions:        [study.repetitions] per (algorithm, problem) pair
Seed Strategy:      [study.seed_strategy]
Sampling Strategy:  [study.sampling_strategy]
Pre-Registered Hypotheses:
  H1: [hypothesis text] (test: [test_type])
  H2: ...
```

If `pre_registered_hypotheses` is empty: "No hypotheses were pre-registered for
this study. All comparisons are exploratory (see Level 2)."

### Section 4: Run Summary

```
Total Runs:     [N]  (= [problems] problems × [algorithms] algorithms × [repetitions] reps)
Completed:      [N_completed]
Failed:         [N_failed]
```

If `N_failed > 0`, list failed Run IDs and their `failure_reason` values.
Note explicitly: "Aggregates are computed over [N_completed] successful Runs only."

### Section 5: Level 1 — Exploratory Data Analysis

Contains all mandatory Level 1 visualizations (§Mandatory Visualizations) followed by
a free-text observations block rendered from the `AnalysisReport` object.

**Observations block format:**

```
Observations (exploratory — not conclusions):
- [Observation 1: e.g., "CMA-ES shows higher variance on problem sphere-d10-noise-gaussian-0.1"]
- [Observation 2: ...]

Candidate hypotheses for future studies:
- [If any patterns suggest future investigations — not tested in this study]
```

The system generates this block from the `AnalysisReport.exploratory_observations`
field. Observations are labeled "exploratory — not conclusions" to satisfy CONST-SCI-06.

### Section 6: Level 2 — Confirmatory Analysis

One table per pre-registered hypothesis:

```
H1: [hypothesis text]  [PRE-REGISTERED]
Test: [test name] (e.g., Wilcoxon signed-rank, two-sided)
Correction: [correction method] (e.g., None — single hypothesis)
Significance threshold: α = [value]

Problem                          Statistic  p-value  Decision           Conclusion scope
sphere-d10-noise-gaussian-0.1    W = 312    0.031    Reject H0 (p<α)   sphere-d10-noise-gaussian-0.1,
                                                                         CMA-ES vs Nelder-Mead,
                                                                         budget=10000, n=30 runs
```

Any comparisons not in `pre_registered_hypotheses` are placed in a separate
"Exploratory Comparisons" subsection, labeled `[EXPLORATORY — not pre-registered]`.
These are clearly distinct from confirmatory results.

Effect sizes are **not** in this section — they appear in Level 3.

### Section 7: Level 3 — Practical Significance

One table per comparison from Level 2:

```
H1: [hypothesis text]

Problem                          Effect size  Magnitude  Interpretation
sphere-d10-noise-gaussian-0.1    δ = 0.41     medium     Medium practical difference.
                                                          CMA-ES achieves meaningfully lower
                                                          objective values on this problem.
```

Effect size measures: Cliff's delta (δ) for non-parametric tests, Cohen's d for
parametric. Magnitude thresholds: δ — negligible < 0.147 ≤ small < 0.33 ≤ medium <
0.474 ≤ large. These follow Romano et al. (2006).

**Required warning:** "Effect sizes are interpreted in the context of the tested
problem class only. A 'large' effect does not imply practical significance for
problems outside the tested scope."

### Section 8: Standard Reporting Set

One table per (problem, algorithm) cell:

```
Problem: sphere-d10-noise-gaussian-0.1

Metric                          CMA-ES (n=30)                    Nelder-Mead (n=30)
                                mean   median  stdev  q25   q75  mean   median  stdev  q25   q75
QUALITY-BEST_VALUE_AT_BUDGET    0.023  0.019   0.011  0.015 0.027  0.087  0.081  0.023  0.066 0.102
RELIABILITY-SUCCESS_RATE        1.000  —       —      —     —      0.933  —      —      —     —
ROBUSTNESS-RESULT_STABILITY     0.011  —       —      —     —      0.023  —      —      —     —
ANYTIME-ECDF_AREA               0.912  0.921   0.041  0.889 0.938  0.774  0.781  0.062  0.739 0.815
```

`RELIABILITY-SUCCESS_RATE` and `ROBUSTNESS-RESULT_STABILITY` are scalar per algorithm
per problem — no distribution statistics apply; `—` is correct for their stdev/quantile
columns.

### Section 10: Reproducibility Metadata [conditional]

Present when the study was run with `LocalFileRepository` (V1). Contains:

```
Library version:    corvus-corone X.Y.Z
Python version:     3.13.x
Platform:           [OS, architecture]
Run directory:      [absolute path to run data]
Seeds used:         [list of seeds or seed strategy description]
Git hash:           [hash of library code, if available]
```

This section fulfils MANIFESTO Principles 19–21 (full reproducibility, versioning).

---

## Practitioner Report

**Audience:** ML engineers or data scientists selecting an algorithm for a project.
Statistical terminology is avoided. Conclusions are expressed in practical terms.

**Generated by:** `cc.generate_reports(experiment_id)` → `Report(report_type="practitioner")`

### Section Structure

| # | Section | Content summary |
|---|---|---|
| 1 | Header | "Algorithm Comparison Summary", experiment ID, generation date |
| 2 | Scope Statement | Problems, algorithms, budget — in plain language |
| 3 | Study Context | One paragraph: what was tested, why it matters, what was not tested |
| 4 | Key Findings | Per-problem findings in plain language; no p-values |
| 5 | Visualizations | VIZ-L1-02 (convergence curves) and VIZ-L1-03 (ECDF) only |
| 6 | How to Use These Results | Matching problem characteristics; when not to use |
| 7 | Limitations | Mandatory — plain-language version of researcher report limitations |

### Section 2: Scope Statement (Practitioner version)

```
This summary covers [N] algorithms evaluated on [M] problem instances,
each run [R] times with a budget of [B] evaluations per run.
Problem instances tested: [plain-language description of each, e.g.,
"Sphere function, 10 dimensions, Gaussian noise σ=0.1"].
```

### Section 3: Study Context

One paragraph written by the Reporting Engine from structured fields:

```
This study compared [algorithm names] on [problem class description].
The study was designed to investigate: [research_question].
It does not cover [inferred exclusions from scope statement].
```

### Section 4: Key Findings

Plain-language summary per (problem, algorithm) cell. Language rules:

**Allowed:**
- "Algorithm X performed consistently across repetitions on [problem]."
- "Algorithm X reached [quality level] on [problem] within [budget]."
- "Algorithm X showed higher variability than Algorithm Y on [problem]."

**Prohibited:**
- "Algorithm X is recommended." (unscoped recommendation)
- "Algorithm X is better." (comparative without scope)
- "Algorithm X is statistically significant." (unexplained statistical term)
- "Algorithm X is the best algorithm." (ranking — AP-1)

Each finding MUST include a scope parenthetical:
"(result valid for [problem ID], budget=[B], [R] repetitions)"

### Section 6: How to Use These Results

Mandatory guidance text:

```
These results apply to the specific problem characteristics listed above.
Before selecting an algorithm based on this report:
  1. Verify your problem's dimensionality, noise level, and budget match
     the tested conditions.
  2. If your conditions differ significantly, these results may not apply.
     Look for studies that match your conditions more closely.
  3. This report provides evidence to inform your decision — it does not
     make the decision for you (see Scope and Limitations).
```

---

## Mandatory Visualizations

All four visualizations are generated automatically for every completed Experiment.
VIZ-L1-01, VIZ-L1-02, and VIZ-L1-03 appear in the Researcher report. VIZ-L1-02 and
VIZ-L1-03 appear in the Practitioner report. VIZ-L1-04 is generated for the Researcher
report only when `Study.repetitions > 50`.

### VIZ-L1-01: Box Plot of Final Quality

**What it shows:** Distribution of `QUALITY-BEST_VALUE_AT_BUDGET` across repetitions,
one box per (algorithm, problem) cell. Shows median, IQR, whiskers (1.5×IQR), and
outliers.

**Axes:**
- X-axis: Algorithm instance IDs, grouped by problem instance. One group per problem.
- Y-axis: Objective value at budget exhaustion (lower is better for minimization problems).
  Y-axis label: `Best objective value at budget [B]`.

**Interpretation guidance (in report caption):**
"Boxes show the interquartile range of final objective values across [R] repetitions.
A narrower box indicates more consistent results. Overlapping boxes suggest no
practically meaningful difference between algorithms on this problem."

**Implementation note:** One figure per problem instance (not one figure per metric).
All algorithms for the same problem are shown side by side. If more than 6 algorithms
are compared, a violin plot (VIZ-L1-04) replaces the box plot regardless of sample size.

**Appears in:** Researcher report §Level 1 EDA.

---

### VIZ-L1-02: Convergence Curves

**What it shows:** Best-so-far objective value as a function of evaluation number.
For each algorithm: the median curve over repetitions (solid line) and the IQR band
(shaded region between 25th and 75th percentile).

**Axes:**
- X-axis: Evaluation number (1 to `Study.budget`). Log scale if `budget > 100`.
  Label: `Evaluations`.
- Y-axis: Best-so-far objective value. Label: `Best objective value (best so far)`.

**One figure per problem instance.** All algorithms overlaid on the same axes with
distinct colors and a legend.

**Interpretation guidance (in report caption):**
"Each line is the median best-so-far value across [R] repetitions. The shaded band
shows the interquartile range. A lower curve reaching its minimum earlier indicates
faster convergence. Crossing curves indicate that relative performance depends on
budget — compare at the budget relevant to your application."

**Implementation note:** Convergence curves require PerformanceRecord data with
`evaluation_number` and `best_so_far` fields. If `Study.sampling_strategy` is not
`"every_evaluation"`, intermediate points are interpolated using the method specified
in `adr-003-anytime-curve-interpolation.md`.

**Appears in:** Researcher report §Level 1 EDA; Practitioner report §Visualizations.

---

### VIZ-L1-03: Empirical Cumulative Distribution Function (ECDF)

**What it shows:** For each algorithm, the fraction of Runs that achieved a given
quality target or better, plotted as a step function over target quality values.
Aggregated across all problem instances in the study (if multiple problems are tested).

**Implementation:** `matplotlib.pyplot.step(x, y, where='post')` — the `where='post'`
parameter is mandatory so that the step occurs at the exact quality threshold, not
one step before.

**Axes:**
- X-axis: Quality target value (objective value threshold). Label: `Quality target (objective value)`.
- Y-axis: Fraction of runs achieving the target. Range [0, 1]. Label: `Fraction of runs`.

**Interpretation guidance (in report caption):**
"Each curve shows the fraction of Runs (out of [R] repetitions × [M] problems) that
reached a given quality target. A curve shifted left and up indicates better overall
performance — more Runs reach better quality values. An algorithm with a flatter
curve shows high variability. The area under the ECDF curve corresponds to the
`ANYTIME-ECDF_AREA` metric."

**Appears in:** Researcher report §Level 1 EDA; Practitioner report §Visualizations.

---

### VIZ-L1-04: Violin Plot [conditional]

**When generated:** When `Study.repetitions > 50`, the violin plot replaces or
supplements VIZ-L1-01 (box plot) in the Researcher report. For large samples, violins
reveal distribution shape (multimodality, skew) that boxes hide.

**What it shows:** Kernel density estimate of the `QUALITY-BEST_VALUE_AT_BUDGET`
distribution per (algorithm, problem) cell, mirrored to form a symmetric shape.
Inner box shows IQR; center line shows median.

**Axes:** Same as VIZ-L1-01.

**Interpretation guidance (in report caption):**
"Violin shapes show the full distribution of final objective values across [R]
repetitions. A narrow violin indicates concentrated results; a bimodal violin (two
bumps) indicates two distinct performance modes, which warrants further investigation.
Width at any point is proportional to the density of runs achieving that quality."

**Appears in:** Researcher report §Level 1 EDA (when `repetitions > 50`).

---

## Audience Language Rules

### Researcher report — permitted and required vocabulary

| Concept | Permitted phrasing | Prohibited phrasing |
|---|---|---|
| Statistical significance | "statistically significant at α=0.05 (p=0.031)", "we fail to reject H0 (p=0.23)" | "significant" without threshold; "proves" |
| Effect size | "medium practical effect (Cliff's δ=0.41)" | "large difference" without measure |
| Conclusion | "On sphere-d10-noise-gaussian-0.1, CMA-ES achieved [X]. This conclusion is scoped to budget=10000 and 30 repetitions." | "CMA-ES is better" (unscoped) |
| Uncertainty | "median ± IQR", "95% CI [a, b]" | mean alone without spread |

### Practitioner report — permitted and prohibited vocabulary

| Concept | Permitted phrasing | Prohibited phrasing |
|---|---|---|
| Performance difference | "performed consistently", "showed higher variability", "reached [quality] within [budget]" | "statistically significant", "p-value", "effect size" |
| Comparison | "more reliable across repetitions on [problem]" | "better", "superior", "recommended" (unscoped) |
| Scope | "for the tested conditions (see scope above)" | any claim without scope qualifier |
| Uncertainty | "results varied across repetitions" | no acknowledgment of variance |
| Ranking | Not permitted in any form | "best", "winner", "ranked first" |

---

## Relation to Other Documents

| Document | Relationship |
|---|---|
| `04-public-api-contract.md` | `cc.generate_reports()` produces the reports specified here; `Report.artifact_reference` points to the HTML files described in §DD-2 |
| `02-statistical-methodology.md §1–§4` | The three-level framework in §§Level 2 and 3 of the researcher report is the operationalization of that document |
| `03-metric-taxonomy/08-standard-reporting-set.md` | §Standard Reporting Set uses exactly the four mandatory metric IDs from that document |
| `07-fr-4.6-reporting-and-visualization.md` | FR-20 (two reports per experiment), FR-21 (mandatory limitations), FR-22 (raw data export) are all satisfied by this spec |
| `02-const-scientific.md` | CONST-SCI-01 (no rankings), CONST-SCI-05 (limitations section), CONST-SCI-06 (scoped conclusions) — all enforced at the template level |
| `adr-003-anytime-curve-interpolation.md` | VIZ-L1-02 convergence curves interpolate sparse PerformanceRecords using the method decided there |
