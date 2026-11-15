# Final Phase 7 Review and Phase 8 Readiness

**Project:** A Causal Analysis of Acute Myocardial Infarction: Risk Factors and ECG Responses Using MIMIC-IV and MIMIC-IV-ECG  
**Review scope:** Completed Phase 5–7 deliverables and the original roadmap. No new estimator was fit; review calculations summarize saved results. No dataset or prior phase was rebuilt.

## 1. Decision summary

**Gate 2: Partially satisfied.** This is justified by the actual sensitivity results. The central ST/T pattern persists across the primary acute-code analysis and the measured-covariate selection-weighted analysis, and remains visible when the MI-code definition is broadened. However, some estimates move, the broader definition attenuates ST/T contrasts, a subset of feature directions changes, and age/sex interaction tests indicate feature-specific heterogeneity. The unmeasured-confounding analyses do not rule out meaningful bias. None of these analyses supplies the missing MI-onset-to-ECG timing.

**Phase 8 readiness: Ready to begin paper preparation as an observational association study, after the user approves this review.** This is not a recommendation to claim an identified causal effect, a universal MI ECG signature, or literature-based novelty. Phase 8 has not been started by this review.

## 2. Phase 7 completion verification

The original roadmap's four requested sensitivity components are represented in the completed Phase 7 deliverables:

1. **Unmeasured confounding:** Layer 1 approximate E-values are reported for binary risk-factor/acute-MI contrasts. For the 95 continuous Layer 2 feature outcomes, the work correctly avoids treating E-values as directly applicable and instead reports an additive omitted-binary-confounder tipping scale.
2. **ECG selection:** the finalized 431,231-admission denominator and selected-admission IDs were reused. Selection weighting was applied to Phase 5 cross-fitted feature scores; the Phase 3 cohort and ECG dataset were not rebuilt.
3. **Alternative MI coding:** the primary acute-code definition was compared with a documented broader current-admission definition. The broader definition combines an acute MI code with a historical MI code on the same admission; prior-only MI history is not recast as a current case. This is an operational interpretation because the roadmap does not enumerate broad codes.
4. **Age and sex subgroups:** analyses compare age <65 with age >=65 and recorded female with recorded male, with direct interaction contrasts. The roadmap does not set the age cut point; 65 is documented as the implementation choice.

The recorded numerical claims are consistent with the underlying CSV outputs. A reporting nuance is that 67/95 primary BH findings include 66 physiological outcomes and one technical/support metric; feature counts should preserve that distinction. The broad-code and subgroup BH results are likewise counts over the 95-feature family unless a physiological-only count is explicitly given.

## 3. Numerical robustness assessment

### Phase 5 primary estimates and Phase 6 findings

The primary Layer 2 cohort contains **167,066 admissions from 93,946 patients**, with **7,353 acute-MI admissions** and **159,713 clean controls**. It includes 95 complete handcrafted ECG features. The five-fold patient-group cross-fitted AIPW estimates adjust for age, recorded sex, diabetes, hypertension, CKD, and prior MI. These are adjusted observational contrasts.

At BH FDR 5%, **67/95** feature tests passed: **66 physiological outcomes plus one technical/support metric**. The largest adjusted standardized contrasts included ST_Elev_I (-0.346 SD), T_Amp_I (-0.336 SD), T_Amp_aVR (+0.327 SD), and ST_Elev_aVF (-0.302 SD). Phase 6 confirms that ST and T feature groups have the largest average absolute standardized contrasts (0.162 SD and 0.129 SD, respectively), with lead-dependent directions. Crude-to-adjusted correlation was 0.916; directions agreed for 82/95 features, while adjustment reduced absolute magnitude for 75/95. This is a structured, adjusted association pattern, not a single universal ECG signature.

Layer 1 Phase 5 adjusted risk differences were **+0.69 percentage points** for prior diabetes (95% bootstrap CI +0.42 to +0.95), **-0.51 points** for prior hypertension (-0.70 to -0.30), **-0.17 points** for CKD (-0.59 to +0.31; interval includes zero), and **+5.48 points** for prior MI (+4.67 to +6.41). The prior-MI result is descriptive because prior MI is not interpreted as a causal exposure. Limited propensity overlap remains, particularly for some exposure models.

Phase 6's model-implied feature profiles are exploratory conditional predictions, not observed counterfactuals or clinical interventions. Profile propensities were 0.020, 0.032, and 0.037; profile-specific uncertainty intervals were not estimated. They should not be presented as evidence of what would happen if MI were induced or prevented. The beta-VAE dimensions remain excluded because provenance was unavailable.

### Selection-weighted comparison

Only **191,275/431,231 (44.36%)** denominator admissions had an eligible ECG. The selection propensity range was 0.195–0.864; stabilized weights had a 99th percentile of 2.06, maximum 2.27, and effective sample size of 173,194. All eight measured selection covariates had post-weight absolute SMD below 0.10.

