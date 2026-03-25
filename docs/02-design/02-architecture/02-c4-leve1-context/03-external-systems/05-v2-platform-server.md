# External System: V2 Platform Server (future)

> C1 Context: [../01-c1-context.md](../01-c1-context.md)

**What it is:** A planned community server providing shared result repositories, persistent artifact identifiers (DOIs), study discovery, and cross-researcher comparison — not deployed in V1.

**Why we plan to interact with it:** MANIFESTO Principles 20–22 require open data in stable repositories with persistent identifiers. A local Python library alone cannot fulfill these requirements — once a researcher closes their laptop, results are isolated. The V2 Platform Server closes this gap.

**Direction:** Bidirectional — the library's `Repository` interface can be backed by this server in V2. Researchers store studies locally in V1; they can republish to the shared server in V2 without migrating their data because all entity schemas are server-compatible from V1.

**V1 design constraint:** All entity schemas must use globally unique IDs (UUIDs), be JSON-serializable, and reference other entities by ID — not by local file path. This ensures V1-produced artifacts are valid V2 server artifacts without any migration step. This constraint is documented in `docs/03-technical-contracts/data-format.md §1` and enforced by `ADR-001`.

> **`TODO: REF-TASK-0023`** — Design the storage abstraction interface (`Repository`) that allows switching between `LocalFileRepository` (V1) and `ServerRepository` (V2) without modifying library code. Owner: library design lead. Acceptance: `docs/03-technical-contracts/interface-contracts.md` contains the `Repository` interface specification; a `LocalFileRepository` implementation passes the interface contract test suite.
