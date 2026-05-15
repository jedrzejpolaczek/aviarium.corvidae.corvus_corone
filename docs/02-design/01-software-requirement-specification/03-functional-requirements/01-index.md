# Functional Requirements — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: The precise WHAT. Each FR states a verifiable capability the system must provide.
Every FR traces to a MANIFESTO principle and to at least one Use Case that exercises it.

NARRATIVE POSITION:
  MANIFESTO (WHY) → Use Cases (HOW actors interact) → Functional Requirements (WHAT system does)
  Functional Requirements → C2/C3 design (WHERE in the architecture it lives)
  Functional Requirements → Acceptance Tests (HOW we verify it)

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                         : each FR cites the principle that requires it
  ← 02-use-cases/01-index.md                               : each FR is exercised by at least one UC
  → docs/02-design/02-architecture/03-c4-leve2-containers/01-index.md : container responsible for each FR group
  → docs/03-technical-contracts/01-data-format/01-index.md : entity schemas that FRs operate on
  → docs/03-technical-contracts/02-interface-contracts/01-index.md : interfaces that implement FRs
  → docs/03-technical-contracts/03-metric-taxonomy/01-index.md : metrics required by §4.4 FRs
  → docs/04-scientific-practice/01-methodology/            : methodology documents that FRs operationalize
  → docs/05-community/02-versioning-governance.md          : versioning FRs connect here
  → 07-acceptance-test-strategy/01-acceptance-test-strategy.md : each FR has a designated test category
  → 08-traceability-matrix/01-traceability-matrix.md       : full cross-reference table

NOTE ON CONTAINER MAPPING:
  The subsection groupings (4.1–4.8) correspond to C2 container responsibilities defined in
  docs/02-design/02-architecture/03-c4-leve2-containers/01-index.md. Each FR group is in its own file.
-->

---

## FR Groups

| Group | Container | FRs | File |
|---|---|---|---|
| 4.1 Problem Repository | Problem Repository | FR-01..FR-04, FR-32, FR-33 | [02-fr-4.1-problem-repository.md](02-fr-4.1-problem-repository.md) |
| 4.2 Algorithm Registry | Algorithm Registry | FR-05..FR-07 | [03-fr-4.2-algorithm-registry.md](03-fr-4.2-algorithm-registry.md) |
| 4.3 Experiment Runner | Experiment Runner | FR-08..FR-12 | [04-fr-4.3-experiment-runner.md](04-fr-4.3-experiment-runner.md) |
| 4.4 Measurement & Analysis Engine | Analysis Engine | FR-13..FR-16 | [05-fr-4.4-measurement-and-analysis.md](05-fr-4.4-measurement-and-analysis.md) |
| 4.5 Reproducibility Layer | Results Store | FR-17..FR-19 | [06-fr-4.5-reproducibility-layer.md](06-fr-4.5-reproducibility-layer.md) |
| 4.6 Reporting & Visualization | Reporting Engine | FR-20..FR-22 | [07-fr-4.6-reporting-and-visualization.md](07-fr-4.6-reporting-and-visualization.md) |
| 4.7 Ecosystem Integration | Ecosystem Bridge | FR-23..FR-26 | [08-fr-4.7-ecosystem-integration.md](08-fr-4.7-ecosystem-integration.md) |
| 4.8 Learner Actor *(DEFERRED — Phase 4)* | Algorithm Visualization Engine, Corvus Pilot, Reporting Engine | FR-27..FR-31 | [09-fr-4.8-learner-actor.md](09-fr-4.8-learner-actor.md) |
