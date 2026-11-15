# Phase 6 Completion Report

## Components completed

**A. Deconfounded ECG analysis:** reused all 95 Phase 5 adjusted estimates and crude contrasts. 67/95 features passed BH FDR, including 66 physiological features and one technical/support feature. ST and T patterns were largest by group summaries, with lead-dependent directions. Feature dependence means these are not independent replications. See `PHASE6_DECONFOUNDED_ECG_ANALYSIS.md`, `PHASE6_FEATURE_NOVELTY_RESULTS.csv`, and `PHASE6_FEATURE_GROUP_INTERPRETATION.md`.

**B. Latent audit:** excluded for the previously documented missing checkpoint, training metadata, and extraction outputs. No VAE was retrained and no provenance audit repeated; see `PHASE6_LATENT_ANALYSIS_STATUS.md`.

**C. Model-implied profiles:** Phase 5 did not save fitted nuisance models or the cross-fitted m0/m1 predictions. For this specific deliverable, the same Phase 5 outcome-model specification and patient folds were reproduced to generate exploratory profile predictions. The method, profiles, and uncertainty limitation are documented in `PHASE6_COUNTERFACTUAL_ANALYSIS.md`; predictions are in `PHASE6_COUNTERFACTUAL_PROFILE_PREDICTIONS.csv`. They are not observed counterfactuals or causal intervention effects.

## Limitations and review gate

The MI-to-ECG direction is not empirically established because MI onset relative to ECG is unknown. ECG selection may bias associations; overlap is limited for some propensity models; residual feature dependence is substantial; coded histories may be incomplete; and all Phase 5 values are adjusted observational contrasts. Beta-VAE latents remain excluded. No Phase 7 analysis was started.

Phase 6 deliverables are ready for review. The Phase 6 work products are complete, with the latent component explicitly excluded and counterfactual profiles explicitly exploratory. The roadmap's broader Gate 2 stability criterion is not yet cleared: sensitivity analyses are assigned to Phase 7 and have not been performed. This phase does not establish causal identification or a literature-based novelty claim. Phase 7 has not begun.

## Files generated

- `PHASE6_DECONFOUNDED_ECG_ANALYSIS.md`
- `PHASE6_FEATURE_NOVELTY_RESULTS.csv`
- `PHASE6_FEATURE_GROUP_INTERPRETATION.md`
- `PHASE6_COUNTERFACTUAL_ANALYSIS.md`
- `PHASE6_COUNTERFACTUAL_PROFILE_PREDICTIONS.csv`
- `PHASE6_LATENT_ANALYSIS_STATUS.md`
- `PHASE6_FIGURES/` (4 figures)
- `PHASE6_COMPLETION_REPORT.md`
- `run_phase6_novelty_analysis.py`
