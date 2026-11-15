# Phase 3 Analysis Dataset Report

## Dataset created

**Path:** `data/analysis/observational_mi_ecg/analysis_dataset.parquet`  
**Shape:** 191,275 rows × 115 columns  
**Unit:** one selected ECG per admission  
**Patients:** 99,214  
**Admissions:** 191,275 unique  
**ECG IDs:** 191,275 unique  
**Handcrafted features:** 95; all finite and nonmissing in all selected rows.

The primary analysis subset is marked by `primary_analysis_eligible`: 167,066 admissions from 93,946 patients, comprising 7,353 acute-diagnosis cases and 159,713 clean comparisons. Historical/prior MI admissions without an acute code remain in the dataset as a separate sensitivity group (24,209 admissions).

## Contents

The dataset includes:

- `patient_id`, `admission_id`, `ecg_id`, `ecg_time`, and `source_master_split`.
- `ecg_count_in_admission`, `ecg_selection_rank`, and `ecg_selection_rule`.
- `acute_mi_diagnosis`, `historical_mi_this_admission`, `historical_mi_documented`, `prior_mi`, `diabetes_prior`, `hypertension_prior`, and `ckd_prior`.
- `age_years`, recorded `sex`, `mi_diagnosis_group`, `primary_analysis_eligible`, and `feature_complete`.
- All 95 existing handcrafted features. Feature families are enumerated in [`PHASE3_ECG_FEATURE_GROUPS.csv`](./PHASE3_ECG_FEATURE_GROUPS.csv); full descriptions and missingness appear in [`PHASE3_VARIABLE_DICTIONARY.csv`](./PHASE3_VARIABLE_DICTIONARY.csv).

`QRS_Dur_Global_count` is labeled technical/support information, not a physiological outcome. The other features are grouped as ST, Q, R, T, QRS, RR, or S-wave/other morphology. Units remain as stored in the master and were not independently revalidated.

## Exclusions and quality checks

- 375,930 master ECG rows were inspected. In 56 rows, ED registration was after discharge and was treated as invalid; inpatient admission was used as the lower bound. In 54 rows the admission start still followed discharge, so those invalid episode rows were excluded. Overall, 375,642 ECG rows fell within valid ED/admission-to-discharge intervals and 288 out-of-interval rows were excluded.
- The selected set has exactly one row per admission and one occurrence per ECG ID. Repeated patients across different admissions remain.
- Admission/patient IDs match the chronology; all diagnosis audit rows join one-to-one.
- No feature, selected identifier, age, sex, or diagnosis/history variable is missing in the selected dataset. All 191,275 rows have all 95 feature values finite.
- No troponin label, threshold, `index_mi_time`, or pre-/post-event class is included.
- β-VAE dimensions are omitted due unresolved training/extraction provenance.
- Original train/validation/test masters and diagnosis Parquets were not changed.

The complete machine-readable checks are in `data/analysis/observational_mi_ecg/data_quality_checks.csv` and `dataset_missingness.csv`. Cohort counts are in `cohort_counts.csv`.

## Reproducibility

Run from the repository root:

```powershell
python research_audit\build_phase3_observational_dataset.py
```

The script reads the three existing master splits, `admissions_chronology.parquet`, `patients_demographics.parquet`, and the completed `ACUTE_MI_DIAGNOSIS_BY_ADMISSION.csv`. It writes a new Parquet, manifest, counts, missingness, and selection diagnostics under `data/analysis/observational_mi_ecg/`, plus the feature dictionary and feature-group CSV under `research_audit/`. It validates join cardinality, patient/admission identity, the 95-feature count, and one selected ECG per admission.

The output SHA-256 is `4e76c9575b40687e2c7014844482075e943931bf4aa19e257349e6ec3695149d`; it is also recorded in `data/analysis/observational_mi_ecg/dataset_manifest.json`. The repository ignores `data/` as a local/private dataset, so the Parquet and generated machine-readable diagnostics remain local; keep the script and report with the project code.
