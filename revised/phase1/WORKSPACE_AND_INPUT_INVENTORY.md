# Revised Phase 1 — Workspace and Input Inventory

**Purpose:** establish the implementation workspace and identify source inputs for study design of *Modifiable Cardiovascular Risk Factors, Heterogeneous Causal Effects and Counterfactual ECG Modelling*.

**Scope:** inventory only. No effect estimation, model fitting, training, prediction, or Phase 2 work was performed. All additions for this task are confined to `revised/phase1/`.

## 1. Verified repository structure

The checked-out repository is `C:\Capstone\capsone_causal_framework` (Git worktree present). Top-level directories are `1.preprocessing/`, `2.analysis_and_validation/`, `cuda_env/`, `data/`, `docs/`, `models/`, `notebooks/`, `reports/`, `research_audit/`, `scripts/`, `src/`, and `tests/`, plus root documentation, dependency files, and scripts. The requested `revised/phase1/` directory was created for this document.

Existing audit materials are organized in `research_audit/`, with phase 5–9 outputs under their respective subdirectories. Existing raw inputs are under `data/raw/`. The raw folder currently contains the six compressed archives listed below; no extracted subdirectories or Parquet files are present there.

## 2. Reusable existing components

- `research_audit/PHASE1_CAUSAL_ESTIMANDS.md`, `PHASE3_STUDY_COHORT_DEFINITION.md`, `PHASE3_VARIABLE_DICTIONARY.csv`, and `PHASE4_FINAL_CAUSAL_GRAPH.md` document the original causal estimands, cohort, variables, and assumed graph. They are useful background only; their MI–ECG design is superseded for this extension.
- `research_audit/PHASE4_ADJUSTMENT_SETS.csv` records original adjustment sets; it is not an approved adjustment set for the revised SBP study.
- `research_audit/EXISTING_DATASET_INVENTORY.md` reports prior Parquet schemas, row counts, and data quality checks. It is a historical inventory, not verification that those extracted files currently exist in this checkout.
- `research_audit/ACUTE_MI_OUTCOME_AUDIT.csv` and related documentation describe explicit acute and historical MI coding. Continue to use the coding definitions below and rebuild/check flags from diagnosis-code fields rather than treating the old `is_mi_code` derivative as acute-only.
- `src/features/extract_comorbidities.py` and `src/features/fix_temporal_features.py` illustrate diagnosis and longitudinal feature processing, but contain legacy path assumptions and are not ready to run unchanged. `scripts/extract_cohort.py` and the master dataset builder are also legacy pipeline references, not revised study implementations.
- `data/raw/longitudinal.rar` contains prior longitudinal Parquet derivatives (member names listed in §5); `data/raw/master.rar` contains three ECG master splits. `data/raw/omr.rar` supplies outpatient measurement records.

No existing component was executed or modified. The existing Streamlit demo and prior AIPW outputs concern the original study and are not evidence for the revised intervention effect.

## 3. Existing files to preserve untouched

All original repository files and outputs outside `revised/phase1/` remain untouched. In particular, preserve the original `research_audit/` phase 1–9 records and outputs, all prior causal/ECG scripts and documentation, the Streamlit demo, source data archives, and original model/master files. Do not overwrite prior reports with the reconciled revised-cohort findings. The root `.gitignore` was inspected but not changed.

## 4. Local paths and access status

