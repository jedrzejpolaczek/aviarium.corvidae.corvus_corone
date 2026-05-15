# §5 Repository Interface

> Index: [01-index.md](01-index.md)

The Repository layer provides read/write access to all persistent entities. Storage layout
and format are implementation details — callers interact only through these interfaces.

→ Used by: all containers that need to access stored artifacts

**Design decisions recorded here:**
- **Domain-specific repositories.** Each entity type has its own repository interface.
  This avoids a bloated monolithic interface and allows independent versioning and testing
  of each domain. A `RepositoryFactory` groups all domain repositories and is the single
  object passed to components that need cross-entity access.
- **Versioning semantics (all repositories).** `get_*(id, version=None)` returns the latest
  non-deprecated version. `get_*(id, version="X.Y.Z")` returns exactly that version —
  required for reproducibility (MANIFESTO Principle 19).
  → versioning policy: [versioning-governance.md §1](../../05-community/02-versioning-governance.md)
- **Server-compatible IDs.** All entity IDs are UUIDs. No file paths in method signatures.
  → ADR-001

---

### RepositoryFactory

Groups all domain repositories. Components that need cross-entity access receive a
`RepositoryFactory` instance rather than individual repositories.

```
RepositoryFactory {
    problems:    ProblemRepository
    algorithms:  AlgorithmRepository
    studies:     StudyRepository
    experiments: ExperimentRepository
    runs:        RunRepository
    aggregates:  ResultAggregateRepository
    reports:     ReportRepository
}
```

`LocalFileRepository` (V1) implements all seven domain interfaces and exposes itself as a
`RepositoryFactory`. Server-backed implementations (V2) replace individual interfaces
independently without changing the factory contract.

---

### ProblemRepository

#### get_problem(id: str, version: str | None = None) → ProblemInstance
Returns the Problem Instance with the given ID. `version=None` returns the latest
non-deprecated version; a pinned version string returns exactly that version.

**Exceptions:** `EntityNotFoundError`, `VersionNotFoundError`

#### list_problems(filters: ProblemFilter | None = None) → list[ProblemInstanceSummary]
Returns summaries of all non-deprecated Problem Instances matching the filter.
`ProblemFilter` fields: `provenance`, `real_or_synthetic`, `min_dimensions`, `max_dimensions`,
`landscape_characteristics` (subset match). `None` returns all.

#### register_problem(problem: ProblemInstance) → str
Validates and persists a new Problem Instance. Returns the assigned ID.

**Preconditions:** all data-format.md §2.1 validation rules pass
**Exceptions:** `ValidationError`

#### deprecate_problem(id: str, reason: str, superseded_by: str | None = None) → None
Marks a Problem Instance as deprecated. Deprecated instances are excluded from
`list_problems()` but remain retrievable by exact ID and version for reproducibility.

---

### AlgorithmRepository

#### get_algorithm(id: str, version: str | None = None) → AlgorithmInstance
**Exceptions:** `EntityNotFoundError`, `VersionNotFoundError`

#### list_algorithms(filters: AlgorithmFilter | None = None) → list[AlgorithmInstanceSummary]
`AlgorithmFilter` fields: `algorithm_family`, `supported_variable_types` (subset match),
`framework`, `contributed_by`.

#### register_algorithm(algorithm: AlgorithmInstance) → str
Validates and persists a new Algorithm Instance. Returns the assigned ID.

**Preconditions:** all data-format.md §2.2 validation rules pass; `code_reference` is
resolvable and version-pinned (UC-02 F2); `configuration_justification` is non-empty (UC-02 F3)
**Exceptions:** `ValidationError`, `CodeReferenceError`

#### deprecate_algorithm(id: str, reason: str, superseded_by: str | None = None) → None

---

### StudyRepository

#### get_study(id: str, version: str | None = None) → Study
**Exceptions:** `EntityNotFoundError`, `VersionNotFoundError`

#### list_studies(filters: StudyFilter | None = None) → list[StudySummary]
`StudyFilter` fields: `status` (`"draft"`, `"locked"`), `created_by`, `problem_instance_ids` (overlap).

#### create_study(study: Study) → str
Persists a new Study in `"draft"` status. Returns the assigned ID.

**Preconditions:** all data-format.md §2.3 validation rules pass

#### lock_study(id: str) → None
Transitions Study from `"draft"` to `"locked"`. After locking, `sampling_strategy`,
`log_scale_schedule`, `improvement_epsilon`, and `experimental_design` fields are immutable.

**Preconditions:** Study is in `"draft"` status; all required fields are present
**Exceptions:** `StudyAlreadyLockedError`, `ValidationError`

---

### ExperimentRepository

#### get_experiment(id: str) → Experiment
**Exceptions:** `EntityNotFoundError`

#### list_experiments(study_id: str | None = None) → list[ExperimentSummary]

#### create_experiment(experiment: Experiment) → str
Persists a new Experiment in `"running"` status. Returns the assigned ID.

**Preconditions:** referenced Study exists and is locked

#### update_experiment(id: str, **fields) → None
Updates mutable fields: `status`, `completed_at`. Immutable fields (`study_id`,
`execution_environment`) cannot be changed after creation.

**Exceptions:** `ImmutableFieldError`

---

### RunRepository

#### get_run(id: str) → Run
**Exceptions:** `EntityNotFoundError`

#### list_runs(experiment_id: str, filters: RunFilter | None = None) → list[RunSummary]
`RunFilter` fields: `status`, `problem_instance_id`, `algorithm_instance_id`.

#### create_run(run: Run) → str
Persists a new Run record. Returns the assigned ID.

#### update_run(id: str, **fields) → None
Updates mutable fields: `status`, `budget_used`, `completed_at`, `failure_reason`,
`cap_reached_at_evaluation`.

#### save_performance_records(run_id: str, records: list[PerformanceRecord]) → None
Appends Performance Records for the given Run. Records must be in ascending
`evaluation_number` order.

**Preconditions:** Run exists; `evaluation_number` sequence is strictly monotonic
**Exceptions:** `ValidationError`, `DuplicateEvaluationError`

#### get_performance_records(run_id: str) → list[PerformanceRecord]
Returns all Performance Records for the given Run, sorted ascending by `evaluation_number`.

---

### ResultAggregateRepository

#### get_result_aggregate(id: str) → ResultAggregate
**Exceptions:** `EntityNotFoundError`

#### list_result_aggregates(experiment_id: str) → list[ResultAggregate]

#### save_result_aggregates(aggregates: list[ResultAggregate]) → None
Persists a batch of Result Aggregates. All aggregates must reference the same Experiment.

**Preconditions:** all data-format.md §2.7 validation rules pass; metric names in `metrics`
are valid entries in metric-taxonomy.md

---

### ReportRepository

#### get_report(id: str) → Report
**Exceptions:** `EntityNotFoundError`

#### list_reports(experiment_id: str) → list[Report]

#### save_report(report: Report) → str
Persists a Report and its artifact. Returns the assigned ID.

**Preconditions:** `limitations` is non-empty (FR-21); `artifact_reference` is resolvable
**Exceptions:** `ValidationError`
