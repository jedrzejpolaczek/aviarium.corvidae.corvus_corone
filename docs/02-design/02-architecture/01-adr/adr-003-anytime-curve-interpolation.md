# ADR-003: Anytime Curve Interpolation

<!--
STORY ROLE: Defines how the Analysis Engine fills gaps in PerformanceRecord sequences
to reconstruct a complete best-so-far curve at any evaluation count.
Without this ADR, different Analyzer implementations produce different ResultAggregate
values from identical input data — making reproducibility claims meaningless at the
analysis layer.

CONNECTS TO:
  → docs/03-technical-contracts/01-data-format/08-result-aggregate.md (anytime_curves)
  → docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md : Analyzer, InterpolationStrategy
  → docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md : ANYTIME-ECDF_AREA computation
  → ADR-002-performance-recording-strategy.md : produces the PerformanceRecords this ADR reads
-->

---

**Status:** Accepted

**Date:** 2026-03-23

**Deciders:** Core maintainers, methodology lead

---

## Context

ADR-002 defines when the Runner writes PerformanceRecords: at log-scale scheduled
checkpoints, on best-so-far improvement, and at end-of-run. Within a single Run, records
exist at an irregular and algorithm-dependent set of evaluation counts. Across multiple
Runs in the same Experiment, different Runs have records at different evaluation counts.

The Analysis Engine must answer: **what was the best-so-far value at evaluation `n`,
given that no record exists at exactly that count?**

This question must have one documented, deterministic answer. If different Analyzer
implementations choose different reconstruction methods, two researchers computing
`ANYTIME-ECDF_AREA` from identical raw data produce different numbers — violating
NFR-REPRO-01 and MANIFESTO Principle 19.

**Constraints:**

- The method must be mathematically correct for best-so-far curves, not merely practical
- The method must be transparent: the Report must document which interpolation was used
  (FR-21, MANIFESTO Principle 24)
- The method must be extensible without changing the Analyzer interface (NFR-MODULAR-01)

---

## Decision

The canonical interpolation rule for best-so-far curves is
**Last Observation Carried Forward (LOCF)**:

> The best-so-far at evaluation `n` is the `objective_value` of the most recent
> PerformanceRecord in the same Run with `evaluation_number ≤ n`.

LOCF is implemented as the default `InterpolationStrategy` in the Analyzer. It is the
only strategy that may be used without explicit pre-registration in the Study record.
Any other strategy must be declared before execution, is locked with the Study plan, and
is automatically flagged in the Report's limitations section (FR-21).

The `InterpolationStrategy` is a pluggable abstraction in the Analyzer interface — LOCF
is the sole V1 implementation. Cross-study comparisons use LOCF to normalize all
convergence curves to a common evaluation grid before computing ECDF values or aggregate
statistics.

---

## Rationale

### Why LOCF is correct, not merely conventional

Best-so-far is a **monotone non-increasing loss / non-decreasing quality** function by
construction. Between two consecutive PerformanceRecords, the value did not change —
the algorithm ran evaluations but none produced a strictly better result (otherwise the
improvement trigger in ADR-002 would have fired). The value at evaluation `n` is exactly
the value of the last record before `n`. LOCF does not approximate; it reproduces the
exact state the algorithm held.

This makes LOCF categorically different from all alternatives:

| Method | Correct? | Why |
|---|---|---|
| **LOCF** | Yes — exact | Best-so-far is constant between improvements |
| Linear interpolation | No | Implies smooth improvement between records — false. Produces optimistic curves; makes `TIME-EVALUATIONS_TO_TARGET` meaningless at fractional eval counts |
| Worst-value fill | Correct only for the pre-first-record gap | No prior exists before eval 1; resolved by ADR-002's mandatory eval-1 scheduled record |

### Why pluggable despite LOCF being the only correct choice

LOCF is correct for the current data model where `objective_value` is the running
best-so-far. If a future extension stores the current (non-cumulative) evaluation result
rather than the best-so-far, the correct interpolation would differ. Hardcoding LOCF
prevents that extension without an interface break.

The `InterpolationStrategy` abstraction has no V1 cost — LOCF is the one implementation
— and preserves extensibility (NFR-MODULAR-01).

### Why LOCF enables free cross-study schedule comparison

