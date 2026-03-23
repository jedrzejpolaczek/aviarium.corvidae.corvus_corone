# §2.4 Experiment

> Index: [01-data-format.md](01-data-format.md)

> See GLOSSARY: [Experiment](../GLOSSARY.md#experiment)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | int | yes | Experiment ID |
| study_id | int | yes | ID of the Study this Experiment realizes |
| status | string | yes | `planned`, `running`, `completed`, or `failed` |
| execution_environment.platform | string | yes | Operating system and version (e.g., `Ubuntu 22.04`) |
| execution_environment.hardware | string | yes | Hardware description (e.g., CPU model, RAM, GPU if applicable) |
| execution_environment.language_version | string | yes | Programming language version used eg. `Python` |
| run_ids | list[int] | yes | IDs of all Runs produced by this Experiment; empty until Runs are created |
| started_at | datetime | no | ISO 8601 UTC timestamp when execution began; `null` while `status` is `planned` |
| completed_at | datetime | no | ISO 8601 UTC timestamp when execution finished; `null` until `status` is `completed` or `failed` |

**Validation rules:**
- `study_id` must reference an existing Study
- `completed_at` must be after `started_at` when both are set
- `len(run_ids)` must equal `study.experimental_design.repetitions × len(study.problem_instance_ids) × len(study.algorithm_instance_ids)` when `status` is `completed`
- A `failed` Experiment must still record all Run IDs created before failure
