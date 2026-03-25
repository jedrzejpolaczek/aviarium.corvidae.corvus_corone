# Tutorial: Visualize an HPO Algorithm

---

## Audience

**Actor:** Learner

**Prior knowledge assumed:**
- Domain: knows what hyperparameter optimization is; knows the name of at least one algorithm
  (TPE, CMA-ES, random search) but does not yet have a geometric or intuitive picture of how
  it operates
- Technical: comfortable running Python commands; basic familiarity with `import` statements
- System: `corvus_corone` installed: `pip install corvus_corone`

No prior tutorials are required. If you want to first run a study yourself to generate the
data used in the data-driven visualizations, complete
[`02-researcher-design-and-execute-study.md`](02-researcher-design-and-execute-study.md)
first. This tutorial shows the fallback path when no study data is available, and also the
data-driven path when it is.

---

## Learning Objective

After completing this tutorial, the Learner will be able to generate four types of algorithm
visualization — convergence animation, search trajectory, parameter sensitivity heatmap, and
Pareto front — and connect each visual directly to the mathematical property of the algorithm
it represents.

---

## Prerequisites

- `corvus_corone` installed: `pip install corvus_corone`
- For interactive visualizations: `pip install corvus_corone[interactive]`
- CMA-ES default instance is pre-registered with the package; no manual registration needed
- Optional: a completed Study experiment ID from
  [`02-researcher-design-and-execute-study.md`](02-researcher-design-and-execute-study.md)

---

## Overview

An HPO algorithm is an abstract procedure. Reading pseudocode is one way to understand it.
Watching it search is another — and often more durable. This tutorial generates four visuals
for CMA-ES, each answering a different question about how the algorithm behaves:

1. **Convergence animation** — does the algorithm improve over time? how fast?
2. **Search trajectory** — where in the search space did it look? did it explore or exploit?
3. **Parameter sensitivity heatmap** — which algorithm hyperparameters matter most? (analogous
   to SHAP feature importance for ML models)
4. **Pareto front** (multi-objective problems) — when the algorithm faces competing objectives,
   what tradeoffs did it find?

Each visual is linked to its mathematical concept so you always know what you are looking at.
This tutorial demonstrates UC-07 (Algorithm Visualisation) and uses the Algorithm Visualization
Engine container
(→ [`../02-design/02-architecture/03-c4-leve2-containers/06-algorithm-visualization-engine.md`](../02-design/02-architecture/03-c4-leve2-containers/06-algorithm-visualization-engine.md)).

---

## Steps

### Step 1: List available algorithms

```python
import corvus_corone as cc

algorithms = cc.list_algorithms()
for alg in algorithms:
    print(alg.id, "—", alg.name)
```

Expected output (trimmed):

```
cma-es-default — CMA-ES (default configuration)
tpe-default    — Tree-structured Parzen Estimator (default)
random-search  — Random Search (baseline)
```

**Why this step matters:** Visualizations are tied to a registered Algorithm Instance.
`list_algorithms()` confirms which instances are available and shows their IDs.

**Expected result:** A list of registered algorithm IDs. CMA-ES and TPE are included in
the default package installation.

---

### Step 2: Inspect the mathematical specification

```python
alg = cc.get_algorithm("cma-es-default")
print(alg.name)
print(alg.algorithm_family)
print(alg.known_assumptions)
```

Expected output:

```
CMA-ES (default configuration)
CMA-ES
['continuous search space', 'unimodal or mildly multimodal', 'no categorical variables']
```

**Why this step matters:** The mathematical specification — `algorithm_family`, `hyperparameters`,
and `known_assumptions` — is what the visualizations are grounded in. Each subsequent visual
will label itself against these properties. Knowing the assumptions before generating the visuals
helps you know what the visualization is and is not designed to show.

**Expected result:** You can see the CMA-ES configuration and its declared assumptions.

**Common mistake:** Requesting a visualization for an algorithm that has no registered instance.
If `get_algorithm()` raises `EntityNotFoundError`, check the ID with `list_algorithms()` first.

---

### Step 3: Generate a convergence animation

The convergence animation shows `best_so_far` over time as an animated GIF. It is data-driven:
it requires at least one completed Study that includes CMA-ES.

**With study data:**

```python
# Replace with your experiment ID from a completed Study
result = cc.visualize(
    algorithm_id="cma-es-default",
    viz_type="convergence",
    experiment_id="<your-experiment-id>",
    format="gif",
    output_path="cmaes_convergence.gif",
)
print("Saved to:", result.output_path)
```

