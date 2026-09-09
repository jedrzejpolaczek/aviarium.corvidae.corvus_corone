# Execution Coordinator

> Container: [Study Orchestrator](../../07-study-orchestrator.md)
> C3 Index: [01-index.md](01-index.md)

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

- **Experiment Runner** — one Run at a time, through the Runner interface
  (`02-interface-contracts/04-runner-interface.md`)
- **Results Store**, through the `RepositoryFactory` (ADR-001) — updates Run and Experiment status
- No concurrency primitive. V1 execution is local and sequential (SRS §1.4, boundary B-01);
  `max_workers` is a V2 name and must not appear in a V1 component.

---

## Key Behaviors

> **Unresolved: the failure model below is not in any contract.** `Study.on_failure`, the Run
> statuses `skipped` and `aborted`, the Experiment statuses `partial` and `aborted`, and
> `Experiment.skipped_count` appear in no entity schema. `06-run.md` admits `completed`,
> `failed` and `budget_exhausted`; `05-experiment.md` admits `planned`, `running`, `completed`
> and `failed`; FR-12 requires a failed Run to carry `status="failed"` and a non-empty
> `failure_reason`. Behaviours 2, 3 and 5 are therefore described here against vocabulary that
> does not exist, and this document may not coin it (ADR-012). The decision is open as
> REF-TASK-0041; until it is made and the entity schemas are changed, treat behaviours 2 and 3
> as a proposal, not as a specification.

1. **Sequential dispatch** — iterates the run plan in order and executes one Run to completion before starting the next. The order is the run-plan order the Seed Manager also uses (problem index, then algorithm index, then repetition index), so that the sequence of `SeedSequence` children is reproducible (ADR-017). No parallelism, no worker pool, no futures (B-01).

2. **`skip` policy** — when a Run returns `status=skipped`, the Coordinator records the failure, logs it, and continues to the next Run. The Experiment's `skipped_count` is incremented.

3. **`abort` policy** — a critical error (`SeedCollisionError`, `StorageError`) propagates out of the Coordinator; no further Runs are dispatched. Aborting is the Coordinator's response to the error, not a separate exception type (ADR-015).

4. **Progress reporting** — if `on_progress` is provided, calls it after each Run completes (success or failure). Used by the CLI to display a progress bar.

5. **Status updates** — updates each Run's status through the repository as Runs complete, then sets the Experiment status on exit.

---

## State

Transient in-process state: the set of active futures and their run_id mappings. Not persisted.

---

## Implementation Reference

`corvus_corone/study_orchestrator/execution_coordinator.py`

---

## SRS Traceability

- UC-02 (run study): the Execution Coordinator drives the actual execution.
- FR-11 (Run isolation): each Run executes without shared mutable state. Execution is sequential in V1 — SRS 1.4 boundary B-01 reserves `max_workers` for V2.
- FR-12 (failure policy): `on_failure` behaviour is enforced here.
