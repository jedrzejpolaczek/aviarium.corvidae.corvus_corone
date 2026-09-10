# C3: Components — Study Orchestrator

> C2 Container: [07-study-orchestrator.md](../../07-study-orchestrator.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

The Study Orchestrator is where a Study becomes an Experiment. It validates the plan and locks it,
walks the run plan in order, and triggers analysis and reporting once the plan is exhausted.

Locking is the moment pre-registration takes effect and is an explicit act, not a side effect of
creating the Study (ADR-013). Everything the orchestrator refuses at that moment it must also
explain: FR §4.8 requires it to report every unresolved decision at once, name the rule each
message enforces, and state the remedies.

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| Study Builder | Validates the plan, applies the cross-entity rules, and performs the draft-to-locked transition | ADR-013, ADR-021; [`12-cross-entity-validation.md`](../../../../../03-technical-contracts/01-data-format/12-cross-entity-validation.md) |
| Execution Coordinator | Walks the run plan in order, one Run at a time, and records each outcome | ADR-017, ADR-027; SRS §1.4 B-01 |
| Post-Execution Pipeline | Triggers the Analysis Engine and then the Reporting Engine once the plan is exhausted | [`05-analyzer-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/05-analyzer-interface.md), ADR-019 |

---

## Where the vocabulary comes from

| Subject | Contract |
|---|---|
| Study, Experiment and Run fields and their status enumerations | [`01-data-format/`](../../../../../03-technical-contracts/01-data-format/01-index.md) |
| Validation performed at lock time, `CV-018` and `CV-021` among them | [`01-data-format/12-cross-entity-validation.md`](../../../../../03-technical-contracts/01-data-format/12-cross-entity-validation.md) |
| Repository access, through a factory rather than individual repositories | [`02-interface-contracts/06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) |
| Exception classes raised at the boundary | [`02-interface-contracts/07-cross-cutting-contracts.md`](../../../../../03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md) |

The run-plan order — problem index, then algorithm index, then repetition index — is not an
implementation detail: it is the order `SeedSequence` children are spawned in, so it is what makes
a Study reproducible from its `root_seed` alone (ADR-017).
