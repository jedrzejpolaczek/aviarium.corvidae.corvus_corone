# ADR-023: PerformanceRecord Stores Both the Raw Value and the Best So Far

<!--
STORY ROLE: Resolves what `objective_value` means. Three contract files gave two
incompatible answers, and every anytime metric reads this field, so the ambiguity
reached the ECDF procedure, the LOCF correctness argument in ADR-003, and the
implemented IOHprofiler exporter.

CONNECTS TO:
  → docs/03-technical-contracts/01-data-format/07-performance-record.md : the schema
  → docs/03-technical-contracts/01-data-format/10-file-formats.md : JSONL and Parquet layouts
  → docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md : COCO and IOH mappings
  → adr-003-anytime-curve-interpolation.md : LOCF is redefined over best_so_far
  → docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md : reconstruction step
-->

---

**Status:** Accepted

**Date:** 2026-09-09

**Deciders:** Core maintainers, methodology lead

---

## Context

Three files in the normative data format directory answer the same question differently.

`07-performance-record.md` types `objective_value` as "Current **best** objective value observed
up to this evaluation", and defines `is_improvement` relative to it. Under that reading the field
is the running best and there is no separate best-so-far.

`11-interoperability-mappings.md` states the opposite in its IOHprofiler mapping table:
"`objective_value` is the *current* eval value; `raw_y` requires *best-so-far*. `best_so_far`
takes precedence." Under that reading the field is the raw value of that one evaluation.

`10-file-formats.md` maps `raw_y` from "`PerformanceRecord.best_so_far` (or `objective_value` if
absent)" and shows JSONL lines carrying both keys, so it treats `best_so_far` as a field that
exists but may be missing. No entity table defines it.

The ambiguity is not contained. ADR-003 rests its argument that LOCF is exact rather than
approximate on the first reading: "best-so-far is constant between improvements". The
ECDF_AREA procedure reconstructs curves from "objective_value of the most recent record". The
implemented exporter hedges with `getattr(rec, "best_so_far", rec.objective_value)`. If the
field holds the raw value, carrying it forward under LOCF propagates a value that may be worse
than the best already seen, and every anytime metric is wrong.

---

## Decision

**A PerformanceRecord carries two required value fields.**

| Field | Meaning |
|---|---|
| `objective_value` | The objective value returned by the evaluation at `evaluation_number`. Raw, not cumulative. |
| `best_so_far` | The best objective value observed in this Run at or before `evaluation_number`, in the direction given by `ProblemInstance.objective.type`. |

`is_improvement` is `true` when this evaluation changed `best_so_far`, subject to
`Study.improvement_epsilon` (ADR-004).

**Anytime reconstruction reads `best_so_far`, never `objective_value`.** ADR-003's LOCF rule and
§1 of the ECDF_AREA procedure are restated over `best_so_far`. LOCF remains exact, because
`best_so_far` is by construction constant between improvements; the argument was always about
that quantity and only the field name was wrong.

`07-performance-record.md` adds `best_so_far` and retypes `objective_value`.
`11-interoperability-mappings.md` keeps its mapping unchanged and loses the contradiction.
`LOSS-COCO-09`, which declared that Corvus stores only the best-so-far and therefore duplicates
COCO column 3 from column 2, is withdrawn: the raw value is now available and the columns differ.

---

## Rationale

Storing only the best-so-far discards information irreversibly, and it is information the
project's own metrics need. `ROBUSTNESS-NOISE_SENSITIVITY` compares performance under matched
noisy and noiseless instances; the per-evaluation spread that makes noise visible lives in the
raw values, not in a monotone envelope. MANIFESTO Principle 12 asks for noise robustness to be
measured, and Principle 14 asks for full curves rather than endpoints. A monotone curve alone
cannot distinguish a problem whose evaluations are stable from one whose evaluations are wildly
noisy but whose running best happens to look identical.

Storing only the raw value is worse still, because every anytime metric would have to recompute
the running best on read, which is cheap but makes the stored record non-self-describing: a
single record could no longer be interpreted without its predecessors. The IOHprofiler mapping
needs `raw_y` per record, so the reconstruction would happen on every export.

Two fields cost one float per record. ADR-005 and ADR-010 are concerned with record count, not
record width, and the Parquet column added here dictionary-compresses poorly but is a plain
float64 that the benchmark in ADR-010 already assumed.

The decision also removes a documented information loss rather than adding one, which is the
direction the ecosystem mappings are supposed to move in.

**Trade-off accepted:** `07-performance-record.md` gains a required field, so any artifact
written before this ADR lacks it. Since no study has been run, there are no such artifacts. The
schema version moves from `0.0.1` to `0.0.2`, which is a pre-release change and owes no migration
guide (ADR-022 sets the pre-release policy, REF-TASK-0039 the version).

*Citation corrected 2026-09-09: the mitigation above cited rule 6 under a `CEV-` prefix. No rule
carries that prefix; `12-cross-entity-validation.md` defines `CV-001` through `CV-023`, and
`CV-006` is the Study-locking rule. The rules that actually constrain the record sequence are `CV-010`
(`evaluation_number` strictly increasing) and `CV-023` (`best_so_far` monotone). The decision is
unchanged; only the pointer was wrong.*

---

## Alternatives Considered

### `objective_value` means best-so-far; no second field

**Description:** Keep `07-performance-record.md` as written and correct the two mapping files.

**Why rejected:** Loses the raw per-evaluation value permanently. The information cannot be
recovered later, and `ROBUSTNESS-NOISE_SENSITIVITY` plus any future analysis of evaluation-level
variance depends on it. It also keeps `LOSS-COCO-09` as a permanent, avoidable export loss.

---

### `objective_value` means the raw value; best-so-far is computed on read

**Description:** Store one field, reconstruct the running best in the Analyzer.

**Why rejected:** Makes a PerformanceRecord meaningless in isolation, which breaks the JSONL
format's property that each line is self-contained (`10-file-formats.md` §3.2), and forces a
sequential pass before any export or metric computation.

---

## Consequences

**Positive:**

- The three contract files stop contradicting each other on the field every anytime metric reads.
- ADR-003's correctness argument becomes true of the field it names.
- The implemented exporter's defensive `getattr` becomes unnecessary.
- `LOSS-COCO-09` is withdrawn; COCO exports carry genuine per-evaluation values.

**Negative / Trade-offs:**

- One extra float per PerformanceRecord.
- The Runner must maintain the running best, which it already does to fire the improvement
  trigger.

**Risks:**

- **Risk:** An implementation writes `best_so_far` inconsistently with `objective_value`, for
  example not resetting it between Runs.
  **Mitigation:** CV-010 and CV-023 already constrain the record sequence within a Run; a companion rule
  that `best_so_far` is monotone in the objective direction is added to `07-performance-record.md`
  validation rules.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/01-data-format/07-performance-record.md` | Schema changed by this ADR |
| `docs/03-technical-contracts/01-data-format/10-file-formats.md` | `best_so_far` becomes a defined field |
| `docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md` | `LOSS-COCO-09` withdrawn |
| `adr-003-anytime-curve-interpolation.md` | LOCF restated over `best_so_far` |
| `docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md` | Reconstruction step restated |
| `adr-024-ecdf-area-integration-domain.md` | The other defect found in the same procedure |
