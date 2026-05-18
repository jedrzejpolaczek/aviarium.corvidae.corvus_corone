# §2.4 Experiment

> Index: [01-index.md](01-index.md)

> See GLOSSARY: [Experiment](../../GLOSSARY.md#experiment)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Experiment UUID (RFC 4122 v4) |
| study_id | string | yes | UUID of the Study this Experiment realizes |
| status | string | yes | `planned`, `running`, `completed`, `failed`, or `aborted` |
| software_environment | object | no | Captured automatically at execution start. Fields: `dependencies: list[{name, version}]` (all installed packages). Complements `execution_environment` which records platform details. `null` until `status` transitions to `running`. |
| reproducibility_hash | string | no | SHA-256 hash of the canonical serialization of `{study_id, software_environment, execution_environment}`. Used to detect environment drift between reproduction runs. Populated when the Experiment transitions to `completed`. |
| execution_environment.platform | string | yes | Operating system and version (e.g., `Ubuntu 22.04`) |
| execution_environment.hardware | string | yes | Hardware description (e.g., CPU model, RAM, GPU if applicable) |
| execution_environment.language_version | string | yes | Programming language version used eg. `Python` |
| run_ids | list[string] | yes | UUIDs of all Runs produced by this Experiment; empty until Runs are created |
| started_at | datetime | no | ISO 8601 UTC timestamp when execution began; `null` while `status` is `planned` |
| completed_at | datetime | no | ISO 8601 UTC timestamp when execution finished; `null` until `status` is `completed` or `failed` |

**Validation rules:**
- `study_id` must reference an existing Study
- `completed_at` must be after `started_at` when both are set
- `len(run_ids)` must equal `study.experimental_design.repetitions × len(study.problem_instance_ids) × len(study.algorithm_instance_ids)` when `status` is `completed`
- A `failed` or `aborted` Experiment must still record all Run IDs created before the terminal state was reached
- `aborted` status indicates a critical error that halted the entire Experiment early (e.g., seed collision, storage unavailable); individual Run failures within an otherwise-proceeding Experiment use `status="failed"` on the Run record, not on the Experiment
