# LangGraph Graph

> Container: [Corvus Pilot V2](../../03-c4-leve2-containers/14-corvus-pilot.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Manage the Pilot V2 agent session lifecycle: receive a user query, route it to the appropriate agent node via the Query Router, maintain conversation state across turns using `MemorySaver` checkpointing, and support `interrupt_before=["execute_study"]` for human-in-the-loop confirmation before executing a study.

---

## Interface

Entry point (from CLI):

```python
graph.invoke(
    input={"query": str, "interaction_mode": Literal["direct_answer", "socratic"]},
    config={"configurable": {"thread_id": str}},
)
```

State schema (`PilotState`):

```python
class PilotState(TypedDict):
    messages:          list[BaseMessage]   # full conversation history
    query:             str                 # current user input
    interaction_mode:  Literal["direct_answer", "socratic"]
    thread_id:         str                 # session identifier for MemorySaver
    awaiting_response: bool                # True while Socratic loop expects Learner reply
    knowledge_state:   dict | None         # assessed from conversation; populated by Socratic node
```

Output (to CLI):
- `PilotState["messages"][-1]` — the last `AIMessage` is the response presented to the user.

---

## Dependencies

- **Query Router** — provides the `route_query()` conditional edge function
- **Socratic Guide Node** — registered as a graph node
- **Planner Node, Executor Node, Analyst Node** — registered as graph nodes
- **Session Tracker** — called at graph entry and exit to record session metadata
- **LangGraph** (`langgraph` Python package) — `StateGraph`, `MemorySaver`, `interrupt_before`

---

## Key Behaviors

1. **Graph construction** — at module import, a `StateGraph(PilotState)` is compiled with all nodes (Query Router, Socratic Guide, Planner, Executor, Analyst) and edges. The conditional edge from the router is registered with `add_conditional_edges("router", route_query)`.

2. **MemorySaver checkpointing** — the compiled graph uses `MemorySaver` as the checkpointer. Each `graph.invoke()` call with the same `thread_id` resumes from the last checkpoint, giving multi-turn conversation continuity.

3. **interrupt_before execution** — the graph is compiled with `interrupt_before=["executor"]`. This means the Executor Node is never called automatically; the CLI pauses and prompts the user to confirm before the graph resumes past the interrupt point.

4. **Mode propagation** — `interaction_mode` is set from CLI input at the start of a session and stored in `PilotState`. It is read by the Query Router on every turn. Changing mode mid-session (CLI command) resets `knowledge_state` and `awaiting_response` to `None` and `False` respectively.

5. **Session tracking** — on graph entry, the Session Tracker is called to start an MLflow run. On graph exit (normal or error), the tracker is called to finalize the run with output metrics.

---

## State

`PilotState` — persisted across turns via `MemorySaver` keyed by `thread_id`. The `MemorySaver` is in-memory by default; for persistent multi-session history, it can be replaced with a SQLite-backed checkpointer via configuration.

Lifecycle boundary: state exists for the duration of a `thread_id` session. A new `thread_id` starts a fresh session.

---

## Implementation Reference

`corvus_corone_pilot/v2_researcher/graph.py`

---

## SRS Traceability

Core orchestration component for all Pilot V2 use cases. Required by:
- IMPL-034 (multi-agent researcher workflow)
- IMPL-045 (Socratic Guide node integration)
- UC-09 step 2 (multi-turn state persistence via MemorySaver)