ADR-002 permits per-Study `log_scale_schedule` configuration. Two studies may therefore
have PerformanceRecords at different evaluation counts, making direct record-to-record
comparison invalid. LOCF resolves this: because interpolation is exact, reconstructing a
value at an unlogged count produces the same number that would have been logged if a
record had existed there. The schedule controls *storage density*, not *data existence*.

The Analysis Engine normalizes studies to a common evaluation grid using LOCF before any
cross-study computation. The common grid is either:
- **Default:** the union of all scheduled points across the studies being compared
- **Explicit:** a researcher-specified list provided at analysis time

The grid used is documented in the analysis output; the underlying PerformanceRecords are
never modified.

---

## Alternatives Considered

### Mandate a global fixed schedule for all studies

**Description:** Require all studies to use the same `log_scale_schedule`. Records then
exist at identical evaluation counts across studies; normalization is unnecessary.

**Why rejected:** Prevents legitimate specialized studies. A fixed schedule optimized for
budget-200 early-convergence research is inappropriate for budget-10,000 asymptotic
studies, and vice versa. Additionally, studies with different budgets on the same schedule
still produce records at different late-stage counts — the normalization problem persists.

**Under what conditions reconsidered:** A future community benchmark suite with a fixed
budget and fixed comparison points could mandate a schedule for that suite specifically,
as an opt-in constraint on top of the general policy.

---

### Linear interpolation as the default

**Description:** Reconstruct best-so-far between logged points by linear interpolation.

**Why rejected:** Mathematically incorrect for best-so-far curves. Implies smooth progress
between improvement events that did not occur. Produces systematically optimistic curves
and makes `TIME-EVALUATIONS_TO_TARGET` meaningless.

**Under what conditions reconsidered:** Never as a default for best-so-far data. Could be
the correct default for a future data type storing average batch value rather than running
best.

---

### Pre-compute a dense interpolated curve into ResultAggregate

**Description:** The Analyzer materializes interpolated values onto a fixed grid and
stores them in ResultAggregate. Downstream tools query the pre-computed grid.

**Why rejected:** Bakes a grid choice into stored data. Any later query at a different
evaluation count requires re-running the Analyzer. Increases ResultAggregate storage by
an unbounded factor. LOCF at query time is O(log n) with no pre-computation.

**Under what conditions reconsidered:** If interactive visualization over large result
sets makes query-time interpolation too slow. A pre-computed cache could be stored
alongside the ResultAggregate as a performance optimization, with LOCF remaining
authoritative.

---

## Consequences

**Positive:**

- `ANYTIME-ECDF_AREA` is deterministic: any two Analyzer implementations following this
  ADR produce identical values from the same PerformanceRecords
- Cross-study comparison is possible without constraining Study schedule choices
- The `InterpolationStrategy` interface enables future extensions without breaking the
  Analyzer contract
- The pre-first-record gap is resolved by ADR-002's mandatory eval-1 record (the
  `{1,2,5} × 10^i` default always includes eval 1)

**Negative / Trade-offs:**

- The Analysis Engine must implement grid normalization — it cannot join on
  `evaluation_number` directly for cross-study work
- The common grid derivation must be documented in every cross-study analysis output
- Non-default interpolation strategies require pre-registration; researchers cannot
  experiment post-hoc

**Risks:**

- **Risk:** An Analyzer uses linear interpolation for efficiency.
  **Mitigation:** The Analyzer interface specifies LOCF explicitly. Integration tests
  must verify LOCF output for cases where it differs detectably from linear.
- **Risk:** Two cross-study comparisons use different common grids and produce different
  ECDF values from the same data.
  **Mitigation:** The grid is documented in the analysis output and labeled in the Report.
  Differences due to grid choice are valid but must be surfaced, not buried.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/01-data-format/08-result-aggregate.md` | ResultAggregate `anytime_curves` — populated using the rule defined here |
| `docs/03-technical-contracts/02-interface-contracts.md` | `InterpolationStrategy` interface and `Analyzer` contract governed by this ADR |
| `docs/03-technical-contracts/03-metric-taxonomy.md` | `ANYTIME-ECDF_AREA` computation depends on the interpolation rule and grid normalization defined here |
| `ADR-002-performance-recording-strategy.md` | Produces the PerformanceRecords this ADR reads; eval-1 guarantee resolves the pre-first-record gap |
