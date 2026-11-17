# Phase 1 Completion Report

## Status

**Completed:** revised study-design and estimand protocol documents created under `revised/phase1/`.  
**Not performed:** cohort rebuild, archive extraction, effect estimation, outcome/propensity modeling, AIPW, causal forest, neural-network work, BP-to-ECG analysis, or Phase 2 implementation.

## Deliverables

1. `EXTENSION_PHASE1_RESEARCH_DESIGN.md` — complete protocol and population/exposure/intervention/outcome framework.
2. `EXTENSION_PHASE1_CAUSAL_DAG.md` — Mermaid working DAG, node roles, candidate adjustment, alternatives and assumptions.
3. `EXTENSION_PHASE1_ESTIMANDS.md` — formal target population, policies, primary RD and secondary risks/RR, horizon, death/censoring interpretation.
4. `EXTENSION_PHASE1_ANALYSIS_PLAN.md` — future construction, support, estimation, uncertainty, heterogeneity, sensitivity and reporting plan.
5. `PHASE1_DECISION_REGISTER.md` — finalized choices, recommended candidates, unresolved approvals and required evidence.
6. `PHASE1_ASSUMPTIONS_AND_LIMITATIONS.md` — identification assumptions, data constraints and resolution actions.
7. `PHASE1_VALIDATION_CHECKLIST.md` — future empirical and approval gates.
8. `WORKSPACE_AND_INPUT_INVENTORY.md` — Task 1 repository/data/tool inventory.

## Protocol summary

- **Question:** effect of a supported baseline SBP reduction on first acute MI admission risk.
- **Target population:** MIMIC-IV patients entering observable hospital cohort and satisfying common index and final BP eligibility. Not the general population; no claim of complete pre-first-admission history.
- **Index:** same eligibility in both groups; earliest nonacute admission; exclude documented acute/historical MI at or before index; future MI does not disqualify controls.
- **Exposure:** OMR valid parsed SBP/DBP, bounds SBP 60–260 and DBP 20–160 with SBP>DBP, strictly pre-index date, candidate 730-day window and arithmetic mean. Measurement count threshold remains open.
- **Intervention:** candidate deterministic modified policy `d(A)=A-10` for `A>=130`, otherwise unchanged; no prescription or sustained effect claim; conditional support unestablished.
- **Outcome:** first post-index acute-MI-coded admission (ICD-9 `410*`, ICD-10 `I21*`/`I22*`); admission-time proxy, not biological onset.
- **Follow-up:** recommend 365-day fixed horizon for review only; requires approval after aggregate coverage checks.
- **Primary estimand:** population-average fixed-horizon cumulative-incidence risk difference under policy versus observed SBP, among eligible BP-observed patients, with death competing when ascertainment permits; secondary RR and policy risks.
- **DAG/adjustment:** candidate age at exposure-window start, sex, diabetes, hypertension, CKD defined before the 730-day exposure window; BMI conditional on valid pre-window measurement. This temporal cutoff is recommended and awaits approval. Prior MI omitted because the exclusion rule makes it structurally constant. Medication not automatic primary adjustment.
- **Identification:** consistency, exchangeability, conditional positivity, temporality, outcome/exposure validity, selection, censoring and competing-event assumptions all require assessment.
- **Analysis:** future g-computation candidate for policy risks; target-specific AIPW/IPW robustness only after methods review; patient-level cross-fitting and bootstrap; conditional support, balance, selection, missingness, sensitivity, and prespecified heterogeneity diagnostics.
- **Heterogeneity:** age, sex and diabetes candidate modifiers; counts are descriptive only and precision targets require approval.
- **Limitations:** OMR selection, incomplete observation/death/medication ascertainment, unavailable smoking and sparse lipids, possible undocumented MI, and non-generalizable hospital cohort.

## Cross-document consistency audit

Reviewed the four main documents for the required common definitions:

