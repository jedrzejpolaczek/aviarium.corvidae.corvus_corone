# C4: Code — Index

> C3 Components: [../04-c4-leve3-components/01-c4-l3-components/01-c4-l3-components.md](../04-c4-leve3-components/01-c4-l3-components/01-c4-l3-components.md)

C4 Level 4 documents the architecturally significant code abstractions within Corvus Corone —
the interfaces, protocols, and data types whose shape is a design decision that affects multiple
containers. It is **not** an exhaustive class inventory.

**Selection rule:** an abstraction qualifies for C4 if removing it or changing its shape would
require changes in more than one container. Everything else belongs in docstrings.

---

## Architecture Overview

The diagram below shows all documented abstractions and their relationships. It is the
"map" of this section — each node links to a detailed C4 file.

```mermaid
---
config:
  look: neo
  theme: redux-dark
  themeVariables:
    background: transparent
---
flowchart TD
  subgraph SHARED["02 · Shared Abstractions"]
    ai["AlgorithmInterface\nProtocol\nask · tell · reset"]
    aii["AlgorithmInstance\ndataclass frozen\nalgorithm_id · version · implementation"]
    pi["ProblemInterface\nProtocol\nevaluate · bounds · dimension · optimum"]
    pii["ProblemInstance\ndataclass frozen\nproblem_id · version · implementation"]
    pr["PerformanceRecord\ndataclass frozen\nrun_id · iteration · value · best_so_far"]
    sc["StudyConfig\ndataclass\nalgorithms · problems · budget · base_seed"]
    rc["RunConfig\ndataclass\nrun_id · algorithm_id · problem_id · seed"]
  end

  subgraph PILOT["03 · Corvus Pilot V2"]
    ps["PilotState\nTypedDict\nmessages · query · interaction_mode · awaiting_response"]
  end

  subgraph ER["04 · Experiment Runner"]
    sm["SeedManager\ngenerate_seed · inject_seeds · persist_seed"]
    el["EvaluationLoop\nrun(algorithm, problem, budget, recorder)"]
  end

  subgraph AE["05 · Analysis Engine"]
    md["MetricDispatcher\ndispatch(experiment_id, config, store)"]
  end

  subgraph RS["06 · Results Store"]
    repo["Repository\nProtocol\nrun_dir · jsonl_path · parquet_path · ensure_dirs"]
  end

  subgraph API["07 · Public API + CLI"]
    af["APIFacade\ncc.* module\nrun · resume · visualize · export"]
  end

  ps    L_ps_af@-- cc.* via MCP --> af
  af    L_af_sc@--> sc
  sc    L_sc_rc@-- generates --> rc
  aii   L_aii_ai@-- satisfies --> ai
  pii   L_pii_pi@-- satisfies --> pi
  sm    L_sm_el@-- seed injection --> el
  el    L_el_ai@-- ask / tell --> ai
  el    L_el_pi@-- evaluate --> pi
  el    L_el_pr@-- produces --> pr
  md    L_md_pr@-- aggregates --> pr
  repo  L_repo_pr@-- persists / loads --> pr

  style SHARED fill:#1e1e1e,stroke:#555555,color:#aaaaaa
  style PILOT  fill:#161616,stroke:#FFD600,color:#aaaaaa
  style ER     fill:#161616,stroke:#FF6D00,color:#aaaaaa
  style AE     fill:#161616,stroke:#AA00FF,color:#aaaaaa
  style RS     fill:#161616,stroke:#00C853,color:#aaaaaa
  style API    fill:#161616,stroke:#FFD600,color:#aaaaaa

  linkStyle 0     stroke:#FFD600,fill:none
  linkStyle 1,2   stroke:#FF6D00,fill:none
  linkStyle 3,4   stroke:#46EDC8,fill:none
  linkStyle 5,6,7 stroke:#FF6D00,fill:none
  linkStyle 8     stroke:#00C853,fill:none
  linkStyle 9     stroke:#AA00FF,fill:none
  linkStyle 10    stroke:#2962FF,fill:none

  L_ps_af@{   animation: slow }
  L_af_sc@{   animation: fast }
  L_sc_rc@{   animation: fast }
  L_aii_ai@{  animation: fast }
  L_pii_pi@{  animation: fast }
  L_sm_el@{   animation: fast }
  L_el_ai@{   animation: fast }
  L_el_pi@{   animation: fast }
  L_el_pr@{   animation: fast }
  L_md_pr@{   animation: fast }
  L_repo_pr@{ animation: fast }
```

