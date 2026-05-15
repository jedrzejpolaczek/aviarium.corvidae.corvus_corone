# Container: Analysis Engine

> Index: [01-index.md](01-index.md)

**Responsibility:** Compute metrics and statistical tests over completed Run data to produce
`ResultAggregate` entities and `StatisticalTestResult` records. Implements the three-level
analysis defined in the statistical methodology: descriptive metrics, non-parametric
statistical tests (Wilcoxon signed-rank, Kruskal-Wallis + Holm-Bonferroni), and scoped
conclusions. All conclusions carry an explicit `conclusion_scope` to prevent
over-generalisation (MANIFESTO Principle 3).

**Technology:** Python · SciPy (statistical tests).

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Full experiment analysis | `analyze(experiment_id, config)` → `AnalysisReport` with `ResultAggregate`s, test results, and scoped conclusions | Study Orchestrator (triggered after all Runs complete) |
| Partial metric computation | `compute_metrics(run_ids, metric_names)` → `list[ResultAggregate]` | Researcher (via Public API for custom analysis) |
| Pairwise comparison | `compare(experiment_id, algorithm_ids, metric_name, test_config)` → `StatisticalTestResult` | Researcher (via Public API) |

Full interface contract: [`../../../03-technical-contracts/02-interface-contracts/05-analyzer-interface.md`](../../../03-technical-contracts/02-interface-contracts/05-analyzer-interface.md)

**Dependencies:**

| Dependency | Reason |
|---|---|
| Results Store | Reads `PerformanceRecord[]` and `Run` records for all completed Runs in an Experiment; writes computed `ResultAggregate` entities |

**Data owned:** None directly. `ResultAggregate` entities are persisted to the Results Store
by the Analysis Engine but owned by the store.

**Design constraints:**

- Analysis is **batch-only** in V1: `analyze()` requires `experiment.status == "completed"`.
  Streaming (incremental analysis as Runs complete) is not supported.
- Pre-registered hypotheses (listed in `Study.pre_registered_hypotheses`) are marked
  `"pre_registered": true` in the report; exploratory comparisons are marked `false`.
  The system records the distinction but does not technically block exploratory comparisons
  (MANIFESTO Principle 16 — scientific integrity is the researcher's responsibility).
- LOCF (Last Observation Carried Forward) is the default interpolation strategy for
  reconstructing `best_so_far` at un-logged evaluation counts (ADR-003).

**Actors served:** Researcher (primary — metric computation and statistical analysis,
UC-01 steps 5-6).

**Relevant SRS section:** FR-13 (metric computation from taxonomy), FR-14 (PerformanceRecord log-scale recording), FR-15 (three analysis levels — exploratory, confirmatory, practical significance),
FR-16 (pre-registration distinction in report).
