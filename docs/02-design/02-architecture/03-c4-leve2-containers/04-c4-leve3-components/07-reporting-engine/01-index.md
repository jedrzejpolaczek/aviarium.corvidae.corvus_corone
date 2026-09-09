# C3: Components — Reporting Engine

> C2 Container: [05-reporting-engine.md](../../05-reporting-engine.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

The Reporting Engine produces exactly two Reports per completed Experiment, one for a Researcher
and one for a Practitioner (ADR-019). They are not two views of one document: the practitioner
report deliberately omits the statistical tables the researcher report exists to show.

Output is HTML in V1 (SRS §1.4, boundary B-03). Every Report carries a scope statement and a
limitations section, and no Report may contain a ranking or a "best algorithm" claim — FR-21 and
the scientific constraints make that a property the engine enforces rather than a convention it
follows.

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| Result Reader | Loads the aggregates, entities and records a Report needs | [`06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |
| Mandatory Visualization Renderer | Produces the four charts every Report must contain | ADR-011, ADR-018; `02-statistical-methodology.md` §2.1 |
| Template Renderer | Assembles each audience's document from the sections that audience gets | ADR-019; `03-report-format-spec.md` |
| Limitations Enforcer | Refuses to emit a Report missing a mandatory section | FR-21; `03-report-format-spec.md` |

---

## Where the vocabulary comes from

| Subject | Contract |
|---|---|
| Report entity fields | [`01-data-format/09-report.md`](../../../../../03-technical-contracts/01-data-format/09-report.md) |
| Section structure and audience language | `03-c4-leve2-containers/03-report-format-spec.md` (authoritative for this surface, per ADR-026) |
| The `VIZ-L1-NN` identifiers and what each chart shows | `04-scientific-practice/01-methodology/02-statistical-methodology.md` §2.1 (authoritative, per ADR-026) |
| Rendering libraries | ADR-011 |

Trajectory and parameter-sensitivity plots are **not** Report visualizations. They answer a
question about an algorithm's mechanism rather than about a comparison, and they belong to the
deferred Algorithm Visualization Engine (ADR-018).


---

## Open decisions

- **REF-TASK-0043** — the Level 3 section of every researcher report is specified by §4 of
  `02-statistical-methodology.md`, which has no content.
