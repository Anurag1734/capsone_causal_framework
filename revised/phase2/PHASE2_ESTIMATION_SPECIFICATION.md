# Phase 2 — Estimation and Uncertainty Specification

No estimator was fit in Phase 2.0. This protocol defines the future primary method subject to the cohort, support, follow-up and death gates.

## 1. Estimand

For the approved target population with final BP eligibility, compare reference `d0(A)=A` with fixed modified policy `d1(A)=A-10 I(A>=130)`. Primary:

`RD(τ) = F_M^d1(τ) - F_M^d0(τ)`

where `F_M^d(τ)` is cumulative incidence of first acute-MI-coded admission by approved fixed horizon τ, with death as a competing event. Target population is selected MIMIC hospital entrants meeting common index, history exclusion, BP, and follow-up criteria. Report both standardized risks and a two-sided 95% interval. Risk ratio is secondary. Cause-specific hazard ratios are not the primary estimand.

Candidate τ is 365 days; it is not established by current follow-up data. The effect is hypothetical baseline-value shift, not a sustained regimen. Do not call it a medical prescription.

## 2. Primary estimator: competing-risk g-computation

Use a discrete-time event-process g-computation, not a binary `MI by day 365` regression that ignores death/censoring.

1. Represent each person in 30-day intervals from index through τ, with a final partial interval; sensitivity check a finer weekly partition. At each interval while event-free, model mutually exclusive interval outcomes: first acute MI, death, or event-free. Use exact admission timestamps for MI where available; represent date-only death as interval/day uncertainty and handle same-calendar-day MI/death ties in sensitivity analysis.
2. Fit separate cause-specific discrete-time hazards or an equivalent calibrated multinomial event model with flexible elapsed-time effects, continuous baseline SBP, and the primary pre-B covariates. Model SBP nonlinearly (restricted cubic spline; knots chosen from the exposure distribution without outcome-guided selection). Include prespecified treatment-policy and modifier interactions only for approved heterogeneity analyses.
3. For each eligible patient, predict interval MI/death probabilities under `d0(A)` and `d1(A)` at the same measured baseline covariate profile. Standardize over the target population. For each policy, calculate `S_k = S_(k-1) [1-p_M(k)-p_D(k)]` and `CIF_M(τ)=Σ_k S_(k-1) p_M(k)`. The contrast of standardized CIFs is RD; report risks and RR.
4. Handle right censoring only with a validated censoring process. If individual censor times are observable, estimate conditional censoring probabilities from baseline exposure/covariates and justified pre-censor history; use inverse censoring weights in event-model fitting or a validated equivalent. Check censoring positivity and weight tails. A model cannot repair unobserved out-of-system follow-up or unknown censor dates. Current sources do not establish this process, so estimator is blocked pending validation.
5. Death must be observed with defensible dates for the competing-risk event process. Missing DOD cannot be coded alive. If death ascertainment remains inadequate, do not report the target cumulative incidence as identified; present only explicitly assumption-based sensitivity scenarios or stop estimation.

## 3. Why g-computation

It directly standardizes policy-specific risks for a continuous modified treatment policy and naturally computes cumulative incidence from event hazards. It is compatible with one index per patient and patient-level resampling. It still requires conditional exchangeability, support, correct event/censoring models, and outcome capture. Generic binary-treatment AIPW from original MI–ECG work is not valid as the primary estimator here.

AIPW/IPW are secondary robustness analyses only after statistical review derives the continuous-policy density ratio and competing-risk/censoring formulation. Do not call an off-the-shelf binary AIPW result doubly robust for this target.

## 4. Positivity/support gate

Before fitting outcome models, assess conditional exposure density across age, sex, pre-B diabetes, hypertension, CKD, BMI availability, and joint profiles where sample size allows. Specifically inspect near 130 mmHg, density at `d1(A)`, shifted-value support, density ratios, and fraction unsupported overall/by subgroup. Use cross-validated conditional density estimates and profile/stratum plots; marginal min–max or bins are insufficient. Establish a numeric near-zero density/weight threshold before viewing outcomes. Preserve full target and report unsupported mass; do not trim or change intervention automatically. Any restriction requires team approval and new estimand. No conditional support result is available yet.

## 5. Dependence, cross-fitting, and uncertainty

There is one index per patient, but person-period rows repeat within patient. If flexible nuisance learners are used, use five-fold cross-fitting grouped by `subject_id`; all time rows and linked records for a patient stay in one fold. Do not split admission/person-period rows independently.

Use a patient-level nonparametric bootstrap with 1,000 resamples as the primary uncertainty procedure, refitting nuisance/event/censoring models and restandardizing in each replicate. Use two-sided 95% percentile intervals for the primary risk difference and policy risks; report convergence failures and effective bootstrap count. Patient is the resampling unit. Validate interval coverage and model stability with simulation before final analysis. Record software versions and random seeds.

## 6. Heterogeneity and multiplicity

Prespecified modifiers are age <65 vs ≥65 at B, recorded sex, and documented diabetes strictly before B. The supplied counts (375/848 age, 651/572 sex, 503/720 diabetes) refer to reconciled two-year BP-available cases under supplied definitions and do not guarantee final subgroup counts after the pre-B timing rule or ≥2 threshold.

Report subgroup standardized risks and RDs with patient-bootstrap intervals, direct contrasts in RD between strata, and a joint omnibus test that all three modifier-specific RD contrasts equal zero. Apply Holm family-wise adjustment at 0.05 to the three prespecified modifier tests; the main population RD remains the single primary contrast. No CATE/causal forest.

Before subgroup estimation, approve a clinically meaningful minimum detectable RD/interaction and target 95% CI width, then simulate precision under observed event/censoring and overlap patterns. Raw events-per-parameter is not sufficient. No numeric clinical precision target can be justified from the available aggregate counts alone; this decision remains with the research team.

## 7. Diagnostics and sensitivity analyses

- Calibration and discrimination of interval cause-specific predictions; flexible time and SBP functional form; alternative spline complexity.
- Conditional support, density ratios, shifted-value out-of-support fraction, weight tails and effective sample size.
- Censoring model calibration/positivity and observed follow-up; no last-encounter-to-admin-end assumption.
- Competing death under-ascertainment scenarios; same-day tie handling.
- BP count thresholds ≥1/≥2/≥3/≥4; mean vs median and measurement frequency influence; one-/two-/three-year windows (two-year primary candidate).
- Pre-B covariate missingness; BMI inclusion sensitivity; no fictional smoking/lipid values; quantitative unmeasured-confounding analysis.
- Selection into BP measurement using measured pre-index predictors only; selection weighting is sensitivity, not a cure for unmeasured selection.
- ICD code implementation checks and, only if prespecified, code-position sensitivity.
- Alternative horizons 90/180/365/730 days after 365-day feasibility decision.
- Medication sensitivity only with clearly named recorded-prescription measure; do not equate record with outpatient use or adherence.

## 8. Reporting

Report population flow, definitions, missingness, coverage and censoring; both policy risks, RD and secondary RR; 95% intervals; support/selection/competing-risk diagnostics; all prespecified sensitivity results; and assumptions/limitations. Use aggregate outputs only. Do not reuse original MI–ECG effects as SBP effects or imply individual causal truth.
