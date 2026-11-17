# Phase 2 — Workspace and Input Inventory

**Task:** Phase 2 setup inventory only. No Phase 2.0 decisions were closed, no cohort was built, no outcome/effect model was fit, and no treatment effect was estimated. This document and any future Phase 2 deliverables belong under `revised/phase2/`; row-level data must remain outside this deliverables folder.

## 1. Workspace and Phase 1 handoff

Repository checkout: `C:\Capstone\capsone_causal_framework`. The Phase 1 package exists in `revised/phase1/` with the eight requested protocol documents plus `WORKSPACE_AND_INPUT_INVENTORY.md`. The revised protocol specifies:

- Target population: MIMIC-IV patients entering the observable hospital cohort and satisfying common index and BP eligibility; not the general population.
- Common index: earliest eligible non-acute-MI admission for cases and controls under the same rules. Exclude documented acute or historical MI on/before index; do not select controls by future MI-free status.
- Outcome: first acute-MI-coded admission strictly after index; ICD-9 `410*`, ICD-10 `I21*`/`I22*`. Historical documentation is ICD-9 `412`, ICD-10 `I25.2`.
- Baseline OMR BP: parse both values from `SBP/DBP`; SBP 60–260, DBP 20–160, SBP>DBP, and `chartdate < index_date`; candidate window `[index_date - 730 days, index_date)` and arithmetic mean SBP.
- Policy: reference `d0(A)=A`; modified `d1(A)=A-10 I(A>=130)`. This changes the measured baseline summary hypothetically; it is not a prescription, sustained reduction, or supported value for every profile.
- Estimand: fixed-horizon cumulative-incidence contrast (risk difference primary candidate), with death competing when ascertainment permits.

The Phase 1 decision register is not a closed, executable Phase 2 specification. Research-team feedback explicitly requires Phase 2.0 to close, before primary cohort construction: minimum BP measurement count; horizon; death/censoring and operational observation end; prior-MI exclusion/adjustment consistency; covariate timing and diagnosis look-back; conditional positivity/support; subgroup precision; final estimator; and uncertainty/multiplicity procedures. The Phase 1 recommendations (including 365 days and g-computation) must not be represented as approved merely because they appear in a draft. Phase 2.0 should record approvals and exact operational definitions; the treatment shift itself is authoritative and must not be changed if support is limited.

### Authoritative aggregate reconciliation for planning

Use the research-team counts, not older event-anchored counts: 9,703 patients with acute-MI-coded admissions; common-index cohort 168,915; 3,207 incident first acute-MI cases; 165,708 with no acute MI recorded before censoring; 54,565 with any valid pre-index BP; 53,956 with a valid BP in the two-year window; 1,229 / 1,223 corresponding incident cases with any pre-index BP / two-year BP. The two-year BP-case subgroup counts are age <65 375, age ≥65 848, male 651, female 572, documented diabetes 503, and no documented diabetes 720. These are aggregate reconciliation evidence, not guaranteed Phase 2 denominators or precision results. Never substitute 5,008 or 4,797.

## 2. Existing repository components and reuse assessment

