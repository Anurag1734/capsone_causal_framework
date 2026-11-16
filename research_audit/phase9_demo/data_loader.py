"""Load and validate saved aggregate Phase 3–7 CSV outputs."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "research_audit" / "phase8" / "PHASE8_TABLES"


def _read(name: str) -> pd.DataFrame:
    path = TABLES / name
    if not path.is_file():
        raise FileNotFoundError(f"Required saved result table is missing: {path}")
    return pd.read_csv(path)


def load_results() -> dict[str, pd.DataFrame]:
    """Return publication tables; this module never reads row-level data."""
    data = {
        "cohort": _read("Table1_cohort_counts.csv"),
        "layer1": _read("Table2_layer1_adjusted_estimates.csv"),
        "layer2": _read("Table3_layer2_all_95_features.csv"),
        "groups": _read("Table4_feature_group_omnibus.csv"),
        "selection": _read("TableS1_selection_weighted_feature_results.csv"),
        "coding": _read("TableS2_alternative_MI_definition_results.csv"),
        "subgroups": _read("TableS3_age_sex_subgroup_feature_results.csv"),
        "interactions": _read("TableS4_age_sex_interaction_results.csv"),
        "confounding": _read("TableS5_confounding_sensitivity_results.csv"),
        "comparison": _read("TableS6_primary_selection_broad_comparison.csv"),
    }
    validate_results(data)
    return data


def validate_results(data: dict[str, pd.DataFrame]) -> None:
    """Fail fast if key cohort counts or result structure drift from saved files."""
    expected_columns = {
        "layer1": {"exposure", "adjusted_risk_difference", "adjusted_ci_lower", "adjusted_ci_upper"},
        "layer2": {"feature", "feature_group", "physiological_outcome", "standardized_effect", "outcome_sd", "q_value", "significant_bh_fdr_05"},
        "selection": {"feature", "standardized_effect", "adjusted_effect_selection_weighted"},
        "coding": {"feature", "standardized_effect", "adjusted_effect"},
        "interactions": {"contrast", "feature", "estimate_difference", "interaction_q_value_bh"},
    }
    for key, columns in expected_columns.items():
        missing = columns.difference(data[key].columns)
        if missing:
            raise ValueError(f"{key} result is missing required columns: {sorted(missing)}")
    if len(data["layer2"]) != 95 or data["layer2"]["feature"].nunique() != 95:
        raise ValueError("Expected exactly 95 unique saved Layer 2 features.")
    if len(data["layer1"]) != 4:
        raise ValueError("Expected four saved Layer 1 contrasts.")
    if int(data["layer2"]["n_admissions"].iloc[0]) != 167066:
        raise ValueError("Saved Layer 2 cohort count differs from the finalized 167,066 admissions.")
    if int(data["layer2"]["n_patients"].iloc[0]) != 93946:
        raise ValueError("Saved Layer 2 patient count differs from the finalized 93,946 patients.")
