# §4 Interoperability Mappings

> Index: [01-data-format.md](01-data-format.md)

This section defines how Corvus Corone entities map to external platform formats. Each subsection
covers one platform: direction, field-level mapping, information-loss manifest items, and version
compatibility. The information-loss manifest items listed here are the authoritative source for the
`information_loss_manifest` returned by every `export()` call (FR-26, NFR-INTEROP-01).

---

## §4.1 COCO / BBOB (Comparing Continuous Optimisers)

**Direction:** Export only (Corvus → COCO). Import from COCO is not supported in V1.

**Supported COCO format version:** BBOBNewDataFormat (introduced in COCO ≥ 2.0;
current reference implementation: `cocopp` ≥ 2.6). The legacy `BBOBOldDataFormat` (single
`.dat` column layout) is not produced.

**COCO output files produced per export call:**

| File | Role |
|---|---|
| `<algId>/<suite>_f<funcId>_DIM<d>.info` | Index file: problem metadata + per-instance eval/target summary |
| `<algId>/data_f<funcId>/bbob_f<funcId>_DIM<d>_i<inst>.dat` | Performance log: one row per recorded evaluation |

### §4.1.1 Field mapping

#### Problem Instance → COCO `.info` header

| Corvus Field | COCO Field | Notes / Losses |
|---|---|---|
| `ProblemInstance.dimensions` | `DIM` | Exact |
| `ProblemInstance.objective.known_optimum` | `f_opt` (implied) | Required for computing `f(x)−f_opt`; if `null`, see **LOSS-COCO-01** |
| `ProblemInstance.source_reference` | `funcId` | For `provenance=adapted_from_coco` problems, `source_reference` must contain the COCO function ID as `coco:funcId=<N>`. If absent, see **LOSS-COCO-04** |
| `ProblemInstance.variables[*].type` | Suite name (`bbob` vs `bbob-mixint`) | `continuous`-only → `bbob`; mixed `continuous`+`integer` → `bbob-mixint`; `categorical` variables → **LOSS-COCO-05** |
| `ProblemInstance.evaluation.default_budget` | `maxevals` in `.info` line 3 | Exact when `budget_type=evaluation_count`; see **LOSS-COCO-06** for `wall_time` |
| `ProblemInstance.name` | Comment line in `.info` | Informational only; not parsed by `cocopp` |

#### Algorithm Instance → COCO `.info` algorithm block

| Corvus Field | COCO Field | Notes / Losses |
|---|---|---|
| `AlgorithmInstance.name` | `algId` | Exact; used as top-level directory name |
| `AlgorithmInstance.algorithm_family` | Comment line | Informational |
| `AlgorithmInstance.framework` + `framework_version` | Comment line | Informational |
| `AlgorithmInstance.code_reference` | Comment line | Informational; not parsed by `cocopp` |
| `AlgorithmInstance.hyperparameters` | Not represented | **LOSS-COCO-07** |

#### Run → COCO `.info` line 3 instance entry

| Corvus Field | COCO Field | Notes / Losses |
|---|---|---|
| `Run.seed` | `instance` (proxy) | COCO instance numbers encode random transformations of the function; Corvus seeds are independent random integers. The seed is written into the `.info` comment block. The `instance` field in the `.info` line is set to the run's repetition index (1-based) within the Experiment. See **LOSS-COCO-03** |
| `Run.budget_used` | `maxevals` in instance entry | Exact when `budget_type=evaluation_count` |
| `Run.status=failed` | No representation | Failed runs are excluded from COCO export. **LOSS-COCO-08** |

#### Performance Record → COCO `.dat` row

| Corvus Field | COCO `.dat` Column | Format | Notes / Losses |
|---|---|---|---|
| `PerformanceRecord.evaluation_number` | Col 0 (`%lu`) | f-evaluations count | Exact |
| *(not stored)* | Col 1 (`%lu`) | Constraint evaluations count | Always exported as `0`; Corvus does not track constraint evaluations separately. **LOSS-COCO-02** |
| `PerformanceRecord.objective_value − ProblemInstance.objective.known_optimum` | Col 2 (`%+10.9e`) | `best f(x)−f_opt so far` | Exact when `known_optimum` is not `null`; see **LOSS-COCO-01** otherwise |
| *(not stored)* | Col 3 (`%+10.9e`) | `current f(x)` (non-best) | Corvus records only `best objective value so far` in `objective_value`. When `is_improvement=false`, the current evaluation value is not stored. Exported as the same value as col 2. **LOSS-COCO-09** |
| `PerformanceRecord.current_solution` values | Col 4+ (`%+10.9e` each) | Decision variables | Exported only when `current_solution` is present AND `dimensions < 7`. If `current_solution` is absent or `dimensions ≥ 7`, columns 4+ are omitted. **LOSS-COCO-10** |

