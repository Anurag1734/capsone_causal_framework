# Phase 7D - Age and Sex Subgroups

The original roadmap requests age and sex subgroup analyses but does not specify age cut points. We used <65 and >=65 years and recorded sex F and M. The Phase 3 primary cohort, 95 outcomes, acute-only definition, and Phase 4 adjustment variables were retained; within a sex stratum the constant sex variable was omitted. Five-fold patient-group nuisance fitting and patient-clustered Wald confidence intervals were used. BH FDR was applied within each subgroup across 95 features, and direct age/sex interaction contrasts were BH-adjusted separately across 95 features.

| Subgroup | Admissions | Patients | MI cases | Controls | Features passing within-group BH | Direction agreement with primary | Median CI width (SD) |
|---|---:|---:|---:|---:|---:|---:|---:|
| age_<65 | 90,395 | 51,381 | 2,551 | 87,844 | 66 | 86/95 | 0.092 |
| age_>=65 | 76,671 | 42,565 | 4,802 | 71,869 | 57 | 89/95 | 0.080 |
| sex_F | 84,650 | 46,950 | 2,877 | 81,773 | 58 | 85/95 | 0.088 |
| sex_M | 82,416 | 46,996 | 4,476 | 77,940 | 56 | 89/95 | 0.085 |

Direct interaction tests found 11 age contrasts and 13 sex contrasts passing BH q<0.05. The leading age interaction features include ST_Elev_V5, ST_Elev_V6, and R_Amp_aVR; sex interactions include RR_Mean_Global_iqr, R_Amp_aVF, R_Amp_V2, and ST_Elev_V2. These are adjusted exploratory differences, not proof of biological effect modification; subgroup and interaction estimates are in `PHASE7_SUBGROUP_RESULTS.csv` and `PHASE7_SUBGROUP_INTERACTIONS.csv`.

All subgroup case counts exceed 2,500, but direct effects still have uncertainty and multiple testing. Do not infer a subgroup difference from significance in one group and nonsignificance in another; use the interaction contrast and its interval. Age boundary choice was not specified by the roadmap and should be treated as an implementation choice.
