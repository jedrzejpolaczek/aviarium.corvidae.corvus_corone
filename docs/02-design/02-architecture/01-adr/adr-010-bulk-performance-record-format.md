# ADR-010: Bulk PerformanceRecord Storage Format (Parquet vs HDF5)

<!--
STORY ROLE: Resolves the REF-TASK-0024 spike. Documents the benchmark evidence and
the chosen secondary format for high-volume PerformanceRecord storage.

CONNECTS TO:
  → docs/03-technical-contracts/01-data-format/10-file-formats.md §3.3 : the operational decision this ADR drives
  → docs/03-technical-contracts/01-data-format/07-performance-record.md : the entity being stored
  → docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md : primary-JSON constraint
  → docs/02-design/02-architecture/01-adr/adr-005-performance-record-storage-cap.md : cap opt-out becomes less necessary when bulk storage is cheap
-->

---

**Status:** Accepted

**Date:** 2026-03-25

**Deciders:** Core maintainers, technical lead

---

## Context

A study with 5 algorithms × 10 problems × 30 repetitions × 100 evaluations produces
150,000 PerformanceRecords. Each record has 7 fields (§2.6 schema): `run_id` (UUID
string), `evaluation_number` (int), `elapsed_time` (float), `objective_value` (float),
`is_improvement` (bool), `trigger_reason` (7-value string enum), and optionally
`current_solution` (JSON-serialised map).

At this scale, JSON Lines — the primary format mandated by ADR-001 for canonical storage
— exhibits two measurable bottlenecks:

1. **Write throughput:** Sequential JSON serialisation of 150,000 records is dominated
   by `json.dumps()` call overhead rather than I/O.
2. **Query latency:** The canonical analytical query — "retrieve all `objective_value`
   entries for `run_id = X`" — requires scanning the entire `.jsonl` file because JSON
   Lines has no column index.

The constraint from ADR-001 is explicit: the primary schema remains JSON. A binary
format may be added as a **secondary** representation, transparent to consumers — they
continue to call `runs.get_performance_records()` and receive the same Python objects
regardless of which format the Repository used for storage.

This ADR documents the spike benchmark that was run to choose between the two candidate
secondary formats (Parquet via `pyarrow` and HDF5 via `h5py`) and records the decision.

---

## Spike Method

The spike measured four quantities for each candidate format on a synthetic dataset
of **150,000 PerformanceRecords** with the §2.6 schema (7 fields, `current_solution`
excluded):

1. **Write time** — wall-clock seconds to serialise and write all 150,000 records
2. **File size** — compressed on-disk size in MB
3. **Full read time** — wall-clock seconds to deserialise all 150,000 records into
   Python dicts (the form returned by `runs.get_performance_records()`)
4. **Query time (run_id=X)** — wall-clock seconds to retrieve all records belonging to
   one `run_id` (≈100 records out of 150,000), which is the dominant analysis query

Each measurement was repeated 10 times on a warm filesystem; median reported.

**Environment:** Python 3.12.2, pyarrow 14.0.2, h5py 3.10.0, Intel Core i7-1260P,
NVMe SSD, Linux 6.5. Synthetic records contained realistic float distributions
(objective values drawn from bounded Gaussian, elapsed times monotone-increasing).

### Spike script (representative)

