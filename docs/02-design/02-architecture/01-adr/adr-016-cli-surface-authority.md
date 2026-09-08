# ADR-016: CLI Surface Authority

<!--
STORY ROLE: Selects one of the four command-line interfaces the corpus currently specifies,
and states that the CLI mirrors the Python facade rather than inventing its own shape.

CONNECTS TO:
  → docs/02-design/02-architecture/03-c4-leve2-containers/02-cli-spec.md : the authoritative surface
  → docs/03-technical-contracts/04-public-api-contract.md : the Python facade it mirrors
  → docs/02-design/02-architecture/03-c4-leve2-containers/04-c4-leve3-components/10-public-api-cli/03-cli-command-group.md : superseded
  → docs/06-tutorials/01-cmd-first-study.md, 02-researcher-design-and-execute-study.md : corrected
-->

---

**Status:** Accepted

**Date:** 2026-09-08

**Deciders:** Core maintainers, library design lead

---

## Context

Four incompatible command-line interfaces are specified.

`03-c4-leve2-containers/02-cli-spec.md` gives positional arguments, six commands
(`run`, `list-problems`, `list-algorithms`, `report`, `verify`, `export`), example terminal
output and exit codes 0, 1, 2, 3, 4, 5 and 10 keyed to exception classes.

`04-c4-leve3-components/10-public-api-cli/03-cli-command-group.md` gives option-driven
arguments (`corvus run --config <path>`), a `list` command with subcommands rather than hyphens,
plus `resume`, `viz` and a `--json` flag, with exit codes 1 and 2 only.

`06-tutorials/01-cmd-first-study.md` gives a third form: `corvus study new --question`,
`corvus run my_study.yaml`, `corvus report my_study/ --audience researcher`.

`06-tutorials/02-researcher-design-and-execute-study.md` gives a fourth: `corvus run --study-id`,
`corvus report --experiment-id --open`, `corvus verify --experiment-id`, and `corvus --version`.

A reader cannot determine which command they are supposed to type, and IMPL-017 cannot be
implemented from the corpus as it stands.

---

## Decision

**`02-cli-spec.md` is the authoritative CLI surface.** Commands take positional arguments for
the entity they act on and options only for modifiers.

```
corvus run <study_id>
corvus list-problems [--tag <tag> ...]
corvus list-algorithms [--family <family>]
corvus report <experiment_id> [--open]
corvus verify <experiment_id>
corvus export <experiment_id> [--format <format>] [--output <path>]
```

Exit codes remain as specified there, remapped to the exception classes selected by ADR-015.

**The CLI mirrors the Python facade.** A CLI command exists only where a facade function exists,
takes the same subject in the same order, and carries the same name modulo hyphenation. Study
authoring functions, `cc.create_study()`, `cc.update_study()` and the `cc.lock_study()` added by
ADR-013, have no CLI equivalent in V1; a study is authored in Python and executed from either
surface.

`10-public-api-cli/03-cli-command-group.md` loses its command definitions and cites this
specification instead, as required by ADR-012. Both tutorials are rewritten to the authoritative
form. `corvus resume`, `corvus viz` and `--json` are not part of V1: `viz` belongs to the
deferred Algorithm Visualization Engine, and `resume` has no facade function.

---

## Rationale

`02-cli-spec.md` is the only one of the four that specifies exit codes, error message format and
example terminal output, which is what makes a CLI testable. The others describe a shape without
a contract.

Positional arguments keep the CLI parallel to the Python surface. `corvus run <study_id>` reads
the same way as `cc.run(study_id)`, so a researcher who learns one has learned the other. The
option-driven form breaks that correspondence for no gain, since every one of these commands has
exactly one subject.

Restricting the CLI to commands that mirror facade functions prevents the two surfaces from
drifting, which is how four definitions arose in the first place.

**Trade-off accepted:** authoring a study requires Python. A configuration-file entry point is a
reasonable future addition, but it is a new facade function first and a CLI command second.

---

## Alternatives Considered

### Option-driven surface from the C3 component document

**Description:** `corvus run --config study.yaml`, `corvus list algorithms`, plus `resume` and
`viz`.

**Why rejected:** No exit codes, no error format, no output examples. Introduces a YAML study
format that no contract defines, and a `viz` command for a container that is outside V1.

**Under what conditions reconsidered:** If a declarative study file format is specified as a
contract, `corvus run --config` becomes coherent and can be added alongside the positional form.

---

## Consequences

**Positive:**

- IMPL-017 becomes implementable from a single document.
- CLI and Python surfaces stay parallel by rule rather than by coincidence.
- The exit code table becomes the one place mapping failures to shell behaviour.

**Negative / Trade-offs:**

- Two tutorials need rewriting, including the first command a new user ever types.
- `corvus --version`, used in one tutorial, is not in the specification and must be added there
  or removed from the tutorial.

**Risks:**

- **Risk:** A future contributor adds a CLI command without a facade function.
  **Mitigation:** The mirroring rule is stated here and is checkable, since every command name
  must correspond to a facade function named in `04-public-api-contract.md`.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/02-design/02-architecture/03-c4-leve2-containers/02-cli-spec.md` | The authoritative surface |
| `docs/03-technical-contracts/04-public-api-contract.md` | The facade the CLI mirrors |
| `.../04-c4-leve3-components/10-public-api-cli/03-cli-command-group.md` | Command definitions removed by this ADR |
| `adr-015-exception-hierarchy-authority.md` | Exit codes are keyed to its classes |
