# PHASE 1 — CAUSAL ESTIMANDS

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

