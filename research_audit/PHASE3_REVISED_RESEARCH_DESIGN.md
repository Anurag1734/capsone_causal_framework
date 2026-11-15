# Phase 3 Revised Research Design

## Research direction

The primary study is an **adjusted observational association study**, not a causal analysis:

> Among adult MIMIC-IV hospital admissions with an in-encounter ECG, how are acute MI diagnoses recorded during the admission associated with ECG morphological features after adjustment for selected, previously documented patient characteristics?

No biological MI onset, pre-/post-MI ECG status, or causal effect is identified. The exposure is an acute ICD diagnosis during the admission, not a troponin threshold or ECG label.

## Questions

- **Primary:** What are the adjusted associations of acute MI diagnosis with each of the 95 handcrafted ECG features?
- **Secondary:** Which ST, Q, R, T, QRS, RR, and other morphology groups show the largest associations? Does a group-level omnibus test support heterogeneity across feature families?
- **Latent features:** The 64 β-VAE columns occur in the existing master but are excluded because their checkpoint, training cohort, and extraction provenance cannot be validated. Revisit only after provenance is supplied.
- **Sensitivity:** How do estimates change when historical/prior MI admissions are retained as a separate group, all nonacute admissions are used as controls, the acute definition is restricted to principal diagnoses, or all ECGs are analyzed with patient clustering?
- **Selection:** How do admissions with and without an eligible ECG differ, and are selection weights a credible sensitivity analysis for a broader admission target?

## Population and analysis unit

Use the corrected ICD admission audit. Acute MI is ICD-9 410* or ICD-10 I21*/I22*. Historical MI is ICD-9 412 or ICD-10 I25.2 and is never relabeled acute solely because it is an MI code.

The primary unit is **one admission with one selected ECG**. Select the earliest master ECG in the ED-registration-to-discharge interval; if ED registration is absent, use admission-to-discharge. Break timestamp ties by the lowest `study_id`. This deterministic rule is independent of feature values, diagnosis labels, and hypothesis direction. It gives each admission equal representation and avoids treating repeated ECGs as independent observations. Repeated admissions per patient remain and inference must cluster by patient.

The primary comparison uses acute-coded admissions versus nonacute admissions with no documented current or prior MI. Nonacute admissions with a current historical MI code or a prior MI code remain in the constructed dataset as a distinct sensitivity group, rather than being mislabeled acute or silently mixed into the primary controls. Acute cases with prior MI remain cases; prior MI is a candidate adjustment variable.

## Confounding and selection framework

The analysis targets a conditional association among admissions with an eligible ECG. A confounding framework—not a causal effect claim—is:

```text
Age, sex, prior diabetes, prior hypertension, prior CKD, prior MI
      ↘ likelihood of an acute MI diagnosis
      ↘ ECG morphology

Acute diagnosis, clinical severity, care pathways, and ECG abnormalities
      ↘ ECG acquisition / inclusion in the observed ECG cohort
```

Diagnosis and ECG are observed during the same admission, and their temporal ordering is not established. Therefore, no directional causal arrow from diagnosis to feature is asserted. Conditioning on ECG acquisition can induce selection bias; severity, indication, care access, and other unmeasured determinants may remain.

Use age and recorded sex as adjustment variables, never as interventions. Candidate history covariates are prior-admission diabetes, hypertension, CKD, and MI flags. These flags represent documented inpatient history, not verified absence of disease. Define a feature/group-specific adjustment set from the prespecified confounder framework before fitting outcome models; do not mechanically apply one universal set. Same-admission treatments and diagnoses are not baseline covariates.

Unavailable or not yet joined confounders include smoking and lipids. BMI is listed in the OMR coverage catalogue, but patient-level OMR rows are not in the analysis-ready Parquets; the source archive contains OMR data that have not been joined. Do not treat these as observed baseline values until their timing and linkage are established.

## Dataset and feature handling

The separate dataset is `data/analysis/observational_mi_ecg/analysis_dataset.parquet`. It contains identifiers, selected-ECG metadata, diagnosis/history flags, age, sex, and all 95 handcrafted features. It excludes troponin-derived labels/times and the 64 β-VAE dimensions. See [`PHASE3_ANALYSIS_DATASET_REPORT.md`](./PHASE3_ANALYSIS_DATASET_REPORT.md), [`PHASE3_VARIABLE_DICTIONARY.csv`](./PHASE3_VARIABLE_DICTIONARY.csv), and [`PHASE3_ECG_FEATURE_GROUPS.csv`](./PHASE3_ECG_FEATURE_GROUPS.csv).

Group the features into ST, Q, R, T, QRS, RR, S-wave/other morphology, and technical measurement support. `QRS_Dur_Global_count` is a technical support/count measure, not a physiological morphology outcome. Keep it separate in interpretation. No feature is removed based on observed association.

## Troponin and prior labels

The supplied item thresholds remain unchanged and provisional. They are not used in cohort construction, exposure classification, event timing, ECG selection, or the primary dataset. No ECG is categorized as pre-MI or post-MI. Any future threshold-based analysis must be clearly labeled exploratory and must not validate timing or MI diagnosis.

## Readiness

The analysis-ready admission dataset, feature map, cohort counts, missingness checks, and selection diagnostics have been produced. The project is ready for **Phase 4 adjusted association estimation**, subject to locking the feature/group-specific adjustment sets and following [`PHASE3_STATISTICAL_ANALYSIS_PLAN.md`](./PHASE3_STATISTICAL_ANALYSIS_PLAN.md). It is not ready for causal-effect estimation or event-relative ECG analysis.
