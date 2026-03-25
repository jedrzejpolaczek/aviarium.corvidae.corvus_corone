# Container: Algorithm Visualization Engine

> Index: [01-index.md](01-index.md)

**Responsibility:** Generate algorithm-understanding visualizations for the Learner actor
(UC-07..UC-11) — static and animated representations of how HPO algorithms work mechanically,
including search trajectories, parameter sensitivity heatmaps, convergence animations, and
algorithm genealogy timelines. Distinct from the Reporting Engine: the Reporting Engine
produces comparative study outputs (which algorithm performed better); this container produces
explanatory outputs (how a specific algorithm searches).

**Technology:** Python · `matplotlib >= 3.7` (static PNG/SVG, animated GIF via `FuncAnimation`)
· `plotly >= 5.18` (interactive HTML; optional dependency — `pip install corvus_corone[interactive]`).
See [ADR-011](../01-adr/adr-011-visualization-technology.md) for the full technology selection
rationale and the decision to defer `manim` to V2.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Static visualizations | PNG / SVG files; base64-embeddable in HTML | Learner (via Public API `cc.visualize()`), Researcher (enriched reports) |
| Animated convergence | Animated GIF (`FuncAnimation`) | Learner (UC-07 convergence animation) |
| Interactive visualizations | Self-contained HTML fragment (`plotly`; optional) | Learner (browser-based parameter sensitivity explorer, search trajectory explorer) |
| Genealogy timeline | SVG node-link diagram | Learner (UC-10 algorithm history) |

All surfaces are exposed through the Public API + CLI container. The Visualization Engine
does not expose a network interface; it is a library component invoked in-process.

**Dependencies:**

| Dependency | Data consumed | Reason |
|---|---|---|
| Algorithm Registry | Algorithm metadata: `algorithm_family`, `hyperparameters`, `known_assumptions` | Required to label visualizations with algorithm identity and parameter names |
| Results Store | `PerformanceRecord[]` for a selected Run or Experiment | Required for data-driven visualizations (convergence, trajectory); absent data triggers static-only fallback (UC-07 F1) |
| Results Store | `ResultAggregate` (parameter sensitivity data) | Required for heatmap visualizations |

**Data owned:** None. Visualization artifacts (PNG, SVG, GIF, HTML) are ephemeral outputs
returned to the caller; they are not stored in the Results Store. If persistence is needed,
the caller (Public API) writes the artifacts to disk.

**Relationship to Researcher data flow:**

The Visualization Engine is a **read-only consumer** of data produced by the Researcher
actor's workflow. The data flow mirrors the Learner–Researcher relationship defined in C1:

```
Researcher → [Study → Experiment → PerformanceRecords / ResultAggregates]
                                            ↓
                          Algorithm Visualization Engine (read-only)
                                            ↓
                                   Learner (artifact consumer)
```

The Engine never modifies, re-runs, or annotates any entity in the Results Store.

**Actors served:**

- **Learner** (primary) — all UC-07..UC-11 visualization requests
- **Researcher** (secondary) — when `cc.generate_reports()` is called with
  `include_algorithm_viz=True`, the Reporting Engine delegates algorithm-understanding
  inserts to this container (e.g., search trajectory panel embedded in the report)

**Relevant SRS section:** UC-07 (Algorithm Visualisation), UC-08 (Contextual Algorithm Help),
UC-09 (Socratic Guided Deduction — visual context for bridging questions), UC-10 (Algorithm
History — genealogy timeline), UC-11 (Learner Explores Study Results — visualization pivot).
Learner-actor functional requirements to be added in a future task.