### §4.1.2 Information-loss manifest

Each `export(experiment, "coco")` call returns an `information_loss_manifest` list. The following
items are always evaluated; items that do not apply to the specific export (e.g., no `null`
`known_optimum`) are omitted from the returned manifest.

| Manifest Key | Severity | Condition | Description |
|---|---|---|---|
| `LOSS-COCO-01` | **critical** | Any `ProblemInstance.objective.known_optimum` is `null` | COCO column 2 requires `f(x)−f_opt`; gap cannot be computed without the known optimum. `objective_value` is exported as a proxy (raw objective, not a gap). Post-processing with `cocopp` will yield incorrect convergence plots for this problem. |
| `LOSS-COCO-02` | informational | Always | Constraint evaluations (COCO col 1) not tracked by Corvus; exported as `0`. Affects constraint benchmarking suites only. |
| `LOSS-COCO-03` | informational | Always | COCO `instance` encodes a specific random affine transformation of the benchmark function. Corvus `Run.seed` is a free integer seed — not equivalent. Reproducibility of the COCO random transformation is not guaranteed from the exported `.dat` alone. |
| `LOSS-COCO-04` | warning | `ProblemInstance.source_reference` does not contain `coco:funcId=<N>` | Cannot populate COCO `funcId` in `.info` header. `cocopp` dimension-function grouping will not work correctly. |
| `LOSS-COCO-05` | **critical** | Any `ProblemInstance.variables[*].type == "categorical"` | COCO has no categorical variable type. Categorical dimensions cannot be represented. Export is blocked unless the calling code provides an explicit override mapping. |
| `LOSS-COCO-06` | warning | `ProblemInstance.evaluation.budget_type != "evaluation_count"` | COCO `maxevals` is expressed in function evaluations. Wall-time or combined budgets are approximated using `Run.budget_used` converted to the nearest integer evaluation count. |
| `LOSS-COCO-07` | informational | Always | `AlgorithmInstance.hyperparameters` are not represented in any structured COCO field; written to the `.info` comment block only and not parsed by `cocopp`. |
| `LOSS-COCO-08` | informational | Any `Run.status == "failed"` | Failed runs are excluded from COCO export. The `.info` instance list will contain fewer entries than `Study.experimental_design.repetitions`. |
| `LOSS-COCO-09` | informational | Always | COCO col 3 is the current (non-best) `f(x)` at each recorded evaluation. Corvus stores only `best_so_far`; col 3 is duplicated from col 2. ERT-based analyses are unaffected; per-evaluation value analyses will show staircase artifact. |
| `LOSS-COCO-10` | informational | `PerformanceRecord.current_solution` absent OR `dimensions ≥ 7` | Decision variable columns (col 4+) omitted. `cocopp` scatter plots of decision space are unavailable. |

### §4.1.3 Trigger-model compatibility

COCO's `.dat` format logs a row when the algorithm crosses a new precision target
(i.e., `f(x)−f_opt` drops below a threshold in the standard log-scale target sequence).
Corvus's `trigger_reason=improvement` fires when `objective_value` strictly improves by at
least `Study.improvement_epsilon`.

These are not equivalent:
- COCO targets are absolute gaps from `f_opt` on a fixed log scale; Corvus records any strict
  improvement relative to the previous best.
- A Corvus run with `improvement_epsilon=null` (strict improvement) will produce more rows than
  COCO would for the same run, because Corvus fires on every new best, not only on threshold
  crossings.
- Rows that are scheduled (`trigger_reason=scheduled`) but not improvements are included in
  the export and may not align with COCO precision thresholds.

`cocopp` processes the full `.dat` file and extracts the relevant threshold-crossing rows during
post-processing, so additional rows do not break analysis — but the resulting ECDF plots may
differ slightly from runs collected natively via `cocoex`.

### §4.1.4 Version compatibility

| COCO / `cocopp` version | Supported | Notes |
|---|---|---|
| `cocopp` ≥ 2.6, BBOBNewDataFormat | Yes | Reference implementation |
| `cocopp` < 2.0, BBOBOldDataFormat | No | Single-column legacy format; not produced |

