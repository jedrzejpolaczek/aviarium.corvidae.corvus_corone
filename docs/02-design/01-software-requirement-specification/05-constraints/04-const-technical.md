# Technical Constraints

*Govern platform, language, and dependency decisions. Each decision that narrows the technical space MUST be recorded as an ADR in `docs/02-design/02-architecture/01-adr/`.*
*Source: ADR-001.*

---

## CONST-TECH-01

**The primary data layer MUST be implemented as a `Repository` interface abstraction that can be satisfied by both a local file implementation (V1) and a server database implementation (V2) without schema migration.**

- Source: ADR-001
- Connects to: `docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md`

## CONST-TECH-02

**All entity schemas MUST be JSON-serializable in their primary representation; binary secondary representations (e.g., Parquet) are permitted for bulk data only.**

- Source: ADR-001
- Connects to: `docs/03-technical-contracts/01-data-format.md` §1

## CONST-TECH-03

**All entity IDs MUST be UUID format; no local file paths may serve as entity identifiers.**

- Source: ADR-001
- Enforced by: FR-17 (UUID on every entity), FR-19 (cross-entity references use IDs only)
- Connects to: `docs/03-technical-contracts/01-data-format.md` §1

---

## Pending Technical Decisions

*(REF-TASK-0011 — each decision below requires an ADR when resolved)*

| Decision area | Status | Notes |
|---|---|---|
| Python version minimum | Pending ADR | Must support the Python versions used by target research environments |
| OS support targets | Pending ADR | Linux required (HPC/server); Windows and macOS for local development |
| Dependency restrictions | Pending ADR | Avoid GPL-only dependencies if MIT/Apache license is targeted |
| Execution platform targets | Pending ADR | Local multiprocessing (V1); HPC/Cloud (V2 Horizon) |

**Connects to:**
- `docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md` — source of CONST-TECH-01, 02, 03
- `docs/02-design/02-architecture/01-adr/` — future ADRs for pending decisions
- `docs/02-design/01-software-requirement-specification/03-functional-requirements/06-fr-4.5-reproducibility-layer.md` — FR-17, FR-19 enforce CONST-TECH-01, CONST-TECH-03
