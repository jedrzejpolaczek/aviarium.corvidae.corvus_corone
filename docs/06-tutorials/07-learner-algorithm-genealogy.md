# Tutorial: Explore Algorithm History and Genealogy

---

## Audience

**Actor:** Learner

**Prior knowledge assumed:**
- Domain: knows what hyperparameter optimization is; has used or read about at least one
  algorithm (e.g., Bayesian optimization, TPE, random search) and wants to understand where
  it came from and why it was designed the way it was
- Technical: comfortable running Python commands
- System: `corvus_corone` installed: `pip install corvus_corone`

No prior tutorials are required, though
[`06-learner-algorithm-visualization.md`](06-learner-algorithm-visualization.md)
provides a useful visual companion — the genealogy visualization from that tutorial
gives a structural overview before this tutorial adds historical narrative.

---

## Learning Objective

After completing this tutorial, the Learner will be able to trace the intellectual lineage
of TPE from its earliest ancestor (Multi-Armed Bandit) through Bayesian Optimization to the
present, identify what problem each step in the lineage solved, and navigate to any algorithm
in the lineage to explore its own history.

---

## Prerequisites

- `corvus_corone` installed: `pip install corvus_corone`
- TPE, Bayesian Optimization, and MAB genealogy data are bundled with the package — no
  separate download required

---

## Overview

Every algorithm was invented to solve a problem its predecessor could not. Understanding
this chain of problems and solutions — the genealogy — is often more durable than memorizing
an algorithm's update rule. Once you know *why* CMA-ES adapts a covariance matrix, you
never forget it; if you only memorize the update rule, you will forget it.

This tutorial walks the lineage: **Multi-Armed Bandit → Bayesian Optimization → TPE**,
covering:
- what problem each method solved
- what limitation it still had that motivated the next step
- which design choices distinguish each descendant from its parent

A second path explores the **CMA-ES lineage**: Evolution Strategies → CMA-ES → variants.

This tutorial demonstrates UC-10 (Algorithm History and Evolution) and uses the Algorithm
Genealogy module
(→ IMPL-046; `docs/02-design/01-software-requirement-specification/02-use-cases/11-uc-10.md`).

---

## Steps

### Step 1: List algorithms with genealogy data

```python
import corvus_corone as cc

algorithms = cc.list_algorithms()
for alg in algorithms:
    if alg.has_genealogy:
        print(alg.id, "—", alg.name)
```

Expected output:

```
tpe-default        — Tree-structured Parzen Estimator (default)
cma-es-default     — CMA-ES (default configuration)
random-search      — Random Search (baseline)
bayesopt-gp        — Bayesian Optimization (Gaussian Process)
```