| Topic | Consistent protocol definition |
|---|---|
| Time zero | Common eligible index admission date; follow-up starts at index |
| Population | Observable MIMIC-IV hospital cohort with common index and sufficiently observed OMR BP; not general population |
| SBP window | Candidate fixed `[index_date-730 days,index_date)`; alternatives are sensitivity/design checks |
| Exposure | Valid outpatient OMR SBP summary; strict pre-index date; count threshold unresolved |
| Intervention | Reference observed `A`; candidate `A-10` for `A>=130`, otherwise `A` |
| MI codes | Acute ICD-9 `410*`; ICD-10 `I21*`/`I22*`; historical ICD-9 `412`, ICD-10 `I25.2` |
| Prior MI | Documented acute/historical MI by index excluded; prior-MI adjustment omitted as structurally constant; no-code is not proven absence |
| Follow-up | 365 days is an unapproved candidate; begins at index and ends at first MI, death (if defensible), horizon, or defined observation end |
| Estimand | Fixed-horizon cumulative-incidence risk difference under candidate policy vs observed SBP; RR secondary |
| Adjustment | Candidate age at exposure-window start, sex, diagnoses strictly before that window, BMI only if validly pre-window; no automatic medication adjustment. Covariate cutoff awaits approval |
| Competing event | Death competes for primary cumulative incidence where dates/linkage defensible; otherwise distinct censoring alternative and underascertainment sensitivity |

The unresolved points are intentionally visible in relevant documents: the one-year horizon/death/censoring rule, minimum BP measurement count, and temporal cutoff for covariates within the exposure window. They are not represented as approved facts. The prior-MI covariate inconsistency is explicitly documented and resolved conservatively under the stated exclusion rule, pending team confirmation.

## Checks performed and not performed

- Confirmed all eight files are in `revised/phase1/` and no original Phase 1–9 artifact was edited during this task.
- Reviewed cross-document terminology and definitions as summarized above.
- Protocol checklist created; no empirical checklist item is claimed to pass solely from document preparation.
- No tests were run because no code was implemented and the task prohibits Phase 2 analyses. No effect, propensity, precision, or subgroup calculations were performed.
- No archive was extracted; no patient-level data were read or placed in the research-output folder.

## Researcher approvals required before later analysis

1. Minimum OMR reading count and final baseline exposure eligibility.
2. Whether 365-day follow-up is supportable and approved; operational observation end.
3. Death linkage/competing-risk primary rule under incomplete ascertainment.
4. Confirm prior-MI exclusion despite the candidate prior-MI covariate request.
5. Operational diagnosis look-backs, BMI/medication definitions, primary adjustment set, and estimator formulation.
6. Precision target and multiplicity procedure for age, sex and diabetes heterogeneity.
7. Conditional support findings and any restriction/alternative intervention, before effect estimation.

Phase 1 stops here. No subsequent phase has been started.

---

## Task 3 — Independent completion audit (2026-11-17)

This update records a direct review of the files in this directory, not a restatement of the earlier completion note. The audit found and corrected a directed cycle in the first DAG draft: the former `A -> HTN` arrow conflicted with `HTN -> A`. The revised graph represents earlier chronic BP history as a separate antecedent of a pre-window hypertension diagnosis and baseline SBP. The graph is now acyclic under a structural edge check. This is a temporal modeling decision, not clinical validation; alternative hypertension roles remain in the protocol for review.

### Deliverable audit

| Deliverable | Created | Reviewed | Validated | Status |
|---|---|---|---|---|
| `EXTENSION_PHASE1_RESEARCH_DESIGN.md` | Yes | Yes | Cross-checked design terms, counts, boundaries | Complete; horizon and covariate timing are candidates |
| `EXTENSION_PHASE1_CAUSAL_DAG.md` | Yes | Yes | Mermaid block/edges structurally checked; 65 directed edges, 34 nodes, acyclic | Complete working DAG; not clinically validated |
| `EXTENSION_PHASE1_ESTIMANDS.md` | Yes | Yes | Compared population, policy, outcome, horizon, death/censoring to other main docs | Complete; horizon/death rule unresolved |
| `EXTENSION_PHASE1_ANALYSIS_PLAN.md` | Yes | Yes | Checked future-only scope, adjustment timing, estimator and diagnostics consistency | Complete future plan; no analyses run |
| `PHASE1_DECISION_REGISTER.md` | Yes | Yes | Checked open decisions against main protocol | Complete |
| `PHASE1_ASSUMPTIONS_AND_LIMITATIONS.md` | Yes | Yes | Checked limits and assumptions against evidence supplied | Complete |
| `PHASE1_VALIDATION_CHECKLIST.md` | Yes | Yes | Checked checklist coverage of cohort, exposure, support, follow-up and methods | Complete; empirical items remain unchecked for later work |
| `PHASE1_COMPLETION_REPORT.md` | Yes | Yes | Updated with this independent audit and deliverable table | Complete |
| `WORKSPACE_AND_INPUT_INVENTORY.md` | Yes | Yes | Rechecked against Task 1 observations and current raw-folder listing | Complete; archive CRC integrity remains unverified |

