# Revised Phase 1 — Future Statistical Analysis Plan

This is a prespecified plan for a later phase, not an analysis report. **No cohort construction, treatment/outcome model, propensity model, AIPW, causal forest, effect calculation, or model validation was run.** The primary exposure policy and estimand are defined in `EXTENSION_PHASE1_ESTIMANDS.md`; review `PHASE1_DECISION_REGISTER.md` before any implementation.

## 1. Analysis population and data construction

1. Build one common index per patient using earliest eligible non-acute-MI admission, applying identical rules to cases/controls. Exclude documented acute and historical MI on/before index. Do not select controls based on future MI-free status; later first events change status at event time.
2. Reconstruct acute (`410*`, `I21*`, `I22*`) and historical (`412`, `I25.2`) flags from diagnosis code/version and admission linkage. Validate first-event ordering and explicitly distinguish missing documentation from known absence.
3. Parse OMR SBP/DBP, apply limits and SBP>DBP, and require chartdate strictly before index. Use candidate 730-day interval `[index-730d,index)`. Compute mean SBP and retain count, median, variability, date/frequency distribution, and missingness. Apply the team-approved minimum count; report the denominator flow at each step.
4. Define time-varying baseline covariates using data strictly before the exposure-window start (`index_date - 730 days`) as the recommended temporal rule; a by-index diagnosis can postdate BP readings in the 730-day mean window. Use age at window start and recorded sex. Do not leak within-window/post-exposure information into primary baseline adjustment without explicit DAG justification and approval. Preserve person-level linkage for repeated admissions and cluster inference.
5. Establish follow-up data coverage, event date, death linkage and censoring/observation end. Reconcile patient-level and admission-level death variables before selecting the competing-risk definition. No date-of-death null is interpreted as survival.

## 2. Descriptive and measurement diagnostics

Report aggregate flow and missingness from hospital cohort → common index → no documented prior MI → qualifying BP → approved measurement-count rule → outcome/death/follow-up availability. Describe age, sex, diabetes, hypertension, CKD, BMI availability, BP mean/median/range, count and within-window variability, follow-up coverage, events, competing deaths, and censoring by policy-relevant strata. Avoid patient-level records in reports.

Assess measurement-frequency effects: compare distributions by reading count and utilization, inspect whether a few frequent attenders dominate arithmetic means, and compare the prespecified mean with median and variability summaries as measurement sensitivity checks. Do not choose the exposure summary or window based on treatment-effect results.

## 3. Outcome and follow-up analysis

After horizon approval, estimate policy-specific fixed-horizon cumulative incidence of first acute-MI admission, treating death as a competing event when defensible. Define administrative horizon and observation end explicitly. Later MI admissions do not add events. Present event-free observation and censoring summaries over time. If death dates are incomplete, provide prespecified sensitivity analyses under alternative death ascertainment assumptions and clearly label any analysis that censors death rather than treating it as competing.

## 4. Covariates and missingness

Primary candidate adjustment set: flexible age at exposure-window start, recorded sex, and documented diabetes, hypertension and CKD strictly before the exposure-window start. BMI is added only if validly measured before that start under an approved rule; provide a separate analysis and missingness report. This temporal cutoff is a recommended candidate requiring approval and may omit recent disease. Diagnoses first recorded during the exposure window are not automatically baseline confounders. Prior MI is excluded by design and cannot vary as a primary adjuster; verify this in cohort flow. Medication variables are not included by default because recorded prescription, pharmacy, or administration does not prove outpatient use, adherence, dose, or index exposure. A separately interpreted sensitivity analysis may use a defensible pre-window prescription indicator.

Do not create smoking/lipid observations. Quantify available missingness; use multiple imputation only for measured-but-missing variables under a defensible missingness model, with complete-case and missing-not-at-random sensitivity as appropriate. Selection weights may use measured pre-index predictors of BP availability (age, sex, diagnoses, admission/utilization history, and other available covariates), but cannot correct unmeasured drivers. Report weight distribution, truncation if predeclared, effective sample size, and selected-versus-unselected balance.

## 5. Intervention support and positivity diagnostics

Before effect estimation, assess the deterministic modified policy's support:

- Conditional SBP distributions/densities within prespecified covariate profiles and clinically interpretable strata.
- Observed density/overlap at `A` and `d1(A)`, including threshold behavior around 130 mmHg.
- Shifted-value range/support and fraction outside supported regions overall and by age, sex, diabetes, and key confounder profile.
- Weight or density-ratio tails if used, effective sample size, and sensitivity to prespecified truncation.
- Positivity violations across multivariable profiles, not only marginal bins or global min–max.

If support is inadequate, stop estimation for unsupported population/contrast and return a prespecified restriction or alternative stochastic intervention to researcher approval. Do not silently trim or claim positivity from descriptive marginals.

## 6. Candidate estimators and recommended future primary

Candidate approaches:

