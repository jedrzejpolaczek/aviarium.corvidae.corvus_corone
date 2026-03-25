# External System: COCO (Comparing Continuous Optimizers)

> C1 Context: [../01-c1-context.md](../01-c1-context.md)

**What it is:** A widely-used benchmark framework for continuous black-box optimization, maintained by the COCO community. Defines standard problem suites (BBOB) and a performance analysis workflow.

**Why we interact with it:** Interoperability (MANIFESTO Principle 26). Researchers already use COCO; publishing results in COCO-compatible format enables cross-study comparisons.

**Direction:** Outbound export — our system produces data exportable to COCO's format. Import of COCO problem definitions is a secondary use case.

**Risk:** COCO's data format evolves. If incompatible changes are made, the export mapping must be updated. Format mapping is documented in `docs/03-technical-contracts/data-format.md` §3.

> **`TODO: REF-TASK-0005`** — Define the COCO format mapping in `data-format.md` §3 when the
> internal data format is finalized. Owner: ecosystem integration lead. Acceptance: a study result
> can be exported and loaded by COCO's analysis tools without data loss beyond documented mappings.
