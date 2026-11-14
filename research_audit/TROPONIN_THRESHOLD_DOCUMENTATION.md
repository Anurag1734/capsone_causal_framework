# Troponin Threshold Documentation

## Transcription and source

The original input is `data/raw/troponin_thresholds.jpeg`, a rendered table rather than a CSV. It was transcribed without changing the displayed fields into `research_audit/artifacts/troponin_thresholds.csv`: `itemid`, `assay_type`, `anchor_year_start`, `anchor_year_end`, `sex`, `url_value`, and `unit`. The three rows are 51002/cTnI/0.04 ng/mL, 51003/cTnT/0.014 ng/mL, and 52642/cTnI/0.04 ng/mL; each specifies years 2100-2250 and sex `ALL`.

The project presentation `docs/capstone_phase3_ppt_content.md` attributes the cTnT and cTnI cutoffs to ACC/AHA but gives no assay-specific bibliographic citation. It also applies one cTnI value to both 51002 and 52642. Thus the table is retained as **user-provided and provisional**, not certified as a validated 99th-percentile URL table.

## Source data and validation

`data/raw/labevents.rar` contains `labevents.csv` with columns `labevent_id`, `subject_id`, `hadm_id`, `specimen_id`, `itemid`, `order_provider_id`, `charttime`, `storetime`, `value`, `valuenum`, `valueuom`, `ref_range_lower`, `ref_range_upper`, `flag`, `priority`, and `comments`. The archive's 13.73 GB uncompressed member could not fit in available free disk. Instead, 118,171,367 rows were streamed without modifying the archive; 359,163 rows for the three configured item IDs were retained in `research_audit/artifacts/troponin_measurements.csv`.

`d_labitems.parquet` labels 51002 and 52642 Troponin I and 51003 Troponin T. Observed data show:

| Item | Rows | Admission-linked rows | Units | Observed `ref_range_upper` | Supplied cutoff | Result |
|---|---:|---:|---|---:|---:|---|
| 51002 | 0 | 0 | none | none | 0.04 ng/mL | Cannot validate: no observations. |
| 51003 | 359,000 | 194,115 | ng/mL | 0.01 for all rows | 0.014 ng/mL | Same unit, but cutoff exceeds the recorded upper reference range; source applicability unresolved. |
| 52642 | 163 | 0 | ng/mL | 0.08 for all rows | 0.04 ng/mL | Cutoff is below the recorded upper reference range; no records can be linked to admissions. |

Observed chart years are 2105-2212, within the supplied interval. The table specifies sex `ALL` and does not stratify by sex. The absence of platform/assay-generation details and citations prevents validating the limits across these years. The in-row reference range is a comparison, not a substitute for an externally sourced assay-specific 99th-percentile URL.

## Candidate event-time rule

For diagnostic review only, a candidate is the earliest measurement per admission with numeric `valuenum` strictly greater than its supplied cutoff, exact unit match, year in scope, and compatible sex scope. It is a troponin-derived event proxy, **not biological MI onset**, and does not apply the separate >=20% delta criterion in the project presentation. Because threshold validation is unresolved, every admission has `event_time_proxy_accepted=false`; ECG timing based on these candidates remains uncertain. No timestamp is imputed.

The runner found 38,077 admissions with a provisional candidate, including 10,099 acute-ICD admissions. 38,282 candidate measurements with null admission IDs are excluded from admission linkage. See `TROPONIN_THRESHOLD_VALIDATION.csv` and `MI_EVENT_TIME_AUDIT.csv`.