| Component | What exists / reusable logic | Phase 2 caution |
|---|---|---|
| `research_audit/phase1_2_audit_runner.py` | `classify_diagnosis_codes()` separates acute ICD-9 `410*`, acute ICD-10 `I21*`/`I22*`, historical `412`/`I25.2`, and diabetes/HTN/CKD code flags. `admission_diagnosis_audit()` links to admissions and computes earlier-admission history. Uses paths relative to repository root. | Useful as a coding reference, not a finished Phase 2 cohort builder. Prior flags mean earlier recorded admissions, not the new pre-exposure-window look-back. Audit runner also expects extracted source Parquets and lab audit artifacts absent locally. Do not use old MI derivatives as acute-only labels.
| `research_audit/ACUTE_MI_OUTCOME_AUDIT.csv`, `PHASE1_2_COMPLETION_REPORT.md`, `DATASET_READINESS_REPORT.md`, `FINAL_EVENT_TIME_FEASIBILITY.md` | Existing aggregate diagnosis/timing audit outputs and caveats. | Original MI–ECG/troponin conclusions are not estimates or evidence for the new SBP intervention. The Phase 1 diagnosis audit is historical evidence; reproduce only when needed under approved paths/rules.
| `research_audit/EXISTING_DATASET_INVENTORY.md` | Reports schemas, keys, row counts and quality summaries for a prior extracted Parquet workspace. | Historical report only: extracted files are absent in this checkout. Do not claim live Parquet verification based on this report.
| `research_audit/phase2b_troponin_audit.py` | Root-relative paths and careful interval candidate linkage without assigning ambiguous missing admission IDs. | Troponin is not required for ICD-defined primary outcome; do not run it for Phase 2 SBP.
| `research_audit/build_phase3_observational_dataset.py` | Repository-relative roots, PyArrow schema inspection, patient/admission linkage, diagnosis audit merge, 95-feature selection and validation patterns. | Original ECG analysis; reads extracted master/longitudinal Parquets and writes under `data/analysis/observational_mi_ecg/`. It must not be run or modified for the revised cohort.
| `src/features/extract_comorbidities.py` | Illustrates chunked diagnosis reads and temporal joins. | Hard-coded `C:\Users\Acer\Desktop\...` paths; prior-MI coding is not acceptable for the revised definitions (it includes ICD-9 410/412 and ICD-10 I21/I22 but omits historical I25.2); loops by cohort row and uses earlier admission time rather than approved pre-window cutoff. Do not reuse unchanged.
| `scripts/extract_cohort.py` | Legacy DuckDB cohort SQL and OMR BP query; demonstrates parsing with `SPLIT_PART(result_value,'/',1/2)`. | Hard-coded old data tree; selects `arg_max` (latest BP pair), uses an inclusive `BETWEEN ... anchor_time`, and has no revised QC/count/730-day policy. Not reusable as the exposure builder.
| `src/features/fix_temporal_features.py` | Chunked CSV patterns and subject/admission matching for labs/vitals. | Hard-coded paths; unrelated large tables; not needed for primary BP-to-MI design.
| `tests/test_phase1_2_audit.py` | Existing unit tests cover acute vs historical codes, earlier-admission MI flags, threshold unit/year logic, timing categories, and ambiguous interval linkage. | Tests concern original Phase 0 audit functions, not revised BP parsing/index/intervention/estimand. They were inspected, not run in this inventory task.
| `requirements.txt` | Declares pinned pandas, PyArrow and DuckDB versions among many project dependencies. | Declaration is not proof of installation. Actual current package availability is in §6.

The original generic binary-treatment AIPW/MI–ECG infrastructure is not the primary estimator for a continuous deterministic SBP policy with competing risks and censoring. The Phase 1 recommended future candidate is g-computation, subject to the team closing estimator and event-process decisions. No estimator is implemented in this task.

## 3. Existing audit outputs

Relevant existing tracked research outputs include `research_audit/ACUTE_MI_OUTCOME_AUDIT.csv`, `PHASE1_2_COMPLETION_REPORT.md`, `PHASE2_DATA_FEASIBILITY_REPORT.md`, `DATASET_READINESS_REPORT.md`, `EXISTING_DATASET_INVENTORY.md`, `FINAL_EVENT_TIME_FEASIBILITY.md`, `EVENT_TIME_COVERAGE_REPORT.md`, `PHASE3_*`, and `PHASE4_*`. Phase 5–9 files contain original MI–ECG analyses and must remain untouched and must not be used as revised BP effect estimates.

Some scripts refer to generated row-level artifacts, including `ACUTE_MI_DIAGNOSIS_BY_ADMISSION.csv`, under `research_audit/`; the admission-level diagnosis CSV is gitignored and is not present in the current file listing. Existing aggregate reports can guide specifications but do not replace Phase 2 source validation.

## 4. Current source availability and schemas

### Current local state

The only files in `data/raw/` are the six archives listed in §5. No extracted `data/raw/longitudinal/`, `data/raw/master_dataset/`, OMR CSV, admissions CSV, diagnosis Parquet, or other source table was found. There is therefore no live row-level schema to inspect from extracted tables. The schemas below are from prior repository documentation/inventory and must be confirmed after a safe targeted extraction.

