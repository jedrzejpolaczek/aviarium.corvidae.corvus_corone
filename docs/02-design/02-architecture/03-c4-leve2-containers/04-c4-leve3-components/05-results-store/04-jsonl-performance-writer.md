# JSONL Performance Writer

> Container: [Results Store](../../12-results-store.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Stream PerformanceRecord observations to a JSONL file during Run execution, providing low-latency append-only writes that survive subprocess crashes mid-run.

---

## Interface

```python
class JsonlPerformanceWriter:
    def __init__(self, run_id: str, repo: LocalFileRepository) -> None: ...
    def write(self, record: PerformanceRecord) -> None: ...
    def flush(self) -> None: ...
    def close(self) -> None: ...
```

Called by the Performance Recorder component within the Experiment Runner.

---

## Dependencies

- **Local File Repository** — resolves `performance.jsonl` path for the run
- Python `io` stdlib (buffered file I/O)
- `json` stdlib

---

## Key Behaviors

1. **Streaming append** — opens the JSONL file in append mode (`"a"`) at construction. Each `write()` call appends one JSON line (one serialised PerformanceRecord + newline) to the file.

2. **Buffered I/O** — uses a 64 KB in-process write buffer. The buffer is flushed every 100 records (called by the Performance Recorder) and on `close()`.

3. **Crash resilience** — because each record is a complete, independent JSON line, a crash mid-write at most corrupts the last incomplete line. On resume the reader skips that line and logs it; the Run's own `status` and `failure_reason` fields carry the outcome, and no separate data-quality field exists.

4. **No read capability** — this component is write-only. Reading is handled by the Performance Record Reader.

5. **File creation** — if the JSONL file does not exist at construction time, it is created. If it already exists (resume scenario), new records are appended to the existing file.

---

## State

Open file handle to `performance.jsonl` for the run_id. Closed on `close()`.

---

## Implementation Reference

`corvus_corone/results_store/jsonl_performance_writer.py`

---

## SRS Traceability

- FR-14 (anytime-curve granularity): the writer must sustain the recording rate that `Study.sampling_strategy` declares, so that granularity is a methodological choice and not an I/O limit.
- ADR-010: JSONL is the primary write format; chosen for streaming write performance (20× faster than SQLite).
