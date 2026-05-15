# Result Reader

> Container: [Reporting Engine](../../03-c4-leve2-containers/05-reporting-engine.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Load aggregated MetricResults, TestResults, and entity metadata (Study, Experiment, Run summaries) from the Results Store for use by the HTML Template Renderer.

---

## Interface

```python
class ResultReader:
    def load_report_data(
        self,
        experiment_id: str,
        entity_store: JsonEntityStore,
        record_reader: PerformanceRecordReader,
    ) -> ReportData:
        """
        Loads all data needed to render the report.
        Raises ReportDataNotFoundError if MetricResults are absent.
        """
```

`ReportData` fields: `experiment`, `study`, `runs_summary`, `metric_results`, `test_results`, `algorithm_metadata`, `problem_metadata`.

---

## Dependencies

- **Results Store — JSON Entity Store** — loads Study, Experiment, Run entities
- **Results Store — Performance Record Reader** — loads aggregated convergence data for report charts

---

## Key Behaviors

1. **Entity loading** — loads the Experiment entity, parent Study, and all Run summaries (status, duration, seed, outcome).

2. **MetricResult loading** — reads MetricResults from the Results Store. If none exist for the experiment, raises `ReportDataNotFoundError` with a clear message indicating analysis has not run.

3. **Convergence data loading** — loads a downsampled convergence time-series per algorithm (median best-so-far across runs at each budget fraction) for the convergence chart.

4. **Metadata enrichment** — attaches full Algorithm and Problem metadata to the `ReportData` so that the template renderer does not need to query the registry.

5. **Partial data handling** — if some Runs are `skipped` or `aborted`, includes them in `runs_summary` with their status. Does not exclude partial data silently.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/reporting_engine/result_reader.py`

---

## SRS Traceability

- UC-06 (view report): report data loading is the first step of report generation.
- FR-P-01 (report completeness): all required data must be present before rendering begins.
