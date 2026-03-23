# §2.1 Problem Instance

> Index: [01-data-format.md](01-data-format.md)

> See GLOSSARY: [Problem Instance](../GLOSSARY.md#problem-instance)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | int | yes | Problem Instance ID |
| name | string | yes | Human-readable name |
| version | string | yes | Version of this record. Structure is described in validation rules |
| provenance | string | yes | Source of this problem (e.g., `real_ml_task`, `synthetic`, `adapted_from_coco`) |
| dimensions | int | yes | Number of hyperparameters in the search space |
| variables | list[object] | yes | List of variable descriptors; each entry has `name`, `type` (`continuous`/`integer`/`categorical`), and `bounds` or `choices` |
| dependencies | list[object] | no | Known interactions between variables (e.g., conditional activation); empty list if none |
| objective.type | string | yes | `minimize` or `maximize` |
| objective.noise_level | string | yes | `deterministic` or `stochastic`; if stochastic, include characterization in notes |
| objective.known_optimum | float | no | Known optimal objective value; `null` if unknown |
| evaluation.budget_type | string | yes | `evaluation_count`, `wall_time`, or `combined` |
| evaluation.default_budget | int or float | yes | Recommended budget for this problem expressed in units of `budget_type` |
| landscape_characteristics | list[string] | no | Known properties of the objective landscape (e.g., `multimodal`, `separable`, `noisy`) |
| real_or_synthetic | string | yes | `real` or `synthetic` |
| domain | string | no | ML or optimization domain this problem represents (e.g., `neural_architecture_search`, `hyperparameter_tuning`) |
| source_reference | string | no | Citation or URL of the paper or system this problem originates from |
| created_by | string | yes | Author or system that registered this problem instance |
| created_at | datetime | yes | ISO 8601 UTC timestamp of creation |
| last_updated | datetime | yes | ISO 8601 UTC timestamp of last modification |

**Validation rules:**
- `dimensions` must equal `len(variables)`
- For `continuous` and `integer` variables, `bounds[0]` must be strictly less than `bounds[1]`
- For `categorical` variables, `choices` must contain at least 2 distinct values
- `objective.known_optimum` is required if `real_or_synthetic` is `synthetic` (synthetic problems are expected to have a known optimum)
- `source_reference` is required if `provenance` is `adapted_from_*` or `real_ml_task`
- `version` must be updated on every field change: `X` increments on schema-breaking changes, `Y` on additions, `Z` on corrections
