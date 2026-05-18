# Static Renderer

> Container: [Algorithm Visualization Engine](../../03-c4-leve2-containers/06-algorithm-visualization-engine.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Render static visualizations (search trajectory scatter, parameter sensitivity heatmap, genealogy SVG) from `VisualizationData` using matplotlib, writing the output to a file.

---

## Interface

```python
class StaticRenderer:
    def render(
        self,
        viz_type: Literal["trajectory", "sensitivity", "genealogy"],
        viz_data: VisualizationData,
        format: Literal["png", "svg"],
        output_path: Path,
        dpi: int = 150,
    ) -> VisualizationResult:
        """
        Renders the visualization and writes to output_path.
        Raises VisualizationNotApplicableError for pareto_front on single-objective data.
        """
```

`VisualizationResult` fields: `viz_type`, `output_path`, `format`, `fallback_used`, `fallback_reason`.

---

## Dependencies

- `matplotlib` (core, always available)
- `matplotlib.pyplot`, `matplotlib.cm`, `matplotlib.colors`
- `networkx` — for genealogy graph layout (directed node-link diagram)

---

## Key Behaviors

1. **Trajectory scatter** — plots each candidate solution as a point, colored by evaluation number (blue=early, red=late). Axes are the two most variable dimensions (PCA projection for d>2). Each algorithm gets its own subplot.

2. **Sensitivity heatmap** — plots a grid of algorithm hyperparameters (rows) × problem characteristics (columns). Cell color encodes sensitivity score. Uses `matplotlib.cm.RdYlGn` colormap. Annotates cells with numeric sensitivity scores.

3. **Genealogy SVG** — uses `networkx` to lay out the directed genealogy graph (Sugiyama/hierarchical layout). Nodes are labeled with algorithm name and year; edges are labeled with the limitation addressed. Output is SVG for scalable rendering in browsers and reports.

4. **Pareto front** — raises `VisualizationNotApplicableError` if the `viz_data.study_data` does not contain multi-objective results. The error message explains that a multi-objective experiment ID is required.

5. **Fallback labeling** — if `viz_data.fallback_used`, adds a watermark text to the plot: "Illustrative data — no study results available." in the bottom-right corner of the figure.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/algorithm_visualization_engine/static_renderer.py`

---

## SRS Traceability

- UC-07 steps 3–5 (trajectory, sensitivity, genealogy visualizations).
- FR-V-01 (static visualization output): PNG and SVG formats required.
- ADR-011: matplotlib is the core rendering library for all static output.
