# Constraints — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: Hard boundaries on what the system must and must not do.
Constraints are not design preferences — they are invariants derived from scientific ethics,
community commitments, and architectural decisions. Violating a constraint is not a trade-off;
it is a disqualification.

NARRATIVE POSITION:
  MANIFESTO anti-patterns → Scientific Constraints (what the system must never become)
  MANIFESTO Principles 20, 22 → Community Constraints (licensing and openness)
  ADR-001 → Technical Constraints (platform and schema invariants)

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                                          : anti-patterns and principles
  ← docs/02-design/02-architecture/c1-context.md                           : anti-pattern definitions in Scope Exclusions
  ← docs/02-design/02-architecture/adr/ADR-001-library-with-server-ready-data-layer.md : CONST-TECH-01–03
  → functional-requirements.md                                              : FRs that enforce each constraint
  → non-functional-requirements.md                                          : NFR-OPEN-01 operationalizes community constraints
  → docs/05_community/versioning-governance.md                             : licensing policy
  → docs/02-design/02-architecture/adr/                                     : pending technical constraint ADRs
-->

---

## Scientific Constraints

These derive directly from MANIFESTO anti-patterns and are hard constraints — not design preferences. They guard against the most common ways benchmarking systems become scientifically invalid.

Anti-patterns are defined in `docs/02-design/02-architecture/c1-context.md` (Explicit Scope Exclusions). (`REF-TASK-0032` — reconcile anti-pattern numbering; add anti-patterns section to MANIFESTO.)

| Constraint | MANIFESTO Anti-Pattern | Statement | Prevents |
|---|---|---|---|
| CONST-SCI-01 | Anti-pattern 1 (Algorithm ranking) | The system MUST NOT produce or display global algorithm rankings or "best algorithm" declarations | `use-cases.md` UC-03 F1 (false extrapolation); enforced by FR-21 |
| CONST-SCI-02 | Anti-pattern 3 (Competition) | The system MUST NOT support competition-style scoring or leaderboard features | Misuse as a marketing tool |
| CONST-SCI-03 | Anti-pattern 7 (Substitute for thinking) | The system MUST NOT make algorithm selection decisions on behalf of the user; it produces evidence, not recommendations | `use-cases.md` UC-03 (Practitioner selects, system does not) |
| CONST-SCI-04 | Anti-pattern 4 (Black box) | Every analysis step performed by the system MUST be inspectable, documented, and reproducible by the user independently | Opacity in FR-15, FR-16 analysis outputs |
| CONST-SCI-05 | Anti-pattern 6 (Marketing tool) | Every generated report MUST include an explicit limitations section stating the scope conditions of conclusions | Enforced by FR-21 |
| CONST-SCI-06 | Principle 3 | Conclusions in any system-generated output MUST be scoped to the Problem Instances actually tested; extrapolations MUST be explicitly labeled | `use-cases.md` UC-01 postconditions; enforced by FR-21 |

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — anti-patterns and Principle 3
- `docs/02-design/02-architecture/c1-context.md` — Explicit Scope Exclusions (anti-pattern definitions)
- `functional-requirements.md`: FR-21 enforces CONST-SCI-05 and CONST-SCI-06
- `use-cases.md`: UC-03 main flow Step 6 enforces CONST-SCI-03

---

## Community Constraints

These govern how Artifacts produced by the system are licensed and distributed.

| Constraint | Source | Statement | Operationalized in |
|---|---|---|---|
| CONST-COM-01 | MANIFESTO Principle 20 | All source code MUST be released under an open source license | Licensing ADR (→ `REF-TASK-0011`) |
| CONST-COM-02 | MANIFESTO Principle 20 | All experimental data and results produced by the system MUST be publishable under an open data license | `docs/05_community/versioning-governance.md` §5 |
| CONST-COM-03 | MANIFESTO Principle 22 | All data formats used for archival MUST be open, well-documented, and readable without proprietary tools | `docs/03-technical-contracts/data-format.md` §3 |

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — Principles 20, 22
- `docs/05_community/versioning-governance.md` — §5 (licensing policy)
- `non-functional-requirements.md`: NFR-OPEN-01 operationalizes these constraints
- `functional-requirements.md`: FR-22 (Raw Data export format must comply with CONST-COM-03)

---

## Technical Constraints

These govern platform, language, and dependency decisions. Each decision that narrows the technical space MUST be recorded as an ADR in `docs/02-design/02-architecture/adr/`.

**Known constraints (established):**

| Constraint | Source | Statement |
|---|---|---|
| CONST-TECH-01 | ADR-001 | The primary data layer MUST be implemented as a `Repository` interface abstraction that can be satisfied by both a local file implementation (V1) and a server database implementation (V2) without schema migration |
| CONST-TECH-02 | ADR-001 | All entity schemas MUST be JSON-serializable in their primary representation; binary secondary representations (e.g., Parquet) are permitted for bulk data only |
| CONST-TECH-03 | ADR-001 | All entity IDs MUST be UUID format; no local file paths may serve as entity identifiers |

**Pending decisions (`REF-TASK-0011`):**

| Decision area | Status | Notes |
|---|---|---|
| Python version minimum | Pending ADR | Must support the Python versions used by target research environments |
| OS support targets | Pending ADR | Linux required (HPC/server); Windows and macOS for local development |
| Dependency restrictions | Pending ADR | Avoid GPL-only dependencies if MIT/Apache license is targeted |
| Execution platform targets | Pending ADR | Local multiprocessing (V1); HPC/Cloud (V2 Horizon) |

**Connects to:**
- `docs/02-design/02-architecture/adr/ADR-001-library-with-server-ready-data-layer.md` — source of CONST-TECH-01, 02, 03
- `docs/02-design/02-architecture/adr/` — future ADRs for pending decisions
- `functional-requirements.md`: FR-17, FR-19 enforce CONST-TECH-01, CONST-TECH-03
