# ADR-002: Dual-Trigger PerformanceRecord Strategy

<!--
STORY ROLE: Defines the "measurement contract" of the system.
Every PerformanceRecord that exists in this system was written by a Runner
that followed this strategy. Without this ADR, different Runner implementations
would produce incomparable data, and anytime analysis would be undefined.

CONNECTS TO:
  → docs/03-technical-contracts/01-data-format.md §2.6 PerformanceRecord
  → docs/03-technical-contracts/01-data-format.md §2.3 Study (sampling_strategy, log_scale_schedule)
  → docs/03-technical-contracts/02-interface-contracts.md : Runner.on_evaluation() contract
  → docs/03-technical-contracts/03-metric-taxonomy.md : ANYTIME-ECDF_AREA, TIME-EVALUATIONS_TO_TARGET
  → docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md Step 5
  → ADR-001-library-with-server-ready-data-layer.md
  → ADR-003-anytime-curve-interpolation.md : what the Analysis Engine does with records produced here
  → ADR-004-improvement-sensitivity-threshold.md : governs when the improvement trigger fires
  → ADR-005-performance-record-storage-cap.md : governs storage limits on records produced here
-->

---

**Status:** Accepted

**Date:** 2026-03-23

**Deciders:** Core maintainers, methodology lead

---

## Context

Every Run in the system produces a sequence of PerformanceRecords — the raw time-series
of best objective value as a function of evaluations consumed. These records are the
sole input to all anytime analysis: `ANYTIME-ECDF_AREA`, `TIME-EVALUATIONS_TO_TARGET`,
and the convergence curves in ResultAggregate.

The question this ADR answers is: **at which evaluation counts must the Runner write a
PerformanceRecord?**

This is not an implementation detail. The answer determines whether anytime metrics can
be computed at all, whether IOHprofiler/COCO export is lossless, and whether
`QUALITY-BEST_VALUE_AT_BUDGET` can be recovered from stored data without re-running.

**Constraints:**

- Records must capture enough resolution for `ANYTIME-ECDF_AREA` (MANIFESTO Principle 14:
  full performance curves, not only endpoints)
- Storing every evaluation is impractical at large budgets: 10,000 evals × 30 runs ×
  10 problems × 5 algorithms = 15 million records per study
- The strategy must be pre-registered in the Study record before execution begins
  (MANIFESTO Principle 16; benchmarking-protocol.md Step 5)
- The strategy must be compatible with IOHprofiler and COCO formats (NFR-INTEROP-01)
- The system must not suppress or alter logged values (MANIFESTO Principles 13, 29)

**Related tools surveyed:**

| Tool | Default logging trigger |
|---|---|
| IOHexperimenter | Improvement (`.dat`, default) + log-scale checkpoints (`.tdat`, opt-in) |
| COCO/bbob | Log-scale eval counts + precision-target hits, both default |
| Nevergrad | ~10% multiplicative growth threshold internally |
| SMAC3 | Every evaluation (RunHistory) + improvement-only trajectory |
| Optuna | Every completed trial |

The black-box optimization benchmarking community (IOHprofiler, COCO) independently
converged on the same structure: improvement-only logging is insufficient for fixed-budget
analysis; log-scale checkpoints provide the right density where it matters.

---

## Decision

The Runner uses three triggers simultaneously. A PerformanceRecord is written whenever
any of the following fires:

1. **Scheduled trigger** — the evaluation count falls on the log-scale schedule
   `{1, 2, 5} × 10^i` up to the run budget (e.g., 1, 2, 5, 10, 20, 50, 100, 200 ...).
   The schedule is configurable per Study via `Study.log_scale_schedule`; this is the
   default.
2. **Improvement trigger** — the current best-so-far objective value is strictly better
   than all previous evaluations in this Run. The sensitivity of this trigger is governed
   by `Study.improvement_epsilon` — see ADR-004.
3. **End-of-run trigger** — the evaluation equals `Run.budget_used`. Always fires,
   regardless of the other two triggers.

When more than one trigger fires at the same `evaluation_number`, exactly one record is
written. Its `trigger_reason` field records which triggers fired. The
`evaluation_number` field is monotonically increasing within a Run by schema constraint;
duplicate records for the same evaluation are not permitted.

