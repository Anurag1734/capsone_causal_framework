# PHASE 2 — DATA FEASIBILITY AND TEMPORAL AUDIT

## Executive summary

The repository snapshot available in this workspace does not contain the required MIMIC-IV raw tables, the MIMIC-IV-ECG source files, or the modeling parquet artifacts needed to execute a numeric Phase 2 audit. The `data/raw` directory contains only archive stubs (`hosp.rar`, `icu.rar`) and there is no `data/modeling` tree with labels, embeddings, or master files. Because the underlying source tables are absent, the audit can only document the required checks and provide the analysis plan in a reproducible form.

## A. Clinical diagnosis timing

Required audit: validate whether diabetes, hypertension, CKD, and prior MI were recorded before the current admission using the longitudinal admission and diagnosis tables.

Current workspace status: not executable. The required longitudinal diagnosis tables are absent.

Strict prior-admission definition: a diagnosis must be documented with a timestamp or encounter date before the index admission start. A same-admission-only code is not treated as historical exposure.

Broader sensitivity definition: allow for a short pre-admission window or charted historical diagnosis from the same patient when the temporal ordering is sufficiently supported by the source records.

## B. Acute MI outcome validation

Required audit: validate ICD-9 410* and ICD-10 I21* / I22* while excluding 412 and I25.2; assess duplicate coding, transfer admissions, and disagreement with troponin-derived labels.

Current workspace status: not executable because the raw diagnosis tables are absent.

## C. ECG timing audit

Required audit: classify each ECG into before MI onset, after MI onset, or uncertain timing using admission context and event timestamps.

Current workspace status: not executable in the workspace because the waveform metadata, admission records, and MI event labels are absent.

## D. ECG feature audit

Required audit: group the 95 handcrafted features by physiologic domain and assess missingness, distributions, plausibility, and timing-specific availability.

Current workspace status: not executable because the feature tables are missing from `data/modeling`.

## E. Beta-VAE provenance audit

Required audit: confirm training checkpoint identity, cohort and split, use of acute MI ECGs in training, embedding extraction method, patient mapping, and variance diagnostics before allowing any causal use.

Current workspace status: not executable; no model/training artifacts exist in the workspace.

## F. ECG selection bias feasibility

Required audit: evaluate whether ECG acquisition can be modeled using measured variables and whether inverse-probability weighting is feasible.

Current workspace status: not executable; no admission-level cohort with ECG acquisition metadata is available.

## G. Dataset and split feasibility

Required audit: quantify patients, admissions, ECGs, MI-positive counts, and split characteristics while preserving patient-level separation.

Current workspace status: not executable because the modeling parquet and label files are absent.

## Final feasibility decision

Decision: C — Not currently feasible.

Reason: the repository snapshot does not include the raw MIMIC-IV, MIMIC-IV-ECG, or master-data artifacts required for a defensible causal audit, and the generated project documentation explicitly states that the final data pipeline outputs are not available in the workspace.

### What evidence supports this conclusion?
- `data/raw` contains only archive stubs and no extracted MIMIC tables.
- `data/modeling` is absent or incomplete.
- The repository contains the prior methodology documents but no actual phase outputs or datasets to audit.
- No validated MI diagnosis or ECG-timing dataset can be reconciled without those data sources.

### What remains uncertain?
- Exact MI-positive/negative counts in the underlying MIMIC cohort.
- ECG-level timing relative to MI onset.
- Whether beta-VAE embeddings are causal-eligible.
- Amount of selection bias associated with ECG acquisition.

### Which analyses must be excluded?
- Primary Layer 2 causal analysis using post-onset ECGs.
- Any causal role for VAE latent dimensions.
- Any use of post-onset ECGs as if they were interchangeable with validated pre-onset or same-admission controls.

### Which variables and cohorts can be used?
- None in the current workspace because the required raw and modeling data are absent.

### Recommendation

Do not estimate causal effects in this workspace. First restore or provide access to the required source datasets and modeling outputs, then rerun the audit pipeline in the `research_audit` directory before attempting final effect estimation.
