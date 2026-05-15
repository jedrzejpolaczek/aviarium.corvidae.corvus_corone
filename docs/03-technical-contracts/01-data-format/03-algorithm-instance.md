# §2.2 Algorithm Instance

> Index: [01-index.md](01-index.md)

> See GLOSSARY: [Algorithm Instance](../../GLOSSARY.md#algorithm-instance)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Algorithm Instance UUID (RFC 4122 v4) |
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
| sensitivity_report | SensitivityReport | no | Documents how performance changes when key parameters are varied (MANIFESTO Principle 11). Required for algorithm contributions submitted via the contribution process; see §2.2.1 |
| contributed_by | string | yes | Author or system that registered this algorithm instance |
| created_at | datetime | yes | ISO 8601 UTC timestamp of creation |

**Validation rules:**
- All keys in `hyperparameters` must match the algorithm's declared parameter schema
- `code_reference` must be resolvable and version-pinned (no floating references such as branch names)
- Two Algorithm Instances with identical `hyperparameters` and `code_reference` but different `id` are distinct records and must not be deduplicated silently
- `version` must be updated on every field change: `X` increments on schema-breaking changes, `Y` on additions, `Z` on corrections
- If `sensitivity_report` is present, it must pass the sub-schema validation in §2.2.1; `null` is valid (the field is optional in the schema but required by the contribution process)

---

## §2.2.1 SensitivityReport Sub-schema

A `SensitivityReport` documents the sensitivity analysis conducted for an Algorithm Instance:
how much does algorithm performance change when one key configuration parameter is varied,
holding all others constant? This implements MANIFESTO Principle 11 (sensitivity documentation
accompanies every algorithm contribution).

| Name | Type | Required | Notes |
|---|---|---|---|
| tested_on_problems | list[string] | yes | Problem Instance IDs (or names) used during sensitivity testing; must be ≥ 1 |
| budget_used | int | yes | Evaluation budget used per Run during sensitivity testing; must be > 0 |
| repetitions_per_config | int | yes | Number of Runs per parameter configuration tested; minimum 10 |
| parameters | list[ParameterSensitivity] | yes | One entry per parameter varied; must be non-empty |
| overall_stability | string | yes | Summary assessment: `"robust"` \| `"moderate"` \| `"sensitive"` |
| notes | string | yes | Free-text rationale for the overall_stability assessment and any caveats |

**Validation rules for SensitivityReport:**
- `repetitions_per_config` must be ≥ 10; fewer repetitions are insufficient to distinguish sensitivity from noise
- `parameters` must contain at least 1 entry
- `overall_stability` must be exactly one of `"robust"`, `"moderate"`, or `"sensitive"`
- `notes` must be non-empty

### §2.2.2 ParameterSensitivity Sub-schema

Each entry in `SensitivityReport.parameters` describes the sensitivity of one parameter:

| Name | Type | Required | Notes |
|---|---|---|---|
| parameter_name | string | yes | Must match a key in the parent `AlgorithmInstance.hyperparameters` |
| values_tested | list[any] | yes | The discrete values at which this parameter was tested; minimum 3 values |
| metric_id | string | yes | ID of the metric used to measure sensitivity (from metric taxonomy) |
| metric_values | list[float] | yes | Aggregate metric value (mean across repetitions) at each entry in `values_tested`; `len(metric_values)` must equal `len(values_tested)` |
| sensitivity_level | string | yes | Per-parameter assessment: `"low"` \| `"moderate"` \| `"high"` |

**Validation rules for ParameterSensitivity:**
- `len(values_tested)` must equal `len(metric_values)`
- `len(values_tested)` must be ≥ 3 (fewer points cannot characterise a sensitivity curve)
- `parameter_name` must match a key in `AlgorithmInstance.hyperparameters`
- `sensitivity_level` must be exactly one of `"low"`, `"moderate"`, `"high"`

**Sensitivity level interpretation:**

| Level | Meaning |
|---|---|
| `"low"` | Performance varies by less than one standard deviation of `ROBUSTNESS-RESULT_STABILITY` across the tested range; the chosen value is not critical |
| `"moderate"` | Performance varies noticeably but the algorithm remains viable across the tested range; the chosen value is important but the algorithm is usable with adjacent settings |
| `"high"` | Performance degrades substantially with small deviations from the chosen value; the configuration justification must explain how the chosen value was determined |

**Example (JSON):**

```json
{
  "tested_on_problems": ["rosenbrock_5d_v1", "branin_v2"],
  "budget_used": 100,
  "repetitions_per_config": 20,
  "overall_stability": "moderate",
  "notes": "acquisition_function choice drives most variance; n_initial_points is robust above 5.",
  "parameters": [
    {
      "parameter_name": "n_initial_points",
      "values_tested": [3, 5, 10, 20],
      "metric_id": "QUALITY-BEST_VALUE_AT_BUDGET",
      "metric_values": [0.82, 0.91, 0.93, 0.92],
      "sensitivity_level": "moderate"
    },
    {
      "parameter_name": "acquisition_function",
      "values_tested": ["EI", "PI", "LCB"],
      "metric_id": "QUALITY-BEST_VALUE_AT_BUDGET",
      "metric_values": [0.93, 0.87, 0.89],
      "sensitivity_level": "moderate"
    }
  ]
}
```
