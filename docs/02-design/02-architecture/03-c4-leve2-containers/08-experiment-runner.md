# Container: Experiment Runner

> Index: [01-c2-containers.md](01-c2-containers.md)

**Responsibility:** Execute individual Runs — the innermost evaluation loop. For each
`(problem, algorithm, repetition)` triple: resolves instances from the registry and
repository, injects seeds, calls the Algorithm ask-tell interface, invokes `Problem.evaluate()`,
fires performance recording triggers (ADR-002: scheduled, improvement, end-of-run), and
persists `Run` and `PerformanceRecord` entities. Runs are isolated: no shared mutable state
between Runs.

**Technology:** Python.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Run execution | `run_study(study)` / `run_single(problem_id, algorithm_id, seed, budget)` | Study Orchestrator |
| Resume | `resume(experiment_id)` — re-executes incomplete Runs from last persisted state | Study Orchestrator (UC-05 reproducibility, FR-18) |
| Evaluation callback | `on_evaluation(eval_number, objective_value)` — internal hook; wired by the framework | Not called by Algorithm Authors |

Full interface contract: [`../../../03-technical-contracts/02-interface-contracts/04-runner-interface.md`](../../../03-technical-contracts/02-interface-contracts/04-runner-interface.md)

**Dependencies:**

| Dependency | Reason |
|---|---|
| Algorithm Registry | Loads `AlgorithmInstance` to instantiate the algorithm implementation for each Run |
| Problem Repository | Loads `ProblemInstance` to instantiate the problem for each Run |
| Results Store | Writes `Run` records (create, update status) and `PerformanceRecord` batches after each triggered recording point |

**Data owned:** None. `Run` and `PerformanceRecord` entities are owned by the Results Store;
the Runner writes them but does not hold them.

**Failure handling:** A Run that raises an unexpected exception is logged as
`status="failed"` with `failure_reason` populated; execution continues with remaining Runs.
Critical errors (seed collision, storage unavailable) abort the entire Experiment
(`status="aborted"`).

**Actors served:** Researcher (indirectly, via Study Orchestrator — UC-01 main execution
workflow, UC-05 reproducibility).

**Relevant SRS section:** FR-08 (study execution), FR-09 (seed injection), FR-10 (run
isolation), FR-11 (evaluation budget enforcement), FR-12 (failure handling — skip vs abort),
FR-19 (execution environment capture).
