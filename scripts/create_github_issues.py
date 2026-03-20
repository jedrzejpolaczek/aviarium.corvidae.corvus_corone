"""
corvus_corone — GitHub Milestones + Issues creator
===================================================
Creates all tasks as GitHub Issues grouped into Milestones.

Usage:
    pip install PyGithub
    export GITHUB_TOKEN=your_personal_access_token
    python create_github_issues.py --repo owner/repo-name

Or pass token directly:
    python create_github_issues.py --repo owner/repo-name --token ghp_xxx
"""

import argparse
import os
import sys
import time

try:
    from github import Github, GithubException
except ImportError:
    print("ERROR: PyGithub not installed. Run: pip install PyGithub")
    sys.exit(1)


# ── MILESTONES ────────────────────────────────────────────────────────────────

MILESTONES = [
    {
        "title": "V1 Core — Contracts & Architecture",
        "description": (
            "Foundation tasks: complete C2/C3 architecture, SRS functional requirements, "
            "interface contracts, data format specification, and GLOSSARY. "
            "These tasks were blocked on C2 design and are now unblocked after Phases 1–2 implementation."
        ),
    },
    {
        "title": "V1 Methodology — Statistics & Metrics",
        "description": (
            "Scientific methodology tasks: formalize ECDF_AREA computation, "
            "statistical test selection procedure, ANYTIME metric decisions, "
            "diversity requirements, and sensitivity documentation format."
        ),
    },
    {
        "title": "V1 Interoperability — Ecosystem Integration",
        "description": (
            "Interoperability tasks: COCO format mapping, Nevergrad adapter pattern, "
            "IOHprofiler export specification. Includes spikes for unknown territory "
            "before implementation."
        ),
    },
    {
        "title": "V1 Infrastructure — ADRs & Technical Constraints",
        "description": (
            "Infrastructure decisions: Python version, OS support, licensing constraints, "
            "bulk storage format (Parquet vs HDF5), repository storage abstraction."
        ),
    },
    {
        "title": "Post-V1 — Continuous Improvement",
        "description": (
            "Post-V1 tasks that require empirical data from real studies before they "
            "can be completed: metric extensions, research question archetypes, "
            "tutorial expansion."
        ),
    },
    {
        "title": "Learner Actor — Education Platform",
        "description": (
            "New actor introduced after V1: Learner persona with Algorithm Visualization, "
            "Socratic guidance mode, algorithm history/evolution features. "
            "Requires C1, SRS, C2, GLOSSARY updates."
        ),
    },
]


# ── ISSUES ────────────────────────────────────────────────────────────────────

ISSUES = [
    # ── MILESTONE: V1 Core — Contracts & Architecture ────────────────────────
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0001] Extend GLOSSARY from interface-contracts and data-format",
        "labels": ["documentation", "glossary"],
        "body": """
## Why This Task
Without this task, new terms introduced by interface-contracts.md and data-format.md exist in code but not in the shared vocabulary. Two contributors using the same term to mean different things is a silent source of inconsistency that code review cannot catch. The GLOSSARY is the single source of truth for terminology — every term defined there prevents one future misunderstanding.

## Summary
Once `docs/03_technical_contracts/interface-contracts.md` and `docs/03_technical_contracts/data-format.md` are filled with real content, all new terms introduced in those documents must be added to `docs/GLOSSARY.md` with precise definitions.

## Acceptance Criteria
- [ ] Every public method parameter name in `interface-contracts.md` has a corresponding GLOSSARY entry if not already defined
- [ ] Every entity field name in `data-format.md` that has domain-specific semantics has a GLOSSARY entry
- [ ] No synonyms for existing terms are introduced — new entries either add new terms or refine existing ones
- [ ] All GLOSSARY entries are cross-referenced with the documents where they are used

## Source
`docs/GLOSSARY.md`

## Dependencies
Completion of `interface-contracts.md` and `data-format.md`
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0002] Verify Schema Version definition against data-format.md",
        "labels": ["documentation", "glossary"],
        "body": """
## Why This Task
Schema Version is defined in two places: GLOSSARY.md and data-format.md §6. If they diverge, contributors follow different rules without knowing it. Versioning governance is the kind of policy that breaks quietly — no test fails, but artifacts become incompatible. Synchronizing these definitions closes that gap.

## Summary
The GLOSSARY definition of "Schema Version" must be verified and updated once `docs/03_technical_contracts/data-format.md` §6 (Schema Versioning) is filled. The definition and the policy must use identical terminology.

## Acceptance Criteria
- [ ] GLOSSARY "Schema Version" definition matches the versioning scheme in `data-format.md` §6
- [ ] The "Used in" field of the GLOSSARY entry lists all documents that reference Schema Version

## Source
`docs/GLOSSARY.md`

## Dependencies
Completion of `data-format.md` §6
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0008] Complete SRS §4, §5, §7, §8 after C2 architecture design",
        "labels": ["architecture", "srs", "blocked"],
        "body": """
## Why This Task
SRS §4 cannot be written speculatively — functional requirements written before implementation are often inaccurate. C2 containers are now implemented in code (weeks 1–16). Writing FR-XX from working public methods produces requirements that are specific, testable, and accurate. Without this, SRS §4 remains a placeholder and the traceability chain from MANIFESTO to code is broken.

## Summary
Sections §4 (Functional Requirements), §5 NFR measurable criteria, §7 (Interface Requirements), and §8 (Acceptance Test Strategy) of the SRS require C2 containers to be designed first. C2 is now complete after Phases 1–2 implementation.

## Acceptance Criteria
- [ ] §4 has formal FR-XX requirements for each C2 container with MoSCoW priority and acceptance criteria
- [ ] §5 has measurable criteria for all 6 NFRs
- [ ] §7 lists all external interfaces with format, direction, and failure handling
- [ ] §8 maps each requirement to at least one test category
- [ ] §9 Traceability Matrix is complete (no "TBD" entries)

## Source
`docs/02_design/01_software_requirement_specification/SRS.md`

## Dependencies
C2 containers designed (complete after implementation phases)
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0009] Expand UC-01 and UC-02 into full use case descriptions",
        "labels": ["architecture", "srs"],
        "body": """
## Why This Task
UC-01 and UC-02 are the highest-traffic use cases in the system — Researcher runs a study, Algorithm Author contributes. Without fully specified main flows, failure scenarios, and preconditions, contributors implement them differently. Each gap in the use case is a future inconsistency between implementations.

## Summary
UC-01 (Researcher runs a study) and UC-02 (Algorithm Author contributes) are the highest-priority use cases. Expand them into full use case descriptions with main flow, preconditions, postconditions, and failure scenarios.

## Acceptance Criteria
- [ ] Each use case has a numbered main flow, preconditions, postconditions, and at least 2 failure scenarios
- [ ] Each use case has a corresponding tutorial in `docs/06_tutorials/`
- [ ] Each use case has at least one end-to-end test in the test suite

## Source
`docs/02_design/01_software_requirement_specification/SRS.md`

## Dependencies
REF-TASK-0008 (C2 needed to describe main flows)
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0010] Add measurable criteria to all NFRs",
        "labels": ["architecture", "srs"],
        "body": """
## Why This Task
NFRs without measurable criteria are assertions, not requirements. "The system must be reproducible" is untestable. "Two runs with identical (algorithm, problem, seed, budget) produce bit-identical PerformanceRecord sequences" is testable. Without measurable criteria, NFRs cannot drive automated verification.

## Summary
The 6 Non-Functional Requirements in SRS §5 currently state what quality attribute is required but not how it is measured. Each NFR needs at least one testable, measurable criterion.

## Acceptance Criteria
- [ ] NFR-REPRO-01: criterion states what "identical results" means (bit-for-bit? numerical tolerance? platform constraints?)
- [ ] NFR-STAT-01: criterion states what automated checks are applied before generating a report
- [ ] NFR-INTEROP-01: criterion states round-trip test conditions for each platform
- [ ] NFR-OPEN-01: criterion states approved license types and format allowlist
- [ ] NFR-MODULAR-01: criterion states the plugin test procedure
- [ ] NFR-USABILITY-01: criterion states what "first study" scenario is used for timing

## Source
`docs/02_design/01_software_requirement_specification/SRS.md`
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0011] Define technical constraints (Python version, OS, dependencies)",
        "labels": ["architecture", "adr"],
        "body": """
## Why This Task
Python version, OS support, and dependency licensing constraints are decisions that affect every contributor and every deployment. Made implicitly, they produce inconsistent environments. Made explicitly in an ADR with rationale, they give contributors clear guidance and give CI a verifiable baseline.

## Summary
The SRS §6 technical constraints section is currently a placeholder. Once the first architectural decisions are made (Python version, OS support, key dependencies), record them here and in ADRs.

## Acceptance Criteria
- [ ] Python minimum version stated and justified in an ADR
- [ ] Supported operating systems listed
- [ ] Core dependency restrictions defined (e.g., no GPL dependencies if library uses MIT license)
- [ ] All constraints recorded as ADRs in `docs/02_design/02_architecture/adr/`

## Proposed Decision (ADR-002)
- Python: >=3.10
- OS: Linux (primary), macOS (supported), Windows (best-effort)
- License: MIT — no GPL dependencies
- Core deps: numpy, scipy, pydantic>=2, click, matplotlib

## Source
`docs/02_design/01_software_requirement_specification/SRS.md`

## Fulfillment Note
This task is fulfilled by IMPL-018 (ADR-002). Close this task when IMPL-018 is merged and `pyproject.toml` reflects the constraints.""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0012] Fill SRS §7 Interface Requirements from interop mappings",
        "labels": ["architecture", "srs"],
        "body": """
## Why This Task
SRS §7 was blocked until the interop mappings (REF-TASK-0005, 0006, 0007) were defined. Those are now complete. Without §7, each external interface (COCO, Nevergrad, IOHprofiler) has no formal specification of direction, format, and failure handling — only informal knowledge in code comments.

## Summary
Once the external interface format mappings (REF-TASK-0005, 0006, 0007) are defined, fill SRS §7 with formal interface requirements for each external system.

## Acceptance Criteria
- [ ] Each external system from C1 has an interface requirement entry in SRS §7
- [ ] Each entry states: direction, data format, protocol, and failure handling
- [ ] Requirements reference the detailed specifications in `data-format.md` §3

## Source
`docs/02_design/01_software_requirement_specification/SRS.md`

## Dependencies
REF-TASK-0005, REF-TASK-0006, REF-TASK-0007
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0013] Fill SRS §8 Acceptance Test Strategy",
        "labels": ["architecture", "srs", "testing"],
        "body": """
## Why This Task
Every FR-XX must map to at least one test for the SRS to be actionable. Without this mapping, requirements exist in one document and tests exist in another with no connection between them. Contributors cannot know which tests protect which requirements, and requirements can be broken silently.

## Summary
Map each requirement to a specific test category and file once the system architecture is designed.

## Acceptance Criteria
- [ ] Every FR-XX requirement maps to at least one test
- [ ] Every NFR maps to at least one automated test or benchmark procedure
- [ ] The reproducibility test procedure (run same study twice, compare results) is formally defined

## Source
`docs/02_design/01_software_requirement_specification/SRS.md`

## Dependencies
REF-TASK-0008 (FR-XX requirements), C3 components designed
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0023] Design the Repository storage abstraction interface",
        "labels": ["architecture", "interface", "adr"],
        "body": """
## Why This Task
The Repository interface is the architectural boundary that makes V1 local storage and V2 server storage interchangeable. Without this interface defined precisely, the ExperimentRunner and Orchestrator are coupled to file paths. ADR-001 established this constraint from day one — this task fulfills it.

## Summary
The `Repository` interface is the storage abstraction that allows switching between `LocalFileRepository` (V1) and `ServerRepository` (V2) without modifying any library code. This is the key architectural boundary from ADR-001.

## Acceptance Criteria
- [ ] `docs/03_technical_contracts/interface-contracts.md` contains a `Repository` interface specification with methods for all entity types
- [ ] Interface methods accept and return entity IDs (UUIDs), not file paths
- [ ] A `LocalFileRepository` implementation is provided and passes all interface contract tests
- [ ] No code outside `Repository` implementations calls file I/O functions directly
- [ ] Integration test demonstrates swapping `LocalFileRepository` for a mock `ServerRepository` requires zero changes to calling code

## Source
`docs/02_design/02_architecture/c1-context.md`, `ADR-001`

## Dependencies
Completion of `data-format.md` §2 (entity definitions); ADR-001

## Fulfillment Note
This task is fulfilled as part of IMPL-010. The Repository interface specification in `interface-contracts.md` should be written after `repository.py` exists — documentation from implementation, not before. Close when IMPL-010 PR includes the interface-contracts.md update.""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0032] Reconcile anti-pattern numbering and add anti-patterns to MANIFESTO",
        "labels": ["documentation", "architecture", "srs"],
        "body": """
## Why This Task
SRS §6 constraints cite anti-patterns by number (AP-1, AP-3 through AP-7). Anti-pattern 2 is absent from every document. The anti-patterns exist only in C1's scope exclusion table — not in MANIFESTO, which is the authoritative source of principles and constraints. A contributor reading the MANIFESTO cannot find the anti-patterns that the SRS says govern the system's scope. SRS constraints citing a non-authoritative location means the constraint chain is broken at its root.

## Summary
Add an explicit Anti-patterns section to `docs/01-manifesto/MANIFESTO.md`, resolve the numbering gap at Anti-pattern 2, and update `docs/02_design/01_software_requirement_specification/SRS.md` §6 to reference MANIFESTO as the authoritative source rather than C1.

## Acceptance Criteria
- [ ] Anti-patterns section exists in MANIFESTO with sequentially numbered entries
- [ ] Anti-pattern 2 is either defined and added, or the numbering gap is explained with an explicit note (author decision required)
- [ ] SRS §6 constraint references cite MANIFESTO anti-patterns section, not C1
- [ ] C1 scope exclusion table cross-references the MANIFESTO anti-patterns section

## Source
`docs/01-manifesto/MANIFESTO.md`, `docs/02_design/01_software_requirement_specification/SRS.md`

## Dependencies
Author decision required on what Anti-pattern 2 should be (or why it was intentionally skipped).
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0033] Specify CLI experience — commands, arguments, terminal output",
        "labels": ["documentation", "api"],
        "body": """
## Why This Task
IMPL-017 implements `corvus run`, `corvus list-problems`, and `corvus list-algorithms`, but a CLI without a written specification defines its contract only through its implementation. A contributor adding a new subcommand cannot know the expected output format. A researcher following documentation cannot predict what the terminal will show. Without this spec, it is impossible to distinguish bugs from intended behavior, and CI cannot verify output format compliance.

## Summary
Write the CLI specification for all `corvus_corone` commands: synopsis, arguments, expected terminal output, produced files, exit codes, and error message format. Document from the working implementation after IMPL-017 is merged — do not speculate before it exists.

## Acceptance Criteria
- [ ] Each command (`corvus run`, `corvus report`, `corvus export`, `corvus list-problems`, `corvus list-algorithms`) has: synopsis, description, required/optional arguments with types, example invocation, example terminal output
- [ ] At least one complete example session is shown: researcher runs a study from invocation to report
- [ ] Exit codes are documented for success, user error, and system error cases
- [ ] Error message format is documented and consistent with the error taxonomy in `interface-contracts.md` §6
- [ ] Document lives in `docs/02_design/02_architecture/c2-containers.md` (Public API + CLI section) or a dedicated spec linked from C2

## Source
`docs/02_design/02_architecture/c2-containers.md`

## Dependencies
IMPL-017 (CLI must be implemented before it can be accurately documented — spec from running code, not speculation)

## Fulfillment Note
Run `corvus --help` and each subcommand `--help`, transcribe the actual behavior into the spec, then verify against the CLI test suite. Close when the spec matches implemented behavior and is linked from C2.
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0034] Specify report output format — sections, visualizations, audience language",
        "labels": ["documentation", "reporting"],
        "body": """
