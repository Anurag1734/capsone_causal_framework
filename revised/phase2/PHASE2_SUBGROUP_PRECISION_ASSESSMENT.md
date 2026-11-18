# Phase 2.0-R — Subgroup precision feasibility

## Definitions and reconciliation

Primary subgroup timing follows the Phase 2.0 covariate dictionary: age at the start of the 730-day exposure window, recorded sex, and diagnosis history documented strictly before that window. Aggregate counts are for the aggregate-only common-index risk set and qualifying BP thresholds; no subgroup model or treatment effect was fit.

The older reconciled ≥1-reading case counts are reproduced when using age at **index** (<65: 375; ≥65: 848), sex (male: 651; female: 572), and diabetes documented by **index** (503 documented; 720 with no documented history). Those definitions do not all satisfy the new baseline timing rule. Moving age to exposure-window start changes the ≥1 BP case split to 443/780. Diabetes documented before the window start is zero in the entire cohort; the earliest eligible hospital admission is the index, so there are no earlier MIMIC inpatient diagnosis records from which to ascertain pre-window diabetes, hypertension, or CKD. The by-index diagnosis categories below are descriptive reconciliation only and cannot be treated as eligible baseline effect modifiers or confounders under the current protocol.

## Candidate ≥2-reading subgroup counts

| Prespecified modifier definition | Common-index N | Common-index cases | ≥2 BP N | ≥2 BP cases, any recorded follow-up | First MI by 365 days among ≥2 BP | Recorded deaths before MI by 365 days* | Any later admission by 365 days |
|---|---:|---:|---:|---:|---:|---:|---:|
| Age <65 at window start | 116,063 | 1,254 | 27,139 | 324 | 73 | 954 | 7,975 |
| Age ≥65 at window start | 52,852 | 1,953 | 13,207 | 609 | 154 | 1,746 | 5,078 |
| Female | 91,534 | 1,411 | 26,218 | 450 | 99 | 1,337 | 7,887 |
| Male | 77,381 | 1,796 | 14,128 | 483 | 128 | 1,363 | 5,166 |
| Diabetes documented before window start | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| No diabetes documented before window start | 168,915 | 3,207 | 40,346 | 933 | 227 | 2,700 | 13,053 |

*These are recorded deaths under the source quality/date-order rules, not complete mortality. “Any later admission” is a healthcare-record contact, not continuous follow-up. Full counts, missingness, BP distributions and alternative thresholds are in `aggregates/PHASE2_SUBGROUP_PRECISION_TABLE.csv`.

The primary age-at-window-start ≥2 split has 324 versus 609 cases; sex has 450 versus 483. At index age, the ≥2 counts are 269 versus 664. The pre-window diabetes split is non-estimable because it has no observed variation. Using diabetes documented by index yields 6,834 BP-eligible / 383 cases versus 33,512 / 550 for ≥2, but that documentation can arise during the BP exposure window and is not a temporally valid primary subgroup. BMI is available before the window in 5,075/40,346 (12.6%) of ≥2 participants; it is missing for 87.4%, and cannot repair the missing diagnosis history.

## Precision sensitivity, not causal power

The CSV gives a deliberately illustrative binomial sensitivity calculation for the difference in a single fixed-horizon outcome risk between two subgroup categories, using the ≥2 eligible subgroup sizes, assumed common risks 1%, 2.5%, and 5%, 80% power, two-sided Bonferroni alpha 0.05/3 (conservative first-step analogue to Holm), and independent complete outcome ascertainment. At assumed risk 2.5%, the approximate detectable subgroup risk differences are 0.54 percentage points for age-at-window-start groups and 0.53 points for sex; the by-index diabetes descriptive split is about 0.67 points. These values are *not* treatment-effect interaction MDEs, are not based on identified 365-day risks, and do not account for competing death, unknown observation, support loss, model complexity, or within-person policy prediction covariance.

Consequently, event counts alone do not establish adequate precision. A genuine causal interaction MDE/interval-width assessment requires an approved, estimable outcome/censoring process, valid pre-window modifier measurement, actual overlap/support, and design simulation under the eventual event-process estimator. No clinical minimum difference or CI-width target is invented here.

## Analysis recommendations for team review

- Age and sex may be described as candidate modifiers using the protocol’s window-start age and recorded sex, with estimates labeled exploratory until a precision target and valid follow-up are approved.
- Diabetes heterogeneity is **not assessable under the current pre-window diagnosis rule**. The team must decide whether the research question requires this modifier and whether a revised, temporally defensible measurement rule is acceptable; no such change is made here.
- If subgroup analyses are later authorized, report direct interaction contrasts and a joint omnibus heterogeneity test, with Holm family-wise correction across age, sex, and diabetes. Treat unavailable diabetes strata as unresolved rather than silently testing the by-index proxy.
- Do not fit CATE models or causal forests in this remediation task.

**Status:** precision evidence is descriptive and scenario-based only. Researcher approval is required for MDE/interval-width targets, subgroup interpretation, and any modification to diabetes ascertainment timing.
