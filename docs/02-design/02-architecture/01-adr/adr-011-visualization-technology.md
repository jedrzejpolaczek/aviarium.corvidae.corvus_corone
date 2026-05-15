# ADR-011: Visualization Technology Choices (matplotlib, plotly, manim)

<!--
STORY ROLE: Records the technology selection for the Algorithm Visualization Engine
and the Reporting Engine's visualization components. Prevents silent technology
accumulation — every rendering library must have a stated purpose and scope.

CONNECTS TO:
  → docs/02-design/02-architecture/03-c4-leve2-containers/01-index.md : Algorithm Visualization Engine container
  → docs/02-design/01-software-requirement-specification/02-use-cases/08-uc-07.md : UC-07 (Algorithm Visualisation — VIZ-L1-01..04)
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md §2 : VIZ-L1-01..04 mandatory visualizations
  → docs/02-design/02-architecture/01-adr/adr-006-python-version-and-platform-constraints.md : platform constraints consulted here
-->

---

**Status:** Accepted

**Date:** 2026-03-25

**Deciders:** Core maintainers, library design lead

---

## Context

Two containers need rendering capabilities:

1. **Reporting Engine** — produces the four mandatory Level 1 visualizations (VIZ-L1-01..04)
   embedded in HTML researcher/practitioner reports. These are static comparison charts:
   box plots, convergence curves, ECDF, violin plots.

2. **Algorithm Visualization Engine** — produces algorithm-understanding visualizations for
   the Learner (UC-07..UC-11): search trajectories, parameter sensitivity heatmaps, algorithm
   genealogy timelines, and optionally animated convergence sequences.

Three candidates were evaluated: `matplotlib`, `plotly`, and `manim`.

**Evaluation dimensions:**
1. Suitability for the output type (static charts, interactive HTML, educational animations)
2. Installation complexity on supported platforms (ADR-006: Python 3.10–3.12, Linux/macOS/Windows)
3. Dependency weight (transitive dependencies, binary size)
4. Scientific Python ecosystem integration
5. Existing use within the codebase (Reporting Engine already uses matplotlib)

---

## Candidates

### matplotlib

The de-facto standard for scientific Python visualization. Produces raster (PNG) and vector
(SVG, PDF) output. Used directly by the Reporting Engine for VIZ-L1-01..04. Already an
indirect dependency via pandas in the scientific Python stack.

**Strengths:**
- Pure Python with optional C extensions; installs via `pip install matplotlib` on all
  supported platforms without system-level dependencies
- Full control over rendering pipeline; suitable for reproducible, publication-quality figures
- `FuncAnimation` supports animated GIFs for simple convergence sequences without requiring
  a separate rendering backend
- Used by the Reporting Engine already; consolidating on one library avoids dual-rendering paths

**Limitations:**
- Interactive output (zoom, hover, live filter) requires Matplotlib's Qt/Tk backends, which
  require a display server; not suitable for headless server environments without modification
- Not designed for web-embedded interactivity (tooltips, linked brushing)

---

### plotly

A web-first interactive visualization library producing HTML/JS output. Renders in browser
without a display server.

**Strengths:**
- Native HTML embedding — interactive charts (hover, zoom, filter) work as static files
- Suitable for the Learner interface when interactive exploration is needed
- No display server required for rendering; outputs a self-contained HTML fragment

**Limitations:**
- `kaleido` (the static image export backend) adds a Chromium-based binary dependency
  (~100 MB); its installation is unreliable on HPC systems and some CI environments
- For non-interactive output (the Report's embedded SVG charts), plotly produces larger files
  than matplotlib SVG and requires `kaleido` for PNG/PDF export
- Adds a significant transitive dependency (`dash` optional, but `plotly` itself is ~18 MB)

---

### manim

A mathematical animation engine designed for educational mathematics videos. Used by the
3Blue1Brown YouTube channel. Produces MP4 and GIF animations.

**Strengths:**
- Professional-quality mathematical animations (LaTeX rendering, smooth object transforms)
- Purpose-built for educational explanations of algorithms with step-by-step geometric motion
- Ideal long-term fit for UC-07 animated convergence demonstrations

**Limitations:**
- Requires LaTeX, Cairo, FFmpeg, and Pango as system-level dependencies — unreliable or
  absent on many research computing environments and CI systems (ADR-006 Windows support)
- `pip install manim` alone is insufficient; installation failure rate is high without a
  pre-built environment (Docker or conda)
- Not appropriate as a core dependency; must be optional or deferred to V2

---

## Decision

### Primary rendering library: `matplotlib` (core dependency)

**Scope:** All visualizations in both the Reporting Engine and the Algorithm Visualization
Engine that produce static output (PNG, SVG):

- VIZ-L1-01: box plot (QUALITY-BEST_VALUE_AT_BUDGET across algorithms)
- VIZ-L1-02: convergence curves (LOCF best-so-far, all runs)
- VIZ-L1-03: ECDF (plt.step where='post')
- VIZ-L1-04: violin plot (conditional on n > 50 or > 6 algorithms)
- UC-07: search trajectory scatter, parameter sensitivity heatmap, algorithm genealogy timeline
- UC-07: convergence animation (via `FuncAnimation` producing animated GIF)

`matplotlib >= 3.7` is added as a core dependency. It is already present as an indirect
dependency via pandas on most research platforms (ADR-006).

### Secondary rendering library: `plotly` (optional, for interactive outputs)

**Scope:** Interactive HTML outputs for the Learner interface when embedded in a browser
environment — specifically the interactive parameter sensitivity heatmap and search trajectory
explorer in UC-07. `plotly` is declared as an **optional dependency** group
(`pip install corvus_corone[interactive]`).

The static (`kaleido`) PNG export path is explicitly **not** used; `plotly` is used
exclusively for HTML output in this codebase. This avoids the `kaleido` binary dependency.

`plotly >= 5.18` is added as an optional dependency.

### manim: **deferred to V2**

**Rationale:** The V1 learning interface is served by matplotlib's `FuncAnimation` (animated
GIFs). manim's system dependency requirements (LaTeX, FFmpeg, Cairo) are incompatible with a
`pip`-only installation contract (ADR-006: must install on clean Python 3.10+ environment
without system package management). Deferred to V2 when the system may adopt a
containerised deployment that can provide these dependencies.