### Relevant documented schemas

| Source | Documented fields / keys | Phase 2 use and linkage |
|---|---|---|
| `hosp/admissions.csv` (inside `hosp.rar`) | Standard source fields include `subject_id`, `hadm_id`, `admittime`, `dischtime`, `deathtime`, `admission_type`, `admission_location`, `discharge_location`, `hospital_expire_flag`, `edregtime`, `edouttime`; confirm actual header. | Admission chronology and common index; `hadm_id` links diagnosis codes; `subject_id` links repeated admissions/patient records. |
| `hosp/patients.csv` (inside `hosp.rar`) | `subject_id`, `gender`, `anchor_age`, `anchor_year`, `anchor_year_group`, `dod` (documented in existing inventory). | Demographics and one patient-level DOD source; missing DOD is not survival. |
| `hosp/omr.csv` (inside `hosp.rar`, duplicated as `omr.csv` in `omr.rar`) | Repository `docs/raw_data_analysis.md` documents `subject_id`, `chartdate`, `seq_num`, `result_name`, `result_value`. Actual archive header was not retrieved in this task. | OMR has patient/date linkage rather than a verified admission foreign key in the documented schema. Link on `subject_id`, then enforce `chartdate < index_date`; parse `result_value` only for the BP result name. Determine which of the two archive copies is authoritative or verify content identity before choosing. |
| `longitudinal/diagnoses_all.parquet` (inside `longitudinal.rar`) | Prior inventory: `subject_id`, `hadm_id`, `icd_code`, `icd_version`, `seq_num`, `admittime`, `dischtime`, `is_mi_code`; 4,756,326 × 8 in prior extracted inventory. | Code-level source; link to admission and patient. Rebuild acute/historical flags from code/version, not `is_mi_code`. |
| `longitudinal/admissions_chronology.parquet` | Prior inventory: 20 fields including patient/admission keys, admit/discharge and ED dates, death fields, `admission_seq`, previous/next admission linkage, and `anchor_time`. Prior inventory reported `hadm_id` unique. | Useful chronology derivative if still reproducible and aligned with approved cohort rules. |
| `longitudinal/patients_demographics.parquet` | Prior inventory: `subject_id`, `gender`, `anchor_age`, `anchor_year`, `anchor_year_group`, `dod`. | Patient-level demographics derivative; validate against source `patients.csv`. |
| `longitudinal/observation_end.parquet` | Prior inventory: `subject_id`, `last_discharge`, `last_admittime`, `in_hospital_deathtime`, `dod`, `is_dead`, `observation_end`. | Candidate follow-up summary only; not proof of continuous observation or complete death ascertainment. |
| `longitudinal/omr_coverage_catalogue.parquet` | Aggregate catalogue with `result_name`, counts/patient coverage, and earliest/latest dates. | Coverage summary only, not BP rows or exposure construction. |
| `master/{train,validation,test}.parquet` (inside `master.rar`) | Prior inventory: each split 184 columns; keys `study_id`, `SubjectID`, `hadm_id`, ECG labels/times, 95 handcrafted ECG fields, 64 latent columns. | Not required for the primary SBP-to-MI cohort. Keep separate BP-to-ECG scope and do not merge its denominators. |

The prior inventory reports 431,231 admissions and 180,733 distinct patients for a previous extracted source universe. These historical counts are not a replacement for the newly reconciled 168,915 common-index population. Reconcile source versions and cohort rules when Phase 2.0 approves construction.

## 5. Local raw archive inventory

Current path: `C:\Capstone\capsone_causal_framework\data\raw`. Each first-eight-byte signature was verified as RAR 5 (`52 61 72 21 1a 07 01 00`). Windows `tar -tf` listed the members below without extraction. Listing success is not a CRC/full integrity test.