## Why This Task
IMPL-014 and IMPL-015 implement the Reporting Engine and visualizations, but what the reports contain — which sections, which visualizations, what audience-appropriate language means — is not specified anywhere. A researcher who runs a study cannot predict what they will receive. A contributor extending the reporting module cannot know the output contract. Every report structural change is a potentially breaking change with no documented baseline to compare against.

## Summary
Write the report output format specification for both Practitioner and Researcher report levels. Document from the working Reporting Engine after IMPL-014 and IMPL-015 are merged — capture what the system actually produces, then formalize it.

## Acceptance Criteria
- [ ] Practitioner report structure documented: sections, mandatory visualizations, scope statement location, what "works well on" language requires
- [ ] Researcher report structure documented: sections, statistical outputs, metric tables, mandatory limitations section format
- [ ] Output format decided and documented (Markdown, HTML, or other); ADR created if the choice is non-obvious
- [ ] Each mandatory visualization (VIZ-L1-01..03) described: what it shows, axis labels, how to interpret it
- [ ] Connection to Level 1 visualizations spec (REF-TASK-0019 / IMPL-020) is explicit

## Source
`docs/02_design/02_architecture/c2-containers.md` (Reporting Engine section)

## Dependencies
IMPL-014 (Reporting Engine), IMPL-015 (Visualizations), REF-TASK-0019 (Level 1 visualizations spec)

