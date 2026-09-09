# Performance Recorder

> Container: [Experiment Runner](../../08-experiment-runner.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Receive per-evaluation observation data from the Evaluation Loop and write PerformanceRecord objects to the Results Store (via the JSONL Performance Writer), providing the bridge between the evaluation subprocess and persistent storage.

---

## Interface

Called by the Evaluation Loop after each `observe()` completes, for the evaluations that `Study.sampling_strategy` selects (ADR-002):

```python
class PerformanceRecorder:
    def record(
        self,
        run_id: str,
        evaluation_number: int,
        objective_value: float,
        current_solution: dict[str, object] | None,
        elapsed_time: float,
    ) -> None:
        """Constructs a Performance Record and writes it to the JSONL writer.

        `best_so_far`, `is_improvement` and `trigger_reason` are computed here,
        not passed in: the recorder is the only component that sees the whole
        sequence for a Run, and the triggers of ADR-002 are defined over it.
        """
```

---

## Dependencies

- **Results Store — JSONL Performance Writer** — the underlying write target. The recorder holds a reference to an open `JsonlPerformanceWriter` instance for the duration of the Run.
- `dataclasses` stdlib (for `PerformanceRecord` construction)

---

## Key Behaviors

1. **Record construction** — assembles a Performance Record with exactly the fields [`07-performance-record.md`](../../../../../03-technical-contracts/01-data-format/07-performance-record.md) defines, and no others. `objective_value` holds the raw result of this evaluation; `best_so_far` holds the running best in the direction of `ProblemInstance.objective.type` (ADR-023). Experiment, algorithm and problem are reached through `run_id` and are not copied onto the record (FR-19).

2. **Trigger-governed recording** — a record is written when `Study.sampling_strategy` schedules one, when the evaluation improves `best_so_far` beyond `Study.improvement_epsilon`, or at end of run; `trigger_reason` states which of the three fired, combined where more than one did (ADR-002, ADR-004). Recording every evaluation is one possible strategy, not the default behaviour.

3. **Failed evaluations** — a Performance Record describes a completed evaluation and has no failure fields. When an evaluation raises, the recorder writes nothing and the Run Isolator records the failure on the Run itself, through `Run.status` and `Run.failure_reason` (FR-12).

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

- FR-14 (anytime-curve granularity): the records this component writes are what every anytime metric is reconstructed from.
- UC-02 step 5 (record results): each `observe()` that a trigger selects produces a stored Performance Record.
- ADR-010 (dual-format storage): the Recorder writes JSONL; the Parquet conversion happens in the Results Store post-write.
