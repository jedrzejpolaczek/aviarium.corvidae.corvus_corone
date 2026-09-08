# Metric Dispatcher

> Container: [Analysis Engine](../../03-c4-leve2-containers/09-analysis-engine.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Load PerformanceRecords from the Results Store, compute the configured benchmark metrics for each algorithm/problem combination, and dispatch metric results to the Statistical Tester for significance testing.

---

## Interface

Entry point for the Analysis Engine — called by the Study Orchestrator:

```python
class MetricDispatcher:
    def dispatch(
        self,
        experiment_id: str,
        analysis_config: AnalysisConfig,
        results_store: PerformanceRecordReader,
    ) -> list[RawMetricResult]:
        """
        Loads records, computes metrics, returns raw results per algorithm/problem/budget.
        """
```

`RawMetricResult` fields: `experiment_id`, `algorithm_id`, `problem_id`, `budget`, `metric_name`, `values` (list of per-run floats), `run_ids`.

---

## Dependencies

- **Results Store — Performance Record Reader** — loads PerformanceRecords for the experiment
- **LOCF Interpolator** — called before metric computation to fill missing data
- **Statistical Tester** — receives `RawMetricResult` list for significance testing
- `scipy.stats` — used for the ECDF computation behind `ANYTIME-ECDF_AREA` (ADR-007)

---

## Key Behaviors

1. **Pre-registration enforcement** — before computing any metric, checks that the requested metrics match the pre-registration configuration. If `analysis_config.pre_registration` is `True` and the requested metrics differ from the registered set, raises `PreRegistrationViolationError`.

2. **Metric computation** — computes each configured metric across all Runs for each algorithm/problem combination:
   - `QUALITY-BEST_VALUE_AT_BUDGET`: `best_so_far` value at the final evaluation for each Run.
   - `TIME-EVALUATIONS_TO_TARGET`: evaluations to reach a pre-specified target, censored at budget + 1.
   - `ANYTIME-ECDF_AREA`: normalised area under the ECDF of best-so-far values (ADR-007). The metric taxonomy is the only source of metric identifiers (ADR-012); a metric absent from it cannot be dispatched.

3. **Missing data handling** — calls the LOCF Interpolator on PerformanceRecords before metric computation. Runs with zero records are excluded and flagged.

4. **Result grouping** — groups computed metric values by `(algorithm_id, problem_id, budget)` into `RawMetricResult` objects. One `RawMetricResult` per unique combination per metric.

5. **Dispatch to tester** — passes the list of `RawMetricResult` objects to the Statistical Tester for pairwise significance testing.

---

## State

No persistent state. All computation is in-memory per Study analysis invocation.

---

## Implementation Reference

`corvus_corone/analysis_engine/metric_dispatcher.py`

---

## SRS Traceability

- FR-A-01 (compute benchmark metrics): dispatcher computes all configured metrics.
- UC-03 step 3 (analyse results): metrics computed after Run completion.
