# Phase 7 Robustness Assessment

## Results across sensitivity analyses

- **Unmeasured confounding:** Layer 1 approximate E-values are modest: diabetes 1.66, hypertension 1.57, and CKD 1.28; the CKD interval includes the null. These rely on an approximate RD-to-RR conversion. Layer 2 uses a binary-U additive tipping grid, not E-values; it shows the bias product needed to move continuous-feature estimates to zero but does not rule out unmeasured confounding.
- **ECG selection:** measured-covariate weighting had good observed balance, and 89/95 weighted estimates kept the primary direction; median absolute shift was 0.009 SD. 66/67 primary BH findings also passed weighted BH. This remains dependent on selection-at-random conditional on measured covariates; unmeasured symptoms/severity are not addressed.
- **Alternative outcome code:** defining broad current MI as acute or historical MI code on the same admission increased cases to 21,930 (from 7,353) while keeping the 159,713 clean controls. 85/95 feature directions matched primary; 76/95 passed BH, with 59 primary discoveries overlapping. ST/T group mean absolute standardized effects were primary 0.162/0.129, selection-weighted 0.146/0.128, and broad-code 0.126/0.108. The broad case definition is less specific to acute MI.
- **Age/sex:** subgroup directions agreed with primary for age_<65 86/95, age_>=65 89/95, sex_F 85/95, sex_M 89/95. Direct interactions passed BH for 11 age and 13 sex feature contrasts. This points to feature-specific heterogeneity, not one uniform subgroup shift.
- **Main pattern:** large ST and T contrasts remain visible under weighted and broad-code analyses, but not all signs, magnitudes, or feature-level FDR flags are invariant. Residual feature dependence prevents treating the features as independent replications.

## Gate 2 decision

**Gate 2: partially satisfied.** Multiple central ST/T signals persist under measured-covariate selection weighting and the broader current-code outcome, and subgroup interactions were tested directly. However, E-values are modest and approximate, continuous-outcome tipping analyses cannot exclude unmeasured confounding, selection weighting relies on measured-only assumptions, broad MI coding changes the estimand, and age/sex interaction signals are feature-specific. Most importantly, MI onset relative to ECG remains unknown. The sensitivity analyses do not establish a causal MI-to-ECG effect.

A Phase 8 observational paper may be justified after review if it is explicitly framed as an adjusted diagnosis-feature association and reports these limitations. A causal/temporal paper claim is not justified. Phase 8 has not been started.