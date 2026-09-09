# ADR-028: Consolidate the C3 Layer and Remove C4

<!--
STORY ROLE: Takes the decision ADR-012 deferred. The descriptive layers described a library
whose core has no code, could not be falsified against anything, and produced every defect of
the class "the descriptive layer invented vocabulary" that the 2026-09-09 audit found.

CONNECTS TO:
  → adr-012-documentation-layer-normativity.md : deferred this decision explicitly
  → adr-026-named-exceptions-to-contract-exclusivity.md : what the descriptive layers may not do
  → adr-027-run-failure-is-recorded-not-configured.md : removes one instance of the same problem
  → docs/README.md : the reading order this ADR shortens
-->

---

**Status:** Accepted

**Date:** 2026-09-09

**Deciders:** Core maintainers, technical lead

---

## Context

ADR-012 named this decision and put it off:

> An earlier proposal was to delete `05-c4-level4-code/` and consolidate the forty-five C3
> component files into eleven. That treats the symptom. … Consolidation may still be worthwhile
> for maintenance cost. That is now a separate, independent decision rather than a repair.

That was right at the time. ADR-012's judgement was that the C4 layer contradicted ADR-001 not
because it was too detailed but because nothing forbade it from redefining `Repository`, and that
the rule was the fix. The rule was written, a gate was built for it, and the corpus went green.

The 2026-09-09 consistency audit measured what the rule and the gate had actually achieved.

**Every finding of the class "a descriptive document states something no contract defines" came
from these two layers.** A parallel execution and failure model — `Study.on_failure`,
`Study.max_workers`, `Run.timeout_s`, `Run.memory_limit_mb`, Run statuses `skipped` and
`aborted`, Experiment statuses `partial` and `aborted`, `Experiment.skipped_count` — spread across
the Experiment Runner group, the Study Orchestrator group and `05-c4-level4-code/02-shared/`. A
component document describing a `LOCFInterpolator` that inserts synthetic Performance Records, in
contradiction of ADR-003, and scans a field named `iteration` that no entity has. `StudySpec`,
`RunResult`, `ExecutionSummary`, `RawMetricResult`, `MetricResult`, `ReportIncompleteError`.
`PilotState`, the state object of a deferred container, inside the V1 Experiment Runner.

**The gate cannot see any of it, by construction.** ADR-012 names seven categories the descriptive
layers may not coin: identifiers, signatures, field names, field types, enumeration values, error
classes, file formats. `check_docs.py` enforces three — exception class names, `cc.*` facade names,
and capitalised types in annotations inside fenced blocks. Field names and enumeration values,
which is what the parallel model consists of, are not checked and cannot easily be: checking them
would require the descriptive layer to declare a machine-readable interface, which is most of the
way to not having a descriptive layer.

**Nothing can falsify these documents.** The library's core is not implemented. A C3 document that
describes a component with no code is a claim no test can contradict and no reader can check
without holding the whole contract tree in their head — which is exactly the check that failed
forty-five times.

**The repair pass demonstrated the failure mode in the act of repairing.** On 2026-09-09 eight
component groups were reconciled with their contracts. The Execution Coordinator's page received a
correct new footnote — *"Execution is sequential in V1 — SRS §1.4 boundary B-01 reserves
`max_workers` for V2"* — appended below an unchanged document body that still described a
`ProcessPoolExecutor` fan-out three paragraphs above it. Reconciling forty-five documents by hand
produces this.

And the audit's verdict measurement gave the cost in numbers: implementing the Execution
Coordinator from its documentation required thirteen invented decisions, the LOCF Interpolator
eleven, the Statistical Tester twelve. The layer whose purpose is to make components implementable
was making them less so.

---

## Decision

**`05-c4-level4-code/` is deleted. The forty-five C3 component files are absorbed into eleven
group indexes, one per container, which describe decomposition and responsibility and define
nothing.**

Each surviving index carries:

- what the container is for, in prose;
- a table of its components, each with a one-line responsibility and a link to the **contract it
  implements**;
- a *Where the vocabulary comes from* section naming the contracts that define every term the page
  uses;
- an *Open decisions* section where one applies, naming the REF-TASK.

Each index states its own status at the top: it is descriptive, it defines nothing, and a
statement on it that the contracts do not support is a defect in the page.

**What the indexes may not contain**, and this is the operative half of the decision: no method
signatures, no field names that are not in an entity schema, no enumeration values, no exception
class names absent from the taxonomy, no dependency lists, no implementation module paths, no
"Key Behaviors" numbered as though they were specification. A component's behaviour is specified
in its contract or it is not specified.

**The reading order in `docs/README.md` loses its C4 step.** It becomes
MANIFESTO → SRS → C1 → C2 → C3 → contracts → docstrings in `packages/`.

**Four accepted ADRs name component files that no longer exist.** ADR-016, ADR-017, ADR-018 and
ADR-019 each instructed a specific component document to change or to lose a definition. Every one
of those instructions was carried out before this ADR; the documents were then absorbed. Under the
mechanism ADR-025 established, each of those four gains a Status-line clause pointing here — the
same one permitted edit, used for a slightly wider purpose than supersession: recording that a
document an ADR names has been absorbed elsewhere. ADR-028 extends the ADR-025 convention to that
case and to no other.

---

## Rationale

**Why consolidation rather than finishing the layer.** Finishing it means closing REF-TASK-0041
and REF-TASK-0042 so the vocabulary exists, then re-reconciling forty-five documents. Both tasks
are worth doing on their own merits and both are being done. The re-reconciliation is not: it is
the same manual sweep that produced the footnote-over-stale-body defect, on the same documents,
with the same absence of any mechanism to catch the next drift. Doing it a third time and expecting
a different outcome is not a plan.

