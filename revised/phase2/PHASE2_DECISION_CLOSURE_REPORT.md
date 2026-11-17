# Phase 2.0 Decision Closure and Feasibility Report

> **Status update:** This is the initial Phase 2.0 record. Its “unavailable” BP-threshold, horizon, conditional-support, and subgroup-precision findings are superseded by the aggregate-only Task 2.0-R evidence in `PHASE2_GATE0_REMEDIATION_REPORT.md` and its workstream reports/tables. The overall Gate 0 conclusion remains **not passed** because outcome observation, complete death ascertainment, and baseline disease covariates remain unresolved.

**Study:** *Modifiable Cardiovascular Risk Factors, Heterogeneous Causal Effects and Counterfactual ECG Modelling*  
**Task boundary:** aggregate feasibility and protocol closure only. No primary patient-level analytical cohort, final exposure variables, outcome models, propensity models, or effect estimates were produced.

## Executive decision

The protocol choices that follow directly from the research instructions are frozen in `PHASE2_FINAL_PROTOCOL.md`: target population, common index and future-event control handling, ICD acute/historical MI definitions and prior-MI exclusion, 730-day OMR exposure candidate and QC, fixed deterministic SBP policy, pre-window covariate timing, population risk difference, continuous-exposure g-computation candidate, patient-level uncertainty, and multiplicity recommendation.

Data-dependent decisions cannot all be closed in Phase 2.0 from supplied aggregate counts without constructing the prohibited cohort or obtaining additional observation data. **Gate 0 is not passed; the study is not ready for primary cohort construction.** The protocol provides explicit recommendations and pass criteria so no research definition is silently invented later. No human approval is claimed.

## Aggregate checks performed

### BP measurement threshold

The reconciliation provides only the ≥1 valid-reading row for the fixed two-year window:

| Minimum readings | Eligible | Incident first MI | No recorded incident MI before censoring | Retention of eligible | Retention of cases | Within-person summary |
|---:|---:|---:|---:|---:|---:|---|
| ≥1 | 53,956 | 1,223 | 52,733 | 31.9% of 168,915 | 38.1% of 3,207 | Mean/median/frequency/variability not supplied |
| ≥2 | Not available | Not available | Not available | Not available | Not available | Requires patient-level reading counts |
| ≥3 | Not available | Not available | Not available | Not available | Not available | Requires patient-level reading counts |
| ≥4 | Not available | Not available | Not available | Not available | Not available | Requires patient-level reading counts |

At ≥1, 114,959/168,915 common-index patients and 1,984/3,207 incident cases do not have a qualifying two-year-window BP. These are aggregate counts, not the final analytic denominator. The fixed-window threshold comparison, SBP mean/distribution, median reading count, measurement frequency, within-person SD/IQR, and measurement-density differences for ≥2/≥3/≥4 cannot be calculated from the reconciliation alone. `aggregates/bp_count_threshold_feasibility.csv` leaves unavailable fields blank with source/provenance; blank does not mean zero.

**Decision:** recommend ≥2 valid readings as the primary threshold candidate, as requested, because it reduces reliance on a single measurement. This remains **recommended; empirical validation required**: no evidence yet establishes that retention and event information remain defensible or that reliability improves enough to justify the selection. Compare ≥1/≥2/≥3/≥4 before freezing cohort; do not select on effect direction. If ≥2 is not defensible, return the least restrictive supported threshold to the team.

### OMR source and aggregate coverage context

Both archive members `hosp.rar::omr.csv` and `omr.rar::omr.csv` were streamed fully through Windows `tar` to a SHA-256 accumulator. They have identical uncompressed size 265,978,805 bytes, identical hash `e8a0178e8c288bccbb0f43676c22b4e30505b812f5701a5cbb4ea4bfc142c255`, and header `subject_id,chartdate,seq_num,result_name,result_value`; both streams exited successfully. No file or row-level output was created. The cohort-candidate OMR source is therefore internally identical between archive copies; use one and record its hash.

The archive's `longitudinal/phase2_stats.json` reports 2,169,549 Blood Pressure records, 135,594 patients, and 59,863 “cohort” patients (1,316,642 cohort BP records; 60.3% coverage) under an older archive cohort definition. It reports 1,662,112 BMI (kg/m2) records and 64,167 old-cohort patients (64.6%). These are source-coverage context only—not valid-QC readings, not restricted to the revised 730-day window, and not denominators for the reconciled common-index population. See `aggregates/omr_coverage_context.csv`.

### Follow-up horizon

