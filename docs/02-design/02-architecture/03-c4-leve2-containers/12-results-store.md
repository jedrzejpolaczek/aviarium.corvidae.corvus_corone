# Container: Results Store

> Index: [01-c2-containers.md](01-c2-containers.md)

**Responsibility:** Persist and serve all runtime entities produced during study execution
and analysis: `Study`, `Experiment`, `Run`, `PerformanceRecord`, `ResultAggregate`, and
`Report` records. Provides the seven domain repositories (via `RepositoryFactory`) through
which all other containers read and write persistent state. In V1, backed by a local file
system with SQLite-compatible structured storage and Parquet for bulk `PerformanceRecord`
data (ADR-010).

**Technology:** Python · SQLite (structured entity records) · Parquet/snappy via `pyarrow >= 13.0`
(bulk `PerformanceRecord` secondary format, ADR-010).

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Domain repositories | `RepositoryFactory` exposing `ProblemRepository`, `AlgorithmRepository`, `StudyRepository`, `ExperimentRepository`, `RunRepository`, `ResultAggregateRepository`, `ReportRepository` | All containers that need persistent state |
| Performance records | `save_performance_records(run_id, records)` / `get_performance_records(run_id)` | Experiment Runner (write), Analysis Engine (read), Algorithm Visualization Engine (read) |
| Result aggregates | `save_result_aggregates(aggregates)` / `list_result_aggregates(experiment_id)` | Analysis Engine (write), Reporting Engine (read), Public API (read) |

Full interface contract: [`../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md`](../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md)

**Dependencies:** None. The Results Store is the persistence leaf of the system; it has no
upstream container dependencies.

**Data owned:** All persistent entities:
- Study and Experiment records (`studies/`, `experiments/`)
- Run records and Performance Records (`runs/<id>/run.json`, `runs/<id>/performance.jsonl`,
  `runs/<id>/performance.parquet` — ADR-010 dual format)
- Result Aggregates (`aggregates/`)
- Report records and HTML artifact files (`reports/`)

**Storage format notes (ADR-010):**
- Primary format for `PerformanceRecord`s: JSON Lines (`.jsonl`) — always written, never deleted
- Secondary format: Parquet/snappy (`.parquet`) — written for runs with ≥ 1,000 records;
  20× faster write, 9.3× smaller, 59× faster column queries vs JSON Lines
- Fallback: `ArrowIOError` → system continues with `.jsonl` only; no data loss

**Actors served:** All actors indirectly — the Results Store is the shared persistence layer
for every container in the system.

**Relevant SRS section:** FR-17 (data immutability and locking), FR-18 (resume interrupted
experiments), FR-19 (execution environment capture and storage), FR-22 (raw data export
alongside reports).
