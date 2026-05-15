# §2.5 Run

> Index: [01-data-format.md](01-data-format.md)

> See GLOSSARY: [Run](../GLOSSARY.md#run)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Run UUID (RFC 4122 v4) |
| experiment_id | string | yes | UUID of the Experiment this Run belongs to |
| study_id | string | yes | UUID of the Study this Run belongs to (denormalized for query convenience) |
| problem_instance_id | string | yes | UUID of the Problem Instance executed in this Run |
| algorithm_instance_id | string | yes | UUID of the Algorithm Instance executed in this Run |
| seed | int | yes | Exact integer seed used; must be reproducible |
| budget_used | int \| float | yes | Actual budget consumed in units of `Study.experimental_design.budget_type`: `int` when `budget_type` is `evaluations`; `float` (seconds) when `budget_type` is `wall_time`; a two-element object `{evaluations: int, wall_time: float}` when `budget_type` is `combined` |
| status | string | yes | `completed`, `failed`, or `budget_exhausted` |
| failure_reason | string | no | Required when `status` is `failed`; describes what caused the failure |
| cap_reached_at_evaluation | int \| null | no | Set when `Study.max_records_per_run` was hit during this Run. Records the `evaluation_number` at which improvement logging stopped. `null` if no cap was hit. When set, the generated Report automatically includes a limitations note (FR-21) |
| started_at | datetime | yes | ISO 8601 UTC timestamp when this Run began |
| completed_at | datetime | no | ISO 8601 UTC timestamp when this Run ended; `null` if still running |

**Validation rules:**
- `seed` must be unique within an Experiment for a given `(problem_instance_id, algorithm_instance_id)` pair
- `failure_reason` is required when `status` is `failed`, otherwise `None`
- `completed_at` must be after `started_at` when set
- `problem_instance_id` and `algorithm_instance_id` must reference IDs declared in the parent Study
