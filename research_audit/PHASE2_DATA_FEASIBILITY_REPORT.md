# Phase 1-2 Data Feasibility and Temporal Audit

## Recommendation

**Gate C: hold causal MI-to-ECG analysis.** The audit runner reads the actual repository paths and real Parquet/lab rows. Successful execution is not a feasibility pass: threshold applicability conflicts with recorded lab reference ranges, one configured assay has no observations, another has no admission IDs, and acute-labeled ECGs remain without an independently validated event time. No causal effects were estimated.

**Gate A, diagnosis coding: conditional pass for descriptive cohort work.** ICD-9 410* and ICD-10 I21*/I22* are separated from historical ICD-9 412 and ICD-10 I25.2. The original `diagnoses_mi_codes.parquet` and `mi_admissions.parquet` remain unchanged; use `ACUTE_MI_DIAGNOSIS_BY_ADMISSION.csv` for corrected audit flags.

**Gate B, event timing: fail/unresolved.** The threshold image lacks assay-specific citations. Item 51003's supplied cutoff (0.014 ng/mL) differs from its stored upper reference range (0.01); item 52642's cutoff (0.04) is below its stored range (0.08) and all its rows lack `hadm_id`; item 51002 has no observations. Candidate times are retained but are not accepted event times. Official timing classes are therefore uncertain.

## Diagnosis audit

The audit covers 431,231 admissions and 4,756,326 code rows. Current acute codes are ICD-9 410* or ICD-10 I21*/I22*; historical codes are ICD-9 412 or ICD-10 I25.2. Prior-MI flags use only earlier admissions for the same patient; same-admission codes are not considered prior. See `ACUTE_MI_OUTCOME_AUDIT.csv` and the admission-level output.

## Lab and event-time audit

Source: `data/raw/labevents.rar`, member `labevents.csv`; 118,171,367 rows were streamed and the archive was preserved. The selected-item subset contains 359,163 rows. The event audit reports 38,077 candidate admissions overall and 10,099 with an acute ICD code. These are unvalidated threshold candidates, not MI diagnoses or biological onset times.

The legacy master contains 7,604 acute-presentation ECG rows, 3,053 with missing `index_mi_time`. Of 3,269 acute-admission legacy timestamps, 3,269 match an observed lab row exactly; this proves a measurement exists at that time, not that it is the first measurement above a valid URL.

Among those acute-labeled ECGs, the **provisional** first-candidate timing classes are 4,929 before, 1,857 after, and 818 uncertain. These are not accepted event-relative classifications; the validated timing class remains uncertain for all 7,604 rows.

`ECG_TEMPORAL_RECORDS.csv` contains all ECG rows, a provisional before/after/uncertain class relative to the candidate time, and an official class that remains uncertain. No missing timestamps were filled. The 95 handcrafted features and 64 latent dimensions remain present in the masters; beta-VAE provenance is still missing, and latents remain excluded from causal use.

## Remaining requirements

1. Provide assay/platform references establishing each item-specific URL and units for the relevant years and sexes; resolve the 51003 and 52642 reference-range discrepancies.
2. Provide linkable observations for item 51002 or document its removal from the rule.
3. Decide how to handle 52642 measurements without admission IDs; do not infer an admission without a validated rule.
4. Re-run after threshold adjudication. Keep candidate values separate from accepted event times.

Until these checks pass, the primary handcrafted ECG analysis is not ready for causal estimation. Beta-VAE eligibility is a separate secondary blocker.
