# Post-Execution Pipeline

> Container: [Study Orchestrator](../../03-c4-leve2-containers/07-study-orchestrator.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Trigger the Analysis Engine and Reporting Engine in sequence after all Runs in a Study complete, coordinate the Parquet conversion of Run performance files, and update the Experiment status to reflect post-execution outcomes.

---

## Interface

Called by the Execution Coordinator on completion:

```python
class PostExecutionPipeline:
    def run(
        self,
        experiment_id: str,
        study_config: StudyConfig,
        analysis_engine: AnalysisEngine,
        reporting_engine: ReportingEngine,
        parquet_writer: ParquetPerformanceWriter,
        entity_store: JsonEntityStore,
    ) -> PostExecutionResult:
        """
        Runs: (1) Parquet conversion, (2) Analysis, (3) Reporting.
        Returns: analysis_status, report_path, errors.
        """
```

---

## Dependencies

- **Analysis Engine** — called for metric computation and statistical testing
- **Reporting Engine** — called for report generation
- **Results Store — Parquet Performance Writer** — triggered for each completed Run
- **Results Store — JSON Entity Store** — updates Experiment status

---

## Key Behaviors

1. **Parquet conversion** — for each completed Run in the experiment, calls `ParquetPerformanceWriter.convert_run()`. Runs below the threshold (< 1000 records) are skipped silently. Conversion is done sequentially (not parallel) to avoid I/O contention.

2. **Analysis trigger** — calls `AnalysisEngine.analyse(experiment_id, study_config.analysis)`. If the analysis fails, records the error in `PostExecutionResult` and updates the Experiment status to `analysis_failed`. Does not raise — the pipeline continues to attempt reporting.

3. **Reporting trigger** — calls `ReportingEngine.generate(experiment_id, study_config.reporting)` after analysis completes. If reporting fails, records the error and updates the Experiment status to `report_failed`.

4. **Status update** — after all pipeline steps, sets the final Experiment `status`:
   - All steps succeeded → `completed`
   - Analysis failed → `analysis_failed`
   - Report failed → `report_failed`
   - Both failed → `pipeline_failed`

5. **Skipped runs exclusion** — passes the list of `skipped_run_ids` to the Analysis Engine so it excludes them from metric computation.

---

## State

No persistent in-memory state. All status is written to the Results Store via the JSON Entity Store.

---

## Implementation Reference

`corvus_corone/study_orchestrator/post_execution_pipeline.py`

---

## SRS Traceability

- UC-02 step 6 (post-execution pipeline): triggered automatically after all Runs complete.
- FR-O-04 (automatic analysis and reporting): pipeline runs without user intervention after execution.
