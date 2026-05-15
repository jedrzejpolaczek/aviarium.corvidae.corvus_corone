# §2.3 Study

> Index: [01-index.md](01-index.md)

> See GLOSSARY: [Study / Benchmarking Study](../../GLOSSARY.md#study--benchmarking-study)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Study UUID (RFC 4122 v4) |
| name | string | yes | Title of the study |
| version | string | yes | Version of this study, updated automatically after each change. Structure is described in validation rules |
| research_question | string | yes | The motivating research question; free text |
| research_question_tags | list[string] | | List of structured tags for research question (e.g., `topic:generalization`, `domain:NLP`) |
| problem_instance_ids | list[string] | yes | Ordered list of Problem Instance UUIDs included in this study, with pinned versions |
| algorithm_instance_ids | list[string] | yes | Ordered list of Algorithm Instance UUIDs included in this study, with pinned versions |
| experimental_design.budget_type | string | yes | Unit of budget measurement: `evaluations` (integer count), `wall_time` (seconds, float), or `combined`; must be consistent with all referenced ProblemInstance `evaluation.budget_type` values; locked before execution begins |
| experimental_design.repetitions | int | yes | Number of independent runs per (problem, algorithm) pair. Must be declared before data collection begins |
| experimental_design.seed_strategy | string | yes | How seeds are generated and assigned (e.g., `sequential`, `random`, `latin-hypercube`) |
| experimental_design.budget_allocation | string | yes | How the evaluation budget is distributed across runs |
| experimental_design.stopping_criteria | string | yes | What terminates a single run (e.g., `budget_exhausted`, `convergence_threshold`) |
| pre_registered_hypotheses | list[string] | no | Hypotheses to be tested, declared before data collection begins (Principle 16) |
| sampling_strategy | string | yes | Identifier of the PerformanceRecord sampling strategy (e.g., `log_scale_plus_improvement`); governs when the Runner writes records. Must be locked before execution begins. See `docs/02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md` |
| log_scale_schedule | object | yes | Parameters of the log-scale scheduled trigger. Fields: `base_points: list[int]` (default `[1, 2, 5]`), `multiplier_base: int` (default `10`). Produces checkpoints at `base_points[i] × multiplier_base^j` up to the run budget. Must be locked before execution begins |
| improvement_epsilon | float \| null | yes | Minimum improvement required to trigger an improvement record. `null` means strict inequality (any improvement triggers a record). Non-null values must be scientifically justified and appear in the Report limitations section (FR-21). Must be locked before execution begins |
| max_records_per_run | int \| null | no | Optional hard cap on PerformanceRecords per Run. `null` means no cap. If set, improvement records stop when the cap is reached; scheduled records continue. A `cap_reached_at_evaluation` field is set on the affected Run and a limitations note is added to the Report automatically (FR-21) |
| study_type | string | no | `"standard"` (default) or `"exploratory"`. When set to `"exploratory"`, diversity validation rules FR-32 (minimum 5 Problem Instances) and FR-33 (dimensionality and noise coverage) are waived and the study produces no Level 2 (Confirmatory) output. |
| status | string | yes | `"draft"` or `"locked"`. Set to `"draft"` on creation; transitions to `"locked"` via `StudyRepository.lock_study()`. After locking, execution fields are immutable. |
| created_by | string | yes | Author (may be a non person) that created this study |
| created_at | datetime | yes | ISO 8601 UTC timestamp of creation |

**Validation rules:**
- `problem_instance_ids` must contain at least 1 entry
- `algorithm_instance_ids` must contain at least 1 entry
- `experimental_design.repetitions` must be ≥ 1 and must not be modified after any Run referencing this Study has been created
- `sampling_strategy`, `log_scale_schedule`, and `improvement_epsilon` must not be modified after any Run referencing this Study has been created
- `version` must be updated on every field change: `X` increments on schema-breaking changes, `Y` on additions, `Z` on corrections
- `status` must be `"draft"` or `"locked"`; `experimental_design`, `sampling_strategy`, `log_scale_schedule`, and `improvement_epsilon` cannot be modified when `status` is `"locked"`
