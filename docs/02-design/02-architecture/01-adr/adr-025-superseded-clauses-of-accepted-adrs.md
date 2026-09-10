# ADR-025: Recording Clauses of Accepted ADRs That a Later ADR Has Superseded

<!--
STORY ROLE: Fixes a hole in the ADR practice itself. An accepted ADR is never edited, only
superseded — but the corpus had no way to record that a later ADR superseded *part* of an
earlier one, so two accepted ADRs could contradict each other with nothing saying which wins.
This ADR states the convention and applies it to the two cases that already exist.

CONNECTS TO:
  → adr-010-bulk-performance-record-format.md : column table partially superseded
  → adr-023-performance-record-value-fields.md : the ADR that superseded it
  → adr-006-python-version-and-platform-constraints.md : the precedent this generalises
  → adr-022-agpl-licence-and-dependency-policy.md : the ADR that superseded ADR-006's clauses
  → docs/03-technical-contracts/01-data-format/10-file-formats.md : the contract the hole reached
-->

---

**Status:** Accepted

**Date:** 2026-09-09

**Deciders:** Core maintainers, technical lead

---

## Context

ADR practice in this project has one rule about amendment: *an accepted ADR is closed. It is
never edited to reflect a new decision, only superseded by a later one that names it.* The rule
is right — an ADR is a record of what was decided and why, at a moment, and editing it destroys
the record.

The rule has a hole. It handles whole-ADR supersession, and every ADR in the corpus is written
as though supersession is all-or-nothing. Most real supersessions are partial: a later decision
invalidates one clause of an earlier ADR and leaves the rest standing.

Two such cases already exist, and they were handled two different ways.

**ADR-006 and ADR-022, handled well.** ADR-022 replaced the licence and inverted the dependency
policy. Someone edited ADR-006's Status line to read *"Accepted; the licensing clauses are
superseded by ADR-022"*, which is technically an edit to a closed ADR but is the smallest
possible one and does not touch the decision text. A reader of ADR-006 is warned before reading
the clause that no longer holds. `CLAUDE.md` also lists it.

**ADR-010 and ADR-023, handled not at all.** ADR-023 split the PerformanceRecord value field in
two: `objective_value` becomes the raw result of one evaluation, and the new `best_so_far` holds
the running best. ADR-010 fixes the Parquet column schema for the bulk format, was accepted
before ADR-023, and therefore lists `objective_value` described as *"Best objective value at this
evaluation"* and has no `best_so_far` column at all.

ADR-023 enumerates the documents it corrects. ADR-010 is not among them, and neither is
`10-file-formats.md`, which reproduces the column table. So the contract kept a column list that
could not satisfy the round-trip invariant stated a few lines below it in the same file: a record
read back from Parquet must be identical to the same record read from JSON Lines, and §2.6 makes
`best_so_far` required. The JSON Lines example in that file carried the field. The Parquet table
did not.

This was found by the 2026-09-09 consistency audit rather than by any gate. `check_docs.py`
cannot see it: both documents use only contracted names, and nothing in the corpus expresses
"these two accepted ADRs disagree".

A third instance of the same shape, smaller: ADR-009 and ADR-023 both cited cross-entity rules
under a `CEV-` prefix that no rule carries. That is a citation error rather than a supersession,
and it was corrected in place with a dated note; it is mentioned here because it came from the
same absence of any convention for annotating a closed ADR.

---

## Decision

**A later ADR may supersede part of an earlier one, and the supersession is recorded in three
places.**

1. **The superseding ADR names the clause.** Its Related Documents table gains a row for the
   earlier ADR with the relationship stated at clause granularity — not "supersedes ADR-010" but
   "supersedes the column table of ADR-010". Where the superseding ADR is already accepted and
   omitted the row, this ADR supplies it on its behalf, as below.

2. **The superseded ADR's Status line says so.** The form ADR-006 already uses is the standard:
   `**Status:** Accepted; the <named> clauses are superseded by ADR-NNN`. This is the only edit
   permitted to a closed ADR, it touches no decision text, and it exists so that a reader who
   opens the ADR directly is warned before reading a clause that no longer holds.

3. **`CLAUDE.md` lists it** in the table of decisions that reverse text still present in older
   documents, which is what a reader consults before trusting anything in the corpus.

**Applying it to ADR-010.** The column table of ADR-010 is superseded by ADR-023 in one respect:
the record carries two float value fields, not one. `objective_value` keeps its column and
becomes the raw per-evaluation result; `best_so_far` gains a column of the same Arrow type. Every
other element of ADR-010 — Parquet with snappy over HDF5, the row-group size of 500, the 1,000
record threshold, the `.jsonl` file remaining the source of truth, `pyarrow` as the library —
stands unchanged. The benchmark that justified the format measured record count and column
compressibility, and one additional plain `float64` column changes neither conclusion; ADR-023
said as much when it accepted the cost.

`10-file-formats.md` already carries the corrected column table.

