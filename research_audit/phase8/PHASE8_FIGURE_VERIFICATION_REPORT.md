# Phase 8 Figure Verification Report

**Scope:** visual inspection of all ten saved PNG figures, review of `FIGURE_CAPTIONS.md`, and comparison of labels/caption claims with finalized Phase 3–7 and Phase 8 aggregate tables. No models were refit and no binaries were rebuilt.

| Figure | Verification |
|---:|---|
| 1 | Cohort flow labels the 431,231 denominator, 191,275 eligible ECG admissions, 44.36% selection, 24,209 history-only admissions, 159,713 clean controls, and 167,066 primary comparison. History-only admissions are visibly separate. Counts agree with Table 1. |
| 2 | The graph is explicitly labeled as proposed/roadmap-based; the image notes unknown onset timing and that the diagnosis-to-feature direction is not established. Selection and unmeasured severity/symptom/care pathway are represented. It is not labeled as a learned DAG. |
| 3 | Layer 1 forest plot uses percentage-point risk differences and confidence intervals with zero reference. Hypertension is inverse, CKD interval crosses zero, and prior MI has a much larger descriptive estimate. Caption supplies the interpretation and patient-cluster interval type. |
| 4 | All 95 estimates and 95% intervals are plotted in feature-SD units. Feature groups have distinct colors and the technical/support count metric is separately labeled. Axis title states the scale; table values agree with Figure 4 ordering/directions. |
| 5 | Crude and adjusted contrasts use the same standardized feature scale and a y=x reference. The visual and caption describe association magnitudes; no causal or predictive language is used. |
| 6 | Group summary uses mean absolute adjusted standardized effects, with BH counts annotated per group. It is descriptive and caption warns that correlated features are not independent replications. Technical support is kept outside the physiological groups. |
| 7 | The displayed subset is the primary BH-significant family; legend/caption distinguishes the technical/support finding from physiological features. The 67 total / 66 physiological + 1 technical distinction matches Table 3. |
| 8 | Primary estimates are compared with selection-weighted and broader-current-code estimates on standardized scales, with equality references. Captions state the broad definition changes case mix and attenuates ST/T means. |
| 9 | Age and sex plots show direct interaction estimates and confidence intervals for features passing BH, rather than comparing subgroup p-values. Axes specify SD units. Captions note chosen age strata and feature-specific interpretation. |
| 10 | Fixed-profile predictions are identified as model-implied exploratory values, with no profile-specific intervals. Axes state stored feature units; caption says these are not observed counterfactuals or intervention effects. |

## Conclusion

The ten figures and numbering are consistent with manuscript references and captions. Labels and units are appropriate to the displayed results; no image implies patient-level prediction. The DAG figure communicates assumptions with explicit caveats, and model-implied profiles retain their exploratory interpretation. Existing files remain in `PHASE8_FIGURES/`; the demo reads these images if present. No generated figure binary was added or rebuilt as part of this audit.
