# MI–ECG Research Results Explorer

A small Streamlit application for presenting the completed two-layer observational analysis using saved aggregate Phase 8 tables and figures.

## Run locally

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r research_audit/phase9_demo/requirements.txt
python -m streamlit run research_audit/phase9_demo/app.py
```

The app opens in a browser. It reads the checked-in aggregate tables under `research_audit/phase8/PHASE8_TABLES/` and, when available, displays the existing Phase 8 PNG figures from `research_audit/phase8/PHASE8_FIGURES/`.

## Sections

- **Study overview:** denominator, selection, primary cohort, design and feature-group summary.
- **Layer 1:** risk differences and patient-cluster bootstrap confidence intervals.
- **Layer 2:** interactive forest plot and searchable/filterable display of 95 standardized feature differences, confidence intervals and BH q-values.
- **Robustness:** measured-covariate selection weighting, broader same-admission coding, direct subgroup interactions and unmeasured-confounding sensitivity.
- **Interpretation & limits:** temporal ordering, diagnostic incorporation, confounding, selection, feature dependence and β-VAE provenance.
- **Saved figures:** view the existing aggregate Phase 8 graphics.

## Data and scientific boundaries

The application reads only the saved aggregate CSV tables and PNG figures. It does not open MIMIC source tables, row-level admissions, waveforms or patient identifiers. It reconstructs no cohort, fits no statistical model, trains no ML model, and provides no patient-level prediction or diagnostic functionality. All displayed estimates retain their saved study definitions and are described as observational associations. Unknown MI-onset-to-ECG timing remains central; ECG evidence may contribute to MI diagnosis, creating diagnostic incorporation.

The plotted Layer 2 confidence intervals are converted from the saved feature units to feature SD units using the saved primary-cohort SD. Significance is based on the saved BH q-value family of 95 tests. The 95 outcomes are correlated and should not be interpreted as independent replications. `QRS_Dur_Global_count` is identified as a technical/support feature.

## Validation

Run the aggregate-data and chart consistency checks from the repository root:

```powershell
python research_audit/phase9_demo/validate_demo.py
```

The validator checks the saved table schema, cohort sizes, key effect sizes, and chart construction. It does not recompute estimates.
