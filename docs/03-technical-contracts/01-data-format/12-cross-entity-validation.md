# §5 Validation Rules (Cross-Entity)

> Index: [01-index.md](01-index.md)

Invariants that span more than one entity and therefore cannot be expressed as a per-field rule
in §2. Each is stated normatively, with the point at which it is checked and the consequence of
violating it.

Three consequences are used:

| Consequence | Meaning |
|---|---|
| **reject** | The operation fails with the named exception. No partial state is written. |
| **warn** | The operation proceeds. The warning is recorded and carried into the Report limitations section (FR-21). |
| **flag** | The operation proceeds. A `data_quality` marker is written onto the affected record so that analysis can account for it. |

The exception names are those of the taxonomy in
[`../02-interface-contracts/07-cross-cutting-contracts.md`](../02-interface-contracts/07-cross-cutting-contracts.md) §6 (ADR-015).

---

## CEV-01 — Study entity references resolve

**Rule:** Every element of `Study.problem_instance_ids` and `Study.algorithm_instance_ids` MUST
resolve to an existing entity that is not deprecated.

**Checked:** at `lock_study()`.

**Consequence:** reject, `ValidationError`, naming every unresolved identifier rather than the
first.

**Note:** entities are immutable (ADR-020), so an identifier that resolves at lock time resolves
forever. This is what makes the reference sufficient on its own and why no version needs to be
recorded alongside it.

---

## CEV-02 — Run entities belong to the parent Study

**Rule:** `Run.problem_instance_id` and `Run.algorithm_instance_id` MUST each appear in the
corresponding list on the Study that the Run's Experiment realises.

**Checked:** at `create_run()`, against `Experiment.study_id`.

**Consequence:** reject, `ValidationError`.

---

## CEV-03 — Seed uniqueness within an Experiment

**Rule:** Within one Experiment, no two Runs sharing a `(problem_instance_id,
algorithm_instance_id)` pair may carry the same `seed`.

**Checked:** by the Runner, before a Run executes, against the set of seeds already assigned in
the Experiment (ADR-017).

**Consequence:** reject, `SeedCollisionError`. This is a critical error: the Experiment aborts
rather than skipping the Run, because a seed collision means the run plan is not what the Study
declared.

---

## CEV-04 — Experiment Run count matches the Study plan

**Rule:** When `Experiment.status` is `"completed"`, `len(Experiment.run_ids)` MUST equal
`repetitions x len(problem_instance_ids) x len(algorithm_instance_ids)` from the Study.

**Checked:** at the transition to `"completed"`.

**Consequence:** reject the transition, `ValidationError`. An Experiment that cannot reach the
planned Run count ends as `"failed"`, which preserves the Runs it did produce (FR-12); it does
not silently complete with fewer.

---

## CEV-05 — ResultAggregate Run accounting

**Rule:** For each `(problem_instance_id, algorithm_instance_id)` cell, `ResultAggregate.n_runs`
MUST equal the number of Runs in the Experiment for that cell whose status is `"completed"`, and
the count of excluded failed Runs MUST be recorded rather than dropped.

**Checked:** in analysis, when aggregates are computed.

**Consequence:** reject, `ValidationError`. Silently aggregating over an unstated subset of Runs
is the failure that MANIFESTO Principle 29 forbids.

---

## CEV-06 — PerformanceRecord sequence integrity within a Run

**Rule:** Within one Run, `evaluation_number` MUST be strictly increasing across the stored
record sequence, and no value may repeat.

**Checked:** at `save_performance_records()`.

**Consequence:** reject, `ValidationError` for a non-monotonic sequence and
`DuplicateEvaluationError` for a repeat.

---

## CEV-07 — Exactly one end-of-run record per completed Run

**Rule:** A Run with status `"completed"` MUST have exactly one PerformanceRecord whose
`trigger_reason` contains `end_of_run`, and that record's `evaluation_number` MUST equal
`Run.budget_used`.

**Checked:** at the Run's transition to `"completed"`.

**Consequence:** reject the transition, `ValidationError`. This invariant holds regardless of
`max_records_per_run`, because ADR-005 exempts the end-of-run record from the cap.

---

## CEV-08 — Report pairing

**Rule:** Every Experiment with status `"completed"` MUST have exactly two Reports, one with
`type` `"researcher"` and one with `"practitioner"` (FR-20, ADR-019).

**Checked:** in analysis, after report generation.

**Consequence:** reject, `ValidationError`. A single Report cannot satisfy MANIFESTO Principle 25.

---

## CEV-09 — Metric identifiers belong to the taxonomy

**Rule:** Every key of `ResultAggregate.metrics` MUST be a metric identifier defined in
[`../03-metric-taxonomy/`](../03-metric-taxonomy/01-index.md), and the four Standard Reporting
Set metrics MUST all be present.

**Checked:** at `save_result_aggregates()`.

**Consequence:** reject, `UnknownMetricError` for an unknown key, `ValidationError` for a missing
Standard Reporting Set metric.

---

## CEV-10 — Hypothesis references resolve

**Rule:** For every entry of `Study.pre_registered_hypotheses`, `test_type` MUST name a test
defined in
[`../../04-scientific-practice/01-methodology/02-statistical-methodology.md`](../../04-scientific-practice/01-methodology/02-statistical-methodology.md)
§3 or be exactly `none`, and `metric_id` MUST be a metric identifier from the taxonomy
(ADR-021).

**Checked:** at `lock_study()`.

**Consequence:** reject, `ValidationError`.

---

## CEV-11 — Problem Instance diversity floor

**Rule:** A Study's Problem Instance set SHOULD satisfy the diversity floor of ADR-009:
at least five instances, covering at least two dimensionality ranges, including at least one
noisy and one deterministic instance (FR-32, FR-33).

**Checked:** at `lock_study()`.

**Consequence:** warn, naming the axis that falls short. The warning is carried into the Report
limitations section. It is a warning rather than a rejection because a Study deliberately scoped
to one problem class is legitimate as long as the Report says so (FR-30).

---

## CEV-12 — Execution environment is recorded

**Rule:** Every Experiment MUST carry a complete `execution_environment` before any Run is
created: platform, hardware and language version (FR-10).

**Checked:** at `create_experiment()`.

**Consequence:** reject, `ValidationError`. An Experiment without an environment record cannot
support the reproduction procedure in the acceptance test strategy.
