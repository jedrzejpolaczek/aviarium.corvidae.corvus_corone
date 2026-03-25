# C4: Code — Experiment Runner

> C4 Top-level Index: [../01-index.md](../01-index.md)
> C3 Container Index: [../../04-c4-leve3-components/03-experiment-runner/01-index.md](../../04-c4-leve3-components/03-experiment-runner/01-index.md)

---

## Documented Abstractions

| File | Abstraction | Why C4 |
|---|---|---|
| [02-seed-manager.md](02-seed-manager.md) | `SeedManager` | Reproducibility enforcement boundary — seed derivation formula and injection order are normative; changing either breaks all previously recorded runs |
| [03-evaluation-loop.md](03-evaluation-loop.md) | `EvaluationLoop` | Core ask/tell execution contract — the only place in the system that calls `algorithm.ask()`, `problem.evaluate()`, and `algorithm.tell()`; loop semantics are normative |

---

## Shared Abstractions Used by This Container

The following cross-container abstractions from [02-shared/](../02-shared/) are consumed here:

| Abstraction | Role in Experiment Runner |
|---|---|
| [`AlgorithmInterface`](../02-shared/01-algorithm-interface.md) | `EvaluationLoop` calls `ask()`, `tell()`, `reset()` on every Run |
| [`ProblemInterface`](../02-shared/02-problem-interface.md) | `EvaluationLoop` calls `evaluate()` on every candidate solution |
| [`PerformanceRecord`](../02-shared/03-performance-record.md) | `PerformanceRecorder` constructs and streams one record per evaluation |
| [`RunConfig`](../02-shared/04-study-spec.md) | `RunIsolator` receives a `RunConfig` per subprocess — seed, budget, algorithm/problem IDs |
