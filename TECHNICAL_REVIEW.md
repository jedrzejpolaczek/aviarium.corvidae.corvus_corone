# Technical Review — Corvus Corone Documentation

**Reviewed:** 2026-05-15  
**Reviewer:** Claude Sonnet 4.6 (automated static analysis)  
**Scope:** All documentation under `docs/`

---

## Summary Table

| Severity | Count |
|---|---|
| Critical | 6 |
| Major | 11 |
| Minor | 10 |
| **Total** | **27** |

---

## Findings

---

### Finding 1

**Severity:** Critical  
**File:** `docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md` — §4.2.1  
**Issue:** The IOH field-mapping table references a non-existent field `PerformanceRecord.best_so_far` as if it were a distinct field separate from `objective_value`.

> `| PerformanceRecord.best_so_far | raw_y (col 1, float %.10f) | Exact. IOHprofiler raw_y is best-so-far; maps directly. |`
> `| PerformanceRecord.objective_value | Not used | objective_value is the *current* eval value; raw_y requires *best-so-far*. best_so_far takes precedence. |`

The authoritative schema in `docs/03-technical-contracts/01-data-format/07-performance-record.md` defines exactly ONE field `objective_value` and states explicitly: **"STORES `best_so_far`"**. There is no separate `best_so_far` field on `PerformanceRecord`. The description in the IOH mapping treats `objective_value` as the raw per-eval value and `best_so_far` as a different field — which is the opposite of the canonical schema.  
**Fix:** Replace both rows with a single row mapping `PerformanceRecord.objective_value` → `raw_y`, noting it already stores the best-so-far value and no distinction exists. The second row (`objective_value → Not used`) must be removed entirely.

---

### Finding 2

**Severity:** Critical  
**File:** `docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md` — §4.2.1 JSON sidecar table  
**Issue:** The JSON sidecar mapping again references the non-existent field `PerformanceRecord.best_so_far`:

> `| Best PerformanceRecord.best_so_far | scenarios[].runs[].best.y | Min (or max) raw_y across all records in the run. |`

`PerformanceRecord` has no `best_so_far` field. The correct source field is `PerformanceRecord.objective_value` (which stores the running best-so-far by definition).  
**Fix:** Change `PerformanceRecord.best_so_far` to `PerformanceRecord.objective_value` in that row.

---

### Finding 3

**Severity:** Critical  
**File:** `docs/03-technical-contracts/01-data-format/12-cross-entity-validation.md` — CV-009 Quick Reference row  
**Issue:** The Quick Reference table summary for CV-009 says:

> `| [CV-009](#cv-009) | ResultAggregate.n_runs == count of completed Runs for (experiment, problem, algorithm) | ...`

But the authoritative field definition in `docs/03-technical-contracts/01-data-format/08-result-aggregate.md` states `n_runs` counts **all attempted runs (completed + failed)**. The CV-009 rule body (lines 310–311) correctly says "counts all attempted Runs for the cell (both `completed` and `failed`)" — but the Quick Reference row says "count of **completed** Runs", which is wrong and contradicts both the schema definition and the CV-009 body.  
**Fix:** Change the Quick Reference summary to: `ResultAggregate.n_runs == count of all attempted Runs (completed + failed) for (experiment, problem, algorithm)`.

---

### Finding 4

**Severity:** Critical  
**File:** `docs/03-technical-contracts/01-data-format/12-cross-entity-validation.md` — CV-009 error message  
**Issue:** The error message at the end of CV-009 reads:

> `"ResultAggregate.n_runs {n} does not match completed run count {count} for (experiment={eid}, problem={pid}, algorithm={aid})"`

The phrase "completed run count" is wrong — `n_runs` counts ALL runs (completed + failed), not only completed ones. An implementer reading only the error message would implement the check incorrectly (counting only `status="completed"` runs), silently dropping failures.  
**Fix:** Change to: `"ResultAggregate.n_runs {n} does not match attempted run count {count} (completed + failed) for (experiment={eid}, problem={pid}, algorithm={aid})"`

---

### Finding 5

**Severity:** Critical  
**File:** `docs/02-design/02-architecture/05-c4-level4-code/02-shared/03-performance-record.md`  
**Issue:** This C4 code document defines a `PerformanceRecord` dataclass with a field named `best_so_far` as a distinct field from `value` (raw objective):

> `| value | Raw objective value returned by problem.evaluate() — None if status=failed |`  
> `| best_so_far | Running minimum (or maximum, per problem) across all evaluations up to this point |`

And the Mermaid class diagram shows `+best_so_far float` as a separate attribute alongside `+value float`.

