# Phase 3 ECG Selection Bias and Missingness Report

## Population and definition

Selection is defined at the **adult admission** level using all 431,231 admissions in the corrected chronology/diagnosis audit. An admission is selected when at least one master ECG falls within the valid ED-registration (or inpatient admission fallback) through discharge interval. The available ECG masters cover 191,275 admissions; 239,956 have no eligible master ECG. The selection rate is **44.36%**.

Of 375,930 master ECG rows, 56 have ED-registration timestamps after discharge and use inpatient admission time as the fallback start. A further 54 rows have admission start after discharge and are excluded; 288 ECG rows in total fall outside valid episode bounds. The dataset includes no ECG with an invalid episode interval.

The selection model is a diagnostic model for ECG availability, not an outcome association model. It uses measured age, sex, acute and historical/prior MI indicators, and prior-admission diabetes, hypertension, and CKD indicators. No outcome weights were applied.

## Selected versus nonselected admissions

| Characteristic | ECG available | No eligible ECG | Standardized mean difference |
|---|---:|---:|---:|
| Age, mean years | 62.22 | 52.61 | 0.524 |
| Female | 49.14% | 54.59% | -0.109 |
| Acute MI diagnosis | 3.84% | 2.01% | 0.109 |
| Historical MI code this admission | 8.18% | 3.51% | 0.200 |
| Any current historical/prior MI documentation | 13.87% | 6.52% | 0.245 |
| Prior diabetes code | 22.57% | 14.89% | 0.198 |
| Prior hypertension code | 43.80% | 30.86% | 0.270 |
| Prior CKD code | 17.47% | 9.47% | 0.236 |
| Prior MI code | 10.70% | 5.24% | 0.203 |

ECG availability is therefore not a random sample of admissions on measured characteristics. ECG-selected admissions are older and have higher recorded acute-MI and comorbidity prevalence; sex composition also differs. These imbalances can limit transportability and can contribute to selection bias in an ECG-only analysis.

## Missingness and variable availability

Anchor age, recorded sex, acute/history diagnosis flags, and prior-admission diagnosis indicators have **0 missing values** in the admission denominator and selected analysis dataset. All 95 ECG features are finite and nonmissing for all 191,275 selected records. Zero missingness does not mean disease absence: comorbidity and prior-MI flags indicate previously coded inpatient diagnoses and may miss uncoded disease or outpatient-only history.

Smoking and lipid values are not available in the current analysis-ready tables. The OMR coverage catalogue lists BMI and eGFR measures, but row-level OMR observations have not been joined to admissions; BMI/eGFR are therefore not included as measured covariates here. Any future OMR linkage must establish measurement time and admission linkage before treating them as baseline. In-hospital treatments are not used as baseline adjustment variables.

## Selection-weighting feasibility

A logistic model of ECG availability using the measured variables above showed overlapping *observed fitted propensity ranges*: 0.195–0.864 for ECG-available and no-ECG admissions. Among ECG-selected admissions, diagnostic inverse-probability weights had a maximum of 5.12 and 99th percentile of 4.64; the stabilized-weight effective sample size was approximately **173,194** versus 191,275 selected admissions. These results show no gross lack of support under this particular measured-covariate model and make weighting feasible to investigate as a sensitivity analysis.

This is not proof of conditional positivity or successful bias correction. The propensity model may omit relevant determinants; ECG ordering may depend on acute severity, symptoms, care pathway, clinician judgment, and prior ECG access not captured by these variables. Positivity must be checked within clinically relevant strata, model specification and calibration examined, and weight influence assessed before any weighted analysis. Do not claim that weighting removes unmeasured selection bias.

## Target population and recommendation

The primary estimand is restricted to admissions with an eligible ECG. It should not be generalized to all MIMIC-IV admissions without additional assumptions. If the scientific target is all adult admissions, estimate selection weights only as a prespecified sensitivity analysis and report weighted and unweighted results side by side. Keep the primary analysis associational, not causal.

Machine-readable counts and diagnostics are in `data/analysis/observational_mi_ecg/selection_diagnostics.csv`; missingness is in `dataset_missingness.csv`.
