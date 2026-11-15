# Phase 7 Completion Report

## Completed analyses

1. Unmeasured confounding: approximate E-values for suitable binary Layer 1 contrasts; Layer 2 additive binary-U tipping products for continuous feature estimates.
2. ECG selection: reused the finalized all-admission diagnosis audit and Phase 3 selected IDs; reproduced the measured-covariate selection model and weighted Phase 5 cross-fitted scores.
3. Alternative outcome coding: broad sensitivity defined as acute or historical MI code on the current admission, with prior-only nonacute history kept out of controls.
4. Age/sex subgroup analyses: <65 vs >=65 and F vs M, with patient-clustered intervals and direct interaction tests.
5. Primary-versus-sensitivity comparison, figures, metadata, and reproducible scripts are included. Primary Phase 3-6 outputs and the analysis Parquet were not rebuilt or modified. No Phase 8 work started.

## Gate 2 and recommendation

Gate 2 is **partially satisfied**, not fully passed. Some main ST/T patterns persist across selection weighting and alternative current-MI coding; subgroup interaction analysis identifies feature-specific heterogeneity. Confounding sensitivity is limited, selection weighting depends on measured covariates, overlap and timing remain limitations, and broad coding changes the estimand. The evidence supports proceeding toward an observational association write-up after review, but not a causal MI-to-ECG claim. Phase 8 has not begun. See `PHASE7_ROBUSTNESS_ASSESSMENT.md`.

## Files generated

- `PHASE7_UNMEASURED_CONFOUNDING.md`
- `PHASE7_EVALUE_RESULTS.csv`
- `PHASE7_ECG_SELECTION_SENSITIVITY.md`
- `PHASE7_SELECTION_SENSITIVITY_RESULTS.csv`
- `PHASE7_SELECTION_COVARIATE_BALANCE.csv`
- `PHASE7_ALTERNATIVE_MI_DEFINITIONS.md`
- `PHASE7_ALTERNATIVE_MI_RESULTS.csv`
- `PHASE7_AGE_SEX_SUBGROUP_ANALYSIS.md`
- `PHASE7_SUBGROUP_RESULTS.csv`
- `PHASE7_SUBGROUP_INTERACTIONS.csv`
- `PHASE7_PRIMARY_VS_SENSITIVITY_COMPARISON.csv`
- `PHASE7_ROBUSTNESS_ASSESSMENT.md`
- `PHASE7_FIGURES/` (4 plots)
- `PHASE7_RUN_METADATA.json`, `run_phase7_sensitivity.py`, `finalize_phase7_reports.py`
