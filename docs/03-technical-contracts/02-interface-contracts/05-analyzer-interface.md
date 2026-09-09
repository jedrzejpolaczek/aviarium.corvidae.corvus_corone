# §4 Analyzer Interface

> Index: [01-index.md](01-index.md)

The Analyzer consumes completed Run data and produces Result Aggregates, statistical test
results, and scoped conclusions. It is separate from the Runner — analysis runs after all
Runs in an Experiment are complete.

→ Used by: researcher (via API/reports), Reporting Layer (C2)

**Design decisions recorded here:**
- **Batch analysis.** `analyze()` requires all Runs in the Experiment to be in
  `status="completed"` or `status="failed"` before it is called. Streaming (incremental
  analysis as Runs complete) is not supported in V1. Callers MUST wait for
  `experiment.status == "completed"` before invoking any Analyzer method.
- **Hypothesis enforcement: convention.** Pre-registered hypotheses are recorded in the
  Study and included in the Report's confirmatory section, but the system does not
  technically prevent the researcher from calling `compare()` with hypotheses not listed
  in the Study. Scientific integrity is the researcher's responsibility (MANIFESTO
  Principle 16). The Report explicitly marks which comparisons were pre-registered and
  which were exploratory.

---

### analyze(experiment_id: str, config: AnalysisConfig) → AnalysisReport

**Signature:**
- `experiment_id: str` — ID of a completed Experiment
- `config: AnalysisConfig` — `{ metric_names: list[str], hypothesis_ids: list[str] }`
- returns: `AnalysisReport` — contains Result Aggregates, statistical test results,
  visualizations, and scoped conclusions

**Semantics:**
Runs the three-level analysis (→ statistical-methodology.md) on all completed Runs in the
specified Experiment. Computes metrics for each `(problem, algorithm)` pair, applies the
specified statistical tests, and generates scoped conclusions.

**Preconditions:**
- `experiment.status == "completed"` — raises `ExperimentNotCompleteError` otherwise
- all `metric_names` in `config` are valid entries in metric-taxonomy.md

**Postconditions:**
- returned `AnalysisReport` contains one `ResultAggregate` per `(problem, algorithm)` pair
- every `ResultAggregate` contains all `metric_names` from `config`
- every conclusion in the report includes an explicit `conclusion_scope` field stating
  which problems and conditions the conclusion applies to (MANIFESTO Principle 3)
- pre-registered hypotheses are marked `"pre_registered": true` in the report;
  any additional comparisons are marked `"pre_registered": false` (exploratory)

**Exceptions:**
- `ExperimentNotCompleteError` — experiment is still running or aborted
- `UnknownMetricError` — a `metric_name` in `config` is not in metric-taxonomy.md

---

### compute_metrics(run_ids: list[str], metric_names: list[str]) → list[ResultAggregate]

**Signature:**
- `run_ids: list[str]` — IDs of completed Runs to aggregate over
- `metric_names: list[str]` — metric names from metric-taxonomy.md
- returns: `list[ResultAggregate]` — one aggregate per `(problem, algorithm)` group found
  in the specified runs

**Semantics:**
Computes specified metrics for specified Runs. Lower-level than `analyze()`; does not run
statistical tests or generate the full report. Used for partial or custom analysis.

**Preconditions:**
- all `run_ids` reference Runs with `status="completed"`
- all `metric_names` are valid entries in metric-taxonomy.md

**Postconditions:**
- every `metric_name` from the input is present in every `ResultAggregate` in the output
- `ResultAggregate.n_runs` equals the count of contributing Runs per group

**Exceptions:**
- `UnknownMetricError` — a `metric_name` is not in metric-taxonomy.md
- `RunNotCompleteError` — a `run_id` references a Run that is not completed

---

### compare(experiment_id: str, algorithm_ids: list[str], metric_name: str, test_config: TestConfig) → StatisticalTestResult

**Signature:**
- `experiment_id: str` — ID of a completed Experiment
- `algorithm_ids: list[str]` — two or more algorithm IDs to compare
- `metric_name: str` — metric name from metric-taxonomy.md
- `test_config: TestConfig` — `{ test: str, alpha: float }` (e.g., `"wilcoxon"`, `0.05`)
- returns: `StatisticalTestResult` — `{ test_name, p_value, effect_size, conclusion_scope, pre_registered }`

**Semantics:**
Applies a specified statistical test to compare algorithms on a single metric.
Two algorithms → Wilcoxon signed-rank test. More than two → Kruskal-Wallis + Holm-Bonferroni
correction (→ statistical-methodology.md §3).

**Preconditions:**
- `experiment.status == "completed"`
- `len(algorithm_ids) ≥ 2`
- `metric_name` is valid in metric-taxonomy.md
- `test_config.alpha` is in `(0, 1)`

**Postconditions:**
- `conclusion_scope` explicitly states which problems and conditions are covered —
  prevents over-generalization (MANIFESTO Principle 3)
- `pre_registered` is `true` if this exact comparison appears in `Study.pre_registered_hypotheses`,
  `false` otherwise (exploratory)
- `effect_size` uses Cliff's delta (→ statistical-methodology.md §4)

**Exceptions:**
- `InsufficientRunsError` — fewer than 2 completed Runs per algorithm for this metric

---

### InterpolationStrategy (abstract)

Pluggable strategy for reconstructing `best_so_far` at an evaluation count that was not
directly logged. The Analyzer holds a reference to an `InterpolationStrategy` and delegates
all gap-filling to it.

→ Decision rationale: [adr-003-anytime-curve-interpolation.md](../../02-design/02-architecture/01-adr/adr-003-anytime-curve-interpolation.md)

#### reconstruct(records: list[PerformanceRecord], eval_number: int) → float

**Signature:**
- `records: list[PerformanceRecord]` — sorted ascending by `evaluation_number`; non-empty
- `eval_number: int` — the evaluation count to reconstruct a value for
- returns: `float` — the reconstructed `best_so_far` value at `eval_number`

**Preconditions:**
- `records` is sorted ascending by `evaluation_number`
- `records` is non-empty (at least the eval-1 record exists per ADR-002)
- `eval_number ≥ 1` and `≤ run.budget_used`

**Postconditions:**
- returned value equals `objective_value` of the most recent record with
  `evaluation_number ≤ eval_number` (Last Observation Carried Forward — the default)

**Default implementation: `LastObservationCarriedForward`**
Returns `records[-1 where evaluation_number ≤ n].objective_value`.
This is the **only** implementation permitted without explicit pre-registration in the
Study record (ADR-003).

**Non-default implementations:**
- must be declared in the Study record before execution begins
- will be labeled in the Report's limitations section (FR-21)
