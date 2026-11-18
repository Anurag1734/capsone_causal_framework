# Phase 2 Prepared-Data Blocker Reassessment

**Purpose:** Test whether the prepared local sources resolve the Phase 2 Gate 0 disease-history, observation/death, selection, and support blockers. This is a source audit only. The index, exposure, intervention and estimand remain unchanged. No cohort file or causal model was created.

## Executive finding

The prepared data add useful source detail, but **do not resolve the material Gate 0 blockers**. The longitudinal archive contains admission-linked diagnoses and history summaries, yet no qualifying diabetes, hypertension or CKD documentation exists before the start of the two-year exposure window in the common-index population. The ECG master schema includes disease and treatment flags, but those are admission-keyed historical/acute features without dates in the master table and are tied to a selected ECG/MI cohort, not the Phase 2 baseline. The documented `features_comorbidities.csv` is not present in the current local workspace.

The available follow-up sources remain hospital encounter records, partial DOD and in-hospital death records, and OMR measurements. No outpatient encounter registry, insurance enrollment, continuous-observation indicator, or verified common extraction boundary was found. Therefore no available source establishes complete first-MI cumulative incidence or individual censoring.

## Sources inspected and relevance

| Source | Actual fields/keys inspected | Relevance and result |
|---|---|---|
| `longitudinal/admissions_chronology.parquet` | 431,231 rows; 20 columns including `subject_id`, `hadm_id`, `admittime`, `dischtime`, `deathtime`, `admission_seq`, previous/next admission links, and anchor time | Provides repeated recorded hospital admissions and in-hospital death timestamps. It is not continuous follow-up or enrollment. |
| `longitudinal/diagnoses_all.parquet` | 4,756,326 rows; `subject_id`, `hadm_id`, `icd_code`, `icd_version`, `seq_num`, `admittime`, `dischtime`, `is_mi_code` | Main prepared inpatient diagnosis history; codes can be reclassified by code/version and dated to the admission. It starts with observed admissions, not complete pre-entry health history. |
| `longitudinal/diagnoses_mi_codes.parquet` | 26,824 rows, same eight-field shape | MI-focused derivative; not a full chronic-disease history source. |
| `longitudinal/mi_admissions.parquet` | 25,755 rows; patient/admission key, MI codes, admission time/sequence, first-MI flag | MI-only derivative, not a chronic-disease source and not an observation registry. |
| `longitudinal/patients_demographics.parquet` | 299,712 rows; `subject_id`, gender, anchor age/year, DOD | Demographics and partial death-date source. Missing DOD does not imply survival. |
| `longitudinal/observation_end.parquet` | 180,733 rows; last admission/discharge, in-hospital death time, DOD, `is_dead`, `observation_end` | Derived endpoint summary. As previously reconciled, `observation_end` is DOD when available and otherwise last discharge; it is not a censor date or global database boundary. |
| Longitudinal OMR/lab/vitals coverage catalogues | Aggregate catalogue schemas and rows | Describe measured-table coverage, not patient observation or continuous enrollment. LDL/HDL are absent from the 26-row prepared lab catalogue. |
| `hosp.rar::admissions.csv`, `patients.csv`, `prescriptions.csv`, `emar.csv`; `labevents.rar::labevents.csv` | Actual CSV headers streamed; no data rows retained | Admission/patient keys and event timestamps exist; prescriptions/eMAR are medication records, not outpatient use or enrollment; labs are not follow-up. |
| `master.rar::master/test.parquet` | Schema metadata only, via a temporary file removed when inspection ended; 56,798 rows, 184 columns | Confirms ECG/clinical columns exist, including four comorbidity flags and treatment flags. It is an ECG-selected analysis split, not a replacement for the risk-set source. No row values were read or retained. |

All archives remain unchanged. Only selected headers, Parquet metadata, aggregate catalogues and aggregate temporal summaries were inspected. No full master dataset or ICU archive was extracted.

## Disease-history finding

A new aggregate-only diagnosis timing audit linked `diagnoses_all` to admission chronology and the transient common-index reconstruction. It used ICD-9 diabetes `250*`, hypertension `401*-405*`, CKD `585*`; ICD-10 diabetes `E08*-E13*`, hypertension `I10*-I15*`, CKD `N18*`. It records admission documentation dates, not onset dates. See `PHASE2_BASELINE_DIAGNOSIS_TEMPORAL_VALIDATION.md` and `aggregates/PHASE2_BASELINE_DIAGNOSIS_TEMPORAL_SUMMARY.csv`.

For each condition, qualifying history strictly before `B=index_date - 730 days` was zero in the 168,915-person risk set; history in `[B,index_date)` was also zero. Diagnoses on the index date or later are observable for many patients, but those do not satisfy the agreed baseline cutoff. Absence of a code is not a valid negative disease indicator.

The legacy feature code and the master schema do not repair this timing gap: comorbidity flags summarize diagnoses in earlier admissions relative to a particular admission/anchor and carry no diagnosis dates. Under the Phase 2 rule that selects the earliest eligible admission, there is no earlier observed inpatient admission from which those flags could establish the requested pre-window disease history.

## Observation, death, treatment and laboratory finding

- Hospital admissions provide event/contact dates inside this institution's record. They do not establish that patients remained alive, observed, or free of MI outside the system.
- `observation_end` is not a global data boundary; its fallback to last discharge is not continuous follow-up. Source date maxima remain record extrema, not a verified data-extraction cutoff.
- DOD is present for only 27,980/180,733 (15.5%) in the admission-linked source universe. Prior reconciliation found 557/8,598 admission-level death timestamps outside their admission interval and six patients with multiple distinct timestamps. The linked common-index DOD/death limitations remain in `PHASE2_OBSERVATION_AND_DEATH_FINAL_AUDIT.md`.
- OMR supplies outpatient measurements, not a visit registry or enrollment history. BP selection can be described by observed age/sex and sparse pre-window BMI; prior admission/utilization history is structurally absent before the earliest index. Weighting cannot address unmeasured outpatient access or observation.
- `phase2_stats.json` reports 15,416,708 prescription rows, 365,442 admissions and 158,421 patients in its source universe. Prescription/eMAR records do not establish outpatient use, adherence, dose, or medication status at the Phase 2 exposure window. Master treatment flags are anchored to another admission/ECG cohort and have no Phase 2-aligned date fields.
- The prepared master documentation reports only 738 lab-feature rows among 194,587 admission keys (<1%); those feature files are absent locally and the master schema contains no laboratory columns. The 26-row longitudinal lab catalogue includes HbA1c (223,244 measurements, 74,715 patients, 30,176 admissions; legacy cohort coverage 41,959) but has no LDL/HDL entries and is not linked to pre-window Phase 2 history. Lab records do not provide follow-up observation.

## Gate implication

Prepared-data investigation **partially resolves source provenance and confirms the blocker**, but does not identify the prespecified risk-difference estimand. During script validation, an initial run stopped before output because the CKD display label did not match the lower-case source flag; after correction it reproduced the 3-row aggregate table. No row-level output was created. Gate 0 remains failed. Researcher approval cannot create missing dates, coverage, or pre-window disease history. The team must consider the alternatives in `PHASE2_IDENTIFIABILITY_AND_ESTIMAND_DECISION.md`; Codex does not select one.
