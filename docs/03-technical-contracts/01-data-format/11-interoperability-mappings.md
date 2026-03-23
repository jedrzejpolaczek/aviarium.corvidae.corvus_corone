# §4 Interoperability Mappings

> Index: [01-data-format.md](01-data-format.md)

<!--
  For each external platform the system integrates with (from C1):

  ### [Platform Name] (e.g., IOHprofiler, COCO, Nevergrad)

  Direction: export / import / both

  Mapping table:
    | Our Entity / Field          | Their Entity / Field        | Notes / Losses            |
    |-----------------------------|-----------------------------|---------------------------|
    | Run.seed                    | [their equivalent]          | exact match / approximate |
    | PerformanceRecord.eval_num  | [their equivalent]          | ...                       |

  Data loss / gain:
    What information is lost when converting to their format?
    What information do we gain when importing from their format?
    → Reference SRS NFR-INTEROP for acceptance criteria

  Version compatibility:
    Which versions of their format do we support?
    → Link to ADR if a compatibility decision was made
-->