## Fulfillment Note
Generate a real report from the integrated system using a known study, then write the spec from what was actually produced. Close when the spec can be used to verify future report completeness in CI.
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0035] Add competitive differentiation statement to SRS §2",
        "labels": ["documentation", "srs"],
        "body": """
## Why This Task
A researcher evaluating Corvus Corone alongside COCO, Nevergrad, and IOHprofiler will ask: "What does this give me that those tools do not?" The MANIFESTO implies the answer — pre-registration enforcement, three-level statistical analysis, multi-audience reporting, anti-ranking stance — but never states it as a positioning statement. Without this, contributors cannot explain the system's purpose, scope decisions lack a shared rationale anchor, and the SRS §2 System Overview describes what the system does without explaining why it exists alongside the tools it interoperates with.

## Summary
Add a concise competitive differentiation paragraph to `docs/02_design/01_software_requirement_specification/SRS.md` §2 (System Overview). Every claim must map to a specific MANIFESTO principle or SRS requirement. Positioning is complementary, not adversarial — Corvus Corone exports to COCO, Nevergrad, and IOHprofiler rather than replacing them.

## Acceptance Criteria
- [ ] SRS §2 contains a differentiation paragraph of 3–6 sentences grounded in MANIFESTO principles
- [ ] The paragraph names at least: pre-registration enforcement, three-level statistical framework, multi-audience reporting, and the anti-ranking stance
- [ ] The paragraph frames Corvus Corone as complementary to existing tools (consistent with C1 interoperability scope — Principle 26)
- [ ] No marketing language: every claim is traceable to a specific MANIFESTO principle number or SRS NFR

## Source
`docs/02_design/01_software_requirement_specification/SRS.md`
""",
    },
    {
        "milestone": "V1 Core — Contracts & Architecture",
        "title": "[REF-TASK-0036] Document LocalFileRepository directory structure",
        "labels": ["documentation", "storage"],
        "body": """
## Why This Task
When a researcher runs `corvus run`, files appear on disk. Without documentation of the directory layout, the researcher cannot interpret what they are looking at, cannot back up results selectively, and cannot understand what `corvus export` is packaging. The layout is also the concrete proof that ADR-001's server-compatibility constraint is satisfied: UUID-keyed files with no path-based entity references mean results are recoverable by ID alone and can migrate to a server repository without structural changes.

## Summary
Document the directory structure produced by `LocalFileRepository` after a completed study. Write from the working implementation after IMPL-010 is merged. Include an annotated directory tree showing every file type, its format, and when it is created.

## Acceptance Criteria
- [ ] An annotated directory tree is shown for a representative completed study (e.g., 2 algorithms × 3 problems × 10 runs)
- [ ] Each file type explained: entity it stores, format (JSON / chosen bulk format), the creation trigger (which API call produces it)
- [ ] The documentation explicitly notes that directory layout is an implementation detail of `LocalFileRepository` and is not part of the public `Repository` interface (ADR-001)
- [ ] `data-format.md §3` (File Formats and Storage) contains or links to this annotated tree

## Source
`docs/03_technical_contracts/data-format.md`

## Dependencies
IMPL-010 (LocalFileRepository must be implemented before its layout can be documented)

## Fulfillment Note
Run a small study end-to-end, capture the resulting directory with `tree`, annotate each file against the entity definitions in `data-format.md §2`. Close when the annotated tree is merged into `data-format.md §3` and matches the actual file output verified by the repository contract tests.
""",
    },

    # ── MILESTONE: V1 Methodology — Statistics & Metrics ─────────────────────
    {
        "milestone": "V1 Methodology — Statistics & Metrics",
        "title": "[REF-TASK-0014] Review and extend metric definitions after first studies",
        "labels": ["methodology", "metrics", "post-v1"],
        "body": """
## Why This Task
The five initial metrics derive from known patterns in HPO benchmarking literature. After running real studies, new patterns emerge — metrics for mixed search spaces, multi-objective scenarios, or noise sensitivity. These cannot be specified speculatively before empirical data exists. This task is scheduled post-V1 by design, not by deferral.

## Summary
The five initial metrics derive from MANIFESTO Principle 12. After conducting the first real studies, new metrics may be needed (e.g., for categorical/mixed search spaces, for multi-objective HPO).

## Acceptance Criteria
- [ ] Each new metric follows the definition template in `metric-taxonomy.md` §2
- [ ] New metrics are added to the Metric Selection Guide in §4
- [ ] Any metrics proposed for the Standard Reporting Set are decided via ADR

## Note
This task is **Post-V1** — it requires empirical data from real studies before it can be meaningfully completed.

## Source
`docs/03_technical_contracts/metric-taxonomy.md`
""",
    },
    {
        "milestone": "V1 Methodology — Statistics & Metrics",
        "title": "[REF-TASK-0015] Add implementation references to all metric definitions",
        "labels": ["methodology", "metrics", "documentation"],
        "body": """
## Why This Task
Each metric in metric-taxonomy.md has a placeholder "Implementation reference" field. Without this field populated, the document describes what a metric computes but not where. When the analysis module changes, no one knows which metric definitions are affected. The reference makes the documentation traceable to code.

## Summary
Each metric definition in `metric-taxonomy.md` §2 has a placeholder "Implementation reference" field. Once the analysis module is built, fill these with module/function references.

## Acceptance Criteria
- [ ] Every metric definition has an accurate implementation reference pointing to `corvus_corone/analysis/metrics.py`
- [ ] When code changes affect a metric computation, the reference is updated as part of the PR
- [ ] Stale references are flagged in CI

## Source
`docs/03_technical_contracts/metric-taxonomy.md`

## Dependencies
Analysis module implementation (corvus_corone/analysis/metrics.py)

## Fulfillment Note
This task is fulfilled as part of IMPL-011. Add implementation references to `metric-taxonomy.md` immediately after `metrics.py` is merged. Close when IMPL-011 PR includes the doc updates.""",
    },
    {
        "milestone": "V1 Methodology — Statistics & Metrics",
        "title": "[REF-TASK-0016] Formalize ANYTIME-ECDF_AREA computation procedure",
        "labels": ["methodology", "metrics"],
        "body": """
## Why This Task
ANYTIME-ECDF_AREA requires normalization before aggregation across problems. Without a formalized procedure, two implementations of the same metric produce different numbers. MANIFESTO Principle 19 (full reproducibility) requires that any two researchers computing ECDF_AREA on the same data get the same result.

## Summary
The ANYTIME-ECDF_AREA metric definition acknowledges that normalization bounds and aggregation across problems need formal specification. Two independent implementations must produce identical results on the same dataset.

## Acceptance Criteria
- [ ] Exact computation procedure documented in `metric-taxonomy.md` §2 (ANYTIME-ECDF_AREA)
- [ ] Normalization strategy chosen and documented: empirical min/max (ADR-003)
- [ ] Aggregation across problems defined
- [ ] Two reference implementations verified to produce identical results on a shared test dataset

## Proposed Decision (ADR-003)
Use empirical normalization (min/max across all runs in the study) because known optima are unavailable for real ML tasks. Limitation: ECDF_AREA values are not comparable across studies.

## Source
`docs/03_technical_contracts/metric-taxonomy.md`
""",
    },
    {
        "milestone": "V1 Methodology — Statistics & Metrics",
        "title": "[REF-TASK-0017] Decide whether TIME-EVALUATIONS_TO_TARGET joins Standard Reporting Set",
        "labels": ["methodology", "metrics", "adr"],
        "body": """
## Why This Task
TIME-EVALUATIONS_TO_TARGET requires a pre-specified target, which adds planning burden before every study. Including it in the Standard Reporting Set means every researcher must specify it. Excluding it means researchers who care about convergence speed must opt in manually. The decision needs to be made explicitly and documented in an ADR so it is not relitigated on every study.

## Summary
TIME-EVALUATIONS_TO_TARGET requires a pre-specified target value, which adds planning burden. Weigh this against its scientific value as an efficiency metric.

## Acceptance Criteria
- [ ] ADR created in `docs/02_design/02_architecture/adr/` recording the decision
- [ ] Standard Reporting Set in `metric-taxonomy.md` §3 updated accordingly
- [ ] Benchmarking Protocol Step 5 updated if the metric is added to the mandatory set

## Source
`docs/03_technical_contracts/metric-taxonomy.md`
""",
    },
    {
        "milestone": "V1 Methodology — Statistics & Metrics",
        "title": "[REF-TASK-0018] Add research question archetypes to Metric Selection Guide",
        "labels": ["methodology", "documentation", "post-v1"],
        "body": """
## Why This Task
A list of metrics does not tell a researcher which metrics to use for their specific question. Archetypes map research intent to metric sets. They cannot be written speculatively — they must emerge from real research questions that appear repeatedly in practice. This task is post-V1 because the patterns need to exist before they can be documented.

## Summary
The Metric Selection Guide in `metric-taxonomy.md` §4 should grow as research patterns emerge from actual studies, with each archetype linked to a tutorial.

## Proposed Archetypes
1. **Budget efficiency comparison** — TIME-EVALUATIONS_TO_TARGET + ANYTIME-ECDF_AREA
2. **Robustness across problem landscape** — RELIABILITY-SUCCESS_RATE + RELIABILITY-IQR_RATIO
3. **Cold start vs warm start** — ANYTIME curves early segment analysis

## Acceptance Criteria
- [ ] Each archetype has a corresponding tutorial in `docs/06_tutorials/`
- [ ] Each tutorial demonstrates the full Protocol workflow end-to-end

## Note
**Post-V1** — requires patterns from real studies to emerge first.

## Source
`docs/03_technical_contracts/metric-taxonomy.md`
""",
    },
    {
        "milestone": "V1 Methodology — Statistics & Metrics",
        "title": "[REF-TASK-0019] Specify required Level 1 visualizations in statistical-methodology.md",
        "labels": ["methodology", "visualization", "reporting"],
        "body": """
## Why This Task
Without a formal list of required Level 1 visualizations, two reports from the same study can look completely different. The ReportingEngine cannot verify completeness. MANIFESTO Principle 13 requires three-level analysis — Level 1 (exploratory) must have a defined minimum set of visualizations for this requirement to be enforceable.

## Summary
Fill `docs/04_scientific_practice/methodology/statistical-methodology.md` §2 with the specific required visualizations for Exploratory Data Analysis.

## Proposed Mandatory Visualizations
- **VIZ-L1-01**: Boxplot per algorithm — distribution of QUALITY-BEST_VALUE_AT_BUDGET
- **VIZ-L1-02**: Convergence curves — median best-so-far (reuse from reporting module)
- **VIZ-L1-03**: ECDF per problem (reuse from reporting module)
- **VIZ-L1-04**: Violin plot (optional, when n_runs > 50)

## Acceptance Criteria
- [ ] List of required visualization types documented in §2
- [ ] Each visualization: name, what it shows, when most useful, how to interpret
- [ ] System generates all required visualizations automatically without extra configuration

## Source
`docs/04_scientific_practice/methodology/statistical-methodology.md`

## Dependencies
Reporting module design (complete after week 12 implementation)
""",
    },
    {
        "milestone": "V1 Methodology — Statistics & Metrics",
        "title": "[REF-TASK-0020] Specify statistical test selection procedure and correction methods",
        "labels": ["methodology", "statistics"],
        "body": """
## Why This Task
The choice between Wilcoxon and Kruskal-Wallis, and between Bonferroni and Holm-Bonferroni correction, is not obvious to every contributor. Without a documented decision tree, different studies apply different tests — making cross-study comparison of p-values meaningless. The decision tree in statistical-methodology.md §3 makes the choice deterministic and auditable.

## Summary
Fill `docs/04_scientific_practice/methodology/statistical-methodology.md` §3 with a decision tree for test selection.

## Decision Tree
- 2 algorithms → Wilcoxon signed-rank (paired, non-parametric)
- >2 algorithms → Kruskal-Wallis + Holm-Bonferroni post-hoc pairwise
- Paired vs unpaired: HPO benchmarking uses same problems → paired

## Acceptance Criteria
- [ ] Decision tree documented for: two-algorithm comparison, multi-algorithm comparison, paired vs. unpaired cases
- [ ] Recommended correction methods listed (Holm-Bonferroni preferred over Bonferroni)
- [ ] References Bartz-Beielstein et al. (2020)
- [ ] `metric-taxonomy.md` statistical treatment notes reference this section

## Source
`docs/04_scientific_practice/methodology/statistical-methodology.md`
""",
    },
    {
        "milestone": "V1 Methodology — Statistics & Metrics",
        "title": "[REF-TASK-0021] Define minimum diversity requirements for Problem Instance selection",
        "labels": ["methodology", "problems"],
        "body": """
## Why This Task
A study with a single problem instance produces results scoped to that instance only (MANIFESTO Principle 3). Without a minimum diversity requirement enforced by the system, researchers can inadvertently draw conclusions from insufficient coverage. The system must warn — or block — when the problem set is too narrow for the stated research question.

## Summary
The Benchmarking Protocol Step 3 defers defining minimum diversity requirements. These need to be formally specified and enforced by the system.

## Proposed Requirements (ADR-005)
- Minimum 5 Problem Instances per study
- Must cover at least 2 different dimensionality ranges
- At least 1 problem with noise, 1 deterministic

## Acceptance Criteria
- [ ] Minimum number of Problem Instances per study defined and justified
- [ ] Required spread across diversity characteristics specified
- [ ] SRS §4.1 (Problem Repository FR) updated with these requirements
- [ ] System validates Study record against these criteria before allowing Experiment to begin

## Source
`docs/04_scientific_practice/methodology/benchmarking-protocol.md`
""",
    },
    {
        "milestone": "V1 Methodology — Statistics & Metrics",
        "title": "[REF-TASK-0022] Define sensitivity documentation format in Algorithm Instance schema",
        "labels": ["methodology", "algorithms", "data-format"],
        "body": """
## Why This Task
MANIFESTO Principle 11 requires sensitivity documentation alongside every algorithm contribution. Without a formal schema field in the Algorithm Instance definition, contributors document sensitivity differently or not at all. The field in data-format.md §2.2 makes the requirement inspectable — CI can verify its presence automatically.

## Summary
MANIFESTO Principle 11 requires sensitivity documentation alongside Algorithm Instance contributions. The format needs to be defined in the Algorithm Instance schema.

## Proposed Schema Field
```python
class SensitivityReport(BaseModel):
    tested_on_problems: list[str]
    budget_used: int
    repetitions_per_config: int  # min 10
    parameters: list[ParameterSensitivity]
    overall_stability: str  # "robust" | "moderate" | "sensitive"
    notes: str
```

## Acceptance Criteria
- [ ] `data-format.md` §2.2 includes a `sensitivity_report` field specification
- [ ] Benchmarking Protocol Step 4 references the format
- [ ] `contribution-guide.md` §2 requires sensitivity documentation as review criterion

## Source
`docs/04_scientific_practice/methodology/benchmarking-protocol.md`

## Dependencies
Completion of `data-format.md` §2.2
""",
    },

    # ── MILESTONE: V1 Interoperability ────────────────────────────────────────
    {
        "milestone": "V1 Interoperability — Ecosystem Integration",
        "title": "[REF-TASK-0004] Define Algorithm Author onboarding tutorial (15-line wrapper)",
        "labels": ["documentation", "tutorial", "algorithm-author"],
        "body": """
## Why This Task
The 15-line wrapper challenge is not a documentation goal — it is an interface test. If wrapping an Optuna sampler requires more than 15 lines, the Algorithm interface has too much surface area for third-party contributors. The tutorial exists as the acceptance criterion: a contributor should be able to complete it without reading any other documentation.

## Summary
The system's core promise to Algorithm Authors is minimal boilerplate: wrap an existing optimizer in approximately 10–15 lines of code. A tutorial must demonstrate this concretely.

## Acceptance Criteria
- [ ] Tutorial exists in `docs/06_tutorials/` following `TEMPLATE.md` format
- [ ] Tutorial shows wrapping an Optuna sampler as an Algorithm Instance in ≤ 15 lines
- [ ] Tutorial is self-contained (a reader can complete it without reading other docs first)
- [ ] Tutorial references the Algorithm Interface (`interface-contracts.md` §2)

## Source
`docs/02_design/02_architecture/c1-context.md`

## Dependencies
Completion of `interface-contracts.md` §2 (Algorithm Interface)
""",
    },
    {
        "milestone": "V1 Interoperability — Ecosystem Integration",
        "title": "[SPIKE → REF-TASK-0005] COCO format mapping in data-format.md §3",
        "labels": ["interop", "spike", "coco"],
        "body": """
## Summary
**This task requires a spike first.** Document how Corvus data entities map to COCO's data formats. Identify what is preserved and what is lost in translation.

## Spike Questions
1. What does COCO `.info` / `.dat` / `.tdat` format look like? (install `cocoex` and inspect)
2. Does COCO assume continuous search space only?
3. Which Corvus fields have no equivalent in COCO format?
4. What Python library reads/writes COCO format?

## Spike Output
A mapping table draft for `data-format.md` §3.

## Implementation Acceptance Criteria
- [ ] `data-format.md` §3 contains a COCO mapping table with documented data loss
- [ ] A study result can be exported and loaded by COCO's analysis tools without errors
- [ ] An interoperability test verifies the round-trip

## Source
`docs/02_design/02_architecture/c1-context.md`

## Dependencies
Completion of `data-format.md` §2 (entity definitions)
""",
    },
    {
        "milestone": "V1 Interoperability — Ecosystem Integration",
        "title": "[SPIKE → REF-TASK-0006] Nevergrad adapter pattern and tutorial",
        "labels": ["interop", "spike", "nevergrad"],
        "body": """
## Summary
**This task requires a spike first.** Define the standard adapter pattern for wrapping Nevergrad optimizers and document it in a tutorial.

## Spike Questions
1. Do all Nevergrad optimizers have ask-tell API?
2. How does `ng.p.Dict` map to Corvus `SearchSpace`?
3. How many lines of boilerplate for a generic wrapper?
4. How to pin Nevergrad version in Algorithm Instance metadata?

## Spike Output
Working `NevergradAdapter` class and data-format.md §3 Nevergrad mapping.

## Implementation Acceptance Criteria
- [ ] Generic `NevergradAdapter` in `corvus_corone/algorithms/adapters/nevergrad_adapter.py`
- [ ] Tutorial in `docs/06_tutorials/` demonstrates wrapping a Nevergrad optimizer
- [ ] Nevergrad format mapping documented in `data-format.md` §3

## Source
`docs/02_design/02_architecture/c1-context.md`

## Dependencies
REF-TASK-0004 (Algorithm Interface tutorial)
""",
    },
    {
        "milestone": "V1 Interoperability — Ecosystem Integration",
        "title": "[REF-TASK-0007] IOHprofiler export format mapping — full spec + round-trip test",
        "labels": ["interop", "iohprofiler"],
        "body": """
## Why This Task
IOHprofiler is the standard tool for ECDF-based anytime performance visualization in the benchmarking community. Without this bridge, researchers who want to use IOHanalyzer must convert results manually. Partial export with documented data loss is more useful than refusing to export — the .meta.json sidecar preserves what the .dat format cannot hold.

## Summary
Export Performance Records in IOHprofiler's `.dat` format so researchers can use IOHanalyzer for visualization. Implementation started in week 11 — this task formalizes the specification and adds full acceptance testing.

## Mapping (data-format.md §3)
| Corvus field | IOHprofiler field | Notes |
|---|---|---|
| PerformanceRecord.evaluation_number | .dat column 1 | direct |
| PerformanceRecord.objective_value | .dat column 2 | direct |
| RunRecord.problem_id | funcName in header | requires string |
| RunRecord.algorithm_id | algId in header | direct |
| RunRecord.seed | not in .dat | stored in sidecar .meta.json |

## Acceptance Criteria
- [ ] `data-format.md` §3 contains IOHprofiler mapping table
- [ ] Performance Records export to `.dat` format and load in IOHanalyzer without errors
- [ ] Sidecar `.meta.json` stores fields not supported by `.dat` format
- [ ] An interoperability test verifies the export

## Source
`docs/02_design/02_architecture/c1-context.md`

## Dependencies
Completion of `data-format.md` §2.6 (PerformanceRecord)
""",
    },

    # ── MILESTONE: V1 Infrastructure — ADRs & Technical Constraints ───────────
    {
        "milestone": "V1 Infrastructure — ADRs & Technical Constraints",
        "title": "[SPIKE → REF-TASK-0024] Decide bulk PerformanceRecord storage format (Parquet vs HDF5)",
        "labels": ["infrastructure", "spike", "storage", "adr"],
        "body": """
## Summary
**This task requires a spike first.** A study with 5 algorithms × 10 problems × 30 repetitions × 100 evaluations = 150,000 PerformanceRecords. JSON at that scale is too slow. Decide on a secondary bulk format.

## Spike: Benchmark These Options
```python
# Generate 150k records and measure:
# 1. JSON write time and file size
# 2. Parquet (pyarrow, snappy compression) write time and file size
# 3. HDF5 (h5py, gzip compression) write time and file size
# 4. Query time: "give me all objective_values for run_id=X"
```

## Constraint (ADR-001)
Primary schema remains JSON. Binary format is a secondary optimization only.

## Spike Output
ADR-006 with benchmark numbers and chosen format.

## Implementation Acceptance Criteria
- [ ] ADR created with benchmark evidence
- [ ] `data-format.md` §3 updated with primary (JSON) + secondary (chosen) format
- [ ] Repository.save_bulk_records() writes chosen format transparently
- [ ] Round-trip test: bulk-stored records produce identical analysis to JSON-stored records

## Source
`data-format.md §1`

## Dependencies
`data-format.md` §2.6 (PerformanceRecord); REF-TASK-0023 (Repository interface)
""",
    },

    # ── MILESTONE: Post-V1 ────────────────────────────────────────────────────
    # (REF-TASK-0014 and 0018 already above with post-v1 label)

    # ── MILESTONE: Learner Actor ──────────────────────────────────────────────
    {
        "milestone": "Learner Actor — Education Platform",
        "title": "[REF-TASK-0025] Add Learner actor to C1 context document",
        "labels": ["architecture", "learner", "c1"],
        "body": """
## Why This Task
The Learner actor does not fit any existing C1 persona. Researcher draws conclusions. Practitioner consumes results for decisions. Learner builds understanding from results. Without a formal actor definition, the system has no basis for Learner-specific interfaces, use cases, or acceptance criteria. Everything downstream depends on this definition existing.

## Summary
Add a new **Learner** actor to `docs/02_design/02_architecture/c1-context.md`. The Learner is a new type of user who consumes Researcher study results for educational purposes rather than research.

## Actor Definition
**Role:** A student, practitioner, or researcher seeking to understand HPO algorithm behavior through interactive exploration and guided discovery.

**Goal:** Build deep understanding of optimization algorithms through visualization of mathematical foundations, historical context, and Socratic guidance — without running studies themselves.

**Gives the system:** Learning queries, algorithm exploration requests, feedback on explanations.

**Gets from the system:**
- Algorithm visualizations (mathematical + intuitive, for general audiences)
- Historical context: where the method came from, what problem it solved
- Socratic guidance: guided questions instead of direct answers
- Access to Researcher study results as learning material

**Consumes output of:** Researcher (study results as teaching material)

**Relevant principles:** 25 (accessibility for different audiences), 28 (education and support), 3 (scoped conclusions)

## Acceptance Criteria
- [ ] Learner actor added to `c1-context.md` with full definition following existing actor format
- [ ] Learner's relationship to Researcher data flow documented
- [ ] Learner added to the C1 context diagram (Mermaid)

## Source
Use Cases UC-01..UC-04 from product backlog
""",
    },
    {
        "milestone": "Learner Actor — Education Platform",
        "title": "[REF-TASK-0026] Add Learner use cases to SRS §3 (UC-07..UC-11)",
        "labels": ["architecture", "learner", "srs"],
        "body": """
## Why This Task
Use cases UC-01 through UC-05 describe Researcher and Practitioner workflows. The Learner's workflows — visualization, contextual help, Socratic guidance, historical exploration — are absent from SRS §3. Without these use cases, C2 component design has no requirements to satisfy and implementation has no acceptance criteria.

## Summary
Add formal use cases for the Learner actor to `docs/02_design/01_software_requirement_specification/SRS.md` §3.

## Use Cases to Add
| ID | Trigger | Goal |
|---|---|---|
| UC-07 | Learner wants to understand how an algorithm works visually | Generate mathematical + intuitive algorithm visualization |
| UC-08 | Learner needs contextual help about an algorithm | Get explanation: how it works, why it works, where it works, with examples |
| UC-09 | Learner wants to be guided toward understanding rather than told answers | Use Socratic mode: system challenges, guides, but does not conclude for the user |
| UC-10 | Learner wants to understand algorithm history and evolution | Explore algorithm genealogy: what problem it solved, what inspired it, what it inspired |
| UC-11 | Learner explores Researcher study results | Consume benchmarking results as educational material with interpretive support |

## Acceptance Criteria
- [ ] UC-07..UC-11 added to SRS §3 following existing use case format
- [ ] Each use case has: Actor, Trigger, Goal, Gives system, Gets from system
- [ ] Each use case references relevant MANIFESTO principles

## Source
Product backlog Use Cases 1–4

## Dependencies
REF-TASK-0025 (Learner actor must exist in C1 first)
""",
    },
    {
        "milestone": "Learner Actor — Education Platform",
        "title": "[REF-TASK-0027] Add Algorithm Visualization container to C2",
        "labels": ["architecture", "learner", "c2", "visualization"],
        "body": """
## Why This Task
The Learner actor requires a visualization capability that does not exist in the current C2 architecture. The existing Reporting Engine produces researcher-facing outputs. Algorithm Visualization requires a different interface — accessible to non-specialists, focused on intuition not statistical validity. Adding it to C2 makes the architectural boundary explicit.

## Summary
Add a new **Algorithm Visualization Engine** container to `docs/02_design/02_architecture/c2-containers.md` to serve UC-07 and UC-10.

## Proposed Container
**Responsibility:** Generate mathematical and intuitive visualizations of HPO algorithm mechanics from Corvus study data.

**Technologies:** matplotlib (static), plotly (interactive), manim (animations for educational use)

**Consumes:** Results Store (study data from Researcher runs), Algorithm Registry (algorithm metadata)

**Exposes:** Visualization artifacts (PNG, HTML, GIF) for embedding in reports and Learner interface

**Actors served:** Learner (primary), Researcher (secondary — enriched reports)

## Acceptance Criteria
- [ ] Algorithm Visualization Engine container added to C2 diagram (Mermaid)
- [ ] Container definition includes: Responsibility, Technology, Interfaces, Dependencies, Actors served
- [ ] Relationship to Researcher data flow documented
- [ ] ADR created for visualization technology choices (matplotlib vs plotly vs manim)

## Dependencies
REF-TASK-0025, REF-TASK-0026
""",
    },
    {
        "milestone": "Learner Actor — Education Platform",
        "title": "[REF-TASK-0028] Add Socratic Guide component to C2/C3 (Pilot V2 extension)",
        "labels": ["architecture", "learner", "c2", "c3", "agent"],
        "body": """
## Why This Task
Socratic mode is a fundamentally different interaction pattern from the existing agent behavior: it guides rather than answers. Without a formal component definition in C2/C3, Socratic mode has no clear home in the architecture and risks being implemented as a scattered set of prompt modifications rather than a coherent component.

## Summary
Add **Socratic Guide** as a component within the Corvus Pilot V2 (Researcher assistant) that implements UC-09. This is a new interaction mode where the agent guides rather than answers.

## Proposed Design
**Activation:** `--mode socratic` flag in Pilot CLI or `mode: "socratic"` in StudyConfig

**LangGraph implementation:** Conditional edge — when query type is `educational` → route to `socratic_guide` node instead of `direct_answer` node.

**Socratic node behavior:**
1. Identify what the Learner already knows (ask)
2. Identify the gap
3. Generate a targeted question that bridges the gap
4. Validate the Learner's answer before proceeding

**Example interaction:**
- User: "Why does CMA-ES use a covariance matrix?"
- Socratic response: "What does the covariance matrix represent geometrically? Think about what information it encodes about the search space."

## Acceptance Criteria
- [ ] Socratic Guide component added to C2/C3 with full definition
- [ ] LangGraph implementation design documented
- [ ] Distinction from direct-answer mode documented
- [ ] Tutorial exists demonstrating Socratic mode in practice

## Dependencies
REF-TASK-0025, REF-TASK-0026, REF-TASK-0027
""",
    },
    {
        "milestone": "Learner Actor — Education Platform",
        "title": "[REF-TASK-0029] Add Learner terms to GLOSSARY.md",
        "labels": ["documentation", "learner", "glossary"],
        "body": """
## Why This Task
Learner, Algorithm Visualization, Socratic Mode, and Algorithm Genealogy are new concepts with no existing definitions. Without GLOSSARY entries, contributors implementing these features may interpret them differently. The GLOSSARY entries also force precision — writing a one-sentence definition reveals ambiguity that was invisible before.

## Summary
Add new terms introduced by the Learner actor to `docs/GLOSSARY.md`.

## Terms to Add

### Algorithm Visualization
**Definition:** A graphical representation of an HPO algorithm's mechanics designed to be accessible to two different audiences: mathematically precise (for Researcher and Algorithm Author), and intuitively understandable (for Learner).

### Algorithm Genealogy
**Definition:** The historical lineage of an optimization method — what problem it was designed to solve, what methods preceded it, and what methods it inspired. Distinct from an algorithm's mathematical specification.

### Socratic Mode
**Definition:** An interaction mode in Corvus Pilot where the system guides the Learner toward understanding through targeted questions rather than providing direct answers. Named after the Socratic method of inquiry.

### Learner
**Definition:** A user who consumes Researcher study results for educational purposes — to understand HPO algorithm behavior — rather than to conduct primary research or make algorithm selection decisions.

## Acceptance Criteria
- [ ] All four terms added to GLOSSARY.md with full definition format
- [ ] Each entry includes: Definition, Distinguished from, Used in, Example (optional)
- [ ] Cross-references to C1, SRS §3, C2 where applicable

## Dependencies
REF-TASK-0025..0028
""",
    },
    {
        "milestone": "Learner Actor — Education Platform",
        "title": "[REF-TASK-0030] Add Learner education tutorials to docs/06_tutorials/",
        "labels": ["documentation", "learner", "tutorial"],
        "body": """
## Why This Task
Tutorials for the Learner persona do not exist. The existing tutorials (wrap Optuna sampler, run a study) target Algorithm Authors and Researchers. Without Learner-specific tutorials, the actor exists in documentation but is inaccessible in practice. Each tutorial is also an acceptance test: if you cannot explain a feature to a Learner in a self-contained tutorial, the feature interface needs work.

## Summary
Add tutorials serving the Learner persona to `docs/06_tutorials/`. These complement the existing Algorithm Author and Researcher tutorials.

## Tutorials to Create

### `04_explore_algorithm_visualization.md`
**Use case:** UC-07
**Content:** How to generate mathematical + intuitive visualizations for any algorithm in Corvus. Includes: convergence animation, parameter sensitivity heatmap, search trajectory plot.

### `05_understand_algorithm_with_socratic_mode.md`
**Use case:** UC-09
**Content:** How to use Socratic mode to build understanding of CMA-ES (worked example). Demonstrates: activation, example dialogue, how to know when understanding is achieved.

### `06_algorithm_genealogy_explorer.md`
**Use case:** UC-10
**Content:** How to explore algorithm history. Example: MAB → Bayesian optimization → TPE lineage. Includes: historical context, what problem each method solved, visual timeline.

## Acceptance Criteria
- [ ] All three tutorials exist in `docs/06_tutorials/` following `TEMPLATE.md` format
- [ ] Each tutorial is self-contained (reader can complete it without reading other docs)
- [ ] Each tutorial references the corresponding use case in SRS §3
- [ ] Tutorials cover the example topics from product backlog: SHAP, CMA-ES, Pareto front, MAB

## Dependencies
REF-TASK-0025..0029
""",
    },
]

