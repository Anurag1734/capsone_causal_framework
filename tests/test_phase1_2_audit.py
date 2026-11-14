from pathlib import Path

import research_audit.phase1_2_audit as audit


def test_generate_audit_outputs_creates_expected_files(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "data" / "raw").mkdir(parents=True)
    (repo_root / "data" / "modeling").mkdir(parents=True)
    (repo_root / "research_audit").mkdir(parents=True)

    audit.REPO_ROOT = repo_root
    audit.AUDIT_ROOT = repo_root / "research_audit"
    audit.OUTPUT_DIR = audit.AUDIT_ROOT

    audit.generate_audit_outputs()

    expected_files = [
        "PHASE1_CAUSAL_ESTIMANDS.md",
        "PHASE2_DATA_FEASIBILITY_REPORT.md",
        "BETA_VAE_PROVENANCE_REPORT.md",
        "ECG_SELECTION_FEASIBILITY.md",
        "PHASE1_2_COMPLETION_REPORT.md",
        "REPO_ARTIFACT_INVENTORY.csv",
        "CLINICAL_DIAGNOSIS_TIMING.csv",
        "ACUTE_MI_OUTCOME_AUDIT.csv",
        "ECG_TEMPORAL_AUDIT.csv",
        "ECG_FEATURE_AVAILABILITY.csv",
        "BETA_VAE_PROVENANCE_REPORT.csv",
        "ECG_SELECTION_FEASIBILITY.csv",
        "COHORT_COUNTS_AND_SPLITS.csv",
    ]

    for relative in expected_files:
        path = repo_root / "research_audit" / relative
        assert path.exists(), f"Missing required file: {relative}"

    inventory = repo_root / "research_audit" / "REPO_ARTIFACT_INVENTORY.csv"
    assert inventory.exists()
