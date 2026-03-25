# Evaluation Loop

> Container: [Experiment Runner](../../03-c4-leve2-containers/08-experiment-runner.md)
> C3 Index: [index.md](index.md)

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
        Runs the ask/tell cycle for `budget` evaluations.
        Calls recorder.record() on every observation.
        Returns LoopResult with: evaluations_completed, best_value, converged.
        """
```

---

## Dependencies

- **Performance Recorder** — `recorder.record()` called after every `tell()` call
- Algorithm instance object (provides `ask()` and `tell()` methods)
- Problem instance object (provides `evaluate()` method)
- `time` stdlib (for per-evaluation timing)

---

## Key Behaviors

1. **Ask/tell cycle** — standard black-box optimization loop:
   ```
   for i in range(budget):
       candidates = algorithm.ask()
       values = [problem.evaluate(c) for c in candidates]
       algorithm.tell(candidates, values)
       recorder.record(iteration=i, candidates=candidates, values=values, ...)
   ```

2. **Budget enforcement** — the loop runs for exactly `budget` evaluations. The algorithm does not control the stopping criterion — the loop does. If the algorithm raises `StopIteration` internally, the loop catches it and treats it as early convergence (marks `converged=True` in `LoopResult`).

3. **Best-so-far tracking** — maintains `best_value` and `best_candidate` across all evaluations. Updated after each `tell()`. Passed to the Performance Recorder on each call.

4. **Evaluation timing** — records wall-clock time per evaluation in milliseconds. Stored in the PerformanceRecord for outlier detection (pathologically slow evaluations indicate implementation problems).

5. **Exception isolation** — if `problem.evaluate()` raises an exception, the loop catches it, records the evaluation as `status=failed` with the exception message, and continues. If `algorithm.ask()` or `algorithm.tell()` raises, the loop re-raises (algorithm failure is a Run-level failure, not evaluation-level).

---

## State

Transient in-process state: `best_value`, `best_candidate`, `iteration_count`. All persistent data is written by the Performance Recorder. State is lost when the subprocess exits.

---

## Implementation Reference

`corvus_corone/experiment_runner/evaluation_loop.py`

---

## SRS Traceability

- FR-E-01 (evaluation loop): the loop must complete exactly `budget` evaluations unless the algorithm signals early convergence.
- UC-02 step 4 (execute run): each evaluation produces a PerformanceRecord.
