# Animation Renderer

> Container: [Algorithm Visualization Engine](../../03-c4-leve2-containers/06-algorithm-visualization-engine.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Render the convergence animation as an animated GIF showing the algorithm's sampling distribution adapting over time, using `matplotlib.animation`.

---

## Interface

```python
class AnimationRenderer:
    def render(
        self,
        viz_data: VisualizationData,
        output_path: Path,
        fps: int = 10,
        dpi: int = 100,
    ) -> VisualizationResult:
        """
        Renders the convergence animation as a GIF.
        Uses fallback synthetic data if viz_data.fallback_used.
        """
```

---

## Dependencies

- `matplotlib` (core)
- `matplotlib.animation.FuncAnimation`
- `Pillow` (`PIL`) — required by matplotlib for GIF export; bundled as a dependency

---

## Key Behaviors

1. **Convergence curve animation** — animates `best_so_far` over evaluations. Each frame shows the convergence curve up to evaluation `i`, with the current best value annotated. The x-axis is budget fraction (0–1); y-axis is objective value (log scale if range > 3 orders of magnitude).

2. **Sampling distribution overlay** (for CMA-ES) — if the algorithm family is `CMA-ES` and sampling distribution data is available, overlays the sampling ellipse at each frame. The ellipse is derived from the covariance matrix recorded in the PerformanceRecord `extra_data` field.

3. **Mathematical-only fallback** — when `viz_data.fallback_used`, generates a schematic animation using synthetic values derived from the algorithm's declared convergence properties. Labels each frame with "Illustrative — no empirical data."

4. **Frame count** — generates `min(budget, 100)` frames, subsampled evenly from the full evaluation sequence. This keeps GIF file size manageable for large budgets.

5. **GIF export** — uses `matplotlib.animation.PillowWriter` to export the animation as a GIF. DPI is set lower than static renders (100 vs. 150) to reduce file size.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/algorithm_visualization_engine/animation_renderer.py`

---

## SRS Traceability

- UC-07 step 3 (convergence animation): the convergence GIF is generated here.
- FR-V-02 (convergence animation): animated GIF format required.
- ADR-011: matplotlib.animation is the animation rendering approach.