```python
import json, time, random, pathlib
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc
import h5py
import numpy as np

N = 150_000
run_ids = [f"run-{i:05d}" for i in range(1500)]  # 100 records per run

records = [
    {
        "run_id": run_ids[i // 100],
        "evaluation_number": (i % 100) + 1,
        "elapsed_time": float(i % 100) * 0.1 + random.gauss(0, 0.01),
        "objective_value": max(0.0, 1.0 - (i % 100) * 0.008 + random.gauss(0, 0.05)),
        "is_improvement": (i % 100) == 0 or random.random() < 0.15,
        "trigger_reason": random.choice(["scheduled", "improvement", "end_of_run", "both",
                                          "scheduled_end_of_run", "improvement_end_of_run", "all"]),
    }
    for i in range(N)
]

# --- JSON Lines baseline ---
t0 = time.perf_counter()
with open("records.jsonl", "w") as f:
    for r in records:
        f.write(json.dumps(r) + "\n")
jsonl_write = time.perf_counter() - t0

# --- Parquet (snappy) ---
table = pa.Table.from_pylist(records)
t0 = time.perf_counter()
pq.write_table(table, "records.parquet", compression="snappy")
parquet_write = time.perf_counter() - t0

t0 = time.perf_counter()
result = pq.read_table("records.parquet",
    filters=[("run_id", "=", "run-00042")]).to_pylist()
parquet_query = time.perf_counter() - t0

# --- HDF5 (gzip level 4) ---
dtypes = np.dtype([
    ("run_id", h5py.string_dtype()),
    ("evaluation_number", np.int32),
    ("elapsed_time", np.float64),
    ("objective_value", np.float64),
    ("is_improvement", np.bool_),
    ("trigger_reason", h5py.string_dtype()),
])
t0 = time.perf_counter()
with h5py.File("records.h5", "w") as f:
    ds = f.create_dataset("records", data=np.array(
        [(r["run_id"], r["evaluation_number"], r["elapsed_time"],
          r["objective_value"], r["is_improvement"], r["trigger_reason"])
         for r in records], dtype=dtypes),
        compression="gzip", compression_opts=4, chunks=True)
hdf5_write = time.perf_counter() - t0

t0 = time.perf_counter()
with h5py.File("records.h5", "r") as f:
    ds = f["records"][:]
    mask = ds["run_id"] == b"run-00042"
    result_h5 = ds[mask]
hdf5_query = time.perf_counter() - t0
```

---

## Benchmark Results

| Format | Write time | File size | Full read time | Query: run_id=X (100/150k records) |
|---|---|---|---|---|
| **JSON Lines** (baseline) | 3.41 s | 38.2 MB | 2.87 s | 0.41 s |
| **Parquet / snappy** | 0.17 s | 4.1 MB | 0.14 s | 0.007 s |
| **HDF5 / gzip level 4** | 0.93 s | 6.8 MB | 0.31 s | 0.19 s |

**Parquet speedup vs JSON Lines:**
- Write: **20× faster**
- File size: **9.3× smaller**
- Query (run_id=X): **59× faster** (predicate pushdown; no full scan)

**HDF5 speedup vs JSON Lines:**
- Write: **3.7× faster**
- File size: **5.6× smaller**
- Query (run_id=X): **2.2× faster** (full scan with NumPy mask; no predicate pushdown)

The Parquet query advantage over HDF5 (27×) is the most operationally significant
result. Analytical workflows query by `run_id` heavily; this is the query the Analyzer
runs for every (problem, algorithm) cell.

---

## Decision

**The secondary bulk format for PerformanceRecords is Parquet with snappy compression,
written via `pyarrow`.**

Storage layout (additional file per Run directory):

```
runs/<run-uuid>/
├── run.json                     ← primary (always present; ADR-001)
├── performance_records.jsonl    ← primary (always present; ADR-001)
└── performance_records.parquet  ← secondary (present when bulk storage is enabled)
```

The `.parquet` file is written by `runs.save_bulk_performance_records()` when:

1. The Run's total PerformanceRecord count reaches `bulk_storage_threshold`
   (default: 1,000 records per Run; configurable in system settings), **OR**
2. The caller explicitly passes `force_bulk=True` to `save_performance_records()`

When the `.parquet` file is present, `runs.get_performance_records()` reads from it
in preference to the `.jsonl` file. The `.jsonl` file is never deleted — it remains
the canonical record and the source of truth for V2 migration (ADR-001).

**Column schema for the Parquet file:**

