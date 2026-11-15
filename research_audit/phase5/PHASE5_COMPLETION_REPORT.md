# Phase 5 Completion Report

## Analysis scope and method

Phase 5 used the finalized Phase 3 Parquet and Phase 4 graph/adjustment sets. No cohort or dataset was rebuilt, and the 64 beta-VAE dimensions remain excluded. Both layers use augmented inverse-probability weighting with five-fold patient-group cross-fitting. Estimates are adjusted observational risk or mean differences; the proposed causal interpretation is not identified by these data.

The Phase 5 brief explicitly requested doubly robust estimation, matching the original roadmap. The Phase 3 statistical plan had cautioned against using a doubly robust estimator as a primary **causal** method. AIPW is used here as the requested estimator for adjusted contrasts, while retaining the Phase 3 limit: its doubly robust property does not establish causal identification, and no result is called a demonstrated causal effect.

Validation selected cubic age spline degrees of freedom from 3, 5, and 7. Cross-fitting used seed 20261115. Patient bootstrap intervals use 1,000 resamples, seed 20261115, resampling patients with all their admissions. Nuisance predictions are held fixed in the bootstrap. The test split was used for effect stability and a held-out feature-dependence check. No Phase 6 work was started.

## Layer 1: chronic factors and acute MI diagnosis

The analysis includes 191,275 ECG-selected admissions from 99,214 patients. Acute MI outcome prevalence is 3.84% (7,353 admissions). Estimates below are adjusted risk differences with 95% patient-bootstrap intervals.

| Exposure | Prevalence | Adjusted risk difference | 95% bootstrap CI | Interpretation |
|---|---:|---:|---:|---|
| Prior diabetes | 22.57% | +0.69 percentage points | +0.42 to +0.95 | Adjusted observational contrast |
| Prior hypertension | 43.80% | -0.51 percentage points | -0.70 to -0.30 | Adjusted observational contrast |
| Prior CKD | 17.47% | -0.17 percentage points | -0.59 to +0.31 | Interval includes zero; overlap is limited |
| Prior MI | 10.70% | +5.48 percentage points | +4.67 to +6.41 | Descriptive association only |

Crude and adjusted estimates, p-values, sample sizes, and exact adjustment sets are in `PHASE5_LAYER1_EFFECT_ESTIMATES.csv`. The Phase 4 exposure-specific sets were preserved. Alternative diabetes/hypertension orderings remain sensitivity considerations and were not substituted into these primary estimates.

## Layer 2: acute MI diagnosis and ECG features

The primary comparison contains 167,066 admissions from 93,946 patients: 7,353 acute MI and 159,713 clean controls. All 95 feature outcomes are complete. Crude estimates are in `PHASE5_LAYER2_CRUDE_ESTIMATES.csv`; adjusted AIPW estimates and intervals are in `PHASE5_LAYER2_ADJUSTED_ESTIMATES.csv`; raw p-values, BH q-values, and flags are in `PHASE5_LAYER2_FDR_RESULTS.csv`.

At BH FDR 5%, **67 of 95** tests are significant: 66 physiological outcomes plus the distinct technical/support count metric. The largest standardized adjusted contrasts include ST_Elev_I (-0.346 SD; 95% CI -0.384 to -0.311), T_Amp_I (-0.336 SD; -0.370 to -0.304), T_Amp_aVR (+0.327 SD; +0.296 to +0.360), and ST_Elev_aVF (-0.302 SD; -0.340 to -0.264). All 95 feature flags and estimates are in the FDR table. Significance does not establish clinical importance; correlated features are not independent replications.

All seven physiological feature-group omnibus Wald tests were significant after Holm correction. Mean absolute standardized contrasts were largest for ST (0.162 SD), T (0.129 SD), RR (0.128 SD), QRS (0.091 SD), other morphology (0.062 SD), R (0.053 SD), and Q (0.053 SD). The technical count is separate. Results are in `PHASE5_FEATURE_GROUP_RESULTS.csv`.

## Diagnostics and stability

The 117 logistic nuisance fits recorded in `PHASE5_CONVERGENCE_AUDIT.csv` had zero convergence warnings or iteration-limit hits (maximum 40 of 500 iterations). Propensity clipping at [0.01, 0.99] affected 9.96% of CKD exposure rows, 12.37% of prior-MI rows, and 13.63% of Layer 2 rows. Treated-weight effective sample sizes were 4,554, 4,690, and 3,958, respectively. These indicate limited overlap and sensitivity to modeling and clipping, despite successful convergence.

On the held-out test split, Layer 2 estimate directions agreed with the full-data cross-fit direction for 81/95 features. Median absolute cross-fit/test difference was 0.040 outcome SDs (maximum 0.139 SD). Layer 1 test contrasts retained their signs; CKD remained small and uncertain. This supports broad, but not uniform, numerical stability. The test split's held-out feature-dependence check found median |r|=0.067, 95th percentile=0.467, maximum=0.873, with 1,697/4,371 pairs at |r|>=0.10. This agrees with Phase 4: the sparse measured-parent-only feature-independence implication is unsupported. No graph edges were automatically added or oriented.

ECG selection remains material: only 44.36% of adult admissions in the Phase 3 denominator had an eligible ECG. Coded history can be under-recorded; smoking, BMI, and lipids are unavailable. Biological MI onset relative to the selected ECG is unknown, so the proposed MI-to-ECG arrow is not empirically established. Estimates apply to selected ECG admissions and do not establish that MI caused the measured ECG differences.

## Review gate

The Phase 5 deliverables and figures are ready for review. Given limited overlap for some exposures, residual feature dependence, selection, and unknown MI/ECG timing, the results are **not ready to support stronger causal claims or automatic progression to Phase 6**. Phase 6 has not been started.

## Deliverable inventory

- `PHASE5_LAYER1_EFFECT_ESTIMATES.csv`
- `PHASE5_LAYER1_MODEL_DIAGNOSTICS.md`
- `PHASE5_LAYER2_CRUDE_ESTIMATES.csv`
- `PHASE5_LAYER2_ADJUSTED_ESTIMATES.csv`
- `PHASE5_LAYER2_FDR_RESULTS.csv`
- `PHASE5_FEATURE_GROUP_RESULTS.csv`
- `PHASE5_BOOTSTRAP_RESULTS.md`
- `PHASE5_CROSSFITTING_REPORT.md`
- `PHASE5_FIGURES/` - five figures: Layer 1, crude/adjusted, full forest, group summary, FDR-significant features
- `PHASE5_COMPLETION_REPORT.md`

Supporting artifacts include fold assignments, validation model selection, convergence and nuisance diagnostics, run metadata, test-split stability and independence checks, and the estimation script.
