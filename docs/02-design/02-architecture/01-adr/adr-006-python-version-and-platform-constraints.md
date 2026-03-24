# ADR-006: Python Version, Platform, and Dependency License Constraints

**Status:** Accepted

**Date:** 2026-03-23

**Deciders:** Core maintainers, technical lead

---

## Context

Three categories of technical constraint must be decided explicitly before the first public release of
`corvus-corone`:

1. **Minimum Python version.** Python version choice determines which language features are available
   in library code, which CI environments are required, and which research environments can adopt the
   library without upgrading. An unspecified minimum causes contributor confusion and production
   surprises.

2. **Supported operating systems.** The target audience includes academic researchers on Linux
   workstations and HPC clusters, ML practitioners on macOS and Windows. CI must run on at least the
   supported platforms; "works on my machine" is incompatible with reproducibility goals.

3. **Dependency license policy.** Corvus Corone targets a permissive open source license (MIT).
   Linking a GPL-only dependency makes the combined work GPL, which prevents commercial use and
   some institutional deployments. This is incompatible with the MANIFESTO goal of broad community
   adoption (Principle 27). The dependency license policy must be explicit so contributors know which
   third-party libraries are acceptable.

**Dependencies in scope for the first release** (drawn from the existing IMPL roadmap):
- `numpy` — array operations in metric computation
- `scipy` — statistical tests (Wilcoxon, Kruskal-Wallis, effect sizes)
- `pydantic` ≥ 2 — entity schema validation
- `click` — CLI interface
- `matplotlib` — visualization in reports

All of these are MIT or BSD-licensed; none are GPL.

---

## Decision

### Python version minimum: 3.10

The minimum supported Python version is **3.10**.

Version 3.10 is the minimum because:
- Structural pattern matching (`match`/`case`, PEP 634) is used in the Runner's trigger dispatch
  and in the Ecosystem Bridge's format selection path.
- The `|` union type syntax in annotations (PEP 604, available without `from __future__ import annotations`
  in 3.10) is used throughout the codebase to improve annotation readability.
- Python 3.9 reached end-of-life in October 2025 and is no longer receiving security updates.
  Requiring 3.9 would mean testing against an EOL runtime.
- Python 3.10 was released October 2021 and is in widespread use across research computing
  environments as of 2026.

Version 3.12 is **not** the minimum (even though it is the latest stable) because:
- Many HPC cluster environments lag 1–2 major Python versions behind the latest stable.
- The performance benefits of 3.12 do not justify excluding users on 3.10/3.11.

CI will test against Python **3.10, 3.11, 3.12** (three-version window). When Python 3.10 reaches EOL
(October 2026), the minimum will be bumped to 3.11 in a minor version release.

### Supported operating systems

| Platform | Support tier | CI requirement |
|---|---|---|
| Linux (x86-64) | **Primary** — all features, all tests | Required — blocking failure |
| macOS (arm64 and x86-64) | **Supported** — all features, all tests | Required — blocking failure |
| Windows 10/11 (x86-64) | **Best-effort** — known path separator issues are bugs | CI run — non-blocking on failure |

**Rationale for Linux primary:**
- Target HPC environments are Linux-only.
- Linux is the platform that most accurately reflects reproducibility conditions for published studies.
- Most CI minutes are spent on Linux.

**Rationale for macOS supported:**
- Algorithm Authors and Researchers predominantly develop on macOS.
- arm64 (Apple Silicon) is now the dominant macOS architecture.
- macOS and Linux share POSIX paths, so most code works without modification.

**Rationale for Windows best-effort:**
- Windows is common in ML practitioner workflows and should not be a hard barrier to adoption.
- Path separator differences (`\` vs `/`) are the primary source of Windows-specific bugs. These
  are tracked as bugs (not "won't fix") but do not block releases.
- Windows CI failures do not block merges to `main`; they create issues for triage.

### Dependency license policy: permissive-only

The library's public API surface MUST NOT depend on GPL-licensed packages.

**Definition of "GPL-licensed"**: any package distributed under GPL-2.0-only, GPL-3.0-only,
GPL-2.0-or-later, GPL-3.0-or-later, AGPL-3.0, or LGPL variants where the LGPL-specific exemption
does not apply (e.g., packages distributed only as LGPL-3.0-only that require modifications to be
shared back as LGPL).

**Acceptable licenses in the dependency tree:** MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0,
ISC, PSF-2.0, LGPL-2.1-or-later (with dynamic linking, where the library exception applies).

**Rationale:**
- Corvus Corone is MIT-licensed. A GPL transitive dependency would make the combined work GPL,
  which is incompatible with permissive use.
- MANIFESTO Principle 27 (community development) requires broad adoption, including commercial ML
  teams. GPL incompatibility eliminates that path.
- `scipy` and `numpy` are BSD-3-Clause; `pydantic`, `click`, `matplotlib` are MIT. No GPL
  dependencies are currently in the dependency tree.

**Enforcement:** CI includes a `licensecheck` step that fails the build if a newly added
dependency is GPL-only. Optional (development-only) dependencies are exempt from this check
but must be noted in `pyproject.toml` as optional.

### Core dependency set

The following packages are declared as runtime dependencies in `pyproject.toml`:

| Package | Version constraint | License | Purpose |
|---|---|---|---|
| `numpy` | `>=1.24` | BSD-3-Clause | Array operations; metric computation |
| `scipy` | `>=1.11` | BSD-3-Clause | Statistical tests (Wilcoxon, Kruskal-Wallis, effect sizes) |
| `pydantic` | `>=2.0` | MIT | Entity schema validation and serialization |
| `click` | `>=8.1` | BSD-3-Clause | CLI interface (`corvus` commands) |
| `matplotlib` | `>=3.7` | PSF-based (MIT-compatible) | Visualizations in reports |

**Why pydantic ≥ 2 (not 1.x):** Pydantic v2 rewrites the validation engine in Rust, producing
a 5–20× validation speedup. The V2 API (`model_validator`, `model_fields`, `ConfigDict`) is not
backward-compatible with v1. Since this is a greenfield project, adopting v2 from the start
avoids a future migration. Pydantic v1 compatibility is not maintained.

**Why numpy ≥ 1.24 (not 2.x):** NumPy 2.0 introduced breaking API changes (`np.bool` removal, etc.).
Many research environments have not yet migrated. Requiring 1.24 maintains compatibility while
excluding end-of-life 1.x releases. NumPy 2.x compatibility will be added as it stabilises
in the ecosystem.

---

## Alternatives Considered

### Python 3.9 as minimum

**Why rejected:** Python 3.9 reached EOL in October 2025. Testing against an EOL runtime means
no security patches for the test environment. `match`/`case` and `X | Y` annotation syntax would
not be available, requiring workarounds (e.g., `Union[X, Y]`, `isinstance` chains) throughout
the codebase. The usability improvement from the cleaner syntax outweighs the marginal increase
in compatibility.

### Python 3.12 as minimum

**Why rejected:** HPC cluster environments at major research institutions commonly run Python 3.10
or 3.11. Requiring 3.12 would exclude users who cannot control their cluster's Python version.
The 3.10 minimum is already beyond EOL and represents a defensible minimum.

### No Windows support at all

**Why rejected:** Windows is standard in industry ML teams and some academic labs. Explicitly
dropping Windows without a documented reason signals poor community health. Best-effort support
with clear issue tracking is a better signal than silent incompatibility.

### Allow LGPL dependencies

**Why accepted with condition:** LGPL dependencies are acceptable if the LGPL library exception
applies (i.e., the library is dynamically linked and not statically embedded). This is typically
the case for Python packages. The CI `licensecheck` step distinguishes LGPL dynamic-link (allowed)
from LGPL static-embed (blocked).

---

## Consequences

**Positive:**
- Contributors have unambiguous guidance on which Python features they may use and which
  environments they must target.
- CI matrix (Linux + macOS blocking; Windows non-blocking) gives reproducibility confidence
  on the two primary researcher platforms.
- `licensecheck` in CI prevents accidental GPL contamination before it reaches a release.
- Pydantic v2 gives fast schema validation with no legacy weight.

**Negative / Trade-offs:**
- Python 3.10 minimum excludes environments pinned to 3.8/3.9. These users will see a
  dependency resolution error and will need to upgrade Python.
- Windows best-effort means Windows bugs are not release blockers. A Windows user may encounter
  path-related issues that are tracked but slow to fix.
- Pydantic v2's API is significantly different from v1; contributors familiar with v1 will need
  to learn the v2 patterns.

**Impact on existing documents:**
- `docs/02-design/01-software-requirement-specification/05-constraints/04-const-technical.md`
  — pending decisions (Python version, OS support, license) are now resolved; CONST-TECH-04
  through CONST-TECH-07 are added.
- `docs/05-community/02-versioning-governance.md` §5 — license policy is now stated; CONST-COM-01
  is resolved.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/02-design/01-software-requirement-specification/05-constraints/04-const-technical.md` | CONST-TECH-04 through CONST-TECH-07 implement this ADR |
| `docs/02-design/01-software-requirement-specification/04-non-functional-requirements/05-nfr-open-01.md` | NFR-OPEN-01 measurable criterion references the license check from this ADR |
| `docs/02-design/01-software-requirement-specification/08-traceability-matrix/01-traceability-matrix.md` | CONST-COM-01 resolved by this ADR |
| `ADR-001` | Platform constraints follow from the library-first delivery form decided there |
