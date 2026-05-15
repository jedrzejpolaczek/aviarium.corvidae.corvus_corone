# MCP Server

> Container: [Corvus Pilot V2](../../03-c4-leve2-containers/14-corvus-pilot.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Expose the Corvus Corone core library as a set of LLM-callable tools via the MCP `@app.tool()` interface, bridging the Python API surface to the language model's tool-calling capability.

---

## Interface

Outward (to LLM agent nodes via MCP protocol):

| Tool name | Signature | Delegates to |
|---|---|---|
| `run_study` | `(study_config: dict) -> dict` | `cc.run()` |
| `list_problems` | `(filters: dict = {}) -> list[dict]` | `cc.list_problems()` |
| `list_algorithms` | `(filters: dict = {}) -> list[dict]` | `cc.list_algorithms()` |
| `get_study_results` | `(experiment_id: str) -> dict` | `cc.get_result_aggregates()` |
| `get_algorithm_properties` | `(algorithm_id: str) -> dict` | `cc.get_algorithm()` |
| `get_algorithm_genealogy` | `(algorithm_id: str) -> dict` | `cc.get_algorithm_genealogy()` |

All tool responses are serialised to JSON-serialisable dicts before returning to the MCP protocol layer.

Inward (consumed by agent nodes):
- Executor Node: calls `run_study`, `list_problems`, `list_algorithms`, `get_study_results`
- Planner Node: calls `list_problems`, `list_algorithms`
- Socratic Guide Node: calls `get_algorithm_properties`, `get_algorithm_genealogy`, `get_study_results` (read-only subset only)
- Direct Answer Node: calls `get_algorithm_properties`

---

## Dependencies

- **Public API + CLI container** (core library) — all tool calls delegate here
- **MCP framework** (`mcp` Python package) — `@app.tool()` decorator and MCP transport

---

## Key Behaviors

1. **Tool registration** — on server startup, each `@app.tool()` decorated function is registered with its JSON schema (derived from Python type annotations). The schema is the contract the LLM uses to invoke the tool correctly.

2. **Delegation without transformation** — each tool function calls the corresponding `cc.*` public API function directly; it does not re-implement any business logic. Transformation is limited to serialisation (domain objects → dicts).

3. **Socratic access restriction** — the server itself does not enforce access restrictions; the LangGraph graph node configuration (tool-access lists per node) restricts which tools the Socratic Guide Node may call. The MCP server exposes the full surface; restriction is upstream.

4. **Error passthrough** — exceptions raised by the core library (e.g., `EntityNotFoundError`, `StudyValidationError`) are caught, wrapped in a structured error dict `{"error": "<type>", "message": "<str>"}`, and returned as the tool result. The calling agent node is responsible for handling the error payload.

5. **Health check** — exposes a `health_check()` tool (not LLM-callable; used by integration tests and the CLI startup sequence) that verifies connectivity to the core library.

---

## State

Stateless. Each tool call is fully independent. No session state is held in this component; session state lives in `PilotState` managed by the LangGraph Graph.

---

## Implementation Reference

`corvus_corone_pilot/v2_researcher/mcp_server.py`

---

## SRS Traceability

Enables all Pilot-served use cases (UC-07 through UC-10) by providing the tool access layer between the LLM and the core library. Specifically required by:
- UC-08 (Contextual Algorithm Help): `get_algorithm_properties`
- UC-09 (Socratic Guided Deduction): `get_algorithm_properties`, `get_algorithm_genealogy`, `get_study_results`
- UC-10 (Algorithm History and Evolution): `get_algorithm_genealogy`
- IMPL-034 (multi-agent researcher workflow)