- **G-computation:** model the outcome/cumulative-incidence process conditional on measured confounders and SBP, then standardize predictions under `d0` and `d1`. Directly targets the fixed-horizon population risks and accommodates the deterministic modified policy; vulnerable to outcome-model misspecification and extrapolation, so support diagnostics are essential.
- **AIPW:** can combine outcome and generalized treatment-density models for a continuous exposure, with censoring/competing-risk nuisances. Doubly robust properties require correct formulation for the modified policy and event process; deterministic many-to-one threshold map and competing events need careful derivation.
- **IPW:** treatment density ratios and censoring/selection weights can be transparent but may be unstable under sparse conditional support and extreme weights.
- **Double machine learning:** may help flexible nuisance estimation and orthogonalization, but is not automatically an estimator for this competing-risk fixed-horizon modified-treatment policy. Use only after target-specific theory/implementation is specified.

**Recommended future primary candidate:** outcome-regression g-computation for policy-specific fixed-horizon cumulative incidence, with flexible prespecified nuisance models, patient-level cross-fitting for nuisance selection where suitable, and patient-cluster bootstrap uncertainty. This aligns directly with the policy risks and avoids pretending a generic binary AIPW handles time-to-event, censoring, and death automatically. Use correctly derived AIPW/IPW as robustness estimators if support permits. Final estimator requires method review before Phase 2. No estimator is fitted here.

## 7. Repeated patients, splitting, and uncertainty

Use patient—not admission or measurement—units for the index cohort; if any analysis retains multiple records, cluster all uncertainty by patient. Split/cross-fit at patient level so one person's admissions cannot cross folds. Use a patient-level bootstrap (resample patients and retain their records) for uncertainty, repeating relevant nuisance fitting and standardization. Report two-sided 95% intervals and convergence/support failures. Account for estimation of censoring/competing-risk quantities within each resample where feasible.

## 8. Heterogeneity and multiplicity

Candidate modifiers: age <65 vs ≥65; recorded sex; documented diabetes before the exposure-window start. Report subgroup policy risks and RD intervals plus direct interaction/contrast estimates. Use an omnibus test of no heterogeneity across prespecified modifier terms, alongside direct interaction tests; avoid comparing significance in one subgroup with nonsignificance in another. Define minimum useful heterogeneity and interval-width/precision targets before estimation using design-based simulation/precision calculations that do not inspect favorable treatment effects. Supplied by-index case counts (375/848 age, 651/572 sex, 503/720 diabetes among two-year BP cases) are descriptive feasibility facts and may not match the causally timed subgroup definition. Control multiplicity across the three modifiers (for example, Holm adjustment) and label all additional subgroup exploration exploratory. No causal forest in this study phase; any later use requires separate approval and validation.

## 9. Prespecified sensitivity analyses

- Look-back: one, two (primary candidate), and three years; do not select on effect direction.
- Exposure summary/count: mean vs median/variability; ≥1 vs approved repeated-measure threshold; frequency restrictions/standardization.
- Intervention: deterministic 10-mmHg map vs any approved support-restricted stochastic alternative; report as distinct estimands.
- Follow-up: approved primary horizon and prespecified feasible shorter/longer horizons, with censoring implications.
- Medication: no medication adjustment primary; separately defined pre-index prescription indicator sensitivity; do not label prescriptions as actual use.
- Outcome: explicit ICD code/version implementation; sensitivity excluding/including selected code-position rules only if prespecified and clinically reviewed.
- Selection: unweighted BP-observed cohort vs measured selection-weighted analysis; report limitations and weight diagnostics.
- Missingness: BMI inclusion strategy, complete case vs justified imputation, and sensitivity to unobserved smoking/lipids/confounding.
- Confounding: quantitative bias/sensitivity analysis for unmeasured smoking/lipids and healthcare/utilization factors.
- Competing death/censoring: defensible competing-risk analysis vs clearly distinct censoring-based alternatives and death-underascertainment scenarios.
- Positivity: supported population restrictions only if approved; compare effect target and population transparently.

## 10. External benchmark and reporting

Before results, select an external clinical benchmark or guideline-compatible scale for context and document its population/intervention differences; it is not a validation dataset and cannot validate causal identification. Report absolute risks and differences first, with relative measures secondary. Include cohort flow, code rules, DAG, estimand, support and missingness diagnostics, uncertainty, assumptions, deviations, and all prespecified analyses. Do not use original Phase 1–9 MI–ECG estimates as estimates of this new SBP policy.

## 11. Separate modules

BP-to-ECG requires its own non-MI/historical-MI status at ECG, index ECG definition, BP-before-ECG requirement, fixed look-back and temporal gap, feature completeness, separate adjustment DAG, selection diagnostics, and multiplicity correction across ECG outcomes. Its 52,267 / 38,987 Phase 0 counts are not incident-MI denominators. Individual scenario estimation is downstream of validated population analysis and must return uncertainty/applicability/support flags, avoid extrapolation, and never prescribe or claim individual causal truth. Neither module is run here. β-VAE work is explicitly excluded.
