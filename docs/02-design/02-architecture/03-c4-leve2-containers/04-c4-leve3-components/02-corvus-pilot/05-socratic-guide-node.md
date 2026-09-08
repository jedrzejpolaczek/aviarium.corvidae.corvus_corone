# Socratic Guide Node

> Container: [Corvus Pilot V2](../../03-c4-leve2-containers/14-corvus-pilot.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Implement the Socratic interaction pattern from UC-09 — guide the Learner toward their own conclusions through targeted bridging questions, never providing the answer directly. Activated when `interaction_mode == "socratic"` or when the Query Router detects an educational query.

---

## Interface

Input state fields consumed:

| Field | Purpose |
|---|---|
| `state["messages"]` | Full conversation history — used to assess current knowledge state |
| `state["query"]` | The Learner's current question |
| `state["knowledge_state"]` | Previously assessed knowledge (persisted across turns by `MemorySaver`) |

Output state fields produced:

| Field | Value |
|---|---|
| `state["messages"]` | Appended with one `AIMessage` containing a bridging question (never a direct answer) |
| `state["awaiting_response"]` | Set to `True` — graph expects the Learner's reply on next turn |
| `state["knowledge_state"]` | Updated assessment after this turn |

MCP tools accessible to this node (read-only subset only):
- `get_algorithm_properties(algorithm_id)`
- `get_algorithm_genealogy(algorithm_id)`
- `get_study_results(experiment_id)`

Write-path tools (`run_study`, etc.) are not accessible — enforced by the LangGraph node tool-access configuration.

---

## Dependencies

- **MCP Server** — read-only tool calls for algorithm metadata and study results
- **LangGraph Graph** — receives and returns `PilotState`; `MemorySaver` persists `knowledge_state` across turns
- **Ollama LLM** — structured-output calls for knowledge assessment and bridging question generation

---

## Key Behaviors

1. **Assess current knowledge** — reads `state["messages"]` to infer what the Learner already knows. Issues a structured LLM call returning `{"knows": [...], "misconceptions": [...], "current_step": int}`. Stores result in `state["knowledge_state"]`.

2. **Identify the gap** — compares the Learner's `knowledge_state` against the target conclusion implicit in the original query. The gap is the smallest reasoning step not yet taken.

3. **Generate bridging question** — produces exactly one question that nudges the Learner one step toward gap closure, without revealing the answer. The question is grounded in algorithm properties from `get_algorithm_properties()` or study data from `get_study_results()` when available.
   Example: *"What does the covariance matrix represent geometrically? Think about what information it encodes about the shape of the search space."*

4. **Validate response** (next turn) — when `state["awaiting_response"] == True`, evaluates the Learner's reply:
   - Gap closed → advance to next gap; update `knowledge_state`.
   - Same error three times → change bridging strategy (F2 from UC-09): try a different angle, simpler analogy, or concrete example.
   - Direct answer requested → acknowledge + offer to exit Socratic mode (F1 from UC-09).

5. **Confirm conclusion** — when the Learner's reasoning reaches the target, the node confirms their conclusion without embellishing or expanding on it. Prints the target reasoning explicitly. Does not introduce new questions.

**Distinction from Direct Answer Node:**

| Dimension | Direct Answer Node | Socratic Guide Node |
|---|---|---|
| Output | Factual answer or task result | A question only — never an answer |
| Goal | Minimise turns to resolution | Maximise Learner's independent reasoning |
| Algorithm metadata | Provides facts | Uses facts only to formulate questions |
| Activation | Default; task queries | `mode=socratic`; educational queries |
| Session exit | Answers immediately | Stays in loop until conclusion or explicit exit |

---

## State

Stateful across turns (via `PilotState` + `MemorySaver`). `knowledge_state` and the full message history persist between turns within the same `thread_id`. Resetting mode mid-session clears `knowledge_state` and `awaiting_response`.

---

## Implementation Reference

`corvus_corone_pilot/v2_researcher/agents/socratic_guide.py`

---

## SRS Traceability

- UC-09 Main Flow steps 1–8
- UC-09 Failure Scenario F1 (exit offer when Learner requests direct answer)
- UC-09 Failure Scenario F2 (strategy change on repeated same error)
- IMPL-045
