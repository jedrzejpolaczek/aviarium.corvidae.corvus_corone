# Mandatory Viz Renderer

> Container: [Reporting Engine](../../05-reporting-engine.md)
> C3 Index: [01-index.md](01-index.md)

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
        Raises ValidationError if any required visualization fails.
        """
```

Mandatory visualization set (always required):
- `VIZ-L1-01` box plot of final quality (per problem, PNG)
- `VIZ-L1-02` convergence curves (per problem, PNG)
- `VIZ-L1-03` ECDF, drawn with step interpolation (per problem, PNG)

Optional visualizations (generated if `include_algorithm_viz=True` and data available):
- `VIZ-L1-04` violin plot, which replaces `VIZ-L1-01` when a cell contributes more than 50 Runs
- `genealogy` (always available from registry metadata)

---

## Dependencies

- **Algorithm Visualization Engine** — all rendering is delegated here; the Mandatory Viz Renderer does not call matplotlib directly
- `pathlib.Path` stdlib

---

## Key Behaviors

1. **Mandatory set enforcement** — generates VIZ-L1-01, VIZ-L1-02 and VIZ-L1-03 for every problem in the Study, plus VIZ-L1-04 where the Run count requires it. These are non-negotiable; failure to generate any of them raises `ValidationError`. Trajectory and sensitivity plots are Algorithm Visualization Engine output and are outside V1 (ADR-018).

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

- Mandatory visualizations VIZ-L1-01..04 must appear in every Report, as required by
  `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` 2.1 and ADR-018.
- UC-06 step 3 (generate visualizations): visualization generation is triggered here.
