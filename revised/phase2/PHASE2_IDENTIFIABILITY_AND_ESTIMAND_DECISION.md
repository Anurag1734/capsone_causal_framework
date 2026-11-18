# Phase 2 Identifiability and Estimand Decision

## Fixed scientific target

The design remains unchanged: in eligible MIMIC-IV hospital-entry patients with baseline OMR SBP `A`, compare the first acute-MI cumulative incidence under `d0(A)=A` and `d1(A)=A - 10 I(A >= 130)`, primary risk difference `F_M^d1(tau) - F_M^d0(tau)`. Acute codes are ICD-9 `410*`, ICD-10 `I21*`/`I22*`; historical codes ICD-9 `412`, ICD-10 `I25.2`; documented MI on/before index is excluded. Candidate exposure window is `[index_date - 730 days,index_date)` and the target horizon remains 365 days only as a proposal.

This audit does not redefine or estimate that contrast.

## Identification assessment

| Requirement/blocker | Prepared-source evidence | Status for fixed estimand |
|---|---|---|
| Common index and event code history | `diagnoses_all` and admission chronology were streamed; aggregate reconstruction matched 168,915/3,207/165,708. Admission time is a code-event proxy. | Partially resolved using existing prepared data; final record-level construction and transfer validation remain future checks. |
| Diagnosis/source schema and code classification | Actual prepared diagnosis and admission schemas, source ICD version fields and code mappings were inspected. | Resolved using existing prepared data for source schema/code-rule specification; this does not establish complete pre-entry disease history. |
| Baseline SBP availability | OMR threshold aggregates reproduced; at least 2 readings is recommended but unapproved. | Partially resolved using existing prepared data; explicit researcher approval remains required for the threshold. |
| Baseline disease adjustment | Diagnosis temporal summary finds zero pre-window diabetes/HTN/CKD; master flags are not Phase 2-aligned and have no diagnosis dates. | Unresolved with current data; requires additional valid history. Any timing/design change requires explicit team approval. |
| Conditional positivity | Existing boosted-quantile/KNN/density diagnostics condition only on age, sex, sparse pre-window BMI; disease profiles unavailable. | Partially assessed; full joint positivity is not established. Additional valid covariate data and researcher review are required before support can pass. No trimming or policy change authorized. |
| Outcome ascertainment | First MI admissions are observable within the source, but external events and continuous follow-up are not. No verified source boundary. | Unresolved with current data; requires additional observation data or an explicitly approved record-capture estimand. |
| Competing death | DOD missing for 84.5% of source universe; timestamp anomalies and date-only order ambiguity remain. | Unresolved with current data; improved death data are required for completeness, and sensitivity assumptions require researcher approval. |
| Censoring/observation | No enrollment, observation-end, outpatient encounter or claims source; last discharge is only last record. | Unresolved with current data; requires additional observation/boundary data. Researcher approval alone cannot supply it. |
| Selection into BP/observed hospital care | Age/sex/BMI measurement differences can be described; no complete pre-entry utilization or outside-system care data. | Partially resolved descriptively; additional valid predictors would be needed for weighting, and unmeasured selection remains. |
| Research-team choices | No documented human approval for threshold, horizon, restricted capture estimand, or any cutoff change. | Approval required; Codex recommendations are not approvals. |

## Options for the research team

### A. Retain the original estimand and obtain additional valid data

Keep the fixed target and intervention. Obtain linkable pre-window disease history with dates, plus a defensible patient-level observation/enrollment or claims process and a reliable death source. Validate linkage and coverage for the common-index population. This is the option needed to pursue the original complete-risk interpretation without redefining it. None of these additional sources is present in the current local project data.

### B. Consider a restricted hospital-record capture estimand

A distinct, team-approved candidate could define `Y_MIMIC^d(365)=1` when a first qualifying acute-MI-coded admission is recorded in MIMIC within 365 elapsed days of index under policy `d`. Restrict the target to common-index eligible patients whose entire 365-day period lies within a verified common data-release boundary. The candidate contrast would be `RD_MIMIC(365)=E[Y_MIMIC^d1(365)-Y_MIMIC^d0(365) | eligible, full_source_opportunity]`.

This asks about first-MI **record capture in this hospital database**, not whether a patient had a first clinical MI anywhere. An MI treated elsewhere is not counted. It is not equivalent to the original cumulative-incidence estimand. A causal interpretation would still require adequate control of baseline confounding, conditional support, valid exposure measurement, correct coding, and stable/differentially understood capture under the hypothetical BP policy. Missing pre-window disease histories would remain a confounding limitation. If death is included in this record-capture outcome, it means no subsequent MIMIC MI record; it does not estimate competing-risk mortality or true MI risk.

No verified common extraction boundary is available, so the restricted full-opportunity target cannot currently be operationalized. This candidate requires explicit research-team approval, a boundary source, and a separate signed estimand/protocol before any analysis. It is not selected here.

### C. Stop causal effect estimation under current data

Do not estimate a causal contrast with the current records. Report the identification limitations and preserve the fixed research question for future data acquisition or explicit team review. This is the current safe operational gate status, not a decision made on behalf of the research team about the project's long-term direction.

## Recommendation and approval boundary

**Gate 0 fails on current evidence.** The project should not proceed to causal estimation unless the research team resolves the identification path and required data/assumptions. Codex does not choose A, B, or C for the team. An approval alone cannot replace missing disease history, observation boundaries, death capture, or conditional support. No intervention or estimand has been silently changed.
