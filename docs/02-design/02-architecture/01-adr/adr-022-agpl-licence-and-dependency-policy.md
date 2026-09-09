# ADR-022: AGPL-3.0 Licence and Revised Dependency Policy

<!--
STORY ROLE: Records the licence decision and the dependency policy that follows from it.
Supersedes the licensing clauses of ADR-006, whose rationale assumed a permissive licence
and is therefore void. The licence choice is not a formality here: it decides who is able
to contribute an algorithm, which bears directly on MANIFESTO Principle 9.

CONNECTS TO:
  → adr-006-python-version-and-platform-constraints.md : licensing clauses superseded
  → docs/02-design/01-software-requirement-specification/05-constraints/04-const-technical.md : CONST-TECH-06 rewritten
  → docs/02-design/01-software-requirement-specification/05-constraints/03-const-community.md : CONST-COM-01
  → docs/02-design/01-software-requirement-specification/04-non-functional-requirements/05-nfr-open-01.md : NFR-OPEN-01
  → LICENSE
-->

---

**Status:** Accepted

**Date:** 2026-09-09

**Deciders:** Project author

**Supersedes:** the licensing clauses of ADR-006 (the "Dependency license policy" section and
the statement that Corvus Corone is MIT-licensed). ADR-006 remains in force for the Python
version and platform decisions.

---

## Context

ADR-006 stated that Corvus Corone is MIT-licensed and forbade GPL dependencies, reasoning that
a copyleft transitive dependency "would make the combined work GPL, which is incompatible with
permissive use" and that MANIFESTO Principle 27 "requires broad adoption, including commercial
ML teams".

No `LICENSE` file was ever added. The README stated the opposite of the ADR, that the licence
decision was still pending. The 2026-09-08 audit found the three-way contradiction: an accepted
ADR declaring MIT, a README declaring the question open, and no licence file at all. Until it is
resolved the repository cannot be opened, because code published without a licence is not open
source, which makes CONST-COM-01 and NFR-OPEN-01 unsatisfiable.

The requirement the author set is narrower than MIT and wider than nothing: the code may be used,
provided that what is built on it is opened in turn. That is a copyleft requirement, and the
remaining question was how far the obligation reaches.

---

## Decision

**Corvus Corone is licensed under the GNU Affero General Public License, version 3.0 or later
(AGPL-3.0-or-later).** The verbatim licence text is in `LICENSE` at the repository root.

Three consequences follow, and are accepted deliberately:

1. **Derivative works must be released under AGPL-3.0.** Anything that incorporates or links
   against `corvus_corone` and is distributed must carry the same licence.
2. **Network use counts as distribution.** An organisation that offers Corvus Corone, or a
   modified version of it, as a hosted service must publish the corresponding source. This is
   the clause that distinguishes AGPL from GPL, and it is chosen with the V2 Platform Server in
   mind: a shared result repository is exactly the kind of deployment that GPL alone would leave
   closed.
3. **An algorithm wrapped for benchmarking is a derivative work.** An Algorithm Author whose
   optimizer is proprietary cannot contribute it without licensing their adapter, and in the
   usual reading their optimizer, under AGPL-3.0.

**The dependency policy is inverted.** The runtime dependency tree may include copyleft packages,
because the combined work is already AGPL-3.0. The requirement is now compatibility in the other
direction: every dependency must be under a licence whose terms AGPL-3.0 can satisfy. MIT, BSD,
Apache-2.0, ISC, PSF-2.0, LGPL and GPL-3.0-or-later all qualify. Licences that qualify **not**:
proprietary and source-available-but-not-free licences, and GPL-2.0-only, which is incompatible
with version 3. The `licensecheck` step in CI changes accordingly: it fails on a non-free
dependency and on GPL-2.0-only, not on copyleft as such.

---

## Rationale

The decision follows from what the author wants the licence to achieve: use is permitted, but
what is built on top is opened in turn. MIT does not achieve it, since it permits closed
derivatives. MPL-2.0 achieves it only for modified Corvus files. GPL-3.0 achieves it for
distributed derivatives but leaves the hosted case open, and the V2 Platform Server is a planned
hosted deployment. AGPL-3.0 is the licence that closes all three.

