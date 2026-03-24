# ADR-008: TIME-EVALUATIONS_TO_TARGET Exclusion from Standard Reporting Set

<!--
STORY ROLE: Closes the open question of whether the Standard Reporting Set (metric-taxonomy.md §3)
should include TIME-EVALUATIONS_TO_TARGET. The decision establishes what the mandatory four-metric
set covers and why that set is stable — with explicit reasoning about what categories of metric
are appropriate to mandate vs. leave optional.

CONNECTS TO:
  → docs/03-technical-contracts/03-metric-taxonomy/08-standard-reporting-set.md : the set this ADR governs
  → docs/03-technical-contracts/03-metric-taxonomy/03-time-evaluations-to-target.md : the metric considered
  → docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md : the target-free alternative
  → docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md Step 5 : where researchers choose metrics
  → docs/01-manifesto/MANIFESTO.md Principles 14, 29 : the scientific principles at stake
-->

---

**Status:** Accepted

**Date:** 2026-03-24

**Deciders:** Core maintainers, methodology lead

---

## Context

The Standard Reporting Set currently contains four metrics that every study must compute
(MANIFESTO Principle 29, metric-taxonomy.md §3). A `TODO: REF-TASK-0017` in that document
flagged the open question of whether `TIME-EVALUATIONS_TO_TARGET` should be added as a fifth
mandatory metric.

`TIME-EVALUATIONS_TO_TARGET(τ)` requires a pre-specified target value τ set in the Study plan
before data collection begins (MANIFESTO Principle 16, Benchmarking Protocol Step 5). The
question is whether requiring τ imposes an acceptable planning burden or creates risks that
outweigh the scientific value.

---

## Decision

**`TIME-EVALUATIONS_TO_TARGET` is NOT added to the Standard Reporting Set.**

The Standard Reporting Set remains:

| Metric ID | Why Mandatory |
|---|---|
| `QUALITY-BEST_VALUE_AT_BUDGET` | Final quality — the most basic outcome measure |
| `RELIABILITY-SUCCESS_RATE` | Reliability independently of peak quality |
| `ROBUSTNESS-RESULT_STABILITY` | Spread required by MANIFESTO Principle 15 |
| `ANYTIME-ECDF_AREA` | Full performance curve scalar; target-free (ADR-007) |

`TIME-EVALUATIONS_TO_TARGET` is reclassified as a **strongly recommended optional metric**
for research questions specifically about efficiency (reaching acceptable solutions quickly).
It must not be computed without a pre-registered, ecologically valid target τ stored in the
Study record before data collection.

---

## Rationale

### The mandatory metric category has a specific criterion

A metric belongs in the Standard Reporting Set only if it can be computed from any completed
Experiment record without any information beyond what the Study plan already mandates. The
four existing mandatory metrics all satisfy this: they require only Budget, PerformanceRecords,
and a threshold-free comparison of objective values.

`TIME-EVALUATIONS_TO_TARGET` does not satisfy this criterion. It requires a domain-specific
target τ that expresses what counts as an "acceptable solution" for the application at hand.
No universal τ exists across ML hyperparameter optimization tasks: a cross-validation loss of
0.05 is excellent for some models and useless for others.

### Forcing τ degrades scientific quality

Making τ mandatory would create one of two failure modes:

1. **Arbitrary τ**: Researchers set τ to an arbitrary value (e.g., the median final value from
   a pilot run) just to satisfy the system requirement. The resulting metric is meaningless —
   or worse, encodes a specific algorithm's typical outcome, which is a form of the cherry-picking
   bias MANIFESTO Principle 29 is designed to prevent.

2. **Post-hoc τ**: Researchers choose τ after seeing the data (e.g., to make a preferred
   algorithm look more efficient). This is a confirmatory analysis violation (MANIFESTO
   Principle 16), reduces the study to exploratory, and cannot be detected by the system if τ
   is entered retroactively into the Study record.

Neither failure mode is acceptable for a mandatory metric. The Standard Reporting Set must be
a floor that improves report quality; a metric that can be filled with meaningless values
without detection does the opposite.

### ANYTIME-ECDF_AREA already covers the efficiency dimension

`ANYTIME-ECDF_AREA` captures how quickly and reliably an algorithm improves across the full
budget, without requiring a pre-specified target. For any research question about algorithm
efficiency, ECDF_AREA provides a scientifically stronger answer than a single-point
`TIME-EVALUATIONS_TO_TARGET` because it:

