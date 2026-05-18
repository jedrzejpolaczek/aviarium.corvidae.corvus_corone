# Documentation — Corvus Corone

## Reading Paths

### System design — what we are building
[MANIFESTO](01-manifesto/MANIFESTO.md)
→ [SRS](02-design/01-software-requirement-specification/01-srs/01-SRS.md)
→ [C1 Context](02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md)
→ [C2 Containers](02-design/02-architecture/03-c4-leve2-containers/01-index.md)
→ [C3 Components](02-design/02-architecture/04-c4-leve3-components/01-c4-l3-components/01-c4-l3-components.md)
→ [C4 Code](02-design/02-architecture/05-c4-level4-code/01-index.md)
→ Docstrings (code)

### Technical contracts — how components speak to each other
[C2](02-design/02-architecture/03-c4-leve2-containers/01-index.md)
/ [C3](02-design/02-architecture/04-c4-leve3-components/01-c4-l3-components/01-c4-l3-components.md)
→ [Interface contracts](03-technical-contracts/02-interface-contracts/01-index.md)
→ [Data format](03-technical-contracts/01-data-format/01-index.md)
→ [C4 Code](02-design/02-architecture/05-c4-level4-code/01-index.md)
→ Docstrings

### Scientific practice — how to use it
[MANIFESTO](01-manifesto/MANIFESTO.md)
→ [Benchmarking protocol](04-scientific-practice/01-methodology/01-benchmarking-protocol.md)
→ [Statistical methodology](04-scientific-practice/01-methodology/02-statistical-methodology.md)
→ [Metric taxonomy](03-technical-contracts/03-metric-taxonomy/01-index.md)

### Community — how it grows
[MANIFESTO](01-manifesto/MANIFESTO.md)
→ [Contribution guide](05-community/01-contribution-guide.md)
→ [Versioning governance](05-community/02-versioning-governance.md)
→ [Interface contracts](03-technical-contracts/02-interface-contracts/01-index.md)
→ [Data format](03-technical-contracts/01-data-format/01-index.md)

---

## Structure

```
docs/
├── MANIFESTO.md                    ← why this system exists; values and principles
├── GLOSSARY.md                     ← canonical term definitions
├── ROADMAP.md                      ← milestone plan
│
├── 01-manifesto/
│   └── MANIFESTO.md
│
├── 02-design/
│   ├── 01-software-requirement-specification/
│   │   ├── 01-srs/                 ← master SRS document
│   │   ├── 02-use-cases/           ← UC-01 through UC-11
│   │   ├── 03-functional-requirements/
│   │   ├── 04-non-functional-requirements/
│   │   ├── 05-constraints/
│   │   ├── 06-interface-requirements/
│   │   ├── 07-acceptance-test-strategy/
│   │   └── 08-traceability-matrix/
│   │
│   └── 02-architecture/
│       ├── 01-adr/                 ← Architecture Decision Records (ADR-001 … ADR-011)
│       ├── 02-c4-leve1-context/    ← C1: system context diagram
│       │   ├── 01-c4-l1-context/   ← main C1 diagram + actors + external systems
│       │   ├── 02-actors/          ← one file per actor (Researcher, Learner, …)
│       │   └── 03-external-systems/ ← one file per external system (COCO, Nevergrad, …)
│       ├── 03-c4-leve2-containers/ ← C2: container diagram + one file per container
│       ├── 04-c4-leve3-components/ ← C3: component diagrams + one file per component
│       │   ├── 01-c4-l3-components/ ← system-wide overview diagram
│       │   ├── 02-corvus-pilot/
│       │   ├── 03-experiment-runner/
│       │   ├── 04-analysis-engine/
│       │   ├── 05-results-store/
│       │   ├── 06-study-orchestrator/
│       │   ├── 07-reporting-engine/
│       │   ├── 08-algorithm-visualization-engine/
│       │   ├── 09-ecosystem-bridge/
│       │   ├── 10-public-api-cli/
│       │   ├── 11-algorithm-registry/
│       │   └── 12-problem-repository/
│       └── 05-c4-level4-code/      ← C4: architecturally significant code abstractions
│           ├── 01-index.md         ← overview diagram + scope table
│           ├── 02-shared/          ← cross-container Protocols and dataclasses
│           ├── 03-corvus-corone-pilot/
│           ├── 04-experiment-runner/
│           ├── 05-analysis-engine/
│           ├── 06-results-store/
│           └── 07-public-api-cli/
│
├── 03-technical-contracts/
│   ├── 01-data-format/             ← entity schemas, file formats, interoperability mappings
│   ├── 02-interface-contracts/     ← AlgorithmInterface, ProblemInterface, Repository, …
│   ├── 03-metric-taxonomy/         ← canonical metric definitions and selection guide
│   └── 04-public-api-contract.md   ← cc.* versioned public API surface
│
├── 04-scientific-practice/
│   └── 01-methodology/             ← benchmarking protocol, statistical methodology
│
├── 05-community/
│   ├── 01-contribution-guide.md
│   ├── 02-versioning-governance.md
│   └── 03-notes.md
│
└── 06-tutorials/
    ├── 01-cmd-first-study.md
    ├── 02-researcher-design-and-execute-study.md
    ├── 03-nevergrad-adapter.md
    ├── 04-algorithm-author-onboarding.md
    ├── uc-02-contribute-algorithm.md
    ├── 05-learner-socratic-mode.md
    ├── 06-learner-algorithm-visualization.md
    └── 07-learner-algorithm-genealogy.md
```

---

## Document conventions

Each document has three structural features that keep the documentation coherent across levels:

1. **STORY ROLE** — what chapter is this in the narrative, and what question does it answer?
2. **CONNECTS TO** — explicit bidirectional links to other documents at adjacent levels.
3. **Docstring / task bridge** — every document explicitly states where the documentation story hands off to code docstrings and to the issue tracker. This ensures docs, docstrings, and tasks form one coherent system rather than three independent silos.