Each PerformanceRecord carries a `trigger_reason` field populated automatically by the
Runner base class. Algorithm Authors call `on_evaluation(eval_number, value)` and never
set `trigger_reason` directly.

Storage limits on the records produced by this strategy are governed by ADR-005.

---

## Rationale

### Why three triggers as a unit

The three triggers answer three different analysis questions:

| Trigger | Enables |
|---|---|
| Scheduled | Fixed-budget analysis at any eval count in the schedule; `ANYTIME-ECDF_AREA` |
| Improvement | Exact `TIME-EVALUATIONS_TO_TARGET`; convergence trace reconstruction |
| End-of-run | `QUALITY-BEST_VALUE_AT_BUDGET` from stored data alone |

No single trigger is sufficient on its own. Improvement-only misses fixed-budget queries
(Option B, below). Schedule-only misses exact target-crossing times. End-of-run alone
gives a single point per Run. The three together cover all metric requirements without
logging every evaluation.

### Why COCO-style `{1, 2, 5} × 10^i` as the default schedule

- **Density where it matters.** Convergence is most volatile early. `{1,2,5}` places
  the first checkpoints at evals 1, 2, 5 — capturing the steepest part of the curve —
  then spaces out as curves flatten.
- **Budget-independent count.** Budget 200 → 8 scheduled records. Budget 10,000 → 13.
  The O(log budget) growth means the schedule never dominates storage.
- **Engineering standard.** `{1, 2, 5}` is the IEC E3 preferred-number series, used
  in metrology and scientific reporting for spanning orders of magnitude with minimal
  redundancy. COCO adopted it for the same reason.
- **IOH and COCO interoperability.** IOHprofiler `.tdat` defaults to the same pattern.
  COCO `.tdat` uses `dim × {1,2,5} × 10^i` — the same base scaled by dimension. The
  scheduled records produced here map directly to `.tdat` without approximation (NFR-INTEROP-01).
- **Why not dimension-scaled.** COCO scales by problem dimension because continuous BBO
  has a well-defined dimensionality. HPO search spaces are mixed-type (continuous,
  integer, categorical, conditional); "dimension" is a poor proxy for budget requirements.

### Why `trigger_reason` is a required schema field

IOHprofiler's export format separates improvement records (`.dat`) from scheduled records
(`.tdat`). Without `trigger_reason`, a scheduled non-improvement record cannot be
distinguished from an improvement record that happens to land on a scheduled point.
Lossless IOH export requires this field (NFR-INTEROP-01).

`trigger_reason` is populated by the Runner base class, not by Algorithm Authors. This
keeps the framework concern out of algorithm wrappers (NFR-MODULAR-01). The field has
seven values to compose all three triggers:

| `trigger_reason` | Meaning |
|---|---|
| `"scheduled"` | Scheduled checkpoint only |
| `"improvement"` | Improvement trigger only |
| `"end_of_run"` | End-of-run trigger only |
| `"both"` | Scheduled + improvement |
| `"scheduled_end_of_run"` | Scheduled + end-of-run |
| `"improvement_end_of_run"` | Improvement + end-of-run |
| `"all"` | All three triggers |

### Why end-of-run is mandatory

`QUALITY-BEST_VALUE_AT_BUDGET` is the best value at the final evaluation. If the
algorithm stagnates before exhausting the budget, the final eval may not be a scheduled
point and may not trigger an improvement — leaving no record at the endpoint.
`ResultAggregate.anytime_curves` is validated to cover the same `evaluation_number` range
as the underlying PerformanceRecords; without a guaranteed endpoint the upper bound is
undefined. The end-of-run record is the only guaranteed anchor point.

### Why deduplication is a constraint, not a choice

The PerformanceRecord schema requires `evaluation_number` to be monotonically increasing
within a Run. Two records at the same evaluation count would violate this and corrupt any
ordered iteration. When multiple triggers coincide, one record is the only valid outcome.
`trigger_reason` preserves the full information; no data is lost.

---

## Alternatives Considered

### Option A — Log every evaluation

**Description:** One PerformanceRecord per evaluation, unconditionally.

