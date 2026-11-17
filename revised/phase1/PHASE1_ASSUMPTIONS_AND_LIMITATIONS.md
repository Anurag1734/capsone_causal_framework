# Phase 1 Assumptions and Limitations

## Assumptions requiring empirical assessment

- **Consistency / intervention versions:** a 10-mmHg change in an OMR baseline mean can arise from different behaviors, medication regimens, illness states, or measurement patterns. The modified policy is a hypothetical shift of a measured value, not a unique real-world regimen or proven sustained intervention.
- **Conditional exchangeability:** age, sex, diabetes, hypertension, CKD, and possibly BMI/utilization may not capture smoking, lipids, severity, access, adherence, socioeconomic factors, or other shared causes of BP and MI.
- **Positivity:** prior marginal SBP bins and min–max shifts do not establish support conditional on confounder profiles. Deterministic shifted SBP may be unsupported in subgroups.
- **Temporal order and validity:** OMR date has day precision; same-index-date BP is excluded. Parsing, unit validity, duplicates, and mean reliability require verification. Diagnosis timing may represent detection rather than disease onset.
- **Outcome validity:** ICD-coded admission is an administrative event proxy and may miss events outside the observed health system; first recorded event is not necessarily first biological MI.
- **Selection:** entry into hospital data, survival to index, health-care contact, and OMR BP availability can select patients and open collider paths. Selection models cannot repair unmeasured selection causes.
- **Follow-up and censoring:** acute admission records are intermittent and are not continuous insurance enrollment. Leaving the observed database is not necessarily loss to care, and observed last encounter may be informative.
- **Death:** death ascertainment is incomplete. Available counts differ by unit/table universe: 27,980 patient-level DOD values in an 180,733 patient source universe; 8,592 patient-level in-hospital death timestamps; 8,598 admission-level death timestamps in another universe. Missing death date is not survival. These counts must not be combined.
- **Model specification:** later nuisance models, policy standardization, competing-risk handling, censoring models, and uncertainty procedures can be misspecified. Cross-fitting and robustness estimators do not prove identification.

## Data limitations and scientific consequences

1. **No complete pre-observation history:** exclusion means no documented acute/historical MI by index in available records, not no lifetime MI. Unrecorded prior events can contaminate the incident cohort.
2. **BP selection and frequency:** only 53,956 of 168,915 common-index patients had any valid OMR BP in the two-year window; 1,223 of 3,207 incident cases had such BP. These are aggregate feasibility counts, not the final count-rule cohort. Measurement depends on care and may correlate with risk. Frequent measurements can dominate a mean.
3. **Unmeasured smoking and sparse lipids:** major cardiovascular confounders are unavailable/insufficient in processed data. No fictional observed history or routine imputation is permitted.
4. **Medication capture:** outpatient capture incomplete; prescription, pharmacy, and administration records do not establish outpatient use, adherence, dose, or index exposure. Medication may be a proxy, confounder, or mediator depending on timing.
5. **BMI and other OMR variables:** measurement and temporal validity require actual schema/unit/date checks. Missing BMI may induce additional selection.
6. **Death and observation:** the source does not establish complete death or continuous follow-up. Competing risk and censoring estimates depend on defensible linkage and sensitivity assumptions.
7. **CATE precision:** age/sex/diabetes subgroup case counts are descriptive, not proof of precision. No events-per-parameter shortcut establishes adequate heterogeneity estimation.
8. **Index admission proxy:** coded admission date is not biological onset; acute MI must follow index, but exact onset within an admission is unknown.
9. **External validity:** estimates apply only to selected MIMIC-IV hospital entrants meeting common index, BP, and approved follow-up criteria. Not a community population effect.
10. **Intervention interpretation:** a one-time baseline summary shift does not demonstrate sustained SBP reduction or clinical safety. The candidate intervention is research-only.
11. **Covariate timing:** “documented by index” can still mean a diagnosis was first recorded after some BP readings contributing to the 730-day mean. The recommended pre-window covariate cutoff avoids that ordering problem but can omit recent disease and requires approval.

## Unresolved decisions, consequences, and resolution

| Issue | Consequence | Recommended handling | Resolution evidence / owner |
|---|---|---|---|
| Measurement count threshold | Changes reliability, denominator, and selection | Compare ≥1/≥2/higher-count rules with aggregate diagnostics; recommend ≥2 only after review | Research team approval before construction |
| Follow-up horizon | Changes primary risk estimand and data sufficiency | Review one-year candidate coverage, event accrual, and observation limits; do not pick by effect | Research team approves horizon after aggregate-only audit |
| Death rule | Incomplete death may distort cumulative incidence | Reconcile individual-level vs admission-level source units; competing risk where defensible, underascertainment sensitivity | Data owner/researcher approves linkage and primary rule |
| Censoring/observation end | Potential informative loss and unobserved care elsewhere | Define source cutoff/last-observation proxy; model measured predictors and sensitivity | Research team approves operational rule |
| Prior MI covariate | Redundant under exclusion rule | Omit from primary adjustment; keep exclusion audit. Changing requires explicit population/estimand revision | Team confirms intended exclusion vs covariate list |
| Hypertension meaning/timing | Adjustment may control proxy or downstream diagnosis | Primary candidate adjustment plus alternative DAG/diagnosis timing sensitivity | Clinical/research review of code timing |
| BMI/medications | Validity and missingness/mediation uncertain | Include only with pre-index definitions; medication sensitivity only | Verify source fields and approve definitions |
| Primary estimator | Competing risks and deterministic modified policy complicate generic methods | G-computation candidate; target-specific AIPW/IPW robustness after method review | Statistical reviewer approves target-specific formulation |
| Heterogeneity precision | Subgroup estimates may be too imprecise | Set interval width/minimum detectable interaction before fitting | Team specifies precision target and multiplicity plan |

## Protection of scope and data

This Phase 1 package contains protocol and aggregate evidence only. It includes no patient identifiers, row-level BP readings, predictions, or ECG waveforms. It does not alter original phases, execute treatment-effect analysis, or perform β-VAE work. The repository `.gitignore` excludes `data/` and `*.rar`; future row-level data must remain local and outside revised research outputs.
