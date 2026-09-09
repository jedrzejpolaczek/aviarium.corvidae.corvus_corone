# Pre-Launch Checklist

<!--
STORY ROLE: The things that must be settled before the repository becomes public.
Everything here is a maintainer decision, not a design question: the architecture
does not depend on any of it, but publishing without settling it causes harm that
is hard to undo.

CONNECTS TO:
  → LICENSE and ADR-022 : the licence these items interact with
  → docs/05-community/01-contribution-guide.md : what a new contributor sees first
-->

The repository is planned to open after the V1 release (SRS §1). Publishing makes the
**entire git history and every pushed branch** public at once, not just `main`. The items below
are therefore not tidiness; each one is something that cannot be quietly fixed afterwards.

---

## 1. Stray branch `initial_implementation`

**Status: resolved 2026-09-09, deleted.**

The branch was last touched on 2025-11-24, six days after the repository's first commit and ten
months before the decision. It held an abandoned architecture, not work in progress. Deleted locally and from `origin`. It carried demonstration credentials in two files and its
own MIT `LICENSE`, which contradicted the AGPL on `main`; deletion was the only option that
removes both from what gets published. The credential literals are deliberately not
reproduced here.

## 2. Remote branch count

**Status: resolved 2026-09-09, pruned to `main` and `dev`.**

The 38 further branches were merged task branches named after closed `REF-TASK` items. They
made the branch list unreadable and suggested work in progress that had in fact landed.

## 3. Redistribution of papers

**Status: resolved 2026-09-09, PDFs removed.**

`papers/` now holds a `README.md` of citations with arXiv identifiers and links, and
`papers/*.pdf` is ignored. IMPL-027 builds its index from files the operator fetches locally,
which is the correct arrangement in any case.

The foundational paper, arXiv:2007.03488, was verified as carrying the *arXiv perpetual
non-exclusive license*: it grants arXiv the right to distribute and grants that right to
nobody else. The other two were unverified, and one had no arXiv identifier at all.

## 4. Contact details

**Status: resolved 2026-09-09, GitHub issues only.**

One public channel, stated in the README and in the contribution guide. No mailing list and no
private support address: a design decision argued in private cannot be checked by anyone who was
not present, which is the transparency the MANIFESTO asks of its own users. Security reports use
GitHub's private vulnerability reporting.

## 5. Secret scan on the final history

**Status: rerun 2026-09-09 after the branch deletion.** A pattern scan over all branches found the
credentials in item 1 and nothing else: no private keys, no provider tokens, no `.env` files at
any point in the history. Re-run after item 1 is resolved, because deleting a branch changes
what is reachable.

---

## What is already settled

- **Licence:** AGPL-3.0-or-later, `LICENSE` present, obligations stated in the contribution
  guide and both algorithm author tutorials (ADR-022).
- **Python and platforms:** 3.10 minimum, tested on 3.10 to 3.12 across Linux, macOS and Windows
  (ADR-006).
- **CI:** runs on push and pull request, and includes the documentation integrity gate.
- **Documentation integrity:** zero dead links, zero undefined requirement identifiers, zero
  duplicate definitions, enforced by `scripts/check_docs.py`.
