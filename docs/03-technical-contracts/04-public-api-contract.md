# Public API Facade Contract — corvus_corone

<!--
STORY ROLE: The "researcher-facing handshake". This document defines the complete public
surface of the corvus_corone library as experienced by the scientist calling
`import corvus_corone as cc`. It is the single authoritative source for every function
signature, view object field, exception, and CLI command that a caller can depend on.
Implementors of IMPL-017 read this document first; the interface-contracts describe what
happens internally to fulfil these guarantees.

NARRATIVE POSITION:
  docs/03-technical-contracts/02-interface-contracts/01-interface-contracts.md (internal)
  → 04-public-api-contract.md (external surface, THIS FILE)
  → researcher code, tutorials, contribution guides

CONNECTS TO:
  → docs/03-technical-contracts/02-interface-contracts/01-interface-contracts.md §1–§5 :
      facade delegates to Problem, Algorithm, Runner, Analyzer, Repository interfaces
  → docs/03-technical-contracts/01-data-format/ :
      view objects here are distinct from the storage entities defined there; §2 of that
      document defines the canonical on-disk/DB schemas; view objects here are read-only
      projections for callers
  → docs/03-technical-contracts/03-metric-taxonomy/01-metric-taxonomy.md :
      metric_id keys used in ResultAggregate.metrics come from this taxonomy
  → docs/GLOSSARY.md : all capitalised terms (Study, Experiment, Run, Budget, etc.) are
      defined there and are used here with their exact glossary meanings
  → REF-TASK-0037 : the task that produced this document

GLOSSARY: All terms from docs/GLOSSARY.md apply. Use exact glossary terms.
-->

---

## Audience and Scope

This document is written for **researchers** — scientists and engineers who write Python code
of the form:

```python
import corvus_corone as cc

study = cc.create_study(
    name="My Benchmark Study",
    research_question="Does Algorithm X outperform Algorithm Y on noisy functions?",
    problem_ids=["sphere-d10-noise-gaussian-0.1", "rastrigin-d10-noiseless"],
    algorithm_ids=["cma-es-default", "nelder-mead-default"],
    repetitions=30,
    budget=10_000,
)
experiment = cc.run(study.id)
aggregates = cc.get_result_aggregates(experiment.id)
```

It specifies every function the caller can invoke, every view object those functions return,
the exceptions that may be raised, and the CLI commands available on the command line.

**This document does NOT cover:**

- How any function is implemented internally.
- The storage schemas for Study, Experiment, Run, PerformanceRecord, and ResultAggregate
  entities — those are specified in `docs/03-technical-contracts/01-data-format/`.
- The Problem, Algorithm, Runner, Analyzer, and Repository interfaces — those are specified
  in `docs/03-technical-contracts/02-interface-contracts/`.
- Metric definitions — those are specified in
  `docs/03-technical-contracts/03-metric-taxonomy/01-metric-taxonomy.md`.

Implementors of IMPL-017 (the facade module) must satisfy every contract stated here. The
contracts in `02-interface-contracts/` govern how they do so internally.

---

## Design Decisions

The following five design questions arose during specification. Each decision is recorded
here with its rationale so that future contributors understand why the surface looks the way
it does and do not reopen these questions without cause.

### DQ-1: `create_study()` — Flat Parameters (Decided)

**Question:** Should `create_study()` accept a nested `experimental_design` dict (mirroring
the storage schema in `01-data-format/04-study.md`) or flat keyword arguments?

**Decision: Flat keyword arguments.**

The function signature uses:

```python
cc.create_study(
    *,
    problem_ids: list[str],
    algorithm_ids: list[str],
    repetitions: int,
    budget: int,
    ...
)
```

The arguments `repetitions` and `budget` are direct keyword arguments. There is no
`experimental_design` wrapper dict. The parameter names are `problem_ids` and
`algorithm_ids` (not `problem_instance_ids` / `algorithm_instance_ids`). The V1
stopping criterion is always `budget_exhausted`; no `stopping_criteria` parameter is
exposed. The budget allocation is an integer `budget`; no `budget_allocation` string is
exposed.

**Rationale:** Flat parameters are more Pythonic, fully discoverable via IDE completion and
`help()`, and individually validatable with precise error messages. The `experimental_design`
wrapper adds one nesting level with no benefit in V1; it would force callers to construct a
dict to pass to the function instead of using keyword arguments directly. If V2 introduces
variable budget allocation strategies, a separate keyword argument (`budget_allocation:
str`) can be added without breaking existing callers.

---

### DQ-2: `update_study()` — Takes `study_id: str` (Decided)

**Question:** Should `update_study()` accept a `Study` view object as its first argument
(to mirror the update-by-value pattern used in some ORMs) or a `study_id: str`?

**Decision: `study_id: str`.**

```python
cc.update_study(study_id: str, **fields) -> None
```

**Rationale:** The facade is intentionally stateless — it holds no in-memory Study objects
between calls. All operations identify their subject by ID and fetch the current state from
the repository internally. This is consistent with every other function: `cc.run(study_id)`,
`cc.get_experiment(experiment_id)`, `cc.get_runs(experiment_id)`, and so on all take ID
strings. Passing a `Study` object would require the caller to retain and pass stale objects,
creating a category of "stale object" bugs that do not exist with the ID-based API.

Note: In V1, `update_study()` **always raises `StudyLockedError`** because studies are
immediately locked upon creation. The function exists in the public surface to allow callers
to write future-compatible code and to make the locking policy explicit via a named
exception.

---

### DQ-3: `ResultAggregate` — Field Names and `MetricStatistics` Object (Decided)

**Question (field names):** Should `ResultAggregate` use `.problem_id` / `.algorithm_id` or
`.problem_instance_id` / `.algorithm_instance_id`?

**Decision: `.problem_id` and `.algorithm_id`.**

**Rationale:** These names are consistent with `Run.problem_id` and `Run.algorithm_id`. The
`_instance_` infix adds no disambiguation value at the public API level (callers interact
with IDs, not with ProblemInstance storage entities) and would create inconsistency within
the same API surface.

**Question (metric statistics shape):** Should `agg.metrics["QUALITY-BEST_VALUE_AT_BUDGET"]`
return a plain `dict`, a `dict` with a `.statistics` sub-dict, or a named object?

**Decision: A named `MetricStatistics` object** with attributes `.mean`, `.median`,
`.stdev`, `.q25`, `.q75`.

```python
quality = agg.metrics["QUALITY-BEST_VALUE_AT_BUDGET"]
print(quality.median)
iqr = quality.q75 - quality.q25
```

**Rationale:** Named attributes are refactor-safe (renaming a key in a dict is a silent
breaking change; renaming an attribute causes an `AttributeError` at the call site),
IDE-discoverable via autocomplete, and align with the view object pattern used throughout
this API. Plain dicts are inappropriate for a public API used interactively because they
require callers to remember string keys and offer no type-checker support.

---

### DQ-4: `Experiment.run_ids: list[str]` — Lazy Loading (Decided)

**Question:** Should the `Experiment` view object embed a list of `Run` objects or hold only
a list of run ID strings?

**Decision: `Experiment.run_ids: list[str]`** for lightweight access; full `Run` objects via
`cc.get_runs(experiment_id)`.

