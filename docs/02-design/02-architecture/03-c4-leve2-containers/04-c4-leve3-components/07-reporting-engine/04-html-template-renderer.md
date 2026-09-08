# HTML Template Renderer

> Container: [Reporting Engine](../../03-c4-leve2-containers/05-reporting-engine.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Assemble the final self-contained HTML report from `ReportData` and visualization paths using Jinja2 templates, embedding all visualizations inline as base64 data URIs.

---

## Interface

```python
class HtmlTemplateRenderer:
    def render(
        self,
        report_data: ReportData,
        viz_paths: dict[str, Path],
        limitations: list[str],
        template_name: str = "standard",
        output_path: Path = Path("report.html"),
    ) -> Path:
        """
        Renders and writes the HTML report.
        Returns the output_path on success.
        Raises TemplateRenderError if a required template variable is missing.
        """
```

---

## Dependencies

- `jinja2` — `Environment`, `FileSystemLoader` for template rendering
- `base64` stdlib — for embedding images inline
- `pathlib.Path` stdlib

---

## Key Behaviors

1. **Template loading** — loads the Jinja2 template from `corvus_corone/reporting_engine/templates/{template_name}.html.j2`. The `standard` template is bundled with the package.

2. **Visualization embedding** — reads each visualization file referenced in `viz_paths` and embeds it as a base64 data URI (`data:image/png;base64,...` or `data:image/gif;base64,...`). This makes the report self-contained — no external file references.

3. **Section rendering** — renders the following sections in order: Study metadata, Algorithm comparison table, Convergence plots, Trajectory scatter plots, Sensitivity heatmaps, Statistical test results, Limitations.

4. **Error reporting** — if a Jinja2 `UndefinedError` occurs (missing template variable), raises `TemplateRenderError` naming the undefined variable and the template section it occurred in.

5. **Self-contained output** — the output HTML file has no external dependencies (no CDN links, no relative image paths). It can be opened in any browser without a web server.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/reporting_engine/html_template_renderer.py`
`corvus_corone/reporting_engine/templates/standard.html.j2`

---

## SRS Traceability

- UC-06 (view report): the HTML report is the primary artifact of the reporting pipeline.
- FR-P-03 (self-contained report): report must open in a browser without an internet connection.
