# Phase 8 Research Paper Preparation — Completion Report

## Status

The Phase 8 paper package has been strengthened and the aggregate-only Phase 9 demonstration is implemented. The manuscript remains a working draft, not a final journal submission. It follows the Phase 7 readiness decision: Gate 2 remains partially satisfied, and all findings are framed as observational associations. Phase 9 is limited to an aggregate research-results explorer; it is not a patient-facing or diagnostic application.

## Deliverables

- `PHASE8_MANUSCRIPT_DRAFT.md` — structured manuscript with the nine requested sections and all four analysis phases represented.
- `PHASE8_ABSTRACT.md` — structured abstract with key cohort and sensitivity results.
- `PHASE8_LITERATURE_REVIEW.md` — focused narrative literature comparison; not an exhaustive systematic review.
- `PHASE8_NOVELTY_ASSESSMENT.md` — modest/provisional positioning; no priority claim.
- `PHASE8_REFERENCES.bib` — DOI-linked bibliography for manuscript references.
- `PHASE8_CLAIM_TO_EVIDENCE_MAP.csv` — claims linked to finalized results and caveats.
- `PHASE8_CAUSAL_METHODOLOGY_AUDIT.md` and `PHASE8_PUBLICATION_COMPLIANCE_AUDIT.md` — methodology and STROBE-oriented reporting reviews.
- `PHASE8_REFERENCE_VERIFICATION_REPORT.md` — source-by-source metadata and citation-relevance audit; 17 checked, 11 bibliography entries corrected, none unresolved.
- `PHASE8_ADDITIONAL_ANALYSIS_RECOMMENDATIONS.md` — optional analyses assessed; none run pending user approval.
- `PHASE8_FIGURE_VERIFICATION_REPORT.md` — visual/caption review of all ten saved figures.
- `PHASE8_TABLES/` — 11 manuscript and supplement tables derived from finalized Phase 3–7 artifacts.
- `PHASE8_FIGURES/` — 10 figures and captions, including cohort, DAG, estimates, sensitivity, subgroup, and exploratory profile displays.
- `build_phase8_tables_figures.py` — reproducible formatting script; it reads saved results and fits no model or cohort.

## Scientific framing retained

The analysis has two admission-level layers and uses 95 handcrafted ECG features. The primary ECG cohort is ECG-selected, only 44.36% of the adult admission denominator. Selection weighting and broader coding retain the general ST/T pattern, but the broader definition attenuates it and other feature groups change. Modest Layer 1 E-values and direct feature-specific subgroup interactions are reported. The key limitation is that MI onset relative to the selected ECG is unknown. The results therefore do not establish MI-caused ECG changes, a universal MI signature, or literature-based novelty.

The revised abstract and manuscript explicitly describe diagnostic incorporation: ECG findings may contribute to MI diagnosis, so group differences may partly reflect the diagnostic process and not physiology following infarction alone. Numerical claims were reconciled against the manuscript, claim map, and saved Phase 3–7 results. No primary or sensitivity analysis results were changed.

## Phase 9 demonstration

`../phase9_demo/` contains a modular Streamlit application that reads saved aggregate Phase 8 result tables and existing figures. It reads no row-level MIMIC data, rebuilds no cohort, fits no model, and provides no individual predictions. The six sections cover the study overview, Layer 1, Layer 2, robustness, interpretation/limitations, and saved figures. Setup steps and scientific scope are in `../phase9_demo/README.md`; smoke and numeric validation are in `../PHASE9_DEMO_VALIDATION_REPORT.md`.

## Document format note

A DOCX was not produced. The available session did not provide a supported document-generation and render/visual-QA toolchain required to verify a DOCX layout. The complete editable Markdown manuscript and all supporting tables/figures are provided instead.

## Review items before submission

1. Complete and record a submission-ready literature search before making any novelty statement; the current review is focused and non-systematic.
2. Check exact software versions, data access/ethics statements, and journal-specific requirements against authoritative project records before submitting.
3. Keep onset-to-ECG timing and diagnostic incorporation prominent in the abstract, discussion, and conclusion.
4. Any additional sensitivity analysis requires explicit user approval; recommendations are documented separately and none has been run.
