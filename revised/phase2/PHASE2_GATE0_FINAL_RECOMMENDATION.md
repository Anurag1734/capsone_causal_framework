# Phase 2 Gate 0 Final Recommendation

## Gate decision

**Gate 0: FAILED / not passed.** Prepared-data inspection did not supply the required pre-window disease histories or a defensible individual observation/censoring process. Death ascertainment is incomplete, full conditional positivity is not assessable, and the at least 2-reading BP threshold/horizon/estimand alternatives lack human approval. No Phase 2.1 cohort construction or causal estimation is authorized by this report.

## What is now established

1. The local source set includes prepared longitudinal admissions, diagnoses, MI derivatives, patient demographics, observation-end summaries, coverage catalogues, OMR, prescriptions, eMAR, labs, and a prepared ECG master archive.
2. The actual diagnosis table provides admission-dated inpatient diagnosis codes. In the 168,915-person common-index risk set, no participant has qualifying diabetes, hypertension or CKD documentation before the 730-day BP window. Index-date and later diagnoses exist but cannot be moved backward to baseline.
3. The documented `features_comorbidities.csv` is an admission-keyed binary history summary from prior admissions; it stores no dates and is absent from the local workspace. Its corresponding flags in the ECG master are not valid substitutes for pre-window Phase 2 covariates.
4. Prepared records support recorded hospital events, not continuous outcome surveillance. No outpatient-visit, claims/enrollment, observation-end, or common administrative boundary source is available. Death evidence remains incomplete.
5. Age/sex/BMI support diagnostics remain partial. At the >=2 threshold OMR retention differs by age and recorded sex, and valid pre-window BMI is available in 12.6%; no selection model was fitted. Disease-profile positivity and unmeasured outpatient/hospital observation selection remain unresolved.

See `PHASE2_PREPARED_DATA_BLOCKER_REASSESSMENT.md`, `PHASE2_BASELINE_DIAGNOSIS_TEMPORAL_VALIDATION.md`, `PHASE2_OBSERVATION_AND_DEATH_FINAL_AUDIT.md`, and `PHASE2_IDENTIFIABILITY_AND_ESTIMAND_DECISION.md` for evidence and definitions.

## Team choices still required

- Decide whether to retain the original complete first-MI cumulative-incidence estimand and obtain external/linkable pre-window diagnosis, observation and death data (Option A).
- Decide whether to consider a separately defined hospital-record capture estimand, with full opportunity window and changed interpretation, if the required boundary can be established (Option B).
- Decide whether to stop causal effect estimation under current data (Option C).
- If the team retains the primary design, approve the BP threshold and follow-up horizon only after their scientific implications are reviewed; do not treat approval as a substitute for absent data.

No choice is made on behalf of the research team. The fixed BP intervention, 130-mmHg threshold, index and target estimand remain unchanged unless the team explicitly approves a separately documented design decision. The original estimand cannot currently be identified from the available data alone.

## Scope and data handling

Prepared-source investigation and aggregate diagnosis timing validation only. No patient-level cohort/exposure file, outcome model, propensity model, g-computation, AIPW, CATE, causal forest, Phase 3 work, dashboard change, or beta-VAE investigation was performed. Only aggregate disease rows and source schema metadata were written under `revised/phase2/`; temporary master Parquet metadata inspection used an auto-deleted temporary file. Raw archives and original Phases 1-9 artifacts were not modified.
