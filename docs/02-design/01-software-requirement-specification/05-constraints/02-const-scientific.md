# Scientific Constraints

*Hard guards against the most common ways benchmarking systems become scientifically invalid.*
*Source: MANIFESTO anti-patterns 1, 3, 4, 6, 7; Principle 3.*
*Anti-patterns are defined in `docs/02-design/02-architecture/02-c1-context.md` (Explicit Scope Exclusions).*
*(REF-TASK-0032 — reconcile anti-pattern numbering; add anti-patterns section to MANIFESTO.)*

---

## CONST-SCI-01

**The system MUST NOT produce or display global algorithm rankings or "best algorithm" declarations.**

- Anti-pattern: 1 (Algorithm ranking)
- Prevents: False extrapolation as in UC-03 F1
- Enforced by: FR-21

## CONST-SCI-02

**The system MUST NOT support competition-style scoring or leaderboard features.**

- Anti-pattern: 3 (Competition)
- Prevents: Misuse as a marketing or competition tool
- Enforced by: Design exclusion — no ranking API

## CONST-SCI-03

**The system MUST NOT make algorithm selection decisions on behalf of the user; it produces evidence, not recommendations.**

- Anti-pattern: 7 (Substitute for thinking)
- Prevents: Replacing researcher judgment with automated selection
- Enforced by: Design exclusion — no recommendation API; UC-03 Step 6 (Practitioner selects, system does not)

## CONST-SCI-04

**Every analysis step performed by the system MUST be inspectable, documented, and reproducible by the user independently.**

- Anti-pattern: 4 (Black box)
- Prevents: Opacity in analysis outputs
- Enforced by: FR-15, FR-16 (three-level analysis with inspectable outputs)

## CONST-SCI-05

**Every generated report MUST include an explicit limitations section stating the scope conditions of conclusions.**

- Anti-pattern: 6 (Marketing tool)
- Prevents: Reports that overstate generality of findings
- Enforced by: FR-21

## CONST-SCI-06

**Conclusions in any system-generated output MUST be scoped to the Problem Instances actually tested; extrapolations MUST be explicitly labeled.**

- Source: Principle 3
- Prevents: Silent extrapolation beyond tested scope
- Enforced by: FR-21; UC-01 postconditions

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — anti-patterns and Principle 3
- `docs/02-design/02-architecture/02-c1-context.md` — Explicit Scope Exclusions (anti-pattern definitions)
- `docs/02-design/01-software-requirement-specification/03-functional-requirements/07-fr-4.6-reporting-and-visualization.md` — FR-21 enforces CONST-SCI-05 and CONST-SCI-06
- `docs/02-design/01-software-requirement-specification/02-use-cases/04-uc-03.md` — UC-03 Step 6 enforces CONST-SCI-03