> **Arrow colour legend**
> | Colour | Meaning |
> |---|---|
> | ![#FFD600](https://placehold.co/12x12/FFD600/FFD600.png) yellow | Entry / user-facing (Pilot → API) |
> | ![#FF6D00](https://placehold.co/12x12/FF6D00/FF6D00.png) orange | Execution dispatch (API → spec · runner) |
> | ![#46EDC8](https://placehold.co/12x12/46EDC8/46EDC8.png) teal | Registry / protocol satisfaction |
> | ![#00C853](https://placehold.co/12x12/00C853/00C853.png) green | Writes / produces |
> | ![#AA00FF](https://placehold.co/12x12/AA00FF/AA00FF.png) purple | Analysis pipeline |
> | ![#2962FF](https://placehold.co/12x12/2962FF/2962FF.png) blue | Reads from store |

---

## Scope

| Section | Abstraction | Containers affected |
|---|---|---|
| [02-shared/01-algorithm-interface.md](02-shared/01-algorithm-interface.md) | `AlgorithmInterface` (Protocol) | Experiment Runner, Algorithm Registry, Analysis Engine, Visualization Engine, Ecosystem Bridge |
| [02-shared/02-problem-interface.md](02-shared/02-problem-interface.md) | `ProblemInterface` (Protocol) | Experiment Runner, Problem Repository, Analysis Engine |
| [02-shared/03-performance-record.md](02-shared/03-performance-record.md) | `PerformanceRecord` (dataclass) | Experiment Runner, Results Store, Analysis Engine, Reporting Engine, Visualization Engine |
| [02-shared/04-study-spec.md](02-shared/04-study-spec.md) | `StudyConfig` + `RunConfig` (dataclasses) | Public API, Study Orchestrator, Experiment Runner, Analysis Engine |
| [03-corvus-corone-pilot/02-pilot-state.md](03-corvus-corone-pilot/02-pilot-state.md) | `PilotState` (TypedDict) | Corvus Pilot V2 — all 7 agent nodes share this state |
| [04-experiment-runner/02-seed-manager.md](04-experiment-runner/02-seed-manager.md) | `SeedManager` (class + invariant) | Experiment Runner — reproducibility contract boundary |
| [04-experiment-runner/03-evaluation-loop.md](04-experiment-runner/03-evaluation-loop.md) | `EvaluationLoop` (ask/tell contract) | Experiment Runner — core execution contract between AlgorithmInterface, ProblemInterface, PerformanceRecorder |
| [05-analysis-engine/02-metric-dispatcher.md](05-analysis-engine/02-metric-dispatcher.md) | `MetricDispatcher` (routing abstraction) | Analysis Engine — adding any new metric requires extending this |
| [06-results-store/02-repository-protocol.md](06-results-store/02-repository-protocol.md) | `Repository` (Protocol) | Results Store — V1→V2 swap point; all path resolution goes through here |
| [07-public-api-cli/02-api-facade.md](07-public-api-cli/02-api-facade.md) | `APIFacade` (`cc.*`) | Public API — versioned surface consumed by CLI, MCP Server, and all external callers |

---

## What is NOT here

- Implementation classes fully contained within one component (e.g. `StatisticalTester`, `HTMLTemplateRenderer`)
- Third-party library internals (LangGraph, SciPy, Click, MLflow)
- Container-internal helpers and private utilities
- Algorithm or problem implementations contributed by users

All of the above belong in code docstrings, adjacent to the implementation.

---

## Conventions used in this section

- **Mermaid `classDiagram`** is used for per-file diagrams. Max ~10 nodes per diagram.
- **`〈Protocol〉`** in node labels marks Python structural-subtyping interfaces (PEP 544).
- **`〈dataclass〉`** marks frozen or mutable dataclasses used as value objects.
- **`〈TypedDict〉`** marks LangGraph-compatible typed dictionaries.
- Method signatures in diagrams show name and arity only — full signatures are in docstrings.
- The overview diagram above uses `flowchart` to support colour-coded, animated arrows.
