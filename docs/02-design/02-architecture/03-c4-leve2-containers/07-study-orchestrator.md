# Container: Study Orchestrator

> Index: [01-c2-containers.md](01-c2-containers.md)

**Responsibility:** Coordinate the full lifecycle of a Study — from creation and locking
through execution and analysis to report generation. Acts as the top-level workflow engine:
receives a Study from the Public API, delegates individual Run execution to the Experiment
Runner, triggers metric computation via the Analysis Engine once all Runs complete, and
triggers report generation via the Reporting Engine.

**Technology:** Python.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Study orchestration | Called by Public API via `cc.create_study()` and `cc.run()` | Researcher (via API or `corvus run`) |
| Study lifecycle transitions | `create_study()` → draft, `lock_study()` → locked, run → completed | Internal; state transitions persist to Results Store |

**Dependencies:**

| Dependency | Reason |
|---|---|
| Experiment Runner | Delegates execution of individual Runs for each `(problem, algorithm, repetition)` triple in the Study plan |
| Analysis Engine | Triggers metric computation (`analyze()`) after all Runs in an Experiment reach `"completed"` or `"failed"` status |
| Reporting Engine | Triggers report generation (`generate_reports()`) after analysis completes, if requested by the caller |
| Results Store | Creates and updates Study, Experiment records; reads status to detect completion and resume interrupted experiments |

**Data owned:** None. Study and Experiment records are persisted by the Results Store; the
Orchestrator only drives transitions.

**Actors served:** Researcher (primary — drives the main study execution workflow, UC-01, UC-05).

**Relevant SRS section:** FR-08 (study execution entry point), FR-09 (seed management),
FR-10 (run isolation), FR-17 (reproducibility — locking and immutability), FR-18 (resume
interrupted experiments), FR-19 (execution environment capture).
