# Analyst Node

> Container: [Corvus Pilot V2](../../03-c4-leve2-containers/14-corvus-pilot.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Interpret the MCP tool results produced by the Executor Node and generate the final direct answer or report summary that is returned to the user.

---

## Interface

Input state fields consumed:
- `state["tool_results"]` — ordered list of tool results from the Executor Node
- `state["query"]` — original user query (for grounding the answer)
- `state["messages"]` — conversation history (for context)

Output state fields produced:
- `state["messages"]` — appended with the final `AIMessage` containing the answer or summary

---

## Dependencies

- **LangGraph Graph** — receives and returns `PilotState`; this is the terminal node in the task path
- **Ollama LLM** — structured-output call to synthesise tool results into a natural-language answer

---

## Key Behaviors

1. **Result synthesis** — issues an LLM call with `state["query"]` and `state["tool_results"]` as context. The call produces a natural-language answer grounded in the actual tool results.

2. **Error interpretation** — if any `tool_results` contain error dicts, the Analyst surfaces them in human-readable form rather than presenting them as raw JSON. E.g., `EntityNotFoundError` for `algorithm_id="xyz"` → "Algorithm 'xyz' was not found. Available algorithms: ..."

3. **Partial success handling** — if some tool calls succeeded and some failed, the Analyst presents the successful results and notes which operations failed, rather than treating the entire response as an error.

4. **Format selection** — for result-aggregation queries (e.g., "compare TPE and CMA-ES"), the Analyst formats the answer as a structured comparison table. For single-entity queries, it uses prose. Format selection is driven by a rule on the `query` type, not an LLM call.

5. **Answer grounding** — the Analyst LLM prompt explicitly instructs: "answer only from the tool results provided; do not add information not present in the results." This prevents hallucination of performance numbers or algorithm properties.

---

## State

Reads `state["tool_results"]` and `state["query"]`; writes only `state["messages"]`. No persistent state.

---

## Implementation Reference

`corvus_corone_pilot/v2_researcher/agents/analyst.py`

---

## SRS Traceability

- IMPL-034 (multi-agent researcher workflow)
- Supports all Researcher-facing task use cases (UC-01 through UC-06) as the final response generator
