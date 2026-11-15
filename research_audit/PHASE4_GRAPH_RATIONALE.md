# Phase 4 Graph Rationale

## Source decisions retained

The graph follows the original roadmap's two layers and the Phase 3 decisions. Acute MI is the acute ICD diagnosis on the current admission. Diabetes, hypertension, CKD, and prior MI use the finalized Phase 3 indicators. The roadmap's exposure-specific adjustment sets are retained. The graph treats ECG features as outcomes and keeps ECG availability as an explicit selection mechanism. The 64 beta-VAE features stay excluded.

The data support adjusted observational associations only. Diagnosis codes are not interventions or complete clinical adjudication, and the timing of the selected ECG relative to biological MI onset is unknown. Accordingly, the graph's MI-to-ECG arrow is a proposed causal assumption; estimated associations cannot verify that direction or establish a causal effect.

## Variable roles and adjustment choices

- Age and recorded sex are baseline causes in both layers, not interventions.
- Prior diabetes and hypertension are separate exposures for Layer 1. Their models adjust for age and sex, not CKD.
- The CKD model adjusts for age, sex, diabetes, and hypertension; it does not adjust for prior MI.
- The prior-MI model uses the roadmap's listed adjustment set but is descriptive. Prior MI can mark unmeasured coronary disease, and its relation to current MI is not treated as a discovered causal effect.
- Alternative diabetes/hypertension orderings remain sensitivity assumptions because their ordering is unresolved.
- For Layer 2, adjust for age (flexibly), sex, prior diabetes, prior hypertension, prior CKD, and prior MI. Do not adjust for in-hospital treatment or troponin as though they were baseline.
- Keep the 95 handcrafted outcomes and their Phase 3 groups. `QRS_Dur_Global_count` is a technical/support outcome. Exclude all 64 beta-VAE dimensions.

The exact machine-readable adjustment rows, including the 95 features, are in `PHASE4_ADJUSTMENT_SETS.csv`.

## Selection and empirical scope

The graph includes an edge from MI diagnosis to eligible ECG observation and an edge from unmeasured acute illness severity/symptoms/care pathway to ECG observation. Conditioning on ECG availability can associate MI with severity even after measured adjustment. Severity may also influence the ECG. The Phase 3 selection-bias report found an ECG availability rate of 44.36%, with standardized mean differences of 0.109 for acute MI diagnosis and 0.198-0.270 for several prior comorbidities/MI history. Those existing results are cited as the selection assessment; the Phase 3 selection dataset was not rebuilt or re-audited.

The analysis target remains ECG-selected admissions. Weighting is not assumed to eliminate unmeasured selection. The single selected ECG per admission and acute diagnosis do not reveal MI onset time; no temporal classification or event-time recovery is attempted.

## Conditional-independence reasoning

The roadmap's sparse measured-parent representation of Layer 2 gives each ECG feature the same observed parent set (MI and the six baseline factors) and no feature-to-feature edges. Under that restricted representation, distinct features should be conditionally independent given those parents. The training diagnostic residualizes every physiological feature on that set, using a five-degree-of-freedom cubic spline for age, and summarizes each pair's residual Pearson correlation and residual Spearman correlation.

This is a diagnostic of a restricted implication, not a proof that the full selection-aware DAG is false. Shared electrical physiology, cross-lead construction, measurement processes, and the unmeasured selection mechanism can all induce dependence. The observed residual correlations are too large and widespread to support the measured-parent-only factorization. They identify a specific limitation of the sparse graph representation; the graph is not automatically modified. Clinical review is needed before adding or orienting any new edges.

Layer 1 supplies no exposure-outcome independence to test: the proposed graph explicitly connects each exposure to MI. The alternatives for diabetes/hypertension order and the descriptive prior-MI relation also do not produce a testable independence claim from the available selected-admission variables. ECG availability is constant among rows in the analysis Parquet, so its selection collider cannot be tested there. The existing all-admission selection diagnostics are reused as descriptive evidence only.

## Statistical interpretation

The conditional-independence CSV contains all 4,371 pairs among the 94 physiological features. Pairwise effect sizes are shown without p-values. Absolute partial correlation of 0.05 is used as a screening flag for a small but visible residual association, and 0.10 as a more material-departure flag; these are transparent diagnostic thresholds, not established clinical cutoffs. The technical count measure is excluded from this physiological pairwise screen and retained in the adjustment schedule as a separate sensitivity/QC outcome.

## Roadmap tasks not performed in Phase 4

No Phase 5 effect estimation, cross-fitted estimation, counterfactual prediction, event-time reconstruction, ECG feature re-audit, dataset rebuilding, model retraining, or sensitivity weighting was run. Phase 4 ends with the graph and its diagnostics for review.