---

## §4.2 IOHprofiler

> TODO: REF-TASK-0006 — IOHprofiler format mapping spike required before this section can be filled.

---

## §4.3 Nevergrad

**Direction:** Bidirectional.
- **Corvus → Nevergrad (adapter):** Corvus runs Nevergrad optimizers via `NevergradAdapter`,
  translating the Corvus ask-tell interface to Nevergrad's native `ask()` / `tell()` API.
  Described in `corvus_corone/algorithms/adapters/nevergrad_adapter.py` and
  `docs/06-tutorials/03-nevergrad-adapter.md`.
- **Corvus → Nevergrad log format (export):** Corvus `PerformanceRecord`s can be serialized
  to the Nevergrad `ParametersLogger` JSON-lines format for downstream analysis with
  Nevergrad benchmark tooling.

**Supported Nevergrad version:** 1.0.x (current stable as of 2026-03-24; `nevergrad==1.0.12`).
Nevergrad uses PEP 440 semantic versioning. The ask-tell interface (`ask()`, `tell()`,
`provide_recommendation()`) has been stable across the 0.x series and is not expected to
break within 1.x.

### §4.3.1 SearchSpace → Nevergrad parametrization mapping

Nevergrad optimizers receive a `parametrization` object at construction time. `NevergradAdapter`
builds a `ng.p.Dict` from the Corvus `SearchSpace`, mapping each variable type as follows:

| Corvus variable type | Nevergrad class | Constructor call |
|---|---|---|
| `continuous` | `ng.p.Scalar` | `ng.p.Scalar(lower=float(lo), upper=float(hi))` |
| `integer` | `ng.p.Scalar` + `.set_integer_casting()` | `ng.p.Scalar(lower=float(lo), upper=float(hi)).set_integer_casting()` |
| `categorical` (unordered) | `ng.p.Choice` | `ng.p.Choice(choices)` |

**Categorical ordering note:** All Corvus `categorical` variables are mapped to `ng.p.Choice`
(non-deterministic softmax selection). If the variable is ordinally ordered (e.g., `[1, 2, 4, 8]`
layer counts), `ng.p.TransitionChoice` would produce better optimization trajectories, but
this distinction is not expressed in the Corvus `variables` schema — see **LOSS-NG-05**.

**Seeding:** `parametrization.random_state.seed(seed)` is called with the Runner-injected seed
before the optimizer is constructed. This satisfies the §6 randomness isolation contract.

### §4.3.2 Corvus Algorithm Instance → Nevergrad optimizer fields

| Corvus Field | Nevergrad concept | Notes |
|---|---|---|
| `AlgorithmInstance.algorithm_family` | `optimizer_name` key in `ng.optimizers.registry` | The registry key is the exact string passed to `NevergradAdapter(optimizer_name=...)`. |
| `AlgorithmInstance.framework_version` | `nevergrad.__version__` | Retrieved at `get_metadata()` time. Version-pinned in `code_reference` as `nevergrad==<version>`. |
| `AlgorithmInstance.hyperparameters["budget"]` | `budget` constructor arg | Must match Study budget so that budget-adaptive optimizers (e.g. NGOpt) can tune their internal strategy. |
| `AlgorithmInstance.hyperparameters["optimizer_name"]` | `ng.optimizers.registry` key | Redundant with `algorithm_family`; stored for explicitness. |
| `AlgorithmInstance.hyperparameters[*]` | Additional constructor kwargs | Any extra keys are forwarded to the optimizer constructor as `**hyperparameters`. |
| `AlgorithmInstance.known_assumptions` | Not represented | Nevergrad does not have a concept of declared assumptions; stored in Corvus only. |

### §4.3.3 Corvus → Nevergrad log format field mapping

When exporting Corvus `PerformanceRecord`s to the Nevergrad `ParametersLogger` JSON-lines
format (one JSON object per `tell()` call):

