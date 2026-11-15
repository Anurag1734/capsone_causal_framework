# Final Troponin Threshold Decision

**Decision: D — Reject threshold-based event timing for the current study.**

Do not retain, correct, or promote the configured values as clinically validated thresholds. Stop using threshold crossings to define or time MI events in the primary analysis. The repository does not establish a reproducible derivation, and available assay-level evidence conflicts with two of the three values. No replacement numeric cutoffs are proposed.

## What the repository establishes

The configured table contains:

| Item ID | Label in dictionary | Configured value | Recorded unit |
|---|---|---:|---|
| 51002 | Troponin I | 0.04 | ng/mL |
| 51003 | Troponin T | 0.014 | ng/mL |
| 52642 | Troponin I | 0.04 | ng/mL |

The source is a rendered threshold table transcribed into [`artifacts/troponin_thresholds.csv`](./artifacts/troponin_thresholds.csv). The project presentation attributes the generic cTnT and cTnI values to “ACC/AHA,” but supplies no assay/platform-specific reference, method, or citation. It also applies the same cTnI value to items 51002 and 52642. That attribution does not establish applicability to these item IDs, populations, assay generations, or years.

The repository's pipeline proposal describes defining assay-specific 99th-percentile URLs; it is a proposal, not evidence that these three numbers were calculated that way. No reproducible 95th-percentile procedure, source population, inclusion criteria, or control/MI stratification was recovered. See [`THRESHOLD_DERIVATION_EVIDENCE.md`](./THRESHOLD_DERIVATION_EVIDENCE.md).

## Item-level disposition

| Item | Evidence | Disposition |
|---|---|---|
| 51002 | No measurements in the streamed source subset; no observed range or distribution to assess. | Reject for event timing; neither retain nor correct from these data. |
| 51003 | 359,000 rows, 149,109 numeric values, all in ng/mL; recorded `ref_range_upper` is 0.01 ng/mL on every row. The configured 0.014 ng/mL exceeds that recorded upper reference. The supplied task description's 0.015 does not match the repository configuration. | Reject as an event-time cutoff pending authoritative assay/platform documentation; do not silently substitute 0.01. |
| 52642 | 163 numeric measurements, all in ng/mL; recorded `ref_range_upper` is 0.08 ng/mL on every row. The configured 0.04 is below that reference. All 163 rows lack `hadm_id`, and none matches a patient ED/admission interval. | Reject for event timing; cannot assign these measurements to admissions from the available linkage evidence. |

The recorded reference ranges are useful conflict checks, not automatically valid substitutes for assay-specific clinical URLs. The 51003 and 52642 rows therefore do not support a simple numeric “correction.”

## Research decision

No existing threshold-derived event time is accepted for primary or causal analysis. Candidate threshold crossings and legacy `index_mi_time` values must not be interpreted as validated onset times. A first above-URL measurement, even with a validated assay-specific URL, would be a biomarker-time proxy rather than biological MI onset and would not by itself establish MI.

Proceed only with a reframed, adjusted observational association study using independently defined, diagnosis-based outcomes and the available ECG features, without claims of event-relative timing or causal MI effects. Explicitly address ECG-selection and residual confounding; the current workspace does not contain the admission-level ECG acquisition denominator needed to establish or correct selection bias. See [`FINAL_EVENT_TIME_FEASIBILITY.md`](./FINAL_EVENT_TIME_FEASIBILITY.md).

## Scope and stopping rule

This decision follows a focused repository-wide search of scripts, notebooks, documentation, audit artifacts, structured files, and available Git history. It does not authorize further threshold tuning, master-data edits, model retraining, or causal-effect estimation. Reopen threshold validation only if sourceable item/platform/year/sex-specific assay documentation and a reproducible admission-linkage plan become available.
