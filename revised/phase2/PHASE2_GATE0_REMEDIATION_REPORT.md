# Phase 2.0-R — Gate 0 remediation report

**Study:** Modifiable Cardiovascular Risk Factors, Heterogeneous Causal Effects and Counterfactual ECG Modelling  
**Scope:** five aggregate feasibility workstreams only. No Phase 2.1–2.5 cohort/exposure dataset, causal outcome model, effect estimate, AIPW, CATE, causal forest, dashboard change, or β-VAE work was performed.

## Initial Gate 0 failure

The Phase 2.0 closure report did not authorize cohort construction because BP-count feasibility, horizon/follow-up, death/censoring, conditional support, and subgroup precision were unresolved. Task 2.0-R explicitly authorized a separate, aggregate-only remediation using temporary in-memory linkage. This report records that evidence and does not treat the authorization as approval to start Phase 2.1.

## Successfully completed

### Workstream A — Minimum BP measurement count

Streamed the verified OMR source in 250,000-row chunks and matched it transiently to the common-index eligibility definition. Applied the requested SBP/DBP parsing/range/order rules and strict 730-day date window. The resulting ≥1 count exactly matches 53,956 eligible patients and 1,223 cases. Counts at ≥2/≥3/≥4 are 40,346/933, 31,478/722, and 25,564/582. SBP summaries, within-person SD, reading-count/frequency and last-measurement-gap distributions, frequent-attender comparisons, and retained/excluded characteristics are provided in the BP comparison and selection tables.

**Recommendation:** ≥2 readings is supported as a reasonable reliability/retention trade-off (74.8% of ≥1 BP participants and 76.3% of their cases remain; median reading count rises from 3 to 5). It is not a validated measurement-error correction and remains subject to researcher approval.

### Workstream B — Follow-up horizons

Computed recorded first acute-MI events, source-consistent recorded deaths classified before MI, later encounter availability, no later encounter counts, and event/last-subsequent-record time summaries at 90/180/365/730 days. The 365-day row contains 898 recorded first-MI admissions and 47,426 patients with a later admission record within the horizon. The remaining 121,489 have no such later encounter. No one has a verifiable continuous-observation indicator; these counts are not completeness estimates.

**Finding:** 365 days remains a candidate only. No horizon is defensible as complete fixed-horizon cumulative incidence under current data. A hospital encounter is not continuous follow-up; no encounter is not known survival or MI-free status.

### Workstream C — Death/censoring sources

Re-read admission chronology, observation-end, patient demographics, and diagnosis source tables from the longitudinal archive. The 8,598 admission death rows include 8,041 timestamps within their admission interval, 25 before admission and 532 after discharge; six patients have multiple distinct timestamps. All 8,592 linked patient-level in-hospital timestamps agree exactly with admission-level timestamps. Patient DOD values agree across the two patient-level sources when both are present (27,980/27,980), but DOD is absent in 152,753/180,733 source-universe patients. The `observation_end` field equals DOD when present and last discharge when DOD is absent; neither yields a common administrative boundary or continuous observation.

In the reconciled common-index set, 24,543/168,915 have agreeing DOD, 6,813 have one unique in-interval in-hospital timestamp, and these sources overlap. Same-day date precision is left unordered. Complete death-before-MI cumulative incidence is not identified from this linkage alone.

### Workstream D — Conditional positivity

For the candidate ≥2 population, compared held-out gradient-boosted conditional q01/q99 support with leave-self-out local KNN q01/q99 at k=100/250, plus conditional kernel density ratios at SBP bandwidths 5/10. These are exposure-support diagnostics only; no outcome was used. The methods flag about 1.3%–2.5% shifted values outside their age/sex/BMI conditional quantile envelopes. Density ratios vary by bandwidth, with 19.3% above 10 at bandwidth 5 versus 3.5% at bandwidth 10.

**Finding:** possible support among observed age/sex/BMI profiles, not demonstrated conditional positivity. Diabetes, hypertension, and CKD have no observed pre-window variation in the eligible population under the earliest-admission index rule; full joint confounder-profile support is not assessable. No patient was trimmed and the fixed intervention was not changed.

### Workstream E — Subgroup precision

Computed subgroup eligible populations, incident cases, 365-day recorded events, death ascertainment, BP summaries and missingness for age at window start, age at index for reconciliation, sex, and diabetes documented by the pre-window cutoff versus by index. Age-at-index ≥1 BP case counts reproduce 375/848; sex reproduces 651/572; diabetes documented by index reproduces 503/720. Under the prespecified pre-window diagnosis cutoff, diabetes/HTN/CKD are all undocumented and diabetes heterogeneity cannot be assessed.

Provided an illustrative independent-binomial MDE/CI-width sensitivity table at assumed outcome risks 1%, 2.5%, and 5%, 80% power, and conservative two-sided alpha 0.05/3. This is not causal treatment-effect interaction power and not evidence of adequate precision. Researcher MDE/CI-width targets remain unresolved.

## Validation and provenance checks

