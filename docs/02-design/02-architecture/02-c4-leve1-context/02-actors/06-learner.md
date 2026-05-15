# Actor: Learner

> C1 Context: [01-c1-context.md](../01-c4-l1-context/01-c1-context.md)

**Role:** A student, practitioner, or researcher seeking to understand HPO algorithm behavior through interactive exploration and guided discovery — consuming existing study results as teaching material rather than producing new ones.

**Goal:** Build deep understanding of optimization algorithms through visualizations of mathematical foundations, historical context, and Socratic guidance, without designing or running studies themselves.

**Gives the system:** Learning queries, algorithm exploration requests, feedback on explanations.

**Gets from the system:**
- Algorithm visualizations (mathematical and intuitive, for general audiences — MANIFESTO Principle 25)
- Historical context: where the method originated, what problem it was designed to solve
- Socratic guidance: guided questions and counterexamples rather than direct answers (MANIFESTO Principle 28)
- Access to Researcher study results as learning material — the Learner consumes Reports and ResultAggregates produced by the Researcher's Studies

**Relationship to Researcher:**

The Learner is a **downstream consumer** of the Researcher actor's output. The data flow is one-directional:

```
Researcher → [Study → Experiment → Report / ResultAggregates] → Learner
```

The Learner does not modify, re-run, or extend any Study. They read completed Reports and ResultAggregates to understand algorithm behavior. The Researcher's obligation to scope conclusions correctly (MANIFESTO Principle 3) is therefore the Learner's protection: a Report that overstates its conclusions misleads both the Practitioner and the Learner equally.

**Relevant principles:** 3 (scoped conclusions — protects the Learner from over-generalisation), 25 (accessibility for different audiences), 28 (education and support).
