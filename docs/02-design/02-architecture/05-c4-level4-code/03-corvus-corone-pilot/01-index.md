# C4: Code — Corvus Pilot V2

<!-- check-docs: allow-undefined -->
<!-- This container is outside the V1 release (SRS 1). Its contracts are written
     when the Learner actor enters scope, so ADR-012 check 4 cannot resolve its
     vocabulary yet and is suppressed for this document. -->

> C4 Top-level Index: [../01-index.md](../01-index.md)
> C3 Container Index: [../../04-c4-leve3-components/02-corvus-pilot/01-index.md](../../03-c4-leve2-containers/04-c4-leve3-components/02-corvus-pilot/01-index.md)

---

## Documented Abstractions

| File | Abstraction | Why C4 |
|---|---|---|
| [02-pilot-state.md](02-pilot-state.md) | `PilotState` (TypedDict) | Shared by all 7 agent nodes — changing any field requires updating every node function and the MemorySaver checkpoint schema |

---

## Shared Abstractions Used by This Container

The following cross-container abstractions from [02-shared/](../02-shared/) are consumed here:

| Abstraction | Role in Corvus Pilot V2 |
|---|---|
| [`APIFacade` (cc.*)](../07-public-api-cli/02-api-facade.md) | The Executor Node calls `cc.run()` and `cc.visualize()` via the MCP Server to invoke core library operations |
