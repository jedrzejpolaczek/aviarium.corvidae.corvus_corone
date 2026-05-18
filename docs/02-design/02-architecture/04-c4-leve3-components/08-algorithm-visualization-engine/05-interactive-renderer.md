# Interactive Renderer

> Container: [Algorithm Visualization Engine](../../03-c4-leve2-containers/06-algorithm-visualization-engine.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Render interactive HTML visualizations (sensitivity heatmap with hover tooltips, trajectory scatter with zoom/pan) using plotly, which is an optional dependency available via `pip install corvus_corone[interactive]`.

---

## Interface

```python
class InteractiveRenderer:
    def render(
        self,
        viz_type: Literal["sensitivity", "trajectory", "pareto_front"],
        viz_data: VisualizationData,
        output_path: Path,
    ) -> VisualizationResult:
        """
        Renders an interactive HTML visualization.
        Raises ImportError if plotly is not installed, with pip install instruction.
        """
```

---

## Dependencies

- `plotly` (optional) — raises `ImportError` at call time if not installed; does not raise at import time
- `pathlib.Path` stdlib

---

## Key Behaviors

1. **Import guard** — checks for plotly availability at the start of `render()`. If not installed, raises `ImportError` with the message: `"Interactive visualizations require plotly. Install with: pip install corvus_corone[interactive]"`. Does not raise at module import time (lazy check).

2. **Interactive sensitivity heatmap** — renders the sensitivity grid as a `plotly.graph_objects.Heatmap`. Each cell has a hover tooltip showing: hyperparameter name, problem characteristic, sensitivity score, and interpretation (e.g., "High sensitivity: tune carefully on this problem type").

3. **Interactive trajectory scatter** — renders candidate solutions as a `plotly.graph_objects.Scatter` with color encoding for evaluation number. Supports zoom, pan, and hover (shows candidate coordinates and objective value).

4. **Interactive Pareto front** — renders multi-objective results as a `plotly.graph_objects.Scatter` with hover showing all objective values. Only available when `viz_data.study_data` contains multi-objective results.

5. **Self-contained HTML** — uses `plotly.io.write_html(fig, include_plotlyjs="cdn")` by default, or `include_plotlyjs=True` (inline) if `offline_mode=True` is set in the `VisualizationConfig`. The default (CDN) produces a smaller file; inline produces a self-contained file.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/algorithm_visualization_engine/interactive_renderer.py`

---

## SRS Traceability

- UC-07 step 5 (interactive sensitivity heatmap): interactive HTML output.
- ADR-011: plotly is the optional interactive rendering library; core output must not require it.