This directly contradicts the canonical schema in `docs/03-technical-contracts/01-data-format/07-performance-record.md`, which defines a single `objective_value` field that stores best_so_far. The C4 document also uses entirely different field names: `iteration` (not `evaluation_number`), `wall_time_ms` (not `elapsed_time`), `candidate` (not `current_solution`), and additional fields `budget`, `timestamp`, `status`, `error` that do not appear in the canonical schema.

This is a deeply divergent parallel schema that would produce an incompatible implementation if followed.  
**Fix:** Rewrite this document to use the canonical field names from `07-performance-record.md`: `id`, `run_id`, `evaluation_number`, `elapsed_time`, `objective_value`, `current_solution`, `is_improvement`, `trigger_reason`. Remove `best_so_far`, `value`, `iteration`, `budget`, `wall_time_ms`, `candidate`, `timestamp`, `status`, `error`.

---

### Finding 6

**Severity:** Critical  
**File:** `docs/02-design/02-architecture/04-c4-leve3-components/03-experiment-runner/05-performance-recorder.md`  
**Issue:** This C3 document describes `PerformanceRecord` with the same divergent field set as Finding 5:

> `assembles a PerformanceRecord dataclass from the observation data. Fields: run_id, experiment_id, algorithm_id, problem_id, iteration, budget, value, best_so_far, candidate, wall_time_ms, timestamp, status, error.`

The canonical schema (`07-performance-record.md`) has none of `iteration`, `budget`, `value` (as a distinct raw-eval field), `best_so_far` (as a separate field), `candidate`, `wall_time_ms`, `timestamp`, `status`, `error`. These invented field names conflict with the technical contract and would produce an incompatible implementation.  
**Fix:** Replace the field list with the canonical fields from `07-performance-record.md`: `id`, `run_id`, `evaluation_number`, `elapsed_time`, `objective_value`, `current_solution`, `is_improvement`, `trigger_reason`.

---

### Finding 7

**Severity:** Major  
**File:** `docs/03-technical-contracts/01-data-format/01-index.md` — Mermaid entity overview diagram  
**Issue:** The `Run` node in the entity diagram reads:

> `R["**Run**\nid · seed · status\nproblem_id · algorithm_id"]`

The canonical field names (from `06-run.md`) are `problem_instance_id` and `algorithm_instance_id`, not `problem_id` and `algorithm_id`. This abbreviated naming in a canonical reference document could lead implementers to use incorrect field names.  
**Fix:** Change the node to: `R["**Run**\nid · seed · status\nproblem_instance_id · algorithm_instance_id"]`

---

### Finding 8

**Severity:** Major  
**File:** `docs/02-design/01-software-requirement-specification/02-use-cases/08-uc-07.md` — Connects to section  
**Issue:** References a non-existent path:

> `docs/02-design/02-architecture/02-c1-context.md — Learner actor definition (REF-TASK-0025)`

No file exists at `docs/02-design/02-architecture/02-c1-context.md`. The actual file is at `docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md`.  
**Fix:** Replace `docs/02-design/02-architecture/02-c1-context.md` with `docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md`

---

### Finding 9

**Severity:** Major  
**File:** `docs/02-design/01-software-requirement-specification/02-use-cases/10-uc-09.md` — Connects to section  
**Issue:** Same stale path as Finding 8:

> `docs/02-design/02-architecture/02-c1-context.md — Learner actor definition (REF-TASK-0025)`

**Fix:** Replace with `docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md`

---

### Finding 10

**Severity:** Major  
**File:** `docs/03-technical-contracts/01-data-format/02-problem-instance.md` — Index backlink  
**Issue:** The backlink reads:

> `> Index: [01-data-format.md](01-data-format.md)`

The actual index file is named `01-index.md`, not `01-data-format.md`. This is a broken relative link.  
**Fix:** Change to `> Index: [01-index.md](01-index.md)`

---

### Finding 11

**Severity:** Major  
**File:** `docs/03-technical-contracts/01-data-format/05-experiment.md` — Index backlink  
**Issue:** Same broken backlink:

> `> Index: [01-data-format.md](01-data-format.md)`

**Fix:** Change to `> Index: [01-index.md](01-index.md)`

---

### Finding 12

**Severity:** Major  
**File:** `docs/03-technical-contracts/01-data-format/06-run.md` — Index backlink  
**Issue:** Same broken backlink:

> `> Index: [01-data-format.md](01-data-format.md)`

**Fix:** Change to `> Index: [01-index.md](01-index.md)`

---

### Finding 13

**Severity:** Major  
**File:** `docs/03-technical-contracts/01-data-format/09-report.md` — Index backlink  
**Issue:** Same broken backlink:

> `> Index: [01-data-format.md](01-data-format.md)`

**Fix:** Change to `> Index: [01-index.md](01-index.md)`

---

### Finding 14

**Severity:** Major  
**File:** `docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md` — Index backlink  
**Issue:** Same broken backlink:

> `> Index: [01-data-format.md](01-data-format.md)`

