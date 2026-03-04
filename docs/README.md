# The Narrative Flow (reading hints)

## For system design (what we are building here)
[MANIFESTO](../docs/01_manifesto/MANIFESTO.md) → SRS → C1 → C2 → C3 → C4 → **Docstrings** (code)

## Technical contracts (how components speak to each other)
[C2](../docs/02_design/02_architecture/c2-containers.md)/[C3](../docs/02_design/02_architecture/c3-components.md) → [interface contracts](../docs/03_technical_contracts/interface-contracts.md) → [data format](../docs/03_technical_contracts/data-format.md) → [C4](../docs/02_design/02_architecture/c4-code.md) → Docstrings

## Scientific practice (how to use it)
[MANIFESTO](../docs/01_manifesto/MANIFESTO.md) → [benchmarking protocol](../docs/04_scientific_practice/methodology/benchmarking-protocol.md) → [statistical methodology](../docs/04_scientific_practice/methodology/statistical-methodology.md) → [metric taxonomy](../docs/03_technical_contracts/metric-taxonomy.md)

## Community (how it grow!)
[MANIFESTO](../docs/01_manifesto/MANIFESTO.md) → [contribution guide](../docs/05_community/contribution-guide.md) → [versioning governance](../docs/05_community/versioning-governance.md) → [interface contracts](../docs/03_technical_contracts/interface-contracts.md) → [data format](../docs/03_technical_contracts/data-format.md)

Each template has three structural features that maintain the story:
1. **STORY ROLE** — what chapter is this in the narrative?
2. **CONNECTS TO** — explicit bidirectional links to other documents
3. **Docstring/task bridge** — every template explicitly states where the documentation story hands off to code docstrings and to issue tracker tasks, so the three documentation layers (docs, docstrings, tasks) form a single coherent system rather than three independent silos.
