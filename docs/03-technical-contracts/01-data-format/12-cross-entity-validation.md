# §5 Validation Rules (Cross-Entity)

> Index: [01-index.md](01-index.md)

<!--
STORY ROLE: The enforcement layer that makes all per-entity schemas cohere into a consistent
whole. Cross-entity rules cannot be expressed as per-field constraints on a single schema —
they require reading two or more entities together. These rules are the difference between
"each entity looks valid in isolation" and "the full dataset is internally consistent".

Without these invariants, the system cannot guarantee reproducibility (MANIFESTO Principles 19–22)
— a Run could reference a problem outside the Study's scope, a seed could collide silently,
or a ResultAggregate could count runs that never completed.

CONNECTS TO:
  ← §2.1–§2.8 (entity schemas)           : per-entity fields referenced in each rule
  → interface-contracts.md §5 (Repository): enforcement is the Repository's responsibility at
    write time; the Analyzer enforces read-time rules before analysis begins
  → c4-level4-code/06-results-store/      : implementation location for write-time checks
  → c4-level4-code/05-analysis-engine/    : implementation location for analysis-time checks
  → community/versioning-governance.md    : schema versioning must not break any invariant here
-->

---

## Overview

Cross-entity validation rules (CVs) are **invariants that span two or more entities**.  
They supplement the per-entity validation rules in §2.1–§2.8, which remain in force.

Each rule specifies:

| Field | Meaning |
|---|---|
| **ID** | Stable identifier (`CV-NNN`) for use in error messages and code comments |
| **Entities** | Which entity types the rule spans |
| **Check point** | When the rule is evaluated: *write time*, *status transition*, or *analysis time* |
| **Violation response** | What happens when the rule fails: `reject` (hard block), `warn` (proceed but log), or `flag` (mark aggregate as suspect) |

**Enforcement responsibility:**

| Check point | Responsible component |
|---|---|
| Write time | `Repository` (§5 of interface-contracts.md) |
| Status transition | `Repository` on entity update |
| Analysis time | `Analyzer` (§4 of interface-contracts.md) before computing metrics |

---

## Quick Reference

