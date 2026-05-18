# Tutorial: Explore an Algorithm in Socratic Mode

---

## Audience

**Actor:** Learner

**Prior knowledge assumed:**
- Domain: knows what hyperparameter optimization is; has heard of at least one algorithm
  (e.g., TPE, CMA-ES, Bayesian optimisation) but does not yet understand its mechanics
- Technical: can run a terminal command; no Python coding required for this tutorial
- System: Corvus Corone and Corvus Pilot V2 installed (`pip install corvus_corone[interactive] corvus_corone_pilot`)

Before this tutorial you may want to read:
[`01-cmd-first-study.md`](01-cmd-first-study.md) — not required, but provides context if
you want to connect algorithm behavior to benchmarking results.

---

## Learning Objective

After completing this tutorial, the Learner will be able to use Socratic mode to reason
their way to an understanding of why a specific algorithm design choice exists — without
the system giving them the answer directly.

---

## Prerequisites

- `corvus_corone_pilot` installed: `pip install corvus_corone_pilot`
- Ollama running locally with at least one model pulled: `ollama pull llama3.2`
- At least one `AlgorithmInstance` registered (the tutorial uses CMA-ES, which ships with the package)

---

## Overview

Socratic mode is a deliberate constraint: the system will not answer your question directly.
Instead, it will ask you questions that move your thinking one step forward. This is
uncomfortable at first. That discomfort is the learning happening.

This tutorial walks through a complete Socratic session on one question:
*"Why does CMA-ES use a covariance matrix?"*

You will not find the answer written here. You will find it yourself, guided by the system.

This tutorial demonstrates UC-09 (Socratic Guided Deduction) and uses the Socratic Guide
component of Corvus Pilot V2 (→ `docs/02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot.md`).

---

## Steps

### Step 1: Start a Socratic session

Run the Pilot CLI with the `--mode socratic` flag:

```bash
corvus-pilot run --mode socratic
```

The system responds with a session header:

```
Socratic mode active.
I will guide you with questions rather than answers.
To exit Socratic mode at any time, type: /exit-socratic
To start, ask me something about any algorithm you want to understand.
```

**Why this step matters:** The `--mode socratic` flag sets `interaction_mode = "socratic"`
in `PilotState` for the entire session. All queries in this session will be routed to the
Socratic Guide node, not the Direct Answer node.
→ Query routing design: [`../02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot/01-index.md`](../02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot/01-index.md) (Query Router section)

**Expected result:** The session is active. You see the Socratic mode header.

---

### Step 2: Pose your question

Type:

```
Why does CMA-ES use a covariance matrix?
```

The system will **not** answer. It will ask you a question instead. A representative first
response:

```
Before we get to the covariance matrix, let's start with what CMA-ES is trying to do.
What is the core problem that any search algorithm faces when exploring a continuous
search space?
```

**Why this step matters:** The system identifies that you asked a *why* question —
a question about design rationale rather than a factual lookup. It activates the
Socratic Guide node, which first assesses what you already know and identifies the
smallest reasoning step forward.

**Expected result:** You receive a question, not an explanation. The question is about
something simpler than the covariance matrix itself.

**Common mistake:** Expecting the system to answer. It will not. If you type
"just tell me the answer", the system will acknowledge your request and offer to exit
Socratic mode — but it will not answer while Socratic mode is active.

---

### Step 3: Respond with your current understanding

Answer the system's question honestly, even if you are not sure. For example:

```
I guess the problem is that the algorithm doesn't know which directions in the search
space are promising, so it wastes evaluations exploring bad regions?
```

The system evaluates your response and asks the next bridging question:

```
Good — you've identified that direction matters. Now: if you had two algorithms,
one that samples uniformly at random and one that samples more in directions that
previously led to improvement, what information would the second algorithm need to
store in order to know which directions those were?
```

**Why this step matters:** Each response closes part of the reasoning gap. The system
tracks your knowledge state across turns and generates the next smallest step.

**Expected result:** You receive another question that builds on your previous answer.
The questions should feel connected — each one follows from what you just said.

---

### Step 4: Continue the reasoning loop

Keep responding. The conversation will move through approximately three to five exchanges.
Each exchange narrows the gap between what you know and what the covariance matrix
represents geometrically.

A mid-session exchange might look like:

```
You: So the algorithm would need to remember the shape of the region it has already
     explored? Like, whether the good solutions are clustered in a line or a blob?

Pilot: Exactly. If solutions cluster along a particular axis or diagonal — what
       mathematical object describes the orientation and spread of a set of points
       in multiple dimensions?
```

**Checkpoint:** After three responses, you should be able to complete this sentence
without help: *"The covariance matrix encodes..."*
If you cannot, continue the loop — the system will keep asking.

---

### Step 5: Reach your conclusion

When your answer closes the final gap, the system confirms — without expanding:

```
You: The covariance matrix encodes the shape of the distribution of previous solutions
     — which directions had high variance and which were correlated — so the algorithm
     can sample new points that match that shape.

Pilot: That's it. CMA-ES uses the covariance matrix to adapt its sampling distribution
       to the geometry of the search space as revealed by previous evaluations.
       You got there yourself.
```

**Why this step matters:** The system confirms only after your reasoning is correct. It
does not elaborate further, add caveats, or suggest follow-up topics unprompted — those
next steps are yours to choose.

**Expected result:** The system's confirmation message. The session remains active — you
can ask another question.

---

### Step 6: Explore failure mode handling (optional)

Test the system's response to a direct-answer request:

```
I give up — just tell me how CMA-ES updates the covariance matrix.
```

The system responds:

```
I can see you'd like a direct answer. You can exit Socratic mode with /exit-socratic
and I'll explain the update rule. But if you want to continue, let me try a different
angle: what does it mean to "update" a distribution based on observed samples?
```

The system offers to exit but changes its bridging question strategy rather than
repeating the same one. This is the F2 failure scenario from UC-09.

**Expected result:** The system offers the exit option and pivots to a different bridging
angle. If you type `/exit-socratic`, the session switches to direct-answer mode and the
system explains the CMA-ES update rule directly.

---

## Expected Outcome

At the end of this tutorial you will have:
1. Completed a Socratic reasoning loop on one algorithm question
2. Reached a conclusion that you reasoned to yourself, not one that was given to you
3. Seen the F1 and F2 failure handling (exit offer, strategy pivot) in action

**Verifiable criterion:** Run `corvus-pilot history` after the session. The session log
will show `interaction_mode: socratic`, the number of turns, and the final Learner message
that triggered the confirmation. If the confirmation message is present, the session
completed successfully.

---

## What You Learned

- **Socratic mode is a mode, not a character** — the system routes your query to the
  Socratic Guide node based on `--mode socratic` or question type detection.
  → Architecture: `02-corvus-pilot.md` (Query Router section)

- **The system tracks your knowledge state** — `PilotState.knowledge_state` is updated
  after each turn so bridging questions build on what you said, not on a generic script.
  → Component design: `02-corvus-pilot.md` (Socratic Guide Node section)

- **Bridging questions are grounded in real data** — the system pulls algorithm metadata
  from the Algorithm Registry and, when available, empirical examples from the Results
  Store. Questions about CMA-ES reference the algorithm's registered `known_assumptions`.
  → Interface: `02-corvus-pilot.md` (MCP Server section)

- **Exit is always available** — `/exit-socratic` switches the session to direct-answer
  mode. Socratic mode is an opt-in constraint, not a lock.

---

## Further Reading

- **Understand what Socratic mode is for:** [`../02-design/01-software-requirement-specification/02-use-cases/10-uc-09.md`](../02-design/01-software-requirement-specification/02-use-cases/10-uc-09.md) — UC-09 full use case
- **Algorithm mechanics (direct answers):** [`09-uc-08.md`](../02-design/01-software-requirement-specification/02-use-cases/09-uc-08.md) — UC-08: Contextual Algorithm Help (when you want the explanation without the Socratic loop)
- **See algorithm behavior visually:** [`../02-design/01-software-requirement-specification/02-use-cases/08-uc-07.md`](../02-design/01-software-requirement-specification/02-use-cases/08-uc-07.md) — UC-07: Algorithm Visualisation
- **Explore a completed study's results:** [`12-uc-11.md`](../02-design/01-software-requirement-specification/02-use-cases/12-uc-11.md) — UC-11: Learner Explores Researcher Study Results
- **Architectural design of the Socratic Guide:** [`../02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot/01-index.md`](../02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot/01-index.md)