print(f"Total issues defined: {len(ISSUES)}")
milestones_in_issues = set(i["milestone"] for i in ISSUES)
print(f"Milestones referenced: {milestones_in_issues}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def get_or_create_milestone(repo, title, description):
    """Get existing milestone by title or create it."""
    for m in repo.get_milestones(state="open"):
        if m.title == title:
            print(f"  ✓ Milestone exists: {title}")
            return m
    m = repo.create_milestone(title=title, description=description)
    print(f"  + Created milestone: {title}")
    time.sleep(0.5)
    return m


def get_or_create_label(repo, name, color="0075ca"):
    """Get existing label or create it."""
    try:
        return repo.get_label(name)
    except GithubException:
        try:
            label = repo.create_label(name=name, color=color)
            time.sleep(0.3)
            return label
        except GithubException:
            return None


LABEL_COLORS = {
    "documentation": "0075ca",
    "architecture":  "e4e669",
    "methodology":   "a2eeef",
    "metrics":       "7057ff",
    "interop":       "d93f0b",
    "infrastructure":"0052cc",
    "spike":         "e11d48",
    "adr":           "f97316",
    "srs":           "6366f1",
    "glossary":      "84cc16",
    "testing":       "22c55e",
    "tutorial":      "14b8a6",
    "post-v1":       "f59e0b",
    "learner":       "c026d3",
    "c1":            "6b7280",
    "c2":            "6b7280",
    "c3":            "6b7280",
    "visualization": "ec4899",
    "agent":         "f97316",
    "algorithm-author": "0ea5e9",
    "coco":          "dc2626",
    "nevergrad":     "2563eb",
    "iohprofiler":   "16a34a",
    "storage":       "78716c",
    "problems":      "854d0e",
    "algorithms":    "0e7490",
    "data-format":   "6d28d9",
    "blocked":       "b91c1c",
    "implementation": "10b981",
    "portfolio":     "0ea5e9",
    "pilot-v2":      "06b6d4",
    "pilot-v3":      "f97316",
    "ml-foundations":"8b5cf6",
    "ci-cd":         "64748b",
    "mcp":           "0ea5e9",
    "langgraph":     "6366f1",
    "rag":           "f59e0b",
    "llm":           "4f46e5",
    "mlops":         "059669",
    "dvc":           "84cc16",
    "security":      "dc2626",
    "multi-agent":   "7c3aed",
    "optuna":        "3b82f6",
    "nevergrad":     "2563eb",
    "spike":         "e11d48",
    "reporting":     "0891b2",
    "statistics":    "4f46e5",
}



# ── IMPLEMENTATION MILESTONES ─────────────────────────────────────────────────
# One per phase of the 47-week learning plan + implementation plan
# Separate from documentation TASKS.md milestones

IMPL_MILESTONES = [
    {
        "title": "IMPL Phase 0 — Project Setup",
        "description": "Monorepo initialization: pyproject.toml, uv workspace, GitHub Actions CI skeleton. Must be completed before any implementation task.",
    },
    {
        "title": "IMPL Phase 1 — corvus_corone Library",
        "description": "Core library implementation: Problem/Algorithm interfaces, Runner, Storage, Analysis, Reporting, Orchestrator, Public API.",
    },
    {
        "title": "IMPL Phase 2 — Repo Closure",
        "description": "ADRs, bulk storage implementation after spike, IOHprofiler/COCO/Nevergrad bridges, LLM analysis tools.",
    },
    {
        "title": "IMPL Phase 3a — Pilot V2 Researcher",
        "description": "corvus_corone_pilot V2: MCP server, ReAct agent, LangGraph graph, ML foundations (backprop, surrogate, XGBoost), multi-agent system, MLflow tracking.",
    },
    {
        "title": "IMPL Phase 3b — Pilot V3 Autonomous",
        "description": "corvus_corone_pilot V3: hypothesis generation, meta-analysis, safety module, autonomous cycle with DVC, shadow/canary deployment, agent evaluation harness.",
    },
    {
        "title": "IMPL Phase 4 — Learner Actor",
        "description": "Learner implementation: Algorithm Visualization Engine, Socratic Guide LangGraph node, Algorithm Genealogy module.",
    },
]


# ── IMPLEMENTATION ISSUES ─────────────────────────────────────────────────────
# 47 implementation tasks — one per week of the learning plan
# Each maps to a specific file/module to create

IMPL_ISSUES = [
    # ── Phase 0: Project Setup ─────────────────────────────────────────────
    {
        "milestone": "IMPL Phase 0 — Project Setup",
        "title": "[IMPL-000] Setup monorepo: uv workspace, pyproject.toml, CI skeleton",
        "labels": ["implementation", "infrastructure", "ci-cd"],
        "body": """
## Why This Task
Without a working CI pipeline from the first commit, adding it later requires retrofitting tests, fixing lint errors in existing code, and negotiating CI failures mid-feature. The cost of CI setup grows with the size of the codebase. Starting with an empty package that passes CI establishes the standard before any code exists to violate it.

## Summary
Initialize the monorepo structure with uv workspace managing two packages: `corvus_corone` (library) and `corvus_corone_pilot` (agents). Set up GitHub Actions CI.

## Current State
Repository contains documentation only. No Python code exists yet.

## Tasks
- [ ] Create root `pyproject.toml` with `[tool.uv.workspace]` members
- [ ] Create `corvus_corone/pyproject.toml` with core dependencies (numpy, scipy, pydantic>=2, click, matplotlib)
- [ ] Create `corvus_corone_pilot/pyproject.toml` with agent dependencies (langgraph, mcp, ollama, mlflow, xgboost)
- [ ] Create `corvus_corone/__init__.py`
- [ ] Create `corvus_corone_pilot/__init__.py`
- [ ] Create `.github/workflows/ci.yml`: lint (ruff), type check (mypy), tests (pytest) on push
- [ ] CI matrix: ubuntu + macos × python 3.10 + 3.11 + 3.12
- [ ] Add `uv.lock` to version control

## File Structure After Completion
```
aviarium.corvidae.corvus_corone/
├── pyproject.toml          # uv workspace root
├── uv.lock
├── corvus_corone/
│   ├── pyproject.toml
│   └── __init__.py
├── corvus_corone_pilot/
│   ├── pyproject.toml
│   └── __init__.py
└── .github/workflows/ci.yml
```

## Dependencies
None — this is the first task.

## References
ADR-002 technical constraints, REF-TASK-0011
""",
    },

    # ── Phase 1: corvus_corone Library ─────────────────────────────────────
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-001] Problem Interface: base.py, ABC, EvaluationResult, SearchSpace",
        "labels": ["implementation", "problems", "interface"],
        "body": """
## Why This Task
The Problem interface is the contract between the benchmarking infrastructure and every problem implementation. Without it, the ExperimentRunner cannot call evaluate() deterministically, and contributors cannot know what they must implement. Every other module depends on this contract existing before it can be built.

## Summary
Implement the core Problem Interface as defined in `docs/03_technical_contracts/interface-contracts.md` §1.

## Files to Create
- `corvus_corone/problems/base.py`
- `tests/test_problem_interface.py`

## Implementation Requirements
- [ ] `EvaluationResult` dataclass: `objective_value: float`, `evaluation_number: int`, `metadata: dict`
- [ ] `SearchSpace` dataclass: `variables: list`, `dimensions: int`
- [ ] `Problem` ABC with `@abstractmethod`: `evaluate()`, `get_search_space()`, `get_remaining_budget()`, `reset(seed)`
- [ ] `TypeError` raised immediately when subclass missing abstract methods
- [ ] Contract test: `test_problem_interface_enforced()`

## References
`interface-contracts.md` §1, REF-TASK-0023
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-002] Problem Repository: registry.py, decorator, auto-discovery",
        "labels": ["implementation", "problems"],
        "body": """
## Why This Task
Problem discovery requires a mechanism to find and register implementations without a central manifest file. A central dict requires every contributor to edit the same file — a merge conflict source. The decorator registry makes each module self-registering and validates interface compliance at import time, not at runtime.

## Summary
Implement the Problem Repository with decorator-based registration and automatic discovery via `importlib`.

## Files to Create
- `corvus_corone/problems/registry.py`
- `tests/test_problem_registry.py`

## Implementation Requirements
- [ ] `ProblemRepository` class with `_registry: dict[str, type]`
- [ ] `@registry.register('name')` decorator — validates on registration, not on use (fail-early)
- [ ] Raises `ValueError` on duplicate registration
- [ ] Raises `TypeError` if class doesn't implement Problem interface
- [ ] `discover(package_path)` using `pkgutil.walk_packages` + `importlib.import_module`
- [ ] `get(name)` raises `KeyError` with available names listed

## References
MANIFESTO Principles 4–7
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-003] SearchSpace types: ContinuousVariable, IntegerVariable, CategoricalVariable",
        "labels": ["implementation", "problems"],
        "body": """
## Why This Task
CMA-ES applied to a categorical search space produces incorrect results without raising an error. Integer variables are discrete but ordered — optimizers that treat them as continuous introduce systematic bias. Without typed variable descriptors, algorithm-problem compatibility cannot be checked before a study runs.

## Summary
Implement typed variable descriptors for search spaces with Pydantic v2 validation.

## Files to Create
- `corvus_corone/problems/search_space.py`
- `tests/test_search_space.py`

## Implementation Requirements
- [ ] `ContinuousVariable(BaseModel)`: name, lower, upper — validator: upper > lower
- [ ] `IntegerVariable(BaseModel)`: name, lower, upper — integer casting
- [ ] `CategoricalVariable(BaseModel)`: name, choices: list — non-empty
- [ ] `SearchSpace(BaseModel)`: variables, `dimensions` property = len(variables)
- [ ] `validate_solution(solution: dict, space: SearchSpace) -> bool` using NumPy broadcast
- [ ] JSON-serializable (Pydantic v2 `model_dump_json()`)

## References
`data-format.md` §2.1, REF-TASK-0022
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-004] Algorithm Interface: base.py, ABC, ask-tell, reset()",
        "labels": ["implementation", "algorithms", "interface"],
        "body": """
## Why This Task
A combined step() method — propose and evaluate in a single call — makes parallel evaluation structurally impossible. The ask-tell split is the architectural prerequisite for any form of async or distributed HPO. Without it, the Algorithm interface constrains the system to serial execution permanently.

## Summary
Implement the Algorithm Interface as defined in `interface-contracts.md` §2.

## Files to Create
- `corvus_corone/algorithms/base.py`
- `tests/test_algorithm_interface.py`

## Implementation Requirements
- [ ] `Algorithm` ABC with `@abstractmethod`: `suggest(context)`, `observe(solution, result)`, `reset(seed)`
- [ ] `AlgorithmInstanceRecord` Pydantic model: id (UUID), name, algorithm_family, hyperparameters, configuration_justification, framework, framework_version
- [ ] `metadata` property `@abstractmethod` → returns `AlgorithmInstanceRecord`
- [ ] `RunContext` dataclass: `remaining_budget: int`, `elapsed_evaluations: int`

## References
`interface-contracts.md` §2, MANIFESTO Principle 8
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-005] Algorithm Registry + RandomSearch built-in",
        "labels": ["implementation", "algorithms"],
        "body": """
## Why This Task
The Algorithm Registry mirrors the Problem Repository pattern but for algorithm implementations. RandomSearch is the built-in baseline required by MANIFESTO — every study needs a reference algorithm that makes no assumptions about the problem. Without RandomSearch, there is no baseline to compare against.

## Summary
Implement the Algorithm Registry (mirror of Problem Repository pattern) and provide RandomSearch as the first built-in algorithm.

## Files to Create
- `corvus_corone/algorithms/registry.py`
- `corvus_corone/algorithms/random_search.py`
- `tests/test_algorithm_registry.py`

## Implementation Requirements
- [ ] `AlgorithmRegistry` — identical pattern to `ProblemRepository`
- [ ] `RandomSearch(Algorithm)` using `numpy.random.default_rng(seed)` (not `random.Random`)
- [ ] `RandomSearch.metadata` returns complete `AlgorithmInstanceRecord`
- [ ] `configuration_justification` field populated for RandomSearch

## References
MANIFESTO Principles 8, 10
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-006] Optuna TPE adapter: adapters/optuna_adapter.py",
        "labels": ["implementation", "algorithms", "optuna"],
        "body": """
## Why This Task
Optuna TPE is the most common algorithm researchers will want to contribute. If wrapping it requires more than 15 lines, the Algorithm interface has too much surface area. This implementation serves two purposes: a useful adapter, and a proof that the interface design is minimal enough for third parties.

## Summary
Wrap Optuna TPE sampler in the Algorithm interface. Must require ≤15 lines of code per REF-TASK-0004 acceptance criteria.

## Files to Create
- `corvus_corone/algorithms/adapters/optuna_adapter.py`
- `docs/06_tutorials/01_wrap_optuna_sampler.md`
- `tests/test_optuna_adapter.py`

## Implementation Requirements
- [ ] `OptunaTPEAdapter(Algorithm)` — reset(), suggest(), observe()
- [ ] Uses Optuna ask-tell API (`study.ask()` / `study.tell()`)
- [ ] `@algorithm_registry.register("optuna_tpe_default")` with complete metadata
- [ ] Wrapper ≤ 15 lines of substantive code (excluding metadata boilerplate)
- [ ] Tutorial in `docs/06_tutorials/01_wrap_optuna_sampler.md`

