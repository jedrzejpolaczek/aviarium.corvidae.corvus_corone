# C2: Containers — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: "What are the major moving parts?"
Decomposes the single black box from C1 into deployable/runnable units.
This is where architecture decisions become visible for the first time.

NARRATIVE POSITION:
  C1 (WHO and WHAT world) → C2 → (WHAT are the parts and HOW do they communicate)
  → C3 (WHAT is inside each part) → SRS (WHAT must each part do)

CONNECTS TO:
  ← C1                    : the system boundary from there is decomposed here
  → C3                    : each container here is zoomed into in a C3 document
  → SRS §4                : each container maps to one or more functional requirement groups
  → specs/data-format.md  : data flowing between containers must conform to schemas there
  → architecture/adr/     : technology choices for each container should have a corresponding ADR
-->

---

## Container Diagram

```mermaid
---
config:
  look: neo
  layout: elk
  theme: redux-dark
  themeVariables:
    background: transparent
---
flowchart TB
  subgraph Client["Client"]
    researcher(["Researcher"])
    alg_author(["Algorithm Author"])
    learner(["Learner"])
  end

  subgraph EntryLayer["Entry Layer"]
    api["Public API + CLI\nPython · Click"]
  end

  subgraph CoreLayer["Core Layer"]
    orchestrator["Study Orchestrator\nPython"]
    runner["Experiment Runner\nPython"]
    analysis["Analysis Engine\nPython · SciPy"]
    reporting["Reporting Engine\nPython · Matplotlib"]
    viz_engine["Algorithm Visualization Engine\nPython · Matplotlib"]
  end

  subgraph DataLayer["Data & Registry"]
    registry["Algorithm Registry\nPython"]
    problems["Problem Repository\nPython"]
    store[("Results Store\nPython · SQLite")]
    bridge["Ecosystem Bridge\nPython"]
  end

  subgraph CorvusCorone["Corvus Corone (Python Library)"]
    EntryLayer
    CoreLayer
    DataLayer
  end

  subgraph ExternalSystems["External Systems"]
    ecosystem["Benchmarking Ecosystem\nCOCO · Nevergrad · IOHprofiler"]
    artifact_repo["Artifact Repository\nZenodo · Figshare"]
  end

  researcher L_researcher_api@-- Designs studies · runs experiments --> api
  alg_author L_alg_author_registry@-- Registers algorithm implementation --> registry
  api L_api_orchestrator@-- Submits study for execution --> orchestrator
  orchestrator L_orchestrator_runner@-- Dispatches individual runs --> runner
  orchestrator L_orchestrator_analysis@-- Triggers metric computation --> analysis
  orchestrator L_orchestrator_reporting@-- Triggers report generation --> reporting
  runner L_runner_registry@-- Loads algorithm instance --> registry
  runner L_runner_problems@-- Loads problem instance --> problems
  runner L_runner_store@-- Writes run records --> store
  analysis L_analysis_store@-- Reads PerformanceRecords · writes ResultAggregates --> store
  reporting L_reporting_store@-- Reads aggregated results --> store
  bridge L_bridge_store@-- Reads study artifacts --> store
  bridge L_bridge_ecosystem@-- Exports data files --> ecosystem
  store L_store_artifact@-- Publishes versioned datasets --> artifact_repo
  learner L_learner_api@-- Explores algorithm visualisations and contextual help --> api
  api L_api_viz@-- Dispatches visualisation requests --> viz_engine
  viz_engine L_viz_registry@-- Reads algorithm metadata --> registry
  viz_engine L_viz_store@-- Reads study data for data-driven visualisations --> store

  researcher:::Peach
  alg_author:::Peach
  learner:::Peach
  api:::Aqua
  orchestrator:::Aqua
  runner:::Aqua
  analysis:::Aqua
  reporting:::Aqua
  viz_engine:::Aqua
  registry:::Aqua
  problems:::Aqua
  bridge:::Aqua
  store:::Sky
  ecosystem:::Sky
  artifact_repo:::Sky

  classDef Aqua stroke-width:1px, stroke-dasharray:none, stroke:#46EDC8, fill:#DEFFF8, color:#378E7A
  classDef Sky stroke-width:1px, stroke-dasharray:none, stroke:#374D7C, fill:#E2EBFF, color:#374D7C
  classDef Peach stroke-width:1px, stroke-dasharray:none, stroke:#FBB35A, fill:#FFEFDB, color:#8F632D

  style researcher color:#000000
  style alg_author color:#000000
  style api color:#000000
  style orchestrator color:#000000
  style runner color:#000000
  style analysis color:#000000
  style reporting color:#000000
  style registry color:#000000
  style problems color:#000000
  style store color:#000000
  style learner color:#000000
  style viz_engine color:#000000
  style bridge color:#000000
  style ecosystem color:#000000
  style artifact_repo color:#000000

  style Client stroke:#666666,fill:#1e1e1e,color:#aaaaaa
  style EntryLayer stroke:#FFD600
  style CoreLayer stroke:#FF6D00
  style DataLayer stroke:#AA00FF
  style CorvusCorone stroke:#555555,fill:#161616,color:#aaaaaa
  style ExternalSystems stroke:#555555,fill:#1e1e1e,color:#aaaaaa

  linkStyle 0 stroke:#FFD600,fill:none
  linkStyle 1 stroke:#FFD600,fill:none
  linkStyle 2 stroke:#FFD600,fill:none
  linkStyle 3 stroke:#FF6D00,fill:none
  linkStyle 4 stroke:#FF6D00,fill:none
  linkStyle 5 stroke:#FF6D00,fill:none
  linkStyle 6 stroke:#00C853,fill:none
  linkStyle 7 stroke:#00C853,fill:none
  linkStyle 8 stroke:#00C853,fill:none
  linkStyle 9 stroke:#AA00FF,fill:none
  linkStyle 10 stroke:#AA00FF,fill:none
  linkStyle 11 stroke:#AA00FF,fill:none
  linkStyle 12 stroke:#2962FF,fill:none
  linkStyle 13 stroke:#2962FF,fill:none
  linkStyle 14 stroke:#FFD600,fill:none
  linkStyle 15 stroke:#FF6D00,fill:none
  linkStyle 16 stroke:#00C853,fill:none
  linkStyle 17 stroke:#AA00FF,fill:none

  L_researcher_api@{ animation: slow }
  L_alg_author_registry@{ animation: slow }
  L_api_orchestrator@{ animation: fast }
  L_orchestrator_runner@{ animation: fast }
  L_orchestrator_analysis@{ animation: fast }
  L_orchestrator_reporting@{ animation: fast }
  L_runner_registry@{ animation: fast }
  L_runner_problems@{ animation: fast }
  L_runner_store@{ animation: fast }
  L_analysis_store@{ animation: fast }
  L_reporting_store@{ animation: fast }
  L_bridge_store@{ animation: fast }
  L_bridge_ecosystem@{ animation: fast }
  L_store_artifact@{ animation: fast }
  L_learner_api@{ animation: slow }
  L_api_viz@{ animation: fast }
  L_viz_registry@{ animation: fast }
  L_viz_store@{ animation: fast }
```