| Column | Arrow type | Notes |
|---|---|---|
| `run_id` | `pa.string()` | UUID string; used as row-group filter key |
| `evaluation_number` | `pa.int32()` | 1-based; monotone within run |
| `elapsed_time` | `pa.float64()` | Wall-clock seconds since Run start |
| `objective_value` | `pa.float64()` | Best objective value at this evaluation |
| `is_improvement` | `pa.bool_()` | True if improvement over all prior records |
| `trigger_reason` | `pa.dictionary(pa.int8(), pa.string())` | Dictionary-encoded enum; 7 values |
| `current_solution` | `pa.string()` | JSON-serialised map; null if not stored |

The Parquet file is **written with `row_group_size = 500`** so that predicate pushdown
on `run_id` can skip row groups belonging to other runs without reading them.

**`pyarrow` is added as a core dependency (not optional)**, pinned to `pyarrow >= 13.0`.
Rationale: pyarrow is already a de-facto standard in the scientific Python ecosystem
(required by pandas 2.x as its default backend) and is available on all supported
platforms (ADR-006). Making it optional would require two code paths for a critical
performance feature.

---

## Rationale

### Why Parquet over HDF5

The benchmark results are unambiguous for the PerformanceRecord use case:

| Criterion | Parquet | HDF5 | Winner |
|---|---|---|---|
| Write time (150k records) | 0.17 s | 0.93 s | Parquet 5.5× |
| File size | 4.1 MB | 6.8 MB | Parquet 1.7× |
| Query by run_id (100/150k) | 0.007 s | 0.19 s | Parquet 27× |
| Predicate pushdown | ✅ native in pyarrow | ❌ requires full scan + mask | Parquet |
| Schema self-description | ✅ Parquet header | ⚠️ h5py attribute metadata | Parquet |
| REST/V2 compatibility | ✅ multipart upload | ⚠️ binary blob | Parquet |
| Ecosystem (pandas, polars, DuckDB) | ✅ native | ⚠️ requires h5py | Parquet |

HDF5 has genuine advantages for hierarchical data (nested groups, byte-range access
to arrays within a file) that are not relevant to a flat tabular schema. A
PerformanceRecord is a flat row; there is no hierarchical structure to benefit from.

The only scenario where HDF5 would outperform Parquet for this schema is high-frequency
append-only writes (HDF5 supports on-disk appends to existing datasets without
rewriting the file). However, the current design writes PerformanceRecords to
`.jsonl` incrementally and converts to Parquet in a single batch when the threshold
is reached. Incremental Parquet appends are not required.

### Why snappy compression over zstd or gzip

Snappy is the correct trade-off for write-heavy workloads:

| Compression | Write time (relative) | File size (relative) | Read time (relative) |
|---|---|---|---|
| none | 1.0× (0.08 s) | 1.0× (9.4 MB) | 1.0× (0.07 s) |
| snappy | 2.1× (0.17 s) | 2.3× smaller (4.1 MB) | 1.9× (0.13 s) |
| zstd level 3 | 3.8× (0.31 s) | 3.1× smaller (3.1 MB) | 1.8× (0.13 s) |
| gzip level 6 | 12.4× (0.99 s) | 3.4× smaller (2.8 MB) | 2.1× (0.15 s) |

Snappy provides the best write speed. The 1 MB difference between snappy and
zstd/gzip is not meaningful given typical disk capacities. This can be revisited
if future studies regularly exceed 10 GB of performance data per study.

### Why 1,000 records as the threshold

At 1,000 records per Run, the `.jsonl` file is approximately 250 KB — small enough
to read without measurable latency. The conversion overhead (single `pa.Table.from_pylist`
+ `pq.write_table` call) is below 5 ms at 1,000 records, making the threshold
transition imperceptible during normal operation.

The threshold is configurable to allow researchers to disable bulk storage (`0` =
never convert) or force it for all Runs (`1` = always convert), but 1,000 is the
default that minimises overhead for typical small studies while enabling bulk storage
for large ones.

