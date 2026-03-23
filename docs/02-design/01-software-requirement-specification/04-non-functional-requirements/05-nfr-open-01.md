# NFR-OPEN-01 — Open Data and Code

*All experimental data, algorithm code, and analysis scripts are publicly available under open licenses in standardized, well-documented formats.*
*Source: MANIFESTO Principles 20, 22.*
*Use Cases: UC-01, UC-04.*

---

## NFR-OPEN-01

**All experimental data, algorithm code, and analysis scripts MUST be publicly available under open licenses in standardized, well-documented formats readable without proprietary tools.**

- **Source:** MANIFESTO Principles 20, 22
- **Measurable criterion:** (1) All Raw Data exports are valid JSON or CSV parseable by the Python standard library (`json` or `csv` module) with no additional dependencies. (2) All files under `packages/` carry an approved open source license header (verified by `licensecheck` or equivalent CI check). (3) No output format produced by the system requires a proprietary tool to parse — verified by the open format compliance test category, which attempts to read each output format using only OSI-approved open source tools.
- **Operationalized in:** `docs/05-community/02-versioning-governance.md` §5
- **Exercises:** UC-01 (postcondition: Raw Data export available in open format); UC-04 (contributed Problem Instance published openly)
- **Tested by:** License and format compliance checks — verify all output formats are on the approved open-format list; verify license headers on code artifacts
- **Enforced by:** FR-22 (Raw Data export in open format), CONST-COM-01, CONST-COM-02, CONST-COM-03 (→ `docs/02-design/01-software-requirement-specification/05-constraints/01-constraints.md`)
