# ADR-027: A Failed Run Is Recorded, Not Configured

<!--
STORY ROLE: Settles what the system does when a Run fails. The C3 layer had grown a complete
failure-handling and resource-limit model that no contract defined and no requirement asked
for; FR-12 already answered the question, and the answer is simpler than the model.

CONNECTS TO:
  → docs/02-design/01-software-requirement-specification/03-functional-requirements/04-fr-4.3-experiment-runner.md : FR-12, the requirement this ADR reads literally
  → docs/03-technical-contracts/01-data-format/06-run.md : the status enumeration that stays as it is
  → docs/03-technical-contracts/01-data-format/05-experiment.md : likewise
  → docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md : where the behaviour lives
  → adr-012-documentation-layer-normativity.md : the rule the C3 model was written against
-->

---

**Status:** Accepted

**Date:** 2026-09-09

**Deciders:** Core maintainers, technical lead

---

## Context

The Experiment Runner and Study Orchestrator component documents describe a complete failure
and resource-limit model:

- `Study.on_failure`, taking `"skip"` or `"abort"`
- `Study.max_workers`
- `Run.timeout_s` and `Run.memory_limit_mb`
- Run statuses `skipped` and `aborted`
- Experiment statuses `partial` and `aborted`
- `Experiment.skipped_count`

None of it exists. `06-run.md` admits three Run statuses — `completed`, `failed`,
`budget_exhausted`. `05-experiment.md` admits four — `planned`, `running`, `completed`,
`failed`. `04-study.md` has neither `on_failure` nor `max_workers`, and `Run` has neither
timeout nor memory limit. The model appeared in the C3 documents of two container groups and in the C4 shared layer,
and in no contract. ADR-028 has since removed both.

ADR-012 forbids the descriptive layers from coining exactly this kind of vocabulary, so the
situation could not be repaired by editing the components alone: either the contracts gain the
model, or the components lose it. The 2026-09-09 consistency audit measured the cost of leaving
it unresolved — the Execution Coordinator required thirteen invented decisions to implement from
its documentation, seven of them from this table.

`max_workers` was already settled and is not reopened here: SRS §1.4 boundary B-01 reserves the
name for V2, and the parallel dispatch it configured has been removed.

The question this ADR answers is the remaining one: does V1 have a run-failure policy at all?

---

## Decision

**No. A failed Run is recorded and the Experiment continues. There is no policy to configure.**

FR-12 already states the behaviour in full:

> The system MUST record a failed Run with its failure reason and timestamp rather than silently
> skipping it. A Study with failed Runs MUST NOT be reported as if all planned Runs completed.

Operationally:

- A Run whose evaluation raises an uncaught exception is written with `status = "failed"` and a
  non-empty `failure_reason`. That is the only failure status; the cause goes in the reason, not
  in a second status value.
- The Runner proceeds to the next Run in the plan. There is no `abort` mode, because there is no
  Study-level field to select one.
- The Experiment ends `completed` when the plan is exhausted, and `failed` only when the
  Experiment itself could not proceed — a `SeedCollisionError`, a `StorageError`, a repository
  that cannot be written. An Experiment containing failed Runs is a completed Experiment with
  failed Runs in it.
- Both generated Reports state the count of failed against completed Runs and carry it into the
  limitations section, which is the second sentence of FR-12.
- Errors that make the Experiment itself impossible propagate out of the Study Orchestrator as
  their own exception class (ADR-015). Aborting is what the caller sees when one does; it is not
  a mode the caller chose beforehand.

**No resource limits in V1.** `Run.timeout_s` and `Run.memory_limit_mb` are not added. A Run that
exhausts memory or hangs is a Run the operating system or the researcher stops, and the partial
record on disk says what was reached.

**Nothing changes in the contracts.** `06-run.md`, `05-experiment.md` and `04-study.md` are
already correct; it is the C3 layer that is wrong, and it is the C3 layer that changes.

---

## Rationale

**FR-12 is not a weaker version of the model — it is a different and better answer.** A
`skip`/`abort` switch asks the researcher, before any data exists, what should happen if
something they have not anticipated goes wrong. That question cannot be answered well in advance,
and the choice has scientific consequences: `abort` discards the Runs that did succeed, and
`skip` produces the same Experiment as no policy at all. Recording every outcome and reporting
the counts is what MANIFESTO Principle 19 asks for, and it leaves the decision about what the
partial data is worth to the point where the researcher can see the data.

