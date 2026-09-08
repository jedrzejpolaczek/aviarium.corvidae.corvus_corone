# Planner Node

> Container: [Corvus Pilot V2](../../03-c4-leve2-containers/14-corvus-pilot.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Decompose a natural-language task query into an ordered sequence of MCP tool calls that the Executor Node will execute to fulfill the user's request.

---

## Interface

Input state fields consumed:
- `state["query"]` — the user's task (e.g., "Run a study comparing TPE and CMA-ES on sphere-5d")
- `state["messages"]` — conversation history (for context on prior turns)

Output state fields produced:
- `state["plan"]` — an ordered list of `ToolCall` objects specifying tool name and arguments
- `state["messages"]` — appended with an `AIMessage` summarising the plan in natural language

---

## Dependencies

- **MCP Server** — `list_problems()` and `list_algorithms()` are called during planning to validate entity IDs
- **LangGraph Graph** — receives and returns `PilotState`
- **Ollama LLM** — structured-output call to decompose the query into a tool-call plan

---

## Key Behaviors

1. **Entity resolution** — calls `list_problems()` and `list_algorithms()` to confirm that all entity IDs mentioned in the query exist before committing to a plan. Unresolvable IDs cause the node to return a clarification message rather than a plan.

2. **Plan generation** — issues a structured LLM call with the user's query and the MCP tool schema as context. Output is a JSON array of `{"tool": str, "args": dict}` objects.

3. **Plan validation** — validates that all tool names in the generated plan exist in the MCP tool registry. Removes or replaces unknown tool references.

4. **Plan summary** — appends a human-readable summary of the plan to `state["messages"]` (e.g., "I will: (1) list available problems, (2) run a study with TPE on sphere-5d, (3) retrieve and summarise results").

5. **Single-step pass-through** — for simple single-tool queries (e.g., "list all algorithms"), the Planner generates a single-step plan without issuing the planning LLM call (rule-based shortcut to reduce latency).

---

## State

Writes `state["plan"]` — a transient field that exists only within one graph invocation. Not persisted by `MemorySaver` across sessions.

---

## Implementation Reference

`corvus_corone_pilot/v2_researcher/agents/planner.py`

---

## SRS Traceability

- IMPL-034 (multi-agent researcher workflow)
- Supports all Researcher-facing task use cases (UC-01 through UC-06)