**Rationale:** An Experiment in a study with 30 repetitions × 10 problems × 5 algorithms
contains 1 500 Runs. Embedding all Run objects in the Experiment view would make every
`cc.get_experiment()` call load 1 500 objects regardless of whether the caller needs them.
The lazy-loading pattern — IDs in the view object, full objects on an explicit secondary
call — avoids this overhead and is consistent with every other facade function taking IDs.

---

### DQ-5: `Report.report_type`; Exception Namespace via Module Re-Export (Decided)

**Question (Report field):** Should the Report view object expose `.type` or `.report_type`?

**Decision: `Report.report_type`.**

**Rationale:** `type` is a Python builtin. Shadowing it as a dataclass attribute causes
confusion in IDEs, type checkers, and interactive sessions (e.g., `type(report)` becomes
ambiguous in code that also uses `report.type`). The attribute name `report_type` is
unambiguous and consistent with the naming pattern used in this codebase.

**Question (exception namespace):** Should callers be required to write
`from corvus_corone.exceptions import StudyLockedError` or should `cc.StudyLockedError`
work after `import corvus_corone as cc`?

**Decision: Module-level re-export** — both forms work.

Exceptions are defined in `corvus_corone.exceptions` and re-exported from
`corvus_corone.__init__`. The canonical usage is:

```python
import corvus_corone as cc
try:
    cc.update_study(study_id, name="New Name")
except cc.StudyLockedError:
    ...
```

The explicit import also works:
```python
from corvus_corone.exceptions import StudyLockedError
```

**Rationale:** Researchers use `import corvus_corone as cc`; requiring a separate import
for exceptions adds friction and creates a two-namespace mental model. Re-exporting from
`__init__` is a standard Python library pattern (see `requests.exceptions` which also
re-exports from the top-level `requests` namespace).

---

## View Objects

View objects are **frozen dataclasses** — immutable, read-only snapshots returned by facade
functions. They are **not** the storage entities defined in
`docs/03-technical-contracts/01-data-format/`. The storage entities contain fields used for
internal bookkeeping (version, platform metadata, created_by, created_at, etc.) that are
not exposed to callers. View objects present only the fields a researcher needs to interact
with the API.

All view objects are importable from the top-level package:

```python
from corvus_corone import Study, Experiment, Run, ResultAggregate, MetricStatistics, Report
from corvus_corone import ProblemInstanceSummary, AlgorithmInstanceSummary
```

---

### ProblemInstanceSummary

A lightweight summary of a registered problem instance, returned by `cc.list_problems()`
and `cc.get_problem()`.

```python
@dataclass(frozen=True)
class ProblemInstanceSummary:
    id: str
    name: str
    dimensions: int
    noise_level: str
```

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Stable identifier for this problem instance. Pass this value as an element of `problem_ids` in `cc.create_study()`. |
| `name` | `str` | Human-readable display name (e.g., `"Sphere d=10 Gaussian noise σ=0.1"`). |
| `dimensions` | `int` | Number of decision variables (search space dimensionality). Always ≥ 1. |
| `noise_level` | `str` | Describes the noise model applied to objective evaluations. Format: `"<type>_<param>"` for noisy problems (e.g., `"gaussian_0.1"`, `"uniform_0.05"`) or `"none"` for deterministic problems. |

**Notes:**

- `id` values are assigned by the problem registry and are stable across library versions
  unless a breaking change to the problem definition forces a new registration. The metric
  taxonomy document and problem registry documents specify the naming convention.
- `dimensions` is the declared dimensionality of the problem instance. It does not
  vary at runtime.
- `noise_level` is a structured string, not an enum, to allow future noise models without
  a library update. Callers must not parse it programmatically in V1; it is for display
  and filtering only.

**Distinction from storage entity:** The storage entity `ProblemInstance` (defined in
`docs/03-technical-contracts/01-data-format/02-problem-instance.md`) additionally contains
`version`, `provenance`, `code_reference`, `parameter_schema`, `created_at`, and
`created_by`. These fields are omitted from `ProblemInstanceSummary` because they are
not relevant to a researcher selecting problems for a study.

---

### AlgorithmInstanceSummary

A lightweight summary of a registered algorithm instance, returned by
`cc.list_algorithms()` and `cc.get_algorithm()`.

```python
@dataclass(frozen=True)
class AlgorithmInstanceSummary:
    id: str
    name: str
    algorithm_family: str
    configuration_justification: str
```

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Stable identifier for this algorithm instance. Pass this value as an element of `algorithm_ids` in `cc.create_study()`. |
| `name` | `str` | Human-readable display name (e.g., `"CMA-ES default configuration"`). |
| `algorithm_family` | `str` | The family or class of the algorithm (e.g., `"evolution_strategy"`, `"direct_search"`, `"bayesian_optimization"`). Used for filtering via `cc.list_algorithms(family=...)`. |
| `configuration_justification` | `str` | Free-text explanation of why this particular parameter configuration was chosen for this algorithm instance. Required by the scientific practice contracts (Principle 16). |

**Notes:**

- `id` values are stable across library versions unless the algorithm's behaviour changes
  in a way that makes historical comparisons invalid, in which case a new instance is
  registered.
- `configuration_justification` must not be empty. The registry rejects algorithm
  instances with an empty justification at registration time.

**Distinction from storage entity:** The storage entity `AlgorithmInstance` (defined in
`docs/03-technical-contracts/01-data-format/03-algorithm-instance.md`) additionally contains
`version`, `code_reference`, `parameter_schema`, `hyperparameter_values`, `created_at`,
and `created_by`. These fields are omitted from `AlgorithmInstanceSummary`.

---

### Study

A complete snapshot of a study's configuration, returned by `cc.create_study()`.

```python
@dataclass(frozen=True)
class Study:
    id: str
    name: str
    research_question: str
    problem_ids: list[str]
    algorithm_ids: list[str]
    repetitions: int
    budget: int
    seed_strategy: str
    sampling_strategy: str
    improvement_epsilon: float | None
    pre_registered_hypotheses: list[dict]
    status: str
```

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Stable UUID-format identifier. Pass to `cc.run(study_id)` and `cc.update_study(study_id, ...)`. |
| `name` | `str` | Human-readable title provided by the researcher at creation. |
| `research_question` | `str` | The motivating scientific question, free text, provided by the researcher at creation. |
| `problem_ids` | `list[str]` | Ordered list of problem instance IDs included in this study, matching the values passed to `cc.create_study()`. |
| `algorithm_ids` | `list[str]` | Ordered list of algorithm instance IDs included in this study. |
| `repetitions` | `int` | Number of independent Runs per (problem, algorithm) pair. Always ≥ 1. |
| `budget` | `int` | Maximum number of objective function evaluations per Run. Always ≥ 1. |
| `seed_strategy` | `str` | How seeds are generated and assigned across Runs (e.g., `"sequential"`, `"random"`, `"latin-hypercube"`). |
| `sampling_strategy` | `str` | Identifier of the PerformanceRecord sampling strategy (e.g., `"log_scale_plus_improvement"`). |
| `improvement_epsilon` | `float \| None` | Minimum improvement required to trigger an improvement PerformanceRecord. `None` means strict inequality (any improvement is recorded). |
| `pre_registered_hypotheses` | `list[dict]` | Hypotheses declared before data collection. Each dict has at least `"hypothesis"` (str) and `"test_type"` (str) keys. Empty list if none were provided. |
| `status` | `str` | Always `"locked"` after `create_study()`. Studies are immutable once created in V1. |

