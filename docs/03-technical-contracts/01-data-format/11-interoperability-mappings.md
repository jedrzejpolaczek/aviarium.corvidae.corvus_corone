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

> TODO: REF-TASK-0007 — Nevergrad format mapping spike required before this section can be filled.
