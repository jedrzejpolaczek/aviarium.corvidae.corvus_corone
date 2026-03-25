# COCO Exporter

> Container: [Ecosystem Bridge](../../03-c4-leve2-containers/13-ecosystem-bridge.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Convert Corvus Study PerformanceRecords to COCO BBOB format, producing the `data/` directory structure expected by `cocopp` for post-processing and leaderboard submission.

---

## Interface

```python
class COCOExporter:
    def export(
        self,
        experiment_id: str,
        output_dir: Path,
        record_reader: PerformanceRecordReader,
        loss_auditor: LossAuditor,
        coco_suite: str = "bbob",
    ) -> ExportResult:
        """
        Exports experiment to COCO data/ directory.
        Returns: output_path, records_exported, manifest_path.
        """
```

---

## Dependencies

- `cocoex` (`coco-experiment` Python package) — COCO `Suite`, `Observer` for output formatting
- **Results Store — Performance Record Reader** — loads PerformanceRecords
- **Loss Auditor** — called to validate and manifest information loss

---

## Key Behaviors

1. **COCO directory structure** — creates the `data/{algorithm_id}/` output structure expected by `cocopp`. Each algorithm gets its own subdirectory with one data file per problem function.

2. **Record mapping** — maps Corvus PerformanceRecord fields to COCO Observer calls: `candidate` → `x`, `value` → `f(x)`, `iteration` → evaluation count. Budget maps to `cocoex` `evaluations` parameter.

3. **Problem mapping** — maps Corvus problem IDs to COCO function IDs (e.g., `sphere-5d` → `bbob f1 d5`). Unmappable problems are excluded from the export and added to the loss manifest.

4. **Information loss categories** — passes the following loss categories to the Loss Auditor:
   - Multi-objective results: COCO BBOB is single-objective only
   - Conditional parameter spaces: COCO has no conditional parameter representation
   - Custom problem instances: problems not in the COCO suite cannot be exported

5. **Manifest generation** — calls `loss_auditor.audit()` after export; the resulting manifest file is written alongside the COCO data directory.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/ecosystem_bridge/coco_exporter.py`

---

## SRS Traceability

- UC-05 variant (export results): COCO export path.
- FR-B-01 (COCO compatibility): output readable by `cocopp` post-processor.
