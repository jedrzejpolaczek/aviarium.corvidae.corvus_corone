# NFR-STAT-01 — Statistical Validity

*All analysis outputs comply with the three-level analysis methodology — no study report is produced without exploratory, confirmatory, and practical significance analysis.*
*Source: MANIFESTO Principles 13, 15.*
*Use Cases: UC-01.*

---

## NFR-STAT-01

**All analysis outputs MUST comply with the three-level analysis methodology — no study report is produced without exploratory, confirmatory, and practical significance analysis.**

- **Source:** MANIFESTO Principles 13, 15
- **Measurable criterion:** (1) `generate_report()` on a `ResultAggregate` with completed Level 1 but absent Level 2 results raises `AnalysisIncompleteError`. (2) `generate_report()` on a `ResultAggregate` with completed Level 1 and Level 2 but absent Level 3 (effect sizes) raises `AnalysisIncompleteError`. (3) Every successfully generated Researcher Report contains non-null fields for all three analysis levels. All three checks are automated in the statistical validity test category.
- **Operationalized in:** `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md`
- **Exercises:** UC-01 (Step 8: three-level analysis is a mandatory step before report generation)
- **Tested by:** Statistical validity tests — attempt to produce a report with one analysis level missing; system must reject
- **Enforced by:** FR-15 (all three levels mandatory), FR-16 (multiple-testing correction required when multiple hypotheses)