The source reconciliation gives 3,207 incident first acute-MI cases over the common-index follow-up but does not allocate them to 90, 180, 365, or 730 days. It does not provide horizon-specific ascertainable follow-up, censoring, competing-death, or ambiguous-date counts. The source maximum record date, if calculated, would not by itself establish the dataset's administrative end or individual continuous observation. `aggregates/followup_horizon_feasibility.csv` reports all requested horizons as not estimable from available aggregate evidence; the missing values are not zero.

**Decision:** retain 365 elapsed days as the recommended fixed horizon, pending aggregate observation coverage and researcher approval. It is not established as defensible by Phase 0. Do not replace it with 90/180/730 days absent the requested horizon checks and approval; do not choose any horizon based on treatment-effect results.

### Death-source reconciliation

The read-only aggregate script `scripts/phase2_0_death_source_reconciliation.py` streams selected Parquet members in memory and writes only `aggregates/death_source_reconciliation.csv`. It linked source rows only to check aggregate death-source consistency and timing against all-history first acute-coded admissions; it did not define the common-index analytic cohort.

| Finding | Count / denominator | Interpretation |
|---|---:|---|
| Admission `deathtime` rows | 8,598 / 431,231 admissions | Admission-level timestamp source |
| Distinct patients with admission death timestamps | 8,592 / 180,733 patients | Six extra timestamp rows: six patients each have multiple distinct timestamp rows |
| Timestamps inside their admission admit–discharge interval | 8,041 / 8,598 | 557 out-of-interval rows: 25 before admission and 532 after discharge |
| Observation-end patient DOD | 27,980 / 180,733 | 152,753 have missing DOD (84.5%); missing is unknown, not survival |
| Demographics DOD | 29,076 / 299,712 | Wider patient universe; do not combine denominators |
| Shared linked nonmissing DOD dates | 27,980 / 27,980 agree exactly | Strong internal agreement of observed dates, not completeness |
| In-hospital death timestamps in both admission and observation-end sources | 8,592 / 8,592 agree exactly | Patient-level link via `subject_id`; timestamps are source-consistent among observed records |
| First acute-coded MI patients with DOD in all-history source | 3,510 / 9,703 | 6,193 lack DOD; not the 3,207 common-index incident cases |
| DOD before / same day / after first acute admission among those with DOD | 0 / 54 / 3,456 of 3,510 | Same-day order ambiguous because DOD is date precision |
| Exact in-hospital death timestamp vs first acute-MI admission | 1,450 paired; 2 earlier / 0 tie / 1,448 later | Two timestamps earlier than a later first acute-MI admission are anomalous and require source-quality review |

**Decision:** preserve death as the competing event in the scientific estimand, but mark complete MI cumulative incidence **blocked/not identified from current death linkage alone**. Agreement among recorded values does not resolve 84.5% DOD missingness in the admission-linked universe. The 557 death-time interval anomalies also require review. Do not treat unknown death as alive. Explicit missing-death sensitivity scenarios are specified in the follow-up document; they are not substitutes for validated linkage.

### Conditional support/positivity

No conditional SBP density, shifted-value density, joint-profile support, near-130 behavior, unsupported fraction, density ratio, or effective sample size is in the supplied aggregate evidence. Marginal SBP bins/min–max checks are insufficient. No support problem may be hidden by changing the intervention. Full target population remains the intended target; any restriction requires research-team approval and an updated estimand. **Decision status: blocked pending Phase 2.1 aggregate support diagnostics.**

### Subgroup precision and multiplicity

Supplied two-year BP case counts are age <65 375, age ≥65 848, male 651, female 572, diabetes documented 503, and not documented 720. They sum to 1,223 within each partition but use the supplied definition; they do not establish final counts under the pre-window diabetes rule or ≥2 threshold, and raw counts do not establish precision.

**Protocol recommendation:** modifiers are age <65/≥65 at exposure-window start, recorded sex, and pre-window documented diabetes. Test a global joint null and direct risk-difference interactions; Holm-adjust the three prespecified modifier tests at family-wise 0.05. Before subgroup estimates, the research team must set a clinically meaningful minimum detectable RD/interaction and 95% interval-width target, followed by design simulation under actual event, censoring, and support patterns. No numerical clinical precision target can be justified from present aggregates. **Decision status: requires research-team approval/empirical precision analysis.** No CATE model or causal forest is started.

## Decision closure summary

