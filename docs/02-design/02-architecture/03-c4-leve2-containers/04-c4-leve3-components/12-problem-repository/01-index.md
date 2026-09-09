# C3: Components — Problem Repository

> C2 Container: [11-problem-repository.md](../../11-problem-repository.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

The Problem Repository stores Problem Instances under the same identity model as the Algorithm
Registry: validated once, immutable afterwards, superseded rather than edited (ADR-020).

Its validation carries more weight than the registry's, because a Problem Instance is where the
scientific claim of a Study is grounded. FR-02 checks the instance itself; FR-32 and FR-33 check
the *set* an entire Study proposes to use, against the diversity floor of ADR-009.

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| Instance Validator | Applies the registration rules — dimension agreement, variable bounds, required provenance | FR-01, FR-02; [`02-problem-instance.md`](../../../../../03-technical-contracts/01-data-format/02-problem-instance.md) |
| Supersession Manager | Records the lineage between an instance and the registration that replaces it | ADR-020; [`06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |
| Entity Store | Persists instances and resolves identifiers | [`06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |

---

## Where the vocabulary comes from

| Subject | Contract |
|---|---|
| Problem Instance fields and validation rules | [`01-data-format/02-problem-instance.md`](../../../../../03-technical-contracts/01-data-format/02-problem-instance.md) |
| `register_problem`, `get_problem`, `list_problems`, `deprecate_problem` | [`02-interface-contracts/06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |
| The interface a registered problem must satisfy | [`02-interface-contracts/02-problem-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/02-problem-interface.md) |
| The diversity floor a Study's problem set must clear | ADR-009 D-1 … D-3; cross-entity rule `CV-021` |

The diversity check belongs to the Study Orchestrator, not here: it is a property of a Study's
problem *set*, and this container knows only about instances.
