from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = REPO_ROOT / "research_audit"
OUTPUT_DIR = AUDIT_ROOT

EXPECTED_ARTIFACTS = {
    "raw_hosp": REPO_ROOT / "data" / "raw" / "hosp.rar",
    "raw_icu": REPO_ROOT / "data" / "raw" / "icu.rar",
    "raw_modeling_labels": REPO_ROOT / "data" / "modeling" / "labels",
    "raw_modeling_master": REPO_ROOT / "data" / "modeling" / "master",
    "ecg_features_dir": REPO_ROOT / "data" / "modeling" / "ecg_features",
    "ecg_embeddings_dir": REPO_ROOT / "data" / "modeling" / "ecg_embeddings",
    "clinical_dir": REPO_ROOT / "data" / "modeling" / "clinical",
    "demographics_dir": REPO_ROOT / "data" / "modeling" / "demographics",
    "mimic_iv_hosp": REPO_ROOT / "data" / "raw" / "MIMIC-IV-2.2" / "hosp",
    "mimic_iv_ecg": REPO_ROOT / "data" / "raw" / "MIMIC-IV-ECG-1.0",
    "mimic_iv_ecg_ext": REPO_ROOT / "data" / "raw" / "MIMIC-IV-ECG-Ext-ICD-1.0.1",
}


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_csv(path: Path, rows: Iterable[dict]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def inventory_repo() -> pd.DataFrame:
    records: List[dict] = []
    for name, path in EXPECTED_ARTIFACTS.items():
        exists = path.exists()
        records.append(
            {
                "artifact": name,
                "path": str(path),
                "exists": exists,
                "status": "present" if exists else "missing",
                "notes": "required for Phase 1-2 audit" if not exists else "found",
            }
        )
    return pd.DataFrame(records)


def create_placeholder_csvs() -> Dict[str, pd.DataFrame]:
    clinical = pd.DataFrame(
        [
            {
                "condition": "Diabetes",
                "eligible_admissions": 0,
                "patients": 0,
                "historically_established": 0,
                "same_admission_only": 0,
                "uncertain_timing": 0,
                "strict_prior_admission_definition": "not assessed",
                "broader_sensitivity_definition": "not assessed",
                "status": "data unavailable in workspace",
            },
            {
                "condition": "Hypertension",
                "eligible_admissions": 0,
                "patients": 0,
                "historically_established": 0,
                "same_admission_only": 0,
                "uncertain_timing": 0,
                "strict_prior_admission_definition": "not assessed",
                "broader_sensitivity_definition": "not assessed",
                "status": "data unavailable in workspace",
            },
            {
                "condition": "CKD",
                "eligible_admissions": 0,
                "patients": 0,
                "historically_established": 0,
                "same_admission_only": 0,
                "uncertain_timing": 0,
                "strict_prior_admission_definition": "not assessed",
                "broader_sensitivity_definition": "not assessed",
                "status": "data unavailable in workspace",
            },
            {
                "condition": "Previous MI",
                "eligible_admissions": 0,
                "patients": 0,
                "historically_established": 0,
                "same_admission_only": 0,
                "uncertain_timing": 0,
                "strict_prior_admission_definition": "not assessed",
                "broader_sensitivity_definition": "not assessed",
                "status": "data unavailable in workspace",
            },
        ]
    )

    mi_audit = pd.DataFrame(
        [
            {"metric": "MI_positive_admissions", "value": 0, "notes": "not assessed"},
            {"metric": "MI_negative_admissions", "value": 0, "notes": "not assessed"},
            {"metric": "ICD9_410_coverage", "value": 0, "notes": "not assessed"},
            {"metric": "ICD10_I21_I22_coverage", "value": 0, "notes": "not assessed"},
            {"metric": "Duplicate_or_multiple_MI_codes", "value": 0, "notes": "not assessed"},
            {"metric": "Transfer_or_continuation_admissions", "value": 0, "notes": "not assessed"},
            {"metric": "MI_label_depends_on_ECG_interpretation", "value": "unknown", "notes": "not assessed"},
            {"metric": "ICD_vs_troponin_disagreement", "value": 0, "notes": "not assessed"},
        ]
    )

    ecg_timing = pd.DataFrame(
        [
            {"category": "Before_MI_onset", "count": 0, "notes": "not assessed"},
            {"category": "After_MI_onset", "count": 0, "notes": "not assessed"},
            {"category": "Uncertain_timing", "count": 0, "notes": "not assessed"},
        ]
    )

    feature_availability = pd.DataFrame(
        [
            {"feature_group": "ST", "feature_count": 0, "missingness": "not assessed", "availability_by_timing": "not assessed", "notes": "not assessed"},
            {"feature_group": "Q", "feature_count": 0, "missingness": "not assessed", "availability_by_timing": "not assessed", "notes": "not assessed"},
            {"feature_group": "R", "feature_count": 0, "missingness": "not assessed", "availability_by_timing": "not assessed", "notes": "not assessed"},
            {"feature_group": "T", "feature_count": 0, "missingness": "not assessed", "availability_by_timing": "not assessed", "notes": "not assessed"},
            {"feature_group": "QRS", "feature_count": 0, "missingness": "not assessed", "availability_by_timing": "not assessed", "notes": "not assessed"},
            {"feature_group": "RR", "feature_count": 0, "missingness": "not assessed", "availability_by_timing": "not assessed", "notes": "not assessed"},
            {"feature_group": "Signal_quality_stats", "feature_count": 0, "missingness": "not assessed", "availability_by_timing": "not assessed", "notes": "not assessed"},
        ]
    )

    beta_vae = pd.DataFrame(
        [
            {"check": "training_checkpoint_identity", "status": "not assessed", "evidence": "not available"},
            {"check": "training_cohort_and_split", "status": "not assessed", "evidence": "not available"},
            {"check": "acute_MI_ECGs_in_training", "status": "not assessed", "evidence": "not available"},
            {"check": "embedding_extraction_procedure", "status": "not assessed", "evidence": "not available"},
            {"check": "deterministic_latent_means_used", "status": "not assessed", "evidence": "not available"},
            {"check": "patient_and_ECG_mapping_integrity", "status": "not assessed", "evidence": "not available"},
            {"check": "missingness_and_variance", "status": "not assessed", "evidence": "not available"},
            {"check": "primary_causal_analysis_eligibility", "status": "excluded", "evidence": "insufficient provenance evidence in workspace"},
        ]
    )

    selection = pd.DataFrame(
        [
            {"metric": "available_selection_predictors", "value": "not assessed", "notes": "required patient-admission-level data absent"},
            {"metric": "missingness", "value": "not assessed", "notes": "required patient-admission-level data absent"},
            {"metric": "overlap_positivity", "value": "not assessed", "notes": "required patient-admission-level data absent"},
            {"metric": "extreme_weight_risk", "value": "not assessed", "notes": "required patient-admission-level data absent"},
            {"metric": "important_unmeasured_selection_factors", "value": "not assessed", "notes": "required patient-admission-level data absent"},
            {"metric": "ipw_feasibility", "value": "not currently feasible", "notes": "required data absent"},
        ]
    )

    counts = pd.DataFrame(
        [
            {"metric": "unique_patients", "value": 0, "notes": "workspace data unavailable"},
            {"metric": "unique_admissions", "value": 0, "notes": "workspace data unavailable"},
            {"metric": "total_ecgs", "value": 0, "notes": "workspace data unavailable"},
            {"metric": "MI_positive_counts", "value": 0, "notes": "workspace data unavailable"},
            {"metric": "MI_negative_counts", "value": 0, "notes": "workspace data unavailable"},
            {"metric": "patient_count_train_split", "value": 0, "notes": "workspace data unavailable"},
            {"metric": "patient_count_validation_split", "value": 0, "notes": "workspace data unavailable"},
            {"metric": "patient_count_test_split", "value": 0, "notes": "workspace data unavailable"},
            {"metric": "admissions_per_patient", "value": 0, "notes": "workspace data unavailable"},
            {"metric": "patient_overlap_across_splits", "value": "not assessed", "notes": "workspace data unavailable"},
            {"metric": "admission_level_analysis_dataset", "value": "not available", "notes": "workspace data unavailable"},
        ]
    )

    return {
        "clinical_diagnosis_timing": clinical,
        "acute_mi_outcome_audit": mi_audit,
        "ecg_temporal_audit": ecg_timing,
        "ecg_feature_availability": feature_availability,
        "beta_vae_provenance": beta_vae,
        "selection_feasibility": selection,
        "cohort_counts_and_splits": counts,
    }


def write_phase1_estimands() -> None:
    text = """# PHASE 1 — CAUSAL ESTIMANDS

## Decision status

This workspace does not contain the underlying MIMIC-IV, MIMIC-IV-ECG, or modeling parquet artifacts required to finalize numeric estimands. The document below is therefore the required audit specification to be executed once the source datasets are available in the project data directory.

## Layer 1: Clinical risk factors -> Acute MI

### 1. Exposure: Diabetes
- Exposure: historical diabetes diagnosis before the current admission.
- Outcome: acute MI admission (ICD-9 410* / ICD-10 I21* or I22* acute MI, excluding 412 and I25.2) during the index encounter.
- Target population: adult hospital admissions with at least one index admission in the source data and a valid hospital admission time.
- Unit of analysis: admission, with prior diabetes status assigned at admission start.
- Adjustment variables: age, sex, race/ethnicity, chronic comorbidity burden, prior healthcare utilization, indicators of baseline cardiovascular risk, and other diabetes-relevant confounders defined from pre-admission data only.
- Variables not to adjust for: post-exposure diagnostics, acute markers tied to the same admission, troponin labels, and downstream interventions or treatment changes.
- Temporal ordering: historical diabetes diagnosis must precede the index admission; no same-admission coding is counted as prior exposure.
- Assumptions: no unmeasured confounding after measured adjustment; positivity; no collider bias from hospital selection; stable unit treatment value within admission-level cohort.
- Biases: confounding by severity of underlying disease, healthcare contact intensity, and detection bias from diagnostic coding.
- Identifiability: partially identifiable using the available MIMIC-IV clinical data if prior diagnosis timing is well documented; otherwise only a descriptive association is defensible.

### 2. Exposure: Hypertension
- Exposure: prior hypertension diagnosis before the index admission.
- Outcome: acute MI during the same admission.
- Target population: adult admissions meeting the same inclusion criteria as Layer 1.
- Unit: admission.
- Adjustment: age, sex, baseline CKD, diabetes, cardiovascular history, and relevant comorbidity burden measured before the admission.
- Not to adjust: acute clinical deterioration, in-hospital treatments, troponin-derived labels, or any variable affected by the onset of MI.
- Temporal ordering: diagnosis date must precede the admission or be assigned to a prior period.
- Assumptions and biases: same as above, with extra attention to early detection and coding intensity.
- Identifiability: partially identifiable only when high-quality prior-diagnosis timestamps exist.

### 3. Exposure: Chronic kidney disease (CKD)
- Exposure: CKD diagnosed before index admission.
- Outcome: acute MI during the current admission.
- Target population: adult index admissions with admission-level denominator.
- Unit: admission.
- Adjustment: age, sex, diabetes, hypertension, prior MI, cardiovascular disease burden, and baseline medication exposures available before the current admission.
- Not to adjust: short-term kidney function changes occurring during the same admission, acute treatment patterns, and troponin-based MI labels.
- Temporal ordering: CKD diagnosis must precede the current admission or be clearly prior by charted diagnosis records.
- Assumptions and biases: survival and detection bias; confounding by frailty and treatment patterns.
- Identifiability: partial at best unless pre-admission CKD timing is well established.

### 4. Exposure: Previous MI
- Exposure: prior documented MI before the current admission.
- Outcome: acute MI in the current admission.
- Target population: adult admissions with a valid index admission and historical diagnostic record.
- Unit: admission.
- Adjustment: age, sex, comorbidity burden, prior cardiovascular events, and baseline risk factors known before the current admission.
- Not to adjust: downstream acute treatment, troponin or ECG indicators, or any variable that is itself a consequence of the current acute event.
- Temporal ordering: prior MI must be documented before the index admission; this exposure is primarily descriptive due to underlying coronary artery disease confounding.
- Assumptions and biases: high chance of residual confounding because prior MI is a marker of underlying coronary disease and risk severity.
- Identifiability: only descriptive or weakly causal without strong assumptions; not a primary causal estimand.

## Layer 2: Acute MI -> ECG changes

- Exposure: acute MI onset (admission-specific acute MI event) measured as an incident acute MI present during the current admission.
- Outcome: ECG morphologic features, particularly ST elevation, Q-wave amplitudes, R-wave amplitudes, T-wave amplitudes, QRS duration, and other valid handcrafted features among the existing 95 features; latent embeddings are secondary and require provenance validation.
- Target population: admissions with a valid acute MI onset time and at least one ECG recorded after the onset, restricted to the admission-level cohort.
- Unit of analysis: ECG-level for the timing audit; admission-level as the final causal unit once timing is established.
- Adjustment variables: age, sex, relevant clinical comorbidities, ECG acquisition context, and measured baseline medical history. These variables must be defined before the relevant ECG acquisition time.
- Variables not to adjust for: troponin-based labels, index_mi_time, post-onset therapeutic interventions, and ECG machine interpretation variables that are consequences of the event or waveform.
- Temporal ordering: ECG must be measured after MI onset for primary analysis; pre-onset ECGs may serve as negative control only if carefully selected.
- Assumptions: measured confounding sufficient for a post-onset analysis; ECG acquisition timing is accurately classifiable; no major selection bias from ECG acquisition; no overlap issues across timing categories.
- Biases: immortal time, selection on ECG availability, time-varying treatment confounding, and ambiguous temporal windows around the event.
- Identifiability: only partially identifiable unless the onset time and ECG timing are valid and acquisition selection is modeled. The handcrafted ECG analysis is the primary allowed avenue; VAE embeddings should remain excluded unless provenance is fully established.

## Required audit checklist before any causal estimation

1. Validate ICD-based MI definitions and exclude old-MI/history codes.
2. Verify all prior diagnoses are recorded before the index admission.
3. Confirm ECG timing relative to the best MI onset evidence and classify before/after/uncertain.
4. Confirm the selected ECG features are physiologic and not signal-quality indicators.
5. Exclude VAE embeddings unless the provenance audit passes.
6. Evaluate ECG acquisition selection bias and positivity before weighting or subset analysis.

"""
    _write_text(AUDIT_ROOT / "PHASE1_CAUSAL_ESTIMANDS.md", text)


def write_phase2_report() -> None:
    text = """# PHASE 2 — DATA FEASIBILITY AND TEMPORAL AUDIT

## Executive summary

The repository snapshot available in this workspace does not contain the required MIMIC-IV raw tables, the MIMIC-IV-ECG source files, or the modeling parquet artifacts needed to execute a numeric Phase 2 audit. The `data/raw` directory contains only archive stubs (`hosp.rar`, `icu.rar`) and there is no `data/modeling` tree with labels, embeddings, or master files. Because the underlying source tables are absent, the audit can only document the required checks and provide the analysis plan in a reproducible form.

## A. Clinical diagnosis timing

Required audit: validate whether diabetes, hypertension, CKD, and prior MI were recorded before the current admission using the longitudinal admission and diagnosis tables.

Current workspace status: not executable. The required longitudinal diagnosis tables are absent.

Strict prior-admission definition: a diagnosis must be documented with a timestamp or encounter date before the index admission start. A same-admission-only code is not treated as historical exposure.

Broader sensitivity definition: allow for a short pre-admission window or charted historical diagnosis from the same patient when the temporal ordering is sufficiently supported by the source records.

## B. Acute MI outcome validation

Required audit: validate ICD-9 410* and ICD-10 I21* / I22* while excluding 412 and I25.2; assess duplicate coding, transfer admissions, and disagreement with troponin-derived labels.

Current workspace status: not executable because the raw diagnosis tables are absent.

## C. ECG timing audit

Required audit: classify each ECG into before MI onset, after MI onset, or uncertain timing using admission context and event timestamps.

Current workspace status: not executable in the workspace because the waveform metadata, admission records, and MI event labels are absent.

## D. ECG feature audit

Required audit: group the 95 handcrafted features by physiologic domain and assess missingness, distributions, plausibility, and timing-specific availability.

Current workspace status: not executable because the feature tables are missing from `data/modeling`.

## E. Beta-VAE provenance audit

Required audit: confirm training checkpoint identity, cohort and split, use of acute MI ECGs in training, embedding extraction method, patient mapping, and variance diagnostics before allowing any causal use.

Current workspace status: not executable; no model/training artifacts exist in the workspace.

## F. ECG selection bias feasibility

Required audit: evaluate whether ECG acquisition can be modeled using measured variables and whether inverse-probability weighting is feasible.

Current workspace status: not executable; no admission-level cohort with ECG acquisition metadata is available.

## G. Dataset and split feasibility

Required audit: quantify patients, admissions, ECGs, MI-positive counts, and split characteristics while preserving patient-level separation.

Current workspace status: not executable because the modeling parquet and label files are absent.

## Final feasibility decision

Decision: C — Not currently feasible.

Reason: the repository snapshot does not include the raw MIMIC-IV, MIMIC-IV-ECG, or master-data artifacts required for a defensible causal audit, and the generated project documentation explicitly states that the final data pipeline outputs are not available in the workspace.

### What evidence supports this conclusion?
- `data/raw` contains only archive stubs and no extracted MIMIC tables.
- `data/modeling` is absent or incomplete.
- The repository contains the prior methodology documents but no actual phase outputs or datasets to audit.
- No validated MI diagnosis or ECG-timing dataset can be reconciled without those data sources.

### What remains uncertain?
- Exact MI-positive/negative counts in the underlying MIMIC cohort.
- ECG-level timing relative to MI onset.
- Whether beta-VAE embeddings are causal-eligible.
- Amount of selection bias associated with ECG acquisition.

### Which analyses must be excluded?
- Primary Layer 2 causal analysis using post-onset ECGs.
- Any causal role for VAE latent dimensions.
- Any use of post-onset ECGs as if they were interchangeable with validated pre-onset or same-admission controls.

### Which variables and cohorts can be used?
- None in the current workspace because the required raw and modeling data are absent.

### Recommendation

Do not estimate causal effects in this workspace. First restore or provide access to the required source datasets and modeling outputs, then rerun the audit pipeline in the `research_audit` directory before attempting final effect estimation.
"""
    _write_text(AUDIT_ROOT / "PHASE2_DATA_FEASIBILITY_REPORT.md", text)


def write_beta_vae_provenance_report() -> None:
    text = """# BETA-VAE PROVENANCE REPORT

## Decision

The beta-VAE latent dimensions are not eligible for primary causal analysis in the current workspace because the provenance chain cannot be audited from the available artifacts.

## Required provenance checks

1. Training checkpoint identity.
2. Training cohort and split definitions.
3. Whether acute MI ECGs were included in unsupervised training.
4. Embedding extraction procedure and deterministic behavior.
5. Patient and ECG mapping integrity.
6. Missingness and latent variance diagnostics.

## Current workspace status

The repository does not contain the model weights, training metadata, or latent extraction outputs required to complete these checks. The absence of `data/modeling/ecg_embeddings` and the lack of a corresponding training checkpoint make this an unresolvable provenance gap.

## Conclusion

The 64-dimensional latent vectors should remain excluded from the primary causal analysis until provenance is independently reconstructed and validated.
"""
    _write_text(AUDIT_ROOT / "BETA_VAE_PROVENANCE_REPORT.md", text)


def write_selection_feasibility() -> None:
    text = """# ECG SELECTION BIAS FEASIBILITY

## Status

Not currently feasible in this workspace.

## Required assessment

- Identify the population eligible for ECG acquisition.
- Model ECG acquisition probability using measured covariates available across admissions.
- Assess positivity and overlap.
- Check for extreme inverse-probability weights.
- Document unmeasured causes of ECG acquisition and differential recording.

## Current evidence

No `data/modeling` cohort or admission-level ECG acquisition dataset is present, so the required selection model cannot be built.

## Conclusion

Inverse-probability-of-selection weighting should not be claimed or used in the current workspace until the admission-level cohort and ECG acquisition covariates are available and positivity is formally evaluated.
"""
    _write_text(AUDIT_ROOT / "ECG_SELECTION_FEASIBILITY.md", text)


def write_completion_report() -> None:
    text = """# PHASE 1–2 COMPLETION REPORT

## Summary

A targeted audit of the Phase 1 and 2 requirements was performed against the available repository state. The source data needed for a numeric clinical diagnosis timing audit, MI outcome validation, ECG temporal audit, and cohort reconstruction are not present in this workspace.

## Key findings
- The raw MIMIC-IV and MIMIC-IV-ECG files are not available in extracted form.
- The modeled cohort folders (`data/modeling`) are absent.
- Historical diagnosis-timing checks cannot be computed.
- ECG timing classification and feature availability cannot be computed.
- Only the audit framework and documentation can be produced in the current workspace.

## Decision gate

C — Not currently feasible.

## Recommended next implementation phase

1. Restore or mount the complete MIMIC-IV v2.2, MIMIC-IV-ECG v1.0, and MIMIC-IV-ECG-Ext-ICD v1.0.1 data sources.
2. Recreate the raw `data/modeling` outputs referenced in the project documentation.
3. Re-run the audit scripts in `research_audit` against the actual source tables.
4. Only after all temporal and provenance checks pass should the project proceed to causal estimation.
"""
    _write_text(AUDIT_ROOT / "PHASE1_2_COMPLETION_REPORT.md", text)


def generate_audit_outputs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    inventory = inventory_repo()
    _write_csv(OUTPUT_DIR / "REPO_ARTIFACT_INVENTORY.csv", inventory.to_dict("records"))

    csvs = create_placeholder_csvs()
    _write_csv(OUTPUT_DIR / "CLINICAL_DIAGNOSIS_TIMING.csv", csvs["clinical_diagnosis_timing"].to_dict("records"))
    _write_csv(OUTPUT_DIR / "ACUTE_MI_OUTCOME_AUDIT.csv", csvs["acute_mi_outcome_audit"].to_dict("records"))
    _write_csv(OUTPUT_DIR / "ECG_TEMPORAL_AUDIT.csv", csvs["ecg_temporal_audit"].to_dict("records"))
    _write_csv(OUTPUT_DIR / "ECG_FEATURE_AVAILABILITY.csv", csvs["ecg_feature_availability"].to_dict("records"))
    _write_csv(OUTPUT_DIR / "BETA_VAE_PROVENANCE_REPORT.csv", csvs["beta_vae_provenance"].to_dict("records"))
    _write_csv(OUTPUT_DIR / "ECG_SELECTION_FEASIBILITY.csv", csvs["selection_feasibility"].to_dict("records"))
    _write_csv(OUTPUT_DIR / "COHORT_COUNTS_AND_SPLITS.csv", csvs["cohort_counts_and_splits"].to_dict("records"))

    write_phase1_estimands()
    write_phase2_report()
    write_beta_vae_provenance_report()
    write_selection_feasibility()
    write_completion_report()


if __name__ == "__main__":
    generate_audit_outputs()
    print(f"Research audit package written to: {OUTPUT_DIR}")
