# C3: Components — Public API + CLI

> C2 Container: [04-public-api-cli.md](../../04-public-api-cli.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

The Public API + CLI is the only way into the system. Every V1 use case is reachable through the
Python facade, and the command line is a strict subset of it: a command exists only where a facade
function exists, and a capability offered only on the command line would be a defect (FR-39,
FR-40).

Study authoring has no command-line form in V1. A Study is written in Python and executed from
either surface (ADR-016).

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| API Facade | The `cc.*` functions, their validation, and delegation inward | [`04-public-api-contract.md`](../../../../../03-technical-contracts/04-public-api-contract.md) |
| CLI Command Group | The `corvus` commands, each delegating to a facade function | ADR-016; `03-c4-leve2-containers/02-cli-spec.md` |
| Response Mapper | Turns internal records into the read-only view objects the facade returns | [`04-public-api-contract.md`](../../../../../03-technical-contracts/04-public-api-contract.md) §View Objects |

---

## Where the vocabulary comes from

| Subject | Contract |
|---|---|
| Function signatures, view objects, exceptions raised | [`03-technical-contracts/04-public-api-contract.md`](../../../../../03-technical-contracts/04-public-api-contract.md) |
| Command names, arguments, options, output conventions, error grammar, exit codes | `03-c4-leve2-containers/02-cli-spec.md` (authoritative for this surface, per ADR-016 and ADR-026) |
| Exception taxonomy the error messages name | [`02-interface-contracts/07-cross-cutting-contracts.md`](../../../../../03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md) |

The view objects the Response Mapper produces are deliberately not the storage entities. A caller
needing a storage-level field goes through the repository interface, which is outside the public
API.

