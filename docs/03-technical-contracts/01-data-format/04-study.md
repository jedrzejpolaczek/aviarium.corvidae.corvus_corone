# §2.3 Study

> Index: [01-index.md](01-index.md)

> See GLOSSARY: [Study / Benchmarking Study](../../GLOSSARY.md#study--benchmarking-study)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Study UUID (RFC 4122 v4) |
| schema_version | string | yes | Version of the entity schema this record conforms to, e.g. `0.0.2`. Governs the shape of the record, not the identity of the entity. See [13-schema-versioning.md](13-schema-versioning.md) |
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
| pre_registered_hypotheses | list[Hypothesis] | yes | Hypotheses to be tested, declared before data collection begins (Principle 16). Must contain at least one entry before the Study can be locked. See §2.3.1 (ADR-021) |
| root_seed | int | yes | Root seed of the Study. All Run seeds are spawned from `SeedSequence(root_seed)` in run-plan order (ADR-017). Archiving this single integer is sufficient to reproduce every Run seed |
| status | string | yes | `draft` or `locked`. Set to `draft` on creation; `lock_study()` transitions it to `locked`, after which the pre-registration fields are immutable (ADR-013) |
| study_type | string | no | `"standard"` (default) or `"exploratory"`. An exploratory Study waives the diversity rules FR-32 and FR-33 and produces no Level 2 confirmatory output; the declaration is carried into the scope statement of both Reports (ADR-009, ADR-021) |
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
- `pre_registered_hypotheses` must contain at least 1 entry before `lock_study()` succeeds (ADR-021)
- `status` is `draft` on creation and may only transition to `locked`; the reverse transition does not exist (ADR-013)
- `root_seed` must not be modified after any Run referencing this Study has been created

---

## §2.3.1 Hypothesis

A pre-registered hypothesis is a structured record, not free text, so that the Analyzer can
compare what was tested against what was declared and set `pre_registered` on the resulting
`StatisticalTestResult` (ADR-021).

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| hypothesis | string | yes | The claim, stated so that the Study is capable of contradicting it |
| test_type | string | yes | The statistical test that will evaluate it. Must be one of the tests in `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §3. An exploratory Study declares itself through `study_type`, not through this field |
| metric_id | string | yes | The metric the test is applied to. Must be a metric identifier defined in `docs/03-technical-contracts/03-metric-taxonomy/` |

**Validation rules:**
- `test_type` must match a test named in `02-statistical-methodology.md` §3
- `metric_id` must match a metric identifier in the metric taxonomy
- An exploratory Study is declared by `study_type = "exploratory"`. The declaration is carried
  into the Report scope statement so that exploratory results are never presented as
  confirmatory, and it waives the diversity floor (FR-32, FR-33, ADR-009)