Across 95 features, **89/95** selection-weighted estimates retained the primary direction. The median absolute weighted-versus-primary shift was **0.009 SD** (90th percentile 0.022 SD; maximum 0.056 SD). **69/95** weighted estimates passed weighted BH, and **66 of the 67** primary BH-significant results also passed weighted BH. ST/T mean absolute standardized effects were 0.146/0.128 under weighting, compared with 0.162/0.129 in the primary estimates. Thus the main ST/T pattern is reasonably stable to this measured-covariate weighting, while some features shift and the analysis depends on selection being conditionally ignorable given the modeled variables. It cannot correct selection driven by unmeasured severity, symptoms, care pathways, or clinician ECG ordering.

### Broader current-admission MI-code comparison

The broad Layer 2 comparison contains **181,643 admissions**: **21,930 broad current-MI cases** and the same **159,713 clean controls**, versus 7,353 acute-only cases in the primary cohort. In the 95-feature merge, broad-code and primary standardized estimates have correlation **0.956**, median absolute difference **0.024 SD**, and matching directions for **85/95** features. **76/95** pass BH under the broader definition, compared with 67/95 in the primary definition; **59** primary BH discoveries overlap.

Mean absolute standardized ST/T contrasts decrease from **0.162/0.129 SD** in the primary analysis to **0.126/0.108 SD** under broad coding. ST/T patterns therefore remain visible but are attenuated. Other feature groups do not move uniformly: for example, mean absolute QRS contrast rises from 0.091 to 0.123 SD, while RR falls from 0.128 to 0.029 SD. This is a useful coding robustness check, but it changes case composition and the estimand; the additional historical-code cases do not establish an acute event or its timing.

### Unmeasured-confounding sensitivity

The Layer 1 E-values use an explicitly approximate RD-to-RR conversion based on observed unexposed acute-MI risk, not an exact standardized risk ratio. Point E-values and nearest-null confidence-limit E-values were:

| Contrast | Point E-value | Nearest-null CI E-value | Reading |
|---|---:|---:|---|
| Prior diabetes | 1.66 | 1.48 | A relatively modest unmeasured association could explain away the estimate. |
| Prior hypertension | 1.57 | 1.39 | Likewise modest; the sign is inverse and remains an observational contrast. |
| Prior CKD | 1.28 | 1.00 | CI crosses the null; no robust non-null association is established. |
| Prior MI | Not interpreted | Not interpreted | Descriptive contrast; no causal E-value. |

These values materially limit causal interpretation of the small Layer 1 diabetes and hypertension estimates; the CKD result is already uncertain. For Layer 2, the additive tipping grid shows the omitted-confounder prevalence-imbalance by feature-association product needed to move estimates or confidence limits to zero. It is illustrative, not a fitted confounder model, and does not exclude plausible combinations of unmeasured acute severity, smoking, BMI/lipids, or selection processes. It does not address event timing.

### Age and sex comparisons

Within-subgroup BH results were 66/95 for age <65 (2,551 cases), 57/95 for age >=65 (4,802 cases), 58/95 for female (2,877 cases), and 56/95 for male (4,476 cases). Direction agreement with primary estimates ranged from 85/95 to 89/95. More importantly, direct interaction tests passed BH for **11 age contrasts** and **13 sex contrasts**. Leading age contrasts included ST_Elev_V5, R_Amp_aVR, and ST_Elev_V6; leading sex contrasts included RR_Mean_Global_iqr, R_Amp_aVF, R_Amp_V2, and ST_Elev_V2.

These support feature-specific statistical heterogeneity within the chosen strata, not a uniform age or sex modification of all MI-associated ECG features. Subgroup significance counts alone do not establish between-group differences; interpretation should use the direct interaction estimates, confidence intervals, and multiplicity-adjusted q-values. The cut point is an implementation choice, and the contrasts remain observational.

## 4. Gate 2 assessment

**Decision: Partially satisfied.** This is the best-supported of the three available decisions.

Reasons supporting the gate:

- The main ST/T morphology pattern survives measured-covariate selection weighting and remains visible under the broad current-code definition.
- Weighted estimates are close to primary on the standardized scale overall, and most directions agree.
- Direct interaction contrasts, not comparisons of subgroup p-values, were computed and multiplicity-adjusted.
- The sensitivity work exposes coding, overlap, selection, and confounding limitations instead of hiding them.

Reasons the gate is not fully satisfied:

- E-values for the non-null Layer 1 diabetes and hypertension contrasts are modest and approximate; CKD is null-compatible. Layer 2 tipping calculations do not rule out unmeasured confounding.
- The selection analysis balances measured variables only and requires a measured-covariate selection assumption. ECG features are unavailable for nonselected admissions.
- Broad coding attenuates ST/T means, changes the case definition, and leaves only 59 primary BH findings overlapping; not every sign or significance flag is invariant.
- Age/sex interaction signals are feature-specific and exploratory, with an age boundary not dictated by the roadmap.
- There is no reliable MI onset time relative to the selected ECG. Consequently, the proposed MI-to-ECG temporal direction is not empirically established by these analyses.

