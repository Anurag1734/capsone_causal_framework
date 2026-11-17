# Phase 2 — Adjustment Set and Covariate Dictionary

The common temporal cutoff is `B = exposure_window_start = index_date - 730 days`. Except for age/sex, primary baseline covariates must be documented strictly before `B`. A record during the exposure window or after index is not a baseline confounder. The dictionary is a protocol; source availability, units, and chronology must be validated before use.

| Variable | Operational definition | Role / primary handling | Missingness interpretation / validation |
|---|---|---|---|
| Age at B | Derive from source anchor age/year and B only if deidentification convention supports it; retain top-coded category | Confounder; model flexibly; age modifier <65 vs ≥65 at B | Validate derivation, year shifts, top-coding; no age inferred from admission coding |
| Recorded sex | `gender` from patient-level source | Candidate confounder and modifier | Preserve source categories; do not infer gender; specify handling of missing/other from observed schema |
| Diabetes | Any ICD-9 `250*` or ICD-10 `E08*`–`E13*` documented in linked admission history strictly before B | Candidate confounder; modifier documented pre-B | `1` means documented; `0` means no code found in available prior record, not proven disease absence. Report history observability and missing code fields |
| Hypertension | Any ICD-9 `401*`–`405*` or ICD-10 `I10*`–`I15*` documented strictly before B | Candidate confounder/proxy for chronic BP history | Same documented-history caveat; code may reflect detection/healthcare contact |
| CKD | Any ICD-9 `585*` or ICD-10 `N18*` documented strictly before B | Candidate confounder | Same documented-history caveat; do not use acute kidney labs after B |
| BMI | OMR BMI record with chartdate strictly before B; only after result-name, unit, duplicate, parsing, and plausibility verification | Optional candidate confounder; include only if valid and temporal | Report availability, missingness, age of latest measurement, and unit conversions; do not use within-window/post-window BMI. Plausibility bounds require clinical/data-dictionary confirmation before coding |
| Prior MI | Acute `410*`/`I21*`/`I22*` and historical `412`/`I25.2` by index | Exclusion criterion, not adjustment variable | Constant absence of documented codes by index among eligible participants; no lifetime-MI claim |
| Baseline BP medications | Prescription/pharmacy/admin records before B | Not in primary adjustment set | Outpatient use, adherence, dose, and index exposure are not established. Any sensitivity must name source and avoid equating record with actual use |
| Smoking | Not available in processed data | Unmeasured confounder | Do not impute as observed; quantitative bias analysis only |
| LDL/HDL | Extremely sparse in processed data | Insufficiently measured confounder | Do not treat absent labs as normal or impute fictional history |
| Healthcare utilization | Pre-B prior admission/encounter counts and source-observed history where available | Selection/censoring predictors; use only with clear timing | Partial hospital-system measure; not comprehensive healthcare use |

## Diagnosis history algorithm

Link diagnosis code rows to admission chronology by `(subject_id, hadm_id)`, normalize code punctuation/case, and preserve ICD version. For each person and diagnosis family, set documented history to present if at least one qualifying record has `admittime < B`. Do not count diagnosis on B or later. Earlier hospitalization records are incomplete before first recorded admission; `no documented history` is never recoded to known disease absence. Use only available pre-B history; exclude same-day/within-window and post-index information.

## Adjustment set

Primary candidate set: flexible age at B, recorded sex, documented pre-B diabetes, documented pre-B hypertension, documented pre-B CKD. Add BMI only under a valid pre-B measurement rule and report a BMI availability/sensitivity analysis. Do not include prior MI, post-index diagnoses, medication by default, troponin, post-index laboratory values, acute-care status, or downstream treatment. This set requires a DAG and positivity review; inclusion does not guarantee no unmeasured confounding.

## Important limitations

Absence of diagnoses before B is absence of documentation in observed admissions, not proof of disease absence. This may misclassify chronic conditions and leave residual confounding. Age calculation may be affected by source age anchoring/top coding. BMI and medication capture are selected/incomplete. Smoking is unavailable and lipids sparse. These are not repaired by model flexibility.
