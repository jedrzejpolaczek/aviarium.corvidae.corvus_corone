# Non-Functional Requirements — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: The quality attributes the system must exhibit across all functional behaviours.
NFRs are not about what the system does, but how well it does it — and what it must never violate.

NARRATIVE POSITION:
  MANIFESTO (WHY) → NFRs (quality constraints on HOW the system behaves)
  NFRs → Acceptance Tests (measurable pass/fail criteria)
  NFRs → Functional Requirements (FRs that enforce each NFR)

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                                         : source principles
  ← use-cases.md                                                            : which UCs exercise each NFR
  → functional-requirements.md                                              : FRs that enforce each NFR
  → constraints.md                                                          : community constraints overlap NFR-OPEN-01
  → acceptance-test-strategy.md                                             : test category per NFR
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md : NFR-STAT-01 operationalized
  → docs/05-community/02-versioning-governance.md                          : NFR-REPRO-01 and NFR-OPEN-01
  → docs/03-technical-contracts/02-interface-contracts.md                  : NFR-MODULAR-01 operationalized
  → docs/03-technical-contracts/01-data-format.md §4                       : NFR-INTEROP-01 operationalized

NOTE ON MEASURABLE CRITERIA:
  All criteria marked TODO: REF-TASK-0010 are pending architectural decisions.
  When REF-TASK-0010 is resolved, replace each TODO with a concrete number, threshold, or
  automated test condition that can be evaluated without human judgment.
-->

---

## NFR Index

| ID | Quality Attribute | Source | Test Category | File |
|---|---|---|---|---|
| NFR-REPRO-01 | Reproducibility | MANIFESTO 19–22 | Reproducibility | [02-nfr-repro-01.md](02-nfr-repro-01.md) |
| NFR-STAT-01 | Statistical Validity | MANIFESTO 13, 15 | Statistical validity | [03-nfr-stat-01.md](03-nfr-stat-01.md) |
| NFR-INTEROP-01 | Ecosystem Interoperability | MANIFESTO 26 | Interoperability | [04-nfr-interop-01.md](04-nfr-interop-01.md) |
| NFR-OPEN-01 | Open Data and Code | MANIFESTO 20, 22 | Open format compliance | [05-nfr-open-01.md](05-nfr-open-01.md) |
| NFR-MODULAR-01 | Extensibility | MANIFESTO Value 6, 27 | Plugin | [06-nfr-modular-01.md](06-nfr-modular-01.md) |
| NFR-USABILITY-01 | Minimal Onboarding Friction | MANIFESTO 28 | Usability | [07-nfr-usability-01.md](07-nfr-usability-01.md) |