**Notes:**

- `status` is always `"locked"` in V1. The field exists so that callers can assert this
  and so that future versions can introduce a `"draft"` pre-lock status without removing
  the field.
- The `budget` field corresponds to `experimental_design.budget_allocation` in the storage
  schema but is presented as a plain integer at the public API level, because V1 supports
  only uniform budget allocation.
- `pre_registered_hypotheses` is never `None`; it is an empty list when no hypotheses
  were provided. This avoids a `None`-check pattern in caller code.

**Distinction from storage entity:** The storage entity `Study` (defined in
`docs/03-technical-contracts/01-data-format/04-study.md`) additionally contains `version`,
`research_question_tags`, `experimental_design.stopping_criteria`,
`experimental_design.budget_allocation`, `log_scale_schedule`, `max_records_per_run`,
`created_by`, and `created_at`. These fields are omitted from the view object or folded
into simpler fields (`budget` from `experimental_design`).

---

### Experiment

A snapshot of an experiment's execution status, returned by `cc.run()` and
`cc.get_experiment()`.

```python
@dataclass(frozen=True)
class Experiment:
    id: str
    study_id: str
    status: str
    run_ids: list[str]
```

| Field | Type | Description |
|---|---|---|
| `id` | `str` | UUID-format identifier. Pass to `cc.get_runs()`, `cc.get_result_aggregates()`, `cc.generate_reports()`, and `cc.export_raw_data()`. |
| `study_id` | `str` | ID of the Study that this Experiment realises. |
| `status` | `str` | Execution status. One of `"running"`, `"completed"`, `"failed"`. |
| `run_ids` | `list[str]` | Ordered list of Run IDs belonging to this Experiment. May be empty while the Experiment is in `"running"` status. To retrieve full Run objects, call `cc.get_runs(experiment.id)`. |

**Notes:**

- An Experiment returned by `cc.run()` will have `status="completed"` if all Runs finished
  without error, `"failed"` if any Run failed and the experiment could not recover, or
  `"running"` if the call returns before all Runs complete (not the case in V1 — `cc.run()`
  is synchronous in V1 and always returns a terminal-status Experiment).
- `run_ids` contains IDs in the order the Runs were created. The length equals
  `repetitions × len(problem_ids) × len(algorithm_ids)` for a completed Experiment.

**Distinction from storage entity:** The storage entity `Experiment` (defined in
`docs/03-technical-contracts/01-data-format/05-experiment.md`) additionally contains
`platform`, `started_at`, `completed_at`, `software_environment`, and
`reproducibility_hash`. These fields are omitted from the view object.

---

### Run

A record of a single algorithm execution on a single problem instance with a single seed,
returned as part of `cc.get_runs()`.

```python
@dataclass(frozen=True)
class Run:
    id: str
    experiment_id: str
    problem_id: str
    algorithm_id: str
    seed: int
    budget_used: int
    status: str
    failure_reason: str | None
```

| Field | Type | Description |
|---|---|---|
| `id` | `str` | UUID-format identifier for this Run. |
| `experiment_id` | `str` | ID of the Experiment this Run belongs to. |
| `problem_id` | `str` | ID of the problem instance that was evaluated. Matches an element of `Study.problem_ids`. |
| `algorithm_id` | `str` | ID of the algorithm instance that was run. Matches an element of `Study.algorithm_ids`. |
| `seed` | `int` | The random seed used for this Run. Uniqueness within an Experiment is enforced; a `SeedCollisionError` is raised at execution time if a duplicate would occur. |
| `budget_used` | `int` | Actual number of objective function evaluations consumed. Always ≤ `Study.budget`. |
| `status` | `str` | `"completed"` if the Run finished within budget, `"failed"` if an unrecoverable error occurred. |
| `failure_reason` | `str \| None` | Human-readable description of why the Run failed. `None` for completed Runs. |

**Notes:**

- `budget_used` may be less than `Study.budget` if the algorithm terminated early (e.g.,
  converged before exhausting the budget). It is never greater than `Study.budget`.
- `failure_reason` is a diagnostic string intended for human reading, not for programmatic
  parsing. Its exact format is not part of this contract and may change between versions.
- A Run with `status="failed"` is still included in `cc.get_runs()`. Callers should filter
  by `status` if they want only successful Runs.

**Distinction from storage entity:** The storage entity `Run` (defined in
`docs/03-technical-contracts/01-data-format/06-run.md`) additionally contains
`started_at`, `completed_at`, `platform_snapshot`, `cap_reached_at_evaluation`, and a
reference to the PerformanceRecord collection. PerformanceRecords are not exposed via the
public API in V1; raw data is accessed via `cc.export_raw_data()`.

---

### MetricStatistics

A set of summary statistics for a single metric across all Runs within one
(problem, algorithm) cell of an Experiment. Accessed as values in
`ResultAggregate.metrics`.

```python
@dataclass(frozen=True)
class MetricStatistics:
    mean: float
    median: float
    stdev: float
    q25: float
    q75: float
```

| Field | Type | Description |
|---|---|---|
| `mean` | `float` | Arithmetic mean of the metric value across all non-failed Runs in the cell. |
| `median` | `float` | Median (50th percentile) of the metric value across all non-failed Runs in the cell. |
| `stdev` | `float` | Sample standard deviation (N−1 denominator). `0.0` if only one Run contributed. |
| `q25` | `float` | 25th percentile (first quartile) of the metric value distribution. |
| `q75` | `float` | 75th percentile (third quartile) of the metric value distribution. |

**Notes:**

- All statistics are computed over non-failed Runs only. If all Runs in a cell failed,
  the corresponding `ResultAggregate` is not created and does not appear in
  `cc.get_result_aggregates()`.
- The inter-quartile range is `q75 - q25`. This is intentionally not a pre-computed field
  to keep the object minimal.