**Fix:** Change to `> Index: [01-index.md](01-index.md)`

---

### Finding 15

**Severity:** Major  
**File:** `docs/03-technical-contracts/02-interface-contracts/02-problem-interface.md` — Index backlink  
**Issue:** The backlink reads:

> `> Index: [01-interface-contracts.md](01-interface-contracts.md)`

The actual index file is named `01-index.md`, not `01-interface-contracts.md`. This is a broken link.  
**Fix:** Change to `> Index: [01-index.md](01-index.md)`

---

### Finding 16

**Severity:** Major  
**File:** `docs/02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md` — Option A, "Under what conditions reconsidered"  
**Issue:** The text contains a stale open TODO for a task that has since been resolved:

> `If a dedicated high-volume binary format for PerformanceRecords (Parquet/HDF5, TODO: REF-TASK-0024) makes the storage cost acceptable.`

ADR-010 (accepted 2026-03-25) resolves REF-TASK-0024 by selecting Parquet/snappy. Leaving the open TODO creates the false impression that this architectural question is still open.  
**Fix:** Replace with: `If a dedicated high-volume binary format for PerformanceRecords (resolved: ADR-010 chose Parquet/snappy) makes a full-trace mode practical.`

---

### Finding 17

**Severity:** Major  
**File:** `docs/02-design/01-software-requirement-specification/07-acceptance-test-strategy/01-acceptance-test-strategy.md` — Reproducibility Test Procedure, Steps 1c and 3b  
**Issue:** The test procedure captures and asserts a field `best_so_far` that does not exist on `PerformanceRecord`:

> `all PerformanceRecord sequences per Run (evaluation_number, objective_value, best_so_far)` (Step 1c)  
> `assert PerformanceRecord sequences are element-wise equal: evaluation_number, objective_value, best_so_far` (Step 3b)

`PerformanceRecord` has no `best_so_far` field (see Finding 5 and Finding 6). Any test implemented from this spec would fail to reference an existing attribute.  
**Fix:** Remove `best_so_far` from both field lists. The correct fields to assert are: `evaluation_number`, `objective_value`, `elapsed_time`, `is_improvement`, `trigger_reason`.

---

### Finding 18

**Severity:** Major  
**File:** `docs/02-design/02-architecture/04-c4-leve3-components/04-analysis-engine/02-metric-dispatcher.md`  
**Issue:** The metric dispatcher references a metric ID `AUC-CONVERGENCE` that does not exist in the metric taxonomy:

> `AUC-CONVERGENCE: area under the convergence curve (trapezoidal integration of best_so_far over evaluations).`

The canonical equivalent in `docs/03-technical-contracts/03-metric-taxonomy/` is `ANYTIME-ECDF_AREA`. No metric named `AUC-CONVERGENCE` is defined anywhere in the taxonomy. Additionally this line again references `best_so_far` as a PerformanceRecord field (see Finding 5).  
**Fix:** Replace `AUC-CONVERGENCE` with `ANYTIME-ECDF_AREA` and `best_so_far` with `objective_value`. Align the description with the canonical metric definition in `07-anytime-ecdf-area.md`.

---

### Finding 19

**Severity:** Minor  
**File:** `docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md` — `compute_metrics` postcondition  
**Issue:** The postcondition reads:

> `ResultAggregate.n_runs equals the count of contributing Runs per group`

"Contributing Runs" is ambiguous — it implies only successful Runs. Per the canonical schema, `n_runs` counts ALL attempted Runs (completed + failed). The `n_successful` sub-field within `AggregateValue` counts Runs that contributed to a specific metric.  
**Fix:** Change to: `ResultAggregate.n_runs equals the count of all attempted Runs (completed + failed) per group; AggregateValue.n_successful equals the count of Runs that contributed to each metric.`

---

### Finding 20

**Severity:** Minor  
**File:** `docs/03-technical-contracts/03-metric-taxonomy/01-index.md` — open TODO  
**Issue:**

> `**TODO: REF-TASK-0014** — Review and extend metric definitions once the first real studies are conducted.`

This open, unfulfilled TODO in the metric taxonomy index signals incomplete work with no stated deadline or owner.  
**Fix:** Either complete the task (add domain-specific metrics as described) and remove the marker, or move the item to ROADMAP.md with a target milestone and remove the inline TODO.

---

### Finding 21

**Severity:** Minor  
**File:** `docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md` — NFR section  
**Issue:**

> `**TODO: REF-TASK-0010** — Add measurable pass/fail thresholds to each NFR.`

Without measurable thresholds, no NFR can be objectively accepted or rejected in testing. This has been open since at least SRS version 0.4.  
**Fix:** Either add measurable thresholds to each NFR file (correct fix), or escalate with a hard deadline and owner in ROADMAP, and note the unresolved state in the SRS version field.

