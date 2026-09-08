# Run Isolator

> Container: [Experiment Runner](../../03-c4-leve2-containers/08-experiment-runner.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Wrap each algorithm Run in an isolated subprocess with resource limits, handle failure modes (skip vs. abort), and coordinate the lifecycle of the Seed Manager and Evaluation Loop within the subprocess.

---

## Interface

Called by the Study Orchestrator:

```python
class RunIsolator:
    def execute_run(
        self,
        run_config: RunConfig,
        results_dir: Path,
        on_failure: Literal["skip", "abort"],
    ) -> RunResult:
        """
        Spawns a subprocess, injects seed, runs the evaluation loop.
        Returns RunResult with status: success | skipped | aborted.
        """
```

`RunResult` fields: `run_id`, `status`, `duration_s`, `observations_count`, `error` (None on success).

---

## Dependencies

- **Seed Manager** — called at subprocess start to inject seed
- **Evaluation Loop** — called within the subprocess to run the ask/tell cycle
- Python `multiprocessing` (subprocess spawn, not fork — for isolation)
- `resource` stdlib (Unix) / `psutil` (Windows) — for memory limit enforcement

---

## Key Behaviors

1. **Subprocess spawn** — uses `multiprocessing.Process` with `start_method="spawn"` (not `fork`) to ensure a clean process state for each Run. This prevents state leakage between Runs.

2. **Resource limits** — sets `RLIMIT_AS` (Unix) or equivalent (Windows via `psutil.Process.memory_info`) to `memory_limit_mb` from `RunConfig`. If the limit is exceeded, the subprocess is killed and the Run is marked `aborted`.

3. **Failure handling**:
   - `on_failure="skip"`: if the subprocess exits with a non-zero code or raises an exception, mark the Run `status=skipped` and return immediately. Do not re-raise.
   - `on_failure="abort"`: if the subprocess exits non-zero, raise `RunAbortedError` — the Study Orchestrator catches this and stops the Study.

4. **Timeout enforcement** — if `RunConfig.timeout_s` is set and the subprocess exceeds it, the process is killed and the Run is marked `status=aborted` (regardless of `on_failure` setting — timeouts are always fatal).

5. **Subprocess coordination** — passes `RunConfig` (including `run_id`, `seed`, `budget`, algorithm reference, problem reference) to the subprocess via `multiprocessing.Queue`. The subprocess writes its `RunResult` back via the same Queue.

---

## State

No persistent state. Each `execute_run()` call is fully self-contained. The subprocess writes all persistent data to the filesystem via the Performance Recorder.

---

## Implementation Reference

`corvus_corone/experiment_runner/run_isolator.py`

---

## SRS Traceability

- FR-R-02 (run isolation): each Run's random state and memory must not affect other Runs.
- UC-02 step 4 (execute run): runs are isolated and failures are handled per `on_failure` policy.
