# Phase 2 — Follow-up, Death, and Competing-Risk Specification

## 1. Target event process

Time zero is the common index admission timestamp. Follow-up horizon candidate is `τ=365 elapsed days`; `τ` remains subject to aggregate feasibility and research-team approval. Evaluate 90, 180, 365, and 730 days without selecting a horizon based on effect estimates. Event is the first ICD-defined acute MI admission strictly after index. Death before first MI competes with MI for a cumulative-incidence estimand; it is not treated as ordinary independent censoring.

## 2. Death-source aggregate reconciliation

Read-only source-member reconciliation is in `aggregates/death_source_reconciliation.csv`; script is `scripts/phase2_0_death_source_reconciliation.py`. It streams selected longitudinal Parquets in memory and writes aggregate counts only.

| Source | Aggregate result | Interpretation |
|---|---:|---|
| `admissions_chronology.parquet` | 8,598 admission rows with deathtime among 431,231 admissions | Timestamp is admission-linked; 8,592 distinct patients, with 6 extra timestamp rows across 6 patients |
| Admission timestamp interval check | 8,041/8,598 within admit–discharge; 25 before admission; 532 after discharge | 557 timestamps are temporally outside that admission interval; require investigation before using as competing events |
| `observation_end.parquet` | 8,592/180,733 patient rows with in-hospital death timestamp; 27,980/180,733 with DOD | Patient-level linked source universe; missing DOD is unknown, not alive |
| `patients_demographics.parquet` | 29,076/299,712 with DOD | Wider patient universe; do not divide by 180,733 or combine as if same denominator |
| DOD source consistency | The 27,980 shared nonmissing DOD dates agree exactly between demographics and observation-end; no discordance | Strong date agreement for observed values, but says nothing about missing-death sensitivity |
| In-hospital timestamp source consistency | For 8,592 patients with both sources, admission-level latest timestamp and observation-end timestamp agree exactly | Cross-source agreement among recorded in-hospital deaths; not complete mortality capture |
| First acute-MI-coded patients in all-history diagnosis source | 9,703 patients; 3,510 have DOD | This is not the 3,207 common-index incident cohort |
| DOD relative to first acute-MI admission among those 3,510 | 0 earlier; 54 same calendar day; 3,456 later | Day-precision ties have unknown within-day order; 6,193/9,703 have no DOD |
| Exact in-hospital death timestamp relative to first acute-MI admission | 1,450 patients had both; 2 timestamps precede, 0 tie, 1,448 follow | The two timestamps preceding a later first acute-MI admission are internally concerning and require source-quality review; no patient-level rows are included |

Counts are source-specific and units are preserved. The 27,980 DOD values cover only 15.5% of the 180,733 admission-linked source universe (152,753 missing); among the 9,703 patients with any acute-coded admission, 6,193 lack DOD. The patient-level linkage is structurally available through `subject_id`, but completeness is inadequate to claim true death-before-MI cumulative incidence from this linkage alone. Admission timestamps are precise but include 557 out-of-interval records, 6 patients with multiple distinct death timestamps, and two death timestamps before a later first acute-MI admission; validate these anomalies.

**Decision:** maintain the scientific primary estimand as MI cumulative incidence with death competing, but mark it **not currently identified/estimable from available linkage alone**. Do not turn missing death into survival. Before estimation, either obtain/validate complete enough death linkage or approve explicit missing-death sensitivity assumptions and limit interpretation. The currently available mortality sources support source reconciliation, not a complete competing-risk analysis.

## 3. Horizon feasibility

`aggregates/followup_horizon_feasibility.csv` records 90/180/365/730-day fields as unavailable rather than zero. The supplied 3,207 event count is over the common-index source follow-up before censoring, not allocated by elapsed horizon. There is no approved row-level index risk set or individual observation-status data in the supplied aggregate reconciliation. The archive's admissions chronology has last recorded admissions/discharges, but a person's last encounter is not proof of continuous observation to 90/180/365/730 days or survival thereafter.

**Recommendation:** preserve 365 days as the candidate primary horizon because it is the Phase 1 proposal and fixes an interpretable contrast. The evidence does not establish that 365-day ascertainment is defensible. Do not substitute 90/180/730 without team approval. The horizon comparison must be completed in aggregate before construction/estimation and never selected by effect results.

## 4. Observation end and censoring rule

1. Verify a source-wide administrative extraction boundary from dataset release/provenance documentation and confirm all input tables share the coverage period. The maximum observed `admittime`/`dischtime` is a record maximum, not by itself proof of administrative completeness.
2. If verified, set the technical administrative boundary `T_admin` to that documented common data cutoff; administratively truncate potential follow-up at `min(index+τ,T_admin)`. Report how many index dates lack full calendar opportunity to reach τ. This handles database truncation only.
3. Do not use last admission/discharge as a substitute for `T_admin` or assume a person is observed/alive from last encounter through T_admin. A person can have care/events outside the MIMIC hospital system.
4. A patient-level censoring process may be modeled only if individual censor/observation times are actually observed and represent loss of outcome capture. Required assumptions: conditional independent censoring given measured baseline/timed history; censoring positivity in every target profile; correct censoring model; correct time ordering; and no important unmeasured causes of loss and MI after conditioning. Selection/inverse-probability weights cannot repair unknown censor dates or unmeasured observation.
5. Current sources do not establish continuous enrollment or patient-level observation end, so a censoring model is not currently operational. If no defensible observation process becomes available, the population risk contrast is blocked; report data-system event capture descriptively only, not as complete fixed-horizon incidence.

## 5. Required missing-death sensitivity scenarios

If death linkage remains incomplete, no single scenario is treated as truth. Report the observed-death primary candidate only as conditional on recorded deaths, and conduct explicit sensitivity scenarios for the fraction of patients with missing DOD who die before τ (a grid from 0% through 100%, with prespecified intermediate values) and timing of those unobserved deaths (early, midpoint, late in follow-up). Recompute competing-risk incidence under each scenario, distinguish same-day MI/death ties, and report the range. The 0% scenario explicitly assumes missing DOD means survival and is only an optimistic sensitivity case, never a silent default. Add a missingness model using pre-index predictors only as a secondary MAR analysis; it cannot address MNAR death capture. Approval is needed for the scenario grid before implementation.

## 6. Decision status

- Fixed event definition and competing-risk estimand: **finalised design choice**.
- 365-day horizon: **recommended, empirical validation required**; current horizon-specific table is unavailable.
- Death completeness: **blocked by incomplete source ascertainment** despite strong agreement among recorded values.
- Individual censoring / continuous observation: **blocked by unavailable data**.
- No effect estimation is permitted until source boundary, death, censoring and horizon gates pass.
