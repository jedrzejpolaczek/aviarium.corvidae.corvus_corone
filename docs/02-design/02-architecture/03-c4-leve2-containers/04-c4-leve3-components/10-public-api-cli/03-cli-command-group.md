# CLI Command Group

> Container: [Public API + CLI](../../04-public-api-cli.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Provide a Click-based command-line interface that maps `corvus` subcommands to API Facade calls, handling argument parsing, output formatting (human-readable and machine-readable JSON), and CLI-specific error display.

---

## Interface

> **Descriptive document (ADR-012).** The authoritative definition is the contract cited
> below. This page explains only how that contract is grouped into a component and why the
> boundary falls where it does. It does not define signatures.

The command surface, argument forms, terminal output and exit codes are defined in
[`02-cli-spec.md`](../../02-cli-spec.md), which ADR-016 makes authoritative.

The CLI mirrors the Python facade: a command exists only where a facade function exists, takes
the same subject in the same position, and carries the same name modulo hyphenation. Study
authoring functions have no CLI equivalent in V1.

This component is responsible for argument parsing with Click, output formatting, and mapping
the exception taxonomy of ADR-015 onto the exit codes in the CLI specification. It does not
decide what the commands are.

## Dependencies

- `click` Python package — command group, argument/option parsing
- **API Facade** — all command implementations call into the API Facade
- `rich` Python package (optional) — for progress bars and colored output

---

## Key Behaviors

1. **Delegation to API Facade** — every command is a thin wrapper: parse args → call `cc.*` → format output. No business logic in CLI commands.

2. **Output formatting** — writes the result to stdout and every progress indicator, warning and error to stderr, so that stdout stays script-consumable (FR-41). There is no global `--json` flag: `02-cli-spec.md` defines per-command output, and `--format` on `corvus export` is the only format option in V1. A component may not add one (ADR-012, ADR-016).

3. **Error display** — writes `Error: <ClassName>: <message>` to stderr, the class being the ADR-015 exception, and exits with the code that `02-cli-spec.md` §Exit codes gives for it. The prefixes and the codes are both fixed by that document: `2` is entity not found, not an unexpected exception.

4. **Progress display** — `corvus run` uses a progress callback from `cc.run()` to update a progress bar (via `rich` if installed, or simple line printing if not). Progress updates show `{completed}/{total} runs`.

5. **Config file loading** — `corvus run --config` accepts YAML or JSON. Loaded via `yaml.safe_load()` or `json.loads()` depending on file extension; passed to `cc.run()` as a dict.

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/cli/commands.py`
`corvus_corone/cli/__init__.py`

---

## SRS Traceability

- All use cases are accessible via CLI equivalents of the Python API.
- FR-40 (the CLI is a subset of the facade): every command delegates to a `cc.*` function and exposes no capability the facade lacks.
- FR-41 (output stays script-consumable): results to stdout, diagnostics to stderr, each error prefixed with its ADR-015 class name.
- FR-42 (exit codes distinguish failure categories): the mapping is the table in `02-cli-spec.md`.
- ADR-016: `02-cli-spec.md` is the authoritative CLI surface.
