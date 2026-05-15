# ADR-004: Improvement Sensitivity Threshold

<!--
STORY ROLE: Governs when the improvement trigger defined in ADR-002 fires.
This is a separate decision because it sits at the intersection of Runner mechanics
and scientific integrity — the threshold is not a free engineering parameter; it has
direct consequences for what the data says.

CONNECTS TO:
  → docs/03-technical-contracts/01-data-format/04-study.md (improvement_epsilon field)
  → docs/03-technical-contracts/01-data-format/07-performance-record.md (is_improvement field)
  → docs/02-design/01-software-requirement-specification/05-constraints/02-const-scientific.md
  → ADR-002-performance-recording-strategy.md : improvement trigger is one of the three triggers
-->

---

**Status:** Accepted

**Date:** 2026-03-23

**Deciders:** Core maintainers, methodology lead

---

## Context

ADR-002 defines that a PerformanceRecord is written whenever the best-so-far objective
value "strictly improves." This ADR defines what "strictly improves" means in practice.

The naive answer — fire whenever `objective_value < best_so_far` — is correct for
deterministic objectives. But HPO problems frequently involve stochastic objectives:
cross-validation loss varies with random train/validation splits; neural network training
is sensitive to weight initialization. On a stochastic objective with noise amplitude
±0.01, consecutive evaluations can produce sequences like 0.9312, 0.9311, 0.9310 — each
a "strict improvement" by one part in ten thousand, yet representing noise, not progress.

This produces two compounding problems:

1. **Storage pollution.** The improvement trigger fires on nearly every early evaluation,
   generating O(budget) records and negating the O(log budget) design goal of ADR-002.
2. **Misleading convergence traces.** A convergence plot of a noisy algorithm looks like
   rapid, continuous improvement when it is actually noisy stagnation. This violates
   MANIFESTO Principle 13 (report what actually happened) in a subtle way: the data is
   accurate, but the implied narrative is false.

However, any filter on what counts as an improvement is also a form of data suppression,
and suppressions that are not disclosed violate MANIFESTO Principle 29 (Objectivity over
promotion). The system must allow noise-aware filtering without making it a silent default.

---

## Decision

The improvement trigger fires by **strict inequality** with no epsilon by default:

```
is_improvement = (objective_value < best_so_far_before_this_evaluation)
```

A researcher may pre-register an `improvement_epsilon` in the Study record. When set,
the trigger fires only when:

```
best_so_far - objective_value > improvement_epsilon
```

`improvement_epsilon` defaults to `null` (strict inequality). It may only be set before
execution begins, is locked with the Study plan, and is treated as a limitation: any
non-null value is automatically included in the Report's limitations section (FR-21).

---

## Rationale

### Why strict inequality is the default

MANIFESTO Principle 13 requires the system to report what actually happened. Any epsilon
suppresses real data — it alters the stored record to match a researcher-chosen sensitivity
level rather than the observed sequence of events. A system that silently suppresses
small improvements makes an undocumented methodological choice on behalf of the researcher.

MANIFESTO Principle 29 (Objectivity over promotion) is directly at risk: an algorithm
with gradual early improvements might look better or worse depending on epsilon, and a
default epsilon chosen by the system without disclosure could favor certain algorithm
families over others without the researcher noticing.

Strict inequality is the only defensible default — it records every event that occurred.

### Why configurable at all

Strict inequality on a stochastic objective is not always a faithful representation of
scientific progress. If the objective function's noise floor is ±0.01, then a logged
improvement of 0.00001 does not mean the algorithm found a better solution — it means
the random noise happened to produce a lower number. Recording this as "improvement" is
factually accurate but scientifically misleading.

A researcher who characterizes their objective's noise floor and pre-registers
`improvement_epsilon = 0.001` is making a more scientifically accurate record than one
who uses strict inequality on a noisy objective. The epsilon is not suppressing signal;
it is defining what counts as signal for this specific problem.

The pre-registration requirement (locked before execution, part of the Study plan)
prevents post-hoc tuning of epsilon to make an algorithm's convergence trace look better.

### What epsilon does and does not affect

`improvement_epsilon` affects only the improvement trigger. Scheduled records and the
end-of-run record are written regardless. This means:

- The anytime curve shape (from scheduled records) is always correct
- `QUALITY-BEST_VALUE_AT_BUDGET` is always available from the end-of-run record
- `TIME-EVALUATIONS_TO_TARGET` may be affected: if a target is crossed by a
  sub-epsilon improvement, no improvement record is written, and the exact crossing
  evaluation is not captured. The Report limitations section must note this.

---

## Alternatives Considered

### System-wide fixed epsilon

**Description:** The system applies a single fixed epsilon to all studies, without
researcher configuration.

**Why rejected:** There is no universal epsilon. Noise amplitude is problem-dependent —
a good epsilon for a cross-validation loss (typical range 0–1) is useless for a
validation RMSE (typical range 0–100). A system-wide epsilon calibrated for one domain
would be wrong for all others.

**Under what conditions reconsidered:** Never — domain-independence is a fundamental
property of the system.

---

### Relative epsilon (`value < best × (1 - ε)`)

**Description:** Trigger improvement when the new value is at least ε% better than the
current best, regardless of scale.

**Why rejected:** A percentage threshold still requires calibration. Additionally,
relative thresholds behave poorly near zero (a 1% improvement on a loss of 0.0001 is
0.000001, which may be below floating-point precision). The absolute threshold is simpler,
more predictable, and directly relatable to the noise characterization in the Problem
Instance record.

**Under what conditions reconsidered:** If a future extension supports objectives with
wildly varying scales within a single study (e.g., multi-objective optimization where
objectives span different orders of magnitude). A relative epsilon would then be more
scale-invariant.

---

## Consequences

**Positive:**

- Default behavior records every observed improvement — no undisclosed filtering
- Pre-registered epsilon enables scientifically defensible noise filtering that is
  transparent, auditable, and locked before execution
- The Report limitations mechanism (FR-21) ensures no epsilon choice is ever invisible
  to a reader of the study

**Negative / Trade-offs:**

- On stochastic objectives with no epsilon set, improvement record count can approach
  O(budget) — mitigated by ADR-005 (storage cap with warnings)
- Researchers unfamiliar with their objective's noise floor may leave `improvement_epsilon`
  at `null` and get noisy improvement traces, which requires post-hoc interpretation

**Risks:**

- **Risk:** A researcher sets a large epsilon to hide gradual early improvements, making
  an algorithm appear to converge in fewer steps than it did.
  **Mitigation:** Any non-null epsilon appears in the Report's limitations section and
  is archived in the Study record. The raw PerformanceRecords show which improvements
  were suppressed via the absence of improvement records between scheduled checkpoints.
- **Risk:** A researcher forgets to set epsilon on a noisy objective, generating
  millions of spurious improvement records.
  **Mitigation:** ADR-005's warning threshold will fire when improvement records exceed
  the configured count. The warning message suggests reviewing `improvement_epsilon`.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/01-data-format/04-study.md` | Study — `improvement_epsilon` field governed by this ADR |
| `docs/03-technical-contracts/01-data-format/07-performance-record.md` | PerformanceRecord — `is_improvement` semantics governed by this ADR |
| `ADR-002-performance-recording-strategy.md` | Improvement trigger is one of the three triggers defined there; this ADR defines when it fires |
| `ADR-005-performance-record-storage-cap.md` | Storage consequences of high improvement-record counts mitigated there |
