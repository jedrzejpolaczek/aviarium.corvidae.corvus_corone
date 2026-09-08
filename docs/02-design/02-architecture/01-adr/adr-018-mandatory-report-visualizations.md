# ADR-018: Mandatory Report Visualizations

<!--
STORY ROLE: Separates the two visualization sets the corpus conflates: the exploratory set that
every Report must contain, and the algorithm-understanding set that serves the Learner. They
belong to different components in different releases.

CONNECTS TO:
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md §2 : VIZ-L1-01..04
  → docs/02-design/02-architecture/03-c4-leve2-containers/03-report-format-spec.md
  → .../04-c4-leve3-components/07-reporting-engine/03-mandatory-viz-renderer.md : corrected
  → .../04-c4-leve3-components/07-reporting-engine/05-limitations-enforcer.md : corrected
-->

---

**Status:** Accepted

**Date:** 2026-09-08

**Deciders:** Core maintainers, methodology lead

---

## Context

Two mandatory visualization sets are specified.

`02-statistical-methodology.md` §2.1 and `03-report-format-spec.md` require four:
VIZ-L1-01 box plot of final quality, VIZ-L1-02 convergence curves, VIZ-L1-03 ECDF drawn with
`plt.step(where='post')`, and VIZ-L1-04 violin plot, which replaces VIZ-L1-01 when more than
fifty Runs contribute.

`07-reporting-engine/03-mandatory-viz-renderer.md` requires three: `convergence`, `trajectory`
and `sensitivity`. `05-limitations-enforcer.md` encodes that second set in a `REQUIRED_SECTIONS`
constant and refuses to emit a Report without them, which makes the disagreement load-bearing
rather than cosmetic.

Only convergence appears in both.

---

## Decision

**The mandatory set for every Report is VIZ-L1-01 through VIZ-L1-04**, as defined in
`02-statistical-methodology.md` §2.1. `REQUIRED_SECTIONS` in the Limitations Enforcer is
corrected to that set, with VIZ-L1-04 conditional on Run count exactly as the methodology
states.

**Trajectory and parameter sensitivity plots are not report visualizations.** They are
algorithm-understanding output belonging to the Algorithm Visualization Engine, which SRS §1
places outside V1. `03-mandatory-viz-renderer.md` is scoped to the four VIZ-L1 plots; the
algorithm-understanding set moves to the deferred container's documentation.

---

## Rationale

The conflict is not a contest between two candidate sets. It is two different jobs that were
given the same name.

VIZ-L1-01 through VIZ-L1-04 answer a question about a comparison: how did these algorithms
perform on these problems, with what spread and what anytime behaviour. They are derived from
the Level 1 exploratory analysis that MANIFESTO Principle 13 requires before any confirmatory
test, and Principle 23 requires them to accompany the numbers. Every Report needs them because
every Report reports a comparison.

Trajectory and sensitivity plots answer a question about a mechanism: how does this algorithm
move through a search space, and how does it respond to its own parameters. That is the
Learner's question, served by the Algorithm Visualization Engine, and it is deferred with that
container.

Once the two jobs are named separately the disagreement disappears, and neither set has to be
sacrificed.

**Trade-off accepted:** a V1 Report contains no algorithm-mechanism illustration. Researchers
who want one wait for the deferred container.

---

## Alternatives Considered

### Union of both sets

**Description:** Require all seven plots in every Report.

**Why rejected:** Trajectory rendering needs `current_solution` in the PerformanceRecords, which
ADR-002 makes optional and ADR-005 may cap. A mandatory visualization that cannot be produced
from a conforming Study is not mandatory, it is a failure mode. Sensitivity plots additionally
require a `SensitivityReport`, which `01-data-format/03-algorithm-instance.md` marks optional.

---

## Consequences

**Positive:**

- The Reporting Engine and the statistical methodology agree, and the Limitations Enforcer
  enforces the set that the methodology actually requires.
- Every mandatory visualization is producible from data that a conforming Study always has.
- The Algorithm Visualization Engine keeps its own set without contending for the same name.

**Negative / Trade-offs:**

- Two C3 documents change, one of them a constant that reads as implementation-ready.
- `03-mandatory-viz-renderer.md` loses most of its current content to the deferred container.

**Risks:**

- **Risk:** VIZ-L1-04 is conditional, so a naive enforcer treats its absence as a violation on
  studies with fifty or fewer Runs.
  **Mitigation:** The condition is stated in the methodology and must be reproduced in
  `REQUIRED_SECTIONS` as a conditional entry, not a fixed one.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §2.1 | Defines VIZ-L1-01..04 |
| `docs/02-design/02-architecture/03-c4-leve2-containers/03-report-format-spec.md` | Already specifies this set |
| `.../07-reporting-engine/05-limitations-enforcer.md` | `REQUIRED_SECTIONS` corrected |
| `.../07-reporting-engine/03-mandatory-viz-renderer.md` | Scoped to VIZ-L1 by this ADR |
| `adr-011-visualization-technology.md` | Rendering technology for both sets |
