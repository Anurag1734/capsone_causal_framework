# Revised Research Extension — Phase 1 Study Design

**Study title:** *Modifiable Cardiovascular Risk Factors, Heterogeneous Causal Effects and Counterfactual ECG Modelling*  
**Phase:** Study design only. No cohorts were rebuilt, no models fitted, and no treatment effects estimated.

Status labels used throughout: **Finalised design choice** means specified by the research brief; **Recommended candidate** means a reasoned proposal for team review; **Unresolved decision** requires researcher approval; **Assumption requiring empirical assessment** cannot be established from the current aggregate evidence.

## 1. Question and scope

Among eligible patients with sufficiently measured baseline blood pressure and appropriate follow-up, what is the effect of a supported reduction in systolic blood pressure (SBP) on risk of a first acute-MI-coded admission?

The target is the population of MIMIC-IV patients who enter the observable hospital cohort and satisfy the common-baseline eligibility criteria. This is not a general-population cohort. MIMIC-IV does not establish complete health history before a patient's first recorded admission, complete outpatient surveillance, or complete continuous follow-up. The result, if later identified, applies to this selected, observable, BP-measured population under the stated assumptions.

**Finalised design choice:** incident first acute-MI admission, common index rules for cases and controls, no conditioning on remaining event-free, and an OMR-based pre-index exposure. The BP-to-ECG and individual scenario modules are separate downstream questions; neither is analysed in Phase 1.

## 2. Population, index, and eligibility

### 2.1 Candidate source cohort

Start from patients represented in the linked hospital admission source universe. Identify the earliest admission satisfying the common index eligibility criteria. Candidate exclusions at or before index are documented acute MI (ICD-9 `410*`, ICD-10 `I21*`/`I22*`) or historical MI documentation (ICD-9 `412`, ICD-10 `I25.2`). Require valid admission dates and an event strictly after index to count as an incident event. The exact age restriction, handling of transfers/duplicate admissions, and final admission eligibility flags must follow the source cohort's validated rules and be confirmed before extraction.

### 2.2 Index date rule

**Finalised design choice:** apply the same eligibility and date logic to both groups.

- Cases: candidate index is their earliest non-acute-MI admission before their first acute-MI-coded admission.
- Controls: candidate index is their earliest non-acute-MI admission under the same eligibility and history-exclusion rules.
- Exclude documented acute or historical MI on or before index. First acute MI must be strictly after index.
- Do not require a control to remain MI-free. A participant whose first eligible acute MI occurs later contributes an event at that time.
- Time zero is the index calendar date. Because OMR chart dates have date precision, readings on that date are not baseline.

An acute-MI-coded admission is an administrative clinical-record event proxy, not verified biological onset. Absence of a code means absence of documented MI in the available record, not proven absence of prior MI. Patients can have unrecorded events before observation.

### 2.3 Reconciled aggregate feasibility evidence

Use the current reconciliation as the authoritative aggregate evidence: 9,703 unique patients with acute-MI-coded admissions; common-index cohort 168,915; 3,207 first acute-MI cases after index; 165,708 without a recorded acute MI before censoring; 54,565 eligible with any valid pre-index OMR BP; 53,956 with qualifying BP in the two-year pre-index window; and 1,229 / 1,223 corresponding incident cases with any valid BP / two-year-window BP. These are not the final analytic denominator: count rules for exposure sufficiency, follow-up, death, and censoring remain to be applied. Earlier 5,008 / 4,797 event-anchored counts are not substitutes.

## 3. Exposure measurement and eligibility

**Finalised candidate source/QC rules:** outpatient OMR BP; parse both SBP and DBP from `SBP/DBP`; require SBP 60–260 mmHg, DBP 20–160 mmHg, and SBP > DBP. Use only readings with `chartdate < index_date` because chartdate lacks time-of-day precision.

**Recommended candidate window:** `[index_date - 730 days, index_date)`. One-year and three-year windows are prespecified sensitivity/design alternatives, not windows to select according to the estimated effect.

**Recommended candidate summary:** arithmetic mean of all valid SBP values in the window. Retain for later data construction the number of readings, mean, median, within-window SD or other prespecified variability measure, missingness, and dates/frequency summaries. Assess whether a small number of frequent attenders dominates the mean; compare patient-level summaries and frequency-stratified estimates. Do not treat repeated readings as independent people.

