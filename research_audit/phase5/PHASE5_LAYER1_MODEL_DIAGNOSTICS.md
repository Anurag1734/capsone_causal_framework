# Phase 5 Layer 1 Model Diagnostics

Layer 1 uses the full frozen analysis dataset: adult admissions with an eligible ECG, including the separate nonacute historical/prior-MI group. Each of the four binary exposure models uses its own Phase 4 adjustment set. Exposure propensity and outcome regressions are logistic models with a validation-selected cubic age spline (candidate df 3, 5, 7); the outcome nuisance is fit separately within each exposure arm. Five-fold patient-group cross-fitting generates the AIPW risk-difference score.

For each exposure, the diagnostic CSV reports cross-fitted propensity Brier score and log loss, propensity range and 1st/99th percentiles, clipping fraction, treated/control inverse-probability effective sample sizes, and cross-fitted outcome Brier score/log loss. Extreme propensities are clipped to [0.01, 0.99]. Weight ESS is a diagnostic, not evidence that conditional positivity or exchangeability holds.

| Exposure | Propensity Brier | Propensity p01-p99 | Clipped fraction | Treated-weight ESS |
|---|---:|---:|---:|---:|
| Prior diabetes | 0.171 | 0.050-0.284 | 0.00% | 38,098 |
| Prior hypertension | 0.234 | 0.065-0.540 | 0.00% | 70,426 |
| Prior CKD | 0.104 | 0.010-0.633 | 9.96% | 4,554 |
| Prior MI | 0.081 | 0.010-0.449 | 12.37% | 4,690 |

Layer 2 acute-MI propensity clipping was 13.63%, with treated-weight ESS 3,958; details are in `PHASE5_NUISANCE_DIAGNOSTICS.csv`. The CKD, prior-MI, and Layer 2 values indicate limited overlap. Those contrasts rely more heavily on outcome-model assumptions and the clipping rule.

Patient-clustered Wald standard errors use sums of cross-fitted influence scores by patient. Percentile intervals use 1,000 patient resamples with all of each sampled patient's admissions retained. The prior-MI contrast is descriptive. Recorded diagnoses may be undercoded; smoking, BMI, and lipids are unavailable; selection into the ECG cohort limits the target. The estimates are observational risk differences, not identified intervention effects.
