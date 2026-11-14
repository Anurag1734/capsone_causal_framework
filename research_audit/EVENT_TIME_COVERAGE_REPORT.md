# Event-Time Coverage and Gate B

## Recommendation

**Gate B remains FAIL / HOLD.** No item has an authoritative item/platform-specific threshold validated against the provided configuration, assay metadata, unit, year, and sex applicability. Therefore, the number of admissions with a **valid** qualifying measurement is 0, and the number with a **reliable first qualifying measurement timestamp under a validated threshold** is 0. Do not treat the provisional candidates or legacy master timestamps as accepted event times.

## Linkage coverage

Direct source `hadm_id` plus `subject_id` matches are confirmed against `admissions_chronology.parquet`. For item 51003, 194,115 rows have a direct matching admission. Of the 164,885 rows without `hadm_id`, 108,577 match exactly one patient's ED-registration/admission-to-discharge interval, 204 match multiple intervals, and 56,104 match none. These interval results are candidates only; source `hadm_id` values were not filled.

For item 52642, all 163 rows lack `hadm_id`; all 163 have zero matching ED/admission intervals. Patient ID alone cannot establish their admissions. The row-level interval results are retained in `artifacts/troponin_missing_hadm_interval_linkage.csv`.

## Admission and ECG counts

- Acute ICD-coded admissions under ICD-9 410* / ICD-10 I21*/I22*: **12,187**.
- Acute ICD-coded admissions with a usable validated event-time proxy: **0**.
- Acute ICD-coded admissions without a usable validated event-time proxy: **12,187**.
- Master ECG rows: **375,930**; acute-presentation label rows: **7,604**.
- ECGs classifiable before/after a validated proxy: **0 / 0**. Official uncertain: **375,930** overall, including **7,604** acute-presentation rows.

The prior audit's threshold-only candidates are not validated events. It reports 38,077 direct-hadm candidate admissions and 10,099 among acute ICD admissions. Among acute-labeled ECGs, candidate-relative counts were 4,929 before, 1,857 after, and 818 uncertain; all remain officially uncertain because the thresholds are unresolved. The legacy master has 3,053 acute-labeled ECG rows with no `index_mi_time`. The 3,269 non-null acute-admission legacy timestamps match a troponin row at that time, but the match does not establish that the row is the first qualifying measurement under a valid URL.

## Meaning and limits

Even after threshold adjudication, the first above-URL `charttime` is a **troponin-derived event-time proxy**, not biological MI onset. A single above-URL measurement can indicate myocardial injury but does not alone establish acute MI; serial change and clinical/ischemic evidence remain relevant. No timestamp has been invented and no uncertain ECG has been classified as pre- or post-MI.

The threshold image does not cite assay-specific primary references. Item 51003's observed `ref_range_upper` is 0.01 ng/mL in all rows, not the 0.015 stated in the task summary; item 52642's configured 0.04 is below its recorded 0.08. Resolve these against the actual assay/platform documentation before reopening Gate B.
