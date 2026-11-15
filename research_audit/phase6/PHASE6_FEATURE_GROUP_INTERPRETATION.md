# Phase 6A - Feature Group Interpretation

The mean absolute standardized adjusted differences and significant-feature counts below summarize the completed Phase 5 estimates. They are descriptive summaries of correlated features, not independent group replications.

| Group | Features | BH-significant | Mean absolute adjusted difference (SD) | Mean signed difference (SD) |
|---|---:|---:|---:|---:|
| ST | 12 | 10 | 0.162 | -0.048 |
| T | 24 | 22 | 0.129 | +0.000 |
| RR | 2 | 2 | 0.128 | -0.128 |
| QRS | 2 | 1 | 0.091 | +0.068 |
| Other morphology | 6 | 5 | 0.062 | +0.059 |
| R | 24 | 13 | 0.053 | -0.035 |
| Q | 24 | 13 | 0.053 | +0.006 |

ST features show the largest average absolute adjusted contrast (0.162 SD), with 10/12 passing BH FDR. T features average 0.129 SD, with 22/24 passing. Their signs vary across leads: for example, ST_Elev_I and ST_Elev_aVF are negative while ST_Elev_aVR is positive; T amplitudes are positive in aVR and V1 but negative in several lateral/precordial leads. This lead dependence is a pattern to describe, not a validated diagnostic signature.

RR (2/2, mean absolute 0.128 SD) and QRS (1/2, 0.091 SD) also show group-level evidence. Q and R have smaller mean absolute standardized contrasts (about 0.053 SD), though 13 features in each family pass BH. Other morphology has 5/6 features pass with a 0.062 SD mean absolute contrast. `QRS_Dur_Global_count` is technical support and remains distinct from physiology.

The Phase 4 test-split check and training diagnostics show strong residual dependence across features. Accordingly, lead summaries and feature-group results should be read as correlated measurements from the same ECG, not as multiple independent confirmations. See `PHASE5_FEATURE_GROUP_RESULTS.csv` and `PHASE6_FEATURE_NOVELTY_RESULTS.csv` for full estimates.
