# ADR-007: ECDF Area Normalization Bounds

<!--
STORY ROLE: Defines how ANYTIME-ECDF_AREA is normalized so that the scalar lies in [0, 1].
The normalization decision is separate from the interpolation decision (ADR-003) because it
concerns the reference frame (what counts as "worst" and "best"), not how gaps in the data
are filled. Different normalization choices produce incomparable numbers from identical runs,
so this must be a single documented decision.

CONNECTS TO:
  → docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md : metric definition
  → ADR-003-anytime-curve-interpolation.md : LOCF interpolation used before normalization
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md §5
  → docs/03-technical-contracts/03-metric-taxonomy/08-standard-reporting-set.md
-->

---

**Status:** Accepted

**Date:** 2026-03-24

**Deciders:** Core maintainers, methodology lead

---

## Context

To produce a scalar in $[0, 1]$, the area under the anytime best-so-far curve must be divided
by a reference interval that represents the full possible range of objective values. This
reference interval requires a `y_min` (best reachable) and `y_max` (worst reachable).

Two candidate approaches exist:

1. **Known-optimum normalization** — set `y_min` to the known global optimum of the objective
   function. Common in synthetic benchmark suites (COCO, IOHprofiler) where the optimum is
   provided by construction.

2. **Empirical normalization** — set `y_min` to the best value observed across all Runs in
   the Study at their final Budget evaluation; set `y_max` to the worst value observed across
   all Runs at their first recorded evaluation.

The primary target domain for Corvus Corone is real ML hyperparameter optimization tasks
(cross-validation loss, held-out accuracy, etc.) where the global optimum is unknown and
unknowable without exhaustive search. Known-optimum normalization is therefore unavailable
for the majority of studies this system is designed to support.

---

## Decision

ANYTIME-ECDF_AREA uses **empirical normalization**:

> `y_max` = maximum `b_r(1)` across all Runs in the Problem–Algorithm cell (worst initial value)
> `y_min` = minimum `b_r(B)` across all Runs in the Problem–Algorithm cell (best final value)

where `b_r(k)` is the best-so-far value of Run `r` at evaluation `k`, reconstructed using LOCF
(ADR-003). $B$ is the Budget of the Study.

The normalization is computed **per Problem–Algorithm cell** (i.e., separately for each
combination of Problem Instance and Algorithm Instance within the Study). Cross-problem
aggregation uses arithmetic mean of per-cell ECDF_AREA values (see §7 of
`docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md`).

---

## Rationale

### Why empirical normalization is the only viable choice for real ML tasks

ML objective functions (validation loss, negative accuracy, etc.) have no analytically known
optimum. Using an empirical bound is not a concession — it is the only well-defined reference
frame available. The resulting scalar measures *how much of the observable improvement range
was realized, and how early*, which is a scientifically meaningful quantity.

### Why per-cell bounds, not study-wide bounds

Study-wide bounds would conflate normalization across problems with different objective value
scales. A problem whose objective ranges in $[0.01, 0.05]$ and a problem whose objective
ranges in $[0.3, 0.9]$ would not contribute equally to a study-wide normalized area, making
cross-problem aggregation meaningless. Per-cell bounds ensure each problem contributes on the
same $[0, 1]$ scale.

### Why this means values are not comparable across studies

Empirical bounds are computed from the Runs in a specific Study. Two studies that differ in
their algorithm portfolio, Run count, or Budget will produce different `y_min`/`y_max` values
even on the same Problem Instance. Therefore:

- ECDF_AREA values **within** a Study are comparable across algorithms and problems.
- ECDF_AREA values **across** Studies are not directly comparable unless both studies used
  identical bounds (e.g., derived from the same reference Run set).

This limitation is mandatory disclosure in every Report (FR-21). The Report limitations
section must include: *"ANYTIME-ECDF_AREA values are normalized to empirical bounds from
this Study and are not directly comparable to values reported in other Studies."*

---

## Alternatives Considered

### Known-optimum normalization

**Description:** Use the function's known global optimum as `y_min`.

**Why rejected:** Unavailable for real ML tasks. Producing a metric that only works on
synthetic benchmarks would contradict the system's primary design target and force researchers
to use different metrics for synthetic vs. real studies, undermining cross-study comparison
within the same system.

**Under what conditions reconsidered:** A future extension for synthetic-only study types
could offer known-optimum normalization as an opt-in mode, declared in the Study plan and
flagged in the Report. This would require a separate Study type with a `known_optimum` field
in the Problem Instance schema.

---

### Study-wide empirical bounds

**Description:** Compute a single `y_max`/`y_min` from all Runs across all problems in the
Study.

**Why rejected:** Produces an ECDF_AREA value that depends on which problems are included in
the Study. Adding or removing a problem would change the ECDF_AREA of all other problems.
Per-cell bounds are self-contained and reproducible from the cell's own data.

---

### Fixed percentile bounds

**Description:** Use the 5th/95th percentile of all observed values as bounds, to reduce
sensitivity to outliers.

**Why rejected:** Produces values outside $[0, 1]$ for runs at the extremes. The empirical
min/max is already computed from the same Runs contributing to the metric; it is not an
external reference that could be distorted by unrelated data.

---

## Consequences

**Positive:**

- ANYTIME-ECDF_AREA is computable for any real ML study without external oracle
- Per-cell normalization makes cross-algorithm comparison within a study scientifically sound
- The formula is fully determined by the PerformanceRecords of the cell, with no external
  inputs required

**Negative / Trade-offs:**

- Values from different studies are not directly comparable — must be disclosed in every Report
- A study with only 1 Run per cell has trivial `y_min = y_max` — the metric is undefined;
  the Analyzer must raise an error for cells with fewer than 2 Runs

**Risks:**

- **Risk:** A researcher compares ECDF_AREA values across studies without reading the
  limitations section.
  **Mitigation:** FR-21 mandates the limitations disclosure in every Report. The metric
  definition in `07-anytime-ecdf-area.md` includes an explicit cross-study incomparability
  warning.
- **Risk:** The worst initial value `y_max` is an outlier from a crashed Run.
  **Mitigation:** ADR-004's improvement epsilon means the first recorded value is always a
  valid objective evaluation. Crashed Runs that produce `NaN` or `inf` are filtered by the
  Analyzer before bounds computation (validation rule in the Analyzer interface).

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md` | Metric definition — computation procedure references this ADR |
| `ADR-003-anytime-curve-interpolation.md` | LOCF interpolation applied before normalization |
| `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md §5` | Anytime analysis section; ECDF visualization and area metric |
| `docs/03-technical-contracts/03-metric-taxonomy/08-standard-reporting-set.md` | ANYTIME-ECDF_AREA is mandatory in every Study Report |
| `docs/02-design/01-software-requirement-specification/03-functional-requirements/07-fr-4.6-reporting-and-visualization.md` | FR-21 mandates limitations disclosure covering this ADR's cross-study warning |