**Why this step matters:** Genealogy data is not automatically available for every registered
Algorithm Instance. `alg.has_genealogy` checks before requesting, preventing the F1 failure
scenario (UC-10 §Failure Scenarios: "system notes that genealogy data is not yet available
and lists algorithms for which it exists").

**Expected result:** A list of algorithms with genealogy data. TPE and CMA-ES are included
in the default package.

---

### Step 2: Request the genealogy record for TPE

```python
genealogy = cc.get_algorithm_genealogy("tpe-default")

print("Algorithm:", genealogy.algorithm_name)
print("Year:", genealogy.year)
print("Authors:", genealogy.authors)
print("Problem solved:", genealogy.problem_solved)
print()
print("Predecessors:")
for pred in genealogy.predecessors:
    print(" •", pred.name, f"({pred.year})")
    print("   Limitation addressed:", pred.limitation_addressed)
```

Expected output:

```
Algorithm: Tree-structured Parzen Estimator (TPE)
Year: 2011
Authors: Bergstra, Bardenet, Bengio, Kégl
Problem solved: Sequential model-based optimization that scales to high-dimensional,
                mixed-type, conditional search spaces — without the O(n³) cost of
                Gaussian Process regression.

Predecessors:
 • Bayesian Optimization with GP (2008)
   Limitation addressed: O(n³) GP regression cost made it impractical for large
   evaluation budgets; also limited to continuous spaces.
 • SMAC (Sequential Model-based Algorithm Configuration) (2011)
   Limitation addressed: Random Forests used as surrogate, but cannot produce
   a closed-form acquisition function — requires expensive Monte Carlo approximation.
```

**What you are reading:** Each predecessor entry describes the limitation that made a
replacement necessary. Reading the limitations in sequence builds the problem-solution
chain that culminates in TPE.

**Expected result:** A printed genealogy record for TPE with predecessor names, years,
and the limitation each addressed.

---

### Step 3: Navigate to the MAB ancestor

Bayesian Optimization itself has predecessors. Follow the chain backward:

```python
# Follow the chain: TPE → Bayesian Optimization → MAB
bayesopt_genealogy = cc.get_algorithm_genealogy("bayesopt-gp")

print("Algorithm:", bayesopt_genealogy.algorithm_name)
print("Year:", bayesopt_genealogy.year)
print("Problem solved:", bayesopt_genealogy.problem_solved)
print()
print("Predecessors:")
for pred in bayesopt_genealogy.predecessors:
    print(" •", pred.name, f"({pred.year})")
    print("   Limitation addressed:", pred.limitation_addressed)
```

Expected output:

```
Algorithm: Bayesian Optimization (Gaussian Process)
Year: 1998 (Mockus 1975 for foundational concept; Jones et al. 1998 for EGO)
Problem solved: Optimize expensive black-box functions with few evaluations using a
                probabilistic surrogate model and principled acquisition function.

Predecessors:
 • Multi-Armed Bandit (MAB) (1933, formalized 1952)
   Limitation addressed: MAB provides a framework for the exploration–exploitation
   tradeoff but assumes each "arm" has a fixed unknown reward — it cannot model how
   rewards correlate across the input space or use structure to guide sampling.
 • Response Surface Methodology (1951)
   Limitation addressed: RSM fits polynomial surfaces to experimental data but
   assumes a low-dimensional, smooth response and gives no uncertainty estimate
   for where to sample next.
```

**Checkpoint:** You have now traced the MAB → Bayesian Optimization → TPE lineage. You
should be able to answer: *What does Bayesian Optimization add over MAB?*
(Answer: a surrogate model that encodes correlation across the input space, enabling
principled guidance of where to sample — not just pulling arms at random.)

---

### Step 4: Read the full lineage as a narrative

```python
# Print the complete lineage narrative from root to target
lineage = cc.get_algorithm_lineage("tpe-default")

for step in lineage.steps:
    print(f"[{step.year}] {step.name}")
    print(f"  Problem solved: {step.problem_solved}")
    print(f"  Key design choice: {step.key_design_choice}")
    if step.limitation:
        print(f"  Remaining limitation: {step.limitation}")
    print()
```

Expected output:

```
[1933] Multi-Armed Bandit
  Problem solved: How to allocate trials across options with unknown reward distributions
                  to maximize total reward.
  Key design choice: Treat each option as an independent arm; use the UCB formula to
                     balance exploration and exploitation.
  Remaining limitation: Arms are independent — cannot leverage similarity between options
                        to guide where to sample next.

[1998] Bayesian Optimization (Gaussian Process)
  Problem solved: Optimize expensive black-box functions with a surrogate that models
                  correlations across the search space.
  Key design choice: Use a Gaussian Process as the surrogate; use Expected Improvement
                     as the acquisition function to quantify where to sample.
  Remaining limitation: GP regression is O(n³) in the number of observations; limited
                        to continuous, low-dimensional spaces.

[2011] Tree-structured Parzen Estimator (TPE)
  Problem solved: Sequential optimization that scales to large evaluation budgets,
                  high-dimensional spaces, and conditional/mixed-type parameters.
  Key design choice: Model p(x|y<y*) and p(x|y≥y*) separately (two kernel density
                     estimates) instead of p(y|x) — this inverts the GP model and
                     enables tree-structured conditional spaces natively.
  Remaining limitation: Models each dimension independently by default — does not
                        capture interactions between hyperparameters.
```

**What you are reading:** Each step connects to the next through its *remaining limitation*.
The remaining limitation of one algorithm is the *problem solved* by the next. This is the
genealogy logic: each algorithm is an answer to the limitation of its predecessor.

**Expected result:** A full printed lineage narrative from MAB (1933) to TPE (2011).

---

### Step 5: Explore the CMA-ES lineage

Now follow a different path — the CMA-ES lineage through Evolution Strategies:

```python
cmaes_lineage = cc.get_algorithm_lineage("cma-es-default")

for step in cmaes_lineage.steps:
    print(f"[{step.year}] {step.name}")
    print(f"  Problem solved: {step.problem_solved}")
    print(f"  Key design choice: {step.key_design_choice}")
    if step.limitation:
        print(f"  Remaining limitation: {step.limitation}")
    print()
```

Expected output:

```
[1960s–1970s] Evolution Strategies (ES)
  Problem solved: Optimize continuous functions using mutation and selection without
                  requiring gradient information.
  Key design choice: Apply Gaussian mutation to candidate solutions; select the best
                     μ survivors from λ offspring.
  Remaining limitation: Step size (σ) is a scalar — all directions are mutated equally,
                        which is inefficient in anisotropic or ill-conditioned landscapes.

[1987–1996] Self-Adaptive ES / Strategy Parameter Control
  Problem solved: Adapt the mutation step size online without manual tuning.
  Key design choice: Encode σ in the genome and let it evolve alongside the solution.
  Remaining limitation: Step size is still isotropic — adapts magnitude but not direction.
                        Cannot exploit axis-aligned structure or correlated variables.

[1996] CMA (Covariance Matrix Adaptation)
  Problem solved: Adapt the full shape and orientation of the mutation distribution,
                  not just its magnitude.
  Key design choice: Maintain a covariance matrix C that encodes the correlation
                     structure of successful mutation steps; update C online using
                     the evolution path.
  Remaining limitation: Quadratic memory and time cost in dimension d (O(d²)) —
                        impractical for very high-dimensional problems (d > 1000).

[2001] CMA-ES (Hansen & Ostermeier)
  Problem solved: Combine CMA with principled step-size adaptation (cumulative
                  step-size adaptation, CSA) into a single algorithm with no
                  free parameters requiring manual tuning.
  Key design choice: Two complementary adaptation mechanisms: CMA for distribution
                     shape; CSA for global step size.
  Remaining limitation: Still O(d²); not designed for noisy objectives with high
                        evaluation cost.
```

**Why this step matters:** The CMA-ES lineage illustrates a different evolutionary story
than the MAB → TPE path. Both paths solve the same fundamental problem (where to sample
next) but from opposite starting points — one from probability theory, one from biology.

**Expected result:** Full lineage narrative from Evolution Strategies to CMA-ES.

---

### Step 6: Generate a genealogy visualization

```python
result = cc.visualize(
    algorithm_id="tpe-default",
    viz_type="genealogy",
    format="svg",
    output_path="tpe_genealogy.svg",
)
print("Saved to:", result.output_path)
```

Expected output:

```
Saved to: tpe_genealogy.svg
```

Open `tpe_genealogy.svg` in a browser or vector graphics editor. You will see a directed
node-link diagram: nodes are algorithms, edges point from ancestor to descendant,
and each edge is labelled with the limitation it resolves.

**Tip:** Generate the CMA-ES genealogy alongside:

```python
cc.visualize(algorithm_id="cma-es-default", viz_type="genealogy",
             format="svg", output_path="cmaes_genealogy.svg")
```

Place the two SVGs side by side — you can see the different evolutionary paths converging
on the same goal of efficient search over high-dimensional spaces.

**Expected result:** Two SVG files, each showing a directed genealogy timeline ending at
the target algorithm.

---

### Step 7: Navigate to a descendant (optional)

Find what TPE inspired:

```python
genealogy = cc.get_algorithm_genealogy("tpe-default")

print("Successors:")
for succ in genealogy.successors:
    print(" •", succ.name, f"({succ.year})")
    print("   Design choice inherited:", succ.inherited_from_tpe)
    print("   New problem solved:", succ.new_problem_solved)
```

Expected output:

```
Successors:
 • Hyperopt-sklearn (2013)
   Design choice inherited: TPE as the underlying optimizer
   New problem solved: Combined algorithm selection and hyperparameter optimization
                       (CASH) for scikit-learn pipelines.
 • Optuna TPE sampler (2019)
   Design choice inherited: Tree-structured Parzen estimation with independent modeling
   New problem solved: Modern framework API; dynamic search spaces; pruning integration.
```

**Expected result:** A list of algorithms that built on TPE, with the specific design
choice inherited and the new problem each solved.

---

## Expected Outcome

After this tutorial you have:
1. Traced the full MAB → Bayesian Optimization → TPE lineage
2. Traced the Evolution Strategies → CMA-ES lineage
3. Saved genealogy SVG visualizations for both algorithms
4. Identified what problem each algorithm in the lineage solved and what limitation
   it left open

**Verifiable criterion:** Run `cc.get_algorithm_lineage("tpe-default")`. The returned
`lineage.steps` list has at least 3 entries with non-empty `problem_solved` and
`key_design_choice` fields on each. If any field is empty, the genealogy data for that
step is incomplete.

---

## What You Learned

- **Genealogy explains design rationale, not mechanics** — the genealogy record answers
  "why does this algorithm have a covariance matrix?" (because its predecessor could only
  mutate isotropically, which is inefficient in correlated landscapes). The mathematical
  mechanics are separate.
  → GLOSSARY: Algorithm Genealogy

- **Each algorithm is an answer to a limitation** — `step.limitation` is always the
  `problem_solved` of the next step. Reading these in sequence is reading the algorithm's
  problem-solution chain.

- **Navigation is bidirectional** — `genealogy.predecessors` and `genealogy.successors`
  allow traversal in both directions. Starting from a modern algorithm (Optuna TPE) and
  tracing backward reveals the historical context; starting from an ancestor (MAB) and
  tracing forward shows how the field developed.

- **F1: missing genealogy data is explicit** — if no genealogy data exists, the system
  says so and lists algorithms for which it does. It never fabricates historical data.
  → UC-10 Failure Scenario F1

- **Genealogy is metadata-only** — unlike convergence and trajectory visualizations,
  genealogy data does not require a completed Study. The genealogy SVG is always
  available for registered algorithms with genealogy records.
  → Algorithm Visualization Engine: "Data owned: None"

---

## Further Reading

- **See the algorithm search visually:** [`06-learner-algorithm-visualization.md`](06-learner-algorithm-visualization.md) — convergence animation, trajectory, sensitivity heatmap for CMA-ES and TPE
- **Ask deeper questions about CMA-ES:** [`05-learner-socratic-mode.md`](05-learner-socratic-mode.md) — Socratic Mode tutorial using the same CMA-ES covariance matrix question
- **UC-10 full use case:** [`../02-design/01-software-requirement-specification/02-use-cases/11-uc-10.md`](../02-design/01-software-requirement-specification/02-use-cases/11-uc-10.md) — Algorithm History and Evolution
- **Genealogy data schema:** `corvus_corone_pilot/learner/data/genealogy_data.json` — the structured data that backs these results (IMPL-046)
- **GLOSSARY entries:** [`../GLOSSARY.md`](../GLOSSARY.md) — Algorithm Genealogy, Algorithm Visualization, Learner
