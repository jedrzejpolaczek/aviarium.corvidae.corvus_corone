# CLI Experience Specification — `corvus`

<!--
STORY ROLE: The terminal contract. Every command that a researcher types into a shell
has a documented synopsis, arguments, output, and exit code here. A contributor adding
a new subcommand reads this document to understand the expected shape. A CI test can
verify that actual output matches the examples here.

NARRATIVE POSITION:
  C2 (container: Public API + CLI) → this document (CLI detail)
  → 04-public-api-contract.md : the Python API that the CLI delegates to

CONNECTS TO:
  ← docs/02-design/02-architecture/03-c4-leve2-containers/01-c2-containers.md (§ Public API + CLI)
  ← docs/03-technical-contracts/04-public-api-contract.md (§ CLI Command Surface) — the authoritative
      command table; the example session below is the primary addition over that document
  → docs/02-design/01-software-requirement-specification/05-constraints/02-const-scientific.md — AP-3,
      AP-6, AP-7 constraints shape what the CLI output may and may not say
  → docs/03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md §Error Taxonomy —
      error codes and message formats used by CLI error output

REF-TASK: 0033 — Specify CLI experience — commands, arguments, terminal output
-->

---

## Overview

The `corvus` command-line tool is installed as a console script alongside the
`corvus_corone` Python package. All commands operate on the same repository as the
Python API (`import corvus_corone as cc`). The CLI is a thin shell over the public
API facade — it accepts IDs and options, calls the corresponding `cc.*` function, and
formats the result for terminal display.

**Installation:** `pip install corvus-corone-lib` installs the `corvus` entry point.

