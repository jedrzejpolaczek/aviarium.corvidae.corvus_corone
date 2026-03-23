# NFR-INTEROP-01 — Ecosystem Interoperability

*Results can be exported to COCO, Nevergrad, and IOHprofiler formats without data loss beyond the documented field mappings.*
*Source: MANIFESTO Principle 26.*
*Use Cases: UC-06.*

---

## NFR-INTEROP-01

**Results MUST be exportable to COCO, Nevergrad, and IOHprofiler formats without data loss beyond the documented field mappings in `docs/03-technical-contracts/01-data-format.md` §4.**

- **Source:** MANIFESTO Principle 26
- **Measurable criterion:** (1) IOHprofiler: `export(experiment, "iohprofiler")` produces a `.dat` file that loads in IOHanalyzer (or a stub format validator) without error. (2) COCO: `export(experiment, "coco")` produces a `.zip` archive accepted by COCO post-processing scripts without error. (3) Every `export()` call returns a non-empty `information_loss_manifest` — if the manifest is empty for any supported format, the test fails. (4) No export silently drops fields; every dropped field appears in the manifest.
- **Operationalized in:** `docs/03-technical-contracts/01-data-format.md` §4 (Interoperability Mappings)
- **Exercises:** UC-06 (full export flow for each supported platform)
- **Tested by:** Interoperability tests — export a known Experiment to each platform format; verify loadability in the target tool; compare field values against expected mapping
- **Enforced by:** FR-23 (COCO export), FR-24 (IOHprofiler export), FR-25 (Nevergrad adapter), FR-26 (information-loss manifest)