| Archive | Size (bytes) | Listed members | Phase 2 relevance |
|---|---:|---|---|
| `hosp.rar` | 762,388,455 | `emar.csv`, `omr.csv`, `patients.csv`, `prescriptions.csv`, `admissions.csv` | Required: OMR, patients, admissions. Prescriptions optional only under approved sensitivity; not proof of use. |
| `icu.rar` | 1,651,036,480 | `d_items.csv`, `inputevents.csv`, `procedureevents.csv`, `chartevents.csv` | Not required for primary outpatient BP / ICD MI cohort. Do not extract. |
| `longitudinal.rar` | 46,365,688 | `longitudinal/admissions_chronology.parquet`, `diagnoses_all.parquet`, `diagnoses_mi_codes.parquet`, `d_labitems.parquet`, `lab_coverage_catalogue.parquet`, `mi_admissions.parquet`, `observation_end.parquet`, `omr_coverage_catalogue.parquet`, `patients_demographics.parquet`, `phase1_stats.json`, `phase2_stats.json`, `vitals_coverage_catalogue.parquet`, directory entry `longitudinal` | Required/reusable candidates: diagnoses_all, admissions chronology, demographics/observation end, OMR coverage catalogue. Confirm source/version alignment. Do not use historical MI derivatives as acute-only labels. |
| `master.rar` | 395,317,259 | `master/test.parquet`, `master/train.parquet`, `master/validation.parquet`, directory entry `master` | Not required for primary SBP-to-MI analysis. Do not extract for Phase 2.0. |
| `omr.rar` | 33,153,968 | `omr.csv` | Duplicate OMR source candidate; compare with `hosp.rar` OMR before selection. |
| `labevents.rar` | 1,423,986,067 | `labevents.csv` | Not required for ICD-defined primary outcome or OMR exposure. Do not extract for this task. |

Available archive utility: Windows `tar.exe` at `C:\Windows\System32\tar.exe`. No `7z`, `7za`, `7zz`, `UnRAR`, `rar`, or `bsdtar` command was found in PATH/common install locations. RAR listing works, but no available RAR-aware integrity test was found. A limited `tar -xOf` attempt to stream only the OMR header did not return promptly; it was interrupted without saving an output file. No archive was modified and no table was extracted to disk during this task.

## 6. Dependencies, tests, and workflows

Python 3.12.6 is present. Current import checks: `pandas` available; `pyarrow` available; `pytest` available; `networkx` available; `duckdb` unavailable; Python `rarfile` unavailable. Root `requirements.txt` pins DuckDB and PyArrow, but package declarations do not mean installed packages. Installing packages or extraction tools is not part of this inventory task.

PyArrow can inspect/read Parquet after a member is made available locally, but it cannot directly address RAR members. Do not assume DuckDB reads RAR. `tar -tf` can list members but full RAR testing/extraction is unverified here. Existing code predominantly uses pandas/PyArrow for Parquet and pandas chunks for CSV; `scripts/extract_cohort.py` uses DuckDB SQL and `read_csv_auto` on uncompressed CSV paths.

Existing test file `tests/test_phase1_2_audit.py` covers MI code separation, prior-admission diagnosis flags, troponin threshold filters, event-time classification, and ambiguous interval linkage. It does not test revised OMR parsing, the 730-day window, minimum BP count, deterministic continuous SBP policy, competing-risk g-computation, censoring, selection, or patient-level cross-fitting. Tests were inspected but not run.

## 7. Patient-level linkage infrastructure

- Canonical patient key is `subject_id`; repeated admissions are joined by `(subject_id, hadm_id)` and ordered with `admittime` / `admission_seq`.
- Diagnosis rows in `diagnoses_all.parquet` link to admission chronology via `(subject_id, hadm_id)`; admission timestamps supply index-relative ordering.
- OMR documented schema has `subject_id` and date-only `chartdate`, but no `hadm_id`; link each patient's OMR records to their index date by `subject_id` and apply the strict date cutoff. Do not infer a specific admission for an OMR row.
- Patient-level death/demographic tables key on `subject_id`; admission chronology keys on `hadm_id`. Keep death units and universes separate.
- Existing master ECG splits use different column casing (`SubjectID`) and are not part of this primary cohort. Do not use their train/validation/test split as an analysis split for admissions.

