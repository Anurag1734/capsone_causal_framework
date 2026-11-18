# Phase 2 Canonical File Index

This index identifies the current authoritative Phase 2 documents, reproducibility scripts, and aggregate tables. Current decisions are governed by `PHASE2_GATE0_REMEDIATION_DECISION_REGISTER.md` and the evidence summarized in `PHASE2_GATE0_REMEDIATION_REPORT.md`. Earlier Phase 2.0 records remain as history and carry supersession notices. Gate 0 has **not passed**.

## Operational documents

| File | Role | Status |
|---|---|---|
| `PHASE2_GATE0_REMEDIATION_REPORT.md` | Current aggregate feasibility findings and gate reassessment | Current report; no cohort/causal estimation authorization |
| `PHASE2_GATE0_REMEDIATION_DECISION_REGISTER.md` | **Authoritative current decision register** | Current; approvals and blockers explicit |
| `PHASE2_FINAL_PROTOCOL.md` | Frozen research question, target, exposure policy and proposed estimation design | Design reference; read with current gate report |
| `PHASE2_COHORT_AND_EXPOSURE_SPECIFICATION.md` | Eligibility, index, outcome and BP measurement specification | Design reference; cohort construction remains gated |
| `PHASE2_ADJUSTMENT_SET_AND_COVARIATE_DICTIONARY.md` | Candidate covariate timing and coding | Current limitation: pre-window disease documentation absent |
| `PHASE2_FOLLOWUP_AND_COMPETING_RISK_SPECIFICATION.md` | Follow-up, death and censoring assumptions | Current limitation: observation/death processes unresolved |
| `PHASE2_ESTIMATION_SPECIFICATION.md` | Candidate future estimator and uncertainty methods | Future design only; no estimator fitted |
| `PHASE2_GATE_CRITERIA.md` | Sequential gates and current statuses | Updated to reflect remediation; Gate 0 failed |
| `PHASE2_WORKSPACE_AND_INPUT_INVENTORY.md` | Local source/archive and governance inventory | Initial snapshot plus current audited addendum (§12) |
| `PHASE2_BP_THRESHOLD_FEASIBILITY.md` | BP-count aggregate evidence | Current; ≥2 is a recommendation requiring approval |
| `PHASE2_FOLLOWUP_FEASIBILITY.md` | Horizon and observation evidence | Current; no horizon establishes complete follow-up |
| `PHASE2_DEATH_AND_CENSORING_RECONCILIATION.md` | Death source and linkage evidence | Current; death completeness inadequate |
| `PHASE2_CONDITIONAL_POSITIVITY_FEASIBILITY.md` | Outcome-free support diagnostics | Current; full positivity not assessable |
| `PHASE2_SUBGROUP_PRECISION_ASSESSMENT.md` | Descriptive subgroup and scenario precision evidence | Current; causal precision not established |
| `PHASE2_DECISION_CLOSURE_REPORT.md` | Original Phase 2.0 closure snapshot | Historical; superseded feasibility statements retained for audit |
| `PHASE2_DECISION_REGISTER.md` | Original Phase 2.0 decision register | Historical; current register supersedes it |
| `PHASE2_WORKSPACE_AUDIT_AND_CLEANUP_REPORT.md` | This cleanup, privacy and validation audit | Current audit record |

## Reproducibility scripts

| File | Purpose | Output |
|---|---|---|
| `scripts/phase2_0r_aggregate_feasibility.py` | Transient aggregate-only common-index, BP, follow-up, support and subgroup calculations | Source aggregate tables in `aggregates/`; no patient-level file |
| `scripts/phase2_0_death_source_reconciliation.py` | Source-wide death-source reconciliation | `aggregates/death_source_reconciliation.csv` |
| `scripts/phase2_0_compare_omr_archives.py` | Streams and hashes the two OMR archive members | `aggregates/omr_archive_comparison.csv` |
| `scripts/publish_phase2_0r_aggregate_tables.py` | Adds provenance and presentation columns to source aggregate tables | Canonical `aggregates/PHASE2_*.csv` tables only |

## Canonical aggregate CSVs

Every CSV is aggregate-level, contains no patient/admission identifiers, and is stored under `aggregates/`.