- `stdev` uses the sample standard deviation (Bessel's correction, N−1 denominator) for
  consistency with statistical practice. For a single Run, `stdev=0.0`.

**Typical usage:**

```python
aggregates = cc.get_result_aggregates(experiment_id)
for agg in aggregates:
    quality = agg.metrics.get("QUALITY-BEST_VALUE_AT_BUDGET")
    if quality is not None:
        print(f"{agg.problem_id} / {agg.algorithm_id}: "
              f"median={quality.median:.4f}, IQR={quality.q75 - quality.q25:.4f}")
```

---

### ResultAggregate

Aggregated metric statistics for one (problem, algorithm) cell of an Experiment, returned
by `cc.get_result_aggregates()`.

```python
@dataclass(frozen=True)
class ResultAggregate:
    id: str
    experiment_id: str
    problem_id: str
    algorithm_id: str
    n_runs: int
    metrics: dict[str, MetricStatistics]
```

| Field | Type | Description |
|---|---|---|
| `id` | `str` | UUID-format identifier for this ResultAggregate. |
| `experiment_id` | `str` | ID of the Experiment this aggregate belongs to. |
| `problem_id` | `str` | ID of the problem instance this aggregate covers. |
| `algorithm_id` | `str` | ID of the algorithm instance this aggregate covers. |
| `n_runs` | `int` | Number of non-failed Runs that contributed to these statistics. May be less than `Study.repetitions` if some Runs failed. |
| `metrics` | `dict[str, MetricStatistics]` | Map from metric ID (as defined in `docs/03-technical-contracts/03-metric-taxonomy/01-metric-taxonomy.md`) to a `MetricStatistics` object. Keys follow the format `CATEGORY-METRIC_NAME` (e.g., `"QUALITY-BEST_VALUE_AT_BUDGET"`, `"TIME-EVALUATIONS_TO_TARGET"`). |

**Notes:**

- A `ResultAggregate` is created for each (problem_id, algorithm_id) pair in the
  Experiment for which at least one Run completed successfully.
- The set of metric IDs present in `metrics` depends on which metrics are applicable to
  the problem type and which Runs produced sufficient data. Not all metrics are guaranteed
  to be present for every aggregate. Callers should use `agg.metrics.get(metric_id)` and
  handle `None`.
- Metric IDs are the stable identifiers from the metric taxonomy. They do not change
  between versions; if a metric is deprecated, it is removed from new aggregates but
  the ID is preserved in the taxonomy document.

**Distinction from storage entity:** The storage entity `ResultAggregate` (defined in
`docs/03-technical-contracts/01-data-format/08-result-aggregate.md`) stores metrics as a
flat list of `{metric_id, aggregate_value, n_runs}` records. The view object groups all
metrics for a (problem, algorithm) cell into a single object with a `dict[str,
MetricStatistics]` field, which is more convenient for interactive analysis.

---

### Report

A reference to a generated analysis report artifact, returned by
`cc.generate_reports()`.

```python
@dataclass(frozen=True)
class Report:
    id: str
    experiment_id: str
    report_type: str
    artifact_reference: str
    has_limitations_section: bool
```

| Field | Type | Description |
|---|---|---|
| `id` | `str` | UUID-format identifier for this Report. |
| `experiment_id` | `str` | ID of the Experiment this Report covers. |
| `report_type` | `str` | Audience for this report. `"researcher"` — full statistical detail including confidence intervals, effect sizes, and hypothesis test results. `"practitioner"` — summary of findings oriented toward practitioners, without raw statistical tables. |
| `artifact_reference` | `str` | Absolute file path to the generated report file (HTML or PDF). The file is guaranteed to exist at this path at the time `cc.generate_reports()` returns. |
| `has_limitations_section` | `bool` | `True` if the report includes a limitations section (required when `improvement_epsilon` is non-null or `max_records_per_run` was set; automatically `True` in those cases). |

**Notes:**

- `report_type` is intentionally a `str` rather than an enum to allow future report
  audience types without a breaking API change.
- `artifact_reference` is an absolute path. Callers should not construct it from parts;
  use it as-is to open or display the report.
- A call to `cc.generate_reports()` always returns exactly two `Report` objects — one
  with `report_type="researcher"` and one with `report_type="practitioner"`.
- `has_limitations_section` reflects the generated content; callers can use it to decide
  whether to surface a warning to end users.

**Distinction from storage entity:** The storage entity `Report` (defined in
`docs/03-technical-contracts/01-data-format/09-report.md`) additionally contains
`content_format`, `generated_at`, `generator_version`, and `schema_version`. These fields
are omitted from the view object.

---

## Module-Level Functions

All functions are available at the top-level namespace after `import corvus_corone as cc`.
All functions are **synchronous** in V1. None mutates shared state visible to callers.

---

### cc.list_problems()

Returns a list of all registered problem instances, optionally filtered by tags.

**Signature:**

```python
def list_problems(*, tags: list[str] | None = None) -> list[ProblemInstanceSummary]:
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `tags` | `list[str] \| None` | No | `None` | If provided, only problem instances that match **all** of the given tags are returned. Tags are free-form strings registered with each problem instance (e.g., `"continuous"`, `"noisy"`, `"multimodal"`, `"d=10"`). If `None`, all registered problem instances are returned. |

**Returns:** `list[ProblemInstanceSummary]` — zero or more problem instance summaries.
The list is ordered by problem instance ID lexicographically. Returns an empty list if no
problems match the filter; never returns `None`.

**Raises:** This function does not raise any application-level exceptions. An empty result
is a valid, non-exceptional outcome.

**Example:**

```python
import corvus_corone as cc

# All registered problems
all_problems = cc.list_problems()

# Only noisy, continuous problems
noisy_continuous = cc.list_problems(tags=["noisy", "continuous"])
for p in noisy_continuous:
    print(f"{p.id}: {p.name} (dim={p.dimensions}, noise={p.noise_level})")
```

---

### cc.list_algorithms()

Returns a list of all registered algorithm instances, optionally filtered by algorithm
family.

**Signature:**

```python
def list_algorithms(*, family: str | None = None) -> list[AlgorithmInstanceSummary]:
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `family` | `str \| None` | No | `None` | If provided, only algorithm instances whose `algorithm_family` exactly matches this string are returned. If `None`, all registered algorithm instances are returned. |

**Returns:** `list[AlgorithmInstanceSummary]` — zero or more algorithm instance summaries.
The list is ordered by algorithm instance ID lexicographically. Returns an empty list if no
algorithms match the filter; never returns `None`.

**Raises:** This function does not raise any application-level exceptions.

**Example:**

```python
import corvus_corone as cc

# All registered algorithms
all_algs = cc.list_algorithms()

# Only evolution-strategy family algorithms
es_algs = cc.list_algorithms(family="evolution_strategy")
for alg in es_algs:
    print(f"{alg.id}: {alg.name}")
    print(f"  Justification: {alg.configuration_justification}")
```

---

### cc.get_problem()

Retrieves a single problem instance by ID.

**Signature:**

```python
def get_problem(problem_id: str) -> ProblemInstanceSummary:
```

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `problem_id` | `str` | Yes | The ID of the problem instance to retrieve. Must be a non-empty string. |

**Returns:** `ProblemInstanceSummary` — the problem instance with the given ID.

**Raises:**

| Exception | When |
|---|---|
| `cc.NotFoundError` | No problem instance with `problem_id` exists in the registry. |

**Example:**

```python
import corvus_corone as cc

try:
    problem = cc.get_problem("sphere-d10-noiseless")
    print(f"Name: {problem.name}")
    print(f"Dimensions: {problem.dimensions}")
    print(f"Noise: {problem.noise_level}")
except cc.NotFoundError as e:
    print(f"Problem not found: {e}")
```

---

### cc.get_algorithm()

Retrieves a single algorithm instance by ID.

**Signature:**

```python
def get_algorithm(algorithm_id: str) -> AlgorithmInstanceSummary:
```

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `algorithm_id` | `str` | Yes | The ID of the algorithm instance to retrieve. Must be a non-empty string. |

**Returns:** `AlgorithmInstanceSummary` — the algorithm instance with the given ID.

**Raises:**

| Exception | When |
|---|---|
| `cc.NotFoundError` | No algorithm instance with `algorithm_id` exists in the registry. |

**Example:**

```python
import corvus_corone as cc

try:
    alg = cc.get_algorithm("cma-es-default")
    print(f"Name: {alg.name}")
    print(f"Family: {alg.algorithm_family}")
    print(f"Justification: {alg.configuration_justification}")
except cc.NotFoundError as e:
    print(f"Algorithm not found: {e}")
```

---

### cc.create_study()

Creates and locks a new benchmarking study. The study is immediately locked upon creation;
no further modifications are possible in V1.

**Signature:**

```python
def create_study(
    *,
    name: str,
    research_question: str,
    problem_ids: list[str],
    algorithm_ids: list[str],
    repetitions: int,
    budget: int,
    seed_strategy: str = "sequential",
    sampling_strategy: str = "log_scale_plus_improvement",
    log_scale_schedule: dict | None = None,
    improvement_epsilon: float | None = None,
    pre_registered_hypotheses: list[dict] | None = None,
    max_records_per_run: int | None = None,
) -> Study:
```

All parameters are keyword-only (enforced by the leading `*`).

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | `str` | Yes | — | Human-readable title for the study. Must be non-empty. |
| `research_question` | `str` | Yes | — | The motivating scientific question. Must be non-empty. |
| `problem_ids` | `list[str]` | Yes | — | One or more problem instance IDs. Each ID must exist in the registry; a `ValidationError` is raised if any ID is unknown. Must contain at least 1 element. |
| `algorithm_ids` | `list[str]` | Yes | — | One or more algorithm instance IDs. Each ID must exist in the registry. Must contain at least 1 element. |
| `repetitions` | `int` | Yes | — | Number of independent Runs per (problem, algorithm) pair. Must be ≥ 1. |
| `budget` | `int` | Yes | — | Maximum objective function evaluations per Run. Must be ≥ 1. |
| `seed_strategy` | `str` | No | `"sequential"` | How seeds are generated across Runs. Valid values: `"sequential"` (seeds are 0, 1, 2, … in creation order), `"random"` (seeds drawn from a PRNG), `"latin-hypercube"` (seeds assigned via Latin hypercube sampling). |
| `sampling_strategy` | `str` | No | `"log_scale_plus_improvement"` | Identifier of the PerformanceRecord sampling strategy. Valid values: `"log_scale_plus_improvement"` (default), `"log_scale_only"`, `"every_evaluation"`. See `docs/02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md`. |
| `log_scale_schedule` | `dict \| None` | No | `None` | Parameters for the log-scale trigger. Fields: `base_points: list[int]` (default `[1, 2, 5]`), `multiplier_base: int` (default `10`). If `None`, the defaults are used. Ignored when `sampling_strategy="every_evaluation"`. |
| `improvement_epsilon` | `float \| None` | No | `None` | Minimum improvement required to trigger an improvement PerformanceRecord. `None` means any strictly better value triggers a record. Non-null values must be scientifically justified and are noted in the Report limitations section automatically. Must be ≥ 0.0 if non-null. |
| `pre_registered_hypotheses` | `list[dict] \| None` | No | `None` | Hypotheses declared before data collection. Each dict must have at least `"hypothesis"` (str) and `"test_type"` (str) keys. If `None`, treated as an empty list in the returned `Study`. |
| `max_records_per_run` | `int \| None` | No | `None` | Optional hard cap on PerformanceRecords per Run. `None` means no cap. If set, must be ≥ 1. A cap triggers a limitations note in all generated Reports. |

**Returns:** `Study` — the newly created and locked study. `study.status` is always
`"locked"`.

**Raises:**

| Exception | When |
|---|---|
| `cc.ValidationError` | Any required parameter is missing or invalid. Specific cases: `name` or `research_question` is empty; `problem_ids` or `algorithm_ids` is empty; any ID in `problem_ids` or `algorithm_ids` does not exist in the registry; `repetitions < 1`; `budget < 1`; `seed_strategy` is not a recognised value; `sampling_strategy` is not a recognised value; `improvement_epsilon` is non-null and `< 0.0`; `max_records_per_run` is non-null and `< 1`; `log_scale_schedule` contains unrecognised keys or invalid values. |

**Example:**

```python
import corvus_corone as cc

try:
    study = cc.create_study(
        name="CMA-ES vs Nelder-Mead on Noisy Sphere",
        research_question=(
            "Does CMA-ES achieve lower median objective value than Nelder-Mead "
            "at budget 10 000 on the noisy sphere with Gaussian noise σ=0.1?"
        ),
        problem_ids=["sphere-d10-noise-gaussian-0.1"],
        algorithm_ids=["cma-es-default", "nelder-mead-default"],
        repetitions=30,
        budget=10_000,
        seed_strategy="sequential",
        pre_registered_hypotheses=[
            {
                "hypothesis": "CMA-ES achieves lower median QUALITY-BEST_VALUE_AT_BUDGET.",
                "test_type": "wilcoxon_signed_rank",
            }
        ],
    )
    print(f"Study created: {study.id}")
    print(f"Status: {study.status}")   # always "locked"
except cc.ValidationError as e:
    print(f"Invalid study configuration: {e}")
```

---

### cc.update_study()

Attempts to update fields of an existing study. In V1, this function always raises
`StudyLockedError` because all studies are locked upon creation. The function exists to
make the locking policy explicit and to allow future-compatible code.

**Signature:**

```python
def update_study(study_id: str, **fields) -> None:
```

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `study_id` | `str` | Yes | The ID of the study to update. |
| `**fields` | — | No | Field names and new values (e.g., `name="New Name"`). In V1, no field updates are applied; the function always raises before processing any fields. |

**Returns:** `None`

**Raises:**

| Exception | When |
|---|---|
| `cc.StudyLockedError` | Always in V1. Studies are locked immediately upon creation and cannot be modified. |
| `cc.NotFoundError` | If `study_id` does not correspond to any existing study (checked before the lock check). |

**Example:**

```python
import corvus_corone as cc

study = cc.create_study(
    name="Initial Name",
    research_question="...",
    problem_ids=["sphere-d10-noiseless"],
    algorithm_ids=["cma-es-default"],
    repetitions=10,
    budget=1000,
)

try:
    cc.update_study(study.id, name="Updated Name")
except cc.StudyLockedError:
    print("Cannot update: study is locked.")
    # Expected in V1 — handle gracefully
```

---

### cc.run()

Executes all Runs for a Study and returns the resulting Experiment. This function is
synchronous in V1 — it blocks until all Runs have completed.

**Signature:**

```python
def run(study_id: str) -> Experiment:
```

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `study_id` | `str` | Yes | The ID of the Study to execute. The Study must exist and have `status="locked"`. |

**Returns:** `Experiment` — the completed (or failed) experiment. `experiment.status` is
`"completed"` if all Runs succeeded, `"failed"` if at least one Run failed and the
experiment could not recover. In either case, `experiment.run_ids` is populated with all
Run IDs that were created.

**Raises:**

| Exception | When |
|---|---|
| `cc.NotFoundError` | `study_id` does not correspond to any existing Study. |
| `cc.SeedCollisionError` | A duplicate seed would be assigned to two Runs within the same Experiment. This is a configuration error in the seed strategy; it should not occur with the default `"sequential"` strategy. |

**Notes:**

- Individual Run failures (e.g., algorithm crashes, numerical errors) do not cause
  `cc.run()` to raise. They are recorded as `Run.status="failed"` with a
  `Run.failure_reason`, and the Experiment continues. Only the `Experiment.status` field
  reflects the overall outcome.
- `BudgetExhaustedError` is raised internally by `Problem.evaluate()` when a Run's budget
  is consumed; it is caught by the Runner and recorded as a normal Run completion (not a
  failure). It does not propagate to the caller of `cc.run()`.
- The total number of Runs created is `repetitions × len(problem_ids) × len(algorithm_ids)`.

**Example:**

```python
import corvus_corone as cc

study = cc.create_study(
    name="My Study",
    research_question="...",
    problem_ids=["sphere-d10-noiseless"],
    algorithm_ids=["cma-es-default"],
    repetitions=30,
    budget=10_000,
)

try:
    experiment = cc.run(study.id)
    print(f"Experiment {experiment.id}: {experiment.status}")
    print(f"Runs: {len(experiment.run_ids)}")
except cc.NotFoundError:
    print("Study not found.")
except cc.SeedCollisionError as e:
    print(f"Seed collision detected: {e}")
```

---

### cc.get_experiment()

Retrieves an Experiment by ID.

**Signature:**

```python
def get_experiment(experiment_id: str) -> Experiment:
```

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `experiment_id` | `str` | Yes | The ID of the Experiment to retrieve. |

**Returns:** `Experiment` — the experiment with the given ID.

**Raises:**

| Exception | When |
|---|---|
| `cc.NotFoundError` | No Experiment with `experiment_id` exists. |

**Example:**

```python
import corvus_corone as cc

try:
    experiment = cc.get_experiment("3f2e1a00-...")
    print(f"Status: {experiment.status}")
    print(f"Runs: {len(experiment.run_ids)}")
except cc.NotFoundError:
    print("Experiment not found.")
```

---

### cc.get_runs()

Retrieves all Runs belonging to an Experiment.

**Signature:**

```python
def get_runs(experiment_id: str) -> list[Run]:
```

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `experiment_id` | `str` | Yes | The ID of the Experiment whose Runs to retrieve. |

**Returns:** `list[Run]` — all Runs belonging to the Experiment, ordered by Run ID
lexicographically. Includes both `"completed"` and `"failed"` Runs. Returns an empty list
if the Experiment has no Runs (e.g., execution has not started); never returns `None`.

**Raises:**

| Exception | When |
|---|---|
| `cc.NotFoundError` | No Experiment with `experiment_id` exists. |

**Example:**

```python
import corvus_corone as cc

runs = cc.get_runs(experiment_id)
completed = [r for r in runs if r.status == "completed"]
failed = [r for r in runs if r.status == "failed"]

print(f"Completed: {len(completed)}, Failed: {len(failed)}")

for r in failed:
    print(f"  Run {r.id} failed: {r.failure_reason}")
```

---

### cc.get_result_aggregates()

Retrieves all ResultAggregates computed for an Experiment.

**Signature:**

```python
def get_result_aggregates(experiment_id: str) -> list[ResultAggregate]:
```

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `experiment_id` | `str` | Yes | The ID of the Experiment whose aggregates to retrieve. |

**Returns:** `list[ResultAggregate]` — one `ResultAggregate` per (problem_id, algorithm_id)
cell for which at least one Run completed successfully. The list is ordered by
(problem_id, algorithm_id) lexicographically. Returns an empty list if no aggregates have
been computed yet; never returns `None`.

**Raises:**

| Exception | When |
|---|---|
| `cc.NotFoundError` | No Experiment with `experiment_id` exists. |

**Example:**

```python
import corvus_corone as cc

aggregates = cc.get_result_aggregates(experiment_id)
for agg in aggregates:
    quality = agg.metrics.get("QUALITY-BEST_VALUE_AT_BUDGET")
    if quality is not None:
        print(
            f"problem={agg.problem_id}, algorithm={agg.algorithm_id}, "
            f"n_runs={agg.n_runs}, "
            f"median quality={quality.median:.4f}, "
            f"IQR={quality.q75 - quality.q25:.4f}"
        )
```

---

### cc.generate_reports()

Generates analysis reports for an Experiment and returns references to the generated
artifacts.

**Signature:**

```python
def generate_reports(experiment_id: str) -> list[Report]:
```

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `experiment_id` | `str` | Yes | The ID of the Experiment for which to generate reports. The Experiment must have `status="completed"`. |

**Returns:** `list[Report]` — exactly two `Report` objects: one with
`report_type="researcher"` and one with `report_type="practitioner"`. Both are guaranteed
to reference existing files at the time the function returns.

**Raises:**

| Exception | When |
|---|---|
| `cc.NotFoundError` | No Experiment with `experiment_id` exists, or the Experiment exists but has no ResultAggregates (i.e., analysis has not been run). |

**Notes:**

- Reports are regenerated on each call. If reports already exist for the Experiment, they
  are overwritten.
- The report for `report_type="researcher"` includes full statistical tables, confidence
  intervals, effect sizes, hypothesis test results, and (if applicable) a limitations
  section.
- The report for `report_type="practitioner"` includes a plain-language summary of
  findings without raw statistical tables.
- If `Study.improvement_epsilon` is non-null or `Study.max_records_per_run` is set,
  `has_limitations_section=True` on both reports.

**Example:**

```python
import corvus_corone as cc
import webbrowser

reports = cc.generate_reports(experiment_id)
for report in reports:
    print(f"[{report.report_type}] {report.artifact_reference}")
    if report.report_type == "researcher":
        webbrowser.open(report.artifact_reference)
```

---

### cc.export_raw_data()

Exports all raw PerformanceRecord data for an Experiment to a file.

**Signature:**

```python
def export_raw_data(experiment_id: str, *, format: str = "json") -> str:
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `experiment_id` | `str` | Yes | — | The ID of the Experiment whose raw data to export. |
| `format` | `str` | No | `"json"` | Output format. Valid values: `"json"` (a JSON file with one record per PerformanceRecord), `"csv"` (a flat CSV file). Additional formats may be added in future versions. |

**Returns:** `str` — the absolute path to the exported file. The file is guaranteed to exist
at this path at the time the function returns.

**Raises:**

| Exception | When |
|---|---|
| `cc.NotFoundError` | No Experiment with `experiment_id` exists. |
| `cc.UnsupportedFormatError` | `format` is not one of the recognised values (`"json"`, `"csv"`). |
| `cc.ExportValidationError` | The exported data is missing mandatory fields (e.g., `eval_number`, `objective_value`, `run_id`). This indicates a data integrity problem in the repository. |

**Example:**

```python
import corvus_corone as cc
import json

try:
    output_path = cc.export_raw_data(experiment_id, format="json")
    print(f"Exported to: {output_path}")

    with open(output_path) as f:
        records = json.load(f)
    print(f"Total PerformanceRecords: {len(records)}")

except cc.UnsupportedFormatError as e:
    print(f"Unknown format: {e}")
except cc.ExportValidationError as e:
    print(f"Data integrity error: {e}")
```

---

## Exception Hierarchy

All exceptions are defined in `corvus_corone.exceptions` and re-exported from
`corvus_corone.__init__`. Both import forms work:

```python
import corvus_corone as cc
cc.StudyLockedError          # works

from corvus_corone.exceptions import StudyLockedError  # also works
```

All exceptions inherit from `corvus_corone.exceptions.CorvusCoroneError`, which is the
base class for all library-specific errors. This allows callers to catch all library errors
with a single `except cc.CorvusCoroneError` if needed.

```
corvus_corone.exceptions.CorvusCoroneError   (base class)
├── StudyLockedError
├── SeedCollisionError
├── BudgetExhaustedError
├── NotFoundError
├── ValidationError
├── UnsupportedFormatError
└── ExportValidationError
```

---

### StudyLockedError

**Inherits from:** `CorvusCoroneError`

**Raised by:** `cc.update_study()`

**When:** Always in V1, because all studies are locked immediately upon creation and cannot
be modified. The exception signals that the requested mutation was rejected because the
study's lock is in effect.

**Message format:** `"Study <study_id> is locked and cannot be modified."`

**Caller guidance:** Catch this exception when calling `cc.update_study()` and inform the
user that studies are immutable once created. If the researcher needs a different
configuration, they must call `cc.create_study()` with the desired parameters.

---

### SeedCollisionError

**Inherits from:** `CorvusCoroneError`

**Raised by:** `cc.run()`

**When:** A duplicate seed would be assigned to two Runs within the same Experiment. The
seed strategy is expected to generate unique seeds; a collision indicates a misconfiguration
of a custom seed strategy or an edge case in `"random"` mode with a very small seed space.
This exception is not raised with the default `"sequential"` seed strategy.

**Message format:** `"Seed collision detected in Experiment <experiment_id>: seed <seed> would be assigned to multiple Runs."`

**Caller guidance:** If using a custom seed strategy, ensure it generates unique seeds for
`repetitions × len(problem_ids) × len(algorithm_ids)` Runs. If using `"random"`,
the probability of collision is negligible for any realistic repetition count.

---

### BudgetExhaustedError

**Inherits from:** `CorvusCoroneError`

**Raised by:** `Problem.evaluate()` internally (the interface method defined in
`docs/03-technical-contracts/02-interface-contracts/02-problem-interface.md`).

**When:** A Run has consumed its full evaluation budget and `Problem.evaluate()` is called
again. This is the normal termination condition for a Run, not an error from the caller's
perspective.

**Propagation:** This exception is caught by the Runner (see
`docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`) and recorded
as a normal Run completion (`Run.status="completed"` with the budget fully used). It does
**not** propagate to the caller of `cc.run()`. It is documented here because it appears in
the exception hierarchy and may be visible in Runner-level logs.

**Caller guidance:** Callers of `cc.run()` do not need to handle this exception. It is
documented for the benefit of Problem implementors and Runner implementors.

---

### NotFoundError

**Inherits from:** `CorvusCoroneError`

**Raised by:** `cc.get_problem()`, `cc.get_algorithm()`, `cc.get_experiment()`,
`cc.get_runs()`, `cc.get_result_aggregates()`, `cc.generate_reports()`,
`cc.export_raw_data()`, `cc.update_study()`

**When:** The requested entity does not exist in the repository. The ID passed by the caller
is not associated with any stored entity of the expected type.

**Message format:** `"<EntityType> with id '<id>' not found."`
(e.g., `"Experiment with id '3f2e1a00-...' not found."`)

**Caller guidance:** Verify the ID value. IDs are returned by `create_study()` and `run()`;
they should not be constructed manually. If an ID was stored externally (e.g., in a script),
confirm it was not truncated or modified.

---

### ValidationError

**Inherits from:** `CorvusCoroneError`

**Raised by:** `cc.create_study()`

**When:** One or more parameters passed to `create_study()` are invalid. Specific cases:

- `name` or `research_question` is an empty string.
- `problem_ids` or `algorithm_ids` is an empty list.
- Any ID in `problem_ids` does not exist in the problem registry.
- Any ID in `algorithm_ids` does not exist in the algorithm registry.
- `repetitions < 1`.
- `budget < 1`.
- `seed_strategy` is not one of the recognised values.
- `sampling_strategy` is not one of the recognised values.
- `improvement_epsilon` is non-null and `< 0.0`.
- `max_records_per_run` is non-null and `< 1`.
- `log_scale_schedule` contains unrecognised keys or has values of the wrong type.
- Any entry in `pre_registered_hypotheses` is missing the required `"hypothesis"` or
  `"test_type"` keys.

**Message format:** `"Validation error in create_study(): <field>: <reason>."`
(e.g., `"Validation error in create_study(): problem_ids: unknown problem id 'foo-bar'."`)

**Caller guidance:** Read the message to identify which parameter is invalid. Fix the
parameter value and retry. If the error mentions an unknown problem or algorithm ID, use
`cc.list_problems()` or `cc.list_algorithms()` to discover valid IDs.

---

### UnsupportedFormatError

**Inherits from:** `CorvusCoroneError`

**Raised by:** `cc.export_raw_data()`

**When:** The `format` argument is not one of the supported values (`"json"`, `"csv"`).

**Message format:** `"Unsupported export format: '<format>'. Supported formats: json, csv."`

**Caller guidance:** Use one of the documented format strings. Do not construct format
strings dynamically from user input without validation.

---

### ExportValidationError

**Inherits from:** `CorvusCoroneError`

**Raised by:** `cc.export_raw_data()`

**When:** During export, one or more PerformanceRecords are missing mandatory fields
(`eval_number`, `objective_value`, `run_id`). This indicates a data integrity problem in
the repository — the stored data does not conform to the schema defined in
`docs/03-technical-contracts/01-data-format/07-performance-record.md`.

**Message format:** `"Export validation failed for Experiment '<experiment_id>': Run '<run_id>': PerformanceRecord '<record_id>' is missing field '<field_name>'."`

**Caller guidance:** This exception indicates a bug in the Runner or Repository
implementation, not a caller error. Report it as a bug with the full exception message.
The exported file is not written when this exception is raised; no partial output is
produced.

---

## CLI Command Surface

The `corvus` command-line tool is installed alongside the `corvus_corone` Python package.
All commands operate on the same repository as the Python API. Exit codes follow standard
Unix conventions: 0 for success, non-zero for error.

### Common Exit Codes

| Code | Meaning |
|---|---|
| `0` | Command completed successfully. |
| `1` | General error (invalid arguments, validation failure). |
| `2` | Entity not found (equivalent to `NotFoundError`). |
| `3` | Locked entity error (equivalent to `StudyLockedError`). |
| `4` | Unsupported format (equivalent to `UnsupportedFormatError`). |
| `5` | Export validation failure (equivalent to `ExportValidationError`). |
| `10` | Seed collision error (equivalent to `SeedCollisionError`). |

---

### corvus run

Executes all Runs for a Study and prints the resulting Experiment ID.

**Synopsis:**

```
corvus run <study_id>
```

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `<study_id>` | Yes | The ID of the Study to execute. |

**Output:** On success, prints the Experiment ID to stdout:

```
Experiment 3f2e1a00-... completed. 300 runs finished (300 completed, 0 failed).
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Experiment completed; all Runs finished (including those with `status="failed"` — individual Run failures do not produce a non-zero exit code unless the whole Experiment fails). |
| `1` | `<study_id>` argument is missing or malformed. |
| `2` | No Study with `<study_id>` exists. |
| `10` | Seed collision detected during execution. |

---

### corvus list-problems

Lists all registered problem instances.

**Synopsis:**

```
corvus list-problems [--tag <tag> ...]
```

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `--tag <tag>` | No | Filter by tag. May be specified multiple times. Only problem instances matching all given tags are shown. |

**Output:** A table with columns `ID`, `NAME`, `DIM`, `NOISE` printed to stdout. One row
per matching problem instance.

```
ID                                    NAME                          DIM  NOISE
----                                  ----                          ---  -----
sphere-d10-noise-gaussian-0.1         Sphere d=10 Gaussian σ=0.1    10   gaussian_0.1
sphere-d10-noiseless                  Sphere d=10 noiseless          10   none
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Command completed. Zero matching results is not an error. |
| `1` | Invalid `--tag` usage. |

---

### corvus list-algorithms

Lists all registered algorithm instances.

**Synopsis:**

```
corvus list-algorithms [--family <family>]
```

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `--family <family>` | No | Filter to only algorithm instances with the given `algorithm_family` value. |

**Output:** A table with columns `ID`, `NAME`, `FAMILY` printed to stdout.

```
ID                  NAME                       FAMILY
--                  ----                       ------
cma-es-default      CMA-ES default config      evolution_strategy
nelder-mead-default Nelder-Mead default config  direct_search
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Command completed. Zero matching results is not an error. |
| `1` | Invalid `--family` usage. |

---

### corvus report

Generates analysis reports for an Experiment.

**Synopsis:**

```
corvus report <experiment_id> [--open]
```

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `<experiment_id>` | Yes | The ID of the Experiment for which to generate reports. |
| `--open` | No | If specified, opens the researcher report in the system's default web browser after generation. |

**Output:** On success, prints the paths to the generated report files:

```
[researcher]    /path/to/reports/experiment-3f2e1a00-researcher.html
[practitioner]  /path/to/reports/experiment-3f2e1a00-practitioner.html
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Reports generated successfully. |
| `1` | `<experiment_id>` argument is missing or malformed. |
| `2` | No Experiment with `<experiment_id>` exists, or the Experiment has no ResultAggregates. |

---

### corvus verify

Verifies the integrity of an Experiment's data — checks that all Runs have the required
PerformanceRecord fields and that ResultAggregates are consistent with Run data.

**Synopsis:**

```
corvus verify <experiment_id>
```

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `<experiment_id>` | Yes | The ID of the Experiment to verify. |

**Output:** On success, prints a summary of the verification:

```
Experiment 3f2e1a00-...: OK
  300 runs verified.
  0 integrity issues found.
```

If issues are found, each issue is printed to stderr with a description:

```
Experiment 3f2e1a00-...: FAILED
  300 runs verified.
  3 integrity issues found.
  ERROR: Run 'abc-...': PerformanceRecord 'xyz-...' missing field 'objective_value'.
  ERROR: Run 'def-...': PerformanceRecord 'uvw-...' missing field 'eval_number'.
  ...
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Verification passed; no integrity issues. |
| `2` | No Experiment with `<experiment_id>` exists. |
| `5` | One or more integrity issues were found. |

---

### corvus export

Exports raw PerformanceRecord data for an Experiment to a file.

**Synopsis:**

```
corvus export <experiment_id> [--format <format>] [--output <path>]
```

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `<experiment_id>` | Yes | The ID of the Experiment whose data to export. |
| `--format <format>` | No | Output format. One of `json` (default) or `csv`. |
| `--output <path>` | No | Output file path. If not specified, a default path in the current working directory is used: `experiment-<id>.<format>`. |

**Output:** On success, prints the path to the exported file:

```
Exported 45 000 PerformanceRecords to /path/to/experiment-3f2e1a00.json
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Export completed successfully. |
| `1` | `<experiment_id>` argument is missing, or `--output` path is not writable. |
| `2` | No Experiment with `<experiment_id>` exists. |
| `4` | `--format` specifies an unsupported format. |
| `5` | Export validation failed due to missing mandatory fields in stored data. |

---

## Relation to Other Contracts

### Relation to Interface Contracts (`02-interface-contracts/`)

The facade (`corvus_corone`) is a thin coordination layer that delegates to the five
component interfaces defined in
`docs/03-technical-contracts/02-interface-contracts/01-interface-contracts.md`:

| Facade function | Internal interface(s) used |
|---|---|
| `cc.list_problems()`, `cc.get_problem()` | Repository §5 (problem instance registry reads) |
| `cc.list_algorithms()`, `cc.get_algorithm()` | Repository §5 (algorithm instance registry reads) |
| `cc.create_study()` | Repository §5 (Study write); Problem §1 and Algorithm §2 (ID validation) |
| `cc.update_study()` | Repository §5 (Study read, lock check) |
| `cc.run()` | Runner §3 (orchestrates all Runs); Problem §1 (evaluation); Algorithm §2 (search step) |
| `cc.get_experiment()` | Repository §5 (Experiment read) |
| `cc.get_runs()` | Repository §5 (Run reads) |
| `cc.get_result_aggregates()` | Analyzer §4 (metric computation); Repository §5 (ResultAggregate reads) |
| `cc.generate_reports()` | Analyzer §4 (report generation); Repository §5 (Report write) |
| `cc.export_raw_data()` | Repository §5 (PerformanceRecord reads); export serialization |

The public API contract (this document) specifies **what** each function does and what it
returns. The interface contracts specify **how** those results are produced by the
components. An implementor of IMPL-017 must satisfy both contracts simultaneously.

### Relation to Data Format Specification (`01-data-format/`)

The view objects defined in this document (§ "View Objects") are **not** the storage
entities defined in `docs/03-technical-contracts/01-data-format/`. They are read-only
projections:

| View object | Derived from storage entity |
|---|---|
| `ProblemInstanceSummary` | `ProblemInstance` (`01-data-format/02-problem-instance.md`) |
| `AlgorithmInstanceSummary` | `AlgorithmInstance` (`01-data-format/03-algorithm-instance.md`) |
| `Study` | `Study` (`01-data-format/04-study.md`) |
| `Experiment` | `Experiment` (`01-data-format/05-experiment.md`) |
| `Run` | `Run` (`01-data-format/06-run.md`) |
| `ResultAggregate` / `MetricStatistics` | `ResultAggregate` (`01-data-format/08-result-aggregate.md`) |
| `Report` | `Report` (`01-data-format/09-report.md`) |

Storage entities contain additional bookkeeping fields (versions, timestamps, provenance,
platform metadata) that are intentionally omitted from view objects. Callers should not
expect view objects to expose every field of the corresponding storage entity. If a caller
needs a storage-level field, they must access the repository directly via the Repository
interface, which is outside the scope of the public API.

### Relation to Metric Taxonomy (`03-metric-taxonomy/`)

The `metrics` field of `ResultAggregate` is a `dict[str, MetricStatistics]` whose keys are
metric IDs. All valid metric IDs are defined in
`docs/03-technical-contracts/03-metric-taxonomy/01-metric-taxonomy.md`. The format is
`CATEGORY-METRIC_NAME` in `UPPER_SNAKE_CASE` (e.g., `"QUALITY-BEST_VALUE_AT_BUDGET"`,
`"TIME-EVALUATIONS_TO_TARGET"`, `"RELIABILITY-SUCCESS_RATE"`).

Callers must not construct metric ID strings by convention; they should use the IDs exactly
as documented in the taxonomy. Metric IDs are stable identifiers — they do not change once
assigned and are permanent once used in a published study. Display names may change; IDs
must not.

The Analyzer (§4 of the interface contracts) validates that all metric IDs produced by
`compute_metrics()` exist in the taxonomy before writing ResultAggregates. This guarantees
that every key in `ResultAggregate.metrics` is a valid metric ID from the taxonomy.