- Repository: `C:\Capstone\capsone_causal_framework` — accessible.
- Raw archive directory: `C:\Capstone\capsone_causal_framework\data\raw` — accessible and contains exactly `hosp.rar`, `icu.rar`, `longitudinal.rar`, `master.rar`, `omr.rar`, and `labevents.rar`.
- Extracted/processed Parquet data: none found in the current local repository tree. In particular, the prior inventory's paths `data/raw/longitudinal/` and `data/raw/master_dataset/` do not currently exist as extracted directories.
- Other `C:\` directories were not recursively searched; the local raw-data folder is the repository's `data/raw/` directory as supplied. No external data path was assumed.
- The root `.gitignore` excludes `data/`, `dataset/`, `datasets/`, and `*.rar`, and thus protects the current raw-data location and archive types from ordinary Git tracking. It also excludes common waveform and model-weight formats. Keep any future row-level derivatives outside the new research-output folder and locally protected.

## 5. Archives: format, size, member listing, integrity status

Each archive's first eight bytes were read locally and are `52 61 72 21 1a 07 01 00` (`Rar!` RAR 5 signature). Sizes below are exact filesystem byte sizes. Windows `tar -tf` successfully listed each archive without extracting members. This verifies that the member directory is readable; no full CRC/data integrity test was available, so archive integrity beyond listing remains **untested**.

| Archive | Size (bytes) | Format/header | Listed members | Listing / integrity status |
|---|---:|---|---|---|
| `hosp.rar` | 762,388,455 | RAR 5 | `emar.csv`, `omr.csv`, `patients.csv`, `prescriptions.csv`, `admissions.csv` | Member listing succeeded; full integrity test unavailable |
| `icu.rar` | 1,651,036,480 | RAR 5 | `d_items.csv`, `inputevents.csv`, `procedureevents.csv`, `chartevents.csv` | Member listing succeeded; full integrity test unavailable |
| `longitudinal.rar` | 46,365,688 | RAR 5 | `longitudinal/admissions_chronology.parquet`, `diagnoses_all.parquet`, `diagnoses_mi_codes.parquet`, `d_labitems.parquet`, `lab_coverage_catalogue.parquet`, `mi_admissions.parquet`, `observation_end.parquet`, `omr_coverage_catalogue.parquet`, `patients_demographics.parquet`, `phase1_stats.json`, `phase2_stats.json`, `vitals_coverage_catalogue.parquet`, and directory entry `longitudinal` | Member listing succeeded; full integrity test unavailable |
| `master.rar` | 395,317,259 | RAR 5 | `master/test.parquet`, `master/train.parquet`, `master/validation.parquet`, and directory entry `master` | Member listing succeeded; full integrity test unavailable |
| `omr.rar` | 33,153,968 | RAR 5 | `omr.csv` | Member listing succeeded; full integrity test unavailable |
| `labevents.rar` | 1,423,986,067 | RAR 5 | `labevents.csv` | Member listing succeeded; full integrity test unavailable |

`tar -tf` is the only available archive listing tool detected; no `7z`, `7za`, `7zz`, `UnRAR`, or `rar` command was found in PATH or at common 7-Zip/WinRAR install locations. No archive was extracted or modified. The earlier inventory report's claims about streamed `labevents.csv` are historical report content and were not re-executed in this task.

## 6. Python libraries and existing processed-data evidence

Local interpreter: Python 3.12.6. Import availability checks returned:

| Package | Available | Relevance |
|---|---|---|
| `rarfile` | No | Cannot use the Python RAR wrapper here |
| `duckdb` | No | Not available for direct analytical reads |
| `pyarrow` | Yes | Parquet reader support is present; no extracted Parquet source was found to read |
| `pandas` | Yes | Tabular processing support is present |
| `fastparquet` | No | Alternative Parquet engine absent |

The prior `research_audit/EXISTING_DATASET_INVENTORY.md` reports that an earlier workspace had 10 longitudinal Parquet derivatives and three master Parquets. It includes schemas, counts, and quality summaries (for example, admissions chronology, diagnosis-code records, demographics, observation-end/death summaries, OMR coverage catalogue, and master splits). Those files are **not present as extracted data now**, so the report is useful schema/planning evidence, not a current local data verification. No extracted CSV or Parquet was found under the repository's current `data/raw/` tree.

The root `requirements.txt` lists pinned DuckDB and PyArrow versions, but that declaration is not proof they are installed; current environment checks above govern. Do not run the legacy cohort or audit scripts blindly: existing code and docs contain hard-coded Windows paths from an older installation.

## 7. Data required for revised Phase 1

Phase 1 is study design and should rely on the authoritative reconciled aggregate findings in the task instructions; it does not require row-level data, model fitting, or outcome estimation. For a later, approved implementation of the population cohort and its design diagnostics, the likely source tables are:

| Design need | Required source |
|---|---|
| Admission timelines, patient linkage, index candidates, censoring/follow-up candidates | `admissions.csv` from `hosp.rar`; alternatively `admissions_chronology.parquet` from `longitudinal.rar` |
| Acute and historical MI codes and event admission dates | Diagnosis-code source (`diagnoses_icd.csv` if separately available) or `diagnoses_all.parquet` from `longitudinal.rar`; use explicit code patterns |
| Patient demographics and death-date fields (with incomplete ascertainment caveat) | `patients.csv` from `hosp.rar` and/or `patients_demographics.parquet` plus `observation_end.parquet` from `longitudinal.rar` |
| BP measurements and date-precision temporal ordering | `omr.csv` from `omr.rar` or `hosp.rar`; confirm which copy/schema is authoritative and whether copies are identical before use |
| BP/name coverage metadata | `omr_coverage_catalogue.parquet` from `longitudinal.rar` (aggregate summary only; not row-level measurements) |
| Candidate diabetes, hypertension, CKD, and historical MI covariates | Diagnosis-code fields from the longitudinal diagnosis derivative or source diagnoses, with explicit look-back/time rules |
| BMI, weight, height (optional candidates) | `omr.csv`; only after validating measurement names, units, dates, duplicates, and pre-index availability |

The ICU archive and `labevents.csv` are not needed to define this primary BP-to-incident-MI design based on the stated sources. ECG master Parquets are not part of the primary BP-to-MI denominator; the separate BP-to-ECG module must retain its own eligibility definition. Medication records may be useful for explicitly scoped sensitivity/design assessment, but outpatient ascertainment is incomplete and should not be treated as complete baseline medication history. Smoking and sufficiently complete LDL/HDL are unavailable in processed data; do not invent them or code absent history as observed. β-VAE work is explicitly out of scope.

## 8. Authoritative revised cohort and coding notes

Use the reconciled counts supplied for this task, not conflicting older reports: 9,703 unique patients with acute-MI-coded admissions; common-index cohort 168,915; 3,207 incident acute-MI admissions after index; 165,708 without recorded acute MI before censoring; 54,565 eligible with any valid pre-index OMR BP; 53,956 with valid BP in the two-year pre-index window; corresponding BP-available incident cases 1,229 and 1,223. The earlier 5,008 and 4,797 event-anchored counts are not the common-baseline incident-case counts.

Acute event code patterns: ICD-9 `410*`, ICD-10 `I21*` and `I22*`. Historical MI: ICD-9 `412`, ICD-10 `I25.2`. Exclude documented acute MI admissions before or on the index date. For cases, candidate index is the earliest non-acute-MI admission before first acute-MI admission; controls use the earliest admission under the same baseline and history exclusions without conditioning on never having future MI. Controls with later MI become cases at event time. Admission date is an event proxy, not biological onset.

Candidate BP rule: valid parsed SBP 60–260 mmHg, DBP 20–160 mmHg, and SBP > DBP. OMR `chartdate` has date precision; BP must be strictly before the index calendar date. Candidate look-back is 730 days and candidate summary is mean SBP, subject to final specification. Illustrative intervention is a 10 mmHg reduction among baseline SBP ≥130 mmHg; Phase 1 must still specify its support/boundary and comparison condition. Conditional positivity is not established by marginal bins or min–max checks.

Follow-up, censoring, death handling, selection into outpatient BP measurement, subgroup precision targets, and medication limitations require explicit design decisions. Missing death date is not proof of survival. No conditional-overlap or CATE precision conclusion should be inferred from event counts alone.

## 9. BP-to-ECG module separation

The supplied Phase 0 module counts (52,267 non-MI patients with both OMR BP and ECG; 38,987 with BP-before-ECG ordering) describe a distinct eligibility set. Do not merge those denominators with the incident-MI cohort. This task did not inspect ECG archive contents or analyze any ECG rows.

## 10. Safest and most efficient next access method

For study design, use this inventory and the supplied aggregate reconciliation; no extraction is needed. When a later authorized data-processing task requires row-level inputs, use `tar -tf` to identify exact member paths, then extract only the required member(s) into a local temporary/work area outside Git-tracked outputs. Prefer an available RAR-aware backend (for example, 7-Zip/UnRAR or a configured libarchive tool) for targeted extraction, and run the tool's archive test before relying on data integrity. Do not assume DuckDB reads RAR. Do not assume `rarfile` can decompress without a backend. For very large `labevents.csv`, avoid full extraction unless a later analysis explicitly requires it; the primary BP–MI design does not require it. Read Parquet derivatives with `pyarrow`/`pandas` after targeted extraction, and keep row-level data local and out of `revised/phase1/`.

## 11. Blockers and compliance

- No extracted source tables are present locally, so current Parquet schemas could not be independently re-read in this task.
- Archive member names and RAR 5 signatures are verified; full archive integrity/CRC tests are not available with detected tools.
- `rarfile`, DuckDB, 7-Zip, and UnRAR are unavailable. `tar` lists members but a complete archive integrity test was not established.
- Diagnosis source is available as a member of the longitudinal archive, not as an individually listed `hosp.rar` member. Use the diagnosis Parquet or acquire/use an explicitly approved diagnosis source; do not infer its presence in `hosp.rar`.
- Current `.gitignore` adequately excludes `data/` and `.rar`; no change was required. Keep aggregate protocol documents only in the revised output and never write identifiers, row-level records, patient BP values, predictions, or ECG waveforms there.
- Legacy scripts contain hard-coded old paths and must be adapted only in new revised files after checking actual local paths. No path permission error occurred for inspected repository files; no external raw-data directory was independently verified.

