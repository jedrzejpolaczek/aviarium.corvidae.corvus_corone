# C3: Components — Algorithm Registry

> C2 Container: [10-algorithm-registry.md](../../10-algorithm-registry.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

The Algorithm Registry stores Algorithm Instances and serves them by identifier. An instance is
validated once, at registration, and is immutable afterwards: a revision is a new entity with a
new UUID, and the old one records `superseded_by` (ADR-020).

That immutability is what makes an archived Run reproducible. The UUID it references never changes
meaning, so `get_algorithm(id)` returns the same bytes forever — including for deprecated
instances, which only disappear from listings.

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| Instance Validator | Applies the registration rules, including the pinned `code_reference` and the non-empty configuration justification | FR-05 – FR-07; [`03-algorithm-instance.md`](../../../../../03-technical-contracts/01-data-format/03-algorithm-instance.md) |
| Supersession Manager | Records the lineage between an instance and the registration that replaces it | ADR-020; [`06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |
| Entity Store | Persists instances and resolves identifiers | [`06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |

---

## Where the vocabulary comes from

| Subject | Contract |
|---|---|
| Algorithm Instance fields, including `deprecated`, `deprecation_reason` and `superseded_by` | [`01-data-format/03-algorithm-instance.md`](../../../../../03-technical-contracts/01-data-format/03-algorithm-instance.md) |
| `register_algorithm`, `get_algorithm`, `list_algorithms`, `deprecate_algorithm` | [`02-interface-contracts/06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |
| The interface a registered algorithm must satisfy | [`02-interface-contracts/03-algorithm-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/03-algorithm-interface.md) |

Supersession is a lineage, not a graph: `superseded_by` must resolve to another Algorithm Instance,
must not be the entity itself, and must not close a cycle. The repository contract states the
preconditions.

