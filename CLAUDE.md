# CLAUDE.md — Project Invariants for aviarium.corvidae.corvus_corone

Loaded automatically at the start of every session. It holds only what a reader
**cannot derive from the repository itself**: the working method, the decisions that
reverse what older documents still say, and the authorities to consult before writing.

Facts that *are* derivable — file paths, requirement wording, schema fields — are
deliberately not restated here. An earlier version of this file carried tables of
them, and every one of those tables had drifted: it still described an eight-field
Performance Record, a `specs/` layout that no longer exists, and Learner requirements
under identifiers that had been reassigned. A second copy of a specification is a
second thing to keep true. Read the source, or run the checker.

---

## 1. This is a documentation-first project

The documentation is the primary work product; the code in `packages/` follows it and
is expendable where the two disagree. A change that alters behaviour is not finished
until the contract that governs it says so. Do not "fix" a document to match the code.

## 2. Documentation validation

Before reporting findings from a docs review, run the checker:

```
python scripts/check_docs.py
```

Six checks: link resolution, cited-identifier existence, duplicate definitions,
uncontracted vocabulary (ADR-012), filenames named in prose, and requirement labels
that describe a different requirement. All six derive their expectations from the tree
and from the requirement files — nothing is hardcoded. It runs in CI and in the
pre-push hook (`make install-hooks`).

Two opt-out markers exist, both deliberate and both rare:

| Marker | Scope | Means |
|---|---|---|
| `<!-- check-docs: allow-undefined -->` | whole file | a template or a deferred component, whose identifiers are illustrative |
| `<!-- check-docs: planned -->` | one line | names a deliverable that does not exist yet (roadmap entries) |

## 3. Documentation layer normativity (ADR-012)

Precedence, highest first:

```
MANIFESTO → SRS → ADR → 03-technical-contracts → C2/C3/C4 → code
```

`03-technical-contracts/` is **normative**: it is where boundary vocabulary — types,
field names, exception names, metric identifiers — is defined. The C2/C3/C4 layers are
**descriptive**: they may cite that vocabulary but must never coin any. Check 4
enforces this. When a component needs a term the contracts do not have, the contract
is what changes.

## 4. ADR practice

ADRs live in `docs/02-design/02-architecture/01-adr/`. An accepted ADR is closed: it is
never edited to reflect a new decision, only superseded by a later one that names it.
When two documents conflict, the higher layer and the later ADR win together.

**Decisions that reverse text still present in older documents** — check these before
trusting anything you read:

| ADR | Reverses |
|---|---|
| ADR-020 | entities are immutable; no `version` parameter, lineage runs through `superseded_by` |
| ADR-022 | AGPL-3.0-or-later; supersedes the licensing clauses of ADR-006, and inverts its dependency policy |
| ADR-023 | `objective_value` is the **raw** per-evaluation result; the running best is a separate `best_so_far` field, and that is what anytime metrics reconstruct |
| ADR-024 | the ECDF_AREA integration domain; the worked reference value is 0.4375, not 0.21875 |
| ADR-025 | a later ADR may supersede *part* of an earlier one; the superseded ADR's Status line says so, and that line is the only edit a closed ADR may receive |
| ADR-026 | `03-technical-contracts/` is not quite the only place that defines boundary vocabulary: `02-cli-spec.md` (CLI surface), `03-report-format-spec.md` (report sections) and `02-statistical-methodology.md` (`VIZ-L1-NN`) are authoritative for those surfaces and no others |

Partial supersessions currently in force, in addition to ADR-006's licensing clauses:
the Parquet column table of ADR-010 (ADR-023 added `best_so_far`).

## 5. Vocabulary that is easy to get wrong

- The optimizer interface is **`suggest` / `observe`**, not `ask` / `tell`.
- Exception names come from the cross-cutting contract (ADR-015). Do not invent one;
  if the taxonomy has no fitting member, extend the taxonomy.
- The CLI surface is authoritative in `02-cli-spec.md` (ADR-016) and mirrors the Python
  facade rather than diverging from it.

## 6. Scope and release

`01-SRS.md` §1.4 (V1 Release Scope) is the authority on what V1 contains, including the
capability boundaries B-01..B-08. `docs/ROADMAP.md` sequences the work. A requirement
marked `[DEFERRED]` is not a gap — it is a decision, and reporting it as an omission is
a finding against the reviewer, not the project.

## 7. Working agreements

- **Branching.** Every commit goes to `dev` first; `main` receives merges from `dev`,
  and `dev` is not deleted.
- **Python 3.10.** Not a floor to be raised opportunistically.
- **Issues.** GitHub issues are the only intake channel.
- **`papers/`.** PDFs are not redistributable and are gitignored; `papers/README.md`
  carries the citations instead.
