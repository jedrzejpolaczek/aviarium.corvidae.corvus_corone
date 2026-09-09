# ADR-029: Declaring a Study Exploratory

<!--
STORY ROLE: The corpus had two mechanisms for the same declaration and never related them.
This ADR keeps both, because they answer different questions, and adds the rule that makes
them agree.

CONNECTS TO:
  → adr-009-problem-instance-diversity-requirements.md : uses both mechanisms, four sections apart
  → adr-021-pre-registered-hypotheses-mandatory.md     : introduced test_type "none"
  → docs/03-technical-contracts/01-data-format/04-study.md : the Study and Hypothesis schemas
  → docs/03-technical-contracts/01-data-format/12-cross-entity-validation.md : CV-021 and the new CV-024
-->

---

**Status:** Accepted

**Date:** 2026-09-09

**Deciders:** Core maintainers, methodology lead

---

## Context

A Study that is not confirmatory has to say so. The corpus provides two ways to say it and never
says how they relate.

**`study_type = "exploratory"`**, a Study-level field, is what FR-32 and FR-33 test, what
`04-study.md` documents in three places, what cross-entity rule `CV-021` reads, what
`01-benchmarking-protocol.md` describes, and what ADR-009 names in its Enforcement section.

**`test_type: "none"`**, a per-hypothesis value, is what FR-31 requires, what ADR-021 designed as
the escape hatch from mandatory pre-registration, what `04-public-api-contract.md` documents in
three places, what the Statistical Tester admits as its one exception, and what the first tutorial
tells a researcher to write.

ADR-009 uses both. Line 84 says *"A Study is exploratory when every entry in
`pre_registered_hypotheses` carries `test_type = "none"`"*; lines 181 and 246 say the escape valve
is the `study_type` field. `04-study.md` goes further and states, on the `test_type` row, that an
exploratory Study declares itself through `study_type` **and not through this field** — a direct
contradiction of FR-31.

The precedence rule cannot resolve it. The conflict is inside the SRS, between FR-31 on one side
and FR-32 and FR-33 on the other, and those are the same layer.

Found by the 2026-09-09 consistency audit while closing REF-TASK-0044, and opened as
REF-TASK-0051.

---

## Decision

**Both mechanisms stay. They are not two spellings of one statement, and a new cross-entity rule
makes them agree.**

`study_type` is the **declaration**: the researcher's statement about what kind of study this is.
It is what waives the ADR-009 diversity floor, and it is what the Report scope statement carries.

`test_type: "none"` is the **consequence**: what the hypotheses of such a study contain. ADR-021
makes `pre_registered_hypotheses` mandatory and non-empty, so an exploratory Study must still
have an entry; `none` is what an entry says when no test will be run against it.

**New cross-entity rule `CV-024`, checked at `lock_study()`:**

> `study.study_type == "exploratory"` if and only if every entry in
> `study.pre_registered_hypotheses` carries `test_type == "none"`.

A Study that fails it is rejected, and the message names the disagreement rather than one side of
it: either the declaration says exploratory and a hypothesis names a test that will not be run, or
a hypothesis declines to be tested while the Study claims to be confirmatory.

Consequently there is **no mixed Study** in V1. A Study is confirmatory or it is exploratory; it
cannot be confirmatory for two hypotheses and exploratory for a third.

`04-study.md` loses the sentence saying an exploratory Study declares itself through `study_type`
*and not* through `test_type`. FR-31, FR-32 and FR-33 are correct as written and stay as they are:
FR-31 describes the hypothesis side, FR-32 and FR-33 the declaration side, and `CV-024` is what
makes them the same statement.

---

## Rationale

**Why not one mechanism.** Each alternative loses something real.

Dropping `test_type: "none"` means an exploratory Study must name a test it will not run. That is
a false statement in the pre-registration record — the one record in the system whose entire value
is that it says what was actually intended before the data existed. It also strands ADR-021, whose
escape hatch was designed precisely so that mandatory pre-registration would not force a
researcher to invent a hypothesis.

