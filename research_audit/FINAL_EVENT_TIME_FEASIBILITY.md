# Final Event-Time Feasibility and Research Direction

## Direct answers

1. **Can the existing data reliably identify MI-related event times? No.** No threshold is validated for these assay items, and the admission linkage is incomplete or absent for relevant measurements. No admission has an accepted first qualifying time under a validated threshold. A troponin timestamp is not biological onset even when a threshold is established.
2. **Can the 95 ECG features be investigated without validated event times? Yes, with a different estimand.** The audit records 95 handcrafted features in the master dataset. They can support feature-distribution and diagnosis-based association analyses that do not require ordering each ECG before or after MI onset. Do not rely on threshold-derived labels as a validated outcome; use a clearly defined diagnosis-based outcome and state its limitations.
3. **Is causal MI-to-ECG analysis defensible under the available evidence? No.** Event timing is unresolved, acute-presentation timing labels are not validated, ECG acquisition can be selective, and the workspace lacks an admission-level ECG acquisition denominator for a selection model. A causal temporal effect cannot be supported by these data as currently documented.
4. **Retain the original research question or switch? Switch the primary analysis to an adjusted observational association study.** Retain the broader clinical motivation, but replace the causal/event-time claim with a diagnosis-based association question. Do not describe the result as an effect of MI onset on ECG features.

## Evidence relevant to feasibility

- The source-level threshold audit reports 51002: 0 measurements; 51003: 359,000 rows (149,109 numeric), of which 194,115 have direct admission IDs; 52642: 163 numeric rows, all missing admission IDs.
- Item 51003 has recorded upper reference 0.01 ng/mL on all rows, compared with configured 0.014 ng/mL. Item 52642 has recorded upper reference 0.08 ng/mL on all rows, compared with configured 0.04 ng/mL. Item 51002 cannot be assessed from observations.
- For the 164,885 item-51003 rows missing `hadm_id`, interval linkage yielded 108,577 unique interval candidates, 204 ambiguous matches, and 56,104 with no matching interval. These candidates were not assigned as admissions. None of the 163 item-52642 rows matched a patient ED/admission interval.
- [`EVENT_TIME_COVERAGE_REPORT.md`](./EVENT_TIME_COVERAGE_REPORT.md) records 12,187 acute ICD-coded admissions, 7,604 acute-presentation-labeled ECG rows, and zero accepted event times under a validated threshold. Candidate-relative before/after counts in the earlier audit are explicitly provisional and must not be reported as validated event timing.
- The same report records 375,930 master ECG rows and 95 handcrafted ECG features. The diagnosis audit distinguishes acute ICD-9 410*/ICD-10 I21*/I22* from historical MI codes; diagnosis coding is a possible non-temporal outcome definition, not an exact onset timestamp or perfect clinical adjudication.
- [`ECG_SELECTION_FEASIBILITY.md`](./ECG_SELECTION_FEASIBILITY.md) finds no admission-level ECG acquisition dataset for eligibility, selection modeling, positivity, or inverse-probability weighting. Residual selection bias must be acknowledged; weighting cannot be claimed from the current workspace.

## Recommended adjusted observational design

Use the available diagnosis audit to define acute-MI status at the admission level, and analyze ECG features as associations with that status rather than as changes indexed to a troponin-derived onset. Prespecify the population, unit of analysis, ECG-to-admission linkage, feature handling, covariates, and patient-level clustering for repeated ECGs. Exclude historical MI codes from the acute outcome definition and avoid treating the existing troponin timing labels as ground truth.

Report effect estimates as adjusted associations, not causal effects. State that admission selection into ECG testing, diagnostic coding error, residual confounding, and the absence of validated MI event times limit interpretation. Do not use the design to claim that MI caused a measured ECG feature or to establish pre-/post-event feature trajectories.

If accurate event-relative effects remain essential, the current evidence is insufficient: obtain assay/platform-specific URL documentation, recover or adjudicate the event and admission linkage, establish a valid event-time reference, and obtain the ECG-eligible admission denominator before reopening a temporal causal design. This is a prerequisite list, not a reason to continue tuning the current thresholds.