**Without study data (mathematical-only fallback):**

```python
result = cc.visualize(
    algorithm_id="cma-es-default",
    viz_type="convergence",
    format="gif",
    output_path="cmaes_convergence.gif",
)
# Output: a schematic animation of the CMA-ES sampling distribution adapting,
# with no empirical Run data — uses illustrative synthetic values.
print(result.fallback_reason)  # "No completed study data found for this algorithm"
```

**What you are looking at:** The animation shows the sampling distribution (represented as an
ellipse) shrinking and rotating as CMA-ES adapts its covariance matrix. The width and
orientation of the ellipse *is* the covariance matrix — a wide flat ellipse means the algorithm
has learned that one dimension varies more than another.

→ Mathematical concept: covariance matrix adaptation; see GLOSSARY "Algorithm Visualization".

**Expected result:** `cmaes_convergence.gif` in your working directory. Open it in any browser.

---

### Step 4: Generate a search trajectory scatter

```python
result = cc.visualize(
    algorithm_id="cma-es-default",
    viz_type="trajectory",
    experiment_id="<your-experiment-id>",  # or omit for synthetic
    format="png",
    output_path="cmaes_trajectory.png",
)
```

**What you are looking at:** Each point is one candidate solution sampled by CMA-ES during
a Run. The color axis encodes evaluation number: early samples are blue, late samples are
red. You should see the distribution shift and tighten around the best region found.

Compare this to a random search trajectory (try `algorithm_id="random-search"`): random
search shows a uniform scatter with no color gradient toward any region. CMA-ES shows
increasing density near the best point — that density *is* the exploitation behavior.

**Expected result:** `cmaes_trajectory.png` — a 2D scatter with colored points showing
the exploration-to-exploitation transition.

---

### Step 5: Generate a parameter sensitivity heatmap

The parameter sensitivity heatmap answers: **which CMA-ES hyperparameters matter most?**
This is the same question SHAP answers for ML model features: not "what value did this
parameter have?" but "how much does changing it change the outcome?".

```python
result = cc.visualize(
    algorithm_id="cma-es-default",
    viz_type="sensitivity",
    experiment_id="<your-experiment-id>",
    format="png",
    output_path="cmaes_sensitivity.png",
)
```

**What you are looking at:** A heatmap where rows are algorithm hyperparameters
(e.g., `sigma0`, `popsize`, `tolX`) and columns are Problem Instance characteristics
(e.g., dimension, noise level). Cell color encodes the sensitivity score: how much
`QUALITY-BEST_VALUE_AT_BUDGET` changes when the hyperparameter varies across its declared
range, holding other parameters constant.

**SHAP analogy:** In a trained ML model, SHAP tells you how much each input feature moves
the prediction. Here, the heatmap tells you how much each algorithm hyperparameter moves the
final benchmark performance. High sensitivity (bright cell) = this parameter matters on this
problem type. Low sensitivity = safe to leave at default.

**For interactive exploration** (requires `pip install corvus_corone[interactive]`):

```python
result = cc.visualize(
    algorithm_id="cma-es-default",
    viz_type="sensitivity",
    experiment_id="<your-experiment-id>",
    format="html",
    output_path="cmaes_sensitivity.html",
)
```

Open `cmaes_sensitivity.html` in a browser — you can hover over each cell to see the exact
sensitivity score and the problem instance it corresponds to.

**Expected result:** `cmaes_sensitivity.png` (or `.html` for interactive) showing the
hyperparameter sensitivity grid.

**Checkpoint:** At this point you have three visualizations. You should be able to answer:
1. Does CMA-ES converge? (convergence animation — yes, the ellipse shrinks)
2. Where does CMA-ES search? (trajectory — shifts toward the best region)
3. Does `sigma0` matter? (sensitivity heatmap — check the brightness of its row)

---

### Step 6: Generate a Pareto front visualization

On multi-objective problems, the goal is not a single best point but a *set* of points that
represent tradeoffs between competing objectives. The Pareto front shows the boundary of
non-dominated solutions — solutions where you cannot improve one objective without worsening
another.

```python
# This requires an experiment on a multi-objective problem instance
result = cc.visualize(
    algorithm_id="cma-es-default",
    viz_type="pareto_front",
    experiment_id="<multi-objective-experiment-id>",
    format="png",
    output_path="cmaes_pareto.png",
)
```

