# ADR-013: Study Lifecycle — Draft Then Locked

<!--
STORY ROLE: Resolves the conflict between the two-phase Study lifecycle in the repository
contract and the lock-on-creation lifecycle in the public API contract. Pre-registration is
the central mechanism of the MANIFESTO, so the moment at which a Study becomes immutable is
a scientific decision, not an API convenience.

CONNECTS TO:
  → docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md : StudyRepository
  → docs/03-technical-contracts/04-public-api-contract.md : cc.create_study, cc.update_study
  → docs/03-technical-contracts/01-data-format/04-study.md : Study.status
  → docs/02-design/01-software-requirement-specification/03-functional-requirements/04-fr-4.3-experiment-runner.md : FR-08
  → adr-021-pre-registered-hypotheses-mandatory.md
-->

---

**Status:** Accepted

**Date:** 2026-09-08

**Deciders:** Core maintainers, technical lead

---

## Context

Two lifecycles are specified for the same entity.

`02-interface-contracts/06-repository-interface.md` and the C2 end-to-end flow describe two
phases: `create_study()` persists in status `"draft"`, and a separate `lock_study()` transitions
to `"locked"`, after which `sampling_strategy`, `log_scale_schedule`, `improvement_epsilon` and
`experimental_design` become immutable.

`04-public-api-contract.md` describes one phase: `Study.status` is "always `locked` after
`create_study()`", studies are "immutable once created in V1", and `update_study()` "always
raises `StudyLockedError`", existing only to make the policy explicit.

The conflict is visible to users. `06-tutorials/02-researcher-design-and-execute-study.md`
shows `cc.update_study(study.id, repetitions=20)` as a working step, which is possible under
the first lifecycle and impossible under the second.

FR-08 requires that the problem set, algorithm set, experimental design and hypotheses be
locked before any Run executes. It does not state when locking happens.

---

## Decision

**The Study lifecycle has two phases: `"draft"` then `"locked"`.**

`cc.create_study()` returns a Study in status `"draft"`. `cc.update_study(study_id, **fields)`
modifies a draft and raises `StudyAlreadyLockedError` on a locked Study. A new
`cc.lock_study(study_id)` performs the transition and is the point at which pre-registration
takes effect. `cc.run(study_id)` requires status `"locked"` and raises `StudyNotLockedError`
otherwise.

`04-public-api-contract.md` is corrected to match. The repository contract, the C2 flow and
the existing implementation already describe this lifecycle and are unchanged.

---

## Rationale

The two-phase lifecycle is what makes pre-registration a deliberate act. Locking inside the
constructor means the scientific commitment happens as a side effect of object creation, at a
moment the researcher did not choose. MANIFESTO Principle 16 requires that experimental design
be consciously planned before data collection; a commitment nobody noticed making is not a
conscious plan. The explicit `lock_study()` call is the moment where the framework can state
what is about to become immutable and why, which is the behaviour required by the second half
of the system's goal.

The single-phase lifecycle also produces a public function whose only behaviour is to raise.
`update_study()` under that model can never succeed in V1, which is dead surface area in an API
that a researcher is expected to learn.

Finally, the two-phase model is the cheaper correction. The repository contract, the C2 flow
diagram, both repository implementations and the tutorial already assume it. Only
`04-public-api-contract.md` has to change.

**Trade-off accepted:** a researcher must make two calls where one would do, and a Study left
in draft is a Study that cannot run. The framework must therefore report draft status clearly
rather than failing obscurely at `cc.run()`.

---

## Alternatives Considered

### Lock on creation

**Description:** `create_study()` returns a locked Study; there is no draft phase.

**Why rejected:** Makes pre-registration implicit, leaves `update_study()` permanently dead, and
contradicts the repository contract, the C2 flow, the tutorial and the implementation.

**Under what conditions reconsidered:** If a future study-authoring surface makes the design
fully complete before any object is created, for example a validated configuration file, then
creation and locking coincide naturally and the draft phase adds nothing.

---

## Consequences

**Positive:**

- One lifecycle across contract, architecture, tutorial and code.
- `lock_study()` becomes the natural attachment point for design elicitation and for the
  diversity check from ADR-009.
- The tutorial step showing `cc.update_study()` becomes correct.

**Negative / Trade-offs:**

- `04-public-api-contract.md` requires edits to `Study.status`, `cc.update_study()` and DQ-2.
- A new public function, `cc.lock_study()`, enters the V1 API surface and needs a CLI decision.
  It has no CLI equivalent in V1, consistent with the other study-authoring functions.

**Risks:**

- **Risk:** A researcher runs an unlocked Study and receives an unclear error.
  **Mitigation:** `cc.run()` raises `StudyNotLockedError`, which names the missing step.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/04-public-api-contract.md` | Corrected by this ADR |
| `docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md` | Already describes this lifecycle |
| `docs/03-technical-contracts/01-data-format/04-study.md` | `Study.status` enumeration |
| `adr-021-pre-registered-hypotheses-mandatory.md` | Defines what must be present before locking |