**Why rejected:** 15 million records per study at typical scale (see Context). Information
gain over the dual-trigger strategy beyond the first ~100 evaluations is negligible —
performance curves flatten and consecutive records are identical.

**Under what conditions reconsidered:** If a dedicated high-volume binary format for
PerformanceRecords (Parquet/HDF5, `TODO: REF-TASK-0024`) makes the storage cost
acceptable. Could become a secondary "full trace" mode.

---

### Option B — Log on improvement only

**Description:** Write a PerformanceRecord only when `is_improvement` is `true`.

**Why rejected:** Breaks fixed-budget analysis. If no improvement occurred between evals
50 and 150, no record exists in that range, and the value at eval 100 cannot be recovered
without re-running. Violates `QUALITY-BEST_VALUE_AT_BUDGET` and `ANYTIME-ECDF_AREA`
(MANIFESTO Principle 14).

**Under what conditions reconsidered:** Never as a complete strategy. Retained as the
improvement trigger component of this decision.

---

### Option C — Fixed linear schedule (every k-th evaluation)

**Description:** Log at evenly-spaced evaluation counts.

**Why rejected:** Undersamples early convergence (high information density) and
oversamples late convergence (flat). k must be chosen per-study and is budget-dependent.
At budget 200 with k=10, only 20 points are recorded — borderline for ECDF. At budget
10,000 with k=10, 1,000 records per run approach Option A's storage cost.

**Under what conditions reconsidered:** For studies where the research question requires
fixed-interval behavior. Expressible as an explicit list in `log_scale_schedule` without
making it the system default.

---

## Consequences

**Positive:**

- `ANYTIME-ECDF_AREA` is computable from stored records for any budget within the
  schedule range, without re-running experiments
- `TIME-EVALUATIONS_TO_TARGET` is exact — improvement records capture the precise
  evaluation where each target was first crossed
- `QUALITY-BEST_VALUE_AT_BUDGET` is always available via the end-of-run record
- Scheduled record count is O(log budget) — predictable and small
- IOH `.dat` / `.tdat` export is lossless (NFR-INTEROP-01) — `trigger_reason` enables
  the stream split
- Algorithm Authors interact only with `on_evaluation(n, v)` — trigger logic is invisible

**Negative / Trade-offs:**

- Improvement record count is algorithm-dependent and unbounded without a cap (ADR-005)
- The `trigger_reason` enum has 7 values — composite triggers require careful handling
  in export code

**Risks:**

- **Risk:** A Runner implementation omits the end-of-run trigger.
  **Mitigation:** Run validation requires at least one PerformanceRecord with
  `evaluation_number == run.budget_used`. Enforced at write time.
- **Risk:** A researcher's custom schedule omits small evaluation counts, leaving no
  records in the early phase where improvement records have not yet fired.
  **Mitigation:** The `{1,2,5} × 10^i` default always includes eval 1. Custom schedules
  must include at least one point ≤ 5 — a validation rule on `log_scale_schedule`.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/01-data-format.md §2.6` | PerformanceRecord — `trigger_reason` field added by this ADR |
| `docs/03-technical-contracts/01-data-format.md §2.3` | Study — `sampling_strategy`, `log_scale_schedule` fields governed by this ADR |
| `docs/03-technical-contracts/02-interface-contracts.md` | Runner `on_evaluation()` contract governed by this ADR |
| `docs/03-technical-contracts/03-metric-taxonomy.md` | `ANYTIME-ECDF_AREA` and `TIME-EVALUATIONS_TO_TARGET` depend on the records produced here |
| `docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md Step 5` | Requires the sampling schedule to be specified before execution |
| `ADR-001-library-with-server-ready-data-layer.md` | Bulk storage format for high-volume PerformanceRecords deferred to `REF-TASK-0024` |
| `ADR-003-anytime-curve-interpolation.md` | How the Analyzer reconstructs best-so-far at unlogged evaluation counts |
| `ADR-004-improvement-sensitivity-threshold.md` | When the improvement trigger fires (epsilon configuration) |
| `ADR-005-performance-record-storage-cap.md` | Storage limits on records produced by this strategy |