### A. Successfully completed

- Verified all eight required protocol/support documents and the Task 1 inventory exist under `revised/phase1/` (nine files total).
- Reviewed the research question, population, index, outcome coding, OMR exposure/QC, candidate intervention, estimand, adjustment, competing events, censoring and selection strategy across the four main documents and supporting register.
- Corrected the DAG's cycle without changing the requested research question or silently resolving the uncertain hypertension role. The graph now separates earlier chronic BP history, pre-window hypertension status, baseline SBP, post-exposure medication/later BP, outcome, death, censoring, hospital selection, and BP-measurement selection.
- Kept the competing-risk cumulative-incidence risk difference as the primary estimand candidate, with a 365-day horizon explicitly unapproved. The alternative censoring quantity is identified as a different estimand.
- Confirmed the reported `5,008` and `4,797` figures occur only as explicitly rejected older event-anchored counts, not as revised common-baseline event counts.
- Recorded the prior-MI covariate/exclusion conflict and the recommended pre-exposure-window covariate cutoff as requiring team approval.

### B. Validation results

**Consistency checks:** The main documents agree on the common index date, target population, 730-day candidate window, OMR source and QC, strict `chartdate < index_date`, deterministic candidate shift, observed-SBP reference, first acute-MI outcome and codes, exclusion of documented acute/historical MI by index, unapproved one-year horizon, fixed-horizon cumulative-incidence risk difference, conditional death handling, and no future-event-free control requirement. The candidate adjustment set is age at window start, sex, and diagnoses documented before the exposure window; BMI is conditional on valid pre-window measurement. Prior MI is not adjusted because the stated exclusion makes it constant. Selection weighting is only a later sensitivity approach and cannot address unmeasured selection causes.

**Numerical checks:** All authoritative aggregate values specified for this audit were found in the protocol and match the supplied reconciliation:

| Reconciled measure | Reported value | Audit |
|---|---:|---|
| Unique patients with acute-MI-coded admissions | 9,703 | Match |
| Common-index cohort | 168,915 | Match |
| First acute-MI cases after index | 3,207 | Match |
| No recorded acute MI before censoring | 165,708 | Match |
| Eligible with any valid pre-index OMR BP | 54,565 | Match |
| Eligible with valid BP in two-year window | 53,956 | Match |
| Incident cases with any valid pre-index BP | 1,229 | Match |
| Incident cases with two-year-window BP | 1,223 | Match |
| Age <65 / age ≥65 cases in reported BP cohort | 375 / 848 | Match; sums to 1,223 |
| Male / female cases in reported BP cohort | 651 / 572 | Match; sums to 1,223 |
| Diabetes documented / not documented | 503 / 720 | Match; sums to 1,223 |

Other numeric values have a stated source or status: QC limits, 730-day window, 10-mmHg shift and 130-mmHg threshold are protocol specifications; 365 days is an unapproved horizon proposal; death counts and BP-to-ECG counts are attributed to their supplied reconciliation/Phase 0 evidence and retain their distinct units/denominators. Archive byte sizes/member inventories were locally read/listed in Task 1. The death universes are not combined.

**DAG/syntax checks:** One Mermaid fenced block is present and starts with `flowchart LR`. Its 65 `-->` edges resolve into 34 nodes under a structural parser; a directed-graph acyclicity check passes. The graph distinguishes candidate confounders, pre-window medication proxy, post-baseline medication mediator, unmeasured confounders, selection, outcome, death, and censoring. A Mermaid rendering tool was not available, so visual rendering was not verified. No claim of clinical DAG validation is made.

**Phase-boundary checks:** The protocol documents describe future analyses only. No treatment-effect estimate, outcome/propensity fit, AIPW result, CATE/causal-forest result, β-VAE investigation or retraining, dashboard change, or Phase 2 analysis was performed. No tests/models were run; the graph structure and document consistency checks are QA checks, not statistical tests.

