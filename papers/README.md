# Reference Papers

The PDFs that used to sit here were removed on 2026-09-09. They were third-party papers, and
redistributing them is not something this project has the right to do: the foundational one is
under the *arXiv perpetual non-exclusive license*, which grants arXiv the right to distribute
and grants that right to nobody else. The scientific value is the citation, not the copy.

Fetch them yourself from the identifiers below.

## Methodological foundation

The benchmarking methodology of this project derives almost entirely from:

> Bartz-Beielstein, T., Doerr, C., van den Berg, D., Bossek, J., Chandrasekaran, S., Eftimov, T.,
> Fischbach, A., Kerschke, P., La Cava, W., Lopez-Ibanez, M., Malan, K. M., Moore, J. H.,
> Naujoks, B., Orzechowski, P., Volz, V., Wagner, M., & Weise, T. (2020).
> **Benchmarking in Optimization: Best Practice and Open Issues.** arXiv:2007.03488.
> <https://arxiv.org/abs/2007.03488>

Every MANIFESTO principle traces to a section of that paper. The nine principle categories are
listed in `docs/01-manifesto/MANIFESTO.md`.

## Further reading referenced by the design

> Lu, Z., Whalen, I., Boddeti, V., Dhebar, Y., Deb, K., Goodman, E., & Banzhaf, W. (2018).
> **NSGA-Net: Neural Architecture Search using Multi-Objective Genetic Algorithm.**
> arXiv:1810.03522. <https://arxiv.org/abs/1810.03522>

> **Reproducible and Efficient Benchmarks for Hyperparameter Optimization of Neural Machine
> Translation Systems.** Provenance not recorded when the PDF was added; identify it before
> citing it in any published study.

> Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006).
> **Appropriate statistics for ordinal level data: Should we really be using t-test and Cohen's d
> for evaluating group differences on the NSSE and other surveys?**
> Annual meeting of the Florida Association of Institutional Research.
>
> The source of the Cliff's delta interpretation thresholds in
> `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §4.2 — 0.147, 0.33
> and 0.474, obtained by mapping Cohen's conventional d values onto the delta scale. They are
> conventions rather than measurements, and the document says so.

## Note for IMPL-027

ROADMAP task IMPL-027 builds a retrieval index over this directory. The operator supplies the
PDFs locally; the index is built from files that are never committed. `papers/*.pdf` is ignored.
