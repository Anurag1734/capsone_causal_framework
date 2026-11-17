# Phase 2.0-R — BP measurement-count feasibility

## Scope and source

This is an aggregate feasibility calculation, not Phase 2.1 cohort construction. A transient in-memory index linkage was used only to align OMR readings and derive summaries; no patient-level file was written. Source members were `longitudinal/admissions_chronology.parquet`, `longitudinal/diagnoses_all.parquet`, the patient demographics derivative, and `omr.csv` from `data/raw/longitudinal.rar` / `data/raw/omr.rar`. The two OMR copies were previously verified byte-identical. OMR fields used were `subject_id`, date-only `chartdate`, `result_name`, and `result_value`.

Qualifying BP requires `result_name == Blood Pressure`, successful SBP/DBP parsing, SBP 60–260 mmHg, DBP 20–160 mmHg, SBP>DBP, and `chartdate` in `[index_date - 730 days, index_date)`. The baseline summary is the arithmetic mean SBP; the intervention remains `d1(A)=A-10 I(A>=130)`. No treatment effect was estimated.

## Index reconstruction and reconciliation

The transient reconstruction found 180,733 source patients, 9,703 patients with an acute-MI-coded admission, and 174,650 candidate nonacute index patients. Applying the documented prior acute/historical MI exclusion by calendar date excluded 5,735 candidates (5,735 historical MI; none prior acute MI remained among candidates), yielding 168,915 common indices. The strictly later calendar-date acute MI event rule identified 3,207 first post-index cases and 165,708 without a recorded post-index MI, exactly matching the authoritative reconciliation. It had one patient with multiple nonacute candidate admissions tied on admission timestamp (deterministic `hadm_id` tie-break used). This exact aggregate reconciliation validates the implementation logic at aggregate level; it does not turn this in-memory feasibility table into the final Phase 2.1 cohort.

The qualifying BP aggregate at ≥1 reading exactly matches the authoritative aggregate: 53,956 people and 1,223 cases, with 52,733 BP-eligible patients without a recorded post-index event. The common-index and incident-event denominators also now match exactly.

OMR QC found 300,059 candidate BP records in the fixed window for the reconstructed risk set; none failed parsing, 67 failed range/order checks, and 299,992 passed all stated rules. There were no candidate-patient OMR date parse failures.

## Threshold comparison

| Minimum readings | Eligible patients | First-MI cases | No recorded MI by source end | Eligible retained vs ≥1 | Cases retained vs ≥1 | Mean patient mean SBP | Median patient mean SBP | Median count (IQR) | Median within-person SD (IQR) | Median last-reading gap (IQR), days |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53,956 | 1,223 | 52,733 | 100.0% | 100.0% | 127.66 | 126.50 | 3 (1–7) | 9.49 (6.43–13.26)* | 27 (8–82) |
| 2 | 40,346 | 933 | 39,413 | 74.8% | 76.3% | 127.06 | 126.00 | 5 (3–9) | 9.49 (6.43–13.26) | 22 (6–63) |
| 3 | 31,478 | 722 | 30,756 | 58.3% | 59.0% | 126.57 | 125.67 | 6 (4–11) | 9.93 (7.22–13.38) | 18 (6–50) |
| 4 | 25,564 | 582 | 24,982 | 47.4% | 47.6% | 126.04 | 125.19 | 8 (5–12) | 10.08 (7.58–13.37) | 14 (5–42) |

*At the ≥1 threshold, within-person SD is calculable only for people with at least two readings; it does not describe the single-reading participants. Full q05/q25/q75/q95 SBP, reading-count and timing/frequency distributions are in `PHASE2_BP_THRESHOLD_COMPARISON.csv`.

At ≥2, 13,610 (25.2%) of the ≥1 BP-eligible patients and 290 (23.7%) of their incident cases are lost. The median count rises from 3 to 5, and the retained cohort has an observed within-person SD for every person. This is a meaningful availability/reliability-design improvement over a single reading, but the SD distribution is not materially narrower and repeated OMR readings are not a standardized reliability study. The data therefore support **≥2 as a reasonable primary measurement-count recommendation**, not proof that its mean is clinically more reliable or that selection bias is reduced. ≥3 and ≥4 impose larger losses without a demonstrated reliability advantage here.

## Exposure distribution and measurement intensity

Among ≥2 participants, 40.31% have a patient-level mean SBP ≥130; mean/median patient-level mean SBP are 127.06/126.00 mmHg. The mean patient-level median SBP is 126.84 mmHg. Patient-level mean SBP quantiles are 104.8, 116.2, 136.4 and 153.0 mmHg at q05/q25/q75/q95. The median last valid reading is 22 days before index (IQR 6–63); fixed-window measurement frequency has median 2.50 readings/year (IQR 1.50–4.50).

Frequent measurement changes the pooled reading-weighted summary: at ≥2 the reading-weighted mean is 125.40 mmHg, compared with a patient-weighted mean of 127.06; the top reading-count decile contributes 32.0% of qualifying readings. At ≥1 the corresponding values are 125.58 versus 127.66, and the top decile contributes 39.5%. This supports using one patient-level mean per participant rather than letting frequently measured patients dominate. High/low reading-count decile patient means are descriptive and are included in the CSV.

## Selection and subgroup differences

`aggregates/phase2_0r_bp_retained_excluded.csv` compares retained and excluded participants at each threshold on age, sex, documented diagnoses by index, BMI availability, event count and BP density. By-index diagnoses are included only as descriptive selection characteristics; they are not baseline adjustment variables because they may occur during the BP window. For ≥2, retention differs by age-at-window-start (23.4% <65; 25.0% ≥65) and recorded sex (28.6% female; 18.3% male). Valid pre-window BMI is sparse: 5,075/40,346 (12.6%) at ≥2. These differences show selection into measurement; no weighting was applied, and they do not establish exchangeability of BP-measured and unmeasured patients.

## Recommendation and status

Recommend ≥2 valid readings for the future primary summary, conditional on team approval and the unresolved common-index reconciliation. Preserve ≥1 as a prespecified sensitivity cohort and report ≥3/≥4 as robustness descriptions. Do not use treatment-effect direction to choose the threshold. A reliability improvement is plausible because a second measure exists and within-person variation can be described, but no replicate-measurement validation, correction for measurement error, or evidence that outpatient readings are exchangeable was performed. Selection into OMR BP remains a material limitation.

## Reproducibility

Run `python revised/phase2/scripts/phase2_0r_aggregate_feasibility.py` from the repository root with the configured local archives. The script streams OMR in chunks and writes aggregate tables only. Outputs are not a final exposure dataset and must not be interpreted as a completed Phase 2.1 cohort.
