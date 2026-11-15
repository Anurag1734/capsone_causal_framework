# Troponin Threshold Derivation Evidence

## Investigation scope and result

A focused search covered repository scripts, notebooks, documentation and research notes, experiment/configuration artifacts, JSON/CSV files, prior cohort-generation material, and available Git history. It searched for item IDs 51002, 51003, and 52642; configured values 0.04 and 0.014; and derivation terms including 95th percentile, 99th percentile, URL, and troponin threshold.

**Result: the original derivation was not recovered.** No source code, notebook, experiment log, cohort definition, or calculation output was found that reproducibly generates the three configured numbers. The search did find:

- The transcribed configuration [`artifacts/troponin_thresholds.csv`](./artifacts/troponin_thresholds.csv), with one row per item, an assay label, a year interval of 2100–2250, sex `ALL`, value, and unit. These fields describe intended scope, not derivation.
- [`docs/pipeline.txt`](../docs/pipeline.txt), which proposes using an assay-specific **99th-percentile** upper reference limit and stratifying by assay, year, and (where appropriate) sex. This is a pipeline specification, not evidence that the configured values were calculated from patient data.
- [`docs/capstone_phase3_ppt_content.md`](../docs/capstone_phase3_ppt_content.md), which says to apply “ACC/AHA” thresholds of cTnT >0.014 ng/mL and cTnI >0.040 ng/mL. No assay-specific bibliographic citation or platform documentation accompanies that statement.
- [`scripts/extract_cohort.py`](../scripts/extract_cohort.py), which includes the item IDs in a troponin query and extracts a peak value; it does not provide a reproducible derivation for these cutoffs.
- Git history containing the configuration and generic presentation statement, but no earlier calculation or provenance record. The history check does not establish that the numbers were independently estimated.

The presentation's description of item 52642 as “hs-Troponin I” is not accompanied by platform documentation. The dictionary provides only Troponin I/T labels; it does not identify assay manufacturer, platform, or generation.

## Questions about the purported derivation

| Question | Finding |
|---|---|
| Were the values calculated at the 95th percentile? | **Not established.** No 95th-percentile method or calculation record was found. The pipeline specification instead proposes a 99th-percentile URL. |
| What population was used? | **Unknown.** No reference cohort or inclusion criteria were found. |
| Were controls, MI patients, or both included? | **Unknown.** No derivation population labels or cohort-selection procedure were found. |
| Were calculations performed separately for each assay? | **Not demonstrated.** The configuration is item-specific, but has no calculations or population-specific statistics. Both cTnI items share 0.04 ng/mL. |
| Were values experimentally estimated or taken from external documentation? | **Unresolved.** The presentation makes a generic external “ACC/AHA” attribution but gives no assay-specific source; no local experimental derivation was recovered. |

Thus, “95th percentile” must not be used to describe these cutoffs. The best-supported description is: **provisional configured values with undocumented item-specific provenance and a generic, uncited clinical-guideline attribution in a presentation.**

## Distribution and reference-range checks

The figures below come from [`TROPONIN_ITEM_DIAGNOSTICS.csv`](./TROPONIN_ITEM_DIAGNOSTICS.csv), generated from the retained measurements in [`artifacts/troponin_measurements.csv`](./artifacts/troponin_measurements.csv). The quantiles describe the available item-level recorded values; the artifacts do not identify a healthy reference population or separate MI from non-MI patients. They are diagnostic checks, **not** a proposed method for choosing a clinical threshold.

| Item | Measurements / numeric values | Observed distribution (ng/mL) | Recorded upper reference | Configured value |
|---|---:|---|---:|---:|
| 51002 | 0 / 0 | No observations; no distribution or reference range available. | None | 0.04 |
| 51003 | 359,000 / 149,109 | p01 0; p05 0.01; p25 0.03; median 0.09; p75 0.30; p90 1.05; p95 2.13; p99 6.5684; max 52.4 | 0.01 on all 359,000 rows | 0.014 |
| 52642 | 163 / 163 | p01 0; p05 0; p25 0; median 0; p75 0.01; p90 0.04; p95 0.086; p99 1.7134; max 5.51 | 0.08 on all 163 rows | 0.04 |

The configured values do not match the empirical p95 of the available records for 51003 or 52642; for 51002 a percentile cannot be calculated. This does **not** prove what method was used originally, because the derivation population and method are missing. It does rule out claiming that the current summaries reproduce a 95th-percentile derivation. These patient-record distributions are also not substitutes for a healthy reference population or clinical assay validation.

## Assay, unit, and linkage evidence

- The three configured rows specify ng/mL. All 359,000 recorded 51003 rows and all 163 recorded 52642 rows also specify ng/mL; the diagnostic report records no unit mismatch. This confirms recorded unit consistency only, not assay comparability.
- Item 51003 is labeled Troponin T; item 51002 and 52642 are labeled Troponin I in the dictionary. Platform, assay generation, and method are absent.
- Item 51002 has no observations, so no value, unit, reference-range, or linkage check is possible.
- Item 51003 has 194,115 rows with `hadm_id` and 164,885 without it. Prior interval-linkage diagnostics classify the missing-ID rows as 108,577 unique interval candidates, 204 ambiguous, and 56,104 with no interval match. Interval candidates were not substituted for source admission IDs.
- Item 52642 has 0/163 `hadm_id` values; all 163 have no matching ED/admission interval. A patient ID alone does not establish which admission a lab belongs to.
- Observed chart years fall within the table's configured year interval and both sexes occur for items with measurements; this does not prove a single sex-agnostic cutoff is appropriate over the interval.

Detailed audit outputs: [`TROPONIN_ASSAY_VALIDATION.md`](./TROPONIN_ASSAY_VALIDATION.md), [`TROPONIN_THRESHOLD_VALIDATION.csv`](./TROPONIN_THRESHOLD_VALIDATION.csv), and [`VALIDATED_TROPONIN_THRESHOLDS.csv`](./VALIDATED_TROPONIN_THRESHOLDS.csv). Those outputs correctly leave all three thresholds unresolved; this investigation does not change them or the source data.
