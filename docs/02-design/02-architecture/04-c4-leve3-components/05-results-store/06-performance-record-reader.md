# Performance Record Reader

> Container: [Results Store](../../03-c4-leve2-containers/12-results-store.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Provide a unified read interface over JSONL and Parquet performance files, automatically detecting which format is available, and returning PerformanceRecord objects to callers regardless of the underlying storage format.

---

## Interface

```python
class PerformanceRecordReader:
    def read_run(
        self,
        run_id: str,
        filters: RecordFilter | None = None,
    ) -> list[PerformanceRecord]:
        """Auto-detects Parquet or JSONL; applies filters."""

    def read_experiment(
        self,
        experiment_id: str,
        filters: RecordFilter | None = None,
    ) -> dict[str, list[PerformanceRecord]]:
        """Returns {run_id: records} for all Runs in the experiment."""

    def stream_run(
        self,
        run_id: str,
    ) -> Iterator[PerformanceRecord]:
        """Streaming read; preferred for large Runs."""
```

`RecordFilter` fields: `iteration_range`, `status`, `algorithm_id`, `problem_id`.

---

## Dependencies

- **Local File Repository** — path resolution
- `pyarrow.parquet` — Parquet read
- `json` stdlib — JSONL read
- `dataclasses` stdlib — PerformanceRecord construction

---

## Key Behaviors

1. **Format auto-detection** — checks for `performance.parquet` first; falls back to `performance.jsonl` if Parquet is absent. If neither exists, raises `RecordNotFoundError`.

2. **Parquet preference** — when both formats exist, reads from Parquet (59× faster range queries per ADR-010). Reads `performance.jsonl` only when Parquet is absent.

3. **Filter pushdown** — for Parquet reads, applies `RecordFilter` as a row-group predicate to avoid reading the full file. For JSONL reads, filtering is applied in Python (line-by-line).

4. **Malformed line handling** — for JSONL reads, skips lines that fail JSON parsing and records a `data_quality.malformed_lines` count in the returned metadata.

5. **Streaming support** — `stream_run()` yields PerformanceRecord objects one at a time from either format, without loading the entire Run into memory. Used by the Analysis Engine for large datasets.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/results_store/performance_record_reader.py`

---

## SRS Traceability

- FR-S-05 (unified read interface): callers must not need to know the storage format.
- ADR-010: the reader abstracts the dual-format decision from all consumers.
- UC-05 (explore results): the reader enables filtered result queries.
