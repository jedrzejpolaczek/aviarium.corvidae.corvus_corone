# Tutorial: Run Your First Benchmarking Study

<!--
STORY ROLE: Tutorials are the "show, don't tell" chapter. They make the system
accessible to different audiences and demonstrate that the documented principles
actually work in practice.

NARRATIVE POSITION:
  Methodology + Specs + Protocol → Tutorials → (concrete, runnable demonstrations)
  Tutorials are the END of the documentation reading path for most users.

CONNECTS TO:
  → methodology/benchmarking-protocol.md : each tutorial demonstrates one or more protocol steps
  → docs/03-technical-contracts/02-interface-contracts/01-index.md : tutorials show how to implement or use interfaces
  → docs/GLOSSARY.md             : use defined terms; hyperlink on first use per tutorial
  → SRS §3                       : each tutorial covers at least one use case end-to-end

TUTORIAL TYPES to create (one file per tutorial):
  - Getting started: run your first benchmarking study
  - Contribute a benchmark problem: implement Problem Interface and submit
  - Contribute an algorithm: implement Algorithm Interface and submit
  - Design a study: walk through benchmarking-protocol.md Steps 1–5
  - Analyze results: walk through statistical-methodology.md three levels
  - Export to IOHprofiler / COCO: interoperability workflow
  - Reproduce a published study: reproducibility verification workflow
  → Each tutorial corresponds to a use case in SRS §3.

FILE NAMING: [audience]-[action]-[object].md
  Example: researcher-design-study.md
           contributor-add-problem.md
           practitioner-select-algorithm.md

SELF-CONTAINMENT RULE: A reader should be able to complete this tutorial
without reading other documents first. Cross-references are "for more detail",
not prerequisites (except the explicitly listed Prerequisites section).
-->

---

## Audience

<!--
  Who is this tutorial for?
  Use role names from C1 actors: Researcher / Practitioner / Algorithm Author / Community Contributor

  Prior knowledge assumed:
    - Domain: what HPO / optimization knowledge is assumed?
    - Technical: what programming knowledge is assumed?
    - System: has the reader installed the system? Completed a previous tutorial?

  If this tutorial builds on another, name it explicitly:
    "Before this tutorial, complete: docs/tutorials/[prerequisite-tutorial].md"
-->

---

## Learning Objective

<!--
  One sentence: after completing this tutorial, the reader will be able to [verb] [object].

  Examples:
    "...design and execute a reproducible benchmarking study comparing two HPO algorithms."
    "...implement and register a new benchmark problem that passes all contribution requirements."
    "...interpret the three-level analysis output for a completed experiment."

  Bad objective examples (too vague):
    "...understand how the system works."
    "...use the system."
-->

---

## Prerequisites

<!--
  What must be done before starting:
    - Software: what must be installed? Which version?
    - Data: is any data file needed? Where to get it?
    - Previous tutorials: list them explicitly
    - Reading: which spec or methodology sections should be read? (optional vs. required)
-->

---

## Overview

<!--
  A short paragraph: what will the reader do in this tutorial and why?
  Map the steps below to the real-world workflow they represent.
  Reference the protocol steps or use case this tutorial demonstrates.
-->

---

## Steps

The study is authored in Python and executed from the terminal. There is no interactive
`corvus study new` wizard: study authoring functions have no CLI equivalent in V1, because a
Study is a scientific commitment and the framework needs to tell you what it requires before you
make it (ADR-016, FR-27).

### Step 1: Author the Study

```python
import corvus_corone as cc

study = cc.create_study(
    name="TPE vs Random Search under noise",
    research_question=(
        "Does TPE outperform Random Search on noisy, high-dimensional spaces?"
    ),
    problem_ids=[p.id for p in cc.list_problems(tags=["noisy", "continuous"])],
    algorithm_ids=["<tpe-id>", "<random-search-id>"],
    repetitions=10,
    budget=200,
    seed_strategy="sequential",
    sampling_strategy="log_scale_plus_improvement",
    pre_registered_hypotheses=[
        {
            "hypothesis": "TPE reaches a lower final objective than Random Search "
                          "on noisy problems of dimension 10 and above.",
            "test_type": "wilcoxon",
            "metric_id": "QUALITY-BEST_VALUE_AT_BUDGET",
        },
    ],
)
print(study.status)   # draft
```