It is also the licence most consistent with the MANIFESTO taken as a whole. Principles 19 to 22
require reproducibility, open data and open code as conditions of the science, not as a
preference. A benchmarking result whose surrounding tooling is closed cannot be independently
verified, which is the failure those principles exist to prevent. A copyleft licence makes the
openness a property of the artifact rather than of the goodwill of whoever redistributes it, and
that is the same argument the project already makes for enforcing pre-registration in code rather
than by convention.

### The cost, stated plainly

The third consequence above is a real loss and should not be minimised. MANIFESTO Principle 9
requires comparisons to include algorithms from different families, and some of the strongest
HPO implementations are commercial. Under AGPL those cannot be wrapped and contributed without
their owners relicensing. ADR-006 named this as the reason to prefer MIT, and that reasoning was
sound on its own terms; it is overridden here because the author weighs guaranteed openness above
portfolio breadth.

The mitigation is partial and worth stating. Nothing prevents a researcher from running a private,
undistributed benchmark of a proprietary algorithm: AGPL obligations attach on distribution and on
network service, not on private use. What cannot happen is contributing that adapter back to the
project, or publishing a service built on it, without opening the code. So the practical effect is
on the shared algorithm registry, not on private research.

---

## Alternatives Considered

### MIT, as ADR-006 declared

**Why rejected:** permits closed derivatives, which is precisely the outcome the author's
requirement excludes.

---

### MPL-2.0

**Description:** File-level copyleft. Modified Corvus files must be published; code that merely
imports the library need not be.

**Why rejected:** would have preserved the ability of proprietary algorithm authors to
contribute, but does not reach a hosted deployment or a larger closed work built around the
library. It satisfies the letter of "opened in turn" only for the files that were edited.

**Under what conditions reconsidered:** if the algorithm portfolio turns out to be materially
narrowed by AGPL, and empty portfolio breadth is judged the greater harm to Principle 9, MPL-2.0
is the natural fallback. Relicensing requires the consent of every contributor, so the cost of
that reversal rises with every merged contribution. The decision should be revisited before the
repository is opened, not after.

---

### GPL-3.0

**Why rejected:** identical to AGPL for distribution, but leaves the hosted case open. Given the
V2 Platform Server is a planned shared deployment, that gap is the one most likely to matter.

---

## Consequences

**Positive:**

- CONST-COM-01 and NFR-OPEN-01 become satisfiable; the repository can be opened.
- The three-way contradiction between ADR-006, the README and the missing file is resolved.
- The dependency policy stops excluding copyleft libraries that are now perfectly usable.

**Negative / Trade-offs:**

- Proprietary optimizers cannot be contributed to the shared registry, narrowing the portfolio
  that Principle 9 asks for.
- Institutions with blanket policies against AGPL will not adopt the library, which reduces the
  reach that Principle 27 seeks.
- Relicensing later requires every contributor's consent, so this decision hardens quickly.

**Risks:**

- **Risk:** The Algorithm Author use case, UC-02, silently assumes a permissive licence in its
  onboarding material.
  **Mitigation:** the contribution guide and the algorithm author tutorial must state the
  licensing obligation before a contributor writes an adapter, not after.
- **Risk:** A user believes AGPL forbids private benchmarking of a proprietary algorithm.
  **Mitigation:** the README licence section states that obligations attach on distribution and
  on network service, not on private use.

---

## Related Documents

| Document | Relationship |
|---|---|
| `LICENSE` | The verbatim AGPL-3.0 text |
| `adr-006-python-version-and-platform-constraints.md` | Licensing clauses superseded by this ADR |
| `.../05-constraints/04-const-technical.md` | CONST-TECH-06 rewritten by this ADR |
| `.../05-constraints/03-const-community.md` | CONST-COM-01 becomes satisfiable |
| `.../04-non-functional-requirements/05-nfr-open-01.md` | NFR-OPEN-01 becomes satisfiable |
| `docs/05-community/01-contribution-guide.md` | Must state the licensing obligation to contributors |