| File | Contents / provenance |
|---|---|
| `aggregates/phase2_0r_run_metadata.csv` | Cohort reconciliation and input/QC counters; aggregate metrics only |
| `aggregates/PHASE2_BASELINE_DIAGNOSIS_TEMPORAL_SUMMARY.csv` | Disease-level source timing/count table; three rows, no patient identifiers |
| `aggregates/phase2_0r_bp_thresholds.csv` | Detailed threshold calculations produced by the reproducible aggregate script |
| `aggregates/PHASE2_BP_THRESHOLD_COMPARISON.csv` | Enriched canonical BP threshold table with units, window, population and missingness interpretation |
| `aggregates/phase2_0r_bp_retained_excluded.csv` | Retained/excluded source summaries |
| `aggregates/PHASE2_BP_RETAINED_EXCLUDED.csv` | Enriched retained/excluded summaries |
| `aggregates/phase2_0r_horizons.csv` | Detailed recorded event, death, encounter and observation-status summaries |
| `aggregates/PHASE2_FOLLOWUP_HORIZON_COMPARISON.csv` | Enriched canonical horizon table and source definitions |
| `aggregates/phase2_0r_death_index_reconciliation.csv` | Death linkage and timing metrics restricted to the reconstructed common-index set |
| `aggregates/death_source_reconciliation.csv` | Source-universe death reconciliation; different universe and units are labeled per row |
| `aggregates/PHASE2_DEATH_SOURCE_COMPARISON.csv` | Combined, explicitly scoped source-universe and common-index death evidence |
| `aggregates/phase2_0r_conditional_support.csv` | Detailed outcome-free support method results |
| `aggregates/PHASE2_CONDITIONAL_SUPPORT_DIAGNOSTICS.csv` | Enriched support table with policy/covariate availability metadata |
| `aggregates/phase2_0r_subgroups.csv` | Detailed subgroup summaries and illustrative binomial scenarios |
| `aggregates/PHASE2_SUBGROUP_PRECISION_TABLE.csv` | Enriched canonical subgroup table with unit/precision cautions |
| `aggregates/bp_count_threshold_feasibility.csv` | Earlier Phase 2.0 aggregate-only snapshot; superseded by Phase 2.0-R counts |
| `aggregates/followup_horizon_feasibility.csv` | Earlier Phase 2.0 horizon snapshot; superseded by Phase 2.0-R horizon evidence |
| `aggregates/omr_archive_comparison.csv` | OMR archive member sizes, hashes, headers and equality result |
| `aggregates/omr_coverage_context.csv` | Older archive-wide coverage counts, clearly distinguished from revised cohort denominators |

The enriched `PHASE2_*.csv` tables and the lower-case `phase2_0r_*.csv` files are not competing output locations: the latter are reproducibility-script outputs; the former are derived, provenance-enriched deliverables. Both are canonical aggregate evidence in this one directory. The earlier threshold and follow-up snapshots are retained as history, not current findings.

## Layout and privacy

```text
revised/phase2/
  *.md
  aggregates/*.csv
  scripts/*.py
```

Patient-level data are not stored here. Root `.gitignore` excludes `data/` (including the recommended `data/derived/revised_phase2/` local workspace), RAR archives, and Python caches. Verify ignore behavior before any future row-level write. No commit or push was performed.

## Task B prepared-data investigation additions

| File | Role |
|---|---|
| `PHASE2_PREPARED_DATA_BLOCKER_REASSESSMENT.md` | Cross-source blocker and prepared-feature review |
| `PHASE2_BASELINE_DIAGNOSIS_TEMPORAL_VALIDATION.md` | Disease code mappings, admission-level timing and master feature assessment |
| `PHASE2_OBSERVATION_AND_DEATH_FINAL_AUDIT.md` | Final source inventory for observation, encounters, death, treatment and labs |
| `PHASE2_IDENTIFIABILITY_AND_ESTIMAND_DECISION.md` | Original estimand identification assessment and human options A/B/C |
| `PHASE2_GATE0_FINAL_RECOMMENDATION.md` | Final Gate 0 recommendation; no cohort/effects authorization |
| `scripts/phase2_b_prepared_data_audit.py` | Reproduces aggregate diagnosis timing summary using transient patient linkage |
| `aggregates/PHASE2_BASELINE_DIAGNOSIS_TEMPORAL_SUMMARY.csv` | Three disease-level aggregate timing rows; no patient identifiers |

The original research estimand and fixed BP policy are unchanged. Gate 0 remains failed; the research team must decide among the documented paths.