`create_study()` returns a **draft**. Nothing is committed yet, and you can still change your
mind with `cc.update_study(study.id, repetitions=20)`.

### Step 2: Lock the Study

```python
study = cc.lock_study(study.id)
print(study.status)   # locked
```

This is the pre-registration moment (ADR-013, ADR-021). From here the problem set, algorithm
set, experimental design and hypotheses are immutable, and the Study can run.

If something is unresolved, `lock_study()` refuses and names **every** unresolved decision at
once, with the consequence of each, rather than the first missing field (FR-27):

```
ValidationError: Study cannot be locked. 2 decisions are unresolved:
  - pre_registered_hypotheses is empty. A Study without a declared hypothesis cannot
    distinguish a confirmed result from one found by looking. Declare at least one
    hypothesis, or declare the Study exploratory with test_type "none".
    (MANIFESTO Principle 16, ADR-021)
  - problem_instance_ids covers 1 dimensionality range; the diversity floor asks for 2.
    Conclusions will be scoped to that single range in the Report.
    (ADR-009, FR-33)
```

### Step 3: Run it

```bash
corvus run <study_id>
```

Progress is written to the terminal, one line per completed Run.

### Step 4: Read the reports

```bash
corvus report <experiment_id> --open
```

Every completed Experiment produces **two** reports, one for a researcher and one for a
practitioner (ADR-019). Both carry a limitations section; neither ranks the algorithms.

### Step 5: Export, if you want to cross-check elsewhere

```bash
corvus export <experiment_id> --format ioh --output ./ioh-out
```

The export prints an information-loss manifest before it writes anything (FR-24).

<!--
  Each step follows this format:

  ### Step N: [Action in imperative form]

  What the reader does:
    [Concrete instruction — code, command, UI action, or written artifact to produce]

  Why this step matters:
    [One sentence connecting to a MANIFESTO principle or protocol requirement]
    [Link to the relevant spec/methodology section for deeper reading]

  Expected result:
    [What should the reader see/have after completing this step?]
    [If there is a checkpoint — an observable output — describe it exactly]

  Common mistakes:
    [What can go wrong here? How to recognize it? How to fix it?]

  ---

  HINT for tutorial authors:
    Steps should be granular enough that the reader always knows what to do next,
    but not so granular that the tutorial becomes a line-by-line code walkthrough.
    A good step takes 2–10 minutes to complete.

    Code snippets in steps should be runnable as-is (no "replace X with your value"
    without a clear example of what "your value" looks like).

    After every 3–4 steps, include a verification checkpoint:
    "At this point, you should have X. Check by running Y."
-->

---

## Expected Outcome

<!--
  What does the completed tutorial produce?
  Be specific: a file, a report, a test that passes, an artifact registered in the system.

  How does the reader know they succeeded?
  State one verifiable criterion (not "it should work" but "running X produces Y").
-->

---

## What You Learned

<!--
  A brief summary (3–5 bullet points) of the key concepts this tutorial demonstrated.
  Connect each point to the relevant document for further reading.

  Example:
    - How to formulate a valid research question → methodology/benchmarking-protocol.md §Step 1
    - How pre-registration prevents p-hacking → methodology/statistical-methodology.md §3
    - How the seed contract ensures reproducibility → docs/03-technical-contracts/02-interface-contracts/01-index.md §6
-->

---

## Further Reading

<!--
  What to read or do next?
  Build a reading path: this tutorial → [next tutorial] → [reference document]

  Hint: every tutorial should have at least one "next step" to prevent readers
  from hitting a dead end. The reading path is how MANIFESTO's education goal
  (Principle 28) is realized.
-->
