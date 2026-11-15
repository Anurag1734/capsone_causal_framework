# Novelty Assessment

## Decision

**Novelty is not established.** The work may offer a differentiated empirical characterization, but it should not be called the first, novel, or unprecedented study on MI ECG morphology or MIMIC-IV ECG. A focused narrative literature comparison has been assembled; it is not an exhaustive systematic review.

## What is distinct in this project

- A two-layer admission-level structure: recorded chronic risk-factor histories versus acute MI coding, followed by acute-code versus clean-control contrasts in ECG morphology.
- A cohort explicitly restricted to one earliest eligible in-episode ECG per adult admission, with the 44.36% ECG availability rate reported against the adult-admission denominator.
- Adjusted contrasts across 95 handcrafted features, with feature-group summaries, FDR correction, patient-group cross-fitting, and patient-cluster uncertainty.
- Sensitivity analyses covering measured-covariate ECG selection, broader same-admission codes, confounding sensitivity, and direct age/sex interaction contrasts.

These are design and reporting characteristics. They do not demonstrate that no prior study has used similar data, features, or estimands.

## Close prior work and limits

Prior ECG literature includes MI/ACS classification and prediction, prognostic analyses of initial ECGs, and morphology-based MI outcome comparisons. MIMIC-IV-ECG now supports large-scale predictive modeling, including self-supervised waveform approaches. A 2026 MIMIC-IV study of structured ECG features and type 1 versus type 2 MI in ICU patients is a particularly close resource/feature neighbor, though its sample and target differ. A separate 2026 EHR causal-network diagnostic study also occupies related territory. These works make broad “first MIMIC-IV causal MI ECG analysis” language unsafe without a more exhaustive comparison.

The present analysis also cannot claim causal novelty: it does not establish event-before-ECG temporal ordering, does not exclude unmeasured confounding or selection, and is explicitly framed as an observational association study. DAG use and sensitivity analyses improve transparency but do not by themselves identify causal effects.

## Recommended wording

Use wording such as: “This study provides an admission-level observational characterization of adjusted associations between acute-MI coding and 95 handcrafted ECG features in an ECG-selected MIMIC-IV cohort, with prespecified analyses of selection, coding, and subgroup sensitivity.”

Avoid “first,” “novel,” “causal effect,” “MI-induced ECG changes,” and “universal MI ECG signature.” Any stronger novelty statement requires a documented, submission-ready search and direct comparison with close prior work, particularly reference 12.