## References
REF-TASK-0004
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-007] Experiment Runner: runner.py, deepcopy isolation, SeedSequence",
        "labels": ["implementation", "runner"],
        "body": """
## Why This Task
Reproducibility of results depends entirely on the Runner injecting seeds and isolating state between runs. If the Runner shares a mutable algorithm instance across runs, or allows the algorithm to choose its own seed, results are not reproducible. This is the module that makes MANIFESTO Principle 18 enforceable.

## Summary
Implement the Experiment Runner ensuring MANIFESTO Principle 18: each Run is independent and deterministic given the same seed.

## Files to Create
- `corvus_corone/runner/runner.py`
- `tests/test_runner.py`

## Implementation Requirements
- [ ] `ExperimentRunner.run_single(problem_cls, algorithm, seed, budget)` → `list[EvaluationResult]`
- [ ] `deepcopy(algorithm)` before each run — no shared mutable state
- [ ] Fresh `problem_cls()` instance per run
- [ ] Seed injected via `problem.reset(seed)` and `algorithm.reset(seed)` — never self-selected
- [ ] `test_identical_seed_gives_identical_results()` — determinism test
- [ ] `test_different_seeds_give_different_results()` — independence test

## References
`interface-contracts.md` §3, MANIFESTO Principle 18
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-008] Seed Manager: seed_manager.py, SeedSequence, generate_seeds()",
        "labels": ["implementation", "runner"],
        "body": """
## Why This Task
Simple integer seeds (1, 2, 3) can be statistically correlated in some pseudo-random number generators. SeedSequence uses hash-based derivation to guarantee statistical independence between child seeds. Without this, the independence assumption underlying repeated-measures statistical tests is violated.

## Summary
Implement statistically independent seed generation using `numpy.random.SeedSequence`.

## Files to Create
- `corvus_corone/runner/seed_manager.py`
- `tests/test_seed_manager.py`

## Implementation Requirements
- [ ] `generate_seeds(n: int, master_seed: int) -> list[int]` using `SeedSequence.spawn(n)`
- [ ] Seeds are statistically independent (not simply `range(n)`)
- [ ] Deterministic: same master_seed always produces same child seeds
- [ ] `test_seeds_are_reproducible()` — same master → same list
- [ ] `test_seeds_are_independent()` — no correlation between adjacent seeds

## References
MANIFESTO Principle 18
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-009] Data entities: entities.py — RunRecord, PerformanceRecord, StudyRecord",
        "labels": ["implementation", "storage"],
        "body": """
## Why This Task
All downstream modules — Runner, Repository, Analysis — depend on entity schemas existing. Without UUID-keyed, JSON-serializable entities defined upfront, each module invents its own representation and the system cannot store or retrieve results consistently. ADR-001 requires server-compatible schemas from V1 — these entities fulfill that constraint.

## Summary
Implement all data entities as defined in `data-format.md` §2. All entities must be server-compatible (UUID IDs, JSON-serializable, no file-path references) per ADR-001.

## Files to Create
- `corvus_corone/storage/entities.py`
- `tests/test_entities.py`

## Implementation Requirements
- [ ] `RunRecord(BaseModel)`: id (UUID), study_id (UUID), problem_id (str), algorithm_id (str), seed (int), repetition (int), status (str)
- [ ] `PerformanceRecord(BaseModel)`: id (UUID), run_id (UUID), evaluation_number (int), objective_value (float)
- [ ] `StudyRecord(BaseModel)`: id (UUID), research_question (str), problem_ids (list[str]), algorithm_ids (list[str]), master_seed (int)
- [ ] `model_dump_json()` round-trips correctly for all entities
- [ ] UUIDs serialize as strings in JSON
- [ ] `test_round_trip_json()` for each entity type

## References
`data-format.md` §2, ADR-001
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-010] Repository interface + LocalFileRepository + contract tests",
        "labels": ["implementation", "storage", "interface"],
        "body": """
## Why This Task
The Repository interface is what makes LocalFileRepository (V1) and ServerRepository (V2) interchangeable. Without the abstract base and contract tests, the ExperimentRunner is implicitly coupled to the file system. The contract test is the only mechanism that verifies the abstraction is real before V2 is built.

## Summary
Implement the Repository abstraction (REF-TASK-0023) enabling V1→V2 swap without code changes.

## Files to Create
- `corvus_corone/storage/repository.py`
- `tests/test_repository_contract.py`

## Implementation Requirements
- [ ] `Repository(ABC)` with abstract methods: `save_run`, `get_run`, `save_performance_records`, `get_performance_records`, `list_runs`, `list_studies`
- [ ] `LocalFileRepository(Repository)` — JSON files under `base_path/runs/{id}.json`
- [ ] No code outside Repository implementations calls file I/O directly
- [ ] `RepositoryContractTest` — parameterized test suite that any implementation must pass
- [ ] `test_save_and_retrieve_run()` — round-trip identity
- [ ] `test_swap_repository_requires_zero_changes_to_runner()` — integration test

## References
REF-TASK-0023, ADR-001
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-011] Metric taxonomy: metrics.py — QUALITY, TIME, RELIABILITY",
        "labels": ["implementation", "analysis", "metrics"],
        "body": """
## Why This Task
Metrics are the primary output of a benchmarking study. Without this module, no analysis is possible. Metric IDs are permanent public identifiers — once a study is published referencing QUALITY-BEST_VALUE_AT_BUDGET, that identifier cannot change. Getting the IDs right here prevents a breaking change that affects all published studies.

## Summary
Implement all metrics defined in `metric-taxonomy.md` §2 using the `@metric` decorator registry.

## Files to Create
- `corvus_corone/analysis/metrics.py`
- `tests/test_metrics.py`

## Implementation Requirements
- [ ] `METRIC_REGISTRY: dict[str, callable]` and `@metric(metric_id)` decorator
- [ ] `QUALITY-BEST_VALUE_AT_BUDGET`: `min(objective_values)` using NumPy
- [ ] `TIME-EVALUATIONS_TO_TARGET`: first k where f(x_k) ≤ τ, returns B+1 if not reached
- [ ] `RELIABILITY-SUCCESS_RATE`: fraction of runs achieving target
- [ ] All metric IDs match `metric-taxonomy.md` exactly (permanent identifiers)
- [ ] Tests use known input/output values from `metric-taxonomy.md` examples
- [ ] REF-TASK-0015 fulfilled: implementation references added to `metric-taxonomy.md`

## References
`metric-taxonomy.md` §2, REF-TASK-0015, REF-TASK-0016, REF-TASK-0017
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-012] Statistical analysis: statistical.py — three-level analysis",
        "labels": ["implementation", "analysis", "statistics"],
        "body": """
## Why This Task
MANIFESTO Principle 13 requires three-level analysis: exploratory, confirmatory, and practical significance. Without this module, the system produces raw performance data but no statistical interpretation. The t-test is wrong for HPO results (non-normal distribution) — this module enforces the correct tests by making them the only available option.

## Summary
Implement three-level statistical analysis per MANIFESTO Principle 13: exploratory, confirmatory (Wilcoxon/Kruskal-Wallis + Holm-Bonferroni), practical (Cliff's delta).

## Files to Create
- `corvus_corone/analysis/statistical.py`
- `tests/test_statistical.py`

## Implementation Requirements
- [ ] `exploratory_summary(values)` → median, Q25, Q75, min, max, n
- [ ] `confirmatory_wilcoxon(a, b)` using `scipy.stats.wilcoxon`
- [ ] `confirmatory_kruskal(groups)` using `scipy.stats.kruskal` for >2 algorithms
- [ ] `holm_bonferroni_pairwise(groups)` — pairwise with Holm correction
- [ ] `cliffs_delta(a, b) → float` — range [-1, 1]
- [ ] `interpret_cliffs_delta(d)` → negligible/small/medium/large
- [ ] `ThreeLevelAnalysis.analyze()` — refuses to return without all three levels
- [ ] Every report includes `scope_statement` (MANIFESTO Principle 3)
- [ ] REF-TASK-0020 fulfilled: decision tree documented in `statistical-methodology.md` §3

## References
REF-TASK-0020, MANIFESTO Principles 13, 15
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-013] Anytime performance: anytime.py — ECDF, best-so-far curves",
        "labels": ["implementation", "analysis"],
        "body": """
## Why This Task
QUALITY-BEST_VALUE_AT_BUDGET captures the endpoint. ECDF captures the trajectory. Without anytime performance metrics, two algorithms that reach the same final quality — one converging in 10 evaluations and one in 99 — are indistinguishable. MANIFESTO Principle 14 requires anytime analysis; this module fulfills it.

## Summary
Implement anytime performance metrics and ECDF computation per MANIFESTO Principle 14 and REF-TASK-0016.

## Files to Create
- `corvus_corone/analysis/anytime.py`
- `tests/test_anytime.py`

## Implementation Requirements
- [ ] `compute_anytime_curve(runs, minimize)` → (budget_points, median_curve) using `np.minimum.accumulate`
- [ ] `compute_ecdf(values_at_budget, targets)` → (targets, ecdf_values)
- [ ] `compute_ecdf_area(runs, n_targets, normalization='empirical')` per ADR-003
- [ ] Normalization strategy: empirical min/max (ADR-003)
- [ ] REF-TASK-0016 fulfilled: normalization procedure documented in `metric-taxonomy.md`
- [ ] Basic IOHprofiler `.dat` export in `bridge/iohprofiler.py` (full spec in IMPL-023)

## References
REF-TASK-0016, MANIFESTO Principle 14
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-014] Reporting Engine: reports.py — multi-audience, Jinja2, scope enforcement",
        "labels": ["implementation", "reporting"],
        "body": """
## Why This Task
Reports without a scope_statement can be read as universal claims. MANIFESTO Principle 3 requires conclusions scoped to tested instances — enforced here by making scope_statement a required field that raises ValueError when absent. Without this module, the system produces data but no interpretation, and the interpretation can be dangerously broad.

## Summary
Implement multi-audience report generation per MANIFESTO Principles 23–25. Every report must contain `scope_statement` and `limitations` — absent fields raise `ValueError`.

## Files to Create
- `corvus_corone/reporting/reports.py`
- `corvus_corone/reporting/templates/researcher_report.md.j2`
- `corvus_corone/reporting/templates/practitioner_summary.md.j2`
- `tests/test_reports.py`

## Implementation Requirements
- [ ] `StudyReport` dataclass with required `scope_statement` and `limitations` fields
- [ ] `generate_researcher_report(report)` — raises `ValueError` if scope_statement empty
- [ ] `generate_practitioner_summary(report)` — explicit "not a universal ranking" statement
- [ ] Jinja2 templates for both report types
- [ ] `ReportingEngine.generate(study_id, format, output)` — public interface
- [ ] `test_missing_scope_statement_raises()`
- [ ] REF-TASK-0019 fulfilled: mandatory visualizations list in `statistical-methodology.md` §2

## References
REF-TASK-0019, MANIFESTO Principles 24, 25
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-015] Visualizations: visualizations.py — boxplot, convergence, ECDF",
        "labels": ["implementation", "reporting", "visualization"],
        "body": """
## Why This Task
Visualizations are the primary communication layer between statistical results and human understanding. Without mandatory plots — boxplot, convergence curves, ECDF — report completeness cannot be verified automatically. The step() vs plot() distinction is not cosmetic: linear interpolation of an ECDF is mathematically wrong.

## Summary
Implement mandatory Level 1 visualizations per REF-TASK-0019 and `statistical-methodology.md` §2.

## Files to Create
- `corvus_corone/reporting/visualizations.py`
- `tests/test_visualizations.py`

## Implementation Requirements
- [ ] `plot_boxplot_comparison(results, title)` — VIZ-L1-01: per-algorithm boxplot
- [ ] `plot_anytime_curves(algorithms, title)` — VIZ-L1-02: median convergence curves
- [ ] `plot_ecdf(algorithms)` — VIZ-L1-03: **must use `plt.step(where='post')`** (ECDF is step function)
- [ ] `plot_violin_comparison(results)` — VIZ-L1-04: optional when n_runs > 50
- [ ] All plots: `dpi=150`, `bbox_inches='tight'`, publication-ready
- [ ] `ReportingEngine` auto-generates VIZ-L1-01..03 for every report

## References
REF-TASK-0019
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-016] Study Orchestrator: orchestrator.py — Facade pattern",
        "labels": ["implementation", "orchestrator"],
        "body": """
## Why This Task
The Orchestrator is the module that makes corvus_corone usable without understanding its internals. Without it, a researcher must manually instantiate and coordinate eight modules in the correct order. MANIFESTO Principle 16 (planning before execution) is enforced here — StudyConfig must be complete before any run starts.

## Summary
Implement the Study Orchestrator as Facade over ProblemRepository, AlgorithmRegistry, ExperimentRunner, Repository, ThreeLevelAnalysis, and ReportingEngine.

## Files to Create
- `corvus_corone/orchestrator.py`
- `tests/test_orchestrator.py`

## Implementation Requirements
- [ ] `StudyConfig` dataclass: research_question, problem_ids, algorithm_ids, repetitions, budget_per_run, master_seed
- [ ] `StudyOrchestrator.run(config) → StudyReport`
- [ ] Validates StudyConfig before execution (MANIFESTO Principle 16)
- [ ] Calls `validate_problem_diversity()` — warns if < 5 problems (REF-TASK-0021)
- [ ] Generates seeds via `SeedSequence` (IMPL-008)
- [ ] Delegates to all modules — zero business logic in Orchestrator itself
- [ ] Integration test: end-to-end with SphereProblem + RandomSearch

## References
REF-TASK-0021, MANIFESTO Principle 16
""",
    },
    {
        "milestone": "IMPL Phase 1 — corvus_corone Library (weeks 1–16)",
        "title": "[IMPL-017] Public API + CLI: api.py, cli.py (Click)",
        "labels": ["implementation", "api"],
        "body": """
## Why This Task
The Public API and CLI are the only interfaces most users will ever interact with. Without them, corvus_corone is a collection of modules requiring implementation knowledge to use. The CLI also serves as an integration test: if `corvus run` works end-to-end, the module coordination is correct.

## Summary
Implement the public API one-liner entry point and Click CLI per REF-TASK-0004 and MANIFESTO Principle 28.

## Files to Create
- `corvus_corone/api.py`
- `corvus_corone/cli.py`
- `tests/test_cli.py`

## Implementation Requirements
- [ ] `create_study(research_question, problem_ids, algorithm_ids, ...) → StudyOrchestrator`
- [ ] `@click.group()` with subcommand `run`
- [ ] `corvus run --problems sphere_2d --algorithms tpe_default --repetitions 30`
- [ ] `corvus list-problems` and `corvus list-algorithms`
- [ ] CLI testable via `click.testing.CliRunner`
- [ ] Contract tests: all implementations of `Repository`, `Problem`, `Algorithm` must pass

## References
REF-TASK-0004, NFR-MODULAR-01
""",
    },

    # ── Phase 2: Repo Closure ─────────────────────────────────────────────
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-018] ADR-002: Technical constraints (Python >=3.10, MIT, pyproject.toml)",
        "labels": ["implementation", "adr", "infrastructure"],
        "body": """
## Why This Task
Python version, OS support, and licensing constraints affect every contributor and CI configuration. Without ADR-002, these constraints exist as implicit knowledge. The pyproject.toml implementation fulfills the constraint; the ADR records why the specific choices were made so they are not relitigated.

## Summary
Write ADR-002 and implement its decisions: finalize `pyproject.toml` with correct Python version constraint, license, and dependency restrictions.

## Files to Create/Update
- `docs/02_design/02_architecture/adr/ADR-002-technical-constraints.md`
- `corvus_corone/pyproject.toml` (update with final constraints)

## Implementation Requirements
- [ ] ADR-002 written: Context → Decision → Consequences format
- [ ] Python: `requires-python = ">=3.10"`
- [ ] License: `license = {text = "MIT"}`
- [ ] Optional extras: `[project.optional-dependencies]` for `optuna`, `rag`, `all`
- [ ] CI license check job: verifies no GPL dependencies
- [ ] REF-TASK-0011 fulfilled

## References
REF-TASK-0011
""",
    },
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-019] ADR-003 + ADR-004: ECDF_AREA normalization + Standard Reporting Set",
        "labels": ["implementation", "adr", "methodology"],
        "body": """
## Why This Task
ECDF_AREA values from different studies are not comparable without a documented normalization strategy. ADR-003 makes this explicit: empirical normalization chosen for V1, with known limitations documented. Without the ADR, researchers may compare ECDF_AREA values across studies and draw invalid conclusions.

