# Loss Auditor

> Container: [Ecosystem Bridge](../../03-c4-leve2-containers/13-ecosystem-bridge.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Validate the completeness of an export by comparing the Corvus source data against what was successfully written to the target format, and produce a structured information-loss manifest documenting every field and record that could not be faithfully represented.

---

## Interface

```python
class LossAuditor:
    def audit(
        self,
        source_records: list[PerformanceRecord],
        exported_records: list[PerformanceRecord],
        loss_events: list[LossEvent],
        manifest_path: Path,
    ) -> LossManifest:
        """
        Computes loss statistics and writes the manifest to manifest_path.
        Returns LossManifest for the caller to include in ExportResult.
        """
```

`LossEvent` fields: `record_id` (or None for structural losses), `field_name`, `reason`, `category`.
`LossManifest` fields: `total_records`, `exported_records`, `lost_records`, `loss_events`, `loss_categories`, `generated_at`.

---

## Dependencies

- `json` stdlib (manifest serialisation)
- No external libraries required

---

## Key Behaviors

1. **Record count comparison** — computes `lost_records = len(source_records) - len(exported_records)`. A positive value means records were excluded from the export.

2. **Loss event categorisation** — groups `LossEvent` objects by `category` (e.g., `"multi_objective"`, `"conditional_space"`, `"unmapped_problem"`) and includes category counts in the manifest.

3. **Manifest serialisation** — writes the `LossManifest` as a JSON file with `indent=2`. The manifest is human-readable and machine-parseable.

4. **Zero-loss case** — if `lost_records == 0` and `len(loss_events) == 0`, writes a manifest with `"loss_free": true`. This is the expected case for well-mapped experiments.

5. **Mandatory manifest** — every export produces a manifest file, even for zero-loss exports. The manifest is an explicit record that the audit was performed and found no loss — it is not omitted on success.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/ecosystem_bridge/loss_auditor.py`

---

## SRS Traceability

- FR-B-04 (information-loss manifest): every export must produce a manifest.
- MANIFESTO Principle 3 (no silent omissions): the loss manifest is the enforcement mechanism for ecosystem exports.
