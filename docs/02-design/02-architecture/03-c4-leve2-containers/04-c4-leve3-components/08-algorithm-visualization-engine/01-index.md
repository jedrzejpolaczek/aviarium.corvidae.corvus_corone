<!-- check-docs: allow-undefined -->
<!-- This container is outside the V1 release (SRS §1.4). Its contracts are written when
     the Learner actor enters scope, so the ADR-012 vocabulary check cannot resolve its
     names against 03-technical-contracts/ yet. -->

# C3: Components — Algorithm Visualization Engine

> C2 Container: [06-algorithm-visualization-engine.md](../../06-algorithm-visualization-engine.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

**V1 scope: Deferred.** This container serves the Learner: it draws how an algorithm *searches*,
not how much *progress* algorithms made. Search trajectories, parameter-sensitivity surfaces,
convergence animations and genealogy timelines all live here, and ADR-018 moved them out of the
Reporting Engine precisely because they answer a different question.

It is outside V1 (SRS §1.4) and its contracts are written when the Learner actor enters scope,
which is why this page carries the `allow-undefined` marker.

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| Data Resolver | Finds the algorithm metadata and, where it exists, the study data a visualization needs | *(contract not yet written)* |
| Static Renderer | Trajectory scatter, sensitivity heatmap, genealogy timeline (FR-34, FR-37) | ADR-011 |
| Animation Renderer | Convergence animation as an animated GIF | ADR-011 |
| Interactive Renderer | Browser-side interactive views, behind an optional dependency | ADR-011 |

---

## Where the vocabulary comes from

Only ADR-011, which fixes the rendering libraries and defers `manim` to V2. The data this
container reads is contracted — Performance Records and the entity schemas — but what it produces
is not, and will need its own contract before FR-34 through FR-38 can be implemented.