| ID | Rule summary | Entities | Check point | Response |
|---|---|---|---|---|
| [CV-001](#cv-001) | Run.problem_instance_id ∈ Study.problem_instance_ids | Run, Study | Write | Reject |
| [CV-002](#cv-002) | Run.algorithm_instance_id ∈ Study.algorithm_instance_ids | Run, Study | Write | Reject |
| [CV-003](#cv-003) | Run.study_id == Experiment.study_id | Run, Experiment | Write | Reject |
| [CV-004](#cv-004) | Seed unique per (Experiment, problem_instance_id, algorithm_instance_id) | Run, Experiment | Write | Reject |
| [CV-005](#cv-005) | Experiment.run_ids count == repetitions × \|problems\| × \|algorithms\| at completion | Experiment, Study | Status → completed | Reject |
| [CV-006](#cv-006) | Study locking: designated fields must not change after first Run is created | Study, Run | Write (Study update) | Reject |
| [CV-007](#cv-007) | ResultAggregate.problem_instance_id ∈ Study.problem_instance_ids | ResultAggregate, Study | Write | Reject |
| [CV-008](#cv-008) | ResultAggregate.algorithm_instance_id ∈ Study.algorithm_instance_ids | ResultAggregate, Study | Write | Reject |
| [CV-009](#cv-009) | ResultAggregate.n_runs == count of completed Runs for (experiment, problem, algorithm) | ResultAggregate, Run | Write | Reject |
| [CV-010](#cv-010) | PerformanceRecord.evaluation_number strictly increasing within a Run | PerformanceRecord, Run | Write | Reject |
| [CV-011](#cv-011) | PerformanceRecord.elapsed_time non-decreasing within a Run | PerformanceRecord, Run | Write | Reject |
| [CV-012](#cv-012) | First PerformanceRecord of a Run must have is_improvement == true | PerformanceRecord, Run | Write | Reject |
| [CV-013](#cv-013) | Exactly one end_of_run record per Run at evaluation_number == budget_used | PerformanceRecord, Run | Status → completed/failed | Reject |
| [CV-014](#cv-014) | No improvement record after cap_reached_at_evaluation | PerformanceRecord, Run | Write | Reject |
| [CV-015](#cv-015) | Every completed Experiment has exactly one researcher and one practitioner Report | Experiment, Report | Status → completed | Reject |
| [CV-016](#cv-016) | ParameterSensitivity.parameter_name ∈ AlgorithmInstance.hyperparameters | AlgorithmInstance | Write | Reject |
| [CV-017](#cv-017) | ResultAggregate.anytime_curves covers full evaluation_number range of underlying Records | ResultAggregate, PerformanceRecord | Analysis time | Flag |

---

## Rules

---

### CV-001

**Run.problem_instance_id must be in the parent Study's problem scope**

| | |
|---|---|
| **Entities** | Run, Study |
| **Check point** | Write time — when a Run is created |
| **Response** | Reject |

The `problem_instance_id` of every Run must be an element of the `problem_instance_ids` list
of the Study that the Run's parent Experiment references.

```
let study = Study[Experiment[run.experiment_id].study_id]
assert run.problem_instance_id ∈ study.problem_instance_ids
```

**Rationale:** A Run that executes a Problem not declared in the Study is outside the study
design and cannot be attributed to any pre-registered hypothesis. Permitting it would allow
post-hoc problem addition, violating MANIFESTO Principle 4 (problem selection before data
collection).

**Error:** `ValidationError` — `"Run.problem_instance_id {id} is not in Study.problem_instance_ids {ids}"`

---

### CV-002

**Run.algorithm_instance_id must be in the parent Study's algorithm scope**

| | |
|---|---|
| **Entities** | Run, Study |
| **Check point** | Write time — when a Run is created |
| **Response** | Reject |

`Run.algorithm_instance_id` must be an element of the `algorithm_instance_ids`
list of the Study that the Run's parent Experiment references.

```
let study = Study[Experiment[run.experiment_id].study_id]
assert run.algorithm_instance_id ∈ study.algorithm_instance_ids
```

**Rationale:** Symmetric to CV-001. Algorithms not declared in the Study design cannot be
part of a pre-registered comparison (MANIFESTO Principle 8).

**Error:** `ValidationError` — `"Run.algorithm_instance_id {id} is not in Study.algorithm_instance_ids {ids}"`

---

### CV-003

**Run.study_id must match the study_id of its parent Experiment**

| | |
|---|---|
| **Entities** | Run, Experiment |
| **Check point** | Write time — when a Run is created |
| **Response** | Reject |

`Run.study_id` is a denormalized field for query convenience. Its value must equal
`Experiment[run.experiment_id].study_id`.

```
assert run.study_id == Experiment[run.experiment_id].study_id
```

**Rationale:** The denormalized field exists only to avoid repeated joins in queries.
Allowing it to diverge from the canonical value would create a split-brain inconsistency
where queries on `Run.study_id` return different results than queries through
`Run.experiment_id → Experiment.study_id`.

**Error:** `ValidationError` — `"Run.study_id {sid} does not match Experiment.study_id {eid}"`

---

### CV-004

**Seeds must be unique within an Experiment per (problem_instance_id, algorithm_instance_id) pair**

| | |
|---|---|
| **Entities** | Run, Experiment |
| **Check point** | Write time — when a Run is created |
| **Response** | Reject |

No two Runs belonging to the same Experiment may share the same `seed` value for the same
`(problem_instance_id, algorithm_instance_id)` combination.

```
for each existing Run r' in Experiment[run.experiment_id]:
    if (r'.problem_instance_id == run.problem_instance_id and
        r'.algorithm_instance_id == run.algorithm_instance_id):
        assert r'.seed != run.seed
```

**Rationale:** Duplicate seeds within the same (problem, algorithm) cell produce statistically
dependent samples. They undermine the assumed independence of repetitions and invalidate
inter-run variance estimates. This is a direct operationalization of MANIFESTO Principle 18
(reproducibility through seed management) and NFR-REPRO-01.

**Error:** `ReproducibilityError` → `SeedCollisionError` — `"Seed {seed} already used for (problem={pid}, algorithm={aid}) in Experiment {eid}"`

---

### CV-005

**Experiment run count must match the full factorial at completion**

| | |
|---|---|
| **Entities** | Experiment, Study |
| **Check point** | Status transition — when Experiment.status is set to `completed` |
| **Response** | Reject |

When an Experiment transitions to `completed`, the number of Runs in `run_ids` must equal
the full factorial product defined by the Study:

```
let study = Study[experiment.study_id]
let expected = (study.experimental_design.repetitions
                × len(study.problem_instance_ids)
                × len(study.algorithm_instance_ids))
assert len(experiment.run_ids) == expected
```

**Rationale:** A `completed` Experiment with a partial run set is misleading to downstream
analysis. ResultAggregates computed over incomplete data misrepresent statistical power and
may skew conclusions. The Experiment may transition to `failed` instead — that is the
appropriate status when execution was interrupted.

**Error:** `ValidationError` — `"Experiment {eid} has {n} runs but expected {expected} for completed status"`

---

### CV-006

**Study execution parameters must not be modified after the first Run is created**

| | |
|---|---|
| **Entities** | Study, Run |
| **Check point** | Write time — when a Study field update is attempted |
| **Response** | Reject |

The following Study fields are **locked** once any Run referencing the Study exists:

| Locked field | Why it matters |
|---|---|
| `experimental_design.repetitions` | Changing it would invalidate CV-005 and result count expectations |
| `sampling_strategy` | Changing mid-experiment produces records under different sampling regimes — curves are not comparable across runs |
| `log_scale_schedule` | Governs which evaluation checkpoints are written; changing it renders earlier records non-uniform |
| `improvement_epsilon` | Changing it alters which objective improvements produce records, making is_improvement flags inconsistent across runs |

```
if any Run exists with run.study_id == study.id:
    assert none of the locked fields above have changed
```

**Rationale:** These fields govern how the experiment is conducted and how PerformanceRecords
are written. Modifying them after execution begins introduces between-run heterogeneity that
cannot be detected or corrected during analysis, directly violating MANIFESTO Principle 19
(reproducibility) and NFR-REPRO-01.

**Error:** `ValidationError` → `ImmutableFieldError` — `"Study field '{field}' cannot be modified after Runs have been created (study_id={sid})"`

---

### CV-007

**ResultAggregate.problem_instance_id must be in the parent Study's problem scope**

| | |
|---|---|
| **Entities** | ResultAggregate, Study |
| **Check point** | Write time — when a ResultAggregate is created |
| **Response** | Reject |

```
let study = Study[Experiment[agg.experiment_id].study_id]
assert agg.problem_instance_id ∈ study.problem_instance_ids
```

**Rationale:** A ResultAggregate over a Problem not in the Study scope cannot be attributed to
the Study's research question and may indicate a data integrity error (e.g., a Run from a
different Experiment was aggregated by mistake).

**Error:** `ValidationError` — `"ResultAggregate.problem_instance_id {id} is not in Study.problem_instance_ids {ids}"`

---

### CV-008

**ResultAggregate.algorithm_instance_id must be in the parent Study's algorithm scope**

| | |
|---|---|
| **Entities** | ResultAggregate, Study |
| **Check point** | Write time — when a ResultAggregate is created |
| **Response** | Reject |

```
let study = Study[Experiment[agg.experiment_id].study_id]
assert agg.algorithm_instance_id ∈ study.algorithm_instance_ids
```

**Rationale:** Symmetric to CV-007.

**Error:** `ValidationError` — `"ResultAggregate.algorithm_instance_id {id} is not in Study.algorithm_instance_ids {ids}"`

---

### CV-009

**ResultAggregate.n_runs must equal the count of completed Runs for its (experiment, problem, algorithm) cell**

| | |
|---|---|
| **Entities** | ResultAggregate, Run |
| **Check point** | Write time — when a ResultAggregate is created or updated |
| **Response** | Reject |

```
let attempted_runs = count of Runs where:
    run.experiment_id == agg.experiment_id
    AND run.problem_instance_id == agg.problem_instance_id
    AND agg.algorithm_instance_id == run.algorithm_instance_id
assert agg.n_runs == attempted_runs
```

Note: `n_runs` counts all attempted Runs for the cell (both `completed` and `failed`), while
`AggregateValue.n_successful` counts only those that contributed to a specific metric.
The relationship is: `agg.n_runs >= AggregateValue.n_successful` for every metric.

**Rationale:** A mismatch means either failed Runs were silently dropped (obscuring failure
rate) or phantom Runs were invented. Both undermine the statistical validity of the aggregate.
MANIFESTO Principle 15 requires reporting over all runs, not cherry-picked subsets.

**Error:** `ValidationError` — `"ResultAggregate.n_runs {n} does not match completed run count {count} for (experiment={eid}, problem={pid}, algorithm={aid})"`

---

### CV-010

**PerformanceRecord.evaluation_number must be strictly monotonically increasing within a Run**

| | |
|---|---|
| **Entities** | PerformanceRecord, Run |
| **Check point** | Write time — when a PerformanceRecord is created |
| **Response** | Reject |

```
let previous = last PerformanceRecord written for run_id
if previous exists:
    assert record.evaluation_number > previous.evaluation_number
```

**Rationale:** The anytime curve interpretation of PerformanceRecords assumes a total ordering
by evaluation count. Out-of-order or duplicate evaluation numbers produce non-monotonic
performance curves that cannot be interpolated (LOCF interpolation in the Analysis Engine
requires strict ordering).

**Error:** `ValidationError` → `DuplicateEvaluationError` — `"PerformanceRecord.evaluation_number {n} is not greater than previous {prev} for run_id={rid}"`

---

### CV-011

**PerformanceRecord.elapsed_time must be non-decreasing within a Run**

| | |
|---|---|
| **Entities** | PerformanceRecord, Run |
| **Check point** | Write time — when a PerformanceRecord is created |
| **Response** | Reject |

```
let previous = last PerformanceRecord written for run_id
if previous exists:
    assert record.elapsed_time >= previous.elapsed_time
```

Non-strict inequality (`>=`) is used to permit wall-clock precision limitations (two records
may legally have the same `elapsed_time` if they occur within the timer resolution).

**Rationale:** Decreasing elapsed time indicates a clock error or a record written out of
order. TIME-based metrics (e.g., `TIME-EVALUATIONS_TO_TARGET`) rely on monotonic elapsed
time to produce meaningful anytime curves.

**Error:** `ValidationError` — `"PerformanceRecord.elapsed_time {t} is less than previous {prev} for run_id={rid}"`

---

### CV-012

**The first PerformanceRecord of every Run must have is_improvement == true**

| | |
|---|---|
| **Entities** | PerformanceRecord, Run |
| **Check point** | Write time — when the first PerformanceRecord for a Run is created |
| **Response** | Reject |

```
if no PerformanceRecord exists yet for record.run_id:
    assert record.is_improvement == true
```

**Rationale:** There is no prior objective value to compare against at evaluation 1. The first
observation is unconditionally the best observed so far, making `is_improvement == false`
semantically impossible. An incorrect `false` value would corrupt per-Run improvement counts
and success rate calculations.

**Error:** `ValidationError` — `"First PerformanceRecord for run_id={rid} must have is_improvement=true"`

---

### CV-013

**Every Run must have exactly one end-of-run PerformanceRecord at evaluation_number == budget_used**

| | |
|---|---|
| **Entities** | PerformanceRecord, Run |
| **Check point** | Status transition — when Run.status is set to `completed`, `failed`, or `budget_exhausted` |
| **Response** | Reject |

```
let end_records = PerformanceRecords for run where "end_of_run" ∈ trigger_reason
assert len(end_records) == 1
assert end_records[0].evaluation_number == run.budget_used
```

**Rationale:** The end-of-run record is the canonical final observation for a Run. Metric
computations that require the best-at-budget value (e.g., `QUALITY-BEST_VALUE_AT_BUDGET`)
rely on its existence and correct evaluation number. Missing or misplaced end-of-run records
make these metrics undefined.

**Error:** `ValidationError` — `"Run {rid} must have exactly one end_of_run PerformanceRecord at evaluation_number={budget}; found {count}"`

---

### CV-014

**No improvement-triggered PerformanceRecord may exist after cap_reached_at_evaluation**

| | |
|---|---|
| **Entities** | PerformanceRecord, Run |
| **Check point** | Write time — when a PerformanceRecord is created |
| **Response** | Reject |

```
if run.cap_reached_at_evaluation is not null:
    if "improvement" ∈ record.trigger_reason:
        assert record.evaluation_number <= run.cap_reached_at_evaluation
```

Scheduled records (`trigger_reason == "scheduled"` or `"end_of_run"`) are still permitted
after the cap.

**Rationale:** `Study.max_records_per_run` caps improvement logging to bound storage. Once the
cap is hit, the Runner stops writing improvement records but continues writing scheduled
checkpoints. A record with `trigger_reason` containing `improvement` after the cap indicates
a Runner implementation error that would produce inconsistent `is_improvement` accounting.

**Error:** `ValidationError` — `"Improvement PerformanceRecord at evaluation {n} exceeds cap at {cap} for run_id={rid}"`

---

### CV-015

**Every completed Experiment must have exactly one researcher Report and one practitioner Report**

| | |
|---|---|
| **Entities** | Experiment, Report |
| **Check point** | Status transition — when Experiment.status is set to `completed` |
| **Response** | Reject |

```
let reports = Reports where report.experiment_id == experiment.id
let researcher_reports = [r for r in reports where r.type == "researcher"]
let practitioner_reports = [r for r in reports where r.type == "practitioner"]
assert len(researcher_reports) == 1
assert len(practitioner_reports) == 1
```

Reports may be created before completion, but the transition to `completed` is blocked until
both exist.

**Rationale:** FR-20 requires both report types for every completed Experiment.
A `completed` Experiment without both Reports is undischarged — the findings have not been
communicated in any usable form, violating MANIFESTO Principle 24 (scope and conclusions
must be reported). Blocking completion (rather than warning) ensures this is never silently
skipped.

**Error:** `ValidationError` — `"Experiment {eid} cannot transition to completed: missing {type} Report"`

---

### CV-016

**Every ParameterSensitivity.parameter_name must match a key in the parent AlgorithmInstance.hyperparameters**

| | |
|---|---|
| **Entities** | AlgorithmInstance (SensitivityReport sub-entity) |
| **Check point** | Write time — when an AlgorithmInstance with a sensitivity_report is created or updated |
| **Response** | Reject |

```
if algorithm_instance.sensitivity_report is not null:
    for each ps in algorithm_instance.sensitivity_report.parameters:
        assert ps.parameter_name ∈ algorithm_instance.hyperparameters.keys()
```

**Rationale:** A sensitivity report that names a parameter not present in `hyperparameters`
cannot have been produced by varying that parameter on this Algorithm Instance. Such a
mismatch indicates either a copy-paste error from another algorithm or a stale report not
updated after a hyperparameter rename. Either way the sensitivity data is not attributable
to this instance and must be rejected.

**Error:** `ValidationError` — `"SensitivityReport.parameter_name '{name}' not found in AlgorithmInstance.hyperparameters for algorithm_id={aid}"`

---

### CV-017

**ResultAggregate.anytime_curves must cover the full evaluation_number range of underlying PerformanceRecords**

| | |
|---|---|
| **Entities** | ResultAggregate, PerformanceRecord |
| **Check point** | Analysis time — checked by the Analyzer before returning a ResultAggregate |
| **Response** | Flag (`anytime_curves_incomplete: true` on the ResultAggregate) |

```
let records = PerformanceRecords for all Runs in the (experiment, problem, algorithm) cell
let record_range = [min(evaluation_number), max(evaluation_number)] across all records
let curve_range  = [min(evaluation_number), max(evaluation_number)] in anytime_curves
assert curve_range[0] <= record_range[0]
assert curve_range[1] >= record_range[1]
```

A flag (not a rejection) is used here because curve coverage may be intentionally bounded
during exploratory analysis. A rejection would prevent partial analysis; a flag ensures the
limitation is visible in the ResultAggregate and propagated to the Report's limitations
section (FR-21).

**Rationale:** An `anytime_curves` list that stops before `budget_used` silently truncates the
performance profile. Callers computing `ANYTIME-ECDF_AREA` (which integrates over the full
budget) would produce underestimates without any indication that data is missing. Flagging
forces the limitation into the Report, maintaining MANIFESTO Principle 24 (scope of
conclusions must be stated).

**Behavior on flag:** The ResultAggregate gains the field `anytime_curves_incomplete: true`.
The Reporting Engine's Limitations Enforcer checks for this flag and adds a mandatory
limitations note (FR-21): `"Anytime curves do not cover full evaluation range; ECDF area
values may be underestimated."`
