# Existing Dataset Inventory

## Scope and method

Read-only inspection of all 13 Parquet files under `data/raw`, the two RAR member lists, project scripts/docs/configs/logs, and model artifacts. Parquet row counts, schemas, null counts, identifier uniqueness, label distributions, and selected joins were read directly. The archives were listed with `bsdtar`; neither was extracted. No data or model artifacts were changed.

The three master files are located under `data/raw/master_dataset/`, not directly under `data/raw/` as initially listed.

## Parquet inventory

| File | Rows x columns | Identifier fields and duplicate check | Timestamp fields | Nulls and other observations |
|---|---:|---|---|---|
| `data/raw/longitudinal/admissions_chronology.parquet` | 431,231 x 20 | `subject_id` (180,733 distinct; repeated across admissions), `hadm_id` (431,231 distinct; unique key). No duplicate `hadm_id`. | `admittime`, `dischtime`, `deathtime`, `edregtime`, `edouttime`, `previous_dischtime`, `next_admittime`, `anchor_time` | `deathtime` 422,633; `edregtime` 131,949; `edouttime` 131,949; `discharge_location` 119,155; each of `previous_hadm_id`, `previous_dischtime`, `next_hadm_id`, `next_admittime` 180,733. |
| `data/raw/longitudinal/d_labitems.parquet` | 1,622 x 4 | `itemid` (1,622 distinct; unique). | None | `label` has 3 nulls. Dictionary only; it contains no lab results or measurement timestamps. |
| `data/raw/longitudinal/diagnoses_all.parquet` | 4,756,326 x 8 | `subject_id`, `hadm_id`; code-row key (`hadm_id`, `icd_code`, `icd_version`, `seq_num`) has no duplicates. | `admittime`, `dischtime` | No nulls. Repeated patient/admission IDs are expected because this is code-level data. Includes codes and `is_mi_code`. |
| `data/raw/longitudinal/diagnoses_mi_codes.parquet` | 26,824 x 8 | `subject_id`, `hadm_id`; same code-row key has no duplicates. | `admittime`, `dischtime` | No nulls. Includes ICD-9 `412` (old MI) marked `is_mi_code=1`; it is not an acute-only table. |
| `data/raw/longitudinal/lab_coverage_catalogue.parquet` | 26 x 17 | `itemid` (26 distinct; unique). | `earliest_measurement`, `latest_measurement` | `common_unit` has 1 null. Aggregated catalogue only. It has no troponin item among its 26 entries and no row-level values/times. |
| `data/raw/longitudinal/mi_admissions.parquet` | 25,755 x 8 | `subject_id`, `hadm_id` (25,755 distinct; unique admission key). | `admittime` | No nulls. Contains `mi_icd_codes`, sequence counts, and first/recurrent flags; includes historical-code-only admissions (details below). |
| `data/raw/longitudinal/observation_end.parquet` | 180,733 x 7 | `subject_id` (180,733 distinct; unique). | `last_discharge`, `last_admittime`, `in_hospital_deathtime`, `dod`, `observation_end` | `in_hospital_deathtime` 172,141; `dod` 152,753. |
| `data/raw/longitudinal/omr_coverage_catalogue.parquet` | 13 x 7 | `result_name` (13 distinct; unique). | `earliest`, `latest` | No nulls. Aggregate coverage only. |
| `data/raw/longitudinal/patients_demographics.parquet` | 299,712 x 6 | `subject_id` (299,712 distinct; unique). | `dod` | `dod` has 270,636 nulls. |
| `data/raw/longitudinal/vitals_coverage_catalogue.parquet` | 14 x 9 | `itemid` (14 distinct; unique). | None | `mean_value` and `median_value` each have 1 null. Aggregate coverage only. |
| `data/raw/master_dataset/train.parquet` | 262,813 x 184 | `study_id` (262,813 distinct; 0 duplicates); `SubjectID` (69,479 distinct; 193,334 repeats); `hadm_id` (133,771 distinct; 129,042 repeats); 129,042 repeated `(SubjectID, hadm_id)` rows. | `ecg_time`, `index_mi_time`, `time_diff_hours` | `index_mi_time` 229,005 null; all other columns have zero nulls. |
| `data/raw/master_dataset/validation.parquet` | 56,319 x 184 | `study_id` (56,319 distinct; 0 duplicates); `SubjectID` (14,888 distinct; 41,431 repeats); `hadm_id` (28,676 distinct; 27,643 repeats); 27,643 repeated `(SubjectID, hadm_id)` rows. | `ecg_time`, `index_mi_time`, `time_diff_hours` | `index_mi_time` 49,064 null; all other columns have zero nulls. |
| `data/raw/master_dataset/test.parquet` | 56,798 x 184 | `study_id` (56,798 distinct; 0 duplicates); `SubjectID` (14,889 distinct; 41,909 repeats); `hadm_id` (28,922 distinct; 27,876 repeats); 27,876 repeated `(SubjectID, hadm_id)` rows. | `ecg_time`, `index_mi_time`, `time_diff_hours` | `index_mi_time` 49,631 null; all other columns have zero nulls. |

