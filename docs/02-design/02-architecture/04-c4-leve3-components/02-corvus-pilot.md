# C3: Components — Corvus Pilot V2

> Index: [01-c3-components.md](01-c3-components.md)
> Container: [14-corvus-pilot.md](../03-c4-leve2-containers/14-corvus-pilot.md)

Corvus Pilot V2 is the LLM-powered interaction layer over the Corvus Corone core library.
It wraps library tools via MCP, routes queries through a LangGraph multi-agent graph, and
exposes two distinct interaction modes: **direct answer** (default) and **Socratic** (opt-in).
Actors: Researcher (direct mode), Learner (Socratic mode, UC-08, UC-09).

---

## Component Diagram
<!-- FIXME: diagram -->
```mermaid
---
config:
  look: neo
  theme: redux-dark
  themeVariables:
    background: transparent
---
flowchart TB
  subgraph Pilot["Corvus Pilot V2 (corvus_corone_pilot)"]
    cli["Pilot CLI\ncorvus-pilot run\n--mode socratic"]
    mcp["MCP Server\nExposes core library tools\nto LLM via @app.tool()"]
    graph["LangGraph Graph\nStudyState · interrupt · MemorySaver"]

    subgraph Agents["Agent Nodes"]
      planner["Planner Node\nDecomposes query"]
      executor["Executor Node\nCalls MCP tools"]
      analyst["Analyst Node\nInterprets results"]
      direct["Direct Answer Node\nFactual / task queries"]
      socratic["Socratic Guide Node\nEducational queries\n(never answers directly)"]
    end

    router["Query Router\nConditional edge\nroute_query()"]
    tracker["Session Tracker\nMLflow per thread"]
  end

  subgraph CoreLib["Core Library (via MCP)"]
    api["Public API + CLI"]
    registry["Algorithm Registry"]
    store["Results Store"]
  end

  cli --> graph
  graph --> router
  router -->|"mode=direct\nor task query"| planner
  router -->|"mode=socratic\nor educational query"| socratic
  planner --> executor
  executor --> analyst
  analyst --> direct
  socratic -->|"bridging question\n(no answer)"| cli
  direct --> cli
  graph --> tracker
  mcp --> api
  mcp --> registry
  mcp --> store
  executor --> mcp
  socratic --> mcp
```

---

## MCP Server

**Responsibility:** Expose the core Corvus Corone library as callable tools for the LLM,
bridging the Python API surface to the MCP `@app.tool()` interface.

**Interface:**

| Tool | Delegates to | Used by |
|---|---|---|
| `run_study(study_config)` | `cc.run()` | Executor Node |
| `list_problems(filters)` | `cc.list_problems()` | Planner Node, Socratic Guide Node |
| `list_algorithms(filters)` | `cc.list_algorithms()` | Planner Node, Socratic Guide Node |
| `get_study_results(experiment_id)` | `cc.get_result_aggregates()` | Analyst Node, Socratic Guide Node |
| `get_algorithm_properties(algorithm_id)` | `cc.get_algorithm()` | Socratic Guide Node, Direct Answer Node |

**Dependencies:** Public API + CLI container (core library).

**State:** Stateless. Each tool call is independent.

**Implementation reference:** `corvus_corone_pilot/v2_researcher/mcp_server.py`

**SRS traceability:** Enables all Pilot-served use cases by providing the tool layer.

---

## LangGraph Graph

**Responsibility:** Manage the agent session lifecycle — receive a user query, route it
to the appropriate agent node, maintain conversation state across turns via `MemorySaver`
checkpointing, and support `interrupt_before=["execute_study"]` for human-in-the-loop
confirmation before executing a study.

**Interface:**

```python
class PilotState(TypedDict):
    messages:          list[BaseMessage]   # full conversation history
    query:             str                 # current user input
    interaction_mode:  Literal["direct_answer", "socratic"]
    thread_id:         str                 # session identifier for MemorySaver
    awaiting_response: bool                # True while Socratic loop expects Learner reply
    knowledge_state:   dict | None         # assessed from conversation; populated by Socratic node
```

**Key behaviors:**
- Routing decision made at `router` node via `route_query(state)` (see Query Router below)
- `MemorySaver` persists `PilotState` between turns; each turn resumes from last checkpoint
- `interrupt_before=["execute_study"]` pauses the graph before `Executor` calls `run_study()`

**State:** `PilotState` — persisted across turns in `MemorySaver` keyed by `thread_id`.

**Implementation reference:** `corvus_corone_pilot/v2_researcher/graph.py`

---

## Query Router

**Responsibility:** Classify each incoming query and route it to the correct agent node via
a LangGraph conditional edge. The router is the single point where the `socratic` /
`direct_answer` mode boundary is enforced.

**Routing logic:**

```python
def route_query(state: PilotState) -> str:
    # Explicit mode wins
    if state["interaction_mode"] == "socratic":
        return "socratic_guide"

    # Auto-detect: does the query require reasoning rather than factual recall?
    query_type = classify_query(state["query"])
    # "educational" = how/why/where about an algorithm's mechanics
    # "task" = run a study, list problems, get results
    if query_type == "educational":
        return "socratic_guide"

    return "planner"  # task queries → Planner → Executor → Analyst → Direct Answer
```

`classify_query()` uses a lightweight LLM call with a structured output schema
(`{"type": "educational" | "task" | "factual"}`).

**State:** Stateless — reads `state["interaction_mode"]` and `state["query"]`; writes nothing.

