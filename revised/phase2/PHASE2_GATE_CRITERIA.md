# Phase 2 — Gates Before Cohort Construction and Estimation

> **Status update:** This Gate 0 table records the original Phase 2.0 review. Its pre-remediation feasibility statuses are superseded by `PHASE2_GATE0_REMEDIATION_REPORT.md` and the linked workstream reports. Current Gate 0 remains **not passed**: the available data do not establish continuous outcome observation, complete death ascertainment, or the required pre-window disease covariates. Do not infer cohort-construction authorization from completion of aggregate checks.

> **Status update:** The Gate 0 aggregate feasibility items formerly listed as unavailable were rechecked under Task 2.0-R. Use `PHASE2_GATE0_REMEDIATION_REPORT.md`, `PHASE2_GATE0_REMEDIATION_DECISION_REGISTER.md`, and their aggregate tables for current evidence. Gate 0 remains not passed; do not construct the primary cohort until the remediation report's remaining data and researcher decisions are resolved.

These gates are sequential. Passing a later gate does not waive an earlier one. Current state is shown for this Phase 2.0 task.

## Gate 0 — Design closure (before primary cohort construction)

| Requirement | Pass criterion | Current status |
|---|---|---|
| Target, index, event codes, exclusion, intervention | Match fixed protocol definitions; no future-MI-free control selection; no prior-MI adjustment | Design fixed |
| Minimum BP count | ≥1/2/3/4 aggregate table completed in common-index risk set; threshold selected without outcome effect; researcher approves if ≥2 retention/reliability tradeoff is not defensible | Blocked: only ≥1 aggregate supplied |
| Horizon | Aggregate event/observation coverage at 90/180/365/730; 365 approved only if coverage supports interpretation | Blocked: no horizon-specific risk-set coverage |
| Death/censoring | Death linkage completeness and anomalies reviewed; operational observation process and censor assumptions approved | Blocked: death incomplete; no continuous observation/censor dates |
| Covariates/prior MI | Pre-window cutoff operationalized; prior MI exclusion retained; no post-exposure covariates | Design fixed; field validation remains |
| Estimator/uncertainty/multiplicity | G-computation event-process plan and bootstrap/interaction multiplicity agreed | Recommended method specified; validation/team review pending |

**Gate 0 result: NOT PASSED. Do not construct the primary patient-level analytical cohort yet.** This setup task cannot close data-dependent decisions without the prohibited cohort construction or additional observation evidence. No human approval is claimed.

## Gate 1 — Source integrity and cohort-input readiness

- Source archive/member path and release version recorded; verify full member CRC/integrity before relying on all inputs.
- OMR archive copies are byte-identical (currently passed); choose one copy and record SHA-256.
- Diagnosis Parquet and admissions chronology source versions align; row keys and timestamps validated.
- Required exact CSV/Parquet schemas validated; no legacy hard-coded paths.
- `subject_id`/`hadm_id` linkage validated; OMR linked by subject and chartdate only.
- Row-level staging path under ignored local `data/`; verify ignore behavior before any write.

## Gate 2 — Aggregate exposure and follow-up feasibility

- Reproduce authoritative common-index counts and first-event counts before exposure summaries.
- Produce ≥1/≥2/≥3/≥4 patient aggregates with all fields in `aggregates/bp_count_threshold_feasibility.csv` populated or explicitly justified unavailable.
- Compare 90/180/365/730 event/ascertainment/death/censoring fields in the horizon table.
- Verify administrative data boundary from release metadata; do not infer individual survival/observation from last encounter.
- Investigate 557 out-of-interval death timestamps and six repeated patient death rows.
- Approve a defendable competing-risk/death sensitivity plan. Current source linkage alone is insufficient for complete CIF.

## Gate 3 — Conditional support (before outcome model)

- Conditional density for SBP and shifted SBP assessed across continuous and categorical covariate profiles and around 130.
- Predeclare near-zero density/range and density-ratio/weight diagnostics before outcome results.
- Quantify unsupported fraction overall and in age/sex/diabetes strata and report profile coverage.
- No unsupported region is silently extrapolated. Any population restriction or intervention change requires a signed research-team decision. The specified intervention itself remains unchanged.

## Gate 4 — Precision and estimator validation

- Approve subgroup minimum detectable RD/interaction and CI-width target; run design simulations with actual event/censoring/support counts.
- Validate the discrete-time competing-risk g-computation under simulation, including missing/censored follow-up and bootstrap coverage.
- Validate patient-level bootstrap convergence and any five-fold patient-grouped cross-fitting.
- No binary-treatment AIPW as primary; no CATE/causal forest in Phase 2.

## Gate 5 — Estimation authorization

Only after Gates 0–4 pass and the research team approves the final protocol may Phase 2 effect estimation begin. The present task stops before cohort construction and does not authorize Phase 2.1.