---

### Finding 22

**Severity:** Minor  
**File:** `docs/02-design/02-architecture/05-c4-level4-code/06-results-store/02-repository-protocol.md` — canonical directory tree  
**Issue:** The directory tree in this C4 document diverges from the authoritative layout in `docs/03-technical-contracts/01-data-format/10-file-formats.md` §3.2. The C4 document shows:

```
{results_dir}/
  studies/{study_id}/study.json
  experiments/{experiment_id}/experiment.json
  runs/{run_id}/
    seed.json            ← extra; not in §3.2
    run.log              ← extra; not in §3.2
```

The §3.2 authoritative layout has no `seed.json` or `run.log` in run directories, and uses a flat top-level structure (`problems/`, `algorithms/`, `studies/`, `experiments/`, `runs/`, `aggregates/`, `reports/`) not a nested `studies/{study_id}/` layout.  
**Fix:** Align the C4 directory tree with `10-file-formats.md` §3.2, or explicitly label it as an illustrative simplified view rather than the normative structure.

---

### Finding 23

**Severity:** Minor  
**File:** `docs/03-technical-contracts/01-data-format/01-index.md` — Contents table  
**Issue:**

> `| §6 Schema Versioning | 13-schema-versioning.md | 🚧 Pending |`

The file `13-schema-versioning.md` contains substantive content, yet the status is `🚧 Pending`. This is misleading about the state of that section.  
**Fix:** Read `13-schema-versioning.md` and update the status to `✅` if complete, or identify and describe what is genuinely missing for the `🚧` to be accurate.

---

### Finding 24

**Severity:** Minor  
**File:** `docs/02-design/01-software-requirement-specification/02-use-cases/08-uc-07.md` and `09-uc-08.md`, `10-uc-09.md`, `11-uc-10.md`, `12-uc-11.md` — open REF-TASK / IMPL markers  
**Issue:** These UC files contain bare open markers such as `REF-TASK-0027`, `IMPL-044`, `REF-TASK-0028`, `IMPL-048`, `REF-TASK-0029`, `IMPL-045`, `REF-TASK-0030`, `IMPL-046` with no status annotation. The acceptance test strategy acknowledges Learner actor FRs are deferred, but these bare markers without `🚧` or `✅` labels are inconsistent with the convention used elsewhere in the documentation.  
**Fix:** Add `🚧 Pending` annotations to all bare open task/implementation markers in UC-07 through UC-11.

---

### Finding 25

**Severity:** Minor  
**File:** `docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md` — Risks section  
**Issue:** The third risk's mitigation note reads:

> `Mitigation: The PerformanceRecord bulk storage format (e.g., Parquet, HDF5) is a separate ADR decision.`

ADR-010 (2026-03-25) already made this decision (Parquet/snappy). Presenting both Parquet and HDF5 as alternatives creates the false impression the choice is still open.  
**Fix:** Change to: `Resolved by ADR-010 (2026-03-25): Parquet/snappy selected as the secondary bulk format. The primary JSON schema remains canonical.`

---

### Finding 26

**Severity:** Minor  
**File:** Multiple files in `docs/05-community/` and comment blocks across the project  
**Issue:** CONNECTS TO sections and comment blocks in many files use shorthand paths like `specs/interface-contracts.md`, `specs/data-format.md`, `specs/metric-taxonomy.md` that do not correspond to any real file. These appear in comment blocks (not rendered Markdown links), but mislead contributors reading the source. Key affected files: `docs/05-community/01-contribution-guide.md`, `docs/05-community/02-versioning-governance.md`, `docs/03-technical-contracts/02-interface-contracts/01-index.md`, `docs/03-technical-contracts/01-data-format/01-index.md`.

| Stale shorthand | Correct canonical path |
|---|---|
| `specs/interface-contracts.md` | `docs/03-technical-contracts/02-interface-contracts/01-index.md` |
| `specs/data-format.md` | `docs/03-technical-contracts/01-data-format/01-index.md` |
| `specs/metric-taxonomy.md` | `docs/03-technical-contracts/03-metric-taxonomy/01-index.md` |

**Fix:** Do a project-wide search-and-replace for each stale shorthand and update to the canonical path.

---

### Finding 27

**Severity:** Minor  
**File:** `docs/GLOSSARY.md` and `docs/ROADMAP.md`  
**Issue:** References to `docs/02-design/01-software-requirement-specification/SRS.md` appear in comment blocks (GLOSSARY lines 398, 430; ROADMAP). The actual file is at `docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md`. These are not rendered Markdown links but represent stale paths that mislead contributors following the cross-references.  
**Fix:** Update all `SRS.md` shorthand references to `docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md`.

---

*Review complete. Total findings: 27 (6 Critical, 11 Major, 10 Minor).*
