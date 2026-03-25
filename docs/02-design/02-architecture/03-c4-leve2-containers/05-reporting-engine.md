# Container: Reporting Engine

> Index: [01-c2-containers.md](01-c2-containers.md)

**Responsibility:** Generate HTML analysis reports for a completed Experiment — one
`researcher` report with full statistical detail and one `practitioner` report with
plain-language findings.

**Technology:** Python · Jinja2 (HTML templates) · Matplotlib (visualization).
Jinja2 generates the HTML report structure; Matplotlib renders all four mandatory
Level 1 visualizations as inline SVG embedded in the HTML.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Report generation | Called by Public API container via `cc.generate_reports()` | Researcher (via API or `corvus report`) |
| Report files | Two HTML files on disk; paths returned via `Report.artifact_reference` | Researcher, Practitioner (read-only consumers) |

Full report structure, section content, visualization specifications, and audience
language rules: [`03-report-format-spec.md`](03-report-format-spec.md)

**Dependencies:**

| Dependency | Reason |
|---|---|
| Results Store | Reads `ResultAggregate`, `Run`, `PerformanceRecord`, and `Study` entities for the target Experiment |
| Results Store (reports sub-store) | Writes `Report` entity records and stores HTML artifacts |
| Algorithm Visualization Engine | Delegates algorithm-understanding visualization inserts when `cc.generate_reports()` is called with `include_algorithm_viz=True` |

**Data owned:** Generated `Report` entity records and their HTML artifact files.
The Reports directory within the `LocalFileRepository` root (`reports/<uuid>.json`
and the HTML files written alongside it).

**Actors served:** Researcher (primary, via full statistical report); Practitioner
(via summary report, through `corvus report` or direct path).

**Relevant SRS section:** FR-20 (two reports per experiment), FR-21 (mandatory
limitations section, no rankings), FR-22 (raw data export alongside reports).
