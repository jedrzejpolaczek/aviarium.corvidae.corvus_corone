# ADR-030: The Pilot Proposes, the Researcher Decides

<!--
STORY ROLE: Reconciles the Corvus Pilot roadmap with the two anti-patterns it comes closest to.
Post-V1 by scope, decided now because the answer constrains what IMPL-028 onwards may build,
and a constraint stated after the code exists is not a constraint.

CONNECTS TO:
  → docs/01-manifesto/MANIFESTO.md : AP-4 and AP-7, the anti-patterns at stake
  → docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md : Explicit Scope Exclusions
  → docs/02-design/01-software-requirement-specification/05-constraints/02-const-scientific.md : where the exclusions become constraints
  → docs/02-design/02-architecture/03-c4-leve2-containers/14-corvus-pilot.md : the deferred container
  → adr-021-pre-registered-hypotheses-mandatory.md : the argument this ADR reuses
-->

---

**Status:** Accepted

**Date:** 2026-09-09

**Deciders:** Core maintainers, technical lead

---

## Context

The MANIFESTO rejects two things by name:

> **AP-7 — Automated algorithm selection as a substitute for researcher judgment.** Making
> algorithm selection recommendations or decisions on behalf of the user — treating benchmarking
> output as a recommendation engine rather than as evidence.

> **AP-4 — Opaque analysis pipelines.** Implementing analysis workflows that cannot be
> independently inspected, reproduced, or understood by the user. Every statistical test,
> aggregation, and visualization step must be transparent so that conclusions can be verified and
> contested.

C1 turns both into design exclusions and CONST-SCI turns those into constraints on every API path.

The Corvus Pilot roadmap builds, in Phases 3a and 3b: an LLM that generates hypotheses from past
data (IMPL-037), an autonomous research cycle on a weekly cron (IMPL-041), a calibrated predictor
returning a confidence-gated prediction (IMPL-035), an LLM judging study designs against the
MANIFESTO (IMPL-026), and a meta-analyst pooling effect sizes across studies (IMPL-038).

Nothing in the corpus reconciles the two. IMPL-039, the safety module, is the only thing that
looks like a guard, and it guards resource consumption and prompt injection — a different question
from whether the system is deciding on the researcher's behalf.

The 2026-09-09 consistency audit recorded this as a missing decision rather than a defect, because
every one of those tasks has a defensible version and a forbidden one, and the difference between
them is a design constraint. Stating it after the code exists is not stating it: that is the same
argument ADR-021 makes about pre-registration, applied to the system's own construction.

---

## Decision

**Every Corvus Pilot capability produces something a person accepts, rejects or edits, and ships
the material needed to reject it. The Pilot never commits the researcher to anything.**

Two rules, and everything below follows from them.

**Rule 1 — Proposal, not commitment.** No Pilot capability may perform an act that binds the
researcher scientifically. The binding acts in this system are enumerable, because ADR-013 and
ADR-021 made them explicit: locking a Study is where pre-registration takes effect, and the
contents of `pre_registered_hypotheses` at that moment are the scientific commitment. **The Pilot
may not call `cc.lock_study()`.** It may compose a Study, propose hypotheses, explain them and
hand the whole thing to a person; the person locks it.

**Rule 2 — Every output carries its own grounds for rejection.** A statement the researcher cannot
check is a statement AP-4 forbids, regardless of how it was produced. Concretely: a proposed
hypothesis carries the past results it was derived from; a prediction carries its feature
attributions, the data it was trained on and its calibration; a design critique carries the named
principle or requirement each point rests on, so the reader can disagree with the reading rather
than with a score.

Applied to the roadmap:

| Task | Permitted form | Forbidden form |
|---|---|---|
| IMPL-026 LLM-as-judge | A checklist against named MANIFESTO principles and requirements, each item citing what it tests, so the researcher can contest any line | A quality score, a pass/fail verdict, or any output that cannot be traced to a named rule |
| IMPL-037 Hypothesis generator | Candidate hypotheses with the past results that suggested each, presented for editing before they enter a Study | Writing hypotheses into a Study that is then locked without a person reading them |
| IMPL-035 Calibrated predictor | A prediction shipped with its attributions, training set and calibration curve, labelled as a prediction about untested conditions | A recommendation of which algorithm to use; a confidence gate that silently withholds |
| IMPL-038 Meta-analyst | Pooled effect sizes across studies, scoped like any other conclusion, with the heterogeneity between studies stated | A cross-study ranking, or a pooled claim presented without the scope conditions of its inputs |
| IMPL-041 Autonomous cycle | Proposes a Study and stops. The cycle may run unattended up to the lock; a person locks it | Locking and running a Study without a person in the loop |

**The confidence gate in IMPL-035 is redefined.** Returning `None` below a threshold makes the
system decide when the researcher is allowed to see its reasoning, which is the wrong side of both
rules. The predictor returns its estimate with its calibration; the researcher decides what a
poorly calibrated estimate is worth.

**What remains forbidden outright**, because no permitted form exists: any output that names one
algorithm as the one to use, in any phase, by any component. That is AP-7 directly and CONST-SCI-01
already forbids it for every API path, the Pilot included.

---

## Rationale

