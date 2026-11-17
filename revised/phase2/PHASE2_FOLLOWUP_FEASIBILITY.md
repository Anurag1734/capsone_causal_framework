# Phase 2.0-R — Follow-up horizon feasibility

## Scope and definitions

The aggregate pipeline reconstructed one common index per person in memory, linked first post-index acute-MI admissions and source death records, and produced only group-level summaries. It used the same ICD-9 `410*`, ICD-10 `I21*`/`I22*`, historical ICD-9 `412`, and ICD-10 `I25.2` rules and strict calendar-date index exclusion. The resulting 168,915 people and 3,207 first post-index cases match the authoritative reconciliation. This is a feasibility audit, not a persisted Phase 2.1 cohort.

The four requested horizons are elapsed 90, 180, 365, and 730 days from index. A recorded event is a first coded acute-MI admission with event time after the index date. A subsequent admission is a later recorded hospital encounter; it is evidence of another record, not proof of continuous surveillance. Absence of an encounter is not evidence of survival or no MI.

## Aggregate horizon results

| Horizon | First MI events by horizon | Confirmed recorded deaths before MI by horizon* | Any later admission in horizon | No later admission in horizon | Median MI time among horizon events (days) | Continuous observation ascertainable |
|---:|---:|---:|---:|---:|---:|---|
| 90 | 415 | 7,786 | 32,469 | 136,446 | 33.1 | No |
| 180 | 616 | 10,328 | 39,541 | 129,374 | 56.2 | No |
| 365 | 898 | 13,918 | 47,426 | 121,489 | 106.8 | No |
| 730 | 1,321 | 16,622 | 56,565 | 112,350 | 202.0 | No |

*Recorded deaths classified before MI only when a quality-screened timestamp orders before MI, or a source-consistent date-only DOD is strictly earlier by calendar date; same-day date-only ties are not ordered. Death source completeness remains poor. The full output gives denominators, date-only/timestamp rules, quartiles, and source maxima.

Across all horizons, 24,543/168,915 patients have a DOD date agreeing between the two patient-level sources; 6,813 have a unique in-hospital death timestamp that falls inside an admission interval. These sets overlap and must not be added. The database field `observation_end` is per-patient: in the source universe it equals DOD for all 27,980 patients with DOD and equals last discharge for all 152,753 without DOD. This is not a shared database cutoff or evidence of continuous observation.

The source has 74,155 patients with any later admission at some point after index; 94,760 have no later admission record. Even for those with later records, median time to the last subsequent encounter is 646.9 days (IQR 108.6–1,671.1) among people with a later record. These are encounter-time summaries only. The median event time by horizon and its q25/q75 are available in `PHASE2_FOLLOWUP_HORIZON_COMPARISON.csv`.

## Administrative boundary and observation status

The maximum observed source admission/discharge timestamps are 2212-04-06 and 2212-04-12, respectively. These maxima are record extrema, not verified administrative extraction limits. MIMIC timestamps are de-identified/shifted; a single maximum calendar date cannot establish a common patient-level opportunity window. Archive metadata and the local source tables provide no independently verified end-of-surveillance date. No patient-level continuous enrollment or observation indicator is available. The current linkage therefore leaves continuous observation status unknown for the entire risk set; an administrative truncation rule cannot be defensibly operationalized from these sources alone.

`last_discharge`, `last_admittime`, and a later encounter can describe record recency but cannot be used as censor dates under the present evidence. Last hospital encounter does not establish subsequent survival or absence of an MI elsewhere. Patients without another record are not classified as event-free through a horizon.

## Decision

**365 days is not empirically defensible as a fixed-horizon cumulative-incidence estimand with the current observation data.** It remains the candidate horizon for researcher review, but the horizon table cannot establish complete outcome opportunity at 365 days. Shorter horizons also lack continuous observation and do not solve this problem; longer horizons increase recorded events but do not repair ascertainment. There is no evidence-based alternative horizon to recommend as identified incidence.

The current data support descriptive counts of first coded admissions recorded within elapsed time after index. They do not identify complete fixed-horizon MI risk. Researcher approval alone cannot supply missing follow-up data; before causal estimation the team must either obtain a defensible observation/censoring source or explicitly accept a restricted interpretation of hospital-record capture and its assumptions. No treatment effect was estimated.
