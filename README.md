<!-- PROJECT SHIELDS -->
[![CI status][ci-status-shield]](https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone/actions)

# Project data

Project name: Corvus Corone — HPO Algorithm Benchmarking Platform

Application name: corvus-corone

Additional names: corvus (CLI command name)

Software version: 0.1.0

Repository Purpose: Python library and AI-powered pilot for reproducible, statistically rigorous benchmarking of hyperparameter optimization (HPO) algorithms. The system enforces scientific best practices — pre-registration of research questions, seed management, run independence, scoped conclusions — derived from the benchmarking methodology in *Benchmarking in Optimization: Best Practice and Open Issues* (Bartz-Beielstein et al., 2020).

# Table of Contents
1. [Project Data](#project-data)
2. [Project Task Board](#project-task-board)
3. [Technical Details](#technical-details)
   - [Environment](#environment)
   - [File Structure](#file-structure)
   - [Required Tools](#required-tools)
   - [Build Procedure](#build-procedure)
4. [Usage](#usage)
5. [Testing Information](#testing-information)
6. [Other Important Information](#other-important-information)
   - [Coding standards](#coding-standards)
   - [Knowledge base](#knowledge-base)
   - [Contribution Guidelines](#contribution-guidelines)
   - [Versioning Convention](#versioning-convention)
   - [FAQs/Troubleshooting](#faqstroubleshooting)
   - [License](#license)
7. [Contact Information](#contact-information)
8. [Acknowledgments](#acknowledgments)
9. [Screenshots/Media](#screenshotsmedia)
10. [Release History](#release-history)

# Project task board

GitHub Milestones track all open documentation and implementation tasks. See [docs/ROADMAP.md](docs/ROADMAP.md) for the full milestone list and open task index (REF-TASK and IMPL tasks).

WIP: GitHub project board URL pending repository setup.

# Technical details

Corvus Corone is structured as a **uv workspace** with two packages:

- **corvus-corone-lib** — core benchmarking library: Problem/Algorithm interfaces, Experiment Runner, Reproducibility Layer, Statistical Analysis, Reporting Engine, and CLI (`corvus run`, `corvus list-problems`, `corvus list-algorithms`).
- **corvus-corone-pilot** — AI-powered pilot built on LangGraph, MCP, and Ollama. Three planned tiers: V1 (library only), V2 Researcher (ReAct + multi-agent), V3 Autonomous (hypothesis generation, safety guards, DVC pipeline).

The system interoperates with COCO, IOHprofiler, and Nevergrad ecosystems via documented data-format mappings.

Full architecture documentation: [docs/02-design/02-architecture/](docs/02-design/02-architecture/)

## Environment

- **Python**: 3.13 (enforced via `.python-version` and `pyproject.toml`)
- **Package manager**: [uv](https://docs.astral.sh/uv/) workspace
- **Platforms**: Windows, macOS, Linux
- **External integrations** (planned): COCO, IOHprofiler, Nevergrad, Ollama (local LLM), MLflow

## File structure

```
├── .github/workflows/          <- GitHub Actions CI (workflow_dispatch only)
├── docs/
│   ├── 01-manifesto/           <- MANIFESTO.md — values and principles
│   ├── 02-design/              <- SRS, architecture (C1–C4), ADRs
│   ├── 03-technical-contracts/ <- Data format, interface contracts, metric taxonomy
│   ├── 04-scientific-practice/ <- Benchmarking protocol, statistical methodology
│   ├── 05-community/           <- Contribution guide, versioning governance
│   ├── 06-tutorials/           <- Step-by-step tutorials
│   ├── GLOSSARY.md
│   └── ROADMAP.md
├── packages/
│   ├── corvus-corone-lib/      <- Core benchmarking library
│   │   ├── src/corvus_corone/
│   │   └── tests/
│   └── corvus-corone-pilot/    <- AI-powered pilot
│       ├── src/corvus_corone_pilot/
│       └── tests/
├── scripts/
│   ├── pre-push                <- Git pre-push hook (runs linters + tests)
│   └── create_github_issues.py <- Syncs ROADMAP tasks to GitHub Issues
├── spikes/                     <- Exploratory prototypes (not production code)
├── Makefile                    <- Developer commands (lint, format, type, test)
├── pyproject.toml              <- uv workspace root
└── README.md
```

## Required tools

- **Python 3.13** — enforced by the workspace; `uv` will install it automatically
- **[uv](https://docs.astral.sh/uv/)** — required for all package management and running commands
- **Git** — required for version control and the pre-push hook
- **make** — optional; macOS/Linux only; provides shorthand Makefile commands (`make lint`, `make test`, etc.)

## Build procedure

**1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)**

Windows:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS / Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Clone the repository and install dependencies**

```bash
git clone https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone.git
cd aviarium.corvidae.corvus_corone
uv sync --all-extras
```

This creates a virtual environment and installs all workspace packages (`corvus-corone-lib`, `corvus-corone-pilot`) along with their dev dependencies.

**3. Install the pre-push hook (optional but recommended)**

macOS / Linux:
```bash
make install-hooks
```

Windows (Git Bash or PowerShell):
```bash
cp scripts/pre-push .git/hooks/pre-push
```

The hook runs ruff, mypy, and pytest automatically before every `git push`.

# Usage

> **Status: v0.1.0 — API is not yet stable.**

After installing (see [Build Procedure](#build-procedure)), `uv sync --all-extras` installs both workspace packages into the shared virtual environment. All `uv run` commands below must be executed from the repository root.

---

### corvus-corone-lib — core benchmarking library

Run an interactive Python session with the library available:

```bash
uv run --package corvus-corone-lib python
```

```python
>>> import corvus_corone
>>> corvus_corone.__version__
'0.1.0'
```

Run the library tests only:

```bash
uv run pytest packages/corvus-corone-lib/tests
```

---

### corvus-corone-pilot — AI-powered pilot

Run an interactive Python session with the pilot available:

```bash
uv run --package corvus-corone-pilot python
```

```python
>>> import corvus_corone_pilot
>>> corvus_corone_pilot.__version__
'0.1.0'
```

Run the pilot tests only:

```bash
uv run pytest packages/corvus-corone-pilot/tests
```

---

### Day-to-day development (linters, type checker, tests)

macOS / Linux — use the `Makefile`:

```bash
make lint      # ruff check
make format    # ruff format
make type      # mypy
make test      # pytest (all packages)
```

Windows — call `uv run` directly:

```bash
uv run ruff check .
uv run ruff format .
uv run mypy .
uv run pytest
```

Full API and tutorial documentation will be added as the codebase stabilises. See [docs/06-tutorials/](docs/06-tutorials/) for upcoming tutorials.

# Testing Information

Tests live inside each workspace package:

- `packages/corvus-corone-lib/tests/` — unit and integration tests for the core library
- `packages/corvus-corone-pilot/tests/` — unit and integration tests for the pilot

Run all tests from the repository root:

```bash
uv run pytest
```

Run tests for a single package:

```bash
uv run pytest packages/corvus-corone-lib/tests
uv run pytest packages/corvus-corone-pilot/tests
```

The same checks run automatically via the pre-push hook and the GitHub Actions CI workflow (`.github/workflows/ci.yml`, manually triggered via `workflow_dispatch`).

WIP: acceptance test strategy — see [docs/02-design/01-software-requirement-specification/07-acceptance-test-strategy/](docs/02-design/01-software-requirement-specification/07-acceptance-test-strategy/) (REF-TASK-0013).

# Other important informations

## Coding standards

- **Style guide**: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- **Linter / formatter**: [ruff](https://docs.astral.sh/ruff/) — line length 100, import sorting enabled (`extend-select = ["I"]`)
- **Type checker**: [mypy](https://mypy.readthedocs.io/) in strict mode
- **Terminology**: all code identifiers and docstrings must use exact terms from [docs/GLOSSARY.md](docs/GLOSSARY.md)

## Knowledge base

WIP: documentation narrative reading order is described in [docs/README.md](docs/README.md).

## Contribution Guidelines

Contribution types: new benchmark problems, algorithm implementations, analysis tools/metrics, documentation, bug fixes, and architecture changes (require an ADR).

Full process, review criteria, and quality checklist: [docs/05-community/01-contribution-guide.md](docs/05-community/01-contribution-guide.md)

## Versioning convention

WIP: versioning scheme pending ADR decision (REF-TASK-0011). Governance rules for artifact versioning (problem instances, algorithm implementations, data schemas, experiment results) are outlined in [docs/05-community/02-versioning-governance.md](docs/05-community/02-versioning-governance.md).

## FAQs/Troubleshooting

WIP

## License

WIP: license pending ADR decision (REF-TASK-0011). The intent from the manifesto is open code and open data under licenses that support scientific reuse and community contributions.

## Contact Information

WIP

## Acknowledgments

The scientific methodology underlying Corvus Corone is derived primarily from:

> Bartz-Beielstein, T., Doerr, C., van den Berg, D., Bossek, J., Chandrasekaran, S., Eftimov, T., ... & Volz, V. (2020). **Benchmarking in Optimization: Best Practice and Open Issues**. *arXiv:2007.03488*.

## Screenshots/Media

WIP

# Release history

- **v0.1.0** — Initial monorepo setup: uv workspace, package scaffolding, documentation foundation (MANIFESTO, SRS, C1–C2 architecture, use cases, functional requirements, NFRs, constraints, interface requirements, benchmarking protocol, statistical methodology, metric taxonomy, interface contracts, data format, contribution guide, versioning governance, ROADMAP, GLOSSARY).

<!-- MARKDOWN LINKS & IMAGES -->
[ci-status-shield]: https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone/actions/workflows/ci.yml/badge.svg?branch=main