**Unresolved decision:** minimum measurement count. At least one valid reading is the feasibility definition reported by reconciliation, not necessarily sufficient exposure reliability. Compare ≥1, ≥2, and a prespecified higher-count rule; recommend ≥2 for the primary analytic exposure only if this does not make the target population unacceptably selected and reliability/selection diagnostics support it. Final threshold requires team approval before Phase 2. No final exposure variable or denominator is claimed here.

## 4. Intervention and comparison

Let `A` be the selected baseline SBP summary in mmHg. Reference is observed `A`. The primary candidate modified treatment policy is the deterministic map

`d(A) = A - 10` if `A >= 130`; `d(A) = A` if `A < 130`.

The candidate intervention condition evaluates each otherwise eligible person's outcome risk at `d(A)`; the reference condition evaluates risk at `A`. Values under 130 remain observed. Given the SBP QC lower bound of 60, the arithmetic shift cannot produce an SBP below 120 among shifted records. This physical bound does **not** establish conditional empirical support, feasibility, or safety. No value is to be extrapolated beyond later-supported conditional exposure regions; shifted values, conditional density/overlap, support by confounder profile, and fraction outside support must be assessed. Any trimming or restriction must be prespecified and justified before estimation.

**Recommended candidate:** deterministic modified treatment policy, because it directly expresses the requested 10-mmHg shift while leaving the lower-SBP group unchanged. A stochastic shift or support-truncated stochastic intervention is an alternative if the deterministic map has inadequate support; that would be a changed intervention requiring approval. The deterministic map has a many-to-one region around the 130-mmHg threshold and needs careful support/density diagnostics; it is not declared identified by marginal SBP summaries.

This is a hypothetical shift in a single baseline measured summary. It is not a demonstrated sustained real-world regimen, adherence pattern, medication strategy, or clinical prescription. OMR does not show that a person sustained a 10-mmHg reduction after index.

## 5. Outcome, follow-up, death, and censoring

**Outcome:** first acute-MI-coded admission after index using ICD-9 `410*` or ICD-10 `I21*`/`I22*`. Historical MI codes (`412`, `I25.2`) are not acute outcomes. Later acute MI admissions are not additional primary events.

Follow-up begins at index and ends at the earliest of first acute MI, the selected horizon, death (if date and linkage are defensible), or end of observable admission-record follow-up. Hospital data do not imply continuous insurance enrollment or complete health-system surveillance. Last observed admission/discharge is an imperfect observation-end proxy; leaving the hospital database is not known to equal loss of clinical follow-up at that exact time.

**Unresolved decision — horizon:** recommend a fixed **365-day (one-year)** horizon for team review because it defines an interpretable fixed-horizon risk while limiting extrapolation over sparse encounter records. This duration is not clinically validated or approved by Phase 0. Before approval, tabulate aggregate event and observation coverage by elapsed time, assess whether the source supports one-year ascertainment, and compare feasible alternatives (for example, shorter horizons) without choosing based on effect estimates. If one-year surveillance is not defensible, return the horizon choice to the team; do not silently switch estimands.

Death before MI is a competing event where death dates can be linked and judged sufficiently reliable. Reconciliation reports 27,980 nonmissing patient-level DOD values in an 180,733-patient admission-linked universe, 8,592 patient-level in-hospital death timestamps, and 8,598 admission-level death timestamps in a different table/universe. These units and universes must not be combined. Missing death date is not evidence of survival. Primary candidate is cumulative incidence of MI before death by the approved horizon under a competing-risk framework, with explicit death under-ascertainment sensitivity. If death ascertainment is too incomplete, a clearly labelled alternative censoring estimand may be reported only with assumptions; it is not the same quantity as cumulative incidence.

## 6. Estimand and adjustment overview

The primary estimand is the population-average absolute difference in horizon-specific cumulative incidence of first acute-MI admission under `d(A)` versus observed `A` among patients satisfying common baseline, BP sufficiency, and follow-up eligibility. Define the risk ratio as secondary; report both intervention and reference risks and uncertainty intervals. Full notation and censoring/death definitions are in `EXTENSION_PHASE1_ESTIMANDS.md`.