**`pyarrow` stays undeclared until IMPL-022.** ADR-010 makes it a core dependency and no
`pyproject.toml` declares it. That is a real gap between the decision and the build, and it is
deliberately left open: nothing imports `pyarrow` until the bulk writer exists, and adding an
unused runtime dependency so that a file agrees with a document is the wrong direction of fit.
The obligation is on IMPL-022, which is where the import appears.

---

## Rationale

**Why not simply allow editing a closed ADR.** Because the record is the point. An ADR answers
"why does the system look like this", and a reader who finds a coherent, edited document cannot
tell which parts were believed at the time and which were retrofitted. The value of the ADR
series is that it is a history, and a history that is silently corrected is a worse history than
one with visible amendments.

**Why the Status line rather than a note in the body.** A reader who arrives at ADR-010 from a
search result lands somewhere in the middle. The Status line is the one field every ADR has in
the same place, above the fold, and it is already where ADR-006 carries this information. Putting
the warning next to the affected clause would be more precise and would be missed by anyone who
enters the document elsewhere.

**Why three places rather than one.** Each serves a different reader. The superseding ADR's table
serves someone tracing forward from the new decision; the Status line serves someone who opened
the old one; `CLAUDE.md` serves someone about to trust a document they have not opened yet. The
audit found the ADR-010 case precisely because the third of these lists ADR-020, ADR-022, ADR-023
and ADR-024 and the reader could compare that list against what the documents said.

**Why this could not be left as convention.** It was convention. ADR-006 followed it and ADR-023
did not, which is what an unwritten convention produces. The cost of writing it down is this
document.

**Trade-offs accepted:** the Status line of a closed ADR becomes mutable, which is a narrow
exception to "never edited" and has to stay narrow. The rule is that the Status line may gain a
supersession clause and nothing else — no rewording of the decision, no correction of the
reasoning, no updating of examples. A supersession that cannot be expressed in a Status line
clause is not a partial supersession; it is a whole one, and needs a new ADR that replaces the
old outright.

---

## Alternatives Considered

### Leave partial supersession implicit and rely on the precedence rule

**Description:** ADR-012 already says the later ADR wins. A reader who finds two accepted ADRs
disagreeing can apply that rule and move on.

**Why rejected:** the rule only helps a reader who has noticed the disagreement. The ADR-010
case shows what happens otherwise: the contract reproduced the superseded column table, the
implementation would have been written from the contract, and the round-trip test in the same
file would have failed against a specification the implementer had followed correctly. Precedence
resolves conflicts; it does not surface them.

### Deprecate the whole ADR and reissue it

**Description:** when any clause of an ADR is superseded, replace the entire ADR with a new one
carrying the surviving clauses plus the change.

**Why rejected:** it destroys the record in a different way. ADR-010's rationale is a benchmark
with measured numbers and a documented HDF5 rejection; reissuing it would either copy that
verbatim, which duplicates rather than supersedes, or drop it, which loses the reason the format
was chosen. It also scales badly: ADR-023 touched clauses of ADR-003 and ADR-010, so one decision
would have forced two reissues.

### A separate supersession register file

**Description:** one document listing every superseded clause across the corpus.

**Why rejected:** a second copy of information that has to be kept true, which is the failure
mode this project has already been bitten by. `CLAUDE.md` carries a short list for the reader's
first orientation, but the authority stays in the two ADRs themselves.

---

## Consequences

**Positive:**

- Two accepted ADRs can no longer disagree without at least one of them saying so.
- The ADR-010 case is closed: the contract, the ADR pair and `CLAUDE.md` now agree.
- The precedent ADR-006 set becomes a rule instead of an isolated act.

**Negative / Trade-offs:**

- One more obligation on the author of an ADR that supersedes part of another, at the moment when
  they are least likely to notice they are doing it. That is exactly how the ADR-010 case
  happened.
- The Status line of a closed ADR becomes mutable within a narrow exception, which is a rule that
  will need enforcing by review; no gate checks it.

**Risks:**

- **Risk:** an author supersedes a clause without realising, so no Status line is updated and the
  convention does not fire. This is the failure that already occurred once.
  **Mitigation:** partial supersession is now a named thing with a checklist, and the
  `CLAUDE.md` table is the place a reader looks first. It remains a review obligation rather than
  an automated check, and this ADR does not pretend otherwise.

---

## Related Documents

| Document | Relationship |
|---|---|
| `adr-010-bulk-performance-record-format.md` | Its Parquet column table is superseded by ADR-023 in one respect; Status line updated by this ADR |
| `adr-023-performance-record-value-fields.md` | The superseding decision; this ADR supplies the Related Documents row it omitted |
| `adr-006-python-version-and-platform-constraints.md` | The precedent whose Status-line form this ADR generalises |
| `adr-022-agpl-licence-and-dependency-policy.md` | Superseded ADR-006's licensing clauses; the case that established the form |
| `docs/03-technical-contracts/01-data-format/10-file-formats.md` | Carries the corrected Parquet column table |
| `CLAUDE.md` | Lists decisions that reverse text still present in older documents |
