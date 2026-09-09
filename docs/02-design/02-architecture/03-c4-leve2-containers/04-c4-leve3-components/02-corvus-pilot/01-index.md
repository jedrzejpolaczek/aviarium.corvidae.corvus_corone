<!-- check-docs: allow-undefined -->
<!-- This container is outside the V1 release (SRS §1.4). Its contracts are written when
     the Learner actor enters scope, so the ADR-012 vocabulary check cannot resolve its
     names against 03-technical-contracts/ yet. -->

# C3: Components — Corvus Pilot

> C2 Container: [14-corvus-pilot.md](../../14-corvus-pilot.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

**V1 scope: Deferred.** Corvus Pilot is the conversational surface over the library — an MCP
server exposing the facade as tools, and a LangGraph agent that routes a query to a planning,
execution, analysis or Socratic node. It is outside V1 (SRS §1.4) and its contracts do not exist
yet, which is why this page carries the `allow-undefined` marker.

Its decomposition is recorded here so that the target architecture stays legible, not because it
is buildable. Nothing in V1 depends on it, and no V1 component may reference its state object.

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| MCP Server | Exposes the public facade as LLM-callable tools over the MCP protocol | *(contract not yet written)* |
| Graph | Holds the agent session: state, routing, checkpointing between turns | *(contract not yet written)* |
| Query Router | Classifies an incoming query and selects the node that answers it | *(contract not yet written)* |
| Socratic Guide Node | Answers a Learner's question with a bridging question rather than an answer (FR-36) | *(contract not yet written)* |
| Planner Node | Decomposes a natural-language task into a sequence of facade calls | *(contract not yet written)* |
| Executor Node | Performs those calls, pausing for confirmation before anything that executes a Study | *(contract not yet written)* |
| Analyst Node | Turns tool results into the answer the Learner or Researcher reads | *(contract not yet written)* |
| Session Tracker | Records each session for observability | *(contract not yet written)* |

---

## Where the vocabulary comes from

None of it, yet. When the Learner actor enters scope this container needs its own contract before
any of the above may be stated as specification rather than intent, and the `allow-undefined`
marker comes off in the same change.

The V1 surface it will call is already fixed: [`04-public-api-contract.md`](../../../../../03-technical-contracts/04-public-api-contract.md).


---

## Open decisions

- **REF-TASK-0047** — how the V3 autonomous capabilities stay on the right side of MANIFESTO
  anti-patterns AP-4 (opaque analysis pipelines) and AP-7 (automated algorithm selection as a
  substitute for researcher judgement). That decision shapes this container and is not made.
