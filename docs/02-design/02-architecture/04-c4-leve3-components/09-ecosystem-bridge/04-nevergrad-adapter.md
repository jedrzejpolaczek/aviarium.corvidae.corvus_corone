# Nevergrad Adapter

> Container: [Ecosystem Bridge](../../03-c4-leve2-containers/13-ecosystem-bridge.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Provide a bidirectional bridge between Corvus and Nevergrad: wrap Nevergrad optimizers for use within Corvus evaluation loops (Corvus-as-harness), and export Corvus Study results to Nevergrad's experiment format (Corvus-as-exporter).

---

## Interface

```python
class NevergradAdapter:
    # Direction 1: Wrap a Nevergrad optimizer as a Corvus AlgorithmInstance
    def wrap_optimizer(
        self,
        ng_optimizer_class: type,
        hyperparameters: dict,
        algorithm_id: str,
    ) -> AlgorithmInstance:
        """Returns an AlgorithmInstance with ask()/tell() backed by Nevergrad."""

    # Direction 2: Export Corvus results to Nevergrad format
    def export(
        self,
        experiment_id: str,
        output_dir: Path,
        record_reader: PerformanceRecordReader,
        loss_auditor: LossAuditor,
    ) -> ExportResult:
        """Exports experiment to Nevergrad benchmark JSON format."""
```

---

## Dependencies

- `nevergrad` Python package — `ng.optimizers`, `ng.p` parameter space
- **Results Store — Performance Record Reader** (export direction)
- **Loss Auditor** (export direction)

---

## Key Behaviors

1. **Optimizer wrapping** — creates a thin `AlgorithmInstance` subclass that delegates `ask()` to `ng_optimizer.ask()` and `tell()` to `ng_optimizer.tell()`. The Nevergrad parameter space is translated to the Corvus search space schema at construction time.

2. **Parameter space translation** — maps Corvus `SearchSpace` (continuous, integer, categorical, conditional) to Nevergrad `ng.p.Instrumentation`. Conditional spaces are translated to `ng.p.Choice` where possible; unsupported conditionals are added to the loss manifest.

3. **Nevergrad result export** — converts PerformanceRecords to Nevergrad's `Experiment` and `Result` JSON schema. Maps `algorithm_id` to Nevergrad optimizer name; `problem_id` to Nevergrad function name.

4. **Bidirectional loss accounting** — in the wrap direction, records what Corvus features are unavailable in Nevergrad (e.g., no native multi-objective ask/tell in some optimizers). In the export direction, records what Corvus data fields are lost (e.g., per-candidate metadata not in Nevergrad JSON).

5. **Version compatibility** — checks Nevergrad version at import time. If the installed version is incompatible (< minimum required), raises `ImportError` with the minimum version number.

---

## State

The `AlgorithmInstance` wrapper holds a live Nevergrad optimizer object during a Run. Disposed after the Run subprocess exits.

---

## Implementation Reference

`corvus_corone/ecosystem_bridge/nevergrad_adapter.py`

---

## SRS Traceability

- FR-B-03 (Nevergrad integration): bidirectional Nevergrad bridge.
