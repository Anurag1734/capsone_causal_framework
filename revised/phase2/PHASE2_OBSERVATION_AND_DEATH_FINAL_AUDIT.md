# Phase 2 Observation and Death Final Audit

## Sources checked

| Source | Fields/coverage found | What it supports | What it does not support |
|---|---|---|---|
| `admissions.csv` / `admissions_chronology.parquet` | `subject_id`, `hadm_id`, admit/discharge, ED times, admission death time, hospital-expire flag; chronology has 431,231 admissions / 180,733 patients | Subsequent recorded hospital encounters; admission-level event/death chronology | Continuous patient observation, outpatient care, survival between encounters, outside-system events |
| `patients.csv` / `patients_demographics.parquet` | Patient key, demographics, DOD; prepared demographics table has 299,712 rows in a wider source universe | Age/sex derivation and partial date-of-death evidence | Complete vital status; missing DOD is not survival |
| `observation_end.parquet` | Patient-level last admission/discharge, in-hospital death time, DOD, `is_dead`, `observation_end`; 180,733 source-universe patients | Derived record endpoint and available death fields | A verified data release boundary or individual censoring/observation process |
| `diagnoses_all.parquet` / MI derivatives | Admission-keyed diagnosis codes and dates | First acute-MI-coded admissions within observed records | MI occurrence outside the observed hospital system |
| `omr.csv` and OMR coverage catalogue | Patient/date measurements, including outpatient BP; aggregate catalogue by measurement name | BP measurement availability and dates | Outpatient visit dates, care enrollment, or complete outcome capture |
| `prescriptions.csv`, `emar.csv` | Prescription/order rows (`hadm_id`, `starttime`, `stoptime`, drug etc.); eMAR rows (`hadm_id`, `charttime`, `event_txt`) | Recorded medication orders/administration events during recorded encounters | Outpatient use/adherence, insurance coverage, or continued observation |
| `labevents.csv`, prepared lab catalogue | Admission-linked lab events; 26-row aggregate catalogue with timestamps and coverage counts | Selected lab measurement availability in recorded care | Follow-up observation. LDL and HDL are absent from the prepared catalogue. |
| Master ECG splits | ECG timestamps, admission/patient keys, outcome labels and clinical feature flags; test split schema only inspected | Features in an ECG-selected dataset | Complete admissions/encounter follow-up, enrollment, or observation outside selected ECG records |

Raw CSV headers were read only. Relevant headers include admissions with `admittime`, `dischtime`, `deathtime`, `edregtime`, `edouttime`; patient DOD; prescription `hadm_id/starttime/stoptime`; eMAR `hadm_id/charttime/event_txt`; and lab `hadm_id/charttime`. The local `data/` tree contains only the six archives; there is no local outpatient encounter/claims/enrollment file, no standalone `features_comorbidities.csv`, `features_treatments.csv`, `features_labs.csv`, or `features_vitals.csv`. The longitudinal prescription summary reports 15,416,708 rows, 365,442 admissions and 158,421 patients in its legacy source universe. The lab catalogue includes HbA1c (223,244 measurements; 74,715 patients; 30,176 admissions; legacy cohort 41,959) but no LDL or HDL rows. These aggregates do not establish temporal availability before the Phase 2 exposure window.

## Death-source reconciliation

The prior Phase 2.0-R reconciliation was independently checked against actual prepared schemas and retained as the current aggregate count evidence:

- `observation_end.parquet`: 27,980/180,733 patients have DOD; 152,753 (84.5%) do not.
- `patients_demographics.parquet` and `observation_end.parquet` agree on shared nonmissing DOD values. In the common-index set, 24,543/168,915 have an agreeing DOD; 144,372 do not.
- There are 8,592 unique patient-level in-hospital death timestamps, matching admission-level linkage for observed timestamps. In the common-index cohort, 6,813 have a unique quality-screened timestamp within its admission interval. These counts overlap with DOD and are not additive.
- Of 8,598 admission-level death timestamp rows, 8,041 fall within their admission interval, 25 precede admission and 532 follow discharge. Six patients have multiple distinct death times; these are not silently resolved.
- `observation_end` equals DOD when DOD is available and otherwise equals last discharge; it is a derived per-person record endpoint, not a common censor date.
- Date-only DOD and admission timestamps can disagree within a calendar day; same-day MI/death ordering remains ambiguous.

These are record-source findings, not complete mortality ascertainment. Unknown DOD remains unknown vital status. No linked outside-system death or vital-registration source is present locally.

## Horizon and observation findings

The recorded first-MI admission counts and subsequent encounter counts at 90/180/365/730 days are in `aggregates/PHASE2_FOLLOWUP_HORIZON_COMPARISON.csv`. At 365 days the aggregate includes 898 recorded first-MI admissions and 47,426 participants with a later admission record in the interval; 121,489 have no such later admission. The latter count is not an event-free or alive count. Continuous observation status is unknown for all 168,915 participants at every horizon.

Observed source maxima (admission 2212-04-06; discharge 2212-04-12) are record extrema on de-identified dates. No archive release manifest or source table establishes a common administrative extraction date or complete opportunity window. A later admission confirms another record, not uninterrupted observation; the last encounter does not mark censoring. OMR BP dates and inpatient labs/medications do not fill the gap between hospital encounters.

No source supplies continuous enrollment, outpatient visit/claim history, loss-to-follow-up dates, observation start/end, or evidence of care outside the MIMIC hospital. **No defensible individual censoring rule can be operationalized from available sources.** A censoring model cannot be fit without observed censor times and would additionally require conditional independent censoring, positivity, correct specification and adequate measured predictors. Synthetic censor times or using last discharge as censoring are not accepted.

## Decision

Death may be a competing event in the scientific estimand, but the observed linkage does not identify complete competing-risk cumulative incidence. No tested horizon is defensible for complete first-MI risk with these observation data. Any restricted record-capture estimand would require a verified source boundary and team approval and must be labeled as probability of a recorded hospital event, not complete clinical incidence. Further detail and options appear in `PHASE2_IDENTIFIABILITY_AND_ESTIMAND_DECISION.md`.
