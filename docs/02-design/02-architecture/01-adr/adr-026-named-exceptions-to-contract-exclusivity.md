# ADR-026: Named Exceptions to the Exclusivity of `03-technical-contracts/`

<!--
STORY ROLE: Closes a hole in ADR-012. The precedence rule says only 03-technical-contracts/
may define boundary vocabulary, and three later decisions made documents outside it
authoritative for a named surface. The rule was therefore false as written, and it is the rule
the whole layering argument rests on.

CONNECTS TO:
  → adr-012-documentation-layer-normativity.md : the rule this ADR amends
  → adr-016-cli-surface-authority.md           : made 02-cli-spec.md authoritative
  → adr-018-mandatory-report-visualizations.md : leans on the methodology and the report spec
  → adr-019-two-reports-per-experiment.md      : leans on the report spec
  → docs/README.md                             : states the precedence rule to readers
-->

---

**Status:** Accepted

**Date:** 2026-09-09

**Deciders:** Core maintainers, technical lead

---

## Context

ADR-012 fixed the precedence order and one exclusivity rule:

> **`docs/03-technical-contracts/` is normative.** It is the only place in the corpus where the
> following may be *defined*: identifiers, method and function signatures, field names, field
> types, enumeration values, error and exception classes, metric identifiers and file formats.

`docs/README.md` repeats it to every reader in the same categorical form.

Three later decisions broke it, each for a good reason, and none of them said so.

**ADR-016** made `03-c4-leve2-containers/02-cli-spec.md` — a C2 document — the authoritative CLI
surface, and gave the reason: it is the only candidate that specifies exit codes, error message
format and example terminal output, which is what makes a CLI testable. Command names, option
names, the error-message grammar and the exit-code table are all defined there and nowhere else.

**ADR-018 and ADR-019** rest on `03-c4-leve2-containers/03-report-format-spec.md` for the section
structure of both reports, and on `04-scientific-practice/01-methodology/02-statistical-methodology.md`
§2.1 for the identifiers `VIZ-L1-01` through `VIZ-L1-04`. Those four identifiers appear in eight
documents across the corpus and in no contract.

By ADR-012's own precedence rule the later ADR wins, so all three exceptions are in force. The
problem is that they are in force silently. A contributor asked to add a CLI command, reading
ADR-012 and `README.md`, concludes that the authoritative CLI specification is illegal and that
the command belongs in `03-technical-contracts/`. A reader checking whether the corpus obeys its
own rule finds three violations and cannot tell them from defects.

The 2026-09-09 consistency audit found the concrete cost. Two documents defined the CLI exit
codes — `02-cli-spec.md` and a section of `04-public-api-contract.md` — and they had already
diverged: exit code `2` mapped to `NotFoundError` in the authoritative one and to
`EntityNotFoundError` in the other, and the authoritative one carried the name ADR-015 had
removed. Nothing made the duplicate findable. `check_docs.py`'s duplicate-definition check covers
requirement identifiers only, and its vocabulary check reads `03-technical-contracts/` as the
source of truth, so a definition living outside it is invisible in both directions.

---

## Decision

**The exclusivity rule of ADR-012 holds, with exactly three named exceptions. Nothing else is
an exception, and a new one requires an ADR that amends this list.**

| Document | Layer | Authoritative for | By |
|---|---|---|---|
| `03-c4-leve2-containers/02-cli-spec.md` | C2 | Command names, positional arguments, option names, output conventions, error-message grammar, exit-code table | ADR-016 |
| `03-c4-leve2-containers/03-report-format-spec.md` | C2 | Section structure and audience language of the Researcher and Practitioner Reports | ADR-018, ADR-019 |
| `04-scientific-practice/01-methodology/02-statistical-methodology.md` | Scientific practice | The `VIZ-L1-NN` identifiers and the statistical procedures the Analyzer implements | ADR-011, ADR-018 |

**The exception is narrow in three ways.**

It is *per surface*, not per document. `02-cli-spec.md` is authoritative for the command line and
for nothing else; it may not coin an entity field, an exception class or a metric identifier, and
the audit found it doing exactly that with `NotFoundError`.

It does not travel down. A C3 component document under a container whose C2 page holds an
exception has no exception of its own. `10-public-api-cli/03-cli-command-group.md` cites
`02-cli-spec.md`; it does not extend it, which is what ADR-016 already required of it.

It does not create a second home. Where an exception document defines a surface, no other
document may define the same surface. The duplicate CLI section of `04-public-api-contract.md`
was removed on this basis.

**`docs/README.md` and `CLAUDE.md` state the list.** The precedence section of `README.md` is
where a reader learns the rule, so it is where the reader has to learn the exceptions.

---

## Rationale

