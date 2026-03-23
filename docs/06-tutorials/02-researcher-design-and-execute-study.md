# Tutorial: Design and Execute a Reproducible Benchmarking Study

<!--
STORY ROLE: The primary researcher tutorial. Walks through UC-01 end-to-end,
demonstrating every protocol step as concrete, runnable code. This is the document
most researchers will read first after installation.

NARRATIVE POSITION:
  UC-01 → this tutorial → (concrete researcher experience)
  01-cmd-first-study.md (quick CLI demo) → this tutorial (full protocol walkthrough)

CONNECTS TO:
  → docs/02-design/01-software-requirement-specification/02-use-cases/02-uc-01.md
  → docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md : all 8 steps
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md : Step 7 analysis
  → docs/03-technical-contracts/01-data-format.md : Study, Experiment, Run, Report schemas
  → docs/03-technical-contracts/03-metric-taxonomy.md : Standard Reporting Set
  → docs/GLOSSARY.md : all entity names used here
-->

---

## Audience

**Researcher** — a scientist or engineer who wants to produce a valid, reproducible
comparison between two or more HPO algorithms.

**Prior knowledge assumed:**
- *Domain:* You understand what hyperparameter optimization is and why algorithm
  comparisons are scientifically non-trivial (different algorithms work well on
  different problems).
- *Technical:* Python 3.10+, basic familiarity with `pip` or `uv`.
- *System:* `corvus-corone` is installed. If not, run `pip install corvus-corone`.

**Before this tutorial:** optionally complete
[`01-cmd-first-study.md`](01-cmd-first-study.md) for a five-minute CLI orientation.

---

## Learning Objective

After completing this tutorial, you will be able to design, execute, and interpret a
complete reproducible benchmarking study that compares two HPO algorithms — with
pre-registered hypotheses, locked experimental design, and a generated report that
correctly scopes all conclusions to the tested conditions.

---

## Prerequisites

```bash
pip install corvus-corone
corvus --version   # should print 0.x.x
```

No data files needed — this tutorial uses problems from the built-in registry.

---

## Overview

This tutorial walks through all 8 steps of the
[Benchmarking Study Protocol](../04-scientific-practice/01-methodology/01-benchmarking-protocol.md).
You will compare **Random Search** against **TPE** (Tree-structured Parzen Estimator,
via Optuna) on a set of synthetic HPO problems. By the end, you will have:

- A locked, pre-registered [Study](../GLOSSARY.md#study--benchmarking-study) record
- A completed [Experiment](../GLOSSARY.md#experiment) with 10 independent runs per
  (problem, algorithm) pair
- A Researcher Report and a Practitioner Report
- A Raw Data export you can analyze independently

The scenario is intentionally simple so you can focus on the *process*, not the
specific algorithms. The same process applies to any algorithms and problems you
substitute later.

---

## Steps

### Step 1: Formulate the research question

Before touching any code, write down what you want to know. A valid research question
must name the algorithms, the problem class, the performance dimension, and the scope
boundary. Vague questions produce invalid studies.

**Bad:** "Is TPE better than Random Search?"
*(No scope. No performance dimension. Presupposes a universal answer.)*

**Good (what we will use):**
> "Does TPE (Optuna default sampler) achieve better final solution quality than
> Random Search within a budget of 50 evaluations, on low-dimensional (2–5 variable)
> synthetic HPO problems with moderate noise? Conclusions do not extend to
> high-dimensional or deterministic problems."

Write this down now. You will paste it into code in the next step.

*Why this matters:* MANIFESTO Principle 1 — benchmarking serves understanding, not
ranking. A scoped question is the first enforcement mechanism against over-generalization.
→ [Protocol Step 1](../04-scientific-practice/01-methodology/01-benchmarking-protocol.md#step-1-formulate-the-research-question)

---

### Step 2: Browse the Problem Repository

List problems available in the built-in registry and identify ones that match
your scope (low-dimensional, noisy):

```python
import corvus_corone as cc

problems = cc.list_problems()
for p in problems:
    print(f"{p.name}  dim={p.dimensions}  noise={p.noise_level}  id={p.id}")
```

Expected output (built-in registry):

```
SyntheticNoisyRosenbrock2D    dim=2  noise=gaussian_0.1  id=prob-001
SyntheticNoisyBranin          dim=2  noise=gaussian_0.1  id=prob-002
SyntheticNoisyHartmann3D      dim=3  noise=gaussian_0.05 id=prob-003
SyntheticNoisyAckley5D        dim=5  noise=gaussian_0.2  id=prob-004
```

Select three problems that span your stated scope — different dimensionalities and
noise levels, none of which is known to specifically favour either algorithm:

```python
selected_problems = ["prob-001", "prob-002", "prob-004"]
```

*Why this matters:* MANIFESTO Principle 5 — problem diversity prevents cherry-picking.
Three problems is a minimum for a meaningful study; more is better.
→ [Protocol Step 3](../04-scientific-practice/01-methodology/01-benchmarking-protocol.md#step-3-select-problem-instances)

---

### Step 3: Select algorithm instances

List available algorithm instances and identify both your candidates:

```python
algorithms = cc.list_algorithms()
for a in algorithms:
    print(f"{a.name}  family={a.algorithm_family}  id={a.id}")
```

Expected output:

```
RandomSearch                  family=random         id=alg-001
OptunaTPE_default             family=bayesian_tpe   id=alg-002
OptunaTPE_n_startup_10        family=bayesian_tpe   id=alg-003
CMAESDefault                  family=evolutionary   id=alg-004
```

Select the default Random Search and the default Optuna TPE instance. Review the
`configuration_justification` before selecting — it should explain why the chosen
hyperparameters are fair for the problem class you defined:

```python
tpe = cc.get_algorithm("alg-002")
print(tpe.configuration_justification)
# "Default Optuna TPE sampler: n_startup_trials=10, n_ei_candidates=24.
#  These are the documented defaults recommended for general-purpose use.
#  No tuning was performed on problems in this study."

selected_algorithms = ["alg-001", "alg-002"]
```

*Why this matters:* MANIFESTO Principle 10 — every algorithm must be configured at
"best reasonable effort." Using undocumented defaults without justification is a
configuration fairness violation.
→ [Protocol Step 4](../04-scientific-practice/01-methodology/01-benchmarking-protocol.md#step-4-configure-algorithm-portfolio)

---

### Step 4: Pre-register hypotheses

Write down your hypotheses **now**, before any data is collected. The system will
lock them when you create the Study. You cannot change them after that point.

```python
hypotheses = [
    {
        "h0": "There is no significant difference in QUALITY-BEST_VALUE_AT_BUDGET "
              "between OptunaTPE_default and RandomSearch across the three selected "
              "problem instances at budget=50.",
        "h1": "OptunaTPE_default achieves lower QUALITY-BEST_VALUE_AT_BUDGET than "
              "RandomSearch (directional, one-sided).",
        "test": "Wilcoxon signed-rank test (paired, α=0.05)",
        "alpha": 0.05,
        "correction": "Holm-Bonferroni (3 problems = 3 tests)",
        "metrics": ["QUALITY-BEST_VALUE_AT_BUDGET"]
    }
]
```

*Why this matters:* MANIFESTO Principle 16 — experimental design is consciously
planned before data collection. Hypotheses selected after seeing results are
observations, not predictions, and cannot appear in the confirmatory analysis.
→ [Protocol Step 2](../04-scientific-practice/01-methodology/01-benchmarking-protocol.md#step-2-pre-register-hypotheses)

---

### Step 5: Create and lock the Study

Assemble all decisions into a Study record and submit it. This is the
**pre-registration gate** — the system locks the plan the moment you call `create_study`.

```python
study = cc.create_study(
    name="TPE vs RandomSearch on low-dim noisy HPO problems",
    research_question=(
        "Does TPE (Optuna default sampler) achieve better final solution quality "
        "than Random Search within a budget of 50 evaluations, on low-dimensional "
        "(2–5 variable) synthetic HPO problems with moderate noise? "
        "Conclusions do not extend to high-dimensional or deterministic problems."
    ),
    problem_instance_ids=selected_problems,
    algorithm_instance_ids=selected_algorithms,
    experimental_design={
        "repetitions": 10,
        "budget_allocation": "50 evaluations per run, equal across all algorithms",
        "stopping_criteria": "budget_exhausted",
        "seed_strategy": "sequential",
    },
    sampling_strategy="log_scale_plus_improvement",
    log_scale_schedule={"base_points": [1, 2, 5], "multiplier_base": 10},
    improvement_epsilon=None,   # strict inequality — log every genuine improvement
    pre_registered_hypotheses=hypotheses,
)

print(f"Study created: {study.id}")
print(f"Status: {study.status}")   # → "locked"
```

**Checkpoint 1 — verify the lock:**

```python
# Attempting to modify a locked study raises StudyLockedError
try:
    cc.update_study(study.id, repetitions=20)
except cc.StudyLockedError as e:
    print(f"Correctly rejected: {e}")
# Output: Correctly rejected: Study <id> is locked. Modification attempt recorded.
```

The lock is permanent. If you discover a problem with your design at this point,
you must start a new study — not edit this one. This is intentional.

*Why this matters:* FR-12 / MANIFESTO Principle 16. Any post-hoc modification to
hypotheses, problems, or algorithms would invalidate the confirmatory analysis.

---

### Step 6: Execute the Experiment

Run the study. The system assigns seeds automatically, runs each (problem, algorithm,
repetition) triple independently, and writes PerformanceRecords per the sampling
strategy you pre-registered in Step 5.

```python
experiment = cc.run(study.id)

# This takes several minutes. Monitor progress:
# [=====>        ] 18/60 runs complete (3 problems × 2 algorithms × 10 reps)
```

Or from the CLI:

```bash
corvus run --study-id <study.id>
```

**What happens inside each Run:**
- The Runner injects a unique seed (reproducible, collision-checked within the Experiment)
- PerformanceRecords are written at evaluation counts: 1, 2, 5, 10, 20, 50 (scheduled)
  plus whenever best-so-far strictly improves (improvement trigger)
  plus at evaluation 50 (end-of-run trigger)
- Failed runs log the failure reason; the study continues

**Checkpoint 2 — verify completion:**

```python
experiment = cc.get_experiment(experiment.id)
print(f"Status: {experiment.status}")          # → "completed"
print(f"Runs completed: {len(experiment.run_ids)}")   # → 60
print(f"Failed runs: {sum(1 for r in cc.get_runs(experiment.id) if r.status == 'failed')}")
# → 0 (if all succeeded)
```

If any runs failed, inspect them before proceeding:

```python
for run in cc.get_runs(experiment.id):
    if run.status == "failed":
        print(f"Run {run.id}: {run.failure_reason}")
```

*Why this matters:* MANIFESTO Principle 18 — seeds are system-assigned, never
researcher-chosen. This prevents seed selection that favours a preferred algorithm.

---

### Step 7: Inspect the Result Aggregates

The system automatically computes the
[Standard Reporting Set](../03-technical-contracts/03-metric-taxonomy.md) metrics
across all runs. Verify they exist before generating reports:

```python
aggregates = cc.get_result_aggregates(experiment.id)

for agg in aggregates:
    problem = cc.get_problem(agg.problem_instance_id).name
    algorithm = cc.get_algorithm(agg.algorithm_instance_id).name
    quality = agg.metrics["QUALITY-BEST_VALUE_AT_BUDGET"].statistics
    print(
        f"{algorithm:30s} on {problem:30s} | "
        f"median={quality['median']:.4f}  iqr={quality['q75']-quality['q25']:.4f}"
    )
```

Expected output (illustrative — your values will differ):

```
RandomSearch                   on SyntheticNoisyRosenbrock2D   | median=0.0831  iqr=0.0412
OptunaTPE_default              on SyntheticNoisyRosenbrock2D   | median=0.0214  iqr=0.0093
RandomSearch                   on SyntheticNoisyBranin         | median=0.1203  iqr=0.0714
...
```

This is exploratory (Level 1). Do not draw conclusions yet — the confirmatory
analysis in the report will test your pre-registered hypotheses.

---

### Step 8: Generate and read the reports

```python
reports = cc.generate_reports(experiment.id)

# Two reports are always generated:
researcher_report = next(r for r in reports if r.type == "researcher")
practitioner_report = next(r for r in reports if r.type == "practitioner")

print(f"Researcher report: {researcher_report.artifact_reference}")
print(f"Practitioner report: {practitioner_report.artifact_reference}")
```

Or from the CLI:

```bash
corvus report --experiment-id <experiment.id> --open
# Opens both reports in your browser
```

**What to look for in the Researcher Report:**

1. **Confirmatory analysis section** — results for your pre-registered hypothesis only.
   The report shows the Wilcoxon test result with Holm-Bonferroni correction per problem.
   Post-hoc observations appear in a separate "Exploratory findings" section.

2. **Effect sizes** — p-values alone are not enough. Look for Cliff's delta alongside
   each significant result. A result is actionable only if both the p-value and the
   effect size indicate significance.

3. **Limitations section** — every report has one. Read it. It states:
   - Which problem characteristics were *not* tested
   - Which budget levels the conclusion *does not extend to*
   - That no global "best algorithm" ranking exists or is implied

**What to look for in the Practitioner Report:**

A one-page summary stating which algorithm performed better and *on what specific
problem characteristics and budget*, with an explicit scope statement. If a colleague
asks "which is better?", hand them this report — and point them to the limitations
section.

*Why this matters:* FR-20, FR-21 — every report must scope conclusions explicitly.
A report without a limitations section is invalid per the system's validation rules.
→ [Protocol Step 8](../04-scientific-practice/01-methodology/01-benchmarking-protocol.md#step-8-scope-and-report-conclusions)

---

### Step 9: Export the Raw Data

The raw data export lets you perform your own analyses outside the system:

```python
export_path = cc.export_raw_data(experiment.id, format="json")
print(f"Raw data written to: {export_path}")
# → study_<id>/raw_data/
#     runs.jsonl              (all Run records)
#     performance_records/    (one .jsonl per Run)
#     result_aggregates.json  (all Result Aggregates)
#     study.json              (the locked Study record — reproducibility anchor)
```

The `study.json` file is the reproducibility anchor. Anyone with this file plus the
registered algorithm and problem versions can reproduce every run deterministically.

---

## Expected Outcome

After completing this tutorial, you have:

- A completed `Study` record at `study_<id>/study.json`, locked and version-pinned
- 60 `Run` records (3 problems × 2 algorithms × 10 reps), each with PerformanceRecords
- A `Researcher Report` at `study_<id>/reports/researcher_report.html`
- A `Practitioner Report` at `study_<id>/reports/practitioner_report.html`
- A `Raw Data export` at `study_<id>/raw_data/`

**Verification:** Run the following — it should exit with code 0:

```bash
corvus verify --experiment-id <experiment.id>
# ✓ All 60 runs completed
# ✓ All Standard Reporting Set metrics present
# ✓ Both reports generated with non-empty limitations sections
# ✓ Raw data export complete and parseable
```

---

## What You Learned

- **How to formulate a scoped research question** that prevents over-generalization
  → [benchmarking-protocol.md Step 1](../04-scientific-practice/01-methodology/01-benchmarking-protocol.md#step-1-formulate-the-research-question)

- **Why pre-registration locks the study** and what happens if you try to change it
  → [benchmarking-protocol.md Step 2](../04-scientific-practice/01-methodology/01-benchmarking-protocol.md#step-2-pre-register-hypotheses)

- **How the sampling strategy works** — scheduled checkpoints + improvement records
  give you anytime analysis without storing every evaluation
  → [ADR-002](../02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md)

- **How confirmatory and exploratory analysis are separated** in the report — post-hoc
  observations are valid but cannot masquerade as pre-registered findings
  → [statistical-methodology.md](../04-scientific-practice/01-methodology/02-statistical-methodology.md)

- **What the limitations section is for** — not humility, but the primary mechanism
  against over-generalization (MANIFESTO Principle 24)
  → [FR-21](../02-design/01-software-requirement-specification/03-functional-requirements/07-fr-4.6-reporting-and-visualization.md)

---

## Further Reading

| What you want to do next | Where to go |
|---|---|
| Add your own HPO problem to the registry | `03-contributor-add-problem.md` *(coming soon)* |
| Wrap your own optimizer (e.g., SMAC, HyperOpt) | `04-algorithm-author-wrap-optimizer.md` *(coming soon)* |
| Understand the three-level statistical analysis in depth | [statistical-methodology.md](../04-scientific-practice/01-methodology/02-statistical-methodology.md) |
| Export your results to IOHprofiler for visualization | `05-researcher-export-iohprofiler.md` *(coming soon)* |
| Reproduce a study from a published archive | `06-researcher-reproduce-study.md` *(coming soon)* |
| Understand what metrics are computed and why | [metric-taxonomy.md](../03-technical-contracts/03-metric-taxonomy.md) |