**Why consolidation rather than the `allow-undefined` marker.** Marking the layer exempt is
cheaper and honest, and it was the third option considered. It was rejected because it keeps the
cost while dropping the pretence: forty-five documents still have to be maintained, still describe
unbuilt code, and now openly cannot be trusted. If a document is not worth checking it is not
worth keeping at that length.

**Why the contract link in every component row matters more than the prose.** The failure mode was
never that C3 said too little; it was that C3 said things with no owner. A row that names the
contract implementing the component makes the ownership explicit and gives a reviewer a
one-step check: open the contract, see whether it says what the row claims. That is a check a
person can actually perform, unlike "does any of the thirty-one contract files contradict this
paragraph".

**What is genuinely lost.** Real content goes: the per-component Key Behaviors sections contained
design thinking, some of it good — the reasoning about why combined scheduled-and-improvement
records are not suppressed, the fallback chain in the visualization data resolver, the malformed-
line handling in the record reader. Where such a statement is true and load-bearing it belongs in
a contract, and moving it there is work this ADR does not do. Where it is merely plausible, it was
the problem. The audit's judgement — recorded here so a later reader can disagree with it — is
that the ratio of the second kind to the first was high enough to make deletion cheaper than
triage, given that none of it can be verified against code that does not exist.

**Why now rather than after the core is implemented.** The opposite order is defensible: build the
library, then let the C3 documents be checked against it. It was rejected because IMPL-001 onwards
will be written *from* these documents, and thirteen invented decisions per component is what that
produces. The layer has to be either trustworthy or absent before implementation starts, and
absent is achievable today.

**Trade-offs accepted.** The architecture documentation is thinner, and a reader who wants to know
how a component behaves must open a contract rather than a page written for them. That is the
point: the contract is the document that is maintained, checked and implemented. The C3 layer's
job is now to say what the parts are and where each one's specification lives, which is what a C3
level is for in the C4 model and what this one had stopped doing.

---

## Alternatives Considered

### Keep both layers and finish the reconciliation

**Description:** close REF-TASK-0041 and REF-TASK-0042 so the missing vocabulary exists, then pass
over the forty-five component documents again, this time reading each body rather than its
citations.

**Why rejected:** it is the pass that has already been run twice, and the second run produced a
correct footnote under an uncorrected body. Nothing in the proposal changes what will catch the
third drift, because the gate structurally cannot check field names or enumeration values.

**Under what conditions reconsidered:** if the descriptive layer were generated from the contracts
rather than written alongside them, the drift would be impossible by construction. That is a
plausible future and a different decision.

### Mark the C3 layer `allow-undefined` and say so in `README.md`

**Description:** exempt the layer from the vocabulary gate, and state plainly that C3 and C4 are
sketches rather than specifications.

**Why rejected:** it preserves the maintenance cost of forty-five documents while removing the
last reason to trust them, and it drops the layer out of the audit's verdict criterion — a
component would no longer be implementable from its own document by design. Cheap, honest, and
worse than deleting the part that cannot be trusted.

### Delete C4 only, keep the forty-five C3 files

**Description:** the C4 layer is the clearest case — seven groups describing modules that do not
exist — so remove it and leave C3 alone.

**Why rejected:** it removes about a quarter of the problem. The parallel execution model lived
mostly in C3, and so did the LOCF Interpolator contradiction and every invented type the audit
counted.

---

## Consequences

**Positive:**

- The largest source of unverifiable statements in the corpus is gone. Sixty-one documents removed,
  eleven written.
- Every component now names the contract that specifies it, so a reviewer has a one-step check
  where they previously had a whole-tree one.
- The audit's verdict criterion moves to a layer that can satisfy it: a component is implementable
  from its contract, and the C3 page says which contract that is.
- The three open decisions that block implementation — REF-TASK-0041, REF-TASK-0043,
  REF-TASK-0051 — are stated on the pages of the containers they block, rather than being visible
  only in the ROADMAP.

**Negative / Trade-offs:**

- Design reasoning is lost with the deleted files. Where it was true it belonged in a contract, and
  moving it there is unfinished work rather than work this ADR did.
- The architecture documentation is thinner and a reader must follow one more link to reach
  behaviour.
- Four accepted ADRs name documents that no longer exist, handled by the mechanism above but
  leaving a reader one indirection from what the ADR originally pointed at.

**Risks:**

- **Risk:** the eleven indexes drift the same way, more slowly.
  **Mitigation:** they are eleven rather than forty-five, each is short, and each states at the top
  that it defines nothing. The structural fix — generating them from the contracts — is named as
  the condition under which this decision would be reconsidered.
- **Risk:** a future contributor recreates a per-component file because the index feels too thin.
  **Mitigation:** this ADR is the record to point at, and the *What the indexes may not contain*
  list is the specific answer.

---

## Related Documents

| Document | Relationship |
|---|---|
| `adr-012-documentation-layer-normativity.md` | Deferred this decision explicitly; its rule survives unchanged |
| `adr-025-superseded-clauses-of-accepted-adrs.md` | The Status-line mechanism this ADR extends to absorbed documents |
| `adr-026-named-exceptions-to-contract-exclusivity.md` | What a descriptive layer may and may not define |
| `adr-027-run-failure-is-recorded-not-configured.md` | Removes the largest single body of vocabulary the deleted files carried |
| `adr-016-cli-surface-authority.md`, `adr-017-…`, `adr-018-…`, `adr-019-…` | Each names a component document now absorbed into its group index; Status lines updated |
| `docs/README.md` | Reading order loses its C4 step |
| `docs/ROADMAP.md` | C3 and C4 rows restated |
