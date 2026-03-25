# Parquet Performance Writer

> Container: [Results Store](../../03-c4-leve2-containers/12-results-store.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Convert a completed Run's JSONL performance file to Parquet/snappy format when the record count meets the threshold (≥ 1,000 records), enabling fast bulk queries over large performance datasets.

---

## Interface

```python
class ParquetPerformanceWriter:
    def convert_run(
        self,
        run_id: str,
        repo: LocalFileRepository,
        threshold: int = 1000,
    ) -> ConversionResult:
        """
        Reads JSONL, writes Parquet if record_count >= threshold.
        Returns: records_converted, jsonl_path, parquet_path, skipped_reason.
        """
```

Called by the Study Orchestrator's Post-Execution Pipeline after a Run completes.

---

## Dependencies

- **Local File Repository** — path resolution for JSONL and Parquet files
- `pyarrow` — Parquet write (`pyarrow.parquet.write_table`)
- `pyarrow.csv` — fast JSONL-to-Arrow conversion

---

## Key Behaviors

1. **Threshold check** — counts lines in the JSONL file before converting. If line count < threshold, returns `ConversionResult(skipped_reason="below_threshold")` without writing any Parquet file.

2. **Schema enforcement** — converts the JSONL records to a `pyarrow.Table` with a fixed schema (all PerformanceRecord fields typed). This prevents schema drift between JSONL and Parquet.

3. **Snappy compression** — writes Parquet with `compression="snappy"` (ADR-010 default; 9.3× size reduction vs. JSONL at 59× query speedup).

4. **JSONL preservation** — does NOT delete the JSONL file after conversion. Both files coexist. The Performance Record Reader prefers Parquet when both exist. The JSONL file serves as the backup.

5. **Failure safety** — if conversion fails mid-write (e.g., disk full), the partial Parquet file is deleted. The JSONL file remains intact as the source of truth.

---

## State

No persistent state. The Parquet file on disk is the output artifact.

---

## Implementation Reference

`corvus_corone/results_store/parquet_performance_writer.py`

---

## SRS Traceability

- ADR-010: Parquet/snappy is the secondary performance storage format for ≥1000 records.
- FR-S-04 (query performance): bulk queries over large Run datasets require Parquet.
