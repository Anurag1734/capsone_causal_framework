# Revised Phase 1 — Estimands

Status: **Finalised design elements** follow the research brief. The one-year horizon, measurement-count threshold, and final death/censoring estimand remain **recommended candidates / unresolved decisions** pending team approval. No estimand is estimated in this phase.

## 1. Notation and target population

For each patient `i`, let `W_i` be measured pre-index covariates; `A_i` the baseline SBP summary; `T_i` time from index to first acute-MI-coded admission; `D_i` time to death; and `C_i` time to end of observable follow-up. Let `S_i=1` indicate entry into the common hospital cohort, eligibility at index, and sufficiently measured baseline OMR BP under the final measurement-count rule. Let `Y_i` indicate a first post-index acute-MI-coded admission before the horizon and before death.

The target population is the selected MIMIC-IV hospital-observed population satisfying common baseline and BP eligibility, not the general population and not all people with hypertension. It does not guarantee no unrecorded pre-index MI or continuous surveillance. The primary analysis conditions on `S=1`; any transport to those without OMR BP requires additional selection assumptions.

## 2. Exposure conditions

`A` is the arithmetic mean of valid outpatient OMR SBP readings in `[index_date - 730 days, index_date)`, with both SBP and DBP parsed, SBP 60–260, DBP 20–160, SBP>DBP, and chartdate strictly before index date. Final minimum count remains unresolved; one qualifying reading is the reported feasibility threshold, not automatically the final primary threshold.

Reference condition: `d0(A)=A` (observed baseline SBP).  
Recommended deterministic modified treatment policy: `d1(A)=A-10` when `A>=130`, otherwise `d1(A)=A`.

The mapping is a hypothetical intervention on a measured summary, not a prescription or observed sustained reduction. Under each condition, the outcome risk is interpreted by replacing baseline `A` with the corresponding policy value while retaining the target population's covariate distribution. The shifted values require conditional support assessment. Values below 130 are unchanged. No claim of established positivity or safety is made.

## 3. Primary estimand

**Recommended primary estimand (requires horizon and death rule approval):** the population-average absolute difference in cumulative incidence by `τ=365 days` of first acute-MI-coded admission under the deterministic SBP policy versus observed SBP, among `S=1` patients.

Let `F_M^{d}(τ | S=1)` denote the cumulative incidence of first acute MI by time `τ` under exposure policy `d`, with death treated as a competing event (not a censoring event) when ascertainment/linkage supports that definition. Then:

`RD(τ) = F_M^{d1}(τ | S=1) - F_M^{d0}(τ | S=1)`.

Negative values indicate lower risk under the candidate shift, subject to identification assumptions. Report both risks, their absolute difference, and a two-sided 95% uncertainty interval. **The 365-day horizon is a candidate, not an approved or Phase 0 validated clinical follow-up duration.** First establish aggregate observation and event coverage over time; if one year is not defensible, the team must approve a new horizon before analysis, and the estimand must be relabelled accordingly.

### Competing events and observation end

Death before MI is a competing event, not ordinary independent censoring, for the cumulative-incidence estimand. Available death fields are incomplete and have different units/universes: 27,980 patient-level DOD values, 8,592 patient-level in-hospital death timestamps, and 8,598 admission-level death timestamps. Do not pool them as a single complete death variable. Establish linkage/consistency, use only defensible dates, and quantify underascertainment sensitivity.

Administrative end at `τ` is fixed by design. Earlier loss of observable records is censoring/observation termination. Use an explicitly defined end-of-observation rule (candidate: last known eligible admission/discharge record within data coverage) and acknowledge it is not proof the person left care. If censoring is handled with weights/modeling, the target remains identifiable only under conditional independent censoring and positivity. If death cannot be reliably ascertained, an alternative that censors at observed death is not equivalent to the primary competing-risk cumulative incidence and requires a separately stated estimand and sensitivity interpretation.

## 4. Secondary estimands

1. **Risk ratio:** `RR(τ)=F_M^{d1}(τ|S=1)/F_M^{d0}(τ|S=1)`. Report as secondary because relative changes can obscure absolute risk and become unstable when baseline risk is small.
2. **Relative risk reduction:** `(F_M^{d0}-F_M^{d1})/F_M^{d0}=1-RR`, secondary and only with both risks shown.
3. **Risk under each policy:** `F_M^{d0}(τ|S=1)` and `F_M^{d1}(τ|S=1)`, required components of the primary contrast.
4. **Effect heterogeneity:** prespecified contrasts of subgroup-specific `RD(τ)` by age (<65/≥65), recorded sex, and documented diabetes status. These are secondary and contingent on precision targets and support within subgroups. No CATE model is part of Phase 1.

Cause-specific hazard ratios are not the primary estimand: they are rate contrasts among those still event-free and are not cumulative risks. A competing-risk cumulative incidence, cause-specific hazard, and fixed-horizon risk answer different questions and must not be conflated.

## 5. Population and outcome definitions

Common index uses earliest eligible non-acute-MI admission under the same rules for all; documented acute or historical MI on/before index excludes the patient. Event is first acute MI admission strictly after index (ICD-9 `410*`, ICD-10 `I21*`/`I22*`). Historical documentation is ICD-9 `412` or ICD-10 `I25.2`; previously recorded acute MI is distinct from historical code and also causes exclusion when at/before index. No code in available data means no documented event, not proven never-MI. A coded admission date is an administrative event proxy, not biological onset.

## 6. Other target questions (not primary estimands)

- BP-to-ECG morphology association is a separate module with a separate population, index ECG, timing, and DAG. Phase 0 counts (52,267 with BP and ECG; 38,987 BP before ECG) do not define the incident-MI denominator.
- An individual scenario output is a later model-based prediction contrast conditional on validated population model, overlap, and uncertainty. It is not the individual's causal effect or counterfactual truth, and never clinical advice.
- β-VAE counterfactual representations are outside Phase 1; no encoder/decoder is audited or run here.

## 7. Identification population and interpretation limits

The estimand applies to those selected into MIMIC-IV hospital observation, eligible at index, and meeting the final OMR measurement criterion. It does not identify an effect for all community patients or those with no outpatient BP measurements without transport/selection assumptions. The intervention value may not represent a unique treatment version. Exchangeability, conditional support, valid exposure/outcome classification, selection assumptions, censoring assumptions, and death ascertainment remain to be assessed. The count of cases is not a precision guarantee.
