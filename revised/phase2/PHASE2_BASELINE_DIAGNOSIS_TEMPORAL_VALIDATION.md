# Phase 2 Baseline Diagnosis Temporal Validation

## Question and cutoff

The Phase 2 protocol defines baseline disease covariates strictly before `B = index_date - 730 days`. It requires age, recorded sex, diabetes, hypertension and CKD at that cutoff, with BMI only when validly measured before B. This audit does not move the cutoff. It reconstructs aggregate disease timing from existing prepared inpatient diagnoses and chronology, without retaining or exporting patient rows.

## Sources and code rules

Primary source: `longitudinal/diagnoses_all.parquet`, linked to `longitudinal/admissions_chronology.parquet` by `(subject_id, hadm_id)`. The diagnosis source has 4,756,326 rows and fields `subject_id`, `hadm_id`, `icd_code`, `icd_version`, `seq_num`, `admittime`, `dischtime`, and `is_mi_code`. Admission linkage provides a recorded date; it is not biological disease onset.

| Disease | ICD-9 | ICD-10 |
|---|---|---|
| Diabetes | `250*` | `E08*`-`E13*` |
| Hypertension | `401*`-`405*` | `I10*`-`I15*` |
| CKD | `585*` | `N18*` |

Code punctuation/case is normalized; ICD version is used to distinguish code families. The MI-only `diagnoses_mi_codes.parquet` and `mi_admissions.parquet` do not provide complete chronic-disease history.

## Aggregate timing results

Denominator for eligible counts is the 168,915-person common-index population. Ever documented includes any linked source admission, including admissions at index or after index, so it is descriptive and not a baseline covariate. The date range is the earliest and latest diagnosis-admission date across the linked eligible records, not an individual participant history interval.

| Disease | Source admissions with code | Source patients with code | Eligible people ever documented (all dates) | Before B | During BP window, before index | On index date | After index | Earliest linked date | Latest linked date | Negative disease indicator supported? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Diabetes | 103,903 | 36,561 | 31,857 | 0 | 0 | 27,725 | 17,984 | 2105-10-04 | 2212-04-06 | No |
| Hypertension | 216,267 | 88,039 | 78,375 | 0 | 0 | 68,948 | 40,723 | 2105-10-04 | 2212-04-06 | No |
| CKD | 62,558 | 22,350 | 18,913 | 0 | 0 | 12,412 | 12,506 | 2105-10-04 | 2212-04-06 | No |

The date extrema reflect MIMIC de-identified dates and the linked hospital record span. Some categories overlap because a person can have index and later diagnosis records. The source-level row counts refer to admissions with at least one relevant diagnosis after admission-level flag aggregation, not raw code-row totals.

Machine-readable aggregate evidence: `aggregates/PHASE2_BASELINE_DIAGNOSIS_TEMPORAL_SUMMARY.csv`. Reproduction command from repository root: `python revised/phase2/scripts/phase2_b_prepared_data_audit.py`. The script writes one aggregate row per disease and no patient identifiers.

## Prepared feature-file investigation

`clinical/features_comorbidities.csv` is referenced in `docs/Phase F — Master Dataset.md` and loaded by `src/features/build_master_dataset.py`, but it is **not present** among current repository files or the six local archive members. The documentation describes 194,587 rows keyed by `hadm_id` and four fields: diabetes, hypertension, CKD and prior MI. `src/features/extract_comorbidities.py` confirms the output is admission-keyed and sets each flag if a matching diagnosis occurs in any earlier admission with `admittime < anchor_time`; it writes no diagnosis dates or look-back start. Thus it is a temporally indexed any previously recorded inpatient code summary, not a patient-level ever flag and not a specific pre-window baseline history. A zero is no earlier matching code in the available record, not known absence of disease. The script uses outdated hard-coded paths and an incorrect prior-MI mapping; it was inspected, not run or modified.

The actual `master/test.parquet` schema has 184 columns and includes integer `diabetes`, `hypertension`, `ckd`, `prior_mi` flags. It has no diagnosis dates or diagnosis-code source/version columns. The master schema is an ECG-selected split joined across `study_id`, `hadm_id`, and patient ID; these flags cannot be assumed to represent the Phase 2 index/cutoff. They were not joined to the Phase 2 risk set. The single test split was streamed to an anonymous temporary file solely to read Parquet schema metadata; no row values were read and the temporary file closed/deleted automatically.

## Interpretation

Under the current common-index rule, index is the earliest eligible nonacute admission (and documented acute/historical MI on or before index is excluded). The prepared inpatient diagnoses therefore offer no pre-index hospital history before B for this population. The zero pre-B counts are structural to the observed hospital-entry design; they do not imply that participants had no diabetes, hypertension or CKD before entering MIMIC.

The diagnosis table cannot support a true-negative indicator. No documented diagnosis before B is unknown history. Diagnoses on index date and later are not moved backward to baseline. The planned disease adjustment set and documented-diabetes modifier cannot be implemented under the fixed timing rule with current data. Additional temporally linked pre-entry history (for example, valid prior claims/clinical records with dates and a defensible linkage) or an explicit team-approved design change would be required; no change is made here.
