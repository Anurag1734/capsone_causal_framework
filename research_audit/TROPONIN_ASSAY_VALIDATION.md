# Troponin Assay Validation

## Decision

No configured threshold is validated for primary event-time reconstruction. The table is preserved as supplied, but all three rows are explicitly unresolved in `VALIDATED_TROPONIN_THRESHOLDS.csv`; no value is promoted to a validated URL.

## Sources and interpretation

- The complete visible seven-column configuration was transcribed from `data/raw/troponin_thresholds.jpeg` to `research_audit/artifacts/troponin_thresholds.csv`. It specifies item, assay label, anchor-year range, sex, `url_value`, and unit. It contains no manufacturer/platform, method, citation, or provenance field.
- `data/raw/longitudinal/d_labitems.parquet` provides item labels (`Troponin I` or `Troponin T`), fluid (`Blood`), and category (`Chemistry`); it does not identify assay platform or generation.
- `labevents.csv` supplies per-row `ref_range_lower` and `ref_range_upper`. These are recorded laboratory reference bounds in the source rows, not automatically interchangeable with the assay-specific 99th-percentile URL used for research classification.
- The project presentation (`docs/capstone_phase3_ppt_content.md`) attributes 0.014 ng/mL for troponin T and 0.040 ng/mL for troponin I to ACC/AHA but gives no assay-specific source. Its attribution is insufficient to validate the values for these item IDs.
- The Fourth Universal Definition of MI states the general cardiac-troponin principle: myocardial injury is defined relative to the assay's 99th-percentile upper reference limit, and MI additionally requires clinical evidence of ischemia. Reference: Thygesen K, et al. *Fourth Universal Definition of Myocardial Infarction (2018).* Circulation. 2018;138:e618-e651. doi:10.1161/CIR.0000000000000617. This is general diagnostic guidance, not evidence for the three configured numeric values or MIMIC assay platforms.

## Item findings

| Item | Dictionary label | Configured assay/cutoff | Rows / numeric | Unit | Recorded `ref_range_upper` | Decision |
|---|---|---|---:|---|---|---|
| 51002 | Troponin I | cTnI / 0.04 ng/mL | 0 / 0 | no observations | none | Unresolved; cannot assess applicability. |
| 51003 | Troponin T | cTnT / 0.014 ng/mL | 359,000 / 149,109 | ng/mL | 0.01 for all 359,000 rows | Unresolved; configured cutoff is above the recorded upper reference for every row. The user-provided 0.015 value is not present in the retained source subset. |
| 52642 | Troponin I | cTnI / 0.04 ng/mL | 163 / 163 | ng/mL | 0.08 for all 163 rows | Unresolved; configured cutoff is below the recorded upper reference, platform is unknown, and no row has an admission ID. |

All observed configured-item measurements use `ng/mL`. The table's applicability is 2100-2250 and sex `ALL`; observed data years are within that range and both sexes occur for items 51003 and 52642. This does not establish that one sex-agnostic cutoff or one unchanged assay URL is appropriate over the full interval.

Item 51002 is present in `d_labitems.parquet` but has no rows in the complete streamed `labevents.csv` member. The available source files do not establish whether it was not collected, unused in this extract, or absent for another source-specific reason; no result values or reference bounds can be inferred.

The exact distributions, numeric missingness, timestamps, unit/reference counts, and row-level linkage counts are in `TROPONIN_ITEM_DIAGNOSTICS.csv`. No threshold is inferred, optimized, or changed.
