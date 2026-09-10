# §2.1 Problem Instance

> Index: [docs/03-technical-contracts/01-data-format/01-index.md](01-index.md)

> See GLOSSARY: [Problem Instance](../../GLOSSARY.md#problem-instance)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Problem Instance UUID (RFC 4122 v4) |
| schema_version | string | yes | Version of the entity schema this record conforms to, e.g. `0.0.3`. Governs the shape of the record, not the identity of the entity. See [13-schema-versioning.md](13-schema-versioning.md) |
| name | string | yes | Human-readable name |
| version | string | yes | Human-readable version for display and citation; never an addressing key (ADR-020). See validation rules |
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
| deprecated | bool | yes | `true` once `deprecate_problem()` has been called; `false` on registration. Deprecated entities are excluded from `list_problems()` and still returned by `get_problem()` (ADR-020) |
| deprecation_reason | string | no | Why the entity was deprecated. Required when `deprecated` is `true`, `null` otherwise |
| superseded_by | string | no | UUID of the entity that replaces this one, when there is one. Deprecation without a replacement is legitimate — a problem may simply be withdrawn — so this stays optional even when `deprecated` is `true` |
| created_by | string | yes | Author or system that registered this problem instance |
| created_at | datetime | yes | ISO 8601 UTC timestamp of creation |
| last_updated | datetime | yes | ISO 8601 UTC timestamp of the last write. Under ADR-020 the only write after registration is deprecation, so this equals `created_at` for every entity that has not been deprecated |

**Validation rules:**
- `dimensions` must equal `len(variables)`
- For `continuous` and `integer` variables, `bounds[0]` must be strictly less than `bounds[1]`
- For `categorical` variables, `choices` must contain at least 2 distinct values
- `objective.known_optimum` is required if `real_or_synthetic` is `synthetic` (synthetic problems are expected to have a known optimum)
- `source_reference` is required if `provenance` is `adapted_from_*` or `real_ml_task`
- `version` is descriptive metadata for display and citation, never an addressing key (ADR-020). Entities are immutable: a revision is a **new** entity with a new UUID, and the old one is deprecated with `superseded_by` pointing at it. There is no field change to version, because there is no field change
- `deprecation_reason` is required when `deprecated` is `true`
- `superseded_by`, when set, must resolve to a Problem Instance, must not be this entity, and must not close a cycle of `superseded_by` links