| Corvus Field | Nevergrad JSON field | Notes / Losses |
|---|---|---|
| `PerformanceRecord.evaluation_number` | `#num-tell` | Approximate: Nevergrad counts tells since logger registration; Corvus evaluation_number is 1-indexed from Run start. Exact if logger registered before the first tell. |
| `PerformanceRecord.objective_value` | `#loss` | For minimization: exact. For maximization: `#loss` is negated (`-objective_value`); see **LOSS-NG-01**. |
| `PerformanceRecord.current_solution` | `{variable_name}` fields | Exported as named fields when `current_solution` is present. If `current_solution` is absent, variable fields are omitted — see **LOSS-NG-02**. |
| `PerformanceRecord.elapsed_time` | Not represented | No equivalent in Nevergrad JSON-lines format. See **LOSS-NG-03**. |
| `PerformanceRecord.is_improvement` | Not represented | Nevergrad does not annotate tell records with improvement status. See **LOSS-NG-04**. |
| `Run.seed` | `#session` (proxy) | `#session` is the logger initialization timestamp, not a seed. The seed is not stored in the Nevergrad format. See **LOSS-NG-06**. |
| `AlgorithmInstance.name` | `#optimizer` | Nevergrad writes the optimizer class name; `AlgorithmInstance.name` is a human-readable label that may differ. |
| `AlgorithmInstance.algorithm_family` | `#parametrization` | Nevergrad writes the parametrization class name (`Dict`), not the optimizer family. **LOSS-NG-07**. |

### §4.3.4 Information-loss manifest

Each `export(experiment, "nevergrad")` call returns an `information_loss_manifest` list.

| Manifest Key | Severity | Condition | Description |
|---|---|---|---|
| `LOSS-NG-01` | warning | `ProblemInstance.objective.type == "maximize"` | Nevergrad minimizes internally; exported `#loss` values are negated. Downstream Nevergrad benchmark tools that interpret `#loss` as the raw objective will read inverted values. |
| `LOSS-NG-02` | informational | Any `PerformanceRecord.current_solution` is absent | Variable-value fields in the JSON-lines record are omitted. Nevergrad scatter-plot analyses of the decision space are unavailable for those records. |
| `LOSS-NG-03` | informational | Always | `PerformanceRecord.elapsed_time` has no Nevergrad JSON-lines equivalent; not exported. |
| `LOSS-NG-04` | informational | Always | `PerformanceRecord.is_improvement` has no Nevergrad JSON-lines equivalent; not exported. Improvement-annotated analyses using Nevergrad tooling are unavailable. |
| `LOSS-NG-05` | informational | Any `categorical` variable that is ordinally ordered | Corvus `categorical` maps to `ng.p.Choice` (unordered). If the variable is ordinal, `ng.p.TransitionChoice` would yield better optimizer trajectories but cannot be inferred from Corvus schema alone. Re-run the adapter with a custom parametrization to capture this. |
| `LOSS-NG-06` | informational | Always | Corvus `Run.seed` is not stored in the Nevergrad log format. The `#session` field records logger init time, not the seed. Reproducibility from the Nevergrad log alone is not possible without the Corvus Run record. |
| `LOSS-NG-07` | informational | Always | `#parametrization` records the `ng.p.Dict` class name, not `AlgorithmInstance.algorithm_family`. Nevergrad benchmark grouping by algorithm family requires post-processing against the Corvus Algorithm Instance record. |

### §4.3.5 Adapter → Corvus import direction

Nevergrad results produced *natively* (i.e., outside Corvus) can be imported into Corvus
`PerformanceRecord`s by reading the `ParametersLogger` JSON-lines file. The reverse mapping:

| Nevergrad JSON field | Corvus Field | Notes |
|---|---|---|
| `#num-tell` | `PerformanceRecord.evaluation_number` | Direct. |
| `#loss` | `PerformanceRecord.objective_value` | Negate if problem is `maximize`. |
| `{variable_name}` | `PerformanceRecord.current_solution[variable_name]` | Reconstruct from named fields. |
| `#optimizer` | `AlgorithmInstance.algorithm_family` (proxy) | Exact class name; may differ from human-readable family label. |

Fields with no Nevergrad equivalent (`elapsed_time`, `is_improvement`, `trigger_reason`,
`run_id`) are set to sensible defaults (`elapsed_time=0.0`, `is_improvement` recomputed
from `best_so_far` sequence, `trigger_reason="tell"`, `run_id` assigned on import).

### §4.3.6 Version compatibility

| Nevergrad version | Supported | Notes |
|---|---|---|
| `nevergrad` ≥ 1.0 | Yes | Reference implementation; `ask()` / `tell()` API stable |
| `nevergrad` 0.x | Yes (best-effort) | Ask-tell API present from early 0.x; `ng.p.Dict` available since 0.4.x |
| `nevergrad` < 0.4 | No | Pre-`ng.p` parametrization API not supported |