## Summary
Write ADR-003 (empirical normalization for ECDF_AREA) and ADR-004 (Standard Reporting Set definition). Update `metric-taxonomy.md` accordingly.

## Files to Create/Update
- `docs/02_design/02_architecture/adr/ADR-003-ecdf-normalization.md`
- `docs/02_design/02_architecture/adr/ADR-004-standard-reporting-set.md`
- `docs/03_technical_contracts/metric-taxonomy.md` §3 (Standard Reporting Set)

## Implementation Requirements
- [ ] ADR-003: empirical normalization chosen, limitations documented
- [ ] ADR-004: Standard Reporting Set = {QUALITY-BEST_VALUE_AT_BUDGET, ANYTIME-ECDF_AREA, RELIABILITY-SUCCESS_RATE}
- [ ] `metric-taxonomy.md` §3 updated with Standard Reporting Set
- [ ] `anytime.py` `compute_ecdf_area()` uses ADR-003 normalization
- [ ] REF-TASK-0016 and REF-TASK-0017 fulfilled

## References
REF-TASK-0016, REF-TASK-0017
""",
    },
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-020] ADR-005 + statistical-methodology.md: diversity requirements + test decision tree",
        "labels": ["implementation", "adr", "methodology"],
        "body": """
## Why This Task
Without documented minimum diversity requirements, a researcher can run a study on a single problem instance and draw conclusions that MANIFESTO Principle 3 explicitly prohibits. ADR-005 makes the minimum requirements machine-verifiable — the Orchestrator checks before execution, not after.

## Summary
Write ADR-005 (minimum problem diversity) and fill `statistical-methodology.md` §2 (Level 1 visualizations) and §3 (test selection decision tree).

## Files to Create/Update
- `docs/02_design/02_architecture/adr/ADR-005-problem-diversity-requirements.md`
- `docs/04_scientific_practice/methodology/statistical-methodology.md` §2 and §3

## Implementation Requirements
- [ ] ADR-005: minimum 5 problems, coverage of ≥2 dimensionality ranges
- [ ] `statistical-methodology.md` §2: mandatory VIZ-L1-01..03, optional VIZ-L1-04
- [ ] `statistical-methodology.md` §3: decision tree (2 algs → Wilcoxon, >2 → Kruskal + Holm-Bonferroni)
- [ ] `orchestrator.py` `validate_problem_diversity()` enforces ADR-005
- [ ] REF-TASK-0019, REF-TASK-0020, REF-TASK-0021 fulfilled

## References
REF-TASK-0019, REF-TASK-0020, REF-TASK-0021
""",
    },
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-021] Sensitivity documentation: entities.py SensitivityReport + contribution-guide update",
        "labels": ["implementation", "methodology", "data-format"],
        "body": """
## Why This Task
MANIFESTO Principle 11 requires sensitivity documentation for every algorithm contribution. Without SensitivityReport in the schema, the requirement exists in text but is unenforceable. The Pydantic field makes presence checkable by CI; the contribution-guide update makes the expectation explicit to contributors.

## Summary
Add `SensitivityReport` to Algorithm Instance schema and enforce it in contribution review.

## Files to Create/Update
- `corvus_corone/storage/entities.py` (add `SensitivityReport`, update `AlgorithmInstanceRecord`)
- `docs/03_technical_contracts/data-format.md` §2.2
- `docs/05_community/contribution-guide.md` §2

## Implementation Requirements
- [ ] `SensitivityReport(BaseModel)`: tested_on_problems, budget_used, repetitions_per_config (min 10), parameters, overall_stability, notes
- [ ] `ParameterSensitivity(BaseModel)`: parameter_name, tested_values, metric_mean, metric_std, conclusion
- [ ] `AlgorithmInstanceRecord.sensitivity_report: Optional[SensitivityReport]`
- [ ] `contribution-guide.md` §2 adds sensitivity_report as review criterion
- [ ] REF-TASK-0022 fulfilled

## References
REF-TASK-0022
""",
    },
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-022] Bulk PerformanceRecord storage: Parquet/HDF5 after spike (ADR-006)",
        "labels": ["implementation", "storage", "spike"],
        "body": """
## Why This Task
JSON at 150k records per study is too slow for the analytical queries that ThreeLevelAnalysis runs. Without a bulk storage format, analysis time scales linearly with study size. The spike (REF-TASK-0024) determines which format wins on real data; this task implements that decision.

## Summary
After running the spike (REF-TASK-0024), implement the chosen bulk storage format in `LocalFileRepository`.

## Blocked By
[SPIKE → REF-TASK-0024] must be completed first. The spike determines Parquet vs HDF5 — do not implement until ADR-006 is written.

## ⚠️ Depends on spike result
Run the spike notebook first: `notebooks/spike_bulk_storage.ipynb`

## Files to Create/Update
- `docs/02_design/02_architecture/adr/ADR-006-bulk-storage-format.md`
- `corvus_corone/storage/repository.py` (add `save_bulk_records`, `get_performance_records_bulk`)
- `docs/03_technical_contracts/data-format.md` §3

## Implementation Requirements
- [ ] ADR-006 written with benchmark numbers from spike
- [ ] `LocalFileRepository.save_bulk_records(run_id, records)` — writes in chosen format
- [ ] Primary schema still JSON (ADR-001 constraint)
- [ ] Round-trip test: bulk records produce identical analysis to JSON records
- [ ] REF-TASK-0024 fulfilled

## References
REF-TASK-0024, ADR-001
""",
    },
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-023] IOHprofiler bridge: full .dat export + round-trip test",
        "labels": ["implementation", "bridge", "iohprofiler"],
        "body": """
## Why This Task
IOHprofiler is the standard visualization tool for ECDF-based anytime performance analysis. Without this bridge, researchers who want to use IOHanalyzer must convert results manually. MANIFESTO Principle 26 requires interoperability with the ecosystem — this task fulfills it for the most analytically relevant tool.

## Summary
Implement the complete IOHprofiler export bridge with sidecar `.meta.json` and round-trip acceptance test. REF-TASK-0007 fulfilment.

## Files to Create/Update
- `corvus_corone/bridge/iohprofiler.py`
- `docs/03_technical_contracts/data-format.md` §3 (IOHprofiler mapping)
- `tests/test_iohprofiler_export.py`

## Implementation Requirements
- [ ] `IOHprofilerExporter.export_run(run, records, output_path)` — writes `.dat` + `.meta.json`
- [ ] `IOHprofilerExporter.export_study(study_id, repo, output_dir)` — directory structure
- [ ] Header format: `funcId X, funcName Y, DIM Z, maximization F`
- [ ] Sidecar `.meta.json` stores seed, run_id, wall_time (fields not in `.dat`)
- [ ] Round-trip test: exported `.dat` passes format validation (header check)
- [ ] `data-format.md` §3 IOHprofiler mapping table complete
- [ ] REF-TASK-0007 fulfilled

## References
REF-TASK-0007
""",
    },
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-024] COCO bridge: coco_exporter.py after spike (REF-TASK-0005)",
        "labels": ["implementation", "bridge", "coco", "spike"],
        "body": """
## Why This Task
COCO is the standard benchmark framework for continuous optimization. Without this bridge, corvus_corone results cannot be compared against the existing COCO literature. The spike revealed a continuous-only limitation — this implementation documents and enforces that constraint explicitly rather than failing silently.

## Summary
After running the COCO spike (REF-TASK-0005), implement the COCO export bridge.

## ⚠️ Depends on spike result
Run the spike notebook first: `notebooks/spike_coco_format.ipynb`

## Files to Create/Update
- `corvus_corone/bridge/coco_exporter.py`
- `docs/03_technical_contracts/data-format.md` §3 (COCO mapping)
- `tests/test_coco_export.py`

## Known Limitation (from spike)
COCO only supports continuous search spaces. Problems with categorical/integer variables will be excluded from export with a warning.

## Implementation Requirements
- [ ] `COCOExporter.export_study(study_id, repo, output_dir)`
- [ ] Mapping table in `data-format.md` §3 with documented data loss
- [ ] Continuous-only check with clear warning message
- [ ] REF-TASK-0005 fulfilled

## References
REF-TASK-0005

## Blocked By
[SPIKE → REF-TASK-0005] must be completed first. The spike defines the COCO mapping table — implementation follows from documented mapping, not speculation.""",
    },
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-025] Nevergrad adapter: adapters/nevergrad_adapter.py after spike (REF-TASK-0006)",
        "labels": ["implementation", "algorithms", "nevergrad", "spike"],
        "body": """
## Why This Task
Nevergrad provides 100+ algorithm implementations that Algorithm Authors want to contribute. Without the generic adapter, each Nevergrad algorithm requires a custom wrapper. The spike confirmed that ng.p.Dict maps cleanly to SearchSpace — this implementation makes the contribution path as short as possible.

## Summary
After running the Nevergrad spike (REF-TASK-0006), implement the generic Nevergrad adapter.

## ⚠️ Depends on spike result
Run the spike notebook first: `notebooks/spike_nevergrad_api.ipynb`

## Files to Create/Update
- `corvus_corone/algorithms/adapters/nevergrad_adapter.py`
- `docs/06_tutorials/03_wrap_nevergrad_optimizer.md`
- `docs/03_technical_contracts/data-format.md` §3 (Nevergrad mapping)
- `tests/test_nevergrad_adapter.py`

## Implementation Requirements
- [ ] `NevergradAdapter(Algorithm)` — generic, wraps any Nevergrad optimizer
- [ ] SearchSpace → `ng.p.Dict` conversion
- [ ] Tested on: CMA-ES, NGOpt, DE
- [ ] Tutorial ≤ ~10 lines per optimizer
- [ ] REF-TASK-0006 fulfilled

## References
REF-TASK-0006

## Blocked By
[SPIKE → REF-TASK-0006] must be completed first. The spike defines ng.p.Dict → SearchSpace mapping and confirms the adapter pattern is feasible.""",
    },
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-026] LLM-as-judge: analysis/llm_judge.py — ManifestoReview",
        "labels": ["implementation", "analysis", "llm"],
        "body": """
## Why This Task
StudyConfig validation against 32 MANIFESTO principles cannot be fully encoded as deterministic rules — some principles are qualitative. LLM-as-judge fills the gap: structured output via Pydantic makes the review machine-readable, and the optional flag means researchers choose when to invoke it.

## Summary
Implement LLM-as-judge for study design validation against MANIFESTO principles. Uses Ollama locally with Pydantic structured output.

## Files to Create
- `corvus_corone/analysis/llm_judge.py`
- `tests/test_llm_judge.py`

## Implementation Requirements
- [ ] `ManifestoReview(BaseModel)`: overall_score (1-5), missing_research_question, insufficient_repetitions, no_scope_statement, concerns (list), suggestions (list)
- [ ] `StudyDesignJudge.review(config: StudyConfig) → ManifestoReview`
- [ ] Uses Ollama with `format="json"` and Pydantic schema
- [ ] `warn_or_block(review, strict=False)` — warns or raises based on score
- [ ] Integrated into `StudyOrchestrator` when `config.validate_with_llm=True`
- [ ] Optional dependency: only imports ollama if `corvus-corone[llm]` installed

## References
LLM block
""",
    },
    {
        "milestone": "IMPL Phase 2 — Repo Closure (weeks 17–30)",
        "title": "[IMPL-027] RAG on papers/: papers_rag.py — FAISS + Ollama + Bartz-Beielstein 2020",
        "labels": ["implementation", "analysis", "llm", "rag"],
        "body": """
## Why This Task
papers/ contains Bartz-Beielstein 2020 — the methodological foundation for metric-taxonomy.md and statistical-methodology.md. Without RAG over these papers, understanding why a specific metric formula exists requires reading 40 pages manually. The RAG module makes the source documentation queryable during development.

## Summary
Implement RAG over `papers/` to answer methodology questions during development. Developer tool — not end-user feature.

## Files to Create
- `corvus_corone/papers_rag.py`
- `tests/test_papers_rag.py`

## Implementation Requirements
- [ ] `build_index(papers_dir)` → (faiss.Index, chunks) — chunks papers by paragraph
- [ ] `ask_methodology(question, index, chunks, top_k=3)` → answer string via Ollama
- [ ] `PapersRAG.why(metric_id)` — "What is the scientific justification for {metric_id}?"
- [ ] Optional dependency: only active with `corvus-corone[rag]`
- [ ] Integration test: asks about TIME-EVALUATIONS_TO_TARGET, gets B+1 rationale

## References
LLM block
""",
    },

    # ── Phase 3a: Pilot V2 ─────────────────────────────────────────────────
    {
        "milestone": "IMPL Phase 3a — Pilot V2 Researcher (weeks 31–38)",
        "title": "[IMPL-028] Pilot setup: corvus_corone_pilot pyproject.toml, uv workspace root",
        "labels": ["implementation", "pilot-v2", "infrastructure"],
        "body": """
## Why This Task
corvus_corone_pilot depends on corvus_corone as a library. Without the uv workspace configuration, managing two packages in one repository requires manual dependency linking. The workspace root pyproject.toml makes this automatic — `uv sync` installs both packages with a single command.

## Summary
Add `corvus_corone_pilot` to the uv workspace and set up its pyproject.toml with agent dependencies.

## Files to Create/Update
- Root `pyproject.toml` — add `corvus_corone_pilot` to workspace members
- `corvus_corone_pilot/pyproject.toml` — langgraph, mcp, langchain-ollama, mlflow, xgboost, shap, dvc
- `corvus_corone_pilot/__init__.py`
- `corvus_corone_pilot/v2_researcher/__init__.py`
- `corvus_corone_pilot/v3_autonomous/__init__.py`

## Implementation Requirements
- [ ] `uv sync` installs both packages from root
- [ ] `corvus_corone_pilot` depends on `corvus-corone` (local workspace dependency)
- [ ] CI extended to include pilot tests
""",
    },
    {
        "milestone": "IMPL Phase 3a — Pilot V2 Researcher (weeks 31–38)",
        "title": "[IMPL-029] MCP Server: v2_researcher/mcp_server.py — exposes corvus_corone via MCP",
        "labels": ["implementation", "pilot-v2", "mcp"],
        "body": """
## Why This Task
LangGraph agents need to invoke corvus_corone tools without direct Python imports — direct imports couple the agent code to library internals. MCP provides a stable interface: tools are registered with docstrings, type-checked inputs, and versioned independently of the agent graph. The agent calls tools by name, not by function reference.

## Summary
Expose `corvus_corone` library tools via Model Context Protocol (MCP) so agents can invoke them without direct Python imports.

## Files to Create
- `corvus_corone_pilot/v2_researcher/mcp_server.py`
- `tests/test_mcp_server.py`

## Tools to Expose
- [ ] `run_study(research_question, problem_ids, algorithm_ids, repetitions)` → `{study_id, status}`
- [ ] `list_problems()` → `list[{id, description}]`
- [ ] `list_algorithms()` → `list[{id, family, assumptions}]`
- [ ] `get_study_results(study_id)` → study report dict
- [ ] `get_algorithm_properties(algorithm_id)` → metadata dict

## Implementation Requirements
- [ ] Uses `mcp.server.Server` and `@app.tool()` decorator
- [ ] Runs via stdio: `uv run python -m corvus_corone_pilot.v2_researcher.mcp_server`
- [ ] Each tool has docstring (used as MCP tool description)
""",
    },
    {
        "milestone": "IMPL Phase 3a — Pilot V2 Researcher (weeks 31–38)",
        "title": "[IMPL-030] ReAct agent demo: react_demo.py — tool calling loop without framework",
        "labels": ["implementation", "pilot-v2", "agent"],
        "body": """
## Why This Task
LangGraph abstracts the agentic loop behind graph primitives. Without implementing ReAct manually first, the abstractions are opaque — it is unclear what checkpointing, state management, and conditional edges replace. Implementing the raw loop in 30 lines makes LangGraph's value proposition concrete.

