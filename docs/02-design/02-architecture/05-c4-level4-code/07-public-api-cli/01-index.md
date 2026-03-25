# C4: Code — Public API + CLI

> C4 Top-level Index: [../01-index.md](../01-index.md)
> C3 Container Index: [../../04-c4-leve3-components/10-public-api-cli/01-index.md](../../04-c4-leve3-components/10-public-api-cli/01-index.md)

---

## Documented Abstractions

| File | Abstraction | Why C4 |
|---|---|---|
| [02-api-facade.md](02-api-facade.md) | `APIFacade` (cc.*) | Versioned public surface consumed by the CLI, the Pilot MCP Server, and all external callers — any signature change is a breaking change |

---

## Shared Abstractions Used by This Container

The following cross-container abstractions from [02-shared/](../02-shared/) are consumed here:

| Abstraction | Role in Public API + CLI |
|---|---|
| [`StudyConfig` / `RunConfig`](../02-shared/04-study-spec.md) | `cc.run()` accepts raw dict or `StudyConfig`; the facade coerces and passes a validated `StudyConfig` to the Study Orchestrator |
| [`AlgorithmInterface`](../02-shared/01-algorithm-interface.md) | `cc.list_algorithms()` and `cc.get_algorithm()` resolve and return `AlgorithmInstance` wrappers |
| [`ProblemInterface`](../02-shared/02-problem-interface.md) | `cc.list_problems()` and `cc.get_problem()` resolve and return `ProblemInstance` wrappers |
