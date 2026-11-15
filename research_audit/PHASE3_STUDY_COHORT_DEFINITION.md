# Phase 3 Study Cohort Definition

## Source population

The admission denominator is all **431,231** admissions in `admissions_chronology.parquet`; the corrected diagnosis audit covers all 431,231. All have a nonmissing anchor age of at least 18 years. The target population is adult MIMIC-IV admissions, not all patients in the community.

## Inclusion and ECG eligibility

An admission is eligible for the ECG cohort when at least one existing master ECG:

1. Joins to that admission with matching patient ID.
2. Has a recorded ECG time within the episode interval: from ED registration when available and not after discharge, otherwise from inpatient admission, through discharge (inclusive).
3. Has an age value of at least 18 years.

There are 375,930 master ECG rows across the existing splits. In 56 rows, ED registration is after discharge and is treated as invalid; inpatient admission time is used as the lower bound. In 54 rows the admission start still follows discharge, so the invalid episode rows are excluded. The interval check retains 375,642 candidate ECG rows and excludes **288** rows outside valid episode bounds. The retained rows cover **191,275** adult admissions; **239,956** adult admissions have no eligible master ECG. The earliest in-episode ECG per admission is selected; ties use the lowest `study_id`. There are **85,516** admissions with multiple in-episode ECGs; extra ECGs are not used in the primary one-per-admission dataset.

## Exposure and comparison groups

- **Acute MI:** any ICD-9 410* or ICD-10 I21*/I22* code on the admission.
- **Historical MI on the admission:** ICD-9 412 or ICD-10 I25.2. This indicator remains separate from acute MI.
- **Prior MI:** any acute or historical MI code documented on an earlier admission.
- **Primary cases:** eligible ECG admissions with an acute code, whether or not prior MI history is also documented.
- **Primary comparison:** no acute code and no documented current or prior MI.
- **Secondary history group:** no acute code, but current historical code or prior MI history. Keep as a separate group for sensitivity analysis.

## Cohort flow and counts

| Stage/group | Admissions | Patients | ECGs |
|---|---:|---:|---:|
| All admissions in chronology | 431,231 | 180,733 | — |
| Adult admissions with an eligible in-episode master ECG | 191,275 | 99,214 | 191,275 selected |
| Adult admissions without an eligible in-episode ECG | 239,956 | — | 0 |
| Acute MI diagnosis with selected ECG | 7,353 | — | 7,353 |
| Nonacute, documented current/prior MI history with selected ECG | 24,209 | — | 24,209 |
| No acute or documented current/prior MI with selected ECG | 159,713 | — | 159,713 |
| Primary binary cohort (acute cases plus clean comparisons) | 167,066 | 93,946 | 167,066 |

All **191,275** selected ECG records have all 95 feature values finite and nonmissing. The primary cohort contains **7,353 cases** and **159,713 comparisons**. Multiple admissions for a patient are permitted; they are not independent.

The 24,209 nonacute admissions with historical/prior MI are retained in the dataset but excluded from the primary comparison. This avoids mixing chronic scar/history-associated ECG morphology into the reference group. Sensitivity analyses may include them as a separate category or include all nonacute admissions with historical/prior MI adjustment. The selected acute cases are not restricted to first MI; prior MI is retained as a covariate.

## Deterministic ECG selection

The rule selects the earliest ECG within the encounter interval, independent of diagnosis, troponin measurements, and feature values. It addresses repeated ECGs at the admission level and preserves `patient_id`, `admission_id`, `ecg_id`, selected time, source split, candidate ECG count, and selection rule. `source_master_split` is provenance only; it is not treated as an analysis split.

## Exclusions and non-use

- 56 ECG rows have ED-registration timestamps after discharge; these timestamps are treated as invalid and inpatient admission time is used instead. In 54 rows the admission start still followed discharge; those invalid episode rows were excluded. Overall, 288 ECG rows outside valid episode bounds were excluded. The resulting data have one row for each of 191,275 admissions with at least one remaining in-episode ECG.
- Admissions without any master ECG remain in the selection-bias denominator but cannot contribute an ECG outcome.
- Troponin-derived labels, provisional event times, and `index_mi_time` are not used.
- The 64 β-VAE latent columns are not included because provenance is unresolved.
- Diagnosis Parquets and the three original master splits were read only and not modified.

Counts are reproducible from [`build_phase3_observational_dataset.py`](./build_phase3_observational_dataset.py) and saved in `data/analysis/observational_mi_ecg/cohort_counts.csv`.
