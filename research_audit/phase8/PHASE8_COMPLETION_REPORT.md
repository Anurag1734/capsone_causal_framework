# Phase 8 Research Paper Preparation — Completion Report

## Status

The requested paper-preparation package is drafted. This is a working manuscript and supporting material, not a final journal submission. It follows the Phase 7 readiness decision: Gate 2 remains partially satisfied, and the paper is framed as an observational association study. No Phase 9 work has begun.

## Deliverables

- `PHASE8_MANUSCRIPT_DRAFT.md` — structured manuscript with the nine requested sections and all four analysis phases represented.
- `PHASE8_ABSTRACT.md` — structured abstract with key cohort and sensitivity results.
- `PHASE8_LITERATURE_REVIEW.md` — focused narrative literature comparison; not an exhaustive systematic review.
- `PHASE8_NOVELTY_ASSESSMENT.md` — modest/provisional positioning; no priority claim.
- `PHASE8_REFERENCES.bib` — DOI-linked bibliography for manuscript references.
- `PHASE8_CLAIM_TO_EVIDENCE_MAP.csv` — claims linked to finalized results and caveats.
- `PHASE8_TABLES/` — 11 manuscript and supplement tables derived from finalized Phase 3–7 artifacts.
- `PHASE8_FIGURES/` — 10 figures and captions, including cohort, DAG, estimates, sensitivity, subgroup, and exploratory profile displays.
- `build_phase8_tables_figures.py` — reproducible formatting script; it reads saved results and fits no model or cohort.

## Scientific framing retained

The analysis has two admission-level layers and uses 95 handcrafted ECG features. The primary ECG cohort is ECG-selected, only 44.36% of the adult admission denominator. Selection weighting and broader coding retain the general ST/T pattern, but the broader definition attenuates it and other feature groups change. Modest Layer 1 E-values and direct feature-specific subgroup interactions are reported. The key limitation is that MI onset relative to the selected ECG is unknown. The results therefore do not establish MI-caused ECG changes, a universal MI signature, or literature-based novelty.

## Document format note

A DOCX was not produced. The available session did not provide a supported document-generation and render/visual-QA toolchain required to verify a DOCX layout. The complete editable Markdown manuscript and all supporting tables/figures are provided instead.

## Review items before submission

1. Verify all bibliographic metadata, especially records marked for author/title confirmation in the literature review, against publisher or indexing records.
2. Complete and record a submission-ready literature search before making any novelty statement.
3. Check software/version and journal-specific methods details against the finalized Phase 5–7 run metadata before submitting.
4. Keep the onset-to-ECG timing limitation prominent in the abstract, discussion, and conclusion.