For `diagnoses_all` and `diagnoses_mi_codes`, `subject_id` and `hadm_id` repeat by design; the tested code-row key has zero duplicates. The other catalogue/demographic/summary tables have zero duplicates on their listed key. Master `study_id` values are unique within and across splits. Patient and study IDs do not overlap across train, validation, and test.

## Exact longitudinal schemas

- `admissions_chronology.parquet`: `subject_id`, `hadm_id`, `admittime`, `dischtime`, `deathtime`, `edregtime`, `edouttime`, `admission_type`, `admission_location`, `discharge_location`, `insurance`, `race`, `hospital_expire_flag`, `admission_seq`, `previous_hadm_id`, `previous_dischtime`, `next_hadm_id`, `next_admittime`, `anchor_time`, `total_admissions`.
- `d_labitems.parquet`: `itemid`, `label`, `fluid`, `category`.
- `diagnoses_all.parquet` and `diagnoses_mi_codes.parquet`: `subject_id`, `hadm_id`, `icd_code`, `icd_version`, `seq_num`, `admittime`, `dischtime`, `is_mi_code`.
- `lab_coverage_catalogue.parquet`: `itemid`, `lab_name`, `fluid`, `category`, `total_measurements`, `unique_patients`, `unique_admissions`, `cohort_patients`, `cohort_measurements`, `earliest_measurement`, `latest_measurement`, `mean_value`, `median_value`, `std_value`, `min_value`, `max_value`, `common_unit`.
- `mi_admissions.parquet`: `subject_id`, `hadm_id`, `mi_icd_codes`, `min_seq_num`, `admittime`, `mi_admission_seq`, `total_mi_admissions`, `is_first_mi_admission`.
- `observation_end.parquet`: `subject_id`, `last_discharge`, `last_admittime`, `in_hospital_deathtime`, `dod`, `is_dead`, `observation_end`.
- `omr_coverage_catalogue.parquet`: `result_name`, `total_records`, `unique_patients`, `cohort_patients`, `cohort_records`, `earliest`, `latest`.
- `patients_demographics.parquet`: `subject_id`, `gender`, `anchor_age`, `anchor_year`, `anchor_year_group`, `dod`.
- `vitals_coverage_catalogue.parquet`: `itemid`, `vital_name`, `total_records`, `unique_patients`, `unique_admissions`, `cohort_admissions`, `cohort_records`, `mean_value`, `median_value`.

## Master schema and contents

All three splits have the same 184 columns:

