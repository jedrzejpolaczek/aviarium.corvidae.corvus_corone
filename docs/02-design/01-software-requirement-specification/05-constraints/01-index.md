# Constraints — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: Hard boundaries on what the system must and must not do.
Constraints are not design preferences — they are invariants derived from scientific ethics,
community commitments, and architectural decisions. Violating a constraint is not a trade-off;
it is a disqualification.

NARRATIVE POSITION:
  MANIFESTO anti-patterns → Scientific Constraints (what the system must never become)
  MANIFESTO Principles 20, 22 → Community Constraints (licensing and openness)
  ADR-001 → Technical Constraints (platform and schema invariants)

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                                          : anti-patterns and principles
  ← docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md                        : anti-pattern definitions in Scope Exclusions
  ← docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md : CONST-TECH-01–03
  → functional-requirements.md                                              : FRs that enforce each constraint
  → non-functional-requirements.md                                          : NFR-OPEN-01 operationalizes community constraints
  → docs/05-community/02-versioning-governance.md                          : licensing policy
  → docs/02-design/02-architecture/01-adr/                                 : pending technical constraint ADRs
-->

---

## Constraint Groups

| Group | Constraints | Source | File |
|---|---|---|---|
| Scientific | CONST-SCI-01..06 | MANIFESTO anti-patterns | [02-const-scientific.md](02-const-scientific.md) |
| Community | CONST-COM-01..03 | MANIFESTO 20, 22 | [03-const-community.md](03-const-community.md) |
| Technical | CONST-TECH-01..07 | ADR-001, ADR-006 | [04-const-technical.md](04-const-technical.md) |
