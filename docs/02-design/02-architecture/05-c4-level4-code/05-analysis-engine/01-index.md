# C4: Code — Analysis Engine

> C4 Top-level Index: [../01-index.md](../01-index.md)
> C3 Container Index: [../../04-c4-leve3-components/04-analysis-engine/01-index.md](../../04-c4-leve3-components/04-analysis-engine/01-index.md)

---

## Documented Abstractions

| File | Abstraction | Why C4 |
|---|---|---|
| [02-metric-dispatcher.md](02-metric-dispatcher.md) | `MetricDispatcher` | Single authoritative map from metric name → computation; adding any new metric requires extending this component's internal registry |

---

## Shared Abstractions Used by This Container

The following cross-container abstractions from [02-shared/](../02-shared/) are consumed here:

| Abstraction | Role in Analysis Engine |
|---|---|
| [`PerformanceRecord`](../02-shared/03-performance-record.md) | `MetricDispatcher` loads and aggregates records per `(algorithm_id, problem_id)` pair |
| [`StudyConfig` / `AnalysisConfig`](../02-shared/04-study-spec.md) | `AnalysisConfig` (carried inside `StudyConfig`) specifies which metrics to compute, the significance level, and whether pre-registration is enforced |