- Integrates over all quality levels (not just one pre-specified τ)
- Handles the case where different algorithms favor different regions of the quality range
- Does not require domain knowledge to compute correctly

When a researcher has a specific, ecologically valid τ (e.g., "I need validation loss ≤ 0.03
for this classification task"), `TIME-EVALUATIONS_TO_TARGET(τ)` provides precise, additional
information not captured by ECDF_AREA. That is exactly the condition under which it should be
used — as an opt-in metric with a justified target.

### This does not weaken the reporting requirement

The Standard Reporting Set already mandates `RELIABILITY-SUCCESS_RATE`, which captures a
related but distinct efficiency question: *does the algorithm reliably finish within budget
at all?* The combination of `RELIABILITY-SUCCESS_RATE` + `ANYTIME-ECDF_AREA` provides a
complete target-free picture of reliability and efficiency. Adding `TIME-EVALUATIONS_TO_TARGET`
to this combination would be redundant unless a specific τ is meaningful for the research
question.

---

## Alternatives Considered

### Add with a recommended default τ

**Description:** Define a recommended τ (e.g., 10th percentile of all final values across the
Study) so researchers have a concrete starting point without domain knowledge.

**Why rejected:** A statistical τ derived from the Study's own data is by definition not
ecologically valid — it is a post-hoc threshold set to a convenient value. It would make the
metric computationally possible but scientifically empty, and would appear indistinguishable
in the output from a researcher-specified ecologically valid τ.

---

### Add as mandatory but allow τ = null (skip computation silently)

**Description:** List the metric as mandatory but treat τ = null as a valid state that
produces no output, making the effective reporting requirement conditional.

**Why rejected:** Contradicts the purpose of the Standard Reporting Set. A metric that is
"mandatory unless skipped" is optional. It would also add a conditional branch to the Analyzer
that all four currently mandatory metrics do not require.

---

### Remove TIME-EVALUATIONS_TO_TARGET from the taxonomy entirely

**Description:** Treat it as out of scope because it requires pre-specification.

**Why rejected:** The metric is scientifically valuable when used correctly and has a
well-defined role in the three-level analysis framework. Removing it would leave researchers
without a formalized contract for reporting efficiency on task-specific targets.

---

## Consequences

**Positive:**

- Standard Reporting Set remains computable for any Experiment without additional inputs
- Researchers who have an ecologically valid τ can opt in with full protocol support
- MANIFESTO Principle 29 is enforced without creating an avenue for arbitrary metric values
- The protocol explicitly names `TIME-EVALUATIONS_TO_TARGET` as the right metric when τ is
  available — researchers are guided toward it rather than inventing ad-hoc alternatives

**Negative / Trade-offs:**

- Studies without a pre-specified τ cannot report algorithm efficiency at a specific quality
  threshold; they must rely on ECDF_AREA instead
- Reviewers unfamiliar with this decision may ask "why isn't efficiency-to-target reported?"
  — the answer is documented here and should appear in the metric taxonomy

**Required follow-on actions:**

- `docs/03-technical-contracts/03-metric-taxonomy/08-standard-reporting-set.md`: remove the
  TODO and add a prose note explaining why the set is four metrics and what the criterion for
  inclusion is; add a pointer to TIME-EVALUATIONS_TO_TARGET as the recommended opt-in efficiency
  metric
- `docs/03-technical-contracts/03-metric-taxonomy/03-time-evaluations-to-target.md`: add a note
  in the "When to use" section referencing this ADR and making the ecological validity requirement
  explicit

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/03-metric-taxonomy/08-standard-reporting-set.md` | The set this ADR governs — updated to remove REF-TASK-0017 TODO |
| `docs/03-technical-contracts/03-metric-taxonomy/03-time-evaluations-to-target.md` | The metric under consideration |
| `docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md` | The target-free alternative that covers the efficiency dimension |
| `docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md` Step 5 | Where τ must be declared before data collection |
| `docs/01-manifesto/MANIFESTO.md` Principle 29 | Objectivity over promotion — the principle the Standard Reporting Set enforces |
| `ADR-007-ecdf-area-normalization.md` | Defines ECDF_AREA normalization — the companion metric that makes this decision possible |
