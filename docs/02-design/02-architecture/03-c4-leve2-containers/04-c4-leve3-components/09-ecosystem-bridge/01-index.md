# C3: Components — Ecosystem Bridge

> C2 Container: [13-ecosystem-bridge.md](../../13-ecosystem-bridge.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

The Ecosystem Bridge is how a Corvus Experiment reaches the tools researchers already use. It
exports to COCO and IOHprofiler, and imports optimizers from Nevergrad; V1 does not read either
archive format back (SRS §1.4, boundary B-04).

Every export returns an information-loss manifest, and the manifest is never empty. That is the
point of it: a caller who receives a file with no warning attached cannot tell a faithful export
from a lossy one, and FR-24 makes the manifest a precondition of the export rather than a
commentary on it.

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| COCO Exporter | Writes the COCO archive formats, with the known losses declared | FR-23 – FR-26; [`11-interoperability-mappings.md`](../../../../../03-technical-contracts/01-data-format/11-interoperability-mappings.md) §4.1 |
| IOH Exporter | Writes the IOHprofiler formats and the sidecar carrying what they cannot hold | [`11-interoperability-mappings.md`](../../../../../03-technical-contracts/01-data-format/11-interoperability-mappings.md) §4.2 |
| Nevergrad Adapter | Presents a Nevergrad optimizer through the Algorithm Interface | [`03-algorithm-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/03-algorithm-interface.md); [`11-interoperability-mappings.md`](../../../../../03-technical-contracts/01-data-format/11-interoperability-mappings.md) §4.3 |
| Loss Auditor | Assembles the manifest and blocks an export whose losses exceed what the caller accepted | FR-24, FR-25 |

---

## Where the vocabulary comes from

| Subject | Contract |
|---|---|
| Field-by-field mappings and every `LOSS-*` manifest item | [`01-data-format/11-interoperability-mappings.md`](../../../../../03-technical-contracts/01-data-format/11-interoperability-mappings.md) |
| File formats produced | [`01-data-format/10-file-formats.md`](../../../../../03-technical-contracts/01-data-format/10-file-formats.md) |
| Exception classes for unsupported formats and incomplete source data | [`02-interface-contracts/07-cross-cutting-contracts.md`](../../../../../03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md) |
| Interface requirements per external system | `01-software-requirement-specification/06-interface-requirements/01-index.md` |

The IOHprofiler `raw_y` column reads `PerformanceRecord.best_so_far`, and the COCO current-value
column reads `objective_value`. The two are different fields, which is why ADR-023 was able to
withdraw a documented information loss rather than add one.

