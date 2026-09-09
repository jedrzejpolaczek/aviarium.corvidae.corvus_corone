# Execution Coordinator

> Container: [Study Orchestrator](../../07-study-orchestrator.md)
> C3 Index: [index.md](01-index.md)

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
        study_config: Study,
        run_plan: list[Run],
        experiment_runner: ExperimentRunner,
        entity_store: RepositoryFactory,
        on_progress: Callable[[RunResult], None] | None = None,
    ) -> ExecutionSummary:
        """
        Dispatches all runs in the plan; returns summary of outcomes.
        ExecutionSummary: total, succeeded, skipped, aborted, duration_s.
        """
```

`ExecutionSummary` fields: `total` (int), `succeeded` (int), `skipped` (int),
`aborted` (int), `duration_s` (float).

---

## Dependencies

- **Experiment Runner** — calls `run_isolator.execute_run()` for each Run
- **Results Store**, through the `RepositoryFactory` (ADR-001) — updates Run and Experiment status
- Python `concurrent.futures.ProcessPoolExecutor` — for parallel run execution

---

## Key Behaviors

1. **Parallel dispatch** — uses `ProcessPoolExecutor(max_workers=study_config.max_workers)` to execute Runs in parallel. Each Run is submitted as a separate future.

2. **`skip` policy** — when a Run returns `status=skipped`, the Coordinator records the failure, logs it, and continues to the next Run. The Experiment's `skipped_count` is incremented.

3. **`abort` policy** — when a Run returns `status=aborted`, the Coordinator cancels all pending futures, marks the Experiment `status=aborted`, and raises the critical error itself (`SeedCollisionError`, `StorageError`) propagates; aborting is the Runner's response to it, not a separate exception type (ADR-015). No further Runs are dispatched.

4. **Progress reporting** — if `on_progress` is provided, calls it after each Run completes (success or failure). Used by the CLI to display a progress bar.

5. **Status updates** — updates each Run's status through the repository as Runs complete. Updates the Experiment status from `running` → `completed` / `partial` / `aborted` on coordinator exit.

---

## State

Transient in-process state: the set of active futures and their run_id mappings. Not persisted.

---

## Implementation Reference

`corvus_corone/study_orchestrator/execution_coordinator.py`

---

## SRS Traceability

- UC-02 (run study): the Execution Coordinator drives the actual execution.
- FR-11 (parallel execution): Runs execute in parallel up to `max_workers`.
- FR-12 (failure policy): `on_failure` behaviour is enforced here.
