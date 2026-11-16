# Phase 9 Demo Validation Report

**Application:** `phase9_demo/app.py` (Streamlit aggregate-results explorer)

## Checks performed

- Loaded the ten required saved aggregate result tables from `research_audit/phase8/PHASE8_TABLES/` and validated required columns.
- Confirmed exactly 95 unique Layer 2 features, four Layer 1 rows, and the saved primary cohort counts of 167,066 admissions and 93,946 patients.
- Checked headline Layer 1 results against the saved data: diabetes +0.69 percentage points; hypertension −0.51 percentage points.
- Checked primary significance counts: 67/95 BH findings, of which 66 are physiological and one is technical/support; confirmed one non-physiological technical/support feature.
- Checked 24 direct BH-significant subgroup interactions (11 age and 13 sex) and generated all interactive chart objects, including primary/weighted and primary/broad comparisons.
- Executed all six Streamlit sections using Streamlit `AppTest`: Study overview, Layer 1, Layer 2, Robustness, Interpretation & limits, Saved figures. Each rendered with zero application exceptions.
- Started the headless Streamlit server and confirmed the local application endpoint returned HTTP 200.
- Visually inspected a contact sheet of all ten saved Phase 8 figures and individually inspected the all-feature forest figure. See `phase8/PHASE8_FIGURE_VERIFICATION_REPORT.md`.

## Data boundary and methods

The loader points only to saved aggregate CSV tables. The UI does not load row-level MIMIC records, patient identifiers, waveform files, or source clinical tables. No cohort was reconstructed, no estimator or ML model was run, and no patient-level prediction feature exists. Figures are read from the existing Phase 8 figure directory when available.

## Result

**PASS for local demonstration.** The app runs and its tested headline values match finalized aggregate outputs. The project still needs an external academic review of interpretation, software/version and journal-specific reporting details before manuscript submission. The app is an academic research-results display, not a clinical diagnostic product.
