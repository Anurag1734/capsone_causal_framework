# Dataset Readiness Report

## Decision

**Not ready for a complete Phase 1-2 causal audit.** The workspace is materially more complete than the older feasibility report states: three master Parquets and ten longitudinal Parquets are present, as are code-level diagnosis history, admission chronology, 95 handcrafted ECG columns, 64 latent columns, and baseline model artifacts.

Phase 1's admission-level ICD analysis can be rerun from the current diagnosis and chronology Parquets after correcting the acute-versus-history code filter. The primary Phase 1 Layer 2 / Phase 2 MI-to-ECG temporal analysis is blocked because event-onset timestamps are missing for 3,053 acute-labeled ECGs, and the raw lab events and threshold table needed to reconstruct them are absent. The beta-VAE remains secondary and ineligible for causal use because its checkpoint and run provenance are absent, despite embeddings being present in the masters.

No causal effect was estimated. This report does not rebuild data, models, or labels.

## What is present

- 13 Parquet files: master train (262,813 rows), validation (56,319), test (56,798); 431,231 admissions in chronology; 4,756,326 diagnosis-code rows; demographics, observation-end data, code dictionary, MI-code derivatives, and aggregate lab/OMR/vital coverage catalogues.
- Every master ECG has a unique `study_id`, non-null patient/admission IDs, non-null `ecg_time`, all 95 Phase F ECG feature fields, all 64 `z_ecg_*` fields, and non-null clinical/demographic fields. Features and embeddings have zero null cells.
- All master patient IDs and ECG IDs are disjoint across the three splits. Patient/admission IDs repeat within splits because an admission/patient can have multiple ECG records.
- All 375,930 master admission IDs match `admissions_chronology`; there are no patient-ID mismatches. Most ECG timestamps before inpatient admission are between ED registration and inpatient admission, consistent with ED acquisition. 167 ECGs precede ED registration and 122 follow discharge and should be treated as edge cases.
- Age, sex, diabetes, hypertension, CKD, prior-MI, and treatment indicators exist in the masters. Admission race and prior/total admission sequence are available in chronology. The master has no row-level troponin, lipid, or smoking variables.
- `diagnoses_all.parquet` preserves ICD code, version, sequence, admission, and admission-time fields, enabling acute/history rules and prior-admission ordering without restoring `diagnoses_icd.csv` if the derivative is accepted.

## Blocking findings

### Event time and master labels

The masters have 7,604 `MI_Acute_Presentation` ECGs. Only 4,551 have `index_mi_time`; 3,053 (40.2%) do not. Their `time_diff_hours` fields are not evidence of event timing: for every one of those 3,053 records, the value equals `ecg_time - anchor_time`, where the anchor is the admission/ED time. For the 4,551 acute records with an event timestamp, `time_diff_hours` matches `ecg_time - index_mi_time` within 0.01 hour.

Therefore, the current master can support a partial before/after/uncertain timing check, not a complete onset-relative analysis. The intended troponin rule depends on an assay/year/sex-specific URL and first above-URL lab charttime; neither row-level `labevents.csv` nor the specified `troponin_thresholds.csv` is available. The lab coverage catalogue is aggregate-only and does not include troponin among its 26 items.

The label names and counts are present, but not their reproducible provenance. `Label_Troponin` has 362,372 controls, 7,604 acute-presentation, and 5,954 pre-incident ECGs; `is_MI` combines both MI classes and is not an acute-only outcome. The pipeline documents acute as -6 to +2 hours, but its pre-incident cutoff conflicts with `post_incident_analysis.md` (>2 hours before versus < -6 hours). The observed pre-incident `time_diff_hours` values are all below -6 hours. Treat the labels as existing classifications, not independently validated event definitions.

### ICD acute versus historical MI

The ICD code values do distinguish acute from historical MI, but current derived flags do not do so reliably. In `diagnoses_mi_codes.parquet`, all 14,343 ICD-9 `412` (old MI) rows are marked `is_mi_code=1`. `mi_admissions.parquet` consequently contains 13,565 admissions with `412` and no accepted acute `410*`/`I21*`/`I22*` code, plus three more admissions without those acute patterns. ICD-10 `I25.2` appears in `diagnoses_all` but not the MI-code derivative.