- Identifiers, labels, and timing (8): `study_id`, `SubjectID`, `hadm_id`, `ecg_time`, `Label_Troponin`, `is_MI`, `index_mi_time`, `time_diff_hours`.
- Latent values (64): `z_ecg_1` through `z_ecg_64`. All are present and non-null in every split.
- Handcrafted ECG values (95): `QRS_Dur_Global`, `QRS_Dur_Global_iqr`, `QRS_Dur_Global_count`, `RR_Mean_Global`, `RR_Mean_Global_iqr`; `S_Amp_V1`, `S_Amp_V1_iqr`, `S_Amp_V2`, `S_Amp_V2_iqr`, `S_Amp_V3`, `S_Amp_V3_iqr`; and, for each lead `I`, `II`, `III`, `aVR`, `aVL`, `aVF`, `V1`, `V2`, `V3`, `V4`, `V5`, `V6`, `Q_Amp_<lead>`, `Q_Amp_<lead>_iqr`, `R_Amp_<lead>`, `R_Amp_<lead>_iqr`, `T_Amp_<lead>`, `T_Amp_<lead>_iqr`, and `ST_Elev_<lead>`. All 95 have zero nulls.
- Clinical/demographic values (17): `diabetes`, `hypertension`, `ckd`, `prior_mi`, `statin_before`, `statin_during`, `statin_after`, `beta_blocker_before`, `beta_blocker_during`, `acei_before`, `acei_during`, `aspirin_before`, `aspirin_during`, `vasopressor_during`, `mech_vent_during`, `anchor_age`, `sex_male`. All have zero nulls.

The master contains core diagnosis-based risk flags, age, sex, and treatment indicators. `race` is available by joining `hadm_id` to `admissions_chronology`; it is not a master column. The full diagnosis table and admission sequence fields can support prior-admission history and utilization. Smoking, row-level lipids, and row-level troponin are not in the master.

The master has 95 ECG columns as documented in Phase F. The separate definitive extraction list in `docs/final_features_to_extract.txt` has 159 entries (53 base measures times mean/IQR/count); 95 overlap with the master and 64 listed variants do not. Missing variants are mostly count fields and ST-elevation IQR/count fields. Those 64 are not required to use the 95-column Phase F schema, but they would need extraction if the 159-column specification is intended.

## Labels and temporal integrity

Across all splits the labels are `Control_Symptomatic` (362,372), `MI_Acute_Presentation` (7,604), and `MI_Pre-Incident` (5,954). `is_MI` is true for both MI labels (13,558 total) and false for controls. There are no `MI_Post-Incident` rows.

The documented definition is troponin-based: first value above an assay-specific 99th-percentile URL defines `index_mi_time`; the pipeline describes acute-presentation ECGs as -6 to +2 hours relative to that time. The pipeline and `post_incident_analysis.md` disagree on the pre-incident cutoff (>2 hours before versus < -6 hours). The threshold table and label-generation script are absent, so the exact labels cannot be independently reproduced from this repository.

The master mapping is internally coherent with the available admissions: all 375,930 `hadm_id` values join to chronology, with zero patient-ID mismatches and no missing `ecg_time`. In total, 109,148 ECGs before inpatient `admittime` fall between ED registration and inpatient admission; 167 precede ED registration and 122 are after discharge. Pre-admission ECG timestamps therefore are not automatically mapping errors, but the edge cases merit review.

The important failure is event time. Of 7,604 acute-presentation rows, 3,053 (40.2%) have null `index_mi_time`. `time_diff_hours` is non-null even for those rows, but for all 3,053 it equals `ecg_time - anchor_time` (admission/ED anchor), not an MI-event difference. For the other 4,551 acute rows, the stored difference agrees with `ecg_time - index_mi_time` within 0.01 hour. The null-onset acute rows cannot be classified before/after MI onset from the master. Do not treat their `time_diff_hours` as event-relative.

