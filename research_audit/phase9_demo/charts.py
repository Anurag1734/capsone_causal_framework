"""Interactive Plotly views for aggregate analysis results."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLORS = {"primary": "#176B87", "weighted": "#3B8C6E", "broad": "#D17A22"}


def layer1_forest(data: pd.DataFrame) -> go.Figure:
    d = data.copy()
    d["label"] = d["exposure"].map({"diabetes_prior": "Diabetes", "hypertension_prior": "Hypertension", "ckd_prior": "CKD", "prior_mi": "Prior MI (descriptive)"})
    fig = go.Figure(go.Scatter(
        x=d["adjusted_percentage_point_difference"], y=d["label"], mode="markers",
        error_x={"type": "data", "symmetric": False,
                 "array": d["adjusted_ci_upper_percentage_points"] - d["adjusted_percentage_point_difference"],
                 "arrayminus": d["adjusted_percentage_point_difference"] - d["adjusted_ci_lower_percentage_points"]},
        marker={"color": COLORS["primary"], "size": 10},
        customdata=d[["adjusted_ci_lower_percentage_points", "adjusted_ci_upper_percentage_points"]],
        hovertemplate="%{y}<br>Risk difference: %{x:.2f} percentage points<br>95% bootstrap CI: %{customdata[0]:.2f} to %{customdata[1]:.2f}<extra></extra>"
    ))
    fig.add_vline(x=0, line_dash="dash", line_color="#777")
    fig.update_layout(title="Layer 1 adjusted risk differences", xaxis_title="Risk difference (percentage points)", yaxis_title="", height=360, margin={"l": 20, "r": 25, "t": 55, "b": 45})
    return fig


def layer2_forest(data: pd.DataFrame) -> go.Figure:
    d = data.sort_values("standardized_effect").copy()
    sd = d["outcome_sd"]
    d["std_low"] = d["ci_lower"] / sd
    d["std_high"] = d["ci_upper"] / sd
    d["label"] = d["feature"] + d["significant_bh_fdr_05"].map({True: " • BH", False: ""})
    d["type"] = d["physiological_outcome"].map({True: "Physiological", False: "Technical/support"})
    fig = go.Figure()
    colors = {"Physiological": COLORS["primary"], "Technical/support": "#B04A5A"}
    for outcome_type, part in d.groupby("type", sort=False):
        fig.add_trace(go.Scatter(
            x=part["standardized_effect"], y=part["label"], mode="markers", name=outcome_type,
            marker={"color": colors[outcome_type], "size": 8,
                     "symbol": ["diamond" if bool(v) else "circle" for v in part["significant_bh_fdr_05"]]},
            error_x={"type": "data", "symmetric": False,
                     "array": part["std_high"] - part["standardized_effect"],
                     "arrayminus": part["standardized_effect"] - part["std_low"]},
            customdata=part[["feature_group", "std_low", "std_high", "q_value"]],
            hovertemplate="%{y}<br>Group: %{customdata[0]}<br>Adjusted SMD: %{x:.3f} SD<br>95% CI: %{customdata[1]:.3f} to %{customdata[2]:.3f}<br>BH q: %{customdata[3]:.3g}<extra></extra>"
        ))
    fig.add_vline(x=0, line_dash="dash", line_color="#777")
    fig.update_layout(title="Adjusted Layer 2 standardized mean differences", xaxis_title="Adjusted mean difference (feature SD units)", yaxis_title="", height=max(650, len(d) * 17), margin={"l": 25, "r": 20, "t": 55, "b": 45}, legend_title="Outcome type", yaxis={"categoryorder": "array", "categoryarray": d["label"].tolist()})
    return fig


def group_effects(data: pd.DataFrame) -> go.Figure:
    d = data[data["physiological_outcome"].astype(bool)].groupby("feature_group", as_index=False).agg(mean_abs_smd=("standardized_effect", lambda x: x.abs().mean()), n=("feature", "count"))
    d = d.sort_values("mean_abs_smd", ascending=True)
    fig = px.bar(d, x="mean_abs_smd", y="feature_group", orientation="h", text="mean_abs_smd", color_discrete_sequence=[COLORS["primary"]])
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside", hovertemplate="%{y}<br>Mean |SMD|: %{x:.3f} SD<br>Features: %{customdata[0]}<extra></extra>", customdata=d[["n"]])
    fig.update_layout(title="Magnitude by physiological feature group", xaxis_title="Mean absolute standardized difference (SD units)", yaxis_title="", height=400, showlegend=False)
    return fig


def robustness_scatter(data: pd.DataFrame, comparison: str) -> go.Figure:
    if comparison == "Selection weighting":
        y, label = "standardized_effect_selection", "Selection weighted"
    else:
        y, label = "standardized_effect_broad", "Broader current-admission coding"
    d = data.copy()
    x = "standardized_effect_primary"
    fig = px.scatter(d, x=x, y=y, color="feature_group", hover_name="feature", hover_data={x: ":.3f", y: ":.3f"})
    lo = min(d[x].min(), d[y].min())
    hi = max(d[x].max(), d[y].max())
    fig.add_shape(type="line", x0=lo, y0=lo, x1=hi, y1=hi, line={"dash": "dash", "color": "#555"})
    fig.update_layout(title=f"Primary versus {label.lower()} estimates", xaxis_title="Primary adjusted difference (SD units)", yaxis_title=f"{label} difference (SD units)", height=520)
    return fig
