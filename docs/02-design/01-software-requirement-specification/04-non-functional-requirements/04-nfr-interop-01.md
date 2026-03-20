# NFR-INTEROP-01 — Ecosystem Interoperability

*Results can be exported to COCO, Nevergrad, and IOHprofiler formats without data loss beyond the documented field mappings.*
*Source: MANIFESTO Principle 26.*
*Use Cases: UC-06.*

---

## NFR-INTEROP-01

**Results MUST be exportable to COCO, Nevergrad, and IOHprofiler formats without data loss beyond the documented field mappings in `docs/03-technical-contracts/01-data-format.md` §4.**

- **Source:** MANIFESTO Principle 26
- **Measurable criterion:** `TODO: REF-TASK-0010` — round-trip test criteria per platform; information-loss manifest is produced for every export
- **Operationalized in:** `docs/03-technical-contracts/01-data-format.md` §4 (Interoperability Mappings)
- **Exercises:** UC-06 (full export flow for each supported platform)
- **Tested by:** Interoperability tests — export a known Experiment to each platform format; verify loadability in the target tool; compare field values against expected mapping
- **Enforced by:** FR-23 (COCO export), FR-24 (IOHprofiler export), FR-25 (Nevergrad adapter), FR-26 (information-loss manifest)
