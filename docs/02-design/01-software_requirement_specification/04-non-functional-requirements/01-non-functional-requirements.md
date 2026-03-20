# Non-Functional Requirements — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: The quality attributes the system must exhibit across all functional behaviours.
NFRs are not about what the system does, but how well it does it — and what it must never violate.

NARRATIVE POSITION:
  MANIFESTO (WHY) → NFRs (quality constraints on HOW the system behaves)
  NFRs → Acceptance Tests (measurable pass/fail criteria)
  NFRs → Functional Requirements (FRs that enforce each NFR)

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                                         : source principles
  ← use-cases.md                                                            : which UCs exercise each NFR
  → functional-requirements.md                                              : FRs that enforce each NFR
  → constraints.md                                                          : community constraints overlap NFR-OPEN-01
  → acceptance-test-strategy.md                                             : test category per NFR
  → docs/04_scientific_practice/methodology/statistical-methodology.md     : NFR-STAT-01 operationalized
  → docs/05_community/versioning-governance.md                             : NFR-REPRO-01 and NFR-OPEN-01
  → docs/03-technical-contracts/interface-contracts.md                     : NFR-MODULAR-01 operationalized
  → docs/03-technical-contracts/data-format.md §4                          : NFR-INTEROP-01 operationalized

NOTE ON MEASURABLE CRITERIA:
  All criteria marked TODO: REF-TASK-0010 are pending architectural decisions.
  When REF-TASK-0010 is resolved, replace each TODO with a concrete number, threshold, or
  automated test condition that can be evaluated without human judgment.
-->

---

## NFR-REPRO-01: Reproducibility

**Description:** Every Experiment can be exactly re-executed by a different team using the archived Artifacts (code, data, seeds, procedures) to produce identical results.

**Source:** MANIFESTO Principles 19–22.

**Measurable criterion:** `TODO: REF-TASK-0010` — define bit-for-bit vs. numerical tolerance; platform constraints.

**Operationalized in:** `docs/05_community/versioning-governance.md`.

**Exercises:** UC-01 (postcondition: all Artifacts versioned and reproducible), UC-05 (verification run produces identical or documented-divergent results).

**Tested by:** Reproducibility tests (`acceptance-test-strategy.md`) — re-execute the same Study from archived Artifacts on a clean environment and compare Result Aggregates.

**Enforced by:** FR-09 (system-assigned seeds), FR-10 (execution environment recording), FR-17 (UUID-based Artifact identity), FR-18 (complete Artifact archive).

---

## NFR-STAT-01: Statistical Validity

**Description:** All analysis outputs comply with the three-level analysis methodology — no study report is produced without exploratory, confirmatory, and practical significance analysis.

**Source:** MANIFESTO Principles 13, 15.

**Measurable criterion:** `TODO: REF-TASK-0010` — define automated checks for mandatory analysis steps.

**Operationalized in:** `docs/04_scientific_practice/methodology/statistical-methodology.md`.

**Exercises:** UC-01 (Step 8: three-level analysis is a mandatory step before report generation).

**Tested by:** Statistical validity tests (`acceptance-test-strategy.md`) — attempt to produce a report with one analysis level missing; system must reject.

**Enforced by:** FR-15 (all three levels mandatory), FR-16 (multiple-testing correction required when multiple hypotheses).

---

## NFR-INTEROP-01: Ecosystem Interoperability

**Description:** Results can be exported to COCO, Nevergrad, and IOHprofiler formats without data loss beyond the documented field mappings in `docs/03-technical-contracts/data-format.md` §4.

**Source:** MANIFESTO Principle 26.

**Measurable criterion:** `TODO: REF-TASK-0010` — round-trip test criteria per platform; information-loss manifest is produced for every export.

**Operationalized in:** `docs/03-technical-contracts/data-format.md` §4 (Interoperability Mappings).

**Exercises:** UC-06 (full export flow for each supported platform).

**Tested by:** Interoperability tests (`acceptance-test-strategy.md`) — export a known Experiment to each platform format; verify loadability in the target tool; compare field values against expected mapping.

**Enforced by:** FR-23 (COCO export), FR-24 (IOHprofiler export), FR-25 (Nevergrad adapter), FR-26 (information-loss manifest).

---

## NFR-OPEN-01: Open Data and Code

**Description:** All experimental data, algorithm code, and analysis scripts are publicly available under open licenses in standardized, well-documented formats.

**Source:** MANIFESTO Principles 20, 22.

**Measurable criterion:** `TODO: REF-TASK-0010` — license type, format approval list.

**Operationalized in:** `docs/05_community/versioning-governance.md` §5.

**Exercises:** UC-01 (postcondition: Raw Data export available in open format), UC-04 (contributed Problem Instance published openly).

**Tested by:** License and format compliance checks (`acceptance-test-strategy.md`) — verify all output formats are on the approved open-format list; verify license headers on code artifacts.

**Enforced by:** FR-22 (Raw Data export in open format), CONST-COM-01, CONST-COM-02, CONST-COM-03 (→ `constraints.md`).

---

## NFR-MODULAR-01: Extensibility

**Description:** Adding a new Problem Instance or Algorithm Implementation requires only implementing the defined interface — no modification of existing system code.

**Source:** MANIFESTO Value 6 (System adaptability), Principle 27 (community development).

**Measurable criterion:** `TODO: REF-TASK-0010` — plugin test: new algorithm contributes and runs without modifying core library files.

**Operationalized in:** `docs/03-technical-contracts/interface-contracts.md`.

**Exercises:** UC-02 (contribute algorithm via interface), UC-04 (contribute Problem Instance via schema).

**Tested by:** Plugin tests (`acceptance-test-strategy.md`) — contribute a new Algorithm Instance and a new Problem Instance in an isolated test environment; verify no core files are modified; verify the new entries participate correctly in a Study.

**Enforced by:** FR-01, FR-02 (Problem Instance validation without code change), FR-05, FR-06, FR-07 (Algorithm Instance validation without code change).

---

## NFR-USABILITY-01: Minimal Onboarding Friction

**Description:** A researcher familiar with Python can wrap an existing HPO optimizer and run their first benchmarking Study in under 30 minutes from installation.

**Source:** MANIFESTO Principle 28 (education and support), user requirement (Python library, minimal boilerplate).

**Measurable criterion:** `TODO: REF-TASK-0010` — define the "first study" tutorial and measure completion time in user testing.

**Exercises:** UC-02 (algorithm wrapping ≤15 lines), UC-01 (Study definition and execution via the Python API).

**Tested by:** Usability tests (`acceptance-test-strategy.md`) — timed completion of the "Algorithm Author" tutorial (target: ≤15 lines of adapter code) and the "First Study" tutorial (target: ≤30 minutes from installation to report).

**Enforced by:** The Algorithm interface design (→ `docs/03-technical-contracts/interface-contracts.md`) must be minimal enough that common wrappers require ≤15 lines.
