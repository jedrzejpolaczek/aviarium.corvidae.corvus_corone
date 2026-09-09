# C3: Components — Results Store

> C2 Container: [12-results-store.md](../../12-results-store.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

The Results Store is the only component in the system that touches persistent storage. Everything
else reaches it through the repository interface, which is what makes the V1 local-file backend
replaceable by a V2 server without changing a single caller (ADR-001).

Performance Records are written twice over: JSON Lines during the Run, and Parquet afterwards when
a Run is large enough for the columnar format to pay for itself (ADR-010). The JSON Lines file is
never deleted; it stays the source of truth.

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| Local File Repository | Implements the repository interface against a directory tree, and owns the layout, which is not part of the interface | ADR-001; [`06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |
| Entity Store | Reads and writes the seven entity types as JSON | [`01-data-format/`](../../../../../03-technical-contracts/01-data-format/01-index.md) |
| Performance Record Writer | Appends a record for each fired trigger during a Run, and converts to the bulk format afterwards | ADR-002, ADR-010; [`10-file-formats.md`](../../../../../03-technical-contracts/01-data-format/10-file-formats.md) |
| Performance Record Reader | Serves records from whichever format is present, so that callers cannot tell which was used | [`10-file-formats.md`](../../../../../03-technical-contracts/01-data-format/10-file-formats.md) |

---

## Where the vocabulary comes from

| Subject | Contract |
|---|---|
| Every repository method, its preconditions and its exceptions | [`02-interface-contracts/06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |
| Directory layout, JSON Lines and Parquet formats, round-trip invariant | [`01-data-format/10-file-formats.md`](../../../../../03-technical-contracts/01-data-format/10-file-formats.md) |
| The seven entity schemas | [`01-data-format/01-index.md`](../../../../../03-technical-contracts/01-data-format/01-index.md) |
| Cross-entity rules `CV-001` … `CV-023` | [`01-data-format/12-cross-entity-validation.md`](../../../../../03-technical-contracts/01-data-format/12-cross-entity-validation.md) |

Entities are immutable. A revision is a new entity with a new UUID, and the superseded one carries
`superseded_by`; deprecation is the only write a stored entity ever receives (ADR-020).

