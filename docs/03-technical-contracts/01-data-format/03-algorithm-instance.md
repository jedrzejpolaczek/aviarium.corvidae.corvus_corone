# §2.2 Algorithm Instance

> Index: [01-data-format.md](01-data-format.md)

> See GLOSSARY: [Algorithm Instance](../GLOSSARY.md#algorithm-instance)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | int | yes | Algorithm Instance ID |
| name | string | yes | Human-readable name for this specific configuration eg. `NSGANet`, `Grid vs Random` |
| version | string | yes | Version of this record. Structure is described in validation rules |
| algorithm_family | string | yes | The abstract Algorithm this is an instance of (e.g., `Random Search`, `TPE`, `CMA-ES`) |
| hyperparameters | map[string, any] | yes | Key-value map of configuration parameter name → value. All hyperparameters must be fully specified |
| configuration_justification | string | yes | Why this configuration was chosen (required for fairness, Principle 10) |
| code_reference | string | yes | Pointer to the Implementation artifact (git commit SHA or pinned package version) |
| language | string | yes | Programming language of the implementation (e.g., `python`) |
| framework | string | yes | Library or framework used (e.g., `optuna`, `scikit-optimize`) |
| framework_version | string | yes | Pinned version of the framework |
| known_assumptions | list[string] | yes | Problem properties this algorithm assumes (e.g., `continuous search space`, `noise-free evaluations`) |
| contributed_by | string | yes | Author or system that registered this algorithm instance |
| created_at | datetime | yes | ISO 8601 UTC timestamp of creation |

**Validation rules:**
- All keys in `hyperparameters` must match the algorithm's declared parameter schema
- `code_reference` must be resolvable and version-pinned (no floating references such as branch names)
- Two Algorithm Instances with identical `hyperparameters` and `code_reference` but different `id` are distinct records and must not be deduplicated silently
- `version` must be updated on every field change: `X` increments on schema-breaking changes, `Y` on additions, `Z` on corrections
