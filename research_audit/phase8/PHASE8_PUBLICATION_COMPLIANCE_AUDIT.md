# Phase 8 Publication and Reporting Compliance Audit

**Status:** reporting audit against the available manuscript and saved Phase 3–7 artifacts. This is not a claim of causal validity, journal acceptance, or full STROBE compliance. STROBE is used as a reporting checklist for observational studies.

## Reporting checklist summary

| Area | Assessment | Remaining action / limitation |
|---|---|---|
| Abstract and results | The cohort and central estimates match the Phase 8 tables and Phase 5–7 summaries. | Continue to identify the 67/95 BH findings as 66 physiological plus one technical/support measure. |
| Effect measure | Layer 1 results are risk differences; Layer 2 is raw mean difference and standardized mean difference in feature SD units. | State the scale in every figure/table caption; no risk ratio or clinical importance interpretation is implied. |
| Uncertainty and multiplicity | Patient-cluster bootstrap CIs; patient-cluster influence-score Wald p-values; BH for 95 feature tests; Holm for seven physiological group tests. | CI and p-value procedures differ. Report the method for each, and call BH results FDR-adjusted discoveries rather than independent confirmations. |
| Cohort and participant flow | Adult denominator 431,231; ECG-eligible 191,275 (44.36%) / 99,214 patients; primary Layer 2 167,066 admissions / 93,946 patients. History-only admissions are excluded from clean controls. | Figure 1 and Table 1 are the flow references. The draft gives definitions and exclusions, but journal-specific flow format may still be needed. |
| Study design and setting | Retrospective EHR analysis using MIMIC-IV and MIMIC-IV-ECG; admission is the unit, patient is the clustering/grouping unit. | Verify exact data release, access/ethics wording and software versions from project records before submission. |
| Methods and reproducibility | Adjustment sets, cross-fitting, seeds, folds, clipping, bootstrap count, and multiplicity methods are documented across source reports. | Bootstrap holds nuisance predictions fixed; make this conditional uncertainty explicit. Software package versions should be populated from the runtime/environment used for Phase 5–7. |
| Missing data | Phase 5 reports zero missingness for selected analytic feature/covariate values; no imputation was used. | This does not imply complete measurement for admissions without an ECG. |
| Selection and generalizability | 44.36% ECG availability and measured-only selection weighting are reported. | Unmeasured severity, symptoms, clinician ordering and care pathways can drive selection; target is not all admissions without transport assumptions. |
| Confounding and timing | Residual confounding and unknown MI-onset-to-ECG timing are explicit. | Diagnosis/admission labels do not establish MI before ECG. E-values are approximate and modest; Layer 2 tipping analysis is limited. |
| Diagnostic incorporation | Added explicitly to abstract and manuscript: ECG findings may contribute to MI diagnosis, so differences may partly reflect diagnosis assignment/documentation. | Magnitude cannot be estimated from available saved outputs. |
| Correlated outcomes | Dependence checks and manuscript note show 95 features are not independent replications. | Emphasize effect magnitudes and group patterns before significance counts. |
| Exploratory and sensitivity work | Primary, selection-weighted, broader-code, subgroup, confounding sensitivity, and exploratory profile results are distinguished. | Phase 6 profile predictions lack profile-specific intervals; β-VAE embeddings remain excluded due to unresolved checkpoint/training/extraction provenance. |
| Tables and figures | Captions define cohorts, scales, significance families, sensitivity comparisons, and exploratory profiles. | Visual review is recorded in the companion figure verification section of the overall completion report; figure binaries remain generated artifacts. |
| References | All 17 numbered records were checked against publisher, PubMed, or resource-index records. Eleven BibTeX entries were corrected; the complete verification table is in `PHASE8_REFERENCE_VERIFICATION_REPORT.md`. | Apply target-journal style at submission and refresh the focused literature search before making any novelty claim. |

## Numerical consistency check

The abstract numbers were cross-checked against `PHASE8_MANUSCRIPT_DRAFT.md`, `PHASE8_CLAIM_TO_EVIDENCE_MAP.csv`, Phase 8 tables, and the Phase 5–7 result CSVs:

- Cohort: 431,231 adult admissions; 191,275 ECG eligible (44.36%); 99,214 patients; 7,353 acute-code admissions; 24,209 prior-only admissions; 159,713 clean controls; primary Layer 2 167,066 admissions / 93,946 patients.
- Layer 1: diabetes +0.69 percentage points (95% CI +0.42 to +0.95); hypertension −0.51 (−0.70 to −0.30); CKD −0.17 (−0.59 to +0.31); prior MI +5.48, descriptive.
- Layer 2: 67/95 BH findings, comprising 66 physiological and one technical/support feature; leading standardized contrasts and ST/T means match Table 3 and Table 5.
- Sensitivities: selection direction agreement 89/95, median shift 0.009 SD, 66/67 primary findings retained; broad-code direction agreement 85/95 and ST/T means 0.126/0.108 SD; direct interaction findings 11 age and 13 sex contrasts.
- Approximate E-values and unknown timing are consistent with Phase 7. The selected-covariate weighting target is explicitly qualified; it does not correct unmeasured selection.

No discrepancy requiring a numerical result change was found in the abstract claims reviewed. The manuscript/abstract text was strengthened without changing estimates.

## Reference and citation issues found

The literature review has 17 numbered references and the manuscript's numeric citations map to those numbers. Incorrect/incomplete records were corrected, including the wrong journal for reference 4, the incorrect first author/journal metadata for reference 5, the dataset-vs-journal classification for reference 7, and titles/authors for references 2, 3, 9, 10, 15, and 16. Metadata and claim relevance are listed source by source in `PHASE8_REFERENCE_VERIFICATION_REPORT.md`. The focused review remains narrative rather than systematic and does not support a priority claim.

The manuscript's clinical statement that ECG contributes to diagnosis is supported in principle by its clinical-definition citations, but this creates a diagnostic-incorporation limitation for this analysis; it is now stated. Do not use prediction/classification citations as evidence that the observational estimand is valid.

## STROBE scope

The manuscript reports design, setting/data sources, eligibility, variables, data sources/measurement, bias, study size, quantitative methods, participant flow, descriptive cohort data, outcome estimates with precision, limitations, interpretation, and generalizability. Remaining submission work includes completing journal-specific data access/ethics and software-version statements from authoritative project records, ensuring the full STROBE checklist is mapped item by item in the submission supplement, and completing reference verification. STROBE improves reporting completeness; it does not establish exchangeability, temporal ordering, absence of selection bias, or causal validity.