## 8. Hard-coded path and implementation risks

- `src/features/extract_comorbidities.py` and `src/features/fix_temporal_features.py` contain fixed `C:\Users\Acer\Desktop\...` paths.
- `scripts/extract_cohort.py` embeds a legacy `RAW_DIR` layout and writes to old processed paths; its OMR logic takes a latest reading, not the approved mean/QC exposure.
- Phase 1 audit and Phase 3 builder use paths relative to repository root, but expect extracted `data/raw/longitudinal/` and/or `data/raw/master_dataset/` directories not present now.
- New Phase 2 scripts should use a config/CLI for repository root, archive path, source paths, local derived-data directory, and aggregate deliverable path; resolve defaults from script location, not a user's historical Windows home path. Never write row-level data under `revised/phase2/`.

## 9. Data governance

Root `.gitignore` excludes `data/`, `dataset/`, `datasets/`, `*.rar`, common waveform extensions, and serialized model weights. Keep row-level patient-linked intermediates in an appropriately permissioned local path under ignored `data/` (for example, `data/derived/revised_phase2/`) and verify `git check-ignore` before writing. Commit only code, protocol/config templates without secrets, and aggregate outputs under `revised/phase2/`. Do not place identifiers, OMR readings, patient-level predictions, ECG waveforms, or raw archive members in the deliverables folder. Preserve every original source archive and original Phase 1–9 artifact.

## 10. Proposed execution architecture (not executed)

1. **Phase 2.0 decision gate:** record researcher-approved count threshold, fixed horizon, event/death/censoring and operational observation-end rules, prior-MI exclusion, covariate time cutoff/look-back, primary g-computation specification, conditional-support diagnostics/restriction policy, subgroup precision target, and uncertainty/multiplicity plan. Freeze them in a versioned Phase 2 protocol/config before constructing a cohort. Support findings may identify an unsupported target subset; they do not authorize changing `d1(A)`.
2. **Input acquisition:** use a verified RAR-aware tool/backend; list and test archives; extract only approved member(s) to a temporary local directory or stream to a supported reader. Needed initial members are OMR and possibly patients/admissions CSV, plus longitudinal `diagnoses_all.parquet` and either chronology/observation Parquets or a source-derived equivalent. Compare the two OMR copies before selection. Avoid ICU, master, and labevents for this primary module.
3. **Raw-to-local staging:** keep immutable source archives; record source version, member, size, checksum, and schema. Stage source or derived row-level files only under ignored local data storage. Do not log patient rows or IDs.
4. **Phase 2.1 cohort/input construction (future task):** create configurable new code under `revised/phase2/src/`; explicitly classify diagnosis code/version; build common index; apply pre-window diagnosis rules and prior-MI exclusion; parse/QC OMR; create approved patient-level BP summaries and count; link outcome/follow-up/death. Emit row-level intermediate only to ignored local data path and aggregate QA tables only to `revised/phase2/`.
5. **Phase 2.2 diagnostics/estimation (future task after approvals):** first run aggregate support, observation, censoring, and precision diagnostics; then the approved continuous-policy competing-risk g-computation with patient-level uncertainty. Do not use original binary AIPW as the primary estimator. No modeling is part of this setup task.

## 11. Technical blockers and status

1. Extracted source tables are absent locally; source Parquet/CSV schemas can only be partially supported by historical repository documentation.
2. No RAR extraction/test backend (`7z`/UnRAR/rarfile) was detected. `tar -tf` lists all archives, but full CRC testing and prompt targeted OMR extraction were not verified. Resolve tooling before row-level processing.
3. DuckDB is declared but not installed. PyArrow and pandas are installed; DuckDB should be installed only if the approved implementation needs it, and it is not a RAR reader.
4. Duplicate `omr.csv` members exist in `hosp.rar` and `omr.rar`; the authoritative copy/content identity is not confirmed.
5. The Phase 1/team decisions listed in §1 remain open. Per instruction, they must be closed in Phase 2.0 before primary cohort construction; this inventory task does not close them.

**Task boundary:** workspace preparation and inspection only. No Phase 2 analysis or cohort construction has started.