## Summary
Implement ReAct (Thought-Action-Observation) loop from scratch without LangGraph, to understand the foundation.

## Files to Create
- `corvus_corone_pilot/v2_researcher/agents/react_demo.py`
- `tests/test_react_demo.py`

## Implementation Requirements
- [ ] `react_agent(question, tools, max_steps=10)` → str
- [ ] Agentic loop: LLM response → check tool_calls → execute → add to messages → repeat
- [ ] Returns when no tool_calls in response
- [ ] `max_steps` circuit breaker prevents infinite loops
- [ ] Uses `ollama.chat()` with tools parameter
- [ ] Demo: answers "which algorithms are suitable for 5D continuous?" using `get_algorithm_properties`
""",
    },
    {
        "milestone": "IMPL Phase 3a — Pilot V2 Researcher (weeks 31–38)",
        "title": "[IMPL-031] LangGraph graph: graph.py — StateGraph, checkpointing, human-in-the-loop",
        "labels": ["implementation", "pilot-v2", "langgraph"],
        "body": """
## Why This Task
ReAct in a raw Python loop has no state persistence, no human interruption point, and no restart capability. Without LangGraph, a crashed agent loses all progress. `interrupt_before=['execute_study']` is a graph property — the human approval gate is structurally enforced, not conditionally coded.

## Summary
Implement the main LangGraph StateGraph for V2 with checkpointing and human-in-the-loop approval before `execute_study`.

## Files to Create
- `corvus_corone_pilot/v2_researcher/graph.py`
- `tests/test_graph.py`

## Implementation Requirements
- [ ] `StudyState(TypedDict)`: research_question, available_algorithms, selected_algorithms, selected_problems, study_id, analysis, messages
- [ ] Nodes: `plan_study`, `validate_plan`, `execute_study`, `analyze_results`
- [ ] `interrupt_before=["execute_study"]` — waits for human approval
- [ ] `MemorySaver()` checkpointing — resume by thread_id
- [ ] Conditional edge: retry plan if validation fails
- [ ] `graph.get_graph().draw_mermaid_png()` generates visualization
""",
    },
    {
        "milestone": "IMPL Phase 3a — Pilot V2 Researcher (weeks 31–38)",
        "title": "[IMPL-032] ML foundations: autograd.py — Value node, backpropagation from scratch",
        "labels": ["implementation", "pilot-v2", "ml-foundations"],
        "body": """
## Why This Task
Bayesian optimization uses gradient-based fitting of surrogate models. Without understanding automatic differentiation, the GP fitting procedure is a black box. The autograd implementation makes gradient accumulation, chain rule, and topological sort concrete — prerequisites for understanding why surrogate models converge.

## Summary
Implement automatic differentiation from scratch to understand gradient computation. Foundation for understanding surrogate models in HPO.

## Files to Create
- `corvus_corone_pilot/v2_researcher/ml_foundations/autograd.py`
- `tests/test_autograd.py`

## Implementation Requirements
- [ ] `Value` class: data, grad, _backward, _prev
- [ ] Operators: `__add__`, `__mul__`, `__sub__`, `__pow__`, `tanh()`
- [ ] `Value.backward()` — topological sort + reverse pass
- [ ] Gradient accumulation via `+=` (handles multi-use variables)
- [ ] `SimpleNN` class with NumPy — forward + backward manual
- [ ] Tests verify: `d(x*w)/dw == x`, `d(x*w)/dx == w`
""",
    },
    {
        "milestone": "IMPL Phase 3a — Pilot V2 Researcher (weeks 31–38)",
        "title": "[IMPL-033] ML foundations: surrogate.py — GaussianProcess + acquisition functions",
        "labels": ["implementation", "pilot-v2", "ml-foundations"],
        "body": """
## Why This Task
TPE and GP are both surrogate models, but they handle uncertainty differently. Without implementing GP from scratch, the distinction between "a prediction" and "a prediction with calibrated uncertainty" is abstract. The uncertainty estimate is what drives exploration in acquisition functions — the core mechanism of Bayesian HPO.

## Summary
Implement Gaussian Process regression and UCB acquisition function in NumPy to understand Bayesian optimization internals.

## Files to Create
- `corvus_corone_pilot/v2_researcher/ml_foundations/surrogate.py`
- `tests/test_surrogate.py`

## Implementation Requirements
- [ ] `GaussianProcess`: `rbf_kernel()`, `fit()`, `predict()` → (mean, std)
- [ ] RBF kernel: `exp(-dist²/2l²)`
- [ ] `ucb_acquisition(X, surrogate, kappa=2.0)` — exploitation/exploration balance
- [ ] Mini Bayesian optimization loop (5 iterations) in tests
- [ ] Visualization: GP fit with uncertainty bands
""",
    },
    {
        "milestone": "IMPL Phase 3a — Pilot V2 Researcher (weeks 31–38)",
        "title": "[IMPL-034] Multi-agent: Planner + Executor + Analyst with LangGraph supervisor",
        "labels": ["implementation", "pilot-v2", "agent", "multi-agent"],
        "body": """
## Why This Task
A single agent that plans, executes, and analyzes is hard to test and hard to debug — a failure at any stage implicates everything. Splitting responsibilities into Planner, Executor, and Analyst means each can be tested with a hand-crafted state dict. The supervisor routing makes the control flow explicit and inspectable.

## Summary
Implement three specialized agents (Planner, Executor, Analyst) orchestrated by a LangGraph supervisor routing over shared state.

## Files to Create
- `corvus_corone_pilot/v2_researcher/agents/planner.py`
- `corvus_corone_pilot/v2_researcher/agents/executor.py`
- `corvus_corone_pilot/v2_researcher/agents/analyst.py`
- Updated `corvus_corone_pilot/v2_researcher/graph.py`

## Implementation Requirements
- [ ] `supervisor(state)` → str: routes to planner/executor/analyst/END
- [ ] `planner_agent`: ReAct loop with `list_algorithms` + `get_algorithm_properties` tools
- [ ] `executor_agent`: calls `corvus_corone` via MCP, respects `interrupt_before`
- [ ] `analyst_agent`: uses `corvus_corone.analysis.ThreeLevelAnalysis`
- [ ] All agents write to shared `StudyState`, no direct inter-agent calls
- [ ] Integration test: full pipeline from research_question to analysis
""",
    },
    {
        "milestone": "IMPL Phase 3a — Pilot V2 Researcher (weeks 31–38)",
        "title": "[IMPL-035] ML foundations: predictor.py — XGBoost + SHAP for HPO performance prediction",
        "labels": ["implementation", "pilot-v2", "ml-foundations"],
        "body": """
## Why This Task
The Planner agent recommends algorithms based on algorithm metadata (documentation). SHAP on XGBoost trained from actual study results provides empirical evidence. Without the predictor, recommendations are based on design assumptions; with it, recommendations reflect observed performance patterns across the history of studies.

## Summary
Train XGBoost on Corvus study results to predict algorithm performance, with SHAP explanations for interpretability.

## Files to Create
- `corvus_corone_pilot/v2_researcher/ml_foundations/predictor.py`
- `corvus_corone_pilot/v2_researcher/ml_foundations/gradient_boosting.py` (from scratch)
- `tests/test_predictor.py`

## Implementation Requirements
- [ ] `GradientBoosting` from scratch: `DecisionStump`, sequential residual fitting
- [ ] `CalibratedPredictor`: XGBoost + isotonic regression calibration
- [ ] Features: problem_dim, budget, noise_level, alg_family_encoded
- [ ] Target: QUALITY-BEST_VALUE_AT_BUDGET
- [ ] SHAP explanations: `shap.TreeExplainer` for feature importance
- [ ] `predict_with_confidence()` → (prediction, confidence, status)
- [ ] Returns `None` when confidence < 0.6 → triggers new study instead of guessing
""",
    },
    {
        "milestone": "IMPL Phase 3a — Pilot V2 Researcher (weeks 31–38)",
        "title": "[IMPL-036] V2 finalization: CLI + MLflow tracking + agent memory",
        "labels": ["implementation", "pilot-v2", "mlflow"],
        "body": """
## Why This Task
V2 without CLI and tracking is a library, not a tool. The CLI makes V2 invocable from a terminal without writing Python. MLflow tracking makes every agent session reproducible: what question was asked, which algorithms were selected, which study ran, what the results were. Without tracking, the agent's reasoning is ephemeral.

## Summary
Finalize V2 with Click CLI, MLflow experiment tracking, and LangGraph thread-based session memory.

## Files to Create
- `corvus_corone_pilot/v2_researcher/cli.py`
- `corvus_corone_pilot/v2_researcher/tracking.py`

## Implementation Requirements
- [ ] `corvus-pilot run -q "..." [--auto-approve] [--thread-id default]`
- [ ] MLflow: log each agent run as experiment — parameters, metrics, artifacts
- [ ] Thread-based memory: same `thread_id` resumes previous session
- [ ] `corvus-pilot history` — list past sessions from MLflow
- [ ] `uv run corvus-pilot run -q "Does TPE outperform CMA-ES on 5D problems?"` works end-to-end
""",
    },

    # ── Phase 3b: Pilot V3 ─────────────────────────────────────────────────
    {
        "milestone": "IMPL Phase 3b — Pilot V3 Autonomous (weeks 39–46)",
        "title": "[IMPL-037] Hypothesis generator: hypothesis_gen.py + LongTermMemory",
        "labels": ["implementation", "pilot-v3", "agent"],
        "body": """
## Why This Task
V3 autonomous operation requires a basis for generating research questions that are both grounded in existing data and not already answered. Long-term memory provides that basis: patterns from past studies surface what is known and what remains uncertain. Without hypothesis generation grounded in memory, V3 cannot prioritize which questions to investigate.

## Summary
Implement autonomous hypothesis generation from patterns in long-term memory (all past Corvus studies).

## Files to Create
- `corvus_corone_pilot/v3_autonomous/hypothesis_gen.py`
- `corvus_corone_pilot/v3_autonomous/memory/long_term_memory.py`

## Implementation Requirements
- [ ] `Hypothesis(BaseModel)`: statement, motivation, testable_prediction, required_study (dict), confidence (float 0-1)
- [ ] `LongTermMemory(Repository)`: reads all studies, extracts performance patterns
- [ ] `generate_hypothesis(memory, llm) → Hypothesis` with structured JSON output
- [ ] Hypothesis must be falsifiable: `testable_prediction` and `required_study` non-empty
- [ ] `V3 read-only access` to existing studies (cannot overwrite past results)
""",
    },
    {
        "milestone": "IMPL Phase 3b — Pilot V3 Autonomous (weeks 39–46)",
        "title": "[IMPL-038] Meta-analyst: meta_analyst.py — cross-study Cliff's delta aggregation",
        "labels": ["implementation", "pilot-v3", "analysis"],
        "body": """
## Why This Task
A single study's Cliff's delta is subject to sampling variation. Meta-analysis across studies produces a pooled estimate with a confidence interval — the difference between "A beat B in one study" and "A consistently beats B across contexts." Without meta-analysis, V3 cannot distinguish reliable findings from noise.

## Summary
Implement meta-analysis aggregating algorithm performance across multiple studies using weighted Cliff's delta (fixed effects model).

## Files to Create
- `corvus_corone_pilot/v3_autonomous/meta_analyst.py`
- `tests/test_meta_analyst.py`

## Implementation Requirements
- [ ] `meta_analyze_algorithm_performance(algorithm_id, studies)` → pooled Cliff's delta + 95% CI
- [ ] Inverse-variance weighting: weights = 1/SE²
- [ ] Uses `corvus_corone.analysis.statistical.cliffs_delta`
- [ ] Returns: pooled_cliff_delta, 95ci_lower, 95ci_upper, n_studies, interpretation
- [ ] Tests with synthetic multi-study data where true effect is known
""",
    },
    {
        "milestone": "IMPL Phase 3b — Pilot V3 Autonomous (weeks 39–46)",
        "title": "[IMPL-039] Safety module: safety.py — action guards, loop detection, prompt injection",
        "labels": ["implementation", "pilot-v3", "security"],
        "body": """
## Why This Task
An autonomous system with write access to the study database and no execution limits is a liability. Without safety guards, a prompt injection through a problem name, a misbehaving hypothesis generator, or a loop in the agent graph can trigger unbounded computation or data corruption. Safety must be structural — enforced by the architecture, not by convention.

## Summary
Implement safety mechanisms for the autonomous system: action guards with limits, loop detection, prompt injection defense, and read-only Repository wrapper.

## Files to Create
- `corvus_corone_pilot/v3_autonomous/safety.py`
- `tests/test_safety.py`

## Implementation Requirements
- [ ] `@requires_confirmation(max_repetitions=50, max_budget=200)` decorator on autonomous_run_study
- [ ] `validate_research_question(question)` — regex patterns for common injection attempts
- [ ] `LoopDetector` — raises `RuntimeError` after N steps
- [ ] `ReadOnlyRepository(Repository)` — raises `PermissionError` on any write to existing data
- [ ] `SafetyViolation` exception class
- [ ] Tests verify each guard triggers on boundary violation
""",
    },
    {
        "milestone": "IMPL Phase 3b — Pilot V3 Autonomous (weeks 39–46)",
        "title": "[IMPL-040] ML foundations: evaluation.py — regularization, k-fold CV, calibration",
        "labels": ["implementation", "pilot-v3", "ml-foundations"],
        "body": """
## Why This Task
The performance predictor in V3 makes confidence claims: "algorithm A will achieve quality Q on this problem." Without calibration, a confidence of 0.85 may correspond to 60% actual accuracy. An autonomous agent acting on uncalibrated confidence generates studies where the predictor is already confident — and misses the cases where it should be uncertain.

## Summary
Implement model evaluation tools used by V3's `CalibratedPredictor`: L1/L2 regularization, k-fold CV, and probability calibration.

## Files to Create
- `corvus_corone_pilot/v3_autonomous/ml_foundations/evaluation.py`
- `tests/test_evaluation.py`

## Implementation Requirements
- [ ] `update_with_l2(weights, grads, lr, lambda_reg)` — weight decay
- [ ] `kfold_cv(model_class, X, y, k=5)` → (mean_score, std_score) from scratch
- [ ] `evaluate_agent_calibration(confidences, actuals)` → calibration_error using `calibration_curve`
- [ ] `CalibratedPredictor` using isotonic regression: `predict_with_confidence(features)`
- [ ] Tests: L1 sparseness demonstration, calibration on synthetic data
""",
    },
    {
        "milestone": "IMPL Phase 3b — Pilot V3 Autonomous (weeks 39–46)",
        "title": "[IMPL-041] Autonomous cycle: cycle.py + DVC pipeline + GitHub Actions trigger",
        "labels": ["implementation", "pilot-v3", "dvc", "ci-cd"],
        "body": """
## Why This Task
V3 without a scheduled execution loop is not autonomous — it is a manual process with more steps. The DVC pipeline makes each cycle reproducible: any historical cycle can be replayed from a specific git commit. Without DVC, the cycle produces results but the process that generated them cannot be reconstructed.

## Summary
Implement the full autonomous research cycle and version it with DVC. Schedule via GitHub Actions.

## Files to Create
- `corvus_corone_pilot/v3_autonomous/cycle.py`
- `dvc.yaml`
- `.github/workflows/autonomous.yml`

## Implementation Requirements
- [ ] `autonomous_research_cycle()`: memory.get_patterns → generate_hypothesis → validate_safety → run_study → verify_hypothesis → memory.store_result
- [ ] DVC pipeline stages: `fetch_studies` → `train_predictor` → `run_autonomous_cycle`
- [ ] `dvc.yaml` with deps, outs, metrics
- [ ] GitHub Actions trigger: weekly cron + on push to `corvus_corone/algorithms/`
- [ ] `schedule.every().sunday.at("02:00").do(autonomous_research_cycle)`
""",
    },
    {
        "milestone": "IMPL Phase 3b — Pilot V3 Autonomous (weeks 39–46)",
        "title": "[IMPL-042] Shadow/canary deployment: deployment.py — ModelRouter, A/B testing",
        "labels": ["implementation", "pilot-v3", "mlops"],
        "body": """
