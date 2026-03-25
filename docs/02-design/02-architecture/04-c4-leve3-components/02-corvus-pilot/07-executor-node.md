# Executor Node

> Container: [Corvus Pilot V2](../../03-c4-leve2-containers/14-corvus-pilot.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Execute the ordered sequence of MCP tool calls produced by the Planner Node, pausing before `run_study()` for human-in-the-loop confirmation, and collecting results for the Analyst Node.

---

## Interface

Input state fields consumed:
- `state["plan"]` — ordered list of `ToolCall` objects from the Planner Node

Output state fields produced:
- `state["tool_results"]` — list of `{"tool": str, "result": dict | error_dict}` in execution order
- `state["messages"]` — appended with a structured `ToolMessage` per tool call

The LangGraph `interrupt_before=["executor"]` mechanism pauses the graph before this node executes `run_study()`. The CLI prompts the user to confirm; `graph.invoke()` is called again to resume.

---

## Dependencies

- **MCP Server** — all tool calls go through the MCP protocol to the server
- **LangGraph Graph** — `interrupt_before` is declared at the graph level; this node cooperates by being the designated interrupt point
- **Analyst Node** — consumes `state["tool_results"]`

---

## Key Behaviors

1. **Sequential execution** — executes tool calls in the order specified by `state["plan"]`. Does not parallelize (tool results may be inputs to subsequent calls).

2. **Human-in-the-loop for run_study** — when a `run_study` tool call is encountered, the node does not execute it immediately. Instead, it sets a flag in state (`state["awaiting_confirmation"] = True`) and the LangGraph `interrupt_before` mechanism surfaces a confirmation prompt to the CLI user. Only after user confirmation does the graph resume and the tool call execute.

3. **Error capture** — if a tool call raises an exception or returns an error dict, the Executor Node records it in `state["tool_results"]` and continues to the next tool call. It does not abort the entire plan on a single tool failure.

4. **Result accumulation** — all tool results (success and error) are accumulated in `state["tool_results"]` for the Analyst Node to interpret holistically.

5. **Retry on transient failure** — network-level MCP transport failures trigger one automatic retry with 500 ms back-off. Application-level errors (e.g., `EntityNotFoundError`) are not retried.

---

## State

Reads `state["plan"]`; writes `state["tool_results"]` and `state["awaiting_confirmation"]`. Transient within one session turn. Not persisted across `thread_id` sessions.

---

## Implementation Reference

`corvus_corone_pilot/v2_researcher/agents/executor.py`

---

## SRS Traceability

- IMPL-034 (multi-agent researcher workflow)
- UC-01 and UC-02 (study execution requires human-in-the-loop confirmation via `interrupt_before`)
