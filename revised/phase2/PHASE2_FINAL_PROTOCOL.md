# Phase 2 Final Execution Protocol (Phase 2.0)

> **Status update:** This protocol is the frozen design reference, not evidence that its feasibility gates passed. Read it with `PHASE2_GATE0_REMEDIATION_REPORT.md`; the current evidence leaves follow-up ascertainment, death, and pre-window disease adjustment unresolved. No Phase 2.1 cohort construction is authorized by this remediation task.

**Study:** *Modifiable Cardiovascular Risk Factors, Heterogeneous Causal Effects and Counterfactual ECG Modelling*  
**Current phase:** design closure and aggregate feasibility only. Cohort construction/effect estimation have not started.

## Objective and estimand

Among eligible patients with sufficiently measured baseline OMR BP and defensible follow-up, estimate the population-average effect of a hypothetical 10 mmHg reduction in baseline SBP on fixed-horizon cumulative incidence of first acute-MI-coded admission.

Reference: `d0(A)=A`. Intervention: `d1(A)=A-10 I(A>=130)`. Primary: `RD(τ)=F_M^d1(τ)-F_M^d0(τ)`. Report policy-specific risks and 95% uncertainty interval; risk ratio is secondary. `F_M` is first acute-MI cumulative incidence with death competing. Candidate τ is 365 elapsed days, not yet demonstrated feasible. It is a hypothetical shift of a measured summary, not prescription, medication assignment, or sustained effect.

## Population/index/outcome

Target the selected population of MIMIC-IV patients entering the observable hospital cohort and satisfying common index/BP eligibility; not a general-population sample and not a claim of complete pre-first-admission history. Cases use earliest eligible nonacute admission strictly before first acute-coded MI. Controls use the earliest eligible nonacute admission under identical criteria; never condition on future event-free survival. Exclude documented acute MI (ICD-9 `410*`, ICD-10 `I21*`/`I22*`) or historical MI (ICD-9 `412`, ICD-10 `I25.2`) on/before index. Prior MI is not in the adjustment set because this exclusion makes it constant. First acute MI strictly after index is event; a later MI makes a control an incident case. Admission date is an administrative proxy, not biological onset. No code means no documentation, not proven no prior MI.

## Exposure/intervention

Use outpatient OMR; parse SBP and DBP; accept SBP 60–260, DBP 20–160 mmHg, and SBP>DBP; only chartdate strictly before index. Candidate window `[index_date-730d,index_date)`; mean SBP. Recommend ≥2 valid readings as primary threshold if aggregate retention/event/measurement diagnostics support it; compare ≥1/≥2/≥3/≥4 without effect-guided selection. At present, only ≥1 counts are known. The fixed 10 mmHg shift is not to be altered for support problems. Unsupported values must be reported; no automatic trimming.

## Adjustment and identification

Temporal cutoff is the beginning of the exposure window. Candidate primary covariates: age at cutoff, recorded sex, documented diabetes, hypertension and CKD strictly before cutoff; BMI only with valid pre-cutoff OMR measurement. Use all available earlier diagnosis history but distinguish no documented history from true absence. No post-window/post-index diagnosis, medication by default, troponin, post-index lab, or acute-care variable. Smoking unavailable, lipids sparse, medication ascertainment incomplete. Exchangeability, consistency, conditional support, outcome classification, selection, and censoring assumptions require empirical assessment.

## Follow-up, death, and censoring

Candidate fixed horizon 365 days; compare 90/180/365/730 through aggregate feasibility. Death competes with MI if date linkage is adequate. Reconciliation: patient DOD sources agree for 27,980 shared nonmissing values, but DOD exists in only 27,980/180,733 admission-linked patients; admission-level and patient-level in-hospital timestamps agree for 8,592 patients, while 557/8,598 admission timestamp rows fall outside their admission interval. This is insufficient to identify complete competing-risk incidence. Missing DOD is not survival. Last encounter is not continuous observation. Administrative boundary must be verified from release provenance, and individual censor dates need defensible observation data. Until resolved, full fixed-horizon cumulative incidence is blocked.

## Estimator and inference

Future primary candidate: discrete-time competing-risk g-computation (30-day intervals with a final partial interval; weekly sensitivity). Model mutually exclusive first MI/death/no-event probabilities with flexible elapsed-time and continuous SBP functions, standardize predictions under both policies, and compute MI CIF recursively. Use censoring weights/joint censor model only if censor time is observed and conditional independent censoring/positivity are defensible. A binary endpoint logit ignoring death/censoring is prohibited. Generic original binary AIPW is not primary. Use 1,000 patient-level bootstrap replicates for 95% percentile intervals; if flexible nuisance learning is used, five-fold cross-fitting grouped by patient. Validate method and interval coverage by simulation before analysis.

## Heterogeneity

Secondary modifiers: age <65/≥65 at cutoff, recorded sex, documented diabetes before cutoff. The supplied case counts (375/848 age, 651/572 sex, 503/720 diabetes) are descriptive evidence, not final analytic cells or power. Report subgroup risks/RDs, direct interaction contrasts, and joint omnibus heterogeneity. Holm FWER 0.05 across three modifier tests. Research team must approve clinically meaningful MDE/CI-width target after design simulation; no CATE or causal forest.

## Status and boundary

The scientific definitions, code rules, prior-MI exclusion, covariate cutoff, estimator candidate, uncertainty and multiplicity recommendations are specified. BP count/horizon are empirically gated; death/censoring and conditional support are blocked; subgroup precision requires approval. `PHASE2_GATE_CRITERIA.md` is **not passed**. This protocol guides the next decision/feasibility work but does not authorize cohort construction or effect estimation. See supporting cohort, follow-up, covariate, estimation, decision and aggregate files for implementation detail and provenance.
