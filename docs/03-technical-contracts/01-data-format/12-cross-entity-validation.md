# §5 Validation Rules (Cross-Entity)

> Index: [01-data-format.md](01-data-format.md)

<!--
  Invariants that span multiple entities — cannot be expressed as per-field rules.

  Examples of invariants to consider:
    - Every Run.problem_instance_id must reference a Problem Instance with the same version
      as declared in the parent Study
    - Seeds within an Experiment must be unique per (problem, algorithm) pair
    - A Result Aggregate's n_runs must equal the count of completed Runs for that combination
    - Every Performance Record's evaluation_number must be monotonically increasing within a Run

  For each invariant:
    - State it precisely
    - When is it checked? (at write time, at read time, in analysis)
    - What is the consequence of violation? (reject, warn, flag)
-->
