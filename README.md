<!-- PROJECT SHIELDS -->
[![CI status][ci-status-shield]](https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone/actions)

# Project data

Project name: Corvus Corone — HPO Algorithm Benchmarking Platform

Application name: corvus-corone

Additional names: corvus (CLI command name)

Software version: 0.1.0

Repository Purpose: Python library and AI-powered pilot for reproducible, statistically rigorous benchmarking of hyperparameter optimization (HPO) algorithms. The system enforces scientific best practices — pre-registration of research questions, seed management, run independence, scoped conclusions — derived from the benchmarking methodology in *Benchmarking in Optimization: Best Practice and Open Issues* (Bartz-Beielstein et al., 2020).

<img src="https://upload.wikimedia.org/wikipedia/commons/f/fe/Carrion_Crow_%28Corvus_corone%29_%2825932479036%29.jpg" alt="Corvus corone — carrion crow" width="480">

*Photo: Bernard DUPONT, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Carrion_Crow_(Corvus_corone)_(25932479036).jpg), [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/)*

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

GitHub project board [URL](https://github.com/users/jedrzejpolaczek/projects/12).

# Technical details

Corvus Corone is structured as a **uv workspace** with two packages:

- **corvus-corone-lib** — core benchmarking library. Specified in full; implemented so far: the storage layer, the exception taxonomy, the IOHprofiler exporter and the Nevergrad adapter. Problem and Algorithm interfaces, Experiment Runner, Analysis Engine, Reporting Engine and the CLI are specified and not yet built.
- **corvus-corone-pilot** — AI-powered pilot built on LangGraph, MCP and Ollama. **Outside the V1 release** ([SRS §1 V1 Release Scope](docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md)). Two planned tiers: V2 Researcher and V3 Autonomous.

The system interoperates with COCO, IOHprofiler, and Nevergrad ecosystems via documented data-format mappings.

Full architecture documentation: [docs/02-design/02-architecture/](docs/02-design/02-architecture/)

## Environment

- **Python**: 3.10 minimum, tested on 3.10, 3.11 and 3.12 ([ADR-006](docs/02-design/02-architecture/01-adr/adr-006-python-version-and-platform-constraints.md))
- **Package manager**: [uv](https://docs.astral.sh/uv/) workspace
- **Platforms**: Linux and macOS are supported and blocking in CI; Windows is best-effort
- **External integrations** (planned): COCO, IOHprofiler, Nevergrad, Ollama (local LLM), MLflow

## File structure

```
├── .github/workflows/          <- GitHub Actions CI (push, pull request)
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
│   │   ├── src/
│   │   └── tests/
│   └── corvus-corone-pilot/    <- AI-powered pilot
│       ├── src/
│       └── tests/
├── scripts/
│   ├── pre-push                <- Git pre-push hook (docs check, linters, tests)
│   ├── check_docs.py           <- Documentation integrity gate (links, identifiers)
│   └── create_github_issues.py <- Syncs ROADMAP tasks to GitHub Issues
├── spikes/                     <- Exploratory prototypes (not production code)
├── Makefile                    <- Developer commands (lint, format, type, test)
├── pyproject.toml              <- uv workspace root
└── README.md
```

## Required tools

- **Python 3.10 or newer** — enforced by the workspace; `uv` will install it automatically
- **[uv](https://docs.astral.sh/uv/)** — required for all package management and running commands
- **[Git](https://git-scm.com/)** — required for version control and the pre-push hook
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

The hook runs the documentation integrity check, ruff, mypy and pytest before every `git push`.

# Usage

> **Status: v0.1.0 — pre-implementation.** The library is being built documentation-first.
> The contracts are written; most of the library is not. What exists today is the storage
> layer, the exception taxonomy, the IOHprofiler exporter and the Nevergrad adapter.
> You cannot yet run a benchmarking study.

**TODO — write this section after IMPL-017 (Public API + CLI).** It must contain, in this
order: installing the package, the six `corvus` commands from
[the CLI specification](docs/02-design/02-architecture/03-c4-leve2-containers/02-cli-spec.md),
and a worked study from `create_study` through `lock_study` and `run` to the two reports.
Until IMPL-017 lands, any usage example here would document an API that does not exist,
which is the failure this section previously had: it instructed the reader to
`import corvus-corone`, which is not a valid Python identifier, and to read a `__version__`
attribute that is not defined.

The intended experience is specified and can be read now:

- [Tutorial: your first study](docs/06-tutorials/01-cmd-first-study.md)
- [Tutorial: wrap an Optuna sampler](docs/06-tutorials/04-algorithm-author-onboarding.md)
- [Public API contract](docs/03-technical-contracts/04-public-api-contract.md)

### Development

```bash
uv sync --all-extras     # install the workspace and dev dependencies
uv run pytest            # tests
uv run ruff check .      # lint
uv run mypy              # types
python scripts/check_docs.py   # documentation integrity
```

macOS and Linux users can use `make lint`, `make format`, `make type`, `make test`.

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

The acceptance test strategy, including the 49 acceptance scenarios for UC-01 and UC-02, is in
[docs/02-design/01-software-requirement-specification/07-acceptance-test-strategy/](docs/02-design/01-software-requirement-specification/07-acceptance-test-strategy/).

**TODO — after IMPL-001 to IMPL-017:** state which of those scenarios have automated coverage.

# Other important informations

## Coding standards

- **Style guide**: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- **Linter / formatter**: [ruff](https://docs.astral.sh/ruff/) — line length 100, import sorting enabled (`extend-select = ["I"]`)
- **Type checker**: [mypy](https://mypy.readthedocs.io/) in strict mode
- **Terminology**: all code identifiers and docstrings must use exact terms from [docs/GLOSSARY.md](docs/GLOSSARY.md)

## Knowledge base

The reading order, and which documentation layer wins when two disagree, are in
[docs/README.md](docs/README.md) and [ADR-012](docs/02-design/02-architecture/01-adr/adr-012-documentation-layer-normativity.md).

## Contribution Guidelines

Contribution types: new benchmark problems, algorithm implementations, analysis tools/metrics, documentation, bug fixes, and architecture changes (require an ADR).

Full process, review criteria, and quality checklist: [docs/05-community/01-contribution-guide.md](docs/05-community/01-contribution-guide.md)

## Versioning convention

Entities are immutable; a revision is a new entity linked by `superseded_by`
([ADR-020](docs/02-design/02-architecture/01-adr/adr-020-entity-versioning-immutable-entities.md)).
The data schema is at version `0.0.1` and stays below `1.0.0` until the V1 release
([REF-TASK-0039](docs/ROADMAP.md)). Governance rules are in
[docs/05-community/02-versioning-governance.md](docs/05-community/02-versioning-governance.md).

**TODO — before the first release:** state the library's own release versioning scheme.

## FAQs/Troubleshooting

**TODO — after the first external users, so that the questions are real ones.** Seed it with
the failures the framework raises most often at `lock_study()`, since that is where a study is
refused (FR-27).

## License

WIP: license pending ADR decision (REF-TASK-0011). The intent from the manifesto is open code and open data under licenses that support scientific reuse and community contributions.

## Contact Information

**TODO — before opening the repository (point 8 of the audit follow-up).** Needs a maintainer
contact and an issue-reporting route, both of which the contribution guide assumes exist.

## Acknowledgments

The scientific methodology underlying Corvus Corone is derived primarily from:

> Bartz-Beielstein, T., Doerr, C., van den Berg, D., Bossek, J., Chandrasekaran, S., Eftimov, T., ... & Volz, V. (2020). **Benchmarking in Optimization: Best Practice and Open Issues**. *arXiv:2007.03488*.

## Screenshots/Media

**TODO — after IMPL-014 and IMPL-015 (Reporting Engine and visualizations).** A screenshot of a
generated researcher report is the one image that shows what the project produces.

# Release history

- **v0.1.0** — Initial monorepo setup: uv workspace, package scaffolding, documentation foundation (MANIFESTO, SRS, C1–C2 architecture, use cases, functional requirements, NFRs, constraints, interface requirements, benchmarking protocol, statistical methodology, metric taxonomy, interface contracts, data format, contribution guide, versioning governance, ROADMAP, GLOSSARY).

<!-- MARKDOWN LINKS & IMAGES -->
[ci-status-shield]: https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone/actions/workflows/ci.yml/badge.svg?branch=main
