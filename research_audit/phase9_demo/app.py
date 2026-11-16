"""Interactive aggregate-results explorer for academic demonstration."""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from charts import group_effects, layer1_forest, layer2_forest, robustness_scatter
from data_loader import ROOT, load_results


st.set_page_config(page_title="MI–ECG Research Results Explorer", page_icon="📊", layout="wide")
st.title("MI-ECG Research Results Explorer")
st.caption("Aggregate results from a two-layer observational analysis. This demonstration is not a diagnostic or patient prediction tool.")

try:
    d = load_results()
except Exception as exc:  # show actionable local setup error
    st.error(f"Could not load the saved aggregate result tables: {exc}")
    st.stop()

section = st.sidebar.radio("Explore", ["Study overview", "Layer 1 - risk factors", "Layer 2 - ECG features", "Robustness", "Interpretation & limits", "Saved figures"])

if section == "Study overview":
    st.header("Study overview")
    st.write("The study describes two admission-level adjusted association targets: recorded cardiovascular risk-factor histories with acute MI coding (Layer 1), and handcrafted ECG feature differences across acute-MI-coded admissions and clean controls (Layer 2).")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Adult admission denominator", "431,231")
    c2.metric("ECG eligible", "191,275 · 44.36%")
    c3.metric("Primary Layer 2 admissions", "167,066")
    c4.metric("Patient clusters", "93,946")
    st.info("One earliest eligible in-episode ECG was retained per admission. The 24,209 historical-MI-only admissions were kept separate and excluded from the primary clean-control comparison.")
    st.subheader("Primary feature-group pattern")
    st.plotly_chart(group_effects(d["layer2"]), width="stretch")
    st.caption("Bars summarize mean absolute standardized effects across correlated features in each group; they are descriptive summaries, not independent replications.")
    st.subheader("Design")
    st.markdown("- **Layer 1:** four adjusted risk differences for recorded histories and acute MI coding; prior MI is descriptive.\n- **Layer 2:** AIPW adjusted mean differences across 95 handcrafted features.\n- Five-fold patient-group cross-fitting; patient-level uncertainty; 95-feature BH FDR.\n- β-VAE embeddings are excluded because model/checkpoint provenance could not be verified.")

elif section == "Layer 1 - risk factors":
    st.header("Layer 1: cardiovascular risk factors")
    st.write("Adjusted admission-level risk differences for acute MI coding by recorded prior history, in the ECG-selected adult-admission cohort.")
    st.plotly_chart(layer1_forest(d["layer1"]), width="stretch")
    tab = d["layer1"].copy()
    tab["Adjusted RD (percentage points)"] = tab["adjusted_percentage_point_difference"].round(2)
    tab["95% bootstrap CI (percentage points)"] = tab.apply(lambda r: f"{r.adjusted_ci_lower_percentage_points:.2f} to {r.adjusted_ci_upper_percentage_points:.2f}", axis=1)
    st.dataframe(tab[["exposure", "Adjusted RD (percentage points)", "95% bootstrap CI (percentage points)", "interpretation"]], hide_index=True, width="stretch")
    st.caption("Hypertension is a small inverse observational association, not evidence of protection. CKD is compatible with the null. Prior MI is descriptive. These estimates do not establish intervention effects.")

elif section == "Layer 2 - ECG features":
    st.header("Layer 2: adjusted ECG feature differences")
    st.write("Each estimate is an adjusted mean difference divided by that feature's SD in the primary cohort. Positive values mean higher measured feature values in acute-MI-coded admissions under the fitted contrast.")
    all_data = d["layer2"].copy()
    groups = sorted(all_data.loc[all_data["physiological_outcome"], "feature_group"].unique())
    chosen = st.multiselect("Physiological feature groups", groups, default=groups)
    show_sig = st.checkbox("Show BH discoveries only", value=False)
    plot_data = all_data[all_data["feature_group"].isin(chosen) | ~all_data["physiological_outcome"]]
    if show_sig:
        plot_data = plot_data[plot_data["significant_bh_fdr_05"]]
    st.caption("QRS_Dur_Global_count is a technical/support feature and is shown separately; it is not interpreted as physiology.")
    st.plotly_chart(layer2_forest(plot_data), width="stretch")
    st.subheader("Feature table")
    display = plot_data.copy()
    display["Adjusted SMD (SD)"] = display["standardized_effect"].round(3)
    display["95% CI (SD)"] = display.apply(lambda r: f"{r.ci_lower/r.outcome_sd:.3f} to {r.ci_upper/r.outcome_sd:.3f}", axis=1)
    display["BH q"] = display["q_value"].map(lambda x: f"{x:.3g}")
    st.dataframe(display[["feature", "feature_group", "physiological_outcome", "Adjusted SMD (SD)", "95% CI (SD)", "BH q", "significant_bh_fdr_05"]], hide_index=True, width="stretch")
    st.caption("Intervals are Phase 5 patient-cluster bootstrap intervals divided by the saved primary-cohort SD. P-values for BH are patient-cluster influence-score Wald tests. Correlated feature tests are not independent replications.")