**Why amend rather than move the documents into the contracts.** Moving `02-cli-spec.md` and
`03-report-format-spec.md` into `03-technical-contracts/` would make ADR-012 exact with no
exceptions, and it was the tidier option on paper. It was rejected for what it does to the third
case: `VIZ-L1-01` through `VIZ-L1-04` are defined inside a methodology section that also explains
*why* those four charts and not others, in the middle of the Level 1 exploratory analysis they
belong to. Extracting the four identifiers into a contract leaves the methodology citing a
contract for names it invented, and the reason for the choice on the other side of the corpus
from the choice. The same argument holds more weakly for the CLI spec, whose exit-code table is
only meaningful next to the example terminal output that shows what each code accompanies.

The general form of the argument: a definition is worth moving when the definition is the whole
of what the document says about it. In all three cases the definition is embedded in an
explanation that would not survive the move, and a definition separated from its reason is how
the corpus acquired parallel specifications in the first place.

**Why a fixed list rather than a principle.** A principle — "a document may define what it alone
can explain" — is the honest generalisation, and it is unenforceable. Every author believes their
document is the one that can explain the thing. A list of three has the property that adding to
it requires writing an ADR, which is the review step the principle would not get.

**Why this was worth an ADR at all.** The rule ADR-012 states is the foundation of the layering
argument, and it was false. A reader who checks the corpus against its own stated rule and finds
three violations learns that the rule is not enforced, which is worse than the rule not existing:
it makes every other statement of the same kind unreliable. The audit's judgement was that the
absence of this record was a defect in its own right, not a documentation nicety.

**Trade-offs accepted:** the exclusivity rule now has an exception list, so a reader has to
consult two places rather than one, and `check_docs.py` still cannot enforce any of it — the
gate reads `03-technical-contracts/` as its vocabulary source and has no notion of a per-surface
exception. That is stated here rather than papered over: the exception list is a review
obligation.

---

## Alternatives Considered

### Move the three surfaces into `03-technical-contracts/`

**Description:** relocate `02-cli-spec.md` and `03-report-format-spec.md`, and extract the
`VIZ-L1-NN` identifiers into a contract. C2 and the methodology keep pointers.

**Why rejected:** it separates each definition from the explanation that makes it a decision
rather than a fact, and the `VIZ-L1-NN` case makes the cost plain — the identifiers exist to name
the four charts that Level 1 requires, and the requirement is the section they would be moved out
of. Rejected on content, not on the cost of updating links.

**Under what conditions reconsidered:** if a fourth or fifth exception appears. Three named
exceptions is a list; six is a second contracts directory that nobody called one.

### Leave it implicit and rely on ADR-012's precedence rule

**Description:** the later ADR wins, so a reader who notices the conflict can resolve it.

**Why rejected:** precedence resolves conflicts a reader has already noticed. It did not stop the
CLI surface being defined twice and diverging, and it gives a contributor no answer to "where do
I add a command".

### Weaken ADR-012 to "the contracts are normative where they speak"

**Description:** drop exclusivity; say the contracts win on anything they define, and other
layers may define what the contracts leave open.

**Why rejected:** that is the state the corpus was in before ADR-012, and it is what produced
four competing CLI definitions and two exception hierarchies. Exclusivity with a short, named
exception list keeps the property that made ADR-012 worth writing: for any given name, there is
one document you can point at.

---

## Consequences

**Positive:**

- The rule in `README.md` becomes true, and a contributor has a definite answer to where a
  command name or a report section belongs.
- The three exceptions become reviewable: a fourth requires an ADR that amends this one.
- The reasoning that made each exception right is recorded, so a later reader can judge whether
  it still holds.

**Negative / Trade-offs:**

- Exclusivity now has a list attached, and lists rot. The mitigation is that the list is short and
  that adding to it costs an ADR.
- No gate enforces it. `check_docs.py` reads `03-technical-contracts/` as its vocabulary source
  and cannot express "authoritative for the CLI surface only".

**Risks:**

- **Risk:** an exception document coins vocabulary outside its named surface, which is what
  `02-cli-spec.md` did with `NotFoundError`.
  **Mitigation:** the per-surface wording above is the review question, and the exception classes
  in particular are checkable — `check_docs.py` already flags an `*Error` name that no contract
  defines, in every layer, including these three documents.

---

## Related Documents

| Document | Relationship |
|---|---|
| `adr-012-documentation-layer-normativity.md` | The exclusivity rule this ADR amends; Status line updated |
| `adr-016-cli-surface-authority.md` | Created the first exception |
| `adr-018-mandatory-report-visualizations.md` | Relies on the second and third |
| `adr-019-two-reports-per-experiment.md` | Relies on the second |
| `adr-011-visualization-technology.md` | Cites the `VIZ-L1-NN` identifiers as normative in the methodology |
| `docs/README.md` | States the precedence rule and now the exception list |
| `CLAUDE.md` | Carries the same list for a reader's first orientation |
