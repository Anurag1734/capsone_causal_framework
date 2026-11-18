# Phase 2.0-R — Death and censoring reconciliation

## Source-table inspection

All checks used local archive members without modifying or extracting source archives. `admissions_chronology.parquet` is admission-level (431,231 unique `hadm_id` rows) and contains `admittime`, `dischtime`, `deathtime`, and `hospital_expire_flag`. `observation_end.parquet` and `patients_demographics.parquet` are patient-level and key by `subject_id`; the former contains `last_admittime`, `last_discharge`, `in_hospital_deathtime`, `dod`, `is_dead`, and `observation_end`, while the latter contains a separate `dod` alongside demographics.

The `observation_end` field is not a global data end. Among 180,733 linked patients it equals DOD for all 27,980 records with DOD and equals last discharge for all 152,753 records without DOD. This describes a per-patient last known event/encounter in the extract; it does not establish ongoing observation after last discharge. The admission maximum (admittime 2212-04-06; dischtime 2212-04-12) is only the largest shifted timestamp present, not a verified release boundary.

## Linkage, duplicates, and internal consistency

| Source finding | Aggregate | Interpretation |
|---|---:|---|
| Admission death timestamps | 8,598/431,231 admissions | Admission unit; 8,592 distinct patients |
| Timestamp within its admission interval | 8,041/8,598 | 25 before admit, 532 after discharge; 557 require source review |
| Repeated distinct death timestamps | 6 patients | All six have multiple different timestamp rows; not safely reducible without review |
| Patient in-hospital timestamp | 8,592/180,733 | Each agrees exactly with a linked admission timestamp among the 8,592 patient-level timestamps |
| Observation-end DOD | 27,980/180,733 (15.5%) | 152,753 (84.5%) missing; missing is unknown vital status |
| Demographics DOD | 29,076/299,712 | Different and wider patient universe; do not combine denominators |
| Shared DOD keys | 180,733 patients | All 27,980 nonmissing DOD values agree exactly; no discordance or one-source-only DOD among shared keys |
| Acute-MI-coded patients in all-history source | 9,703 | 3,510 have DOD; 6,193 have no recorded DOD |
| DOD date vs first acute-MI admission among those 3,510 | 0 before / 54 same day / 3,456 after | Same-day ordering is unresolved with date-only DOD |
| Exact in-hospital timestamp vs first acute-MI admission | 1,450 paired: 2 before / 0 tie / 1,448 after | Two records are temporally concerning and need review |

The patient and admission counts are deliberately reported separately. Exact agreement among observed records supports linkage integrity for those records, not complete death capture.

## Common-index risk-set reconciliation

The aggregate-only implementation found 168,915 indices and 3,207 first acute-MI admissions strictly after the index calendar date, matching the authoritative reconciliation. In this risk set, 24,543 have DOD available and agreeing across patient sources; 144,372 have no such agreeing DOD (85.5%). A unique admission death timestamp within its admission interval is available for 6,813 patients. These death sources overlap; do not sum them as independent deaths. Five risk-set patients have multiple distinct admission death timestamps. Among agreeing DOD records, 10 dates precede the index date, 254 fall on the index date (order unknown), and 24,279 are after index. The unique quality-screened timestamps are all after the index timestamp. Death records on or before index are not follow-up competing events.

Source-consistent recorded death-before-MI counts by elapsed horizon are given in `aggregates/PHASE2_FOLLOWUP_HORIZON_COMPARISON.csv` and the death-source comparison table. Exact timestamps are used only when unique and inside an admission interval. Date-only DOD is classified before MI only if strictly earlier by calendar date; same-day DOD/MI is left unordered. Date-only deaths on a horizon boundary are also not ordered to elapsed time within that day.

## What the data can and cannot identify

Reliable observed deaths can be represented as competing events, subject to the timestamp/date rules above. The majority of the source-linked patient universe has no DOD (84.5%); missing DOD cannot be set to survival. Neither `observation_end`, last discharge, last admission, nor a maximum shifted record timestamp provides a patient-level censor time or a shared administrative end. Therefore, complete real-world fixed-horizon MI cumulative incidence is **not identified by the current linkage alone**. The data show first MI admissions recorded in this hospital dataset, not continuous health-system surveillance.

## Recommended handling and sensitivity scenarios

1. Keep death as a competing event in the scientific estimand. Do not start the primary CIF estimator with unknown deaths classified as alive.
2. Seek a validated, sufficiently complete death linkage and a documented source-wide availability boundary before attempting an identified competing-risk analysis.
3. If no improved linkage becomes available, require team approval for explicit missing-death sensitivity scenarios. At minimum vary the fraction of patients with missing DOD who die before each horizon from 0% to 100%, and place assumed deaths early, midpoint, and late; separately retain same-day MI/death ambiguity. The 0% scenario is an optimistic assumption, not an observed fact.
4. Do not censor at last encounter or treat no later admission as loss-free survival. A censoring model would require actual individual observation-end times, conditional independent censoring given measured history, censoring positivity, correct model specification, and adequate measurement of common causes of MI and loss of observation. Those inputs are not currently available.

**Status:** internal consistency of observed death sources is partially supported; mortality completeness and the observation process fail the primary causal-incidence gate. No effect or censoring model was fitted.
