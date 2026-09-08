# ADR-012: Documentation Layer Normativity and Precedence

<!-- check-docs: allow-undefined -->

<!--
STORY ROLE: Establishes which documentation layer wins when two documents disagree.
Without this rule, every layer is free to define the same thing differently, and the
project accumulates parallel specifications of the same component. This ADR is the
constitutional rule that makes the other documents checkable against each other.

CONNECTS TO:
  → docs/03-technical-contracts/ : declared normative for identifiers and signatures
  → docs/02-design/01-software-requirement-specification/ : declared normative for requirement IDs
  → docs/02-design/02-architecture/03-c4-leve2-containers/ : declared descriptive
  → docs/02-design/02-architecture/05-c4-level4-code/ : declared descriptive
  → docs/README.md : restates the precedence order for readers
-->

---

**Status:** Accepted

**Date:** 2026-09-08

**Deciders:** Core maintainers, technical lead

---

## Context

The project is written documentation-first: the architecture and contract documents are
produced before the implementation, and the implementation exists partly to test whether
the documents are implementable. This makes the documentation the primary work product of
the current phase, and its internal consistency the acceptance criterion for that phase.

An audit of the corpus on 2026-09-08 found that the same subject is specified more than
once, in incompatible ways, across layers that were each written independently:

| Subject | Specification A | Specification B |
|---|---|---|
| `LocalFileRepository` | `RepositoryFactory` with seven domain repositories (`02-interface-contracts/06-repository-interface.md`) | Filesystem path resolver with `study_dir()`, `run_dir()`, `parquet_path()` (`04-c4-leve3-components/05-results-store/02-local-file-repository.md`) |
| `cc.run()` | Takes `study_id: str` (`04-public-api-contract.md`) | Takes `study_config: dict \| StudyConfig` (`04-c4-leve3-components/10-public-api-cli/02-api-facade.md`) |
| CLI surface | Positional arguments, exit codes 0–10 (`03-c4-leve2-containers/02-cli-spec.md`) | `--config`, `--json`, `resume`, `viz`, exit codes 1–2 (`04-c4-leve3-components/10-public-api-cli/03-cli-command-group.md`) |
| Metric identifiers | Six IDs, permanent once published (`03-metric-taxonomy/`) | `ERT`, `AUC-CONVERGENCE` (`04-c4-leve3-components/04-analysis-engine/02-metric-dispatcher.md`) |
| Storage technology | JSON entity files plus JSONL and Parquet (ADR-010, `01-data-format/10-file-formats.md`) | "SQLite (structured entity records)" (`03-c4-leve2-containers/12-results-store.md`) |
| Requirement identifiers | `FR-01`..`FR-26` (SRS) | `FR-R-01`, `FR-A-02`, `FR-S-04` and 32 others, defined nowhere (30 C3 files) |

The `Repository` protocol in `05-c4-level4-code/06-results-store/02-repository-protocol.md`
additionally defines a path-resolution interface while citing ADR-001 as its justification,
although ADR-001 states that the directory layout is an implementation detail that consumers
must never traverse.

These are not editing mistakes that can be fixed once. They are the predictable result of
having no rule about which layer may define what. Without such a rule, each new document
reasonably assumes it must specify the component it describes, and a seventh conflicting CLI
definition is as likely as the four that already exist.

The constraint on the solution is that the layers must keep earning their place. The C2, C3
and C4 documents carry genuine information that the contracts do not: how responsibilities
are grouped into components, why a component exists, what depends on what. Deleting them
would lose that. What must be removed is only their licence to invent.

---

## Decision

**A single precedence order governs the entire corpus:**

```
MANIFESTO  →  SRS  →  ADR  →  03-technical-contracts/  →  C2 / C3 / C4  →  code
```

When two documents disagree, the one earlier in this order wins, and the later document is
the one that gets corrected.

**`docs/03-technical-contracts/` is normative.** It is the only place in the corpus where the
following may be *defined*: identifiers, method and function signatures, field names, field
types, enumeration values, error and exception classes, metric identifiers, and file formats.

**`docs/02-design/01-software-requirement-specification/` is normative for requirement
identifiers.** `FR-*`, `NFR-*`, `UC-*` and `CONST-*` may only be *cited* elsewhere, never
coined elsewhere.

**`docs/02-design/02-architecture/01-adr/` is normative for decisions.** Where a contract and
an ADR disagree, the ADR wins and the contract is corrected.

**The C2, C3 and C4 layers are descriptive.** They explain how the normative material is
grouped into containers and components and why those boundaries were drawn. They MUST NOT
introduce any identifier, signature, field, enumeration value or format that is not already
present in `03-technical-contracts/`, and they MUST NOT cite a requirement identifier that
the SRS does not define.

**Changing normative material requires changing the normative document first**, in the same
change that updates the descriptive layer. A descriptive document is never the place where a
new design decision first appears.

**A conflict between a descriptive document and a normative one is a defect in the descriptive
document.** It is resolved by editing that document, never by editing the contract to match it.

---

## Rationale

### Why the contracts win rather than C3

Three reasons, in order of weight.

The contracts are internally the most consistent layer in the corpus. The audit found the
error taxonomy in `02-interface-contracts/07-cross-cutting-contracts.md` implemented
name-for-name by `packages/corvus-corone-lib/src/corvus_corone/exceptions.py`, and the file
format specification in `01-data-format/10-file-formats.md` matching the module layout that
was actually built. Choosing the layer that already agrees with the working code minimises
the size of the correction.

