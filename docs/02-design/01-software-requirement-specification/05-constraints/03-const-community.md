# Community Constraints

*Govern how Artifacts produced by the system are licensed and distributed.*
*Source: MANIFESTO Principles 20, 22.*

---

## CONST-COM-01

**All source code MUST be released under an open source license.**

- Source: MANIFESTO Principle 20
- Operationalized in: Licensing ADR (→ REF-TASK-0011)

## CONST-COM-02

**All experimental data and results produced by the system MUST be publishable under an open data license.**

- Source: MANIFESTO Principle 20
- Operationalized in: `docs/05-community/02-versioning-governance.md` §5

## CONST-COM-03

**All data formats used for archival MUST be open, well-documented, and readable without proprietary tools.**

- Source: MANIFESTO Principle 22
- Operationalized in: `docs/03-technical-contracts/01-data-format/01-index.md` §3
- Enforced by: FR-22 (Raw Data export format must comply with this constraint)

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — Principles 20, 22
- `docs/05-community/02-versioning-governance.md` — §5 (licensing policy)
- `docs/02-design/01-software-requirement-specification/04-non-functional-requirements/05-nfr-open-01.md` — NFR-OPEN-01 operationalizes these constraints
- `docs/02-design/01-software-requirement-specification/03-functional-requirements/07-fr-4.6-reporting-and-visualization.md` — FR-22 enforces CONST-COM-03