- Inspected all eight Phase 1 handoff files, the Phase 2.0 decision/protocol/gate/inventory documents, the actual Phase 0 diagnosis/timing reports, diagnosis audit outputs, and source-table schemas from the local archive.
- Confirmed archive reads were limited to longitudinal Parquet members and `omr.csv`; the ICU, master, lab-event, and unrelated members were not extracted or read for this workstream.
- Reconstructed common-index totals exactly: 168,915 patients, 3,207 first post-index acute-MI-coded events, and 165,708 without a recorded first event. The code applies calendar-date MI exclusion at/before index and requires first MI on a later calendar date. It reports one candidate admission timestamp tie and applies a deterministic `hadm_id` tie-break.
- Confirmed BP≥1 totals exactly reproduce the authoritative 53,956/1,223/52,733 aggregate. The aggregate-only calculations do not prove record-level membership identity with an unavailable prior cohort extract.
- Checked table units/denominators, CSV field counts, and script syntax. One scikit-learn/joblib Windows physical-core discovery warning occurred; conditional-support processing completed. No statistical tests were run.
- No temporary patient-level file was written; all patient linkage was in memory and aggregate outputs only were exported. Raw archives and original Phase 1–9 files were not modified. All new deliverables are under `revised/phase2/`.

## Failed, unavailable, or not established

- No patient-level continuous observation/censor time, continuous enrollment, or independently verified common administrative extraction boundary exists in the inspected sources. Last encounter is not censoring evidence.
- Death ascertainment is incomplete; missing DOD is not survival. Death linkage anomalies and within-day DOD ordering limit competing-event classification.
- Pre-window diagnoses have no variation because index is the earliest eligible hospital admission; this leaves planned disease adjustment and diabetes modifier unavailable under the current timing rule.
- Conditional positivity across diabetes, hypertension, CKD, and their joint profiles cannot be evaluated under the currently observed pre-window variables. Current quantile/density methods are exploratory sensitivity diagnostics, not proof of positivity.
- Numeric causal interaction MDE, causal CI width, or subgroup power cannot be calculated without the eventual supported intervention model and defensible follow-up; scenario calculations are not treatment-effect estimates.
- BMI 10–80 kg/m² is a transparent plausibility screen, not a clinically validated protocol range; 87.4% of ≥2 BP participants lack qualifying pre-window BMI.
- The local archive is readable through Windows `tar` and selected members streamed successfully, but whole-archive CRC certification was not attempted. DuckDB and a dedicated RAR backend remain unavailable; no dependency installation was needed.

## Decision status by gate

| Gate area | Status | Reason |
|---|---|---|
| Common index and MI event aggregate validity | PARTIALLY PASSED | Authoritative aggregate totals reproduced with explicit date-level rules; one tied timestamp and downstream admission/transfer checks remain for a later governed build. |
| Minimum BP count | REQUIRES RESEARCHER APPROVAL | Full ≥1–4 aggregate comparison is available; ≥2 is recommended, but reliability/selection trade-off is a team decision. |
| Follow-up horizon | FAILED | Events can be counted as recorded; continuous observation and individual censoring cannot be established at any tested horizon. |
| Death/competing risk | FAILED | Observed source linkage is internally consistent, but 84.5% of source-universe DOD values are missing. |
| Covariate timing | FAILED | Diabetes, hypertension and CKD are absent before the exposure-window start under the current index rule. |
| Selection/missingness | PARTIALLY PASSED | BP threshold retention and observed characteristic differences are described; unmeasured healthcare-use selection remains. |
| Conditional positivity | NOT ASSESSABLE | Preliminary age/sex/BMI support looks possible, but required disease profiles are unobserved and density results are specification-sensitive. |
| Subgroup precision | REQUIRES RESEARCHER APPROVAL | Descriptive cells and illustrative risk precision are supplied; actual causal precision targets and diabetes timing require team decision. |
| Overall Gate 0 / ready for cohort construction | FAILED | Fixed-horizon outcome ascertainment, death/censoring, and pre-window disease adjustment are unresolved. |

## Research-team decisions required

1. Approve or reject the ≥2 valid reading threshold after reviewing its retention and measurement evidence.
2. Decide whether additional linkage can establish observation and death follow-up; otherwise approve or reject a clearly limited hospital-record estimand and missing-death sensitivity assumptions.
3. Decide how to handle the absence of pre-window diabetes/HTN/CKD without silently moving their measurement into the exposure window or changing the estimand.
4. Review the conditional-support diagnostics and proposed warning criteria; no restriction or trimming is recommended automatically.
5. Set meaningful subgroup MDE/CI-width targets and determine whether age/sex analyses are exploratory; diabetes heterogeneity is currently not assessable.
6. Approve the final horizon and uncertainty/multiplicity plan only after the observation limitations are addressed.

## Phase 2 gate decision

The remediation package is ready for research-team review of these decisions and limitations. **Gate 0 is not passed, and the study is not ready for Phase 2.1 cohort construction or Phase 2.6 causal estimation.** No human approval is claimed. The scientific question, 10 mmHg intervention, 130 mmHg threshold, target population, and estimand were not changed. Stop here; no later phase was started.