**Implementation reference:** `corvus_corone_pilot/v2_researcher/graph.py` (inline function)

---

## Socratic Guide Node

**Responsibility:** Implement the Socratic interaction pattern from UC-09 — guide the
Learner toward their own conclusions through targeted bridging questions, never providing
the answer directly. Activated when `interaction_mode == "socratic"` or when the Query
Router detects an educational query.

This node is the architectural home of the "guide, don't answer" principle.

**Interface:**

Input state fields consumed:

| Field | Purpose |
|---|---|
| `state["messages"]` | Full conversation history — used to assess current knowledge state |
| `state["query"]` | The Learner's current question |
| `state["knowledge_state"]` | Previously assessed knowledge (persisted across turns by `MemorySaver`) |

Output state fields produced:

| Field | Value |
|---|---|
| `state["messages"]` | Appended with one `AIMessage` containing a bridging question (never an answer) |
| `state["awaiting_response"]` | Set to `True` — graph pauses here pending the Learner's reply |
| `state["knowledge_state"]` | Updated assessment after this turn |

**Key behaviors:**

1. **Assess current knowledge** — reads `state["messages"]` to infer what the Learner
   already knows about the topic. Uses a structured LLM call returning
   `{"knows": [...], "misconceptions": [...], "current_step": int}`.

2. **Identify the gap** — compares the Learner's knowledge state against the conclusion
   they are seeking. The gap is the smallest reasoning step not yet taken.

3. **Generate bridging question** — produces exactly one question that nudges the Learner
   one step toward the gap closure, without revealing the answer. The question is grounded
   in algorithm properties from `get_algorithm_properties()` or study data from
   `get_study_results()` when available.
   Example: *"What does the covariance matrix represent geometrically? Think about what
   information it encodes about the shape of the search space."*

4. **Validate response** (next turn) — when `state["awaiting_response"] == True`, evaluates
   the Learner's reply: gap closed → next gap; same error three times → change bridging
   strategy (F2 from UC-09); direct answer requested → acknowledge + offer to exit
   Socratic mode (F1 from UC-09).

5. **Confirm conclusion** — when the Learner's reasoning reaches the target, the node
   confirms their conclusion without embellishing or expanding on it.

**Distinction from Direct Answer Node:**

| Dimension | Direct Answer Node | Socratic Guide Node |
|---|---|---|
| Output | Factual answer or task result | A question only — never an answer |
| Goal | Minimize turns to resolution | Maximize Learner's independent reasoning |
| Algorithm metadata | Provides facts from registry | Uses facts only to formulate questions |
| Activation | Default; `mode=direct_answer`; task queries | `mode=socratic`; educational queries |
| UC coverage | Researcher task execution | UC-08, UC-09 Learner education |
| Session exit | Answers immediately | Stays in loop until conclusion or explicit exit |

**State:** Stateful across turns (via `PilotState` + `MemorySaver`). `knowledge_state` and
the full message history persist between turns within the same `thread_id`.

**Implementation reference:** `corvus_corone_pilot/v2_researcher/agents/socratic_guide.py`

**SRS traceability:** UC-09 Main Flow steps 1–8; UC-09 Failure Scenarios F1 (exit offer),
F2 (strategy change on repetition). IMPL-045.

---

## Planner, Executor, and Analyst Nodes

**Responsibility:** Handle task queries (study execution, results retrieval) in the default
direct-answer path. These nodes are the V2 multi-agent researcher workflow.

| Node | Responsibility | Implementation |
|---|---|---|
| Planner | Decomposes a natural-language task into a sequence of MCP tool calls | `agents/planner.py` |
| Executor | Executes MCP tool calls; pauses before `run_study()` for human confirmation | `agents/executor.py` |
| Analyst | Interprets tool results; generates the direct answer or report summary | `agents/analyst.py` |

Full multi-agent design: IMPL-034.

---

## Session Tracker

**Responsibility:** Record each Pilot session (thread) as an MLflow run — capturing the
query, interaction mode, node sequence, and token counts for observability.

**State:** Writes to MLflow tracking store (separate from core library Results Store).

**Implementation reference:** `corvus_corone_pilot/v2_researcher/tracking.py`

---

## Cross-Cutting Concerns Within This Container

**Interaction mode isolation:** `interaction_mode` is set once at session start (`--mode`
flag or first-message intent detection) and held in `PilotState` for the entire session.
Changing mode mid-session resets `knowledge_state` and `awaiting_response`.

**LLM calls:** All structured LLM calls use Ollama with a `format=json` response schema.
Calls in the Socratic Guide node are isolated from calls in the Planner/Analyst nodes —
different prompts and different output schemas.

**Safety boundary:** The Socratic Guide node MUST NOT call `run_study()` or any write-path
MCP tool. It is read-only: only `get_algorithm_properties()` and `get_study_results()` are
permitted in Socratic mode. The LangGraph graph enforces this via node-level tool access
restriction.

**Error handling:** If a MCP tool call fails (core library unavailable), the Socratic node
falls back to metadata-only questions (no empirical examples). It does not surface the
error to the Learner.

**Testing strategy:** Socratic Guide node is unit-tested via LangGraph's `invoke()` with
synthetic `PilotState` fixtures — no real LLM call required for the state-machine behavior.
Integration tests use Ollama with a deterministic seed. Acceptance criterion: the node
MUST NOT produce a message containing the answer to any test question in the fixture set.