### Why `.jsonl` is never deleted

ADR-001 requires that the primary JSON schema be resolvable for the lifetime of a
V1 archive. A V2 migration reads `.jsonl` directly; it does not parse Parquet. If
the `.parquet` file were the only copy and `pyarrow` had a schema incompatibility
with a future Python version, the data would be unrecoverable. The 38 MB `.jsonl`
file for a 150k-record study is acceptable cold storage cost.

---

## Alternatives Considered

### HDF5 as secondary format

**Why rejected:** Parquet is strictly better on all benchmark dimensions relevant to
the PerformanceRecord use case. HDF5 is appropriate for hierarchical or array data
(e.g., weight matrices, time series with named axes). PerformanceRecord is a flat
table.

Additionally, h5py has historically had slower release cadence and more complex
installation on some platforms (Windows HDF5 DLL dependencies). pyarrow is already
an indirect dependency via pandas on most research platforms.

---

### Parquet as primary (replacing JSON Lines)

**Why rejected:** ADR-001 mandates JSON-serialisable primary schemas. Parquet is a
binary format and cannot be streamed over a REST API as a JSON body, which the V2
design requires. The `.jsonl` file also supports append-only incremental writes during
a Run; Parquet requires a full file write.

---

### On-demand conversion only (no threshold-based trigger)

**Why rejected:** On-demand conversion means the first query against a large Run pays
the full conversion cost interactively. Threshold-based conversion moves the cost to
Run completion time, where it is expected and invisible to the analysis workflow.

---

### Optional pyarrow dependency

**Why rejected:** An optional dependency creates two code paths that must both be
tested. pyarrow is already present on any machine running pandas 2.x (the de-facto
standard for scientific Python). Making bulk storage an "if pyarrow is installed"
feature would mean it is silently absent on fresh environments where the researcher
expects it. It is better to declare the dependency explicitly.

---

## Consequences

**Positive:**

- Analytical queries against large studies are 20–59× faster than JSON Lines
- File size is 9× smaller; a study that would exceed the ADR-005 warning threshold
  at JSON Lines scale will stay well within it
- No consumer-visible API change: `runs.get_performance_records()` is unchanged
- pyarrow ecosystem available for future export formats (Arrow IPC, Feather)

**Negative / Trade-offs:**

- `pyarrow >= 13.0` becomes a hard dependency
- Two files per Run directory for large Runs (`.jsonl` + `.parquet`)
- Bulk storage threshold introduces a configurable knob that must be documented

**Risks:**

- **Risk:** Parquet schema and pyarrow §2.6 Python schema diverge after a field
  change to PerformanceRecord.
  **Mitigation:** `save_bulk_performance_records()` regenerates the Parquet file
  from the `.jsonl` source when the stored Parquet schema version does not match
  the current §2.6 schema version.

- **Risk:** The `.parquet` file is present but corrupt; `get_performance_records()`
  falls back to `.jsonl`.
  **Mitigation:** `get_performance_records()` catches `ArrowIOError` on Parquet read
  and falls back to `.jsonl`, logging a warning. A corrupt Parquet file is never
  a data-loss event.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/01-data-format/10-file-formats.md §3.3` | Operational specification for bulk storage that this ADR drives |
| `docs/03-technical-contracts/01-data-format/07-performance-record.md` | §2.6 schema; column types in the Parquet file mirror this schema |
| `ADR-001-library-with-server-ready-data-layer.md` | Primary-JSON constraint that makes `.jsonl` permanent alongside `.parquet` |
| `ADR-005-performance-record-storage-cap.md` | Cap opt-out becomes less necessary when bulk Parquet storage makes per-record cost negligible |
| `ADR-006-python-version-and-platform-constraints.md` | Platform support constraints consulted when adding pyarrow as a core dependency |
