# §2.6 Performance Record

> Index: [docs/03-technical-contracts/01-data-format/01-index.md](01-index.md)

> See GLOSSARY: [Performance Record](../../GLOSSARY.md#performance-record)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Performance Record UUID (RFC 4122 v4) |
| run_id | string | yes | ID of the Run this record belongs to |
| evaluation_number | int | yes | Number of objective evaluations completed so far in this Run |
| elapsed_time | float | yes | Wall-clock seconds elapsed since Run start |
| objective_value | float | yes | The objective value returned by the evaluation at `evaluation_number`. Raw, not cumulative (ADR-023) |
| best_so_far | float | yes | Best objective value observed in this Run at or before `evaluation_number`, in the direction of `ProblemInstance.objective.type`. This is the field every anytime metric reconstructs (ADR-023) |
| current_solution | map[string, any] | no | The solution (hyperparameter configuration) evaluated at `evaluation_number`; may be omitted to reduce storage |
| is_improvement | bool | yes | `true` if this evaluation changed `best_so_far`, subject to `Study.improvement_epsilon` (ADR-004) |
| trigger_reason | string | yes | Why this record was written. One of: `scheduled`, `improvement`, `end_of_run`, `both` (scheduled + improvement), `scheduled_end_of_run`, `improvement_end_of_run`, `all` (all three). Populated automatically by the Runner base class; see [ADR-002](../../02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md) |

**Validation rules:**
- `best_so_far` is monotone in the objective direction within a Run: non-increasing for `minimize`, non-decreasing for `maximize` (ADR-023)
- `evaluation_number` must be monotonically increasing within a Run
- `elapsed_time` must be monotonically non-decreasing within a Run
- `is_improvement` must be `true` for the first record of every Run
- Every Run must have exactly one record where `trigger_reason` contains `end_of_run` and `evaluation_number == run.budget_used`
- `trigger_reason` must be consistent with `is_improvement`: any value containing `improvement` requires `is_improvement=true`; `scheduled` or `end_of_run` alone permit `is_improvement=false`
- Not every evaluation requires a record — the recording strategy is governed by `Study.sampling_strategy`; see [ADR-002](../../02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md)
