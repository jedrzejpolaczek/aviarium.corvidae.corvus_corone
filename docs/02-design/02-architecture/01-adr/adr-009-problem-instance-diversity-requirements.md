# ADR-009: Minimum Problem Instance Diversity Requirements

<!--
STORY ROLE: Establishes the quantitative floor below which a study's problem set is too
narrow for the conclusions it claims. Without this, a researcher can test 2 algorithms on
a single problem and the system produces a report — a scientific validity failure.

The requirements here are minimums, not ideals. They are set at the lowest values where
the statistical machinery (§3 of statistical-methodology.md) remains valid and where the
diversity dimension (noise vs. deterministic, low vs. high dimensionality) is at least
represented once. They are not "good practice" targets — researchers should exceed them.

CONNECTS TO:
  → docs/02-design/01-software-requirement-specification/03-functional-requirements/02-fr-4.1-problem-repository.md : FR-05 and FR-06
  → docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md Step 3
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md §3.4 (Wilcoxon minimum P≥5)
  → docs/03-technical-contracts/01-data-format/02-problem-instance.md : schema fields checked
  → docs/01-manifesto/MANIFESTO.md Principles 3, 4, 5, 6
-->

---

**Status:** Accepted

**Date:** 2026-03-24

**Deciders:** Core maintainers, methodology lead

---

## Context

MANIFESTO Principles 4–6 require Problem Instance sets to be representative, diverse, and
free from selection bias. Principle 3 states that conclusions refer exclusively to actually
tested instances. These principles are satisfied by design intent, but the system must also
enforce a quantitative minimum so that claims such as "Algorithm A performs well on this
problem class" cannot arise from a study with a single problem or a homogeneous set.

Two independent constraints produce the minimum requirements:

1. **Statistical validity:** The Wilcoxon signed-rank test (statistical-methodology.md §3.4)
   requires $P \geq 5$ Problem Instances to have sufficient power. Below 5, the test cannot
   distinguish signal from noise at standard α levels, and its result must be labeled
   "exploratory" regardless of p-value. The statistical floor and the scientific floor are
   therefore the same number.

2. **Diversity coverage:** Two structural dimensions — dimensionality range and
   noise/deterministic character — are documented as fundamental axes of HPO problem
   variation in the benchmarking literature (Bartz-Beielstein et al. 2020 §2). A study that
   samples only one value on either axis cannot claim its conclusions hold for the stated
   problem class; it has tested only one point in that space.

---

## Decision

A Study plan is valid with respect to problem diversity if and only if all of the following
hold at the time the Experiment begins (pre-registration gate):

### D-1: Minimum instance count

$$\lvert \text{problem\_instances} \rvert \geq 5$$

Five is the floor imposed by the Wilcoxon signed-rank test's power requirement. Fewer than 5
instances means confirmatory analysis (Level 2) cannot be conducted; the study is
exploratory by construction.

### D-2: Minimum dimensionality spread

The study must include Problem Instances from **at least 2 of the 3 dimensionality ranges**:

| Range name | Criterion |
|---|---|
| Low-dimensional | `dimensions` ≤ 5 |
| Medium-dimensional | 6 ≤ `dimensions` ≤ 20 |
| High-dimensional | `dimensions` > 20 |

A study that covers only one range (e.g., all problems have `dimensions` in 2–4) produces
conclusions valid only for that range. The system must reject or warn — it does not
extrapolate to uncovered ranges.

*The range boundaries (5, 20) are conventional breakpoints in the HPO literature. They are
not theoretically exact; future studies may provide empirical justification for adjusting
them. Any adjustment requires a new ADR.*

### D-3: Noise coverage

The study must include **at least 1 Problem Instance with `objective.noise_level =
"stochastic"`** and **at least 1 with `objective.noise_level = "deterministic"`**.

Noise fundamentally alters algorithm behavior (MANIFESTO Principle 5). An algorithm that
performs well only on deterministic problems and one that performs well only on noisy ones
are indistinguishable if the study includes only one class. The noise/deterministic axis
must be represented so the scope statement is checkable.

---

## Enforcement

Validation runs at two points:

1. **Study plan submission** (`StudyOrchestrator.validate_study()` or equivalent):
   Violations produce a `DiversityValidationError` with a message that names the specific
   rule(s) failed and the current count/coverage. The Study is not persisted.

2. **Experiment start** (`StudyOrchestrator.run()`): Re-validated immediately before
   execution begins. If a Problem Instance record changed between submission and start
   (e.g., its `noise_level` was corrected), the constraint is re-checked. Failure blocks
   execution.

**Error message format:**

```
DiversityValidationError: Study '<id>' fails diversity requirements:
  - D-1: requires ≥5 problem instances; found 3
  - D-3: requires at least 1 stochastic problem; found 0
```

Any rule that passes is omitted from the error message.

---

## Rationale

### Why 5 and not more

