# Phase 2.0-R — Conditional intervention-support feasibility

## Target and scope

The policy is unchanged: `d0(A)=A`; `d1(A)=A-10 I(A>=130)`. Support diagnostics use the candidate 730-day OMR mean SBP among patients with ≥2 valid readings (40,346 people; 933 first-MI cases over all recorded follow-up). The intervention, 130-mmHg threshold, and target cohort were not changed. No outcome model, causal effect, or treatment model was fit.

The design requires conditioning on age, sex, diabetes, hypertension, CKD and valid pre-window BMI. Age, sex, and BMI availability were observable. **Diabetes, hypertension, and CKD documented strictly before the exposure window have zero variation** under the common earliest-admission index. They cannot be included in a conditional-support model under the current temporal rule. Diagnoses documented by index occur during or after the exposure window and were not used as baseline covariates. Thus the full prespecified confounder-profile support question is not assessable.

## Methods and rules

The outcome-free support diagnostics were defined as follows. A provisional individual support flag is based on whether shifted SBP lies inside the conditional 1st–99th percentile range under both (a) held-out histogram gradient-boosted conditional quantile models and (b) leave-self-out local k-nearest-neighbor empirical quantiles. The KNN predictor uses standardized age, recorded sex, pre-window BMI, and a BMI-missing indicator; joint age×sex profile rates are separately reported. Local neighborhood sizes 100 and 250 are compared. Conditional kernel density ratios `f(A_shift|L)/f(A|L)` are sensitivity diagnostics at SBP bandwidths 5 and 10 mmHg. No outcome was used.

For any later outcome analysis, a provisional warning rule for researcher review is: flag support if >5% of shifts fall outside the 1st–99th conditional range overall, >10% in any age/sex profile, if the two conditional methods materially disagree, or if the shifted-value density ratio is near zero in a consequential profile. These numeric flags are proposed now for team review; they were not preregistered cutoffs for the present descriptive diagnostics, are not validated positivity criteria, and do not authorize trimming. Any target restriction/intervention modification requires explicit team approval. No treatment effect was used to select the intervention or rule.

## Results among the candidate ≥2 population

- 40.31% have mean SBP ≥130 and therefore receive the −10 mmHg shift; other values are unchanged.
- Observed patient-level mean SBP spans 80.0–243.5 mmHg; shifted values span 80.0–233.5 mmHg, with 0/40,346 outside the marginal observed range. This is only a marginal reference. Algebraically, shifted SBP is at least 120 mmHg whenever shifted and never exceeds observed SBP; no impossible shift was created by the policy definition.
- Held-out gradient-boosted conditional q01/q99: 102/8,070 (1.26%) shifted values outside; 2.08% of observed held-out values outside the predicted interval; median interval width 66.0 mmHg.
- Leave-self-out KNN q01/q99: 2.53% outside at k=100 and 1.82% at k=250; corresponding observed-value outside rates are 3.98% and 2.79%. At k=250, shifted outside rates across age×sex cells range about 1.71%–2.00%.
- Local density ratios near threshold (bandwidth 10, k=250) have median 1.01 in observed 130–<140 SBP, 1.39 in 140–<150, and 2.02 in ≥150. The 120–<130 band is unchanged by the policy. Overall ratio behavior is bandwidth-sensitive: bandwidth 5 has q05 0.85, q95 2.47, q99 3.86, and 19.3% above 10; bandwidth 10 has q05 0.89, q95 1.99, q99 2.76, and 3.5% above 10. No ratio fell below 0.1 in either specification. Extreme maxima reflect very small estimated denominator densities and are not taken as definitive evidence of overlap failure.
- The ratio-concentration ESS fields are diagnostic summaries only. They are highly unstable at bandwidth 5 and are not causal-weight ESS, since no density-ratio weighting estimator is planned as primary.

## Interpretation

For measured age/sex/BMI profiles, the two conditional-quantile methods show a modest fraction outside conservative local support envelopes (about 1.3%–2.5%). The result is **possible support, not demonstrated conditional positivity**: neighborhood and bandwidth choices matter; BMI is missing for 87.4% of the ≥2 group; the models do not include pre-window disease profiles because those variables have no observed variation; and a conditional mean/density approximation cannot validate unobserved profiles. Marginal range checks alone would be inadequate and are included only as a reference row.

The current evidence does not quantify full joint support across diabetes, hypertension, and CKD. It also does not prove the intervention value has empirical support for all target profiles. No unsupported patient was removed, no trimming occurred, and no shift or threshold was changed.

## Status

**Partial empirical support only for age, sex, and observed BMI availability. Full conditional positivity is not assessable under the available covariate timing and measurement process.** Require review of diagnosis timing/measurement availability and any conditional support rule before causal estimation. No effect estimation was performed.
