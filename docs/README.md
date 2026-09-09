# Documentation Map and Reading Order

## Precedence

When two documents disagree, the one earlier in this order wins and the later one is corrected.
The rule is recorded in
[ADR-012](02-design/02-architecture/01-adr/adr-012-documentation-layer-normativity.md).

```
MANIFESTO  →  SRS  →  ADR  →  03-technical-contracts/  →  C2 / C3 / C4  →  code
```

- **[`03-technical-contracts/`](03-technical-contracts/)** is the only place that *defines*
  identifiers, signatures, field names and types, enumeration values, error classes, metric
  identifiers and file formats — with exactly three exceptions, named by
  [ADR-026](02-design/02-architecture/01-adr/adr-026-named-exceptions-to-contract-exclusivity.md)
  and listed below. A fourth requires an ADR that amends that list.

  | Document | Authoritative for | By |
  |---|---|---|
  | [`02-cli-spec.md`](02-design/02-architecture/03-c4-leve2-containers/02-cli-spec.md) | command names, arguments, options, output conventions, error-message grammar, exit codes | ADR-016 |
  | [`03-report-format-spec.md`](02-design/02-architecture/03-c4-leve2-containers/03-report-format-spec.md) | section structure and audience language of both Reports | ADR-018, ADR-019 |
  | [`02-statistical-methodology.md`](04-scientific-practice/01-methodology/02-statistical-methodology.md) | the `VIZ-L1-NN` identifiers and the statistical procedures | ADR-011, ADR-018 |

  Each exception is *per surface*. `02-cli-spec.md` is authoritative for the command line and
  for nothing else; it may not coin an entity field, an exception class or a metric identifier.
- **[SRS](02-design/01-software-requirement-specification/01-srs/01-SRS.md)** is the only place
  that defines `FR-*`, `NFR-*`, `UC-*` and `CONST-*`, and, in §1, the V1 release scope.
- **[ADRs](02-design/02-architecture/01-adr/)** are the only place that records decisions.
- **C2, C3 and C4 are descriptive.** They explain how the normative material is grouped into
  containers and components and why. They may cite, never coin — outside the two C2 documents
  named above, and only for the surface named there.

---

## For system design — what we are building

[MANIFESTO](01-manifesto/MANIFESTO.md)
→ [SRS](02-design/01-software-requirement-specification/01-srs/01-SRS.md)
→ [C1 System Context](02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md)
→ [C2 Containers](02-design/02-architecture/03-c4-leve2-containers/01-index.md)
→ [C3 Components](02-design/02-architecture/03-c4-leve2-containers/04-c4-leve3-components/01-c4-l3-components/01-c4-l3-components.md)
→ [C4 Code](02-design/02-architecture/05-c4-level4-code/01-index.md)
→ docstrings in `packages/`

Start here if you want to know what the system is and why its parts are drawn where they are.
The V1 release scope, including which containers and actors are deferred, is in SRS §1.

---

## Technical contracts — how components speak to each other

[C2 Containers](02-design/02-architecture/03-c4-leve2-containers/01-index.md)
→ [Interface contracts](03-technical-contracts/02-interface-contracts/01-index.md)
→ [Data format](03-technical-contracts/01-data-format/01-index.md)
→ [Public API contract](03-technical-contracts/04-public-api-contract.md)
→ docstrings

Start here if you are implementing anything. This is the normative layer.

---

## Scientific practice — how to use it

[MANIFESTO](01-manifesto/MANIFESTO.md)
→ [Benchmarking protocol](04-scientific-practice/01-methodology/01-benchmarking-protocol.md)
→ [Statistical methodology](04-scientific-practice/01-methodology/02-statistical-methodology.md)
→ [Metric taxonomy](03-technical-contracts/03-metric-taxonomy/01-index.md)

Start here if you want to run a study correctly rather than merely successfully.

---

## Community — how it grows

[MANIFESTO](01-manifesto/MANIFESTO.md)
→ [Contribution guide](05-community/01-contribution-guide.md)
→ [Versioning governance](05-community/02-versioning-governance.md)
→ [Interface contracts](03-technical-contracts/02-interface-contracts/01-index.md)
→ [Data format](03-technical-contracts/01-data-format/01-index.md)

Start here if you want to contribute a problem, an algorithm or an analysis tool.

---

## Reference

- [GLOSSARY](GLOSSARY.md) — shared vocabulary; every other document and docstring uses these terms
- [ROADMAP](ROADMAP.md) — work sequencing; it does not define release scope
- [Tutorials](06-tutorials/) — step-by-step walkthroughs, starting with the algorithm author onboarding

---

## Document structure

Each document carries three structural features that keep the corpus navigable:

1. **STORY ROLE** — which chapter of the narrative this document is.
2. **CONNECTS TO** — explicit bidirectional links to related documents.
3. **Docstring and task bridge** — where the documentation hands off to code docstrings and to
   issue tracker tasks, so that documents, docstrings and tasks form one system rather than
   three silos.
