# Container: Corvus Pilot (V2 Researcher Agent)

> Index: [01-index.md](01-index.md)

**Responsibility:** Provide an LLM-powered interaction layer on top of the core Corvus Corone
library — enabling conversational study design, guided algorithm understanding, and Socratic
reasoning support. Corvus Pilot V2 wraps the core library's tools via an MCP server, routes
queries through a LangGraph multi-agent graph, and exposes a CLI (`corvus-pilot run`) with
`--mode socratic` for the Learner interaction pattern.

Corvus Pilot is architecturally distinct from the core library: it adds no new benchmark
data and modifies no stored entities. It is a read-and-orchestrate layer.

**Technology:** Python · [LangGraph](https://github.com/langchain-ai/langgraph) (agent graph,
conditional routing, `MemorySaver` checkpointing) · [MCP](https://modelcontextprotocol.io/)
(tool exposure for LLM) · Ollama (local LLM inference) · MLflow (session tracking).
Lives in the `corvus_corone_pilot` package within the monorepo.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Pilot CLI | `corvus-pilot run -q "..."` with `[--mode socratic]` and `[--auto-approve]` flags | Researcher, Learner (terminal) |
| Interaction modes | `mode: "direct_answer"` (default) / `mode: "socratic"` — selectable per session or per query | Learner (socratic), Researcher (direct) |
| Session history | `corvus-pilot history [--thread-id]` — MLflow-tracked session logs | Researcher, Learner (session review) |

Full C3 component breakdown (including Socratic Guide internal design):
[`../04-c4-leve3-components/02-corvus-pilot.md`](../04-c4-leve3-components/02-corvus-pilot.md)

**Dependencies:**

| Dependency | Reason |
|---|---|
| Public API + CLI (core library) | Accessed via MCP server tools: `run_study`, `list_problems`, `list_algorithms`, `get_study_results`, `get_algorithm_properties` |
| Algorithm Registry | `get_algorithm_properties` tool — reads algorithm metadata to ground Socratic and contextual help responses |
| Results Store | `get_study_results` tool — reads `ResultAggregate[]`, `PerformanceRecord[]` for data-driven Learner responses |

**Data owned:** None in the core library. Session logs and MLflow run records are stored
within the `corvus_corone_pilot` package's own tracking store (separate from the Results
Store). No `Study`, `Run`, or `Report` entities are written by the Pilot.

**Actors served:**

- **Researcher** (primary in V2) — conversational study design, natural-language query over results
- **Learner** (primary for Socratic mode) — algorithm understanding, guided reasoning (UC-08, UC-09)

**Relevant SRS section:** UC-08 (Contextual Algorithm Help — how/why/where), UC-09
(Socratic Guided Deduction — bridging questions, never direct answers); IMPL-028..036
(V2 implementation tasks), IMPL-045 (Socratic Guide node).
