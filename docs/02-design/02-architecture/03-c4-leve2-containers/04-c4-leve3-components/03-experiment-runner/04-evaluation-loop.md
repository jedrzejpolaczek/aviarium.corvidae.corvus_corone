# Evaluation Loop

> Container: [Experiment Runner](../../08-experiment-runner.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Drive the algorithm's ask/tell evaluation cycle for a single Run within budget, passing each candidate solution to the objective function and recording every observation via the Performance Recorder.

---

## Interface

Called within the Run subprocess by the Run Isolator:

```python
class EvaluationLoop:
    def run(
        self,
        algorithm: AlgorithmInstance,
        problem: ProblemInstance,
        budget: int,
        recorder: PerformanceRecorder,
    ) -> LoopResult:
        """
        Runs the ask-tell cycle for `budget` evaluations.
        Notifies the recorder after every evaluation; whether a PerformanceRecord is
        written is the recorder's decision, taken from the ADR-002 triggers.
        Returns a `LoopResult`.
        """
```

`LoopResult` fields: `evaluations_completed` (int), `best_value` (float),
`converged` (bool, true when the algorithm stopped before the budget was spent).

---

## Dependencies

- **Performance Recorder** — notified after every `observe()` call. The loop does not decide what is stored: ADR-002 writes a record only when the scheduled, improvement or end-of-run trigger fires, so most evaluations produce no record.
- Algorithm instance (provides `suggest()`, `observe()`, `initialize()`)
- Problem instance object (provides `evaluate()` method)
- `time` stdlib (for per-evaluation timing)

---

## Key Behaviors

1. **Ask-tell cycle** — the interaction protocol is `suggest` and `observe`, as defined by
   the Algorithm Interface. `ask` and `tell` are Optuna and Nevergrad names and do not appear
   in this system.

   ```
   evaluation_number = 0
   while evaluation_number < budget:
       solutions = algorithm.suggest(context, batch_size)
       for solution in solutions:
           if evaluation_number == budget:
               break                      # the loop owns the budget, not the algorithm
           result = problem.evaluate(solution)     # -> EvaluationResult
           evaluation_number += 1                  # 1-indexed, matches the schema
           algorithm.observe(solution, result)     # one call per solution, in order
           recorder.observe(evaluation_number, result)
   ```

   `observe()` is called once per suggested solution and in the order the solutions were
   returned. An implementation that reports a whole batch against the last suggestion is
   wrong for any `batch_size` above 1.

2. **Budget enforcement** — the loop runs for exactly `budget` *evaluations*, not `budget` iterations. With a batch size above 1 those differ, and a partial batch at the boundary is truncated rather than overrun. The algorithm does not control the stopping criterion — the loop does. If the algorithm raises `StopIteration` internally, the loop catches it and treats it as early convergence (marks `converged=True` in `LoopResult`).

3. **Best-so-far tracking** — maintains the running best across all evaluations and passes it
   to the Performance Recorder, which stores it as `PerformanceRecord.best_so_far` alongside the
   raw `objective_value` of that evaluation (ADR-023).

4. **Evaluation timing** — records wall-clock time per evaluation in milliseconds. Stored in the PerformanceRecord for outlier detection (pathologically slow evaluations indicate implementation problems).

5. **Exception isolation** — if `problem.evaluate()` raises, the loop catches it, stops the Run,
   and the Run record carries `status = "failed"` with `failure_reason` set from the exception
   (FR-12). A PerformanceRecord has no status field, so a failed evaluation produces no record.
   If `algorithm.suggest()` or `algorithm.observe()` raises, the loop re-raises: an algorithm
   failure is a Run-level failure.

---

## State

Transient in-process state: `best_value`, `best_candidate`, `iteration_count`. All persistent data is written by the Performance Recorder. State is lost when the subprocess exits.

---

## Implementation Reference

`corvus_corone/experiment_runner/evaluation_loop.py`

---

## SRS Traceability

- FR-12 (failed Runs are recorded): a Run that ends before its budget is exhausted is recorded with its failure reason, never silently dropped.
- UC-02 step 4 (execute run): each evaluation produces a PerformanceRecord.
