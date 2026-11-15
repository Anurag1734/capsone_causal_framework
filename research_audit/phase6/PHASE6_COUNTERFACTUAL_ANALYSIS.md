# Phase 6C - Exploratory Model-Implied ECG Profiles

## Availability and method

Phase 5 did not persist fitted models or the cross-fitted arm-specific outcome predictions. It did persist the reproducible Phase 5 estimator, model-selection result, cross-fit fold assignments, and nuisance specification. To produce the requested predictions, this component re-fits only the same Phase 5 cross-fitted Layer 2 outcome regressions: separate multivariate least-squares outcome models in MI=0 and MI=1 arms, using the existing six covariates and the validation-selected cubic age spline (df=3). No alternative learner or covariate set was introduced. The same patient folds and the Phase 5 primary cohort were used.

For each fixed covariate profile x, the reported quantities are m0(x) and m1(x), the outcome-model predictions with the acute-MI diagnosis indicator set to 0 or 1 while holding x constant. Each profile is an observed training-set baseline row; no patient identifier or observed ECG value is used. The three profiles are: (1) a common one-history pattern (70-year-old recorded female, hypertension only); (2) no coded prior-history conditions (61-year-old recorded female); and (3) three coded conditions (66-year-old recorded male, diabetes, hypertension, and CKD). The profiles and all 95 feature predictions are in `PHASE6_COUNTERFACTUAL_PROFILE_PREDICTIONS.csv`. Their cross-fitted MI propensities are 0.020, 0.032, and 0.037, respectively, so predictions should be read with the limited-overlap caveat.

## Interpretation and uncertainty

These are model-implied conditional feature profiles, not observed counterfactuals, reconstructed ECG waveforms, clinical interventions, or predictions of what would happen if MI were prevented or induced. They inherit the linear outcome-model form, measured adjustment set, ECG-selected target, possible positivity problems, unmeasured confounding, feature dependence, and unknown diagnosis/ECG timing.

There are no profile-specific uncertainty intervals. The Phase 5 patient bootstrap held fitted nuisance predictions fixed and estimated uncertainty for the population AIPW contrasts; it did not bootstrap-refit these profile prediction functions. The Phase 5 AIPW intervals are included only as context in the profile CSV and must not be read as intervals for m0(x), m1(x), or their difference. Cross-fitted MI propensities at the profiles are included as an overlap diagnostic.

The output is exploratory only, as the roadmap specifies. No causal intervention meaning is assigned to setting the coded diagnosis indicator.