Dropping `study_type` means the diversity waiver has to be derived rather than declared. `CV-021`
would ask "are all hypotheses `none`?" instead of reading a field, which is workable, but it makes
the waiver a side effect of how the hypotheses were written rather than something the researcher
chose. ADR-009's argument for the escape hatch is that *the declaration is how the researcher says
which of the two they are running*; deriving it removes the act of declaring.

**Why the mixed case is excluded rather than defined.** A Study with one untested hypothesis and
two tested ones is expressible, and defining it would mean deciding whether the diversity floor
applies to such a Study, whether its Report is scoped exploratory or confirmatory, and what the
scope statement says. Every answer is arguable and none is needed: a researcher who wants to
explore one question and confirm another can run two Studies, and the two Studies then have
honest, separate scope statements. Excluding the case costs nothing and removes three decisions.

**Why a cross-entity rule rather than a schema constraint.** The relationship spans the Study and
its hypothesis list, which is what the `CV-*` family is for, and it is checkable exactly at
`lock_study()` — the moment the pre-registration becomes binding and the moment FR-27 requires
every unresolved decision to be reported at once.

**Trade-offs accepted.** Two fields must agree, so there is a redundancy a reader can notice and
ask about. The redundancy is the point: the declaration is a statement of intent and the
`test_type` values are its mechanical consequence, and a system that lets them diverge would let a
Study claim to be confirmatory while running no tests.

---

## Alternatives Considered

### `study_type` only

**Description:** remove `test_type: "none"`. An exploratory Study declares `study_type` and its
hypotheses name the test that would apply.

**Why rejected:** it puts a false statement in the pre-registration record. A hypothesis naming
`wilcoxon` in a study that will run no test is exactly the kind of paper compliance ADR-021 exists
to prevent, and the record is the artefact whose value depends on being literally true.

### `test_type: "none"` only

**Description:** remove `study_type`. A Study is exploratory iff every hypothesis is `none`,
which is what ADR-009 line 84 already says.

**Why rejected:** the diversity waiver becomes a derived property rather than a declaration, which
contradicts ADR-009's own reasoning for the escape hatch. It also leaves the mixed case
undefined rather than excluded, since with no Study-level field there is nothing to disagree with.

### Both, with no consistency rule

**Description:** document both and let each serve its own purpose without requiring agreement.

**Why rejected:** that is the current state, and it permits a Study declared `"standard"` whose
every hypothesis is `none` — a study that waives nothing, runs nothing, and reports itself as
confirmatory.

---

## Consequences

**Positive:**

- FR-31, FR-32 and FR-33 stop contradicting each other without any of them changing.
- The one sentence in `04-study.md` that denied FR-31 is removed.
- A Study whose declaration and hypotheses disagree is rejected at the moment pre-registration
  takes effect, with a message that names the disagreement.

**Negative / Trade-offs:**

- Two fields must be kept in agreement, and a caller who sets one and forgets the other gets a
  rejection rather than an inference. That is deliberate: inferring which one the researcher meant
  is the guess this ADR exists to avoid.
- The mixed Study is not expressible. A researcher who wants one runs two Studies.

**Risks:**

- **Risk:** a caller reads only the public API contract, sees `test_type: "none"`, and never sets
  `study_type`.
  **Mitigation:** `CV-024` rejects at `lock_study()`, and FR-27 requires the message to state the
  decision that is unmade rather than only the field that is absent.

---

## Related Documents

| Document | Relationship |
|---|---|
| `adr-009-problem-instance-diversity-requirements.md` | Used both mechanisms four sections apart; the diversity waiver stays on `study_type` |
| `adr-021-pre-registered-hypotheses-mandatory.md` | Introduced `test_type: "none"`; unchanged |
| `01-data-format/04-study.md` | Loses the sentence denying FR-31; gains the `CV-024` reference |
| `01-data-format/12-cross-entity-validation.md` | Gains `CV-024` |
| `03-functional-requirements/09-fr-4.8-study-design-guidance.md` | FR-31, unchanged |
| `03-functional-requirements/02-fr-4.1-problem-repository.md` | FR-32 and FR-33, unchanged |
