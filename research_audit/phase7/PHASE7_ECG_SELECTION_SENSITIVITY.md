# Phase 7B - ECG-Selection Sensitivity

The finalized Phase 3 denominator contains 431,231 adult admissions; 191,275 had an eligible ECG (44.36%). Phase 3 found selected admissions were older (SMD 0.524), more often coded acute MI (0.109), and had higher recorded comorbidity/prior-MI prevalence (SMDs 0.198-0.270 for major history flags). These are observed selection differences, not proof of bias direction.

## Weighted sensitivity

The existing corrected all-admission diagnosis audit and Phase 3 selected-admission IDs were reused; no ECG eligibility rules or Phase 3 dataset were rebuilt. A logistic selection model reproduced the Phase 3 predictor set: age, recorded sex, current acute MI, current historical-MI code, and prior diabetes, hypertension, CKD, and MI. Stabilized inverse-selection weights (selection rate divided by predicted selection probability) were applied to the Phase 5 cross-fitted AIPW feature scores. This changes the target toward all adult admissions under conditional exchangeability/selection-at-random assumptions. The weighted effect results are compared with Phase 5 in `PHASE7_SELECTION_SENSITIVITY_RESULTS.csv`; post-weight covariate balance is in `PHASE7_SELECTION_COVARIATE_BALANCE.csv`.

The selection model yielded propensity range 0.195-0.864, selected-weight 99th percentile 2.06, maximum 2.27, and ESS 173,194 of 191,275. After weighting, 8/8 observed covariates had |SMD|<0.10. For 95 ECG features, 89/95 weighted estimates retained the primary direction; median absolute shift was 0.009 outcome SD. 66/67 primary BH-significant features also passed weighted BH FDR.

## Limits

This is an assumption-dependent sensitivity analysis, not a correction guaranteed to eliminate selection bias. The propensity model is fitted on recorded variables only; unmeasured severity, symptoms, care pathway, clinician ordering, outpatient history, or ECG availability mechanisms can violate conditional selection exchangeability. The selected sample has no ECG features for nonselected admissions, so transport depends entirely on measured predictors and observed support. The Phase 3 selection report's 44.36% selection rate remains the target-population limitation. No timing or causal-ordering assumption is resolved.