# C3: Components — Algorithm Registry

> C2 Container: [10-algorithm-registry.md](../../10-algorithm-registry.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

The Algorithm Registry stores and serves Algorithm Instance registrations. Each instance is validated on registration and immutable thereafter; a revision is registered as a new entity and the old one records `superseded_by` (ADR-020). Reproducibility follows from the UUID in an archived Run never changing meaning.
Actors: Study Orchestrator and Public API read from it; developers register new instances during library development.

---

## Component Diagram

```mermaid
---
config:
  look: neo
  theme: redux-dark
  themeVariables:
    background: transparent
---
flowchart LR
  dev["Developer"] L_dev_iv@-- register --> iv

  subgraph AR["Algorithm Registry"]
    iv["Instance Validator\nValidates AlgorithmInstance\nschema on registration"]
    vm["Supersession Manager\nRecords superseded_by lineage\nEntities are immutable"]
    es["Entity Store\nPersists instances as JSON\nResolves IDs + deprecation"]
  end

  iv L_iv_vm@--> vm
  vm L_vm_es@--> es

  api["Public API\nStudy Orchestrator\nPilot MCP"] L_api_es@-- read --> es

  style AR fill:#161616,stroke:#46EDC8,color:#aaaaaa

  linkStyle 0 stroke:#FFD600,fill:none
  linkStyle 1,2 stroke:#46EDC8,fill:none
  linkStyle 3 stroke:#2962FF,fill:none

  L_dev_iv@{ animation: slow }
  L_iv_vm@{ animation: fast }
  L_vm_es@{ animation: fast }
  L_api_es@{ animation: fast }
```

---

## Components

| Component | File | Responsibility |
|---|---|---|
| Instance Validator | [02-instance-validator.md](02-instance-validator.md) | Validates AlgorithmInstance schema and required fields on registration |
| Supersession Manager | [03-supersession-manager.md](03-supersession-manager.md) | Records the `superseded_by` lineage between an entity and the registration that replaces it (ADR-020) |
| Entity Store | [04-entity-store.md](04-entity-store.md) | Persists algorithm instances as JSON; resolves IDs; supports the deprecation flag |

---

## Cross-Cutting Concerns

### Logging & Observability

One log entry per registration: `algorithm_id`, `registered_at`, `registered_by`. One log entry per deprecation: `algorithm_id`, `deprecated_at`, `reason`, `superseded_by`. All at INFO level.

### Error Handling

- `ValidationError`: raised by Instance Validator on schema violations. Lists all violations.
- `CodeReferenceError`: raised by Instance Validator when `code_reference` does not resolve or is not version-pinned (FR-06).
- `EntityNotFoundError`: raised by Entity Store when `get_algorithm(id)` finds no matching entry.

### Randomness / Seed Management

No random state. Registry is purely read/write storage.

### Configuration

The Registry reads its storage path from `CORVUS_REGISTRY_DIR` (env) or defaults to the package's bundled `data/algorithm_registry/` directory.

### Testing Strategy

All three components are unit-tested with fixture AlgorithmInstance objects. Integration tests verify round-trip registration and retrieval fidelity.
