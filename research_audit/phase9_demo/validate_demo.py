"""Smoke and numeric consistency checks for the aggregate-only demo."""

from data_loader import load_results
from charts import group_effects, layer1_forest, layer2_forest, robustness_scatter


def main() -> None:
    d = load_results()
    assert round(d["layer1"].set_index("exposure").loc["diabetes_prior", "adjusted_percentage_point_difference"], 2) == 0.69
    assert round(d["layer1"].set_index("exposure").loc["hypertension_prior", "adjusted_percentage_point_difference"], 2) == -0.51
    assert int(d["layer2"]["significant_bh_fdr_05"].sum()) == 67
    assert int((d["layer2"]["significant_bh_fdr_05"] & d["layer2"]["physiological_outcome"].astype(bool)).sum()) == 66
    assert int((~d["layer2"]["physiological_outcome"].astype(bool)).sum()) == 1
    assert int(d["interactions"]["interaction_significant_bh_05"].sum()) == 24
    figs = [layer1_forest(d["layer1"]), layer2_forest(d["layer2"]), group_effects(d["layer2"]),
            robustness_scatter(d["comparison"], "Selection weighting"),
            robustness_scatter(d["comparison"], "Broader MI coding")]
    assert all(fig.data for fig in figs)
    print("PASS: aggregate tables, headline numbers, 95-feature multiplicity counts, interactions, and interactive charts validated.")


if __name__ == "__main__":
    main()