**What you are looking at:** Each point on the Pareto front is a solution where no other
solution in the Run is strictly better on all objectives simultaneously. The shape of the
front reveals the nature of the tradeoff: a convex front means the tradeoff is smooth and
continuous; a broken front means there are discrete jumps where you must sacrifice a lot of
one objective to gain a little of another.

**Note:** If your experiment used a single-objective problem instance, this visualization
will raise `VisualizationNotApplicableError` with a message explaining that a
multi-objective experiment ID is required. That is expected behavior — it is not an error in
your setup.

**Expected result:** `cmaes_pareto.png` — a 2D scatter of the Pareto front for the
multi-objective Run, or a clear `VisualizationNotApplicableError` message if not applicable.

---

### Step 7: Generate all visualizations at once

```python
results = cc.visualize(
    algorithm_id="cma-es-default",
    viz_type="all",
    experiment_id="<your-experiment-id>",
    format="png",
    output_dir="cmaes_visuals/",
)
for r in results:
    print(r.viz_type, "→", r.output_path)
```

Expected output:

```
convergence → cmaes_visuals/cmaes-default_convergence.gif
trajectory  → cmaes_visuals/cmaes-default_trajectory.png
sensitivity → cmaes_visuals/cmaes-default_sensitivity.png
genealogy   → cmaes_visuals/cmaes-default_genealogy.svg
```

**Expected result:** Four files in `cmaes_visuals/` — one per visualization type. The
genealogy SVG is generated from metadata alone (no study data required).

---

## Expected Outcome

After this tutorial you have four visualization files for CMA-ES:
- `cmaes_convergence.gif` — animated convergence curve
- `cmaes_trajectory.png` — search trajectory scatter
- `cmaes_sensitivity.png` — hyperparameter sensitivity heatmap
- `cmaes_visuals/cmaes-default_genealogy.svg` — lineage overview

**Verifiable criterion:** Run `cc.visualize(algorithm_id="cma-es-default", viz_type="all",
output_dir="test_out/")`. All four output files are created without error. If any file is
missing, the function raises an exception with the specific `viz_type` that failed.

---

## What You Learned

- **Visualization requires a registered instance** — `cc.visualize()` resolves the algorithm
  from the registry; the registry provides metadata (family, hyperparameters, assumptions)
  that labels each visual.
  → Architecture: `06-algorithm-visualization-engine.md`

- **Data-driven vs. metadata-only** — convergence, trajectory, and sensitivity require a
  completed Study (`experiment_id`). Genealogy is always available from registry metadata
  alone. Missing data triggers a labeled fallback, never a silent error.
  → UC-07 Failure Scenario F1

- **Sensitivity heatmap = SHAP for algorithm hyperparameters** — it shows which parameters
  matter most across problem characteristics, making hyperparameter design choices legible
  without re-running benchmarks.

- **Pareto front applies only to multi-objective problems** — single-objective experiments
  produce a `VisualizationNotApplicableError`, which is the system enforcing scope
  boundaries (MANIFESTO Principle 3).

- **Interactive output requires the `[interactive]` extra** — `format="html"` uses plotly
  and raises `ImportError` if `plotly` is not installed, with a clear install instruction.
  → ADR-011 (visualization technology choices)

---

## Further Reading

- **Understand where CMA-ES came from:** [`07-learner-algorithm-genealogy.md`](07-learner-algorithm-genealogy.md) — Algorithm Genealogy Explorer tutorial (UC-10)
- **Ask the algorithm a question:** [`09-uc-08.md`](../02-design/01-software-requirement-specification/02-use-cases/09-uc-08.md) — UC-08: Contextual Algorithm Help
- **Reason through the covariance matrix yourself:** [`05-learner-socratic-mode.md`](05-learner-socratic-mode.md) — Socratic Mode tutorial (UC-09)
- **Explore study results as a Learner:** [`12-uc-11.md`](../02-design/01-software-requirement-specification/02-use-cases/12-uc-11.md) — UC-11: Learner Explores Study Results
- **Algorithm Visualization Engine architecture:** [`../02-design/02-architecture/03-c4-leve2-containers/06-algorithm-visualization-engine.md`](../02-design/02-architecture/03-c4-leve2-containers/06-algorithm-visualization-engine.md)
- **ADR-011** — why matplotlib is core and plotly is optional: [`../02-design/02-architecture/01-adr/adr-011-visualization-technology.md`](../02-design/02-architecture/01-adr/adr-011-visualization-technology.md)
