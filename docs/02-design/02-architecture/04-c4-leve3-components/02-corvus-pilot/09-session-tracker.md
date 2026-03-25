# Session Tracker

> Container: [Corvus Pilot V2](../../03-c4-leve2-containers/14-corvus-pilot.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Record each Pilot V2 session (identified by `thread_id`) as an MLflow run, capturing query text, interaction mode, node execution sequence, and token counts for observability and debugging.

---

## Interface

Called by the LangGraph Graph at session entry and exit:

```python
tracker.start_session(thread_id: str, query: str, interaction_mode: str) -> None
tracker.record_node_call(thread_id: str, node_name: str, tokens_in: int, tokens_out: int, latency_ms: float) -> None
tracker.end_session(thread_id: str, outcome: Literal["success", "error", "interrupted"]) -> None
```

Not called by agent nodes directly — all calls are made by the LangGraph Graph at graph lifecycle points.

---

## Dependencies

- **MLflow** (`mlflow` Python package) — tracking backend
- **LangGraph Graph** — calls this component at graph entry and exit hooks

---

## Key Behaviors

1. **Session start** — on `start_session()`, opens an MLflow run tagged with `thread_id`, `interaction_mode`, and a truncated version of the query (first 200 chars). Stores the MLflow `run_id` keyed by `thread_id` in an in-process dict.

2. **Node call recording** — on `record_node_call()`, logs a structured metric set: `tokens_in`, `tokens_out`, `latency_ms` under the key `{node_name}.*`. Also appends to an artifact `node_sequence.jsonl` that records the order of node invocations.

3. **Session end** — on `end_session()`, logs the final outcome and total token counts as MLflow metrics. Closes the MLflow run.

4. **Multi-turn accumulation** — for the same `thread_id`, subsequent turns append to the same MLflow run (not a new run). This gives a single run per logical session, not per turn.

5. **Graceful degradation** — if the MLflow tracking server is unavailable, the Session Tracker logs a warning to stderr and becomes a no-op. It does not raise an exception or block the Pilot from running.

---

## State

In-memory `dict[thread_id -> mlflow_run_id]` — maps active sessions to their MLflow run IDs. This is process-local state and is lost if the Pilot process restarts.

---

## Implementation Reference

`corvus_corone_pilot/v2_researcher/tracking.py`

---

## SRS Traceability

Observability requirement. Supports debugging and session replay for all Pilot-served use cases. Referenced by IMPL-034.