The contracts are the layer that external contributors must obey. An algorithm author
implements the Algorithm Interface; they do not implement a C3 component. Making the layer
that faces contributors normative aligns authority with obligation.

The contracts are the smaller surface. Thirty-one files against seventy-one, and one
definition per subject rather than one per describing document.

### Why the descriptive layers are kept rather than deleted

An earlier proposal was to delete `05-c4-level4-code/` and consolidate the forty-five C3
component files into eleven. That treats the symptom. The C4 layer contradicts ADR-001 not
because it is too detailed but because nothing forbade it from redefining `Repository`. With
this ADR in force, the same layer can carry the same detail without being able to diverge,
because any statement it makes must already exist upstream.

Consolidation may still be worthwhile for maintenance cost. That is now a separate,
independent decision rather than a repair.

### Why this is checkable by machine

The rule was chosen in a form a script can enforce. Every identifier appearing in a code block
in C2, C3 or C4 must appear in `03-technical-contracts/`; every requirement identifier cited
anywhere must appear in the SRS. Both are set-membership tests over the corpus. A rule that
depended on human judgement about what counts as a contradiction would decay the same way the
GLOSSARY maintenance rule decayed.

### Trade-offs accepted

Writing a C3 component document now sometimes requires a contract change first, which is
slower than writing the component document alone. That cost is the point: it is the moment at
which a design decision becomes visible and reviewable instead of being smuggled in as an
implementation detail of a description.

The rule also freezes some existing prose. Several C3 documents contain signatures that are
plausible and useful but absent from the contracts. Each must now either be promoted into a
contract or removed. That is one-time work, quantified in the Consequences section.

---

## Alternatives Considered

### No precedence rule; resolve conflicts case by case

**Description:** Keep all layers equally authoritative and fix contradictions as they are found.

**Why rejected:** This is the status quo, and it produced four CLI definitions, two
`LocalFileRepository` interfaces and thirty-five undefined requirement identifiers. Case-by-case
resolution also has no stopping condition: nothing prevents the next document from adding a
fifth CLI.

**Under what conditions reconsidered:** Never for this corpus. A project small enough for one
author to hold in memory does not need the rule, but this corpus is already too large for that,
which is what the audit demonstrated.

---

### Make C3 normative and demote the contracts

**Description:** Treat the component documents as the specification, since they are closer to
the code that will be written.

**Why rejected:** The C3 layer disagrees with the working implementation in every case examined,
uses a requirement identifier scheme that does not exist, and duplicates definitions across
forty-five files. Choosing it would maximise rather than minimise the correction, and would
break the contracts that external contributors are being asked to implement.

---

### Delete the C2, C3 and C4 layers

**Description:** Keep only MANIFESTO, SRS, ADRs and contracts.

**Why rejected:** Discards the grouping and rationale information that those layers carry and
that the contracts deliberately do not: which component owns which responsibility, and why the
boundaries fall where they do. The problem was never that these documents exist; it was that
nothing constrained them.

---

## Consequences

**Positive:**

- Every documented conflict listed in the Context section acquires a mechanical resolution
  rule, without further design discussion.
- The correction criterion becomes "remove from the descriptive layer anything that introduces
  new material", which any contributor can apply, rather than "decide which of two designs is
  better", which only the author can.
- The rule is enforceable in CI as a set-membership test, so recurrence is prevented rather
  than periodically repaired.
- New contributors gain an unambiguous answer to "where is this defined", which is a
  prerequisite for opening the repository.

**Negative / Trade-offs:**

- Adding a genuinely new component behaviour now takes two edits instead of one.
- The existing corpus needs a one-time pass. From the audit: thirty-five undefined requirement
  identifiers across thirty C3 files, two metric identifiers, one storage technology claim, one
  statistical test, one CLI definition set, one API facade surface, and one `Repository`
  protocol must each be either promoted into a contract or removed.
- Some C3 material is better than its contract counterpart and will need promotion rather than
  deletion. Judging which is which is the one part of the cleanup that is not mechanical.

**Risks:**

- **Risk:** The rule is stated and then not enforced, exactly as the GLOSSARY maintenance rule
  was stated and not enforced.
  **Mitigation:** The vocabulary check in `scripts/check_docs.py`, run by CI and by the
  pre-push hook. Until that check exists, this ADR is a convention rather than a rule.
- **Risk:** Contributors treat the descriptive layers as unimportant because they are not
  normative, and let them rot.
  **Mitigation:** Descriptive does not mean optional. The link and identifier checks apply to
  every document in the corpus regardless of layer.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/` | Declared normative for identifiers, signatures, fields, enumerations, errors and formats |
| `docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md` | Declared normative for requirement identifiers and, in §1, for release scope |
| `docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md` | The ADR that `05-c4-level4-code/06-results-store/02-repository-protocol.md` contradicts; that contradiction is resolved by this rule |
| `docs/02-design/02-architecture/03-c4-leve2-containers/` | Declared descriptive |
| `docs/02-design/02-architecture/05-c4-level4-code/` | Declared descriptive |
| `docs/README.md` | Restates the precedence order as reading guidance |
| `audit-2026-09-08.md` | The audit that established the conflict inventory in the Context section |