elif section == "Robustness":
    st.header("Robustness analyses")
    which = st.radio("Comparison", ["Selection weighting", "Broader MI coding"], horizontal=True)
    st.plotly_chart(robustness_scatter(d["comparison"], which), width="stretch")
    if which == "Selection weighting":
        st.markdown("Selection weights used **measured covariates only**. Weighted estimates retained the primary direction for 89/95 features; median absolute shift was 0.009 SD. The analysis cannot remove selection through unmeasured severity, symptoms, clinician ordering, or care pathways.")
    else:
        st.markdown("The broad definition adds historical MI coding on the same admission and changes the case mix. Direction agreement was 85/95, with attenuation in average absolute ST/T effects. Historical coding does not prove acute onset.")
    st.subheader("Subgroup interactions")
    inter = d["interactions"].copy()
    inter = inter[inter["interaction_significant_bh_05"]].sort_values("interaction_q_value_bh")
    st.write("Direct BH-adjusted interaction tests, not comparisons of within-subgroup significance counts:")
    st.dataframe(inter[["contrast", "feature", "feature_group", "estimate_difference", "ci_lower", "ci_upper", "interaction_q_value_bh"]], hide_index=True, width="stretch")
    st.caption("There are 11 age and 13 sex feature interactions passing BH. These indicate feature-specific statistical heterogeneity under the chosen strata; the age cutoff is an implementation choice.")
    st.subheader("Unmeasured-confounding sensitivity")
    conf = d["confounding"]
    st.dataframe(conf[conf["layer"].eq("Layer 1")][["exposure_or_feature", "e_value_point", "e_value_ci_nearest_null", "interpretation"]], hide_index=True, width="stretch")
    st.caption("Layer 1 E-values use an approximate RD-to-RR conversion. The Layer 2 additive tipping analysis is an illustrative binary-confounder scale, not an estimated confounder model.")

elif section == "Interpretation & limits":
    st.header("What these results support")
    st.markdown("The saved results support adjusted observational associations among the studied ECG-selected inpatient admissions. ST and T feature groups have the largest mean absolute standardized contrasts, with lead-dependent directions. Selection weighting and broader-code analyses are robustness checks under their stated assumptions.")
    st.header("What they do not establish")
    st.markdown("- **Temporal order:** MI onset relative to the selected ECG is unknown; MI is not known to precede the waveform.\n- **Diagnostic incorporation:** ECG findings may contribute to MI diagnosis, so feature differences may partly reflect diagnosis assignment/documentation rather than physiology alone.\n- **Causality:** residual confounding, coding error, limited overlap, and selection remain.\n- **Transport:** ECG availability was 44.36%; weights balanced measured covariates only.\n- **Independent replication:** the 95 feature outcomes are correlated.\n- **Prediction:** no patient-level scores, predictions, or clinical decision support are provided.\n- **Latent representations:** β-VAE embeddings are excluded because training/checkpoint provenance was unresolved.")
    st.warning("This application is an aggregate research-results explorer. It is not intended for patient care, diagnosis, or individual risk prediction.")

else:
    st.header("Saved Phase 8 figures")
    fig_dir = ROOT / "research_audit" / "phase8" / "PHASE8_FIGURES"
    images = sorted(fig_dir.glob("Figure*.png"), key=lambda p: int(p.name.split("_")[0].replace("Figure", "")))
    if not images:
        st.info("Saved PNGs are not available in this checkout. The interactive charts above use the saved aggregate tables directly.")
    else:
        selected = st.selectbox("Figure", images, format_func=lambda p: p.name)
        st.image(str(selected), caption=selected.stem, width="stretch")

st.divider()
st.caption("Data source: saved aggregate Phase 8 tables derived from finalized Phase 3–7 outputs. The demo reads no row-level MIMIC data and fits no statistical or machine-learning model.")
