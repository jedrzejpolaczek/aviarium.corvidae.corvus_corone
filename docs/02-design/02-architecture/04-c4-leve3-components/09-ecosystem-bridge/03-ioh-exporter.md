# IOH Exporter

> Container: [Ecosystem Bridge](../../03-c4-leve2-containers/13-ecosystem-bridge.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Convert Corvus Study PerformanceRecords to IOHprofiler JSON format, producing the `.dat` and `.info` files expected by the IOH Analyzer web tool.

---

## Interface

```python
class IOHExporter:
    def export(
        self,
        experiment_id: str,
        output_dir: Path,
        record_reader: PerformanceRecordReader,
        loss_auditor: LossAuditor,
    ) -> ExportResult:
        """
        Exports experiment to IOH format.
        Returns: output_path, records_exported, manifest_path.
        """
```

---

## Dependencies

- `ioh` (IOHprofiler Python package) — `IOH_logger` for format-compliant output
- **Results Store — Performance Record Reader**
- **Loss Auditor**

---

## Key Behaviors

1. **IOH directory structure** — creates `{algorithm_id}/{problem_id}/` with `.dat` files (one per run) and a `.info` index file per algorithm-problem combination.

2. **Record mapping** — maps: `iteration` → evaluation count, `value` → `f(x)`, `best_so_far` → `fbest`. The IOH format requires monotone `fbest` — if the raw data is not monotone (due to algorithm behaviour), the exporter enforces monotonicity and notes it in the loss manifest.

3. **Multi-objective handling** — IOH Analyzer supports multi-objective data via a separate schema. Multi-objective Corvus results are exported to the IOH multi-objective format if detected; otherwise added to the loss manifest.

4. **Information loss categories** — passes to Loss Auditor:
   - Non-BBOB-compatible problem instances
   - Non-monotone `best_so_far` sequences (monotonicity enforced on export)
   - Algorithm hyperparameter metadata (not captured in IOH `.dat` format)

5. **Manifest generation** — calls `loss_auditor.audit()` and writes manifest alongside output.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/ecosystem_bridge/ioh_exporter.py`

---

## SRS Traceability

- FR-B-02 (IOH compatibility): output readable by IOH Analyzer.