**A second failure status is a claim the system cannot support.** Distinguishing `skipped` from
`aborted` means classifying the *cause* of a failure into "recoverable" and "fatal", and the
Runner sees an exception from third-party algorithm code. It has no basis for that judgement. A
single `failed` with a `failure_reason` string records what actually happened and leaves the
classification to the reader, who has the traceback.

**Resource limits are an operational concern wearing a scientific costume.** `memory_limit_mb`
in the Study record would be pre-registered alongside the hypotheses, as though the memory
ceiling were part of the experimental design. It is a property of the machine. Putting it in the
Study makes two Runs of the same Study on different hardware formally different studies, which is
the opposite of what ADR-001 and the reproducibility requirements are for. If V2 needs limits
they belong to the execution environment, next to `execution_environment`, not to the plan.

**Why the model existed at all.** It is a plausible design, written in a layer that was not
required to check whether the fields it named existed. That is the failure ADR-012 was written
to prevent and the gate cannot detect: `check_docs.py` enforces three of the seven categories
ADR-012 names, and field names and enumeration values are not among them. This ADR removes one
instance; REF-TASK-0050 addresses the layer.

**Trade-offs accepted.** A researcher who wants execution to stop at the first failure has no way
to say so and must interrupt the process. That is a real loss for long Studies, and it is the
price of not putting a question in the Study record that the researcher cannot answer when the
Study record is written. If it turns out to matter in practice, it returns as a runtime argument
to `cc.run()` rather than a pre-registered field — a question about this execution, not about
this experimental design.

---

## Alternatives Considered

### Add the full model to the contracts

**Description:** `Study.on_failure`, `Run.timeout_s`, `Run.memory_limit_mb`, the statuses
`skipped`, `aborted` and `partial`, and `Experiment.skipped_count` all enter the entity schemas.
The C3 documents stay as written.

**Why rejected:** it adopts a design because it was already typed, which is the weakest possible
reason. Each element also fails on its own merits — see the Rationale — and the combination adds
a schema field and two enumeration values per entity to support a policy whose `skip` branch is
identical to having no policy.

**Under what conditions reconsidered:** if real studies show that a common failure class is
genuinely recoverable and distinguishable by the Runner, `skipped` earns its place.

### Minimal: `Study.on_failure` only

**Description:** keep the `skip`/`abort` switch as the one decision the researcher makes; drop
the resource limits and the extra statuses. `skip` remains the default and matches FR-12.

**Why rejected:** it is the smallest version of the same mistake. The default branch changes
nothing, so the field exists to serve `abort`, and `abort` is a runtime convenience —
"stop wasting my afternoon" — not an element of experimental design. FR-28 requires parameters
with methodological consequences to be explicit; the corollary is that parameters with no
methodological consequence do not belong in the pre-registered record at all.

---

## Consequences

**Positive:**

- The largest single source of uncontracted vocabulary in the corpus is removed rather than
  legitimised. Seven of the thirteen invented decisions the audit counted in the Execution
  Coordinator disappear.
- No schema change, so no schema version bump and no migration question.
- FR-12 becomes readable as the complete answer it already was, instead of a subset of a model
  described elsewhere.

**Negative / Trade-offs:**

- No way to stop a Study at the first failure. Stated above; the mitigation is a runtime argument
  if it proves necessary, not a Study field.
- No resource limits, so a runaway Run is the operator's problem. This is honest about what a
  library that runs in the caller's process can promise.

**Risks:**

- **Risk:** the removed vocabulary returns, because the design is plausible and the gate cannot
  see field names or enumeration values.
  **Mitigation:** this ADR is the record to point at, and `CLAUDE.md` lists it among the
  decisions that reverse text still present in older documents. It remains a review obligation.

---

## Related Documents

| Document | Relationship |
|---|---|
| `03-functional-requirements/04-fr-4.3-experiment-runner.md` | FR-12 states the behaviour this ADR declares complete |
| `01-data-format/06-run.md` | Status enumeration confirmed unchanged |
| `01-data-format/05-experiment.md` | Status enumeration confirmed unchanged |
| `01-data-format/04-study.md` | Gains no `on_failure` and no `max_workers` |
| `02-interface-contracts/04-runner-interface.md` | Where the recording behaviour is specified |
| `adr-012-documentation-layer-normativity.md` | The rule the removed model was written against |
| `adr-015-exception-hierarchy-authority.md` | Experiment-level failures propagate as taxonomy classes |