The minimum is the lowest value where the primary statistical test (Wilcoxon signed-rank) is
valid at standard power levels for detecting a medium effect size ($r = 0.3$). Setting the
floor higher (e.g., 10) would be scientifically conservative but would block studies on
specialist problem classes where fewer distinct instances exist — an over-constraint not
justified by the statistical requirement.

The minimum is not a recommendation. Studies with 5 instances produce weak conclusions even
if valid. Researchers should include as many representative instances as their compute budget
permits; 5 is a hard floor, not a target.

### Why dimensionality ranges and not a continuous spread test

A continuous diversity metric (e.g., standard deviation of log-dimensions across instances)
requires an arbitrary threshold and is harder to explain to researchers. Three named ranges
provide clear, checkable criteria that correspond to real behavioral differences in HPO
algorithms (search efficiency scales differently across these ranges). The requirement is
one representable predicate: "at least 2 ranges covered."

### Why the noise/deterministic axis specifically

All other structural dimensions (variable types, landscape modality) are either expressible
through dimensionality (continuous vs. integer vs. categorical mix) or difficult to verify
mechanically from the schema. Noise level is directly captured in a binary field
(`objective.noise_level`) and represents the highest-impact structural variation: algorithms
designed for deterministic problems routinely underperform on noisy ones and vice versa.
Requiring at least one instance of each class is the minimum observable check for this axis.

### Why a system block and not a researcher warning

The system enforces this as a validation error, not a warning, because warnings in study
design tooling are routinely ignored. A study that records results but then cannot produce
confirmatory analysis (because P < 5) has wasted compute and produced a misleading report
structure. Blocking before execution prevents that outcome.

Researchers with legitimate reasons to use fewer instances (e.g., a specialized spike study
on a single-problem class) must declare their study type as `exploratory` in the Study plan's
`study_type` field. An exploratory study is exempt from D-1 through D-3 but the Analyzer
will not produce Level 2 (Confirmatory) output for it.

---

## Alternatives Considered

### No floor — rely on researcher judgment

**Why rejected:** MANIFESTO Principle 29 requires the system to prevent metric cherry-picking.
Allowing a single-instance study to produce a researcher report with conclusions violates the
same anti-cherry-picking principle applied to problem selection. The system cannot evaluate
researcher intent; it can only check observable properties of the problem set.

---

### Higher floor (e.g., 10 instances mandatory)

**Why rejected:** Over-constrains specialist or exploratory studies where a researcher has
carefully selected a small representative set. The scientific justification for a specific
higher floor does not exist without empirical data from real studies — that data will come
from post-V1 use. The 5-instance floor is grounded in a specific, citable statistical
requirement (Wilcoxon power); raising it without a comparable grounding is arbitrary.

*Under what conditions reconsidered:* After empirical data from real studies, an ADR may
raise the floor for specific study types (e.g., "algorithm comparison studies" vs. "ablation
studies"). That distinction requires the study type taxonomy to exist first.

---

### Check at analysis time, not at study submission

**Why rejected:** A researcher who executes 50 runs on 4 problems has spent compute budget
on a study the system will refuse to analyze. Checking at submission time is strictly better
for the researcher while producing the same scientific outcome.

---

## Consequences

**Positive:**

- Every study that passes validation can produce a valid Wilcoxon test in Level 2 analysis
- Scope statements in reports are checkable against the actual problem set diversity
- Researchers who want to study single-problem behavior are guided to declare `exploratory`
  and receive appropriate output framing

**Negative / Trade-offs:**

- Studies with fewer than 5 instances must be declared exploratory; they produce no
  confirmatory analysis output
- The dimensionality range boundaries (5, 20) may not align with all domains; researchers
  studying only continuous 2-dimensional search spaces would need to declare exploratory
- Validation adds a check to StudyOrchestrator; error handling must be tested for each rule

**Risks:**

- **Risk:** Researchers register dummy problems to satisfy the count without meaningful
  diversity.
  **Mitigation:** The D-2 and D-3 checks are on schema fields (`dimensions`,
  `noise_level`), not on problem count alone. Registering 5 copies of the same problem
  with different names still fails D-2 if they all have the same dimensionality range.
  The provenance field and reviewer scrutiny cover the remaining surface.

- **Risk:** The 5-instance floor is too restrictive for some legitimate study types.
  **Mitigation:** The `study_type = "exploratory"` escape valve exempts from D-1 through D-3.
  This is documented and expected to be used for feasibility spikes.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/02-design/01-software-requirement-specification/03-functional-requirements/02-fr-4.1-problem-repository.md` | FR-05 and FR-06 formalize D-1 through D-3 as system requirements |
| `docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md` Step 3 | Protocol guidance for problem selection references these requirements |
| `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §3.4 | Wilcoxon P≥5 power requirement — the statistical grounding for D-1 |
| `docs/03-technical-contracts/01-data-format/02-problem-instance.md` | `dimensions` and `objective.noise_level` fields checked by D-2 and D-3 |
| `docs/01-manifesto/MANIFESTO.md` Principles 3, 4, 5, 6 | Scientific principles operationalized by these requirements |
