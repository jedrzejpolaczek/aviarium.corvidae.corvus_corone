# ADR-019: Two Reports Per Experiment

<!--
STORY ROLE: Settles whether a completed Experiment produces one report or two. The answer is a
consequence of MANIFESTO Principle 25, not a formatting preference.

CONNECTS TO:
  → docs/03-technical-contracts/01-data-format/09-report.md : the validation rule
  → docs/03-technical-contracts/04-public-api-contract.md : cc.generate_reports
  → docs/02-design/02-architecture/03-c4-leve2-containers/03-report-format-spec.md
  → .../04-c4-leve3-components/07-reporting-engine/04-html-template-renderer.md : corrected
-->

---

**Status:** Accepted

**Date:** 2026-09-08

**Deciders:** Core maintainers, methodology lead

---

## Context

Three documents say a completed Experiment yields two Reports and one says it yields one.

`01-data-format/09-report.md` validation: "every completed Experiment must have exactly one
`researcher` and one `practitioner` Report (FR-20)". `04-public-api-contract.md`:
"`generate_reports()` always returns exactly two Reports". `03-report-format-spec.md` specifies
a ten-section researcher report and a seven-section practitioner report.

`07-reporting-engine/04-html-template-renderer.md` renders a single `report.html` from one
ordered section list, and its `render()` signature returns one `Path`.

---

## Decision

**A completed Experiment produces exactly two Reports: one `researcher` and one
`practitioner`.**

`cc.generate_reports(experiment_id)` returns both. `04-html-template-renderer.md` is corrected
to render once per audience, taking `report_type` as a parameter and returning both paths.
Section content per audience remains as specified in `03-report-format-spec.md`.

---

## Rationale

MANIFESTO Principle 25 requires results at different levels of detail: summaries for
practitioners, details for researchers, raw data for analysts. One document cannot satisfy it,
because the two audiences need different things from the same evidence and the practitioner
report deliberately omits the statistical tables the researcher report exists to show.

The requirement is also already encoded as a validation rule on the Report entity. A Reporting
Engine that emits one report produces an Experiment that fails its own data format validation,
so the single-report design is not merely a different choice, it is inconsistent with the
schema.

Three normative documents against one descriptive document is, under ADR-012, not a contest.

**Trade-off accepted:** the Reporting Engine renders twice and the Results Store holds two
artifacts per Experiment. Both costs are small next to the Runs that produced the data.

---

## Alternatives Considered

### One report with an audience toggle in the HTML

**Description:** Emit a single document whose practitioner sections collapse or expand.

**Why rejected:** The `Report` entity carries `report_type` and `artifact_reference` per
audience, and the archive published to an artifact repository must contain a file that a
practitioner can read without executing JavaScript. A toggle also makes it possible to publish
the researcher content while claiming to publish the practitioner report.

**Under what conditions reconsidered:** If report distribution moves to a served application
rather than archived files, one document with server-side audience selection becomes coherent.
That is a V2 Platform Server concern.

---

## Consequences

**Positive:**

- The Reporting Engine, the Report schema, the public API and the report format specification
  agree.
- FR-20 becomes satisfiable by the documented component.

**Negative / Trade-offs:**

- `04-html-template-renderer.md` changes signature and section handling.
- Two templates must be maintained rather than one.

**Risks:**

- **Risk:** The practitioner report drifts into a summary of the researcher report and loses the
  scope statements that Principle 24 requires.
  **Mitigation:** The Limitations Enforcer validates both artifacts, not only the researcher
  one, and `03-report-format-spec.md` states the mandatory sections per audience.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/01-data-format/09-report.md` | The validation rule this ADR upholds |
| `docs/03-technical-contracts/04-public-api-contract.md` | `cc.generate_reports()` returns two |
| `docs/02-design/02-architecture/03-c4-leve2-containers/03-report-format-spec.md` | Section content per audience |
| `.../07-reporting-engine/04-html-template-renderer.md` | Corrected by this ADR |
| `adr-018-mandatory-report-visualizations.md` | Both reports carry the VIZ-L1 set |