**Trigger for reconsideration:** If user research shows that GIF animations are insufficient
for UC-07 educational goals, and if a containerised deployment path is available.

---

## Container-level technology assignments

| Container | Library | Output format | Scope |
|---|---|---|---|
| Reporting Engine | `matplotlib` | PNG (inline base64), SVG | VIZ-L1-01..04 embedded in HTML report |
| Algorithm Visualization Engine | `matplotlib` | PNG, SVG, animated GIF | Static Learner visualizations (UC-07..UC-11) |
| Algorithm Visualization Engine | `plotly` (optional) | HTML fragment | Interactive Learner visualizations when `[interactive]` is installed |

---

## Rationale

### Why matplotlib over plotly for the mandatory visualizations

The four VIZ-L1 visualizations (§2 of statistical-methodology.md) are defined to be
reproducible, publication-quality outputs. Their visual appearance must be stable and
deterministic across library versions. matplotlib provides pixel-level control over
rendering and is already used by the Reporting Engine; there is no reason to introduce a
second dependency for the same output type.

plotly's default styling is web-optimised and changes across minor versions; this is
unacceptable for reproducibility claims in researcher reports.

### Why plotly for interactive outputs rather than matplotlib backends

matplotlib's interactive backends (Qt5Agg, TkAgg) require a running display server.
The library must work in headless server environments (CI, HPC, Docker). plotly's HTML
output is display-server-free. For the specific interactive use case (Learner exploring
a parameter sensitivity surface in a browser), plotly is the right tool.

Critically, `kaleido` is explicitly excluded. plotly is used only when the consumer is
a browser; never for server-side PNG/PDF rendering.

### Why manim is deferred and not simply excluded

manim is architecturally correct for long-form educational animations of algorithm
mechanics. Excluding it permanently would commit to a lower quality ceiling for UC-07.
Deferring records the intent without making an installation-breaking promise.

---

## Alternatives Considered

### Bokeh instead of plotly for interactive outputs

**Why not chosen:** Bokeh requires a separate JavaScript bundle delivery mechanism (CDN or
self-hosted) to work in offline HTML reports. plotly bundles its JS in the output HTML by
default, making the interactive charts fully self-contained. This self-containment is
required for offline use on HPC systems without internet access.

---

### Seaborn as the primary library

**Why not chosen:** Seaborn is a high-level wrapper around matplotlib. For the mandatory
VIZ-L1 visualizations, the exact rendering (axis labels, colour scales, legend placement)
is specified normatively in statistical-methodology.md §2. Using the low-level matplotlib
API directly provides the control needed to match the specification; seaborn would add a
layer of abstraction without benefit.

---

## Consequences

**Positive:**

- Single core rendering dependency (`matplotlib`) for all mandatory outputs
- Interactive optional (`plotly`) only when explicitly installed
- No system-level dependencies in V1
- Reporting Engine and Visualization Engine share the same library; same patterns, shared utilities

**Negative / Trade-offs:**

- Two-tier installation (`base` vs `[interactive]`) creates a documentation obligation
- Animated educational content limited to GIF quality in V1

**Risks:**

- **Risk:** Users install base package and find interactive UC-07 visualizations absent.
  **Mitigation:** `visualize_interactive()` raises `ImportError` with a clear install instruction
  if `plotly` is not present (`pip install corvus_corone[interactive]`).

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/02-design/02-architecture/03-c4-leve2-containers/01-index.md` | Algorithm Visualization Engine container specification |
| `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md §2` | VIZ-L1-01..04 visualization specifications that mandate matplotlib |
| `docs/02-design/01-software-requirement-specification/02-use-cases/08-uc-07.md` | UC-07 Learner visualization use case |
| `ADR-006-python-version-and-platform-constraints.md` | Platform constraints that exclude manim in V1 |