## Why This Task
Deploying a new predictor model directly means that if it performs worse, all V3 decisions are affected immediately. Shadow deployment separates "does the model produce reasonable predictions" from "are we ready to serve those predictions." Without this pattern, model updates are either blocked (too cautious) or applied blindly (too risky).

## Summary
Implement safe model rollout for the predictor: shadow mode (log but don't serve), canary release (5%→50%→100%), deterministic A/B routing by thread_id hash.

## Files to Create
- `corvus_corone_pilot/v3_autonomous/deployment.py`
- `tests/test_deployment.py`

## Implementation Requirements
- [ ] `ModelRouter(model_a, model_b, shadow_model=None)`
- [ ] Deterministic routing: `int(md5(thread_id).hexdigest(), 16) % 100`
- [ ] Shadow: logs `shadow_pred`, `prod_pred`, `shadow_delta` to MLflow — never serves
- [ ] `predict(features, thread_id)` → `{prediction, model_version, bucket}`
- [ ] Tests: same thread_id always → same model; shadow never affects prediction
""",
    },
    {
        "milestone": "IMPL Phase 3b — Pilot V3 Autonomous (weeks 39–46)",
        "title": "[IMPL-043] Agent evaluation harness: evals.py — pass@k, task completion",
        "labels": ["implementation", "pilot-v3", "testing", "agent"],
        "body": """
## Why This Task
V3 is stochastic — the same initial knowledge state may produce different hypotheses on different runs. Without a standardized evaluation harness, "does V3 work?" has no quantitative answer. pass@k provides a baseline: if V3 fails every task on first attempt (pass@1 = 0), it is not ready for autonomous operation.

## Summary
Implement evaluation harness for the autonomous V3 agent: pass@k metric, task completion rate, hypothesis falsifiability rate, safety violation tracking.

## Files to Create
- `corvus_corone_pilot/v3_autonomous/evals.py`
- `tests/test_evals.py`

## Implementation Requirements
- [ ] `pass_at_k(n, c, k)` — numerically stable formula from Chen et al. (2021)
- [ ] `evaluate_hypothesis_agent(agent, test_cases, n_runs=10)` → evaluation dict
- [ ] Metrics: task_completion_rate, hypothesis_falsifiable, safety_violations
- [ ] 10 standard test cases (initial knowledge states)
- [ ] CI: eval runner triggers on PR to `v3_autonomous/`
- [ ] Target baseline: pass@1 ≥ 0.6, safety_violations = 0
""",
    },

    # ── Phase 4: Learner ───────────────────────────────────────────────────
    {
        "milestone": "IMPL Phase 4 — Learner Actor (weeks 47+)",
        "title": "[IMPL-044] Algorithm Visualization Engine: learner/visualization_engine.py",
        "labels": ["implementation", "learner", "visualization"],
        "body": """
## Why This Task
The Learner actor's primary need — understanding how algorithms work — cannot be served by the existing Reporting Engine, which produces researcher-facing statistical outputs. Algorithm Visualization requires accessible representations: animated convergence, parameter sensitivity heatmaps, search trajectories. Without this module, the Learner actor exists in documentation but has no interface.

## Summary
Implement Algorithm Visualization Engine serving UC-07. Generates mathematical and intuitive visualizations of HPO algorithms from Corvus study data.

## Files to Create
- `corvus_corone_pilot/learner/visualization_engine.py`
- `tests/test_visualization_engine.py`

## Implementation Requirements
- [ ] `plot_algorithm_convergence(algorithm_id, study_results)` — animated convergence (matplotlib)
- [ ] `plot_parameter_sensitivity(algorithm_id, sensitivity_report)` — heatmap
- [ ] `plot_search_trajectory(run_record, search_space)` — 2D/3D scatter
- [ ] `plot_pareto_front(study_results)` — for multi-objective problems (connects to PhD background)
- [ ] `plot_algorithm_genealogy(algorithm_id)` — timeline visualization (MAB → BayesOpt → TPE)
- [ ] `VisualizationEngine.generate(algorithm_id, study_id, type)` — dispatcher

## References
REF-TASK-0027, UC-07
""",
    },
    {
        "milestone": "IMPL Phase 4 — Learner Actor (weeks 47+)",
        "title": "[IMPL-045] Socratic Guide: agents/socratic_guide.py — LangGraph Socratic mode",
        "labels": ["implementation", "learner", "agent", "pilot-v2"],
        "body": """
## Why This Task
Socratic mode is not a prompt modification — it is a different interaction contract. Direct-answer mode and Socratic mode require different response strategies that cannot coexist in the same node. Without a dedicated LangGraph node and conditional routing, Socratic mode bleeds into direct-answer mode when the LLM decides to be helpful.

## Summary
Implement Socratic mode as a LangGraph node in Pilot V2 per REF-TASK-0028 and UC-09.

## Files to Create
- `corvus_corone_pilot/v2_researcher/agents/socratic_guide.py`
- Updated `corvus_corone_pilot/v2_researcher/graph.py` (add conditional edge)

## Implementation Requirements
- [ ] `socratic_guide_node(state)` — generates guided question instead of direct answer
- [ ] Activation: conditional edge when `state["interaction_mode"] == "socratic"`
- [ ] Pattern: identify what Learner knows → identify gap → generate bridging question
- [ ] Must NOT provide direct answers when in Socratic mode
- [ ] CLI: `corvus-pilot run -q "..." --mode socratic`
- [ ] Tutorial: `docs/06_tutorials/05_understand_algorithm_with_socratic_mode.md`

## References
REF-TASK-0028, UC-09
""",
    },
    {
        "milestone": "IMPL Phase 4 — Learner Actor (weeks 47+)",
        "title": "[IMPL-046] Algorithm Genealogy: learner/genealogy.py — MAB→BayesOpt→TPE lineage",
        "labels": ["implementation", "learner"],
        "body": """
## Why This Task
An algorithm's mathematical specification describes what it computes. Its genealogy describes why it was invented, what problem it solved, and what it inspired. Without genealogy, the Learner sees formulas without context. The MAB → Bayesian optimization → TPE lineage makes the exploration-exploitation tradeoff concrete across 90 years of research.

## Summary
Implement algorithm history and evolution data model per UC-10. Covers the intellectual lineage connecting Multi-Armed Bandit → Bayesian Optimization → TPE, and CMA-ES history connecting to Pareto front work.

## Files to Create
- `corvus_corone_pilot/learner/genealogy.py`
- `corvus_corone_pilot/learner/data/genealogy_data.json`
- `tests/test_genealogy.py`

## Genealogy Data to Include
- Multi-Armed Bandit (Thompson 1933) → Bayesian Optimization (Jones 1998) → TPE (Bergstra 2011)
- Evolution Strategies (Rechenberg 1973) → CMA-ES (Hansen 1996) → relationship with Pareto front / NSGA-II
- Random Search baseline → feature importance connection (Bergstra & Bengio 2012)

## Implementation Requirements
- [ ] `AlgorithmNode`: id, name, year, authors, problem_it_solved, inspired_by (list), inspired (list)
- [ ] `Genealogy`: directed graph of `AlgorithmNode`
- [ ] `Genealogy.get_lineage(algorithm_id)` → list of ancestors
- [ ] `Genealogy.get_descendants(algorithm_id)` → list of successors
- [ ] Tutorial: `docs/06_tutorials/06_algorithm_genealogy_explorer.md`

## References
REF-TASK-0030, UC-10, your PhD background (NSGA-II, CMA-ES)
""",
    },
    {
        "milestone": "IMPL Phase 4 — Learner Actor (weeks 47+)",
        "title": "[IMPL-048] Contextual Algorithm Help: learner/algorithm_help.py — LLM-powered how/why/where explanations",
        "labels": ["implementation", "learner", "agent"],
        "body": """
## Why This Task
The Learner actor needs more than visualisations — they need explanations that answer "how does X work", "why does X work the way it does", and "where does X work best". These are distinct from the Socratic mode (UC-09), which challenges the Learner to reason independently. Contextual help (UC-08) covers established algorithm mechanics: facts the field has settled. Without this module, the Learner has no way to access grounded, theoretically sound explanations of algorithm behaviour from within the system.

## Summary
Implement LLM-powered contextual algorithm help module serving UC-08. Answers how/why/where questions about HPO algorithms with theoretical explanations and practical examples drawn from registered study data. Explicitly marks the boundary between established mechanics and open research questions — the latter are redirected to Socratic mode (UC-09).

## Files to Create
- `corvus_corone_pilot/learner/algorithm_help.py`
- `tests/test_algorithm_help.py`

## Implementation Requirements
- [ ] `AlgorithmHelp.answer(algorithm_id, question_type, question)` — dispatcher for how/why/where question types
- [ ] `AlgorithmHelp.how(algorithm_id)` — explains the algorithm mechanism: probability model, acquisition/sampling rule, update procedure
- [ ] `AlgorithmHelp.why(algorithm_id)` — explains why the algorithm is designed the way it is: the problem it was invented to solve, the limitation of predecessors it addressed
- [ ] `AlgorithmHelp.where(algorithm_id)` — explains where the algorithm performs best: problem characteristics it suits, known failure modes, empirical evidence from study data where available
- [ ] Practical examples drawn from recorded study data (if available) supplement every theoretical explanation
- [ ] Boundary enforcement: questions requiring experimental reasoning are flagged and not answered directly; a redirect message to Socratic mode is returned instead
- [ ] `AlgorithmHelp` must NOT produce research conclusions — it explains established mechanics only
- [ ] Follow-up question handling: context window includes prior exchange so explanations stay coherent across turns

## References
REF-TASK-0026, UC-08
""",
    },
    {
        "milestone": "IMPL Phase 3b — Pilot V3 Autonomous (weeks 39–46)",
        "title": "[IMPL-047] Portfolio: README, docs/architecture.md, end-to-end demo",
        "labels": ["implementation", "documentation", "portfolio"],
        "body": """
## Why This Task
Three systems exist: corvus_corone (V1 library), corvus_corone_pilot V2 (researcher assistant), and V3 (autonomous agent). Without a single document that explains the architecture and rationale of all three together, the project reads as three separate codebases. The README and architecture.md are the entry point for every contributor, recruiter, and collaborator — without them, the work is not discoverable.

## Summary
Produce the top-level documentation that makes the entire corvus_corone project navigable and communicable. This is the week 46 deliverable — portfolio artifacts that present three levels of automation coherently.

## Files to Create/Update
- `README.md` (root) — three-level architecture narrative
- `docs/architecture.md` — C1 context diagram + design philosophy
- `demo/` — end-to-end demo script: natural language question → study → report

## Implementation Requirements
- [ ] README: three-section structure — V1 library, V2 researcher assistant, V3 autonomous
- [ ] README includes: installation (`uv sync`), quick start for each V1/V2/V3, link to tutorials
- [ ] `docs/architecture.md`: C1 diagram (Mermaid), design philosophy, link to ADRs
- [ ] `demo/demo.py`: `corvus-pilot run -q "Does TPE outperform CMA-ES on sphere_5D?"` runs end-to-end
- [ ] `demo/demo_autonomous.py`: one autonomous cycle — hypothesis → study → result
- [ ] CI: demo scripts run in CI as integration tests

## Narrative to Convey
```
V1 — corvus_corone (library)
  Researcher writes Python code to design and run studies.
  Full control, maximum flexibility, rigorous statistics.

V2 — corvus_corone_pilot researcher mode
  Researcher writes natural language. Agents translate to study design.
  Human-in-the-loop before expensive operations.

V3 — corvus_corone_pilot autonomous mode
  System generates hypotheses from past results, runs studies, updates knowledge.
  Weekly autonomous cycles. Safety guards: action limits, read-only past data,
  prompt injection defense, calibrated uncertainty.

The principle: autonomy should be earned through demonstrated reliability.
Trust is built through evaluation (pass@k, safety violations, calibration).
```

## References
Portfolio deliverable
""",
    },
]


# Combined lists for convenience
ALL_MILESTONES = MILESTONES + IMPL_MILESTONES
ALL_ISSUES = ISSUES + IMPL_ISSUES


def main():
    parser = argparse.ArgumentParser(
        description="Create GitHub Milestones and Issues for corvus_corone REF-TASKs"
    )
    parser.add_argument("--repo", required=True, help="GitHub repo in format owner/repo")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be created without creating")
    parser.add_argument("--docs-only", action="store_true", help="Create only documentation tasks (REF-TASK-0001..0030), skip implementation tasks")
    parser.add_argument("--impl-only", action="store_true", help="Create only implementation tasks (IMPL-000..046), skip documentation tasks")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: No GitHub token. Use --token or set GITHUB_TOKEN env var.")
        sys.exit(1)

    if args.dry_run:
        print(f"\n=== DRY RUN — would create in {args.repo} ===")
        print(f"\nMilestones ({len(MILESTONES)}):")
        for m in MILESTONES:
            print(f"  • {m['title']}")
        print(f"\nIssues ({len(ISSUES)}):")
        for i in ISSUES:
            print(f"  • [{i['milestone']}] {i['title']}")
        return

    g = Github(token)
    try:
        repo = g.get_repo(args.repo)
        print(f"\n✓ Connected to: {repo.full_name}")
    except GithubException as e:
        print(f"ERROR: Cannot access repo {args.repo}: {e}")
        sys.exit(1)

    # Create labels
    print("\n── Creating labels ──")
    all_labels_needed = set()
    for issue in ISSUES:
        all_labels_needed.update(issue.get("labels", []))

    label_objects = {}
    for label_name in sorted(all_labels_needed):
        color = LABEL_COLORS.get(label_name, "6b7280")
        lbl = get_or_create_label(repo, label_name, color)
        if lbl:
            label_objects[label_name] = lbl

    # Create milestones
    print("\n── Creating milestones ──")
    milestone_objects = {}
    milestones_to_create = ALL_MILESTONES if not getattr(args, "docs_only", False) else MILESTONES
    if getattr(args, "impl_only", False):
        milestones_to_create = IMPL_MILESTONES
        issues_to_create = IMPL_ISSUES
    elif getattr(args, "docs_only", False):
        milestones_to_create = MILESTONES
        issues_to_create = ISSUES
    else:
        milestones_to_create = ALL_MILESTONES
        issues_to_create = ALL_ISSUES
    for m_data in milestones_to_create:
        m = get_or_create_milestone(repo, m_data["title"], m_data["description"])
        milestone_objects[m_data["title"]] = m

    # Create issues
    print("\n── Creating issues ──")
    created = 0
    skipped = 0

    # Check existing issues to avoid duplicates
    existing_titles = set()
    for issue in repo.get_issues(state="all"):
        existing_titles.add(issue.title)

    for issue_data in issues_to_create:
        title = issue_data["title"]

        if title in existing_titles:
            print(f"  ↷ Skipping (exists): {title[:70]}")
            skipped += 1
            continue

        milestone = milestone_objects.get(issue_data["milestone"])
        labels = [label_objects[l] for l in issue_data.get("labels", []) if l in label_objects]

        try:
            issue = repo.create_issue(
                title=title,
                body=issue_data["body"],
                milestone=milestone,
                labels=labels,
            )
            print(f"  + Created #{issue.number}: {title[:70]}")
            created += 1
            time.sleep(1.0)  # Rate limiting: GitHub allows ~30 requests/min for issue creation
        except GithubException as e:
            print(f"  ✗ Failed: {title[:60]} — {e}")

    print(f"\n══ Done ══")
    print(f"  Milestones: {len(milestone_objects)}")
    print(f"  Issues created: {created}")
    print(f"  Issues skipped (already exist): {skipped}")
    print(f"\n  View at: https://github.com/{args.repo}/issues")
    print(f"  Milestones: https://github.com/{args.repo}/milestones")


if __name__ == "__main__":
    main()
