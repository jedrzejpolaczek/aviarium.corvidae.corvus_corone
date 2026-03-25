# §3 File Formats and Storage

> Index: [01-data-format.md](01-data-format.md)

<!--
CONNECTS TO:
  ← §2 entity schemas     : every file described here stores an entity defined in §2
  → ADR-001               : the server-compatibility design constraint that shapes this layout
  → interface-contracts.md §5 : Repository interface — the layout is its implementation detail
  → src/corvus_corone/repository/local_file.py : the production implementation of this layout
-->

---

## §3.1 IOHprofiler export format

Cross-reference: [§4.2 IOHprofiler mapping](11-interoperability-mappings.md#42-iohprofiler-v033)

The `IOHExporter` class
(`corvus_corone.export.ioh_exporter.IOHExporter`) writes PerformanceRecords to
IOHprofiler v0.3.3+ format.  The output layout under a caller-supplied
`output_dir` is:

```
<output_dir>/
└── <algorithm_id>/
    ├── IOHprofiler_f<func_id>_<func_name>.json   ← JSON sidecar (all dimensions)
    └── data_f<func_id>_<func_name>/
        └── IOHprofiler_f<func_id>_DIM<dim>.dat   ← performance log
```

### .dat file

Two-column tab-separated text file with an unquoted header line repeated at
every run boundary:

```
evaluations raw_y
1 4.2345678901
2 3.1415926536
evaluations raw_y
1 5.0000000000
…
```

| Column | Source | Notes |
|---|---|---|
| `evaluations` | `PerformanceRecord.evaluation_number` | 1-based integer |
| `raw_y` | `PerformanceRecord.best_so_far` (or `objective_value` if absent) | Best-so-far value at this evaluation |

### JSON sidecar

Named `IOHprofiler_f<func_id>_<func_name>.json`, one per (algorithm, function)
pair.  Stores metadata that has no `.dat` equivalent:

| Sidecar field | Source |
|---|---|
| `version` | `"0.3.5"` (hard-coded to spec version) |
| `function_id` | `ProblemMeta.func_id` |
| `function_name` | `ProblemMeta.func_name` |
| `maximization` | `ProblemMeta.maximization` |
| `algorithm.name` | `AlgorithmMeta.name` |
| `corvus_seed` | `RunRecord.seed` (non-standard extension) |
| `corvus_run_id` | `RunRecord.run_id` (non-standard extension) |

Non-standard fields (`corvus_seed`, `corvus_run_id`) are ignored by
IOHanalyzer but preserve Corvus reproducibility metadata.  Full field mapping
and information-loss manifest keys are in
[§4.2](11-interoperability-mappings.md#42-iohprofiler-v033).

---

## §3.2 LocalFileRepository internal storage

> **Source:** `corvus_corone.repository.local_file.LocalFileRepository`
> **Reference implementation:** REF-TASK-0036 / IMPL-010
> **Verified by:** `tests/unit/test_repository_interface.py` (parametrized over both
> `InMemoryRepositoryFactory` and `LocalFileRepository`)

### Design note — layout is an implementation detail

> **This directory structure is an implementation detail of `LocalFileRepository`.
> It is not part of the public `RepositoryFactory` interface (ADR-001).**

Consumer code must never traverse or parse this tree directly. All access to
stored entities must go through a `RepositoryFactory` implementation. A future
`ServerRepository` (V2) will fulfil the same interface using a database
backend and will produce no local files at all — code that relies on the
directory structure will break silently in V2.

Key ADR-001 properties satisfied by this layout:

| Property | How the layout satisfies it |
|---|---|
| **UUID-keyed files** | Every file is named `<uuid>.json` — no file paths in entity content |
| **No path-based references** | Entity JSON contains only UUID foreign keys, never file paths |
| **JSON-serializable schemas** | All entity content is UTF-8 JSON; no binary blobs in primary files |
| **V2-migratable** | `POST /problems/<uuid>` ← `problems/<uuid>.json` — direct 1:1 migration |

### Annotated directory tree

The tree below shows the layout produced after a complete study with
3 problems × 2 algorithms × 10 repetitions (60 runs total).
UUIDs are abbreviated as `<…>` for readability.

```
<root_dir>/
│
├── problems/                           ← Problem Instance registry
│   ├── <prob-uuid-1>.json              │  Created by: problems.register_problem()
│   ├── <prob-uuid-2>.json              │  Format: JSON (§2.1 schema)
│   └── <prob-uuid-3>.json              │  One file per registered ProblemInstance
│
├── algorithms/                         ← Algorithm Instance registry
│   ├── <alg-uuid-1>.json              │  Created by: algorithms.register_algorithm()
│   └── <alg-uuid-2>.json              │  Format: JSON (§2.2 schema)
│                                       │  One file per registered AlgorithmInstance
│
├── studies/                            ← Study records (pre-registration gate)
│   └── <study-uuid>.json              │  Created by: studies.create_study()
│                                       │  Mutated by: studies.lock_study()
│                                       │  Format: JSON (§2.3 schema)
│                                       │  status field: "draft" → "locked"
│
├── experiments/                        ← Experiment records
│   └── <experiment-uuid>.json         │  Created by: experiments.create_experiment()
│                                       │  Mutated by: experiments.update_experiment()
│                                       │  Format: JSON (§2.4 schema)
│                                       │  status field: "running" → "completed"
│
├── runs/                               ← Run records and performance data
│   ├── <run-uuid-001>/                │  Created by: runs.create_run()
│   │   ├── run.json                   │    Format: JSON (§2.5 schema)
│   │   └── performance_records.jsonl  │    Format: JSON Lines (§2.6 schema)
│   │                                  │    Appended by: runs.save_performance_records()
│   ├── <run-uuid-002>/
│   │   ├── run.json
│   │   └── performance_records.jsonl
│   │
│   └── … (60 run directories for 3 problems × 2 algorithms × 10 repetitions)
│
├── aggregates/                         ← Result Aggregate records
│   ├── <agg-uuid-1>.json              │  Created by: aggregates.save_result_aggregates()
│   ├── <agg-uuid-2>.json              │  Format: JSON (§2.7 schema)
│   ├── <agg-uuid-3>.json              │  6 files = 3 problems × 2 algorithms
│   ├── <agg-uuid-4>.json              │  Each file: one (problem, algorithm) aggregate
│   ├── <agg-uuid-5>.json              │    with Standard Reporting Set metrics
│   └── <agg-uuid-6>.json
│
└── reports/                            ← Report records
    ├── <report-uuid-researcher>.json  │  Created by: reports.save_report()
    └── <report-uuid-practitioner>.json│  Format: JSON (§2.8 schema)
                                        │  Always 2 files per completed Experiment
                                        │    (FR-20: one "researcher", one "practitioner")
```

### File type reference table

| Path pattern | Entity | §2 Schema | Format | Creation trigger |
|---|---|---|---|---|
| `problems/<uuid>.json` | ProblemInstance | [§2.1](02-problem-instance.md) | JSON object | `problems.register_problem()` |
| `algorithms/<uuid>.json` | AlgorithmInstance | [§2.2](03-algorithm-instance.md) | JSON object | `algorithms.register_algorithm()` |
| `studies/<uuid>.json` | Study | [§2.3](04-study.md) | JSON object | `studies.create_study()`; mutated by `lock_study()` |
| `experiments/<uuid>.json` | Experiment | [§2.4](05-experiment.md) | JSON object | `experiments.create_experiment()`; mutated by `update_experiment()` |
| `runs/<uuid>/run.json` | Run | [§2.5](06-run.md) | JSON object | `runs.create_run()`; mutated by `update_run()` |
| `runs/<uuid>/performance_records.jsonl` | PerformanceRecord[] | [§2.6](07-performance-record.md) | JSON Lines (one record per line) | `runs.save_performance_records()` (append-only) |
| `aggregates/<uuid>.json` | ResultAggregate | [§2.7](08-result-aggregate.md) | JSON object | `aggregates.save_result_aggregates()` |
| `reports/<uuid>.json` | Report | [§2.8](09-report.md) | JSON object | `reports.save_report()` |

### JSON Lines format for PerformanceRecords

PerformanceRecords are the only entity stored as JSON Lines (`.jsonl`) rather
than a single JSON object. This choice accommodates the append-only write
pattern: the Runner writes records incrementally during a Run without
rewriting the entire file. Each line is an independent, self-contained JSON
object matching the §2.6 schema.

Example `performance_records.jsonl`:
```jsonl
{"evaluation_number": 1, "objective_value": 4.2346, "best_so_far": 4.2346, "trigger_reason": "scheduled"}
{"evaluation_number": 2, "objective_value": 3.1416, "best_so_far": 3.1416, "trigger_reason": "both"}
{"evaluation_number": 5, "objective_value": 1.8743, "best_so_far": 1.8743, "trigger_reason": "scheduled"}
{"evaluation_number": 50, "objective_value": 0.9012, "best_so_far": 0.9012, "trigger_reason": "scheduled_end_of_run"}
```

Records are always returned by `runs.get_performance_records()` sorted
ascending by `evaluation_number`, regardless of write order.

### File counts for a representative completed study

For a study with *P* problems, *A* algorithms, and *R* repetitions per pair:

| Directory | File count | Formula |
|---|---|---|
| `problems/` | *P* | one per registered Problem Instance |
| `algorithms/` | *A* | one per registered Algorithm Instance |
| `studies/` | 1 | one Study per `create_study()` call |
| `experiments/` | 1 | one Experiment per `create_experiment()` call |
| `runs/` | *P* × *A* × *R* subdirectories, 2 files each | `run.json` + `performance_records.jsonl` |
| `aggregates/` | *P* × *A* | one per (problem, algorithm) pair |
| `reports/` | 2 | one `researcher`, one `practitioner` |

For the canonical tutorial study (3 problems × 2 algorithms × 10 repetitions):
60 run subdirectories, 6 aggregate files, 2 report files = **136 files** total.

### Relationship to V2 migration

Because every file is named by UUID and entity JSON contains only UUID
foreign keys, migrating a V1 archive to a V2 server is a direct import:

```
POST /api/problems/<uuid>    ← content of problems/<uuid>.json
POST /api/algorithms/<uuid>  ← content of algorithms/<uuid>.json
POST /api/studies/<uuid>     ← content of studies/<uuid>.json
POST /api/experiments/<uuid> ← content of experiments/<uuid>.json
POST /api/runs/<uuid>        ← content of runs/<uuid>/run.json
                               + runs/<uuid>/performance_records.jsonl
POST /api/aggregates/<uuid>  ← content of aggregates/<uuid>.json
POST /api/reports/<uuid>     ← content of reports/<uuid>.json
```

No field rewriting is needed. This is the ADR-001 guarantee in practice.

---

## §3.3 Bulk performance data (Parquet secondary format)

> **ADR-010** — benchmark evidence and decision rationale: `adr-010-bulk-performance-record-format.md`

For Runs whose PerformanceRecord count reaches the `bulk_storage_threshold` (default:
1,000 records per Run; configurable), the Repository writes a secondary Parquet file
alongside the canonical JSON Lines file:

```
runs/<run-uuid>/
├── run.json                     ← primary (always present; ADR-001)
├── performance_records.jsonl    ← primary (always present; ADR-001)
└── performance_records.parquet  ← secondary (present when threshold is reached)
```

The `.parquet` file is **read in preference to `.jsonl`** by `runs.get_performance_records()`
when present, giving a **20× write and 59× query speedup** (ADR-010 benchmark,
150,000 records). The `.jsonl` file is never deleted.

### Secondary format specification

| Property | Value |
|---|---|
| Format | Apache Parquet |
| Compression | snappy |
| Library | `pyarrow >= 13.0` (core dependency) |
| Row group size | 500 rows (enables predicate pushdown on `run_id`) |
| Written by | `runs.save_bulk_performance_records()` |
| Read by | `runs.get_performance_records()` (transparent; same return type) |
| Fallback | On `ArrowIOError`, falls back to `.jsonl` with a warning log entry |

### Parquet column schema

| Column | Arrow type | §2.6 field |
|---|---|---|
| `run_id` | `pa.string()` | `run_id` |
| `evaluation_number` | `pa.int32()` | `evaluation_number` |
| `elapsed_time` | `pa.float64()` | `elapsed_time` |
| `objective_value` | `pa.float64()` | `objective_value` |
| `is_improvement` | `pa.bool_()` | `is_improvement` |
| `trigger_reason` | `pa.dictionary(pa.int8(), pa.string())` | `trigger_reason` (7-value enum; dictionary-encoded) |
| `current_solution` | `pa.string()` | `current_solution` (JSON-serialised; null if not stored) |

### Benchmark summary (150,000 records)

| Format | Write time | File size | Query: run_id=X (100/150k) |
|---|---|---|---|
| JSON Lines | 3.41 s | 38.2 MB | 0.41 s |
| Parquet / snappy | 0.17 s | 4.1 MB | 0.007 s |
| HDF5 / gzip level 4 | 0.93 s | 6.8 MB | 0.19 s |

Full benchmark method, alternative analysis, and HDF5 rejection rationale: ADR-010.

### Invariants

- The `.jsonl` file is the **source of truth** for V2 migration and for schema
  version mismatch recovery. It is never removed.
- If the stored Parquet schema version does not match the current §2.6 schema
  version, `save_bulk_performance_records()` regenerates the Parquet file from
  `.jsonl` before returning.
- A round-trip test is required: records written via `save_bulk_performance_records()`
  and read via `get_performance_records()` must be identical to records stored and
  read via the JSON Lines path for the same Run.
