# ADR-021: Pre-Registered Hypotheses Are Mandatory

<!--
STORY ROLE: Settles whether a Study can be locked without hypotheses. This is the single point
where the two halves of the system's goal meet: enforcing scientific rigour, and not becoming
an obstacle. The answer determines whether the MANIFESTO's central claim is true of the
artifact or only of the prose.

CONNECTS TO:
  → docs/01-manifesto/MANIFESTO.md Principle 16 : planning precedes execution
  → docs/03-technical-contracts/01-data-format/04-study.md : pre_registered_hypotheses
  → docs/03-technical-contracts/04-public-api-contract.md : cc.create_study
  → docs/02-design/01-software-requirement-specification/03-functional-requirements/04-fr-4.3-experiment-runner.md : FR-08
  → adr-013-study-lifecycle-draft-then-locked.md : locking is the moment this takes effect
-->

---

**Status:** Accepted

**Date:** 2026-09-08

**Deciders:** Core maintainers, methodology lead

---

## Context

`01-data-format/04-study.md` marks `pre_registered_hypotheses` as not required.
`04-public-api-contract.md` gives it the default `None` and omits it from every
`cc.create_study()` example, as does the worked example in `02-cli-spec.md`.

Both repository implementations do the opposite. `_STUDY_LOCK_REQUIRED_FIELDS` includes
`pre_registered_hypotheses`, and `lock_study()` raises `ValidationError` when it is absent or
empty. Verified against both backends: a Study created exactly as the public API contract
documents cannot be locked, and therefore cannot be run.

FR-08 does not settle it. It requires that hypotheses be immutable after locking, not that they
exist.

The MANIFESTO is unambiguous. Principle 16 requires experimental design to be consciously
planned before data collection. `02-statistical-methodology.md` §7 names post-hoc hypothesis
selection as Pitfall 1. The system's stated differentiator, in SRS §2, is that it "requires
hypotheses to be pre-registered before data collection begins", offered as the property that
distinguishes it from COCO, Nevergrad and IOHprofiler, where such discipline is convention
rather than mechanism.

If the field is optional, that differentiator is false.

---

## Decision

**A Study cannot be locked without at least one pre-registered hypothesis.**
`pre_registered_hypotheses` becomes a required field for the draft-to-locked transition
introduced by ADR-013. `lock_study()` raises `ValidationError` when the list is absent or empty.
`01-data-format/04-study.md` marks the field required, and
`04-public-api-contract.md` removes the `None` default and adds it to every example.

**Each hypothesis is a structured record, not free text.** The shape already named in the public
API contract is adopted and made minimal:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `hypothesis` | string | yes | The claim, stated so that the study can contradict it |
| `test_type` | string | yes | The statistical test that will evaluate it, from `02-statistical-methodology.md` §3 |
| `metric_id` | string | yes | The metric the test is applied to, from the metric taxonomy |

**The requirement is paired with guidance, not imposed bare.** The refusal to lock must name
what is missing and why it is required, and must state the decision the researcher has to make.
A bare `ValidationError` naming a field is not sufficient to satisfy this ADR. The general
obligation is specified as a functional requirement group covering study design guidance; this
ADR is the first case that group must serve.

**A study without a hypothesis is still expressible**, as an exploratory Study: a hypothesis
whose `test_type` is `"none"` and whose text states that the study is exploratory and its
results are not confirmatory. That declaration is then carried into the Report's scope
statement, so exploratory work stays possible while remaining labelled.

---

## Rationale

This is the one place in the system where the manifesto's central claim can be made true by
mechanism rather than asserted in prose. Every other rigour guarantee the system offers, seed
control, scoped conclusions, mandatory limitations, is downstream of a study design that was
fixed before data existed. Making the field optional makes all of them decorative, because a
researcher can run first and formulate afterwards, which is Pitfall 1 exactly.

The implementations already enforce it, and they did so because the contract as written made
`lock_study()` meaningless. That is a finding produced by the implementation acting as a test of
the documentation, and the correct response is to fix the contract, not to relax the code.

Requiring structure rather than free text is what makes the pre-registration checkable. A
hypothesis naming its test and its metric can be compared against what the analysis actually
ran, which is what lets the Analyzer mark a result `pre_registered: true` or `false`. Free text
cannot support that flag, and the flag is already in the `StatisticalTestResult` contract.

The guidance pairing is not a courtesy. The system's goal has two halves, and a mandatory field
that rejects without explaining is the failure mode the second half exists to prevent. The
requirement and the guidance ship together or the requirement is an obstacle.

**Trade-off accepted:** a researcher who wants to run something quickly must write one sentence
and name one test first. The exploratory escape hatch keeps that cost at one sentence while
keeping the record honest about what kind of study it was.

---

## Alternatives Considered

### Optional field, enforced by review rather than by code

**Description:** Keep the field optional and rely on the contribution guide and reviewers.

**Why rejected:** This is precisely the arrangement the system was built to replace. SRS §2
states that existing platforms leave the discipline to convention and that Corvus Corone
enforces it; adopting convention here would make the differentiator untrue.

---

### Required, with no exploratory escape hatch

**Description:** Every Study must carry a falsifiable confirmatory hypothesis.

**Why rejected:** Exploratory studies are legitimate and MANIFESTO Principle 13 makes
exploratory analysis the first of three required levels. Forcing a confirmatory hypothesis onto
exploratory work produces hypotheses written to satisfy a validator, which is worse than no
hypothesis because it looks like pre-registration and is not.

---

## Consequences

**Positive:**

- The system's stated differentiator becomes a property of the artifact.
- `pre_registered: true` on a `StatisticalTestResult` becomes verifiable against a structured
  record rather than asserted.
- Contract and implementation stop contradicting each other on the field that matters most.

**Negative / Trade-offs:**

- Every `cc.create_study()` example in the corpus changes, including the CLI walkthrough.
- `lock_study()` becomes the point where a study can fail for a reason the researcher may not
  have anticipated, which is why the guidance obligation is part of this decision and not a
  follow-up.

**Risks:**

- **Risk:** Researchers write placeholder hypotheses to get past the gate.
  **Mitigation:** Partly unavoidable; a system cannot compel thought. The structured shape makes
  a placeholder visible, because `test_type` and `metric_id` are checked against the methodology
  and the taxonomy, and the exploratory declaration gives an honest alternative that is cheaper
  than a fake hypothesis.
- **Risk:** The guidance is deferred and the requirement ships bare.
  **Mitigation:** This ADR states that the pairing is part of the decision. Shipping the gate
  without the guidance does not satisfy it.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/01-data-format/04-study.md` | Field becomes required; hypothesis shape defined |
| `docs/03-technical-contracts/04-public-api-contract.md` | Default removed; examples updated |
| `docs/02-design/01-software-requirement-specification/03-functional-requirements/` | The study design guidance requirement group this ADR depends on |
| `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §3, §7 | Test selection and Pitfall 1 |
| `adr-013-study-lifecycle-draft-then-locked.md` | Locking is the moment this requirement takes effect |