**Isolation/governance checks:** Current Git status shows only the nine new untracked files under `revised/phase1/`; `git diff --name-only` is empty for tracked originals. The current `data/raw/` listing contains only the six previously inventoried archives and no extracted data folders. No patient-level rows, identifiers, predictions, or waveforms were added. No archive was extracted or modified during this audit; the Task 1 archive member listing was read-only. No manuscript, dashboard, or original Phase 1–9 artifact was overwritten.

### C. Unsuccessful or unavailable checks

- No Mermaid renderer (`mmdc`/Mermaid CLI) was available, so only fenced-block structure, edge parsing, and acyclicity were checked; rendered appearance remains unverified.
- Archive directory listings succeeded in Task 1, but a full archive CRC/integrity test was unavailable. This audit did not extract archives.
- Current extracted Parquet sources were absent at the Task 1 inventory location; aggregate values were therefore compared against the authoritative reconciliation supplied by the researcher and existing inventory documentation, not recomputed from row-level source data.
- An initial graph-check command failed because of shell quoting; it was replaced with a successful structural parse and acyclicity check. The failed command made no file changes.

### D. Unresolved research decisions

| Decision | Why it matters | Required decision/evidence |
|---|---|---|
| Minimum valid OMR reading count | Changes exposure reliability, selection, and analytic denominator | Approve ≥1/≥2/higher rule after aggregate reliability and selection review |
| Follow-up horizon | Defines the primary risk estimand; one-year record coverage may not represent continuous surveillance | Approve 365 days only after aggregate observation/event coverage review, or explicitly select another horizon and revise estimand |
| Death linkage and primary competing-risk rule | Death data are incomplete and represented in different units/universes | Reconcile patient/admission linkage and approve primary competing-event and underascertainment sensitivity rules |
| Observation-end/censoring rule | Loss from observed admissions can be informative and care elsewhere is unknown | Define data cutoff/last-observation rule; assess censoring predictors and assumptions |
| Prior-MI covariate vs exclusion | Excluding documented MI by index makes prior-MI adjustment structurally constant | Confirm exclusion takes precedence or formally revise eligibility and target population before analysis |
| Covariate temporal cutoff | “By index” diagnoses may postdate BP readings in the 730-day summary | Approve pre-window cutoff and operational look-back rules; verify chronology |
| Hypertension's causal role | Could proxy prior BP, cause later BP, or mark contact/detection | Clinical/statistical review of alternative DAG assumptions and sensitivity strategy |
| BMI and medication definitions | Measurement validity, missingness, adherence, and mediator status are uncertain | Verify source fields/timing and approve whether/how each enters sensitivity analyses |
| Estimator formulation | Continuous deterministic policy plus competing risks/censoring requires target-specific methods | Statistical review of g-computation primary candidate and any AIPW/IPW robustness formulation |
| Heterogeneity precision and multiplicity | Supplied case counts do not establish useful precision | Set interval-width/minimum detectable interaction target and multiplicity plan before subgroup work |
| Conditional positivity/support | Not established by marginal bins or global ranges | Later conditional density/support and shifted-value diagnostics; approve any restriction or altered intervention before estimation |

### E. Limitations

**Existing data limitations:** incomplete pre-observation history and possible undocumented MI; selected hospital and outpatient BP observation; intermittent admissions rather than continuous surveillance; incomplete death ascertainment; incomplete outpatient medication capture; smoking unavailable and lipids extremely sparse; potential measurement-frequency bias; OMR date-only precision; coded admission date is not biological onset; subgroup precision unknown.

**Methodological assumptions:** consistency for a measured-value shift; no unmeasured confounding; conditional positivity; correct code/event classification; valid covariate timing; selection exchangeability; censoring and competing-risk assumptions; and model specification. These are not validated facts. A baseline mean shift does not specify or demonstrate a sustained treatment regimen.

**Local environment limitations:** extracted source tables were not present for this audit; no Mermaid renderer or full RAR CRC tester was available per Task 1 inventory. Python/networkx supported the acyclicity check. These limitations did not prevent protocol-document review, but they prevent fresh row-level recomputation and visual DAG rendering.

### F. Phase 1 gate

**The documentation package is ready for supervisor/research-team review. It is not approval to begin Phase 2.** The team must resolve the decisions above, especially exposure measurement count, horizon/death/censoring, prior-MI eligibility conflict, covariate timing, estimator, and subgroup precision. No Phase 2 analysis is authorized or started by this audit.
