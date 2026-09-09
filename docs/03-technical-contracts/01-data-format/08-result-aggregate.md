# §2.7 Result Aggregate

> Index: [docs/03-technical-contracts/01-data-format/01-index.md](01-index.md)

> See GLOSSARY: [Result Aggregate](../../GLOSSARY.md#result-aggregate)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Result Aggregate ID |
| schema_version | string | yes | Version of the entity schema this record conforms to, e.g. `0.0.3`. Governs the shape of the record, not the identity of the entity. See [13-schema-versioning.md](13-schema-versioning.md) |
| experiment_id | string | yes | ID of the Experiment this aggregate belongs to |
| problem_instance_id | string | yes | ID of the Problem Instance being aggregated over |
| algorithm_instance_id | string | yes | ID of the Algorithm Instance being aggregated over |
| n_runs | int | yes | Number of Runs aggregated; must equal the count of `completed` Runs for this `(experiment, problem, algorithm)` combination |
| metrics | map[string, object] | yes | Map of `metric_name → AggregateValue`; metric names must exactly match names in `docs/03-technical-contracts/03-metric-taxonomy/01-index.md` |
| anytime_curves | list[object] | yes | Summarized performance curves: mean ± spread of `best_so_far` at each `evaluation_number` across all aggregated Runs, reconstructed by LOCF where a Run has no record at that count. The raw `objective_value` is not aggregated here (ADR-023) |

`AggregateValue` is an open structure — the required field is `n_successful`; all other statistics are metric-defined:

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| n_successful | int | yes | Number of Runs that contributed (excludes `failed` Runs); required for every metric type |
| statistics | map[string, float] | yes | Open map of statistic name → value. Allowed keys per metric type are defined in `docs/03-technical-contracts/03-metric-taxonomy/01-index.md`. Examples: `mean`, `std`, `median`, `q25`, `q75`, `min`, `max`, `success_rate`, `ecdf_auc`, `p10`, `p90` |

This keeps the schema forward-compatible: adding a new statistic for a new metric type requires no schema change here — only an update to `03-metric-taxonomy/01-index.md`.

**Validation rules:**
- All keys in `metrics` must exactly match metric names defined in `docs/03-technical-contracts/03-metric-taxonomy/01-index.md` — this is a hard contract
- For each `AggregateValue`, the keys in `statistics` must match the set declared for that metric type in `03-metric-taxonomy/01-index.md`
- `n_runs` must equal `n_successful` + count of excluded failed Runs; it must not silently drop failures
- `anytime_curves` must cover the same `evaluation_number` range as the underlying Performance Records
