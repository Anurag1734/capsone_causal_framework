"""Create Phase 4 graph, adjustment, and conditional-dependence artifacts.

Uses the finalized Phase 3 parquet read-only and the existing feature dictionary.
The feature-pair diagnostic is a measured-parent residual correlation screen,
not a causal effect estimator or a formal test of unmeasured-variable DAGs.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from patsy import dmatrix
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/analysis/observational_mi_ecg/analysis_dataset.parquet"
AUDIT = ROOT / "research_audit"


def main():
    groups = pd.read_csv(AUDIT / "PHASE3_ECG_FEATURE_GROUPS.csv")
    dict_df = pd.read_csv(AUDIT / "PHASE3_VARIABLE_DICTIONARY.csv")
    features = groups.feature.tolist()
    technical = groups.loc[
        ~groups.physiological_outcome.astype(str).str.lower().isin(["true", "1"]),
        "feature",
    ].tolist()
    physiological = [f for f in features if f not in technical]

    adjustment_rows = [
        ("diabetes_prior", "acute_mi_diagnosis", "age_years; sex", "Causal contrast proposed in roadmap; coded prior history"),
        ("hypertension_prior", "acute_mi_diagnosis", "age_years; sex", "Causal contrast proposed in roadmap; coded prior history"),
        ("ckd_prior", "acute_mi_diagnosis", "age_years; sex; diabetes_prior; hypertension_prior", "Causal contrast proposed in roadmap; no prior-MI adjustment"),
        ("prior_mi", "acute_mi_diagnosis", "age_years; sex; diabetes_prior; hypertension_prior; ckd_prior", "Descriptive association only; no causal discovery claim"),
    ]
    for feature in features:
        role = "technical/support sensitivity outcome" if feature in technical else "physiological ECG outcome"
        adjustment_rows.append(("acute_mi_diagnosis", feature,
                                "age_years (flexible); sex; diabetes_prior; hypertension_prior; ckd_prior; prior_mi",
                                f"Layer 2 adjusted association; {role}; ECG event timing unavailable"))
    pd.DataFrame(adjustment_rows, columns=["exposure", "outcome", "adjustment_set", "interpretation"]).to_csv(
        AUDIT / "PHASE4_ADJUSTMENT_SETS.csv", index=False
    )

    df = pd.read_parquet(DATA)
    df = df[(df.source_master_split == "train") & df.primary_analysis_eligible].copy()
    # Layer 2's Phase 3 primary binary cohort, restricted to original training patients.
    formula = ("1 + bs(age_years, df=5, degree=3) + C(sex) + acute_mi_diagnosis + "
               "diabetes_prior + hypertension_prior + ckd_prior + prior_mi")
    z = np.asarray(dmatrix(formula, df, return_type="dataframe"), dtype=float)
    y = df[physiological].astype(float).to_numpy()
    resid = y - z @ np.linalg.lstsq(z, y, rcond=None)[0]
    resid -= resid.mean(axis=0)
    norms = np.sqrt((resid * resid).sum(axis=0))
    pearson = (resid.T @ resid) / np.outer(norms, norms)
    ranked = np.apply_along_axis(rankdata, 0, resid)
    ranked -= ranked.mean(axis=0)
    rnorms = np.sqrt((ranked * ranked).sum(axis=0))
    spearman = (ranked.T @ ranked) / np.outer(rnorms, rnorms)
    group_map = groups.set_index("feature").feature_group.to_dict()
    n = len(df)
    rows = []
    for i, first in enumerate(physiological):
        for j in range(i + 1, len(physiological)):
            second = physiological[j]
            r, rho = float(pearson[i, j]), float(spearman[i, j])
            rows.append({
                "relationship": "ECG feature pair conditional independence (draft measured-parent implication)",
                "variable_1": first,
                "variable_2": second,
                "group_1": group_map[first],
                "group_2": group_map[second],
                "conditioning_variables": "acute_mi_diagnosis; age_years (5-df cubic spline); sex; diabetes_prior; hypertension_prior; ckd_prior; prior_mi",
                "graph_basis": "Draft Layer 2 graph gives each ECG feature the same measured parent set and has no feature-to-feature or shared measured ECG-substrate edges; independence is conditional on that simplified graph.",
                "diagnostic": "Pearson correlation of feature residuals after multivariable least-squares adjustment; residual Spearman correlation as robustness diagnostic. Training split, primary binary cohort.",
                "n_admissions": n,
                "n_patients": int(df.patient_id.nunique()),
                "partial_pearson_r": r,
                "residual_spearman_rho": rho,
                "practical_departure_abs_r_ge_0_05": abs(r) >= 0.05,
                "practical_departure_abs_r_ge_0_10": abs(r) >= 0.10,
                "interpretation": "Departure from the measured-parent-only implication; may reflect shared waveform substrate, omitted disease/severity, selection, or feature construction. Not a formal rejection of a DAG allowing latent common causes.",
            })
    pd.DataFrame(rows).to_csv(AUDIT / "PHASE4_CONDITIONAL_INDEPENDENCE_TESTS.csv", index=False)
    print(f"rows={n}; patients={df.patient_id.nunique()}; physiological_features={len(physiological)}; pairs={len(rows)}")
    print(f"max_abs_r={max(abs(x['partial_pearson_r']) for x in rows):.6f}; "
          f"median_abs_r={np.median([abs(x['partial_pearson_r']) for x in rows]):.6f}; "
          f"q95_abs_r={np.quantile([abs(x['partial_pearson_r']) for x in rows], .95):.6f}; "
          f"ge_005={sum(x['practical_departure_abs_r_ge_0_05'] for x in rows)}; "
          f"ge_010={sum(x['practical_departure_abs_r_ge_0_10'] for x in rows)}")
    print("top_pairs:")
    for x in sorted(rows, key=lambda x: abs(x["partial_pearson_r"]), reverse=True)[:8]:
        print(f"{x['variable_1']} | {x['variable_2']} | r={x['partial_pearson_r']:.3f} | rho={x['residual_spearman_rho']:.3f}")


if __name__ == "__main__":
    main()
