# ADR-005: PerformanceRecord Storage Cap

<!--
STORY ROLE: Defines how the system behaves when PerformanceRecord counts grow beyond
what is practical. This is an operational concern entirely separate from what triggers
a record (ADR-002) or what threshold defines improvement (ADR-004).

CONNECTS TO:
  → docs/03-technical-contracts/01-data-format.md §2.3 Study (max_records_per_run)
  → docs/03-technical-contracts/01-data-format.md §2.5 Run (cap_reached_at_evaluation)
  → docs/02-design/01-software-requirement-specification/04-non-functional-requirements/01-non-functional-requirements.md
  → ADR-002-performance-recording-strategy.md : defines the records whose count this ADR limits
  → ADR-004-improvement-sensitivity-threshold.md : improvement trigger is the primary source of unbounded growth
-->

---

**Status:** Accepted

**Date:** 2026-03-23

**Deciders:** Core maintainers, methodology lead

---

## Context

ADR-002's improvement trigger is unbounded: on a monotone-improving algorithm against a
smooth deterministic objective, every evaluation may be an improvement, producing O(budget)
records per Run. On a stochastic objective without a pre-registered `improvement_epsilon`
(ADR-004), noise-driven micro-improvements can similarly generate O(budget) records.

The scheduled trigger produces O(log budget) records — predictable and small. The
end-of-run trigger produces exactly one. The improvement trigger is the only source of
unbounded growth.

At scale, this creates a resource risk: a study with budget 10,000, 30 repetitions,
10 problems, and 5 algorithms could generate up to 15 million records if every
evaluation triggers improvement. This would exhaust memory on resource-constrained
machines or fill disk on long-running studies, without any warning to the researcher.

The system must handle this without:
- Silently dropping data (which corrupts `TIME-EVALUATIONS_TO_TARGET`)
- Blocking study execution when limits are approached
- Requiring the researcher to predict record counts before the study runs

---

## Decision

There is **no default hard cap** on PerformanceRecords per Run.

The Runner emits a **warning** when the PerformanceRecord count for a Run exceeds
`record_count_warning_threshold` (default: 10,000 records per Run, configurable in
system settings). The warning names the Run, the current count, and suggests reviewing
`Study.improvement_epsilon` if the growth is unexpected.

A researcher may optionally set `Study.max_records_per_run` before execution. When this
cap is reached during a Run:

1. **Scheduled records continue to be written.** Their count is O(log budget) and does
   not contribute to the unbounded growth.
2. **Improvement-only records stop.** No further records written *solely* by the
   improvement trigger are added for this Run. If an improvement coincides with a
   scheduled checkpoint (trigger_reason `"both"` or `"all"`), the record is still
   written — it would have been written anyway by the scheduled trigger (rule 1).
   The `max_records_per_run` counter and suppression logic track only records that
   would not have been written without the improvement trigger.
3. **`Run.cap_reached_at_evaluation` is set** to the `evaluation_number` at which
   improvement-only logging stopped.
4. **The Report's limitations section** (FR-21) automatically notes that improvement
   records are absent beyond `cap_reached_at_evaluation`, and that
   `TIME-EVALUATIONS_TO_TARGET` for targets first crossed after that point is
   unavailable.

The end-of-run record is always written regardless of the cap.

---

## Rationale

### Why no default hard cap

A hard cap that silently drops improvement records corrupts the best-so-far sequence in
a way that is undetectable from the stored data alone. A consumer reading the records
would not know whether a gap in the improvement trace reflects genuine stagnation or a
suppressed improvement. `TIME-EVALUATIONS_TO_TARGET` computed from a capped trace
would be silently wrong for any target first crossed after the cap.

The integrity of stored data is more valuable than bounded storage. If a researcher runs
a study that produces an unexpectedly large number of records, the right response is a
warning that invites diagnosis — not silent data loss.

### Why a warning threshold, not a hard limit, as the default response

A warning allows the researcher to diagnose the cause:
- Is `improvement_epsilon` null on a noisy objective? → Set it (ADR-004).
- Is the algorithm genuinely improving on every evaluation early in the run? → Expected;
  the count will level off as the curve flattens.
- Is there a bug in the objective function returning random values? → A warning surfaces
  this before the study completes.

A hard default cap would hide all three cases behind a truncated record.

### Why the optional cap stops improvement records but continues scheduled records

When a researcher explicitly accepts a cap, they are trading improvement trace completeness
for storage bounds. The least harmful way to enforce this trade-off is to preserve the
anytime curve shape (scheduled records provide this at O(log budget) cost) while stopping
the unbounded growth source (improvement records).

The alternative — stopping all records including scheduled ones — would leave gaps in the
anytime curve that cannot be filled by LOCF (ADR-003) since there are no prior records to
carry forward in the capped region. Continuing scheduled records avoids this.

### Why combined scheduled+improvement records are not suppressed