| Decision area | Phase 2.0 status |
|---|---|
| Population, common index, acute/historical codes, prior-MI exclusion | Finalised from supplied research definitions |
| Baseline OMR source, QC, strict date cutoff, 730-day candidate | Finalised design specification; source copy identity verified |
| Fixed SBP intervention and reference | Finalised; must not change for support findings |
| Minimum reading count | ≥2 recommended; threshold retention/reliability not available; empirical gate remains |
| Horizon | 365 days recommended; horizon coverage and observation not available |
| Death | Source linkage reconciled; completeness inadequate for identified competing-risk CIF |
| Censoring/observation end | No validated individual observation/censoring process or verified global cutoff |
| Prior MI adjustment | Removed from primary set; exclusion retained |
| Covariate timing/adjustment | Strictly before exposure-window start; age/sex and pre-window diagnoses; BMI conditional |
| Conditional positivity | Not assessed conditionally; must pass before outcome modeling |
| Primary estimator | Discrete-time competing-risk g-computation selected as method recommendation; validation required |
| Uncertainty/multiplicity | 1,000 patient bootstrap / 95% percentile interval; Holm FWER .05 across three modifiers recommended |
| Subgroup precision | Numerical MDE/CI target requires research-team approval and simulation |

## Successfully completed

- Inspected Phase 1 handoff, repository code, diagnosis functions, OMR logic, temporal join examples, existing tests/dependencies, `.gitignore`, prior audit outputs and source inventory.
- Verified all six current RAR 5 archive signatures, sizes and member lists. Targeted aggregate Parquet members streamed through `tar` and PyArrow successfully; no archive was modified or extracted to disk.
- Verified byte-identical OMR archive copies with same header and SHA-256.
- Reconciled patient-level DOD and admission-level death timestamp sources using read-only aggregate processing; output contains counts/denominators/source definitions only.
- Created requested protocol and specification package plus aggregate-only tables/scripts under `revised/phase2/`.
- Preserved current Phase 1–9 artifacts. No effect, outcome, propensity, CATE, or causal forest model was fitted.

## Validation checks performed

- Confirmed all eight requested Phase 2.0 documents exist under `revised/phase2/` and are readable as UTF-8 Markdown.
- Parsed both new aggregate-processing scripts with Python's AST parser; syntax checks passed.
- Checked each aggregate CSV with Python's CSV reader; every data row has the same number of fields as its header.
- Confirmed the aggregate tables contain only summarized metrics/source metadata, not patient-level rows.
- Reviewed the protocol documents for consistency on the fixed intervention, first acute-MI outcome and codes, historical/prior-MI exclusion, strict pre-index OMR date and QC rules, 730-day candidate window, 365-day proposed horizon, prior-MI removal from adjustment, competing death, incomplete observation, g-computation recommendation, and no-cohort/no-effect boundary.
- Reviewed repository status: new work is confined to `revised/phase2/`; no tracked original files are modified. No commit or push was made.
- These were structural/documentation checks, not tests of an analytic cohort or estimator. No statistical tests or effect analyses were run.

## Unsuccessful or unavailable checks

- Minimum ≥2/≥3/≥4 reading counts, BP mean/distribution/frequency/variability, and threshold retention could not be derived without constructing the prohibited primary cohort. Only ≥1 aggregate was supplied.
- 90/180/365/730 event-time, ascertainable-follow-up, censoring, and competing-event distributions could not be derived without the approved index risk set and individual observation process.
- Complete death-before-MI risk is not identified by available death linkage alone; DOD missingness and out-of-interval timestamp anomalies remain.
- Conditional positivity and subgroup precision/MDE could not be assessed from aggregate counts.
- A limited OMR header-only streaming attempt initially did not return promptly and was interrupted. A later complete OMR hash/header stream succeeded for both copies; no output file from the interrupted attempt was created.
- Full CRC testing of every archive member was not performed. Selected Parquet and OMR members streamed successfully; this is not a full archive integrity certification.

## Files created

1. `PHASE2_DECISION_CLOSURE_REPORT.md`
2. `PHASE2_FINAL_PROTOCOL.md`
3. `PHASE2_COHORT_AND_EXPOSURE_SPECIFICATION.md`
4. `PHASE2_FOLLOWUP_AND_COMPETING_RISK_SPECIFICATION.md`
5. `PHASE2_ADJUSTMENT_SET_AND_COVARIATE_DICTIONARY.md`
6. `PHASE2_ESTIMATION_SPECIFICATION.md`
7. `PHASE2_GATE_CRITERIA.md`
8. `PHASE2_DECISION_REGISTER.md`
9. Aggregate-only scripts under `scripts/` and tables under `aggregates/`.

## Completion gate

**Phase 2.0 design recommendations and execution specifications are documented, but the decision-closure gate is not fully passed. The study is not ready for primary cohort construction.** Obtain aggregate threshold/horizon checks, defensible observation/death information, conditional support evidence, and research-team precision/approval decisions first. This task stops here; Phase 2.1 has not started.
