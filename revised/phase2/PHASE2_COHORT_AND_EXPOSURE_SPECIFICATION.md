# Phase 2 — Cohort and Exposure Specification

> **Current status:** Phase 2.0-R completed the >=1/>=2/>=3/>=4 aggregate comparison; see `aggregates/PHASE2_BP_THRESHOLD_COMPARISON.csv`. The at least 2 threshold is recommended but requires team approval. No patient-level cohort was constructed. Prepared-source review finds no pre-window diabetes, hypertension or CKD records under the earliest-index rule; see `PHASE2_BASELINE_DIAGNOSIS_TEMPORAL_VALIDATION.md`. Gate 0 remains failed.

This is an implementation specification, not a constructed cohort. No patient-level cohort or final exposure variables were created in Phase 2.0.

## 1. Target population and keys

Target: MIMIC-IV patients who enter the observable hospital cohort and meet common index eligibility; not a general population. Use `subject_id` for patient identity and `(subject_id, hadm_id)` for admission linkage. One index record per patient. The primary outcome is first acute-MI-coded admission after index; later events do not create repeat outcomes.

## 2. Candidate common index algorithm

1. Build admission-level diagnosis flags from `diagnoses_all.parquet`, grouping code rows by `(subject_id, hadm_id)` and preserving ICD version.
2. Acute MI codes: ICD-9 `410*`; ICD-10 `I21*` or `I22*`. Historical MI: ICD-9 `412`; ICD-10 `I25.2` (normalize dot punctuation without dropping code/version).
3. For every patient with a first acute-coded admission, select the earliest eligible nonacute admission strictly before that first acute admission as candidate index. For those without a recorded acute event, select the earliest eligible nonacute admission under identical rules.
4. Exclude if an acute or historical MI code is documented on the index admission or any admission on/before index. Do not later re-enter patients with earlier documented MI. This is a recorded-history exclusion, not proof of no lifetime MI.
5. Event time is first acute-coded admission timestamp strictly after index. An admission date/time is an administrative clinical-record proxy, not biological onset. A patient without a subsequent code is classified as no recorded event by the relevant data end, not known lifetime event-free.
6. Do not select controls by looking forward and requiring no later MI. A later first event makes the person an incident case at that time.
7. Eligibility details not fully represented by the prior aggregate reconciliation (e.g. invalid admission date/transfer resolution) must be validated and frozen before cohort construction. No extra clinical exclusions may be invented.

## 3. Exposure window and BP QC

`exposure_window_start = index_date - 730 calendar days`  
Window: `[exposure_window_start, index_date)`  
Source: OMR `omr.csv`; byte-identical copies verified in `hosp.rar` and `omr.rar` (SHA-256 recorded in `aggregates/omr_archive_comparison.csv`). Documented columns: `subject_id`, `chartdate`, `seq_num`, `result_name`, `result_value`. OMR has no documented `hadm_id`; link by `subject_id`, not admission.

Select `result_name == "Blood Pressure"`; parse both components from `result_value` as SBP/DBP. A reading is valid only when both parse as finite numeric values and SBP 60–260 mmHg, DBP 20–160 mmHg, and SBP>DBP. Normalize whitespace/decimal formatting only; do not infer units from implausible values. Date eligibility is strict `chartdate < index_date`; same-day readings are excluded because time-of-day is absent. The 730-day lower boundary is inclusive.

For each patient/window threshold, retain count, arithmetic mean SBP (primary summary candidate), median, within-person SD/IQR, date span, readings per observed month, and BP missingness. Do not treat readings as independent people. Check duplicate rows, same-day repeated measurements, and frequent-attender influence; report count-based summaries at patient level.

## 4. Measurement-count threshold decision

**Primary recommendation:** at least 2 valid readings in the fixed 730-day window, conditional on aggregate retention, case count, measurement reliability, and selection review. Compare ≥1, ≥2, ≥3, and ≥4. Do not choose by effect direction.

Phase 2.0-R completed the threshold comparison: >=1/>=2/>=3/>=4 valid readings yield 53,956/40,346/31,478/25,564 eligible patients and 1,223/933/722/582 recorded first-MI cases. The at least 2 threshold retains 74.8% of the at least 1 BP population and 76.3% of its cases; it remains a recommendation requiring team approval. See `aggregates/PHASE2_BP_THRESHOLD_COMPARISON.csv`. These are aggregate feasibility counts, not final cohort membership.

## 5. Intervention

`A_i` is the patient-level mean of qualifying baseline SBP readings after the final count threshold is approved.

- Reference: `d0(A_i)=A_i`.
- Intervention: `d1(A_i)=A_i-10 I(A_i>=130)`.

This deterministic modified treatment policy is fixed. It describes a hypothetical shift in a measured baseline summary; it is not prescription, medication assignment, sustained BP lowering, or proof of biological/safe feasibility. Do not modify it to hide poor support. Preserve all patients in the target definition; identify shifted values outside conditional support and do not extrapolate. Any restriction requires research-team approval and a revised target-population statement.

## 6. Required cohort construction audit (future Phase 2.1)

Before effects: cohort flow from source universe through index and recorded-MI exclusions; match/resolve aggregate counts against authoritative totals; report keys, duplicates, date validity, first event, and no-event-to-data-end status. For each reading threshold report denominator, events/no recorded event, case/eligible retention, SBP distribution, median count, frequency, variability, and missingness. Emit only aggregate tables to `revised/phase2/`; row-level staged data stay under ignored local `data/` and never enter this package.
