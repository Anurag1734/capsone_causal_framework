# Phase 3 Completion Report

## Decision

**Phase 3 dataset construction and statistical planning are complete. The project is ready to proceed to Phase 4: adjusted observational association analysis, subject to locking the feature/group-specific adjustment sets before estimating outcomes.**

This is not approval for causal MI-effect estimation, threshold-based event timing, or pre-/post-MI comparisons. Results must be reported as adjusted associations.

## Deliverables

1. [`PHASE3_REVISED_RESEARCH_DESIGN.md`](./PHASE3_REVISED_RESEARCH_DESIGN.md)
2. [`PHASE3_STUDY_COHORT_DEFINITION.md`](./PHASE3_STUDY_COHORT_DEFINITION.md)
3. [`PHASE3_VARIABLE_DICTIONARY.csv`](./PHASE3_VARIABLE_DICTIONARY.csv)
4. [`PHASE3_ECG_FEATURE_GROUPS.csv`](./PHASE3_ECG_FEATURE_GROUPS.csv)
5. [`PHASE3_SELECTION_BIAS_REPORT.md`](./PHASE3_SELECTION_BIAS_REPORT.md)
6. [`PHASE3_ANALYSIS_DATASET_REPORT.md`](./PHASE3_ANALYSIS_DATASET_REPORT.md)
7. [`PHASE3_STATISTICAL_ANALYSIS_PLAN.md`](./PHASE3_STATISTICAL_ANALYSIS_PLAN.md)
8. This completion report.

The separate dataset is `data/analysis/observational_mi_ecg/analysis_dataset.parquet`; its reproducible builder is [`build_phase3_observational_dataset.py`](./build_phase3_observational_dataset.py).

## Completion criteria

| Item | Result |
|---|---|
| Study population | Adult MIMIC-IV admissions with an ECG in the defined ED/admission-to-discharge interval. |
| Comparison | Acute ICD-coded MI versus nonacute admissions with no documented current/prior MI; historical/prior MI without acute MI retained as a separate sensitivity group. |
| Analysis unit | One deterministic earliest in-encounter ECG per admission. |
| Full ECG cohort | 191,275 admissions, 99,214 patients, and 191,275 selected ECGs. |
| Primary binary cohort | 167,066 admissions from 93,946 patients: 7,353 acute MI cases and 159,713 comparisons. |
| Feature availability | 95 handcrafted features; all 191,275 selected records are finite and complete. |
| Adjustment-variable availability | Age, sex, prior diabetes, hypertension, CKD, and prior MI indicators have no missing values in the constructed set; diagnosis-history indicators remain subject to undercoding. |
| ECG selection | 191,275 of 431,231 adult admissions have an eligible master ECG (44.36%); measured selection differences are material. Weighting is plausible to evaluate as sensitivity, not a guaranteed correction. |
| β-VAE | 64 latent dimensions excluded due unresolved provenance. |
| Troponin | Supplied thresholds unchanged and not used for primary exposure, cohort, or event timing. |
| Master data/models | Existing splits, diagnosis Parquets, and model artifacts preserved; no retraining. |
| Association results | None estimated or reported in Phase 3. |

## Remaining limitations and Phase 4 guardrails

- Diagnosis codes identify recorded acute MI, not validated biological onset or complete clinical adjudication.
- The selected ECG is within the admission episode, but temporal ordering relative to MI is unknown.
- ECG availability is selective; unmeasured severity, symptoms, clinician decision-making, and access may bias the ECG-only association.
- Prior comorbidities are based on earlier inpatient codes; absence of a code does not establish absence of disease.
- Smoking and lipid data are not analysis-ready; BMI/eGFR OMR coverage is known but row-level values are not linked.
- The 64 β-VAE values remain excluded pending provenance.
- Repeated admissions per patient require patient-clustered inference.
- Lock the feature/group-specific adjustment sets before opening outcome model results and apply the 95-feature multiplicity plan.

## Reproducibility and validation

The builder was syntax-checked and run successfully against the existing master splits and corrected admission audit. It validated one-to-one admission/ECG selection, patient/admission identity, all 95 features, complete feature records, diagnosis-audit coverage, and non-use of troponin timing and latent embeddings. It excluded 288 ECG rows outside valid episode bounds (including 54 rows from invalid admission intervals). Output SHA-256: `4e76c9575b40687e2c7014844482075e943931bf4aa19e257349e6ec3695149d`.

Counts, missingness, selection diagnostics, quality checks, and the dataset manifest are saved under `data/analysis/observational_mi_ecg/`. The source data and original analysis artifacts were not modified.
