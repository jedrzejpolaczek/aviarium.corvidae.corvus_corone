# §2.8 Report

> Index: [docs/03-technical-contracts/01-data-format/01-index.md](01-index.md)

> See GLOSSARY: [Report](../../GLOSSARY.md#report)

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| id | string | yes | Report UUID (RFC 4122 v4) |
| schema_version | string | yes | Version of the entity schema this record conforms to, e.g. `0.0.3`. Governs the shape of the record, not the identity of the entity. See [13-schema-versioning.md](13-schema-versioning.md) |
| experiment_id | string | yes | UUID of the Experiment this Report was generated from |
| type | string | yes | `researcher` or `practitioner` |
| generated_at | datetime | yes | ISO 8601 UTC timestamp when the Report was produced |
| generated_by | string | yes | System version or component that produced this Report |
| limitations | string | yes | Mandatory limitations section: scope conditions of all conclusions, characteristics not covered, absence of global rankings (FR-21) |
| content_format | string | yes | Format of the report artifact. `html` in V1: reports are HTML only and PDF rendering is deferred (SRS §1.4 B-03) |
| artifact_reference | string | yes | Pointer to the stored report artifact (path or ID, resolved by the Repository) |

**Validation rules:**
- Every completed Experiment must have exactly one `researcher` Report and one `practitioner` Report (FR-20)
- `limitations` must be non-empty — a Report without a limitations section is invalid
- `artifact_reference` must be resolvable at the time the Report record is created