Successful completion of the analyses is not itself a reason to pass Gate 2. The evidence clears enough of the stability question to support carefully bounded paper preparation, but it does not clear causal identification or temporal ordering.

## 5. Remaining scientific limitations

- **Temporal ordering:** the diagnosis/admission label does not establish that MI began before the selected ECG. The dataset lacks a reliable event-onset-to-ECG interval for this claim.
- **Selection:** the ECG-selected sample is 44.36% of the adult admission denominator. Weighted transport depends on recorded predictors and cannot reconstruct unobserved ECG features for nonselected admissions without assumptions.
- **Confounding and coding:** risk-factor histories can be under-recorded; relevant factors such as smoking, BMI, lipids, and acute severity are not adequately captured. E-values are approximate and the continuous-outcome tipping grid is hypothetical.
- **Overlap and target:** propensity clipping and limited overlap affect some Phase 5 estimates. Conclusions target the coded, ECG-selected inpatient population and its admission-level observations, not all people with MI.
- **Dependence and clinical interpretation:** ECG features are correlated; 95 feature rows are not 95 independent replications. Statistical significance does not establish clinical importance or diagnostic performance.
- **Exploratory Phase 6 profiles:** model-implied profiles have no profile-specific intervals and limited overlap; they are not treatment-effect or intervention estimates. Latent beta-VAE outputs are excluded.
- **Novelty:** no literature-based comparison has been completed in these deliverables. A novelty claim requires a proper comparison with prior MIMIC-IV-ECG and MI ECG studies.

## 6. Publication feasibility and recommended framing

The project is suitable for development as a **two-layer observational association study**:

1. **Layer 1:** adjusted admission-level associations between recorded chronic risk-factor history and an acute-MI diagnosis among ECG-selected adult admissions. Preserve the small effect sizes, uncertainty, exposure-specific adjustment sets, and descriptive-only prior-MI interpretation.
2. **Layer 2:** adjusted admission-level differences in 95 handcrafted ECG features between acute-MI-coded admissions and clean controls. Report the estimates and intervals, multiplicity correction, feature groups, lead-dependent ST/T directions, and feature dependence.

Describe Phase 6 as a structured feature interpretation and exploratory model-profile exercise. Describe Phase 7 as assumption-dependent robustness checks, including selection weighting, broader same-admission coding, confounding sensitivity, and subgroup interaction tests. The analysis is not evidence that MI caused the ECG differences, and it does not establish one universal MI ECG signature.

Keep three claims separate:

- **Observational association:** supportable with the admission-level population, adjustment, uncertainty, selection, and coding limits stated plainly.
- **Causal effect:** not established. The available timing, confounding, selection, and overlap information do not identify the causal direction or intervention effect.
- **Novelty relative to literature:** not established by the analysis alone. Do not claim novelty until a systematic, well-scoped literature comparison is completed and reported in Phase 8.

This recommendation does not change the original research questions or reopen finalized analysis decisions. It limits the scientific language to what the completed work supports. If the working title or roadmap language implies a demonstrated causal effect, revise that wording only after review and approval; no title or roadmap change is made here.

## 7. Explicit Phase 8 readiness decision

**Ready to begin Phase 8 paper preparation as an observational association paper, subject to user approval of this readiness recommendation.** Gate 2 remains partially satisfied; full satisfaction is not a prerequisite for a defensible observational manuscript when limitations and sensitivity results are reported candidly. Phase 8 must not present the work as establishing that MI caused ECG changes. This review does not start Phase 8 or draft the paper.

## 8. Phase 8 must cover

- The original two-layer research structure and each layer's target contrast.
- Admission-level cohort definition and selection into the ECG cohort: 191,275 selected admissions from a 431,231 adult-admission denominator; 99,214 selected-cohort patients; primary Layer 2 has 167,066 admissions, 7,353 acute-MI cases, and 159,713 clean controls.
- The 95 handcrafted ECG features, their groups, preprocessing/measurement provenance, and the separate technical/support metric; no beta-VAE results.
- Phase 5 adjusted risk/mean differences, patient-level uncertainty, covariate sets, cross-fitting, FDR family, limited overlap, and their observational interpretation.
- Phase 6's deconfounded ST/T feature pattern and the exploratory status, limited overlap, and lack of profile-specific intervals for model-implied profiles.
- All four Phase 7 sensitivity components with the actual estimates, confidence intervals or tipping scales, changed definitions, interaction tests, and assumption limits.
- The unknown MI-onset-to-ECG timing, measured-only selection model, unmeasured confounding, code validity/undercoding, feature dependence, lack of clinical importance inference, and limits to generalizability.
- A literature comparison before any novelty claim; distinguish statistical feature characterization from novelty versus prior work.
- A conclusion restricted to adjusted diagnosis-feature associations in the studied ECG-selected admissions; no causal, temporal, or universal-signature claim.