**Why the boundary is `lock_study()` and not "no LLM in the loop".** A rule phrased as a
prohibition on techniques would be both too strong and too weak — too strong because a language
model summarising a Report is harmless, too weak because a deterministic script could equally
select an algorithm and present it as a finding. The question AP-7 asks is who is answerable for
the scientific claim, and this system already has a moment where that transfers: locking. Putting
the boundary there means the rule is checkable by looking at a call graph rather than by judging
intent.

**Why "carries its own grounds for rejection" rather than "is explainable".** Explainability is a
property people assert about their systems. What AP-4 actually requires is that a conclusion can
be *contested*, which needs specific material: the inputs, the intermediate values, and the rule
being applied. Naming the material makes the requirement testable — an output either ships its
attributions or it does not.

**Why this does not gut the roadmap.** Most of Phase 3a is unaffected: the MCP server, the graph,
the planner, the executor and the analyst all operate below the boundary. What changes is where
the cycle stops and what the outputs carry. That is a real constraint on IMPL-035 and IMPL-041,
and a small one on the rest.

**Why decide it now, when the container is deferred.** Because the alternative is the pattern that
produced the C3 layer: a design written out in detail before anyone checked whether it was allowed
to exist, then discovered later at the cost of rewriting. ADR-028 removed sixty-one documents to
that effect. Deciding the constraint before Phase 3a starts costs one ADR.

**Trade-offs accepted.** An autonomous cycle that stops for a human is less autonomous, and the
weekly cron of IMPL-041 becomes a proposal queue rather than a research programme. That is the
point of the decision rather than a side effect of it. Shipping attributions with every prediction
also costs implementation effort and output size, and a Pilot that could simply name the best
algorithm would be a more impressive demo — which is precisely what AP-7 identifies as the thing
this project exists not to build.

---

## Alternatives Considered

### Narrow the V3 scope instead

**Description:** drop the capabilities that sit closest to the line — the calibrated predictor
(IMPL-035), the autonomous cycle (IMPL-041), the shadow/canary deployment (IMPL-042) — and keep
the Pilot as an assistant for writing studies.

**Why rejected:** it answers the question by avoiding it, and the question returns for every future
capability. A rule that says where the boundary is lets each capability be judged against it,
including ones nobody has thought of yet. It is also more restrictive than necessary: a predictor
that ships its attributions and makes no recommendation is evidence, and evidence is what the
system is for.

**Under what conditions reconsidered:** if a capability turns out to have no permitted form —
if, on attempting to build it, every version of it decides something — then it leaves the roadmap.
That is a legitimate outcome and this ADR does not prejudge it.

### Defer the decision until Phase 3a opens

**Description:** leave REF-TASK-0047 open with a note not to start IMPL-028 before closing it.

**Why rejected:** the argument for deferring is that V2 has to exist before it is clear which V3
capabilities are real. The argument against is the C3 layer: a design spelled out before anyone
checked whether it was permitted, discovered at the cost of deleting it. The constraint is
cheaper to state than the rewrite is to perform, and stating it does not require knowing which
capabilities survive.

### Treat the Pilot as outside the MANIFESTO

**Description:** the anti-patterns constrain the benchmarking system; the Pilot is a separate tool
that happens to call it.

**Why rejected:** AP-7 is about what reaches the researcher, not about which module produced it. A
recommendation is no less a recommendation for arriving through a chat interface, and the C1
exclusions are stated for the system as a whole.

---

## Consequences

**Positive:**

- Every Phase 3a and 3b task can be judged against a stated rule instead of against an intuition.
- The boundary is a call, `cc.lock_study()`, so conformance is visible in a call graph rather than
  argued from intent.
- The MANIFESTO stops being a document the roadmap quietly contradicts.

**Negative / Trade-offs:**

- IMPL-041 becomes a proposal queue rather than an autonomous programme, and IMPL-035 loses its
  confidence gate.
- Shipping attributions with every prediction costs effort and output size.
- A more impressive demo is foregone, deliberately.

**Risks:**

- **Risk:** a capability drifts across the boundary during implementation, because the permitted
  and forbidden forms differ by a design detail rather than by a feature.
  **Mitigation:** the boundary is `cc.lock_study()`, which is one call and can be asserted against
  in a test. The rest is a review obligation, and this ADR is the record to review against.
- **Risk:** "carries its own grounds for rejection" is applied as a checkbox and satisfied with an
  attribution nobody can read.
  **Mitigation:** none offered here, honestly. It is a quality judgement and no rule makes it
  automatic.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/01-manifesto/MANIFESTO.md` | AP-4 and AP-7, which this ADR reconciles the roadmap with |
| `02-c4-leve1-context/01-c4-l1-context/01-c1-context.md` | Explicit Scope Exclusions, where both become design exclusions |
| `05-constraints/02-const-scientific.md` | Where the exclusions become constraints on every API path |
| `03-c4-leve2-containers/14-corvus-pilot.md` | The deferred container this constrains |
| `adr-013-study-lifecycle-draft-then-locked.md` | Supplies the boundary: locking is where commitment happens |
| `adr-021-pre-registered-hypotheses-mandatory.md` | The argument reused here — a constraint stated after the fact is not a constraint |
| `docs/ROADMAP.md` | IMPL-026, IMPL-035, IMPL-037, IMPL-038, IMPL-041 gain the constraint |
