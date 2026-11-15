# Phase 3 Statistical Analysis Plan

## Status and estimand

This plan specifies **adjusted observational associations only**. No final association estimates, significance claims, or causal effects are produced in Phase 3.

For each feature \(j\), the primary estimand is the covariate-adjusted mean difference in the selected-ECG feature distribution between:

- acute ICD-coded MI admissions; and
- admissions without an acute code and without documented current/prior MI,

among adults with an eligible ECG and within covariate overlap. This is a conditional descriptive/associational contrast, not the result of assigning or preventing MI. Report raw-unit differences and standardized differences (feature SD units) to aid comparison.

The dataset has 191,275 one-ECG admissions, but the primary binary cohort contains 167,066 admissions: 7,353 cases and 159,713 comparisons. Patient-level clustering is required because a patient can contribute multiple admissions.

## Outcomes and feature groups

Fit one prespecified outcome model for each of the 95 handcrafted features. Use [`PHASE3_ECG_FEATURE_GROUPS.csv`](./PHASE3_ECG_FEATURE_GROUPS.csv) to define ST, Q, R, T, QRS, RR, S-wave/other morphology, and technical support. `QRS_Dur_Global_count` is a measurement-support metric: report it as a technical sensitivity/QC outcome, not a physiological change. Do not combine feature groups solely because their results are favorable.

The β-VAE dimensions are excluded until model and extraction provenance is independently documented.

## Model family

For continuous feature \(Y_j\), use an outcome-specific linear regression:

```text
Y_j = intercept + acute_Mi_diagnosis + prespecified baseline covariates + error
```

Allow a flexible, prespecified age function (for example, restricted cubic spline) rather than assuming linearity. Inspect residuals, leverage, and outcome distributions; report robust/sandwich inference and a prespecified transformed-outcome sensitivity when model diagnostics warrant it. The coefficient for acute diagnosis is an adjusted mean association, not a causal effect.

Use patient-clustered small-sample-corrected robust standard errors (CR2 or a documented equivalent) for 95% confidence intervals and two-sided tests. If the chosen implementation cannot provide reliable cluster-robust inference, use a patient-level bootstrap that resamples patients and retains all their included admissions. Never treat admissions from the same patient as independent.

Do not use a doubly robust causal estimator as the primary method. Its “doubly robust” property would not establish causal identification here, and event chronology, unmeasured confounding, and selection assumptions are not validated. Selection-weighted regression is a sensitivity analysis only.

## Covariate adjustment

Before outcome modeling, lock a feature/group-specific confounding diagram and adjustment set. Candidate measured baseline variables are age, recorded sex, prior-admission diabetes, hypertension, CKD, and prior MI. Use prior-admission flags only; do not use same-admission diagnoses or treatments as if they were established baseline. Age and sex are adjustment variables, not interventions.

Do not mechanically apply the same set to all features. For each feature/group, record why each selected variable is a common cause of acute diagnosis ascertainment and that feature, and why any candidate is omitted. In particular, do not adjust for `statin_during`, `aspirin_during`, vasopressors, ventilation, troponin values, ECG labels, or other potential consequences of acute illness.

The risk-factor flags represent coded inpatient history, not absence of disease. Smoking and lipids are unavailable in the analysis-ready tables. BMI and eGFR appear in OMR coverage metadata but row-level OMR values are not linked; they are not included in the Phase 3 models.

## Historical/prior MI

Primary controls exclude nonacute admissions with a current historical code or prior MI documentation. Keep these admissions as a distinct group. Prespecified sensitivities:

1. Include all nonacute admissions as controls and adjust for documented historical/prior MI.
2. Use a three-category exposure group: acute MI, historical/prior MI without acute MI, and no documented MI.
3. Restrict acute cases to first documented acute MI and compare with clean controls.
4. Restrict cases to acute MI as the principal diagnosis (`seq_num == 1`) if the diagnosis table supports the rule.

Historical codes must never be treated as acute MI by themselves.

## Multiplicity and feature-group tests

- Correct the 95 feature-wise primary family using Benjamini–Hochberg false-discovery-rate control at 5%; report unadjusted and adjusted p-values, estimates, and confidence intervals.
- Treat family-level results as exploratory; do not interpret a single uncorrected feature p-value as confirmatory.
- For secondary group comparisons, use prespecified group-level omnibus tests of all acute-diagnosis coefficients within each feature group, with patient-clustered covariance, and adjust the group-level tests using Holm correction.
- Interpret the technical count feature separately even though it remains in the conservative 95-feature multiplicity family.

## Missing-data strategy

Phase 3 construction found zero missing values for the 95 features, age, sex, and included diagnosis-history indicators in the selected dataset. No imputation is currently needed. Report measurement coverage by exposure group before modeling. If missingness appears in future source revisions, distinguish structural nonmeasurement from ordinary missingness; use multiple imputation for plausible MAR covariates only, and complete-case and missingness-indicator analyses as sensitivity checks where scientifically appropriate. Do not convert an uncoded diagnosis into proof of disease absence.

## Selection bias

ECG selection is substantial and differs by measured age, sex, diagnosis, and comorbidity. The outcome-analysis target is therefore the eligible ECG-admission population. For a broader all-admission target, compare unweighted estimates with an inverse-probability-of-ECG-selection weighted sensitivity analysis only after reviewing propensity overlap, calibration, effective sample size, and weight influence. The available fitted propensity range overlaps, but this does not establish conditional positivity or absence of unmeasured selection. Weighting must not be presented as automatically eliminating selection bias.

## Other prespecified sensitivities

- One earliest in-encounter ECG per admission (primary) versus all in-encounter ECGs with patient-clustered or patient-random-intercept models.
- Primary clean comparison versus inclusion of historical/prior MI admissions as specified above.
- Alternative clinically justified feature-specific adjustment sets, locked before outcome results are reviewed.
- Raw versus standardized outcomes; prespecified robust/transformed-outcome sensitivity if residual diagnostics require it.
- Selection-weighted versus unweighted association estimates, with target population stated.
- Exclude the technical count metric from physiological interpretation.

Do not use provisional troponin thresholds to define exposure, select records, or establish timing in any of these analyses. If exploratory threshold work is later done, label it separately and do not claim validated event timing.