Candidate baseline confounders: age, sex, diabetes, hypertension diagnosis/status, CKD, and BMI when validly measured before the exposure period. Since `A` summarizes readings throughout the 730-day window, a diagnosis first recorded during that window may postdate some contributing BP readings. **Recommended temporal rule:** define time-varying diagnoses and medication/BMI covariates using information available strictly before the exposure-window start (`index_date - 730 days`); use age at that start and recorded sex. This is stricter than merely “by index” and may miss relevant recent conditions. A different ordering rule requires explicit approval and a DAG rationale. Smoking and lipids are important unmeasured/insufficiently measured confounders and must not be fabricated. No post-exposure information is a baseline confounder.

**Prior-MI conflict:** the eligibility rule excludes all documented acute or historical MI at/before index. Therefore a candidate prior-MI adjustment indicator is structurally zero among correctly classified eligible participants and cannot serve as an estimable confounder. Do not put it in the primary adjustment set. Retain the exclusion flag/audit and consider a separately approved sensitivity population only if the team changes eligibility. This is a decision requiring explicit review because the supplied candidate covariate list mentions prior MI.

Hypertension may be a confounder/proxy for chronic BP history, but its diagnosis can be downstream of historical BP and measurement/contact processes. Primary adjustment should use documented status before the exposure window under the recommended temporal rule, while DAG alternatives and sensitivity analyses examine diagnosis timing/meaning. Diabetes subgroup status must follow the same pre-exposure timing rule for causal effect modification; supplied by-index subgroup counts are feasibility descriptions only. See the DAG and decision register.

## 7. Selection, missingness, and identification

Selection occurs at hospital entry, survival/observation to index, and having outpatient BP recorded. Compare the common-index cohort with the BP-observed subset using only pre-index available variables. A later selection model may use age, sex, admission history/utilization, diagnoses, prior encounter counts, and other measured pre-index predictors. Inverse-probability selection weighting is a sensitivity approach, not a cure: it cannot correct unmeasured causes of BP measurement or selection. Document missingness and measurement frequency, avoid fictional smoking/lipid histories, and assess missing BMI/medication handling explicitly.

Identification requires consistency for the precisely defined baseline shift; conditional exchangeability; conditional positivity/support for shifted SBP across confounder profiles; correct temporality and exposure/outcome classification; adequate censoring/competing-event handling; and valid selection/missing-data assumptions. These are assumptions, not facts established by the Phase 0 audits. Smoking/lipids, incomplete medication capture, unrecorded MI, incomplete death ascertainment, and intermittent hospital observation threaten them.

## 8. Heterogeneity, downstream modules, and Phase 1 boundary

Prespecify age (<65 / ≥65), sex (recorded male/female categories, with handling of any other/missing category specified from actual data), and documented diabetes (yes/no under pre-index rule) as candidate modifiers. Reconciliation reports 1,223 two-year-window BP-available incident cases: age <65 375, age ≥65 848, male 651, female 572, documented diabetes 503, no documented diabetes 720. Counts alone do not establish adequate precision. Require an approved precision target and interval-width/minimum-detectable interaction target before subgroup estimation.

The BP-to-ECG module is separate (Phase 0: 52,267 non-MI patients with BP and ECG; 38,987 BP-before-ECG). It requires its own ECG index, BP look-back, temporal gap, eligibility, DAG, feature completeness, and multiplicity plan. Do not merge denominators. A future individual scenario estimator is research-only and depends on a validated population model; it must display uncertainty/support and never prescribe or claim an individual's true cause. No such analysis/software is built now.

This protocol is Phase 1 only. It does not estimate effects, fit outcome/propensity models or causal forests, rebuild cohorts, process row-level archives, or begin ECG/β-VAE work. Cross-references: DAG in `EXTENSION_PHASE1_CAUSAL_DAG.md`; estimands in `EXTENSION_PHASE1_ESTIMANDS.md`; future analyses in `EXTENSION_PHASE1_ANALYSIS_PLAN.md`; decisions and assumptions in supporting files.
