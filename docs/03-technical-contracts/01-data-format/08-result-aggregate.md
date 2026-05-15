# §2.7 Result Aggregate

> Index: [01-index.md](01-index.md)

> See GLOSSARY: [Result Aggregate](../../GLOSSARY.md#result-aggregate)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Result Aggregate UUID (RFC 4122 v4) |
| experiment_id | string | yes | UUID of the Experiment this aggregate belongs to |
| problem_instance_id | string | yes | UUID of the Problem Instance being aggregated over |
| algorithm_instance_id | string | yes | UUID of the Algorithm Instance being aggregated over |
| n_runs | int | yes | Total number of Runs attempted for this `(experiment, problem, algorithm)` combination — counts both `completed` and `failed` Runs; must not silently drop failures |
| metrics | map[string, object] | yes | Map of `metric_name → AggregateValue`; metric names must exactly match names in `docs/03-technical-contracts/03-metric-taxonomy/01-index.md` |
| anytime_curves | list[object] | yes | Summarized performance curves: mean ± spread of `objective_value` at each `evaluation_number` across all aggregated Runs |

`AggregateValue` is an open structure — the required field is `n_successful`; all other statistics are metric-defined:

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| n_successful | int | yes | Number of Runs that contributed (excludes `failed` Runs); required for every metric type |
| statistics | map[string, float] | yes | Open map of statistic name → value. Allowed keys per metric type are defined in `docs/03-technical-contracts/03-metric-taxonomy/01-index.md`. Examples: `mean`, `std`, `median`, `q25`, `q75`, `min`, `max`, `success_rate`, `ecdf_auc`, `p10`, `p90` |

This keeps the schema forward-compatible: adding a new statistic for a new metric type requires no schema change here — only an update to `metric-taxonomy.md`.

**Validation rules:**
- All keys in `metrics` must exactly match metric names defined in `docs/03-technical-contracts/03-metric-taxonomy/01-index.md` — this is a hard contract
- For each `AggregateValue`, the keys in `statistics` must match the set declared for that metric type in `metric-taxonomy.md`
- `n_runs` must equal `n_successful` + count of excluded failed Runs; it must not silently drop failures
- `anytime_curves` must cover the same `evaluation_number` range as the underlying Performance Records