---

## Containers

### Public API + CLI

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
| Python API | Module functions: `cc.create_study()`, `cc.run()`, `cc.list_problems()`, `cc.generate_reports()`, `cc.export_raw_data()`, etc. | Researcher (scripts, notebooks), Algorithm Author |
| CLI | `corvus run`, `corvus list-problems`, `corvus list-algorithms`, `corvus report`, `corvus verify`, `corvus export` | Researcher (terminal), CI scripts |

Full Python API contract:
`docs/03-technical-contracts/04-public-api-contract.md`

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

**Data owned:** None. This container holds no persistent state. All storage is
delegated to the Data & Registry layer.

**Actors served:** Researcher (primary), Algorithm Author (registry reads), Learner
(future — visualisation commands).

**Relevant SRS section:** FR-4.1 (problem registry reads), FR-4.2 (algorithm registry
reads), FR-4.3 (study execution), FR-4.5 (reproducibility), FR-4.6 (reporting).

---

## Key End-to-End Flows

<!--
  Describe the most architecturally significant flows — those that cross multiple containers.
  These flows make the architecture "come alive" and reveal integration points.

  For each flow:
    - Name: a short, human-readable label (e.g., "Run a benchmarking study")
    - Trigger: what initiates this flow? (researcher action, scheduled job, API call)
    - Steps: numbered sequence of container interactions
    - Data exchanged at each step: reference specs/data-format.md entity names
    - End state: what is different in the system after this flow completes?

  Hint — flows to consider:
    1. "Design and execute a benchmarking study" (main researcher workflow)
    2. "Register a new benchmark problem" (contributor workflow)
    3. "Register a new algorithm implementation" (algorithm author workflow)
    4. "Generate a study report" (practitioner workflow)
    5. "Export results to IOHprofiler / COCO" (interoperability workflow)
    6. "Reproduce a published study" (reproducibility workflow)

  Each flow here should correspond to a use case in SRS §3.
-->