The ICD-derived MI set has a separate case-definition issue. `diagnoses_all` contains acute and historical codes and supports their separation by `icd_version` and `icd_code`: acute patterns are ICD-9 `410*` and ICD-10 `I21*`/`I22*`; historical codes include ICD-9 `412` and ICD-10 `I25.2`. But `diagnoses_mi_codes.parquet` marks all 14,343 `412` rows as MI, while `I25.2` is excluded from that derivative. `mi_admissions.parquet` consequently has 13,568 admissions without an accepted acute pattern, including 13,565 with `412` only. The existing `extract_comorbidities.py` rule for `prior_mi` also omits ICD-10 `I25.2`; regenerate prior-MI history from `diagnoses_all` using an explicit historical-code rule. Use `diagnoses_all` with explicit code rules; do not use `is_mi_code` or `mi_admissions` as an acute-only outcome without regeneration.

## Model, script, and archive inventory

- Present scripts: `src/models/train_vae.py`, `vae_conv1d.py`, `extract_embeddings.py`, `validate_embeddings.py`, baseline training/calibration scripts, `src/features/build_master_dataset.py`, `src/features/extract_comorbidities.py`, `src/features/fix_temporal_features.py`, `scripts/extract_cohort.py`, and root `extract_ecg_features.m`.
- Config/log artifacts: `1.preprocessing/preprocessing_pipeline/config.yaml`, `2.analysis_and_validation/config.yaml`, `1.preprocessing/preprocessing_pipeline/outputs/logs/preprocessing_20260802_155708.log`, baseline `results.json` and `calibration_results.json`, and VAE configuration/results documentation in `docs/VAE Embedding Pipeline.md`. No run-specific VAE training log or persisted VAE configuration file was found.
- Present model outputs: eight baseline pickle files (clinical logistic regression, XGBoost all-feature, ECG-plus-clinical, and embedding-plus-clinical, each calibrated and uncalibrated), plus baseline result/calibration JSON and plots.
- No beta-VAE checkpoint exists; `models/checkpoints/` contains only `.gitkeep`. The 64 latent columns exist only inside the master Parquets; separate `data/modeling/ecg_embeddings/*.csv` outputs are absent. No VAE run log or per-run provenance file was found. VAE architecture/training settings and claimed training results exist in `docs/VAE Embedding Pipeline.md`, but that document is not a checkpoint or run log.
- ECG feature extraction code exists, but its referenced ECG mapping, waveform tree, and output CSV are absent. No `.hea`, `.dat`, HDF5 signal file, or extracted ECG feature source CSV was found in the repository.
- `research_audit/phase1_2_audit.py` is not a data audit runner in its current form: it expects `data/modeling/...` paths and writes placeholder zero/"not assessed" results. The actual masters are under `data/raw/master_dataset/`.
- `hosp.rar` members: `emar.csv`, `omr.csv`, `patients.csv`, `prescriptions.csv`, `admissions.csv`.
- `icu.rar` members: `d_items.csv`, `inputevents.csv`, `procedureevents.csv`, `chartevents.csv`.
- Neither archive contains `labevents.csv`, `diagnoses_icd.csv`, or MIMIC-IV-ECG signal/record files. The code-level diagnosis Parquet is an existing derivative equivalent for diagnosis-code analyses; `d_labitems.parquet` is an existing lab dictionary equivalent. No archive was extracted.
- Newly supplied `data/raw/labevents.rar` contains `labevents.csv` (16-column header; 118,171,367 data rows; 13.73 GB uncompressed). Full extraction was not possible with 11.85 GB free on C:. The archive was preserved and streamed read-only; the three configured item IDs yielded 359,163 records in `research_audit/artifacts/troponin_measurements.csv`.
- Newly supplied `data/raw/troponin_thresholds.jpeg` is an image of a 3-row table, not a CSV. Its seven columns and values were transcribed to `research_audit/artifacts/troponin_thresholds.csv`; the table has no assay-specific bibliographic citation and remains provisional after comparison with observed units/reference ranges.

See [MISSING_ARTIFACTS.csv](MISSING_ARTIFACTS.csv) for action and blocker status, and [DATASET_READINESS_REPORT.md](DATASET_READINESS_REPORT.md) for the minimum restoration list.