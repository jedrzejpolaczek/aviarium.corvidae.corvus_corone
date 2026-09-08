# Performance Recorder

> Container: [Experiment Runner](../../03-c4-leve2-containers/08-experiment-runner.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Receive per-evaluation observation data from the Evaluation Loop and write PerformanceRecord objects to the Results Store (via the JSONL Performance Writer), providing the bridge between the evaluation subprocess and persistent storage.

---

## Interface

Called by the Evaluation Loop on every `tell()` completion:

```python
class PerformanceRecorder:
    def record(
        self,
        run_id: str,
        iteration: int,
        candidates: list,
        values: list[float],
        best_value: float,
        best_candidate: list[float],
        wall_time_ms: float,
        status: Literal["success", "failed"] = "success",
        error: str | None = None,
    ) -> None:
        """Constructs a PerformanceRecord and writes it to the JSONL writer."""
```

---

## Dependencies

- **Results Store — JSONL Performance Writer** — the underlying write target. The recorder holds a reference to an open `JsonlPerformanceWriter` instance for the duration of the Run.
- `dataclasses` stdlib (for `PerformanceRecord` construction)

---

## Key Behaviors

1. **PerformanceRecord construction** — assembles a `PerformanceRecord` dataclass from the observation data. Fields: `run_id`, `experiment_id`, `algorithm_id`, `problem_id`, `iteration`, `budget`, `value`, `best_so_far`, `candidate`, `wall_time_ms`, `timestamp`, `status`, `error`.

2. **Streaming write** — writes each record immediately via the JSONL writer without buffering. This ensures that partial Run data is persisted even if the subprocess crashes mid-run.

3. **Error observation recording** — when `status="failed"`, the record is still written with `value=None` and the `error` message. This preserves the full evaluation history including failures.

4. **Writer lifecycle** — the JSONL writer is opened at `PerformanceRecorder.__init__()` and closed at `PerformanceRecorder.close()`. The Run Isolator calls `close()` before subprocess exit.

5. **Flush guarantee** — calls `writer.flush()` every 100 records to prevent data loss on abnormal subprocess termination.

---

## State

Holds an open file handle to the JSONL writer for the duration of the Run subprocess. Stateless between Runs.

---

## Implementation Reference

`corvus_corone/experiment_runner/performance_recorder.py`

---

## SRS Traceability

- FR-S-01 (store performance records): every evaluation observation must be persisted.
- UC-02 step 5 (record results): each tell() call produces a stored PerformanceRecord.
- ADR-010 (dual-format storage): the Recorder writes JSONL; the Parquet conversion happens in the Results Store post-write.
