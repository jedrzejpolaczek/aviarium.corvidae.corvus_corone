# Mandatory Viz Renderer

> Container: [Reporting Engine](../../03-c4-leve2-containers/05-reporting-engine.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Generate the set of visualizations that must appear in every benchmark report, delegating rendering to the Algorithm Visualization Engine and collecting the output paths for the HTML Template Renderer.

---

## Interface

```python
class MandatoryVizRenderer:
    def render_all(
        self,
        report_data: ReportData,
        viz_engine: AlgorithmVisualizationEngine,
        output_dir: Path,
    ) -> dict[str, Path]:
        """
        Generates all mandatory visualizations.
        Returns {viz_type: output_path} for each visualization.
        Raises MandatoryVizError if any required visualization fails.
        """
```

Mandatory visualization set (always required):
- `convergence` (per algorithm, GIF or PNG)
- `trajectory` (per algorithm, PNG)
- `sensitivity` (per algorithm, PNG)

Optional visualizations (generated if `include_algorithm_viz=True` and data available):
- `pareto_front` (only for multi-objective studies)
- `genealogy` (always available from registry metadata)

---

## Dependencies

- **Algorithm Visualization Engine** — all rendering is delegated here; the Mandatory Viz Renderer does not call matplotlib directly
- `pathlib.Path` stdlib

---

## Key Behaviors

1. **Mandatory set enforcement** — generates `convergence`, `trajectory`, and `sensitivity` for every algorithm in the Study. These are non-negotiable; failure to generate any of them raises `MandatoryVizError`.

2. **Per-algorithm generation** — for each algorithm in the report, calls `viz_engine.visualize(algorithm_id, viz_type, experiment_id, output_dir)` for each mandatory type.

3. **Optional visualization handling** — generates optional visualizations only if the configuration and data permit. Missing optional visualizations are noted in the report metadata but do not raise errors.

4. **Output path collection** — returns a `dict[str, Path]` mapping `"{algorithm_id}_{viz_type}"` to the output file path. This dict is passed to the HTML Template Renderer for embedding.

5. **Fallback labeling** — if the Visualization Engine uses a mathematical-only fallback (no study data), the Mandatory Viz Renderer notes this in the returned metadata dict so the HTML renderer can label the visualization accordingly.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/reporting_engine/mandatory_viz_renderer.py`

---

## SRS Traceability

- FR-P-02 (mandatory visualizations): convergence, trajectory, and sensitivity must appear in every report.
- UC-06 step 3 (generate visualizations): visualization generation is triggered here.