Use the full `diagnoses_all` table and explicitly define current acute events as ICD-9 `410*` or ICD-10 `I21*`/`I22*`, excluding ICD-9 `412` and ICD-10 `I25.2`. Regenerate the derived acute cohort and history flags before Phase 1 Layer 1; do not use `is_mi_code` or `mi_admissions` as an acute-only outcome. The diagnosis rows are admission-level, not diagnosis-charttime-level; a strict prior-admission rule can be applied, but finer same-admission diagnosis timing cannot be inferred.

### Feature scope and beta-VAE

The masters have the requested 95 ECG feature columns and all 64 latent values. They are non-null, and `study_id` links them to the ECG-level rows. The extraction-list document has 159 fields; 64 of those are not in the master schema. The separate ECG feature/embedding CSVs are absent, but are not needed to inspect the existing master fields.

The 64 z values do not prove the provenance of the beta-VAE. No VAE checkpoint, raw waveform/HDF5 store, separate embedding output, or run-specific training log/metadata was found. Existing baseline XGBoost embedding models are not VAE checkpoints. Keep the latent dimensions out of causal analysis unless the original checkpoint, cohort/split, and extraction provenance can be restored and verified.

## Other artifact findings

- Baseline models and their results exist: clinical logistic regression and three XGBoost feature families, each calibrated/uncalibrated, with result and calibration JSONs and plots.
- VAE training, architecture, extraction, and validation scripts exist. ECG feature extraction code exists (`extract_ecg_features.m`), as do cohort/comorbidity/master-building scripts. The original source tables/waveforms those scripts reference are not all in the workspace.
- `hosp.rar` contains `emar.csv`, `omr.csv`, `patients.csv`, `prescriptions.csv`, and `admissions.csv`. `icu.rar` contains `d_items.csv`, `inputevents.csv`, `procedureevents.csv`, and `chartevents.csv`. Neither archive was extracted. Neither includes `labevents.csv` or the ECG source files.
- `research_audit/phase1_2_audit.py` currently checks obsolete `data/modeling` paths and writes zero/"not assessed" placeholders; it does not execute the required audits. Existing Phase 1-2 status documents that claim the Parquets are absent are stale relative to this inventory.

## Minimum files and actions before rerun

For the primary temporal MI-to-ECG audit, restore or obtain through the authorized source:

1. `data/raw/MIMIC-IV-2.2/hosp/labevents.csv` (or the equivalent authorized row-level MIMIC-IV lab extract), with `subject_id`, `hadm_id`, `itemid`, `charttime`, and lab value fields. It is absent from both the repository and `hosp.rar`.
2. `troponin_thresholds.csv` with the documented assay/year/sex URL fields, or regenerate this table from a cited, validated threshold source. It is absent from the repository. `d_labitems.parquet` already supplies the lab item dictionary and need not be restored.

Then regenerate an audit-only onset table and acute labels/timing checks from the restored lab input and the existing master `study_id`, `SubjectID`, `hadm_id`, and `ecg_time`. Do not rebuild the master datasets for this task. Review the 167 pre-ED and 122 post-discharge ECG mapping edge cases. Update the Phase 1-2 audit runner to read `data/raw/longitudinal/` and `data/raw/master_dataset/` and perform real checks.

For Phase 1 Layer 1, no raw diagnosis CSV restore is the minimum: use `diagnoses_all.parquet` plus `admissions_chronology.parquet` and `patients_demographics.parquet`, but regenerate the acute/history code flags as above. For secondary beta-VAE work only, additionally restore the original `models/checkpoints/<run>/best_model.pt`, run-specific training/provenance logs, and raw ECG waveform data (or the exact HDF5 input used). These beta-VAE files are not blockers to the primary handcrafted-feature analysis and should not be recreated by retraining as part of this inventory.

Full row counts, schemas, missingness, duplicate checks, archive listings, and file searches are in [EXISTING_DATASET_INVENTORY.md](EXISTING_DATASET_INVENTORY.md). Artifact-by-artifact decisions are in [MISSING_ARTIFACTS.csv](MISSING_ARTIFACTS.csv).