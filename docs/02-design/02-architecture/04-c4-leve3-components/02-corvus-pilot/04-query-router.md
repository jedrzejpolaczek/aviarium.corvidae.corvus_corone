# Query Router

> Container: [Corvus Pilot V2](../../03-c4-leve2-containers/14-corvus-pilot.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Classify each incoming user query and route it to the correct agent node via a LangGraph conditional edge. The Query Router is the single architectural point where the `socratic` / `direct_answer` mode boundary is enforced.

---

## Interface

Consumed by the LangGraph Graph as a conditional edge function:

```python
def route_query(state: PilotState) -> Literal["socratic_guide", "planner"]:
    ...
```

Input: `PilotState` (reads `interaction_mode` and `query`).
Output: node name string used by LangGraph to select the next node.

---

## Dependencies

- **LangGraph Graph** — registers this function as a conditional edge
- **LLM (Ollama)** — lightweight structured-output call for query classification when `interaction_mode` is not `socratic`

---

## Key Behaviors

1. **Explicit mode wins** — if `state["interaction_mode"] == "socratic"`, always return `"socratic_guide"` without any LLM call.

2. **Auto-classification** — if mode is `"direct_answer"`, call `classify_query(state["query"])` which issues a lightweight LLM call with structured output schema `{"type": "educational" | "task" | "factual"}`:
   - `"educational"` → route to `"socratic_guide"` (how/why/where queries about algorithm mechanics)
   - `"task"` or `"factual"` → route to `"planner"`

3. **Classification prompt** — the classification LLM call uses a fixed-schema prompt (not full conversation context) to minimise latency. The prompt includes two exemplars per class.

4. **Fallback** — if the LLM classification call fails or returns an unexpected value, default to `"planner"` (fail-open toward the task path, not the Socratic path, to avoid an unintended educational loop).

5. **Statelessness** — reads state, never writes. Side-effect free.

Routing logic summary:

```python
def route_query(state: PilotState) -> str:
    if state["interaction_mode"] == "socratic":
        return "socratic_guide"

    query_type = classify_query(state["query"])
    if query_type == "educational":
        return "socratic_guide"

    return "planner"
```

---

## Dependencies

- **LangGraph Graph** — calls this function as a conditional edge
- **Ollama LLM** — `classify_query()` makes a structured-output call

---

## State

Stateless — reads `state["interaction_mode"]` and `state["query"]`; writes nothing to state.

---

## Implementation Reference

`corvus_corone_pilot/v2_researcher/graph.py` — implemented as an inline function in the graph module alongside the graph construction code.

---

## SRS Traceability

Enforces the mode boundary required by:
- UC-09 (Socratic Guided Deduction): correct routing to Socratic Guide Node
- IMPL-045 (Socratic Guide node integration)
- IMPL-034 (multi-agent researcher workflow): task routing to Planner
