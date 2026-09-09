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

2. **Output formatting** — by default, outputs human-readable text. With `--json` flag on any command, outputs machine-readable JSON (the raw `cc.*` response dict). This supports scripting without parsing human-readable output.

3. **Error display** — catches `ValidationError` and prints each validation error on its own line with a `[ERROR]` prefix. Exits with code 1. Unexpected exceptions print a stack trace and exit with code 2.

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
- ADR-016: `02-cli-spec.md` is the authoritative CLI surface, and the CLI mirrors the
  Python facade. No functional requirement mandates a command line; see the note in
  [02-api-facade.md](02-api-facade.md).
