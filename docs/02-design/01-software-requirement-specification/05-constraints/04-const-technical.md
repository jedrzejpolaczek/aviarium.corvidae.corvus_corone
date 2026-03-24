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

## CONST-TECH-04

**The library MUST support Python 3.10, 3.11, and 3.12. Python 3.9 and earlier MUST NOT be listed as supported. CI MUST run on all three versions and all three must pass before a release.**

- Source: ADR-006
- Connects to: `docs/02-design/02-architecture/01-adr/adr-006-python-version-and-platform-constraints.md`

## CONST-TECH-05

**Linux (x86-64) and macOS (arm64 and x86-64) are the primary supported platforms; CI failures on either are release blockers. Windows (x86-64) is supported on a best-effort basis; CI runs on Windows but failures are non-blocking.**

- Source: ADR-006
- Connects to: `docs/02-design/02-architecture/01-adr/adr-006-python-version-and-platform-constraints.md`

## CONST-TECH-06

**The runtime dependency tree MUST NOT include packages distributed under GPL-2.0-only, GPL-3.0-only, AGPL-3.0, or equivalent copyleft licenses that would make the combined work GPL. Permissive licenses (MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, ISC, PSF-2.0) and LGPL with dynamic linking are permitted. A `licensecheck` step in CI MUST fail the build if a GPL-only dependency is introduced.**

- Source: ADR-006; CONST-COM-01
- Connects to: `docs/02-design/02-architecture/01-adr/adr-006-python-version-and-platform-constraints.md`; `docs/02-design/01-software-requirement-specification/05-constraints/03-const-community.md` CONST-COM-01

## CONST-TECH-07

**The core runtime dependency set is: `numpy>=1.24`, `scipy>=1.11`, `pydantic>=2.0`, `click>=8.1`, `matplotlib>=3.7`. No runtime dependency may be added without an ADR or a documented justification in the PR description. Pydantic v1 compatibility is explicitly NOT maintained.**

- Source: ADR-006
- Connects to: `docs/02-design/02-architecture/01-adr/adr-006-python-version-and-platform-constraints.md`

---

**Connects to:**
- `docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md` — source of CONST-TECH-01, 02, 03
- `docs/02-design/02-architecture/01-adr/adr-006-python-version-and-platform-constraints.md` — source of CONST-TECH-04, 05, 06, 07
- `docs/02-design/01-software-requirement-specification/03-functional-requirements/06-fr-4.5-reproducibility-layer.md` — FR-17, FR-19 enforce CONST-TECH-01, CONST-TECH-03
