# §3 Runner Interface

> Index: [01-interface-contracts.md](01-interface-contracts.md)

The Runner orchestrates Problems and Algorithms to produce Runs. It owns the evaluation loop,
injects seeds, invokes the `on_evaluation` callback after every objective evaluation, and
persists results via the Repository Interface (§5).

→ Used by: researcher (via CLI/API), Experiment container (C2)

**Design decisions recorded here:**
- **V1 is sequential.** The interface is designed to allow parallel execution in V2 without
  breaking changes: `run_study()` accepts no parallelism parameters in V1, but the isolation
  contract (no shared mutable state between Runs) is a hard requirement precisely to enable
  future parallel implementations. `max_workers` is reserved for V2.
- **Run failure: Skip.** When a single Run raises an unexpected exception, the Runner logs
  the failure (`status="failed"`, `failure_reason` populated), increments a failure counter,
  and continues with the remaining Runs. The Experiment `status` is `"completed"` even if
  some Runs failed — callers must inspect individual Run statuses.
- **Critical errors: Abort.** Errors that invalidate the entire Experiment
  (seed collision, repository unavailable, Study not locked) cause `status="aborted"` on
  the Experiment and raise an exception immediately. No further Runs are attempted.

---

### run_study(study: Study) → Experiment

**Signature:**
- `study: Study` — a locked Study record (→ data-format.md §2.3)
- returns: `Experiment` — completed or partially-completed Experiment record (→ data-format.md §2.4)

**Semantics:**
Executes all Runs defined by the Study plan. For each `(problem, algorithm, repetition)`
combination: resolves the instances from the Repository, generates a seed, calls `reset()` and
`initialize()`, executes the evaluation loop, and persists the resulting Run record.

**Preconditions:**
- `study.status == "locked"` — raises `StudyNotLockedError` otherwise
- all `problem_instance_ids` and `algorithm_instance_ids` in the study are resolvable

**Postconditions:**
- returned Experiment contains one Run record per `(problem, algorithm, repetition)` triple
  for all Runs that were attempted (including failed ones)
- all seeds within the Experiment are unique per `(problem_id, algorithm_id)` pair
- `experiment.status` is `"completed"` if all Runs were attempted (some may have `status="failed"`),
  or `"aborted"` if a critical error halted execution early

**Exceptions:**
- `StudyNotLockedError` — study is not in locked state
- `SeedCollisionError` (critical) — duplicate seed detected; Experiment aborted
- `StorageError` (critical) — Repository unavailable; Experiment aborted

---

### run_single(problem_id: str, algorithm_id: str, seed: int, budget: int) → Run

**Signature:**
- `problem_id: str`, `algorithm_id: str` — IDs resolvable from the Repository
- `seed: int` — exact seed to use for this Run
- `budget: int` — evaluation budget for this Run
- returns: `Run` — completed or failed Run record (→ data-format.md §2.5)

**Semantics:**
Executes a single Run. Lower-level than `run_study()`.
Used for: debugging, incremental execution, custom orchestration.
The Run is persisted to the Repository before this method returns.

**Postconditions:**
- `run.seed` equals the provided `seed`
- `run.status` is `"completed"` or `"failed"` (never left as `"running"` after return)
- one `PerformanceRecord` with `trigger_reason` containing `end_of_run` exists in storage
  for every completed Run

---

### resume(experiment_id: str) → Experiment

**Signature:**
- `experiment_id: str` — ID of an existing Experiment in the Repository
- returns: `Experiment` — Experiment after resumption attempt

**Semantics:**
Resumes an interrupted Experiment from its last persisted state.
Incomplete Runs (those with `status != "completed"` and `status != "failed"`) are re-executed
from the beginning — partial Run state is discarded and the Run is re-run with the same seed.

**Preconditions:**
- Experiment exists in the Repository with `status == "running"` or `status == "aborted"`
- the Study referenced by the Experiment is still locked and unchanged

**Postconditions:**
- all Runs that were `"completed"` or `"failed"` before resumption are left unchanged
- all previously incomplete Runs are re-executed and their records updated

---

### on_evaluation(eval_number: int, objective_value: float) → None

**Signature:**
- `eval_number: int` — current evaluation count (1-indexed, monotonically increasing)
- `objective_value: float` — raw value returned by `Problem.evaluate()`

**Semantics:**
Callback invoked internally after every objective evaluation within `run_single()`.
The Runner base class intercepts this to decide whether to write a `PerformanceRecord`
(per ADR-002: scheduled trigger, improvement trigger, end-of-run trigger).
Algorithm Authors do NOT call this method; it is wired by the framework.

**Preconditions:**
- `eval_number` is monotonically increasing within the current Run (starts at 1)
- `objective_value` is the raw value from `Problem.evaluate()` for this evaluation

**Postconditions:**
- if any trigger fires, a `PerformanceRecord` is written with the correct `trigger_reason`,
  `is_improvement`, and `elapsed_time` fields (→ data-format.md §2.6, ADR-002)
- the Runner's internal `best_so_far` is updated if `objective_value` improves

**Extension point:**
Subclasses MAY override `on_evaluation()` to implement custom logging, but MUST call
`super().on_evaluation()` to preserve the standard ADR-002 trigger logic, or populate
`trigger_reason` manually per ADR-002.

→ PerformanceRecord schema: data-format.md §2.6
→ Recording strategy: [adr-002-performance-recording-strategy.md](../../02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md)

---

### Isolation Contract (critical for reproducibility)

The following rules are MANDATORY for all Runner implementations:

- Each Run executes in isolation — no shared mutable state between Runs
- Seeds are injected by the Runner; never generated inside Problem or Algorithm
- The Runner calls `Problem.reset(seed)` and `Algorithm.initialize(search_space, seed)`
  before every Run, regardless of whether the instances are shared or per-Run
- The Runner records the full execution environment in the Experiment record
  (→ data-format.md §2.4 `execution_environment`)

→ SRS NFR-REPRO; MANIFESTO Principle 18

**Note on future parallelism:**
The isolation contract above is sufficient for parallel execution. A V2 parallel Runner
MUST satisfy the same isolation rules. The `run_study()` interface will accept a
`max_workers: int = 1` parameter in V2 without changing the semantics of the return value.
