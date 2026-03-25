# Container: Public API + CLI

> Index: [01-index.md](01-index.md)

**Responsibility:** Expose the complete researcher-facing surface of the library — the
Python module API (`import corvus_corone as cc`) and the `corvus` terminal commands —
as a single thin coordination layer that delegates to the Core Layer.

**Technology:** Python · [Click](https://click.palletsprojects.com/) (CLI framework).
Click was chosen because it integrates cleanly with Python packaging (`console_scripts`
entry point), supports composable command groups, and generates `--help` output
automatically from docstrings and parameter annotations. No separate build step is
required.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Python API | Module functions: `cc.create_study()`, `cc.run()`, `cc.list_problems()`, `cc.generate_reports()`, `cc.export_raw_data()`, `cc.visualize()`, etc. | Researcher (scripts, notebooks), Algorithm Author |
| CLI | `corvus run`, `corvus list-problems`, `corvus list-algorithms`, `corvus report`, `corvus verify`, `corvus export` | Researcher (terminal), CI scripts |

Full Python API contract: `docs/03-technical-contracts/04-public-api-contract.md`

Full CLI command reference and complete example session:
[`02-cli-spec.md`](02-cli-spec.md)

**Dependencies:**

| Dependency | Reason |
|---|---|
| Study Orchestrator | `cc.create_study()` and `cc.run()` delegate orchestration to this component |
| Algorithm Registry | `cc.list_algorithms()` / `cc.get_algorithm()` read from the registry |
| Problem Repository | `cc.list_problems()` / `cc.get_problem()` read from the repository |
| Results Store | `cc.get_experiment()`, `cc.get_runs()`, `cc.get_result_aggregates()`, `cc.export_raw_data()` read from the store |
| Reporting Engine | `cc.generate_reports()` delegates report generation here |
| Algorithm Visualization Engine | `cc.visualize()` delegates visualization requests here |

**Data owned:** None. This container holds no persistent state. All storage is
delegated to the Data & Registry layer.

**Actors served:** Researcher (primary), Algorithm Author (registry reads), Learner
(visualisation commands via `cc.visualize()`).

**Relevant SRS section:** FR-4.1 (problem registry reads), FR-4.2 (algorithm registry
reads), FR-4.3 (study execution), FR-4.5 (reproducibility), FR-4.6 (reporting).