**Relationship to Python API:** Every CLI command maps directly to one or more Python
API functions (see `docs/03-technical-contracts/04-public-api-contract.md`). The CLI
does not expose any capability that is not also available via the Python API. See
§ [Relation to Python API](#relation-to-python-api) for the mapping table.

---

## Common Conventions

### Output streams

- Normal output goes to **stdout**.
- Error messages go to **stderr**.
- Progress indicators (if any) go to **stderr** so that stdout remains
  script-parseable.

### Error message format

All error output follows the format:

```
Error: <ErrorType>: <human-readable message>
```

Examples:

```
Error: NotFoundError: Study with id '3f2e1a00-...' not found.
Error: ValidationError: create_study(): problem_ids: unknown problem id 'foo-bar'.
Error: SeedCollisionError: Seed collision detected in Experiment 'abc-...': seed 42 would be assigned to multiple Runs.
```

The `<ErrorType>` matches the exception class name from `corvus_corone.exceptions`
(see `04-public-api-contract.md` §Exception Hierarchy). This allows scripts that
parse stderr to identify the error category without parsing the free-form message.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Command completed successfully. |
| `1` | General error — invalid arguments, validation failure, unwritable output path. |
| `2` | Entity not found — `NotFoundError` from the Python API. |
| `3` | Locked entity — `StudyLockedError` from the Python API. |
| `4` | Unsupported format — `UnsupportedFormatError` from the Python API. |
| `5` | Export validation failure — `ExportValidationError` or integrity check failed. |
| `10` | Seed collision — `SeedCollisionError` from the Python API. |

---

## Commands

### `corvus run`

Executes all Runs for a Study and reports the resulting Experiment.

**Synopsis:**

```
corvus run <study_id>
```

**Arguments:**

| Argument | Required | Type | Description |
|---|---|---|---|
| `<study_id>` | Yes | string | The ID of the Study to execute. Obtained from `cc.create_study()` or previously printed output. |

**Example invocation:**

```
corvus run 7c3b2f10-4a91-4e82-bcd3-0f9a1e2d8c47
```

**Example output (success):**

```
Experiment 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc completed. 300 runs finished (300 completed, 0 failed).
```

**Example output (partial failure — individual runs failed, experiment still complete):**

```
Experiment 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc completed. 300 runs finished (296 completed, 4 failed).
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Experiment completed. Individual Run failures (`status="failed"`) do not produce a non-zero exit code — they are reported in the summary line. Only a whole-Experiment failure (internal error preventing the Experiment from running at all) produces a non-zero code. |
| `1` | `<study_id>` argument is missing or malformed. |
| `2` | No Study with `<study_id>` exists. |
| `10` | Seed collision detected during execution. |

---

### `corvus list-problems`

Lists all registered problem instances, with optional tag filtering.

**Synopsis:**

```
corvus list-problems [--tag <tag> ...]
```

**Arguments:**

| Argument | Required | Type | Description |
|---|---|---|---|
| `--tag <tag>` | No | string | Filter by tag. May be specified multiple times. Only problem instances matching **all** given tags are shown. Tags are free-form strings registered with each problem instance (e.g., `continuous`, `noisy`, `d=10`). |

**Example invocation:**

```
corvus list-problems
corvus list-problems --tag noisy --tag continuous
```

**Example output:**

```
ID                                    NAME                               DIM  NOISE
----                                  ----                               ---  -----
rastrigin-d10-noiseless               Rastrigin d=10 noiseless           10   none
sphere-d10-noise-gaussian-0.1         Sphere d=10 Gaussian σ=0.1         10   gaussian_0.1
sphere-d10-noiseless                  Sphere d=10 noiseless              10   none
```

**Output when no problems match:**

```
No problem instances found.
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Command completed. Zero results is not an error. |
| `1` | Invalid `--tag` usage. |

---

### `corvus list-algorithms`

Lists all registered algorithm instances, with optional family filtering.

**Synopsis:**

```
corvus list-algorithms [--family <family>]
```

**Arguments:**

| Argument | Required | Type | Description |
|---|---|---|---|
| `--family <family>` | No | string | Filter to only algorithm instances whose `algorithm_family` exactly matches this value (e.g., `evolution_strategy`, `direct_search`, `bayesian_optimization`). |

**Example invocation:**

```
corvus list-algorithms
corvus list-algorithms --family evolution_strategy
```

**Example output:**

```
ID                   NAME                            FAMILY
--                   ----                            ------
cma-es-default       CMA-ES default configuration    evolution_strategy
nelder-mead-default  Nelder-Mead default configuration  direct_search
```

**Output when no algorithms match:**

```
No algorithm instances found.
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Command completed. Zero results is not an error. |
| `1` | Invalid `--family` usage. |

---

### `corvus report`

Generates analysis reports for a completed Experiment and prints the paths to the
generated files.

**Synopsis:**

```
corvus report <experiment_id> [--open]
```

**Arguments:**

| Argument | Required | Type | Description |
|---|---|---|---|
| `<experiment_id>` | Yes | string | The ID of the Experiment for which to generate reports. Must have `status="completed"`. |
| `--open` | No | flag | If specified, opens the `researcher` report in the system's default web browser after generation. |

**Example invocation:**

```
corvus report 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc
corvus report 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc --open
```

**Example output:**

```
[researcher]    /home/researcher/.corvus/reports/experiment-3f2e1a00-researcher.html
[practitioner]  /home/researcher/.corvus/reports/experiment-3f2e1a00-practitioner.html
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Reports generated successfully. |
| `1` | `<experiment_id>` argument is missing or malformed. |
| `2` | No Experiment with `<experiment_id>` exists, or the Experiment has no ResultAggregates (analysis has not been computed). |

---

### `corvus verify`

Verifies the data integrity of a completed Experiment — checks that all PerformanceRecords
have the required fields and that ResultAggregates are consistent with Run data.

**Synopsis:**

```
corvus verify <experiment_id>
```

**Arguments:**

| Argument | Required | Type | Description |
|---|---|---|---|
| `<experiment_id>` | Yes | string | The ID of the Experiment to verify. |

**Example invocation:**

```
corvus verify 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc
```

**Example output (no issues):**

```
Experiment 3f2e1a00-...: OK
  300 runs verified.
  0 integrity issues found.
```

**Example output (issues found, printed to stderr):**

```
Experiment 3f2e1a00-...: FAILED
  300 runs verified.
  3 integrity issues found.
  ERROR: Run 'abc-123': PerformanceRecord 'xyz-456' missing field 'objective_value'.
  ERROR: Run 'def-789': PerformanceRecord 'uvw-012' missing field 'eval_number'.
  ERROR: Run 'def-789': PerformanceRecord 'rst-345' missing field 'eval_number'.
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Verification passed; no integrity issues found. |
| `2` | No Experiment with `<experiment_id>` exists. |
| `5` | One or more integrity issues found. |

---

### `corvus export`

Exports raw PerformanceRecord data for an Experiment to a file.

**Synopsis:**

```
corvus export <experiment_id> [--format <format>] [--output <path>]
```

**Arguments:**

| Argument | Required | Type | Description |
|---|---|---|---|
| `<experiment_id>` | Yes | string | The ID of the Experiment whose data to export. |
| `--format <format>` | No | string | Output format. One of `json` (default) or `csv`. |
| `--output <path>` | No | path | Output file path. If not specified, defaults to `experiment-<id>.<format>` in the current working directory. |

**Example invocation:**

```
corvus export 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc
corvus export 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc --format csv --output results.csv
```

**Example output:**

```
Exported 45 000 PerformanceRecords to /home/researcher/experiment-3f2e1a00.json
```

**Exit codes:**

| Code | Condition |
|---|---|
| `0` | Export completed successfully. |
| `1` | `<experiment_id>` argument is missing, or `--output` path is not writable. |
| `2` | No Experiment with `<experiment_id>` exists. |
| `4` | `--format` specifies an unsupported format. |
| `5` | Export validation failed — stored data is missing mandatory fields. Report as a bug. |

---

## Complete Example Session

The following session shows a researcher conducting a full benchmarking study from
problem discovery to report generation. Steps marked `[python]` require a Python
script or interactive session; steps marked `[shell]` are CLI commands.

```
# 1. Discover available problem instances
$ corvus list-problems
ID                                    NAME                               DIM  NOISE
----                                  ----                               ---  -----
rastrigin-d10-noiseless               Rastrigin d=10 noiseless           10   none
sphere-d10-noise-gaussian-0.1         Sphere d=10 Gaussian σ=0.1         10   gaussian_0.1
sphere-d10-noiseless                  Sphere d=10 noiseless              10   none

# 2. Discover available algorithm instances
$ corvus list-algorithms
ID                   NAME                              FAMILY
--                   ----                              ------
cma-es-default       CMA-ES default configuration      evolution_strategy
nelder-mead-default  Nelder-Mead default configuration  direct_search

# 3. Design and register the study (Python API — no CLI equivalent in V1)
$ python3 << 'EOF'
import corvus_corone as cc

study = cc.create_study(
    name="CMA-ES vs Nelder-Mead on Noisy Sphere",
    research_question=(
        "Does CMA-ES achieve lower median objective value than Nelder-Mead "
        "at budget 10 000 on the noisy sphere with Gaussian noise σ=0.1, "
        "across 30 independent repetitions?"
    ),
    problem_ids=["sphere-d10-noise-gaussian-0.1"],
    algorithm_ids=["cma-es-default", "nelder-mead-default"],
    repetitions=30,
    budget=10_000,
    seed_strategy="sequential",
    pre_registered_hypotheses=[
        {
            "hypothesis": "CMA-ES achieves lower median QUALITY-BEST_VALUE_AT_BUDGET.",
            "test_type": "wilcoxon_signed_rank",
        }
    ],
)
print(study.id)
EOF
7c3b2f10-4a91-4e82-bcd3-0f9a1e2d8c47

# 4. Execute the study
$ corvus run 7c3b2f10-4a91-4e82-bcd3-0f9a1e2d8c47
Experiment 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc completed. 60 runs finished (60 completed, 0 failed).

# 5. Verify data integrity before reporting
$ corvus verify 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc
Experiment 3f2e1a00-...: OK
  60 runs verified.
  0 integrity issues found.

# 6. Generate reports and open the researcher report in a browser
$ corvus report 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc --open
[researcher]    /home/researcher/.corvus/reports/experiment-3f2e1a00-researcher.html
[practitioner]  /home/researcher/.corvus/reports/experiment-3f2e1a00-practitioner.html

# 7. Export raw data for archival or external analysis
$ corvus export 3f2e1a00-8b12-47d1-a9c4-e5f6d7890abc --format csv --output sphere-study-raw.csv
Exported 30 000 PerformanceRecords to /home/researcher/sphere-study-raw.csv
```

---

## Relation to Python API

Every CLI command delegates to a public API function. The table below shows the mapping.
For full parameter documentation, exception details, and return type descriptions, see
`docs/03-technical-contracts/04-public-api-contract.md`.

| CLI command | Python API function(s) |
|---|---|
| `corvus list-problems [--tag ...]` | `cc.list_problems(tags=[...])` |
| `corvus list-algorithms [--family ...]` | `cc.list_algorithms(family=...)` |
| `corvus run <study_id>` | `cc.run(study_id)` |
| `corvus report <experiment_id>` | `cc.generate_reports(experiment_id)` |
| `corvus verify <experiment_id>` | `cc.export_raw_data(experiment_id)` (internal check) |
| `corvus export <experiment_id>` | `cc.export_raw_data(experiment_id, format=...)` |

**Note:** `cc.create_study()`, `cc.get_experiment()`, `cc.get_runs()`,
`cc.get_result_aggregates()`, and `cc.update_study()` have no CLI equivalents in V1.
These operations are available only through the Python API. The rationale is that
`create_study()` requires structured data (lists, dicts) that is awkward to pass as
CLI arguments, and the retrieval functions are intended for use in analysis scripts
rather than interactive shell sessions.

---

## Constraints and Anti-patterns

The CLI output obeys the same scientific constraints as the Python API:

- **AP-1 (no rankings):** `corvus report` never outputs a "best algorithm" declaration.
  Reports describe performance profiles and scope conditions, not rankings.
- **AP-6 (no marketing):** Output messages are factual. `corvus run` reports run counts,
  not qualitative judgements like "excellent results".
- **AP-7 (no automated selection):** `corvus report` does not recommend an algorithm.
  Reports provide evidence; the researcher interprets.

These constraints are enforced at the Reporting Engine level
(`docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md`) and
are not solely a CLI concern.