When an improvement coincides with a scheduled checkpoint (producing a `"both"` or `"all"`
record), the record would have been written regardless — the scheduled trigger alone
guarantees it. Suppressing the improvement component of this record would not reduce the
total number of PerformanceRecords written; it would only change the `trigger_reason` field
from `"both"` to `"scheduled"` and set `is_improvement=False`. This provides no storage
benefit and corrupts the `is_improvement` flag without cause.

Consequently, the `max_records_per_run` counter counts only records that exist *solely*
because of the improvement trigger (`trigger_reason` = `"improvement"` or
`"improvement_end_of_run"`). Records at scheduled checkpoints that also register an
improvement (`"both"`, `"scheduled_end_of_run"` coincidentally improving, `"all"`) are
not counted and are never suppressed.

### Why automatic limitations disclosure is required

If a cap is hit and the researcher does not notice, they may compute `TIME-EVALUATIONS_TO_TARGET`
on a capped trace and publish a result that is incorrect for targets crossed after the cap.
FR-21 requires every report to identify scope conditions and limitations. A hit cap is a
limitation on the completeness of the improvement trace — it must appear in the Report
automatically, without relying on the researcher to remember to document it.

---

## Alternatives Considered

### Hard cap as the default, with no opt-out

**Description:** Every study has a hard cap of N records per Run. Researchers cannot
remove it.

**Why rejected:** Silent data loss is worse than no cap. A researcher who designs a study
expecting a dense improvement trace would silently receive an incomplete one. The system
would be lying by omission about what happened in the Run.

**Under what conditions reconsidered:** Never for improvement records — the corruption of
`TIME-EVALUATIONS_TO_TARGET` is a fundamental consequence. A cap could be applied to
the scheduled records alone without scientific harm (they are already O(log budget)),
but that does not address the actual problem.

---

### Cap all record types equally when the limit is reached

**Description:** When `max_records_per_run` is hit, stop writing all PerformanceRecords
— including scheduled ones.

**Why rejected:** Scheduled records are O(log budget) and do not contribute to the
unbounded growth. Stopping them creates gaps in the anytime curve that cannot be
reconstructed by LOCF (no prior record to carry forward). The anytime curve — used by
`ANYTIME-ECDF_AREA` — becomes incomplete for no benefit.

**Under what conditions reconsidered:** Never — the asymmetric cap (improvement stops,
scheduled continues) is strictly better for the same storage bound.

---

### Warn only, no cap option at all

**Description:** The system warns but never allows a hard cap to be set.

**Why rejected:** Some deployment environments (embedded, HPC nodes with shared disk
quotas, cloud spot instances with local storage limits) have hard resource constraints
that the researcher cannot control. An explicit cap with full disclosure is better than
having a study crash mid-execution due to disk exhaustion.

**Under what conditions reconsidered:** If the system introduces bulk binary storage
(Parquet/HDF5, `TODO: REF-TASK-0024`) that makes improvement record storage cheap enough
that hard caps are never needed in practice.

---

## Consequences

**Positive:**

- Default behavior preserves full data integrity — no undisclosed data loss
- Warning threshold surfaces unexpected growth early enough for the researcher to act
  before the study completes
- Optional cap provides a predictable storage bound for resource-constrained deployments
- Automatic limitations disclosure (FR-21) ensures capped studies are never misrepresented
- LOCF reconstruction (ADR-003) remains valid after the cap: scheduled records continue
  uninterrupted and provide the anchor points from which `best_so_far` can be carried
  forward — the anytime curve is never left without a prior anchor in the capped region
- The end-of-run record guarantee is unaffected — `QUALITY-BEST_VALUE_AT_BUDGET`
  is always available

**Negative / Trade-offs:**

- Without a cap, a pathological study can exhaust available storage — the warning is not
  a hard stop
- Researchers must understand that `TIME-EVALUATIONS_TO_TARGET` is unavailable after
  `cap_reached_at_evaluation`; this requires reading the limitations section

**Risks:**

- **Risk:** A researcher dismisses the warning and the study exhausts disk space,
  corrupting the Run records that were being written.
  **Mitigation:** The warning should include a projected total record count based on the
  current growth rate, helping the researcher assess whether action is needed.
- **Risk:** A researcher sets `max_records_per_run` very low (e.g., 50), suppressing
  nearly all improvement records and distorting the improvement trace.
  **Mitigation:** The automatic limitations disclosure makes the cap value visible in the
  Report. The Study record archives the cap value in the immutable pre-execution plan.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/01-data-format.md §2.3` | Study — `max_records_per_run` field governed by this ADR |
| `docs/03-technical-contracts/01-data-format.md §2.5` | Run — `cap_reached_at_evaluation` field governed by this ADR |
| `ADR-002-performance-recording-strategy.md` | Defines the three triggers whose records this ADR limits |
| `ADR-004-improvement-sensitivity-threshold.md` | The primary mitigation for unbounded improvement-record growth; should be considered before setting a hard cap |
