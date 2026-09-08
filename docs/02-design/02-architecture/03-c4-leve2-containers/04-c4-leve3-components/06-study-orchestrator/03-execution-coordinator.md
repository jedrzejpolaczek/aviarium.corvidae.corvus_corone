# Execution Coordinator

> Container: [Study Orchestrator](../../03-c4-leve2-containers/07-study-orchestrator.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Dispatch the run plan to the Experiment Runner, collect results as Runs complete, handle partial failures per the `on_failure` policy, and update Study/Experiment status in the Results Store throughout execution.

---

## Interface

Called by the Study Orchestrator entry point after Study Builder completes:

```python
class ExecutionCoordinator:
    def execute(
        self,
        study_config: StudyConfig,
        run_plan: list[RunConfig],
        experiment_runner: ExperimentRunner,
        entity_store: JsonEntityStore,
        on_progress: Callable[[RunResult], None] | None = None,
    ) -> ExecutionSummary:
        """
        Dispatches all runs in the plan; returns summary of outcomes.
        ExecutionSummary: total, succeeded, skipped, aborted, duration_s.
        """
```

---

## Dependencies

- **Experiment Runner** — calls `run_isolator.execute_run()` for each RunConfig
- **Results Store — JSON Entity Store** — updates Run and Experiment status
- Python `concurrent.futures.ProcessPoolExecutor` — for parallel run execution

---

## Key Behaviors

1. **Parallel dispatch** — uses `ProcessPoolExecutor(max_workers=study_config.max_workers)` to execute Runs in parallel. Each Run is submitted as a separate future.

2. **`skip` policy** — when a Run returns `status=skipped`, the Coordinator records the failure, logs it, and continues to the next Run. The Experiment's `skipped_count` is incremented.

3. **`abort` policy** — when a Run returns `status=aborted`, the Coordinator cancels all pending futures, marks the Experiment `status=aborted`, and raises `StudyAbortedError`. No further Runs are dispatched.

4. **Progress reporting** — if `on_progress` is provided, calls it after each Run completes (success or failure). Used by the CLI to display a progress bar.

5. **Status updates** — updates each Run's status in the JSON Entity Store as Runs complete. Updates the Experiment status from `running` → `completed` / `partial` / `aborted` on coordinator exit.

---

## State

Transient in-process state: the set of active futures and their run_id mappings. Not persisted.

---

## Implementation Reference

`corvus_corone/study_orchestrator/execution_coordinator.py`

---

## SRS Traceability

- UC-02 (run study): the Execution Coordinator drives the actual execution.
- FR-O-02 (parallel execution): Runs execute in parallel up to `max_workers`.
- FR-O-03 (failure policy): `on_failure` behaviour is enforced here.
