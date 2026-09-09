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

**Status: open. Requires a decision.**

The branch exists on `origin` and holds 25 commits of a different codebase: a layered
architecture with a web UI, an auth service and a `docker-compose.yml`, 89 files in total. It is
not reachable from `main`.

Three things make it a launch blocker rather than clutter:

- It contains hardcoded credentials in added lines: `researcher123` in
  `src/presentation-layer/web-ui/index.html` and both `researcher123` and `admin123` in
  `src/support-layer/auth-service/main.py`. They are demonstration passwords, not production
  secrets, but a public repository containing credentials invites automated scanners and reads
  as carelessness.
- It carries its own `LICENSE`, MIT, copyright 2024 Aviarium Software. `main` is
  AGPL-3.0-or-later (ADR-022). Two licences in one repository is a question every prospective
  user will have to resolve for themselves, and the wrong answer is permissive.
- It shows an abandoned architecture as if it were current, which misleads anyone who lands on
  the branch list.

**Options:** delete the branch from `origin` and locally; or rewrite its history to remove the
credentials and keep it as an archived design record; or keep it and accept the three costs
above. Deleting is the only option that removes the credentials from what gets published.

## 2. Remote branch count

**Status: open. Requires a decision.**

`origin` carries 38 branches beyond `main`, most of them per-task branches named after closed
`REF-TASK` items. They make the branch list unreadable for a newcomer and suggest work in
progress that has in fact been merged.

**Suggested:** delete the merged task branches, keep `main` and `dev`.

## 3. Redistribution of papers

**Status: open. Requires a decision.**

`papers/` holds 4.4 MB of PDFs across three documents.

| File | Provenance | Redistribution |
|---|---|---|
| `benchmarking-in-optimization-best-practice-and-open-issues.pdf` | arXiv:2007.03488 | **Not clearly permitted.** Verified: the paper is under the *arXiv perpetual non-exclusive license*, which grants arXiv the right to distribute. It does not grant that right to third parties. |
| `1810.03522v2.pdf` | arXiv:1810.03522 (NSGA-Net) | Unverified. arXiv papers carry per-paper licences; some are CC BY, most are the non-exclusive licence above. |
| `Reproducible and Efficient Benchmarks for Hyperparameter Optimization of Neural Machine Translation System.pdf` | Unknown, no arXiv identifier in the filename | Unverified, and the highest risk of the three: a publisher PDF cannot be redistributed at all. |

The project's own licence makes this sharper rather than softer. AGPL-3.0 obliges the project to
publish its corresponding source; it grants no right to relicense someone else's paper.

**Suggested:** replace the PDFs with a `papers/README.md` listing title, authors, arXiv or DOI
identifier and a link. The scientific value is the citation, not the copy. Note that ROADMAP
IMPL-027 plans a retrieval index over `papers/`; that task then needs the operator to fetch the
PDFs themselves, which is the correct arrangement anyway.

## 4. Contact details

**Status: open.** The README section is a TODO and the contribution guide assumes an issue
reporting route exists. Needs a maintainer contact before strangers arrive.

## 5. Secret scan on the final history

**Status: done once, repeat before publishing.** A pattern scan over all branches found the
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
