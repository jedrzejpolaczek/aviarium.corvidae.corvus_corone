# CLI Command Group

> Container: [Public API + CLI](../../03-c4-leve2-containers/04-public-api-cli.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Provide a Click-based command-line interface that maps `corvus` subcommands to API Facade calls, handling argument parsing, output formatting (human-readable and machine-readable JSON), and CLI-specific error display.

---

## Interface

CLI commands exposed under the `corvus` entry point:

```
corvus run    --config <path>          Run a Study from a YAML/JSON config file
corvus resume --study-id <id>          Resume a partially completed Study
corvus list   algorithms [--filter]    List registered algorithms
corvus list   problems   [--filter]    List registered problems
corvus export --experiment-id <id>     Export results to COCO/IOH/Nevergrad
              --format coco|ioh|ng
              --output-dir <path>
corvus report --experiment-id <id>     View the generated HTML report
corvus viz    --algorithm-id <id>      Generate algorithm visualizations
              --viz-type all|...
              --format png|gif|svg|html
              --experiment-id <id>     (optional)
```

---

## Dependencies

- `click` Python package — command group, argument/option parsing
- **API Facade** — all command implementations call into the API Facade
- `rich` Python package (optional) — for progress bars and colored output

---

## Key Behaviors

1. **Delegation to API Facade** — every command is a thin wrapper: parse args → call `cc.*` → format output. No business logic in CLI commands.

2. **Output formatting** — by default, outputs human-readable text. With `--json` flag on any command, outputs machine-readable JSON (the raw `cc.*` response dict). This supports scripting without parsing human-readable output.

3. **Error display** — catches `CorvusValidationError` and prints each validation error on its own line with a `[ERROR]` prefix. Exits with code 1. Unexpected exceptions print a stack trace and exit with code 2.

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
- FR-API-02 (CLI access): all core operations must be accessible from the command line.
