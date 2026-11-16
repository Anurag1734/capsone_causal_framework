# Phase 8 Causal Methodology Audit

**Scope:** read-only review of finalized Phase 3–7 reports/results and the Phase 8 manuscript, tables, captions, and figures. No estimator was refit and no Phase 3–7 result was changed.

## Framework, estimands, and DAG

The two-layer structure is stated consistently: Layer 1 contrasts recorded risk-factor history groups on acute MI coding among ECG-selected adult admissions; Layer 2 contrasts ECG feature distributions across acute-code admissions and clean controls. Phase 4 correctly labels its DAG as a proposed assumption set rather than a graph learned from data. The selection mechanism and descriptive-only prior-MI comparison are documented.

The DAG's adjustment sets follow the Phase 4 rows. Age and recorded sex are included for the Layer 1 contrasts; CKD adds diabetes and hypertension; prior MI adds the listed histories but is not interpreted causally. Layer 2 adjusts for age, recorded sex, diabetes, hypertension, CKD, and prior MI. These are roadmap assumptions, not empirically proven sufficient adjustment sets. The diabetes/hypertension/CKD ordering is uncertain, and the sparse graph's conditional-independence implication is contradicted by observed feature dependence; the project appropriately does not learn or orient new edges from those checks.

The manuscript now calls the empirical targets adjusted marginal observational contrasts. AIPW's double-robust property concerns nuisance-model specification under causal identification assumptions; it does not provide identification. The data do not verify exchangeability, temporal order, positivity, or selection exchangeability. In particular, MI onset relative to the selected ECG is unknown, so the diagnosis-to-feature arrow cannot be read as an established temporal effect.

## Estimation and inference

- AIPW, five-fold patient-group cross-fitting, [0.01, 0.99] propensity clipping, validation-selected age spline degrees of freedom, and patient-level bootstrap procedures match the Phase 5 documentation. Fold assignments are by patient.
- Bootstrap confidence intervals resample patient-level cross-fitted scores while holding nuisance predictions fixed. Thus the intervals reflect cluster sampling uncertainty conditional on fitted nuisance predictions and do not include nuisance refitting uncertainty. This caveat is now stated in the manuscript methods.
- The reported p-values use patient-clustered influence-score Wald inference, while the intervals are percentile patient bootstrap intervals. These are distinct procedures and should continue to be named separately.
- BH controls the feature-family false discovery rate over 95 tests; the 67 discoveries include 66 physiological features and one technical/support measure. Physiological group omnibus tests use Holm correction across seven groups. Direct subgroup interaction p-values use BH; within-subgroup discovery counts are not interaction tests.
- The 95 outcomes are correlated. They cannot be presented as 95 independent replications. Effect sizes and feature-group patterns should lead interpretation, with significance counts secondary.

## Positivity, confounding, and selection

Propensity clipping affected 9.96% of CKD exposure estimates, 12.37% of prior-MI estimates, and 13.63% of Layer 2 estimates. Treated-weight effective sample sizes were 4,554, 4,690, and 3,958, respectively. These indicate limited overlap and make estimates more dependent on model extrapolation/clipping choices; clipping does not establish positivity.

Only 191,275/431,231 adult admissions (44.36%) had an eligible ECG. Phase 7 weighting used measured covariates only. Balance on these variables is useful but does not remove selection through unmeasured severity, symptoms, clinician ordering, or care pathways. It cannot supply ECG features for unselected admissions without assumptions.

Layer 1 approximate E-values (diabetes 1.66, nearest-null CI 1.48; hypertension 1.57, CI 1.39) are modest. CKD is compatible with the null. Prior MI remains descriptive. The Layer 2 additive tipping calculation is an illustrative bias scale for a simplified binary omitted factor, not an estimated confounder model; it does not exclude plausible confounding. Neither approach addresses diagnostic incorporation or event timing.

## Diagnostic incorporation and interpretation

ECG findings may contribute to the clinical diagnosis of MI. The comparisons of ECG features by MI-coded status can therefore partly reflect diagnostic incorporation and documentation practice, rather than physiological change following infarction alone. The manuscript and abstract now state this explicitly. Since the source outputs do not independently adjudicate diagnosis without ECG, the contribution cannot be quantified here.

The Layer 1 hypertension estimate is a small inverse observational association, not a protective effect. Diabetes is also small in absolute terms and has a modest approximate E-value. CKD is null-compatible. Prior MI is descriptive. Layer 2 estimates are presented as standardized effect sizes and group patterns, with lead-dependent signs and no universal-signature or causal claim. Phase 6 fixed-profile predictions remain exploratory and are not observed counterfactuals.

## Potential additional analyses

No additional analysis was run. Candidate analyses and their estimands, assumptions, value, and scope implications are listed in `PHASE8_ADDITIONAL_ANALYSIS_RECOMMENDATIONS.md`. None is required to correct a demonstrated computation error in the saved primary outputs. Additional analyses require explicit approval because they would add sensitivity work beyond the completed Phase 7 set.

## Conclusion

The package supports carefully qualified adjusted associations in the observed, ECG-selected admission population. It does not establish that MI preceded the selected ECG or caused the measured differences. The main methodological improvements made here are reporting changes: diagnostic incorporation is explicit, estimation targets are distinguished from causal effects, and limitations of overlap, selection weighting, bootstrap uncertainty, correlated features, and tipping analyses are prominent.
