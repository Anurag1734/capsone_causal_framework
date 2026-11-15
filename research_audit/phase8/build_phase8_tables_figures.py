"""Build Phase 8 publication tables and figures from finalized Phase 3-7 outputs.

This script only reformats saved results for the manuscript. It fits no models,
rebuilds no cohort, and does not modify any finalized Phase 1-7 artifact.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "research_audit"
OUT = AUDIT / "phase8"
TAB = OUT / "PHASE8_TABLES"
FIG = OUT / "PHASE8_FIGURES"
P5 = AUDIT / "phase5"
P6 = AUDIT / "phase6"
P7 = AUDIT / "phase7"
TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

COLORS = {
    "ST": "#b44e35", "T": "#d5872c", "Q": "#477a9b", "R": "#377f78",
    "QRS": "#755c9a", "RR": "#8b6b55", "Other morphology": "#67824c",
    "Signal/measurement support": "#888888", "primary": "#334e68",
    "weighted": "#2f8f83", "broad": "#d5872c", "age": "#b44e35", "sex": "#477a9b",
}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 11,
                     "axes.labelsize": 9, "figure.dpi": 150, "savefig.dpi": 300,
                     "axes.spines.top": False, "axes.spines.right": False})

layer1 = pd.read_csv(P5 / "PHASE5_LAYER1_EFFECT_ESTIMATES.csv")
primary = pd.read_csv(P5 / "PHASE5_LAYER2_FDR_RESULTS.csv")
groups = pd.read_csv(P5 / "PHASE5_FEATURE_GROUP_RESULTS.csv")
feature_groups = pd.read_csv(AUDIT / "PHASE3_ECG_FEATURE_GROUPS.csv")
sel = pd.read_csv(P7 / "PHASE7_SELECTION_SENSITIVITY_RESULTS.csv")
alt = pd.read_csv(P7 / "PHASE7_ALTERNATIVE_MI_RESULTS.csv")
sub = pd.read_csv(P7 / "PHASE7_SUBGROUP_RESULTS.csv")
inter = pd.read_csv(P7 / "PHASE7_SUBGROUP_INTERACTIONS.csv")
evalues = pd.read_csv(P7 / "PHASE7_EVALUE_RESULTS.csv")
profiles = pd.read_csv(P6 / "PHASE6_COUNTERFACTUAL_PROFILE_PREDICTIONS.csv")

# Publication tables: preserve estimator scales and source-defined meanings.
cohort_rows = [
    ("Adult admission denominator", 431231, "All adult admissions in the corrected chronology and diagnosis audit"),
    ("No eligible in-episode ECG", 239956, "Not eligible for ECG feature outcome analysis"),
    ("ECG-selected admissions", 191275, "One earliest eligible ECG selected per admission"),
    ("ECG-selected patients", 99214, "Patients represented in the selected-admission cohort"),
    ("Acute MI diagnosis with selected ECG", 7353, "Acute ICD code on admission; may also have prior MI"),
    ("Nonacute historical/prior MI group", 24209, "Kept separate; excluded from primary clean comparison"),
    ("Clean comparison admissions", 159713, "No documented current or prior MI"),
    ("Primary Layer 2 admissions", 167066, "7,353 acute cases plus 159,713 clean comparisons"),
    ("Primary Layer 2 patients", 93946, "Patient clusters represented in primary comparison"),
]
pd.DataFrame(cohort_rows, columns=["stage_or_group", "admissions_or_patients", "definition"]).to_csv(TAB / "Table1_cohort_counts.csv", index=False)

l1 = layer1.copy()
for c in ["crude_risk_difference", "crude_ci_lower", "crude_ci_upper", "adjusted_risk_difference", "adjusted_ci_lower", "adjusted_ci_upper"]:
    l1[c.replace("risk_difference", "percentage_point_difference").replace("ci_lower", "ci_lower_percentage_points").replace("ci_upper", "ci_upper_percentage_points")] = 100 * l1[c]
l1.to_csv(TAB / "Table2_layer1_adjusted_estimates.csv", index=False)
primary.to_csv(TAB / "Table3_layer2_all_95_features.csv", index=False)
groups.to_csv(TAB / "Table4_feature_group_omnibus.csv", index=False)
sel.to_csv(TAB / "TableS1_selection_weighted_feature_results.csv", index=False)
alt.to_csv(TAB / "TableS2_alternative_MI_definition_results.csv", index=False)
sub.to_csv(TAB / "TableS3_age_sex_subgroup_feature_results.csv", index=False)
inter.to_csv(TAB / "TableS4_age_sex_interaction_results.csv", index=False)
evalues.to_csv(TAB / "TableS5_confounding_sensitivity_results.csv", index=False)

layer2_alt = alt.query("layer == 'Layer 2'").copy()
merged = primary.merge(sel[["feature", "adjusted_effect_selection_weighted", "standardized_effect", "weighted_q_value", "weighted_significant_bh_05"]], on="feature", suffixes=("_primary", "_selection"))
merged = merged.merge(layer2_alt[["feature", "adjusted_effect", "standardized_effect", "q_value", "significant_bh_fdr_05"]], on="feature", suffixes=("", "_broad"))
merged.rename(columns={"standardized_effect": "standardized_effect_selection_weighted",
                       "standardized_effect_primary": "standardized_effect_primary",
                       "standardized_effect_broad": "standardized_effect_broad",
                       "adjusted_effect": "adjusted_effect_primary",
                       "significant_bh_fdr_05": "significant_primary_bh_05",
                       "q_value": "primary_q_value"}, inplace=True)
merged["standardized_effect_primary"] = primary.set_index("feature").loc[merged.feature, "standardized_effect"].to_numpy()
merged["standardized_effect_broad"] = layer2_alt.set_index("feature").loc[merged.feature, "standardized_effect"].to_numpy()
merged["q_value_broad"] = layer2_alt.set_index("feature").loc[merged.feature, "q_value"].to_numpy()
merged["significant_broad_bh_05"] = layer2_alt.set_index("feature").loc[merged.feature, "significant_bh_fdr_05"].to_numpy()
merged["standardized_difference_broad_minus_primary"] = merged.standardized_effect_broad - merged.standardized_effect_primary
merged.to_csv(TAB / "TableS6_primary_selection_broad_comparison.csv", index=False)

summary = []
for name, d in [("Primary acute-code", primary), ("Selection-weighted", sel), ("Broad current-code", layer2_alt)]:
    for group in ["ST", "T", "QRS", "RR", "R", "Q", "Other morphology"]:
        dd = d[d.feature_group == group]
        if name == "Primary acute-code":
            sig_n = int(dd.significant_bh_fdr_05.sum())
            dir_n = len(dd)
        elif name == "Selection-weighted":
            sig_n = int(dd.weighted_significant_bh_05.sum())
            dir_n = int(dd.weighted_direction_matches_primary.sum())
        else:
            sig_n = int(dd.significant_bh_fdr_05.sum())
            primary_sign = dd.feature.map(primary.set_index("feature").standardized_effect)
            dir_n = int((np.sign(dd.standardized_effect) == np.sign(primary_sign)).sum())
        summary.append({"analysis": name, "feature_group": group,
                        "mean_absolute_standardized_effect": float(dd.standardized_effect.abs().mean()),
                        "features_n": len(dd), "features_BH_05": sig_n,
                        "direction_match_primary_n": dir_n})
pd.DataFrame(summary).to_csv(TAB / "Table5_feature_group_sensitivity_summary.csv", index=False)

# Figure 1: admission-level cohort flow.
fig, ax = plt.subplots(figsize=(10, 6.6)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
def box(x, y, w, h, title, detail, face="#f3f6f8", edge="#334e68"):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.015", linewidth=1.5, facecolor=face, edgecolor=edge)
    ax.add_patch(p); ax.text(x+w/2, y+h*0.64, title, ha="center", va="center", fontsize=11, weight="bold", color="#203548")
    ax.text(x+w/2, y+h*0.30, detail, ha="center", va="center", fontsize=9, color="#334e68", wrap=True)
def arrow(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2), arrowstyle="-|>", mutation_scale=14, linewidth=1.3, color="#52697c"))
box(.28,.82,.44,.12,"Adult admission denominator","431,231 admissions; all age >=18")
box(.28,.62,.44,.12,"Eligible ECG selected","191,275 admissions (44.36%); 99,214 patients\n239,956 denominator admissions had no eligible ECG")
arrow(.5,.82,.5,.74)
box(.02,.32,.29,.16,"Acute MI diagnosis","7,353 admissions\nacute ICD-9 410* or ICD-10 I21*/I22*")
box(.355,.32,.29,.16,"Historical/prior MI only","24,209 admissions\nretained as separate group")
box(.69,.32,.29,.16,"Clean comparison","159,713 admissions\nno documented current/prior MI")
for x in [.165,.5,.835]: arrow(.5,.62,x,.49)
box(.27,.06,.46,.13,"Primary Layer 2 comparison","167,066 admissions: 7,353 cases + 159,713 controls")
arrow(.165,.32,.39,.19); arrow(.835,.32,.61,.19)
ax.text(.5,.01,"One earliest in-episode ECG per admission; history-only group excluded from primary binary contrast.",ha="center",fontsize=8,color="#52697c")
fig.savefig(FIG/"Figure1_cohort_flow.png",bbox_inches="tight"); plt.close(fig)

# Figure 2: proposed causal graph and selection mechanism.
fig, axs = plt.subplots(1,2,figsize=(12,5.6));
def draw_dag_node(ax,xy,label,w=.24,h=.12,unmeasured=False):
    x,y=xy; ec="#b44e35" if unmeasured else "#334e68"; fc="#fff1e8" if unmeasured else "#edf3f7"
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=0.012,rounding_size=0.02",facecolor=fc,edgecolor=ec,linewidth=1.3))
    ax.text(x,y,label,ha="center",va="center",fontsize=8.5,wrap=True)
def draw_dag_edge(ax,a,b,style="-",color="#52697c",rad=0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=11,linewidth=1.1,color=color,linestyle=style,connectionstyle=f"arc3,rad={rad}",shrinkA=22,shrinkB=22))
for ax in axs: ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
axs[0].set_title("Layer 1 · recorded history and acute MI coding",fontsize=10,weight="bold",pad=10)
n1={"dem":(.14,.72),"dm":(.43,.84),"htn":(.43,.63),"ckd":(.43,.39),"pmi":(.43,.17),"ami":(.82,.60)}
for k,label in [("dem","Age and\nrecorded sex"),("dm","Prior diabetes"),("htn","Prior hypertension"),("ckd","Prior CKD"),("pmi","Prior MI\n(descriptive)"),("ami","Acute MI\ndiagnosis")]: draw_dag_node(axs[0],n1[k],label,w=.22 if k!="dem" else .25,h=.13)
for k in ["dm","htn","ckd","pmi"]: draw_dag_edge(axs[0],n1["dem"],n1[k],rad=(.08 if k in ["dm","htn"] else -.06))
for k in ["dm","htn","ckd"]: draw_dag_edge(axs[0],n1[k],n1["ami"],rad=(.07 if k=="dm" else -.04))
draw_dag_edge(axs[0],n1["dem"],n1["ami"],rad=-.18)
draw_dag_edge(axs[0],n1["pmi"],n1["ami"],style="--",color="#8b6b55")
draw_dag_edge(axs[0],n1["dm"],n1["ckd"])
axs[1].set_title("Layer 2 · diagnosis, ECG features, and selection",fontsize=10,weight="bold",pad=10)
n2={"cov":(.18,.72),"ami":(.50,.72),"ecg":(.84,.72),"u":(.44,.25),"s":(.84,.25)}
for k,label in [("cov","Age, sex, diabetes,\nHTN, CKD, prior MI"),("ami","Acute MI\ndiagnosis"),("ecg","95 ECG features"),("u","Acute severity / symptoms /\ncare pathway (unmeasured)"),("s","ECG selected\n(conditioned on)")]: draw_dag_node(axs[1],n2[k],label,w=.27 if k in ["cov","u"] else .22,h=.14 if k=="u" else .13,unmeasured=k=="u")
draw_dag_edge(axs[1],n2["cov"],n2["ami"],rad=-.08); draw_dag_edge(axs[1],n2["cov"],n2["ecg"],rad=.16)
draw_dag_edge(axs[1],n2["ami"],n2["ecg"],style="--",color="#b44e35")
draw_dag_edge(axs[1],n2["ami"],n2["s"],color="#b44e35",rad=.12)
draw_dag_edge(axs[1],n2["u"],n2["s"],color="#b44e35"); draw_dag_edge(axs[1],n2["u"],n2["ecg"],style="--",color="#b44e35",rad=-.12)
fig.suptitle("Roadmap causal structure and ECG selection",fontsize=13,weight="bold",y=.98)
fig.text(.5,.025,"Dashed arrows are descriptive or hypothesized. MI onset relative to the selected ECG is unknown; the diagnosis-to-feature direction is not established.",ha="center",fontsize=8,color="#52697c")
fig.tight_layout(rect=[0,.06,1,.93]); fig.savefig(FIG/"Figure2_proposed_causal_DAG.png",bbox_inches="tight"); plt.close(fig)

# Figure 3: Layer 1 risk differences with intervals.
fig, ax=plt.subplots(figsize=(8.5,4.2))
d=layer1.iloc[::-1].copy(); y=np.arange(len(d)); est=d.adjusted_risk_difference*100; lo=d.adjusted_ci_lower*100; hi=d.adjusted_ci_upper*100
ax.errorbar(est,y,xerr=np.vstack([est-lo,hi-est]),fmt="o",color="#334e68",ecolor="#527c9a",capsize=3,lw=1.5)
ax.axvline(0,color="#777",lw=1,ls="--"); ax.set_yticks(y,d.exposure.str.replace("_prior", "",regex=False).str.replace("_", " ").str.title())
ax.set_xlabel("Adjusted risk difference (percentage points)"); ax.set_title("Layer 1 adjusted risk differences")
fig.tight_layout(); fig.savefig(FIG/"Figure3_layer1_adjusted_effects.png",bbox_inches="tight"); plt.close(fig)

# Figure 4: all Layer 2 features, standardized effect forest.
f=primary.merge(feature_groups[["feature","feature_group"]],on="feature",suffixes=("","_map"))
f["lo_sd"]=f.ci_lower/f.outcome_sd; f["hi_sd"]=f.ci_upper/f.outcome_sd
order=["ST","T","Q","R","QRS","RR","Other morphology","Signal/measurement support"]
f["group_order"]=f.feature_group.map({g:i for i,g in enumerate(order)})
f.sort_values(["group_order","standardized_effect"],inplace=True)
fig,ax=plt.subplots(figsize=(10,23)); y=np.arange(len(f))
for grp,g in f.groupby("feature_group",sort=False):
    ii=g.index; inds=np.array([f.index.get_loc(i) for i in ii]); c=COLORS.get(grp,"#334e68")
    ax.errorbar(g.standardized_effect,inds,xerr=np.vstack([g.standardized_effect-g.lo_sd,g.hi_sd-g.standardized_effect]),fmt="o",ms=3.0,lw=.65,capsize=1.5,color=c,ecolor=c,label=grp)
ax.axvline(0,color="#777",lw=.8,ls="--"); ax.set_yticks(y,f.feature,fontsize=6.3); ax.invert_yaxis()
ax.set_xlabel("Adjusted mean difference (feature SD units; 95% CI)"); ax.set_title("Layer 2 adjusted differences across all 95 features")
ax.legend(loc="lower right",fontsize=7,ncol=2,frameon=False); fig.tight_layout(); fig.savefig(FIG/"Figure4_layer2_all_features_forest.png",bbox_inches="tight"); plt.close(fig)

# Figure 5: crude versus adjusted standardized feature estimates.
c=primary.copy()
c["crude_sd"]=c.crude_difference/c.outcome_sd
fig,ax=plt.subplots(figsize=(7.5,6.5))
for grp,g in c.groupby("feature_group"):
    ax.scatter(g.crude_sd,g.standardized_effect,s=20,alpha=.8,label=grp,color=COLORS.get(grp,"#334e68"),edgecolors="none")
lim=max(abs(c.crude_sd).max(),abs(c.standardized_effect).max())*1.05; ax.plot([-lim,lim],[-lim,lim],color="#888",ls="--",lw=1)
ax.set_xlim(-lim,lim);ax.set_ylim(-lim,lim);ax.set_xlabel("Crude mean difference (SD units)");ax.set_ylabel("Adjusted mean difference (SD units)")
ax.set_title("Adjustment attenuates many feature contrasts");ax.legend(fontsize=7,frameon=False,ncol=2)
ax.text(.03,.97,"r = 0.916; signs agree for 82/95; magnitude reduced for 75/95",transform=ax.transAxes,ha="left",va="top",fontsize=8)
fig.tight_layout();fig.savefig(FIG/"Figure5_crude_vs_adjusted.png",bbox_inches="tight");plt.close(fig)

# Figure 6: group-level mean absolute standardized effects and counts.
fg=pd.read_csv(P6/"PHASE6_FEATURE_GROUP_INTERPRETATION.md") if False else None
gdata=pd.read_csv(P5/"PHASE5_FEATURE_GROUP_RESULTS.csv")
interp=pd.read_csv(AUDIT/"PHASE3_ECG_FEATURE_GROUPS.csv").groupby("feature_group",as_index=False).size()
summary_g=pd.read_csv(OUT/"PHASE8_TABLES"/"Table5_feature_group_sensitivity_summary.csv")
prim_g=summary_g.query("analysis == 'Primary acute-code'").copy()
counts=primary.groupby("feature_group").agg(features=("feature","size"),bh=("significant_bh_fdr_05","sum")).reset_index()
prim_g=prim_g.merge(counts,on="feature_group",how="left")
prim_g=prim_g[prim_g.feature_group!="Signal/measurement support"].sort_values("mean_absolute_standardized_effect")
fig,ax=plt.subplots(figsize=(8.5,5)); y=np.arange(len(prim_g)); ax.barh(y,prim_g.mean_absolute_standardized_effect,color=[COLORS.get(x,"#334e68") for x in prim_g.feature_group],alpha=.88)
ax.set_yticks(y,prim_g.feature_group);ax.set_xlabel("Mean absolute adjusted difference (SD units)");ax.set_title("Physiological feature-group summaries")
for yy,(_,row) in zip(y,prim_g.iterrows()): ax.text(row.mean_absolute_standardized_effect+.003,yy,f"{int(row.bh)}/{int(row.features)} BH-significant",va="center",fontsize=8)
fig.tight_layout();fig.savefig(FIG/"Figure6_feature_group_summary.png",bbox_inches="tight");plt.close(fig)

# Figure 7: all BH-significant feature estimates, technical metric shown distinctly.
sig=primary[primary.significant_bh_fdr_05].copy(); sig["lo_sd"]=sig.ci_lower/sig.outcome_sd;sig["hi_sd"]=sig.ci_upper/sig.outcome_sd
sig.sort_values("standardized_effect",inplace=True);fig,ax=plt.subplots(figsize=(9,15));y=np.arange(len(sig))
for grp,g in sig.groupby("feature_group"):
    inds=np.array([sig.index.get_loc(i) for i in g.index]);c=COLORS.get(grp,"#334e68")
    ax.errorbar(g.standardized_effect,inds,xerr=np.vstack([g.standardized_effect-g.lo_sd,g.hi_sd-g.standardized_effect]),fmt="o",ms=3.5,lw=.8,capsize=2,color=c,ecolor=c,label=grp)
ax.axvline(0,color="#777",lw=.8,ls="--");ax.set_yticks(y,sig.feature,fontsize=6.8);ax.invert_yaxis();ax.set_xlabel("Adjusted mean difference (SD units; 95% CI)")
ax.set_title("Features passing BH FDR 5% (technical support metric separated)");ax.legend(frameon=False,fontsize=7,ncol=2)
fig.tight_layout();fig.savefig(FIG/"Figure7_FDR_significant_features.png",bbox_inches="tight");plt.close(fig)

# Figure 8: 95-feature primary vs sensitivity estimates.
comp=primary[["feature","feature_group","standardized_effect"]].rename(columns={"standardized_effect":"primary"})
comp=comp.merge(sel[["feature","standardized_effect"]].rename(columns={"standardized_effect":"weighted"}),on="feature")
comp=comp.merge(layer2_alt[["feature","standardized_effect"]].rename(columns={"standardized_effect":"broad"}),on="feature")
fig,axs=plt.subplots(1,2,figsize=(11,5.4))
for ax,col,label,color in [(axs[0],"weighted","Selection weighted",COLORS["weighted"]),(axs[1],"broad","Broad current MI code",COLORS["broad"])]:
    for grp,g in comp.groupby("feature_group"):
        ax.scatter(g.primary,g[col],s=18,alpha=.78,color=COLORS.get(grp,"#334e68"),edgecolors="none")
    lim=max(abs(comp.primary).max(),abs(comp[col]).max())*1.06;ax.plot([-lim,lim],[-lim,lim],ls="--",lw=1,color="#777");ax.axhline(0,color="#ccc",lw=.6);ax.axvline(0,color="#ccc",lw=.6)
    ax.set_xlim(-lim,lim);ax.set_ylim(-lim,lim);ax.set_title(label);ax.set_xlabel("Primary adjusted effect (SD)");ax.set_ylabel("Sensitivity adjusted effect (SD)")
axs[0].text(.03,.97,"89/95 directions agree",transform=axs[0].transAxes,va="top",fontsize=8)
axs[1].text(.03,.97,"85/95 directions agree; ST/T attenuate",transform=axs[1].transAxes,va="top",fontsize=8)
fig.suptitle("Feature-level comparison with primary estimates",y=1.02,fontsize=11);fig.tight_layout();fig.savefig(FIG/"Figure8_sensitivity_comparison.png",bbox_inches="tight");plt.close(fig)

# Figure 9: direct age/sex interaction contrasts for BH-significant features.
ints=inter[inter.interaction_significant_bh_05].copy();
sd=primary.set_index("feature").outcome_sd
ints["estimate_sd"]=ints.apply(lambda r:r.estimate_difference/sd[r.feature],axis=1)
ints["lo_sd"]=ints.apply(lambda r:r.ci_lower/sd[r.feature],axis=1);ints["hi_sd"]=ints.apply(lambda r:r.ci_upper/sd[r.feature],axis=1)
fig,axs=plt.subplots(1,2,figsize=(12,8))
for ax,contrast,title,color in [(axs[0],"age_>=65 minus age_<65","Age interaction contrasts",COLORS["age"]),(axs[1],"sex_M minus sex_F","Sex interaction contrasts",COLORS["sex"])]:
    dd=ints[ints.contrast==contrast].sort_values("estimate_sd");y=np.arange(len(dd));ax.errorbar(dd.estimate_sd,y,xerr=np.vstack([dd.estimate_sd-dd.lo_sd,dd.hi_sd-dd.estimate_sd]),fmt="o",ms=4,color=color,ecolor=color,capsize=2,lw=1)
    ax.axvline(0,color="#777",ls="--",lw=.8);ax.set_yticks(y,dd.feature,fontsize=7);ax.set_title(title);ax.set_xlabel("Interaction contrast (primary-cohort SD units; 95% CI)");ax.invert_yaxis()
fig.suptitle("Direct interaction tests passing BH q < 0.05",y=1.02,fontsize=11);fig.tight_layout();fig.savefig(FIG/"Figure9_age_sex_interactions.png",bbox_inches="tight");plt.close(fig)

# Figure 10: model-implied Phase 6 profiles, a small set of lead-dependent ST/T features.
show=["ST_Elev_I","ST_Elev_aVR","ST_Elev_aVF","T_Amp_I","T_Amp_aVR","T_Amp_V5"]
pr=profiles[profiles.feature.isin(show)].copy(); profile_order=list(pr.profile.drop_duplicates());
fig,axs=plt.subplots(1,len(profile_order),figsize=(4.1*len(profile_order),4.8),sharey=True)
if len(profile_order)==1: axs=[axs]
for ax,prof in zip(axs,profile_order):
    dd=pr[pr.profile==prof].set_index("feature").reindex(show).dropna();y=np.arange(len(dd));ax.scatter(dd.model_predicted_feature_MI0,y,label="MI indicator = 0",s=28,color="#477a9b")
    ax.scatter(dd.model_predicted_feature_MI1,y,label="MI indicator = 1",s=28,color="#b44e35")
    for yy,(_,row) in zip(y,dd.iterrows()):ax.plot([row.model_predicted_feature_MI0,row.model_predicted_feature_MI1],[yy,yy],color="#aab3ba",lw=.8)
    ax.set_yticks(y,dd.index if ax is axs[0] else [""]*len(y),fontsize=8);ax.set_title(prof,fontsize=8,wrap=True);ax.set_xlabel("Model-predicted stored-unit feature")
axs[0].legend(frameon=False,fontsize=7);fig.suptitle("Exploratory model-implied profiles; no profile-specific intervals",y=1.02,fontsize=11)
fig.tight_layout();fig.savefig(FIG/"Figure10_model_implied_profiles.png",bbox_inches="tight");plt.close(fig)

captions = """# Figure captions\n\n1. **Cohort flow.** Admission-level selection from the adult denominator to ECG-selected admissions and the acute, history-only, and clean-comparison groups. The selection box also reports the denominator admissions without an eligible ECG. The primary Layer 2 comparison excludes the history-only group.\n2. **Proposed causal graph.** Roadmap-based hypothesized two-layer structure and ECG selection mechanism. The diagnosis-to-feature arrow is an assumption, not identified temporal direction. The prior-MI edge is descriptive.\n3. **Layer 1 estimates.** AIPW adjusted risk differences for coded prior diabetes, hypertension, CKD, and MI predicting acute MI diagnosis in the ECG-selected adult-admission cohort. Horizontal bars show patient-cluster bootstrap 95% intervals.\n4. **Layer 2 estimates.** AIPW adjusted mean differences for all 95 features, standardized by each feature's primary-cohort SD. Error bars are transformed Phase 5 intervals. The technical support measure is distinct.\n5. **Crude versus adjusted.** Crude and adjusted mean differences for the same 95 features, divided by each outcome SD. The diagonal denotes equal estimates.\n6. **Feature groups.** Mean absolute standardized adjusted estimates among physiological groups; labels give BH-significant feature counts. Correlated features are not independent replications.\n7. **FDR results.** Estimates and intervals for features passing the primary 95-feature BH FDR 5% family. One technical support feature is shown separately.\n8. **Sensitivity comparison.** Standardized primary effects plotted against selection-weighted and broader-current-code estimates for all 95 features. The broad definition changes the case mix and attenuates mean ST/T contrasts.\n9. **Age and sex effect modification.** Direct interaction contrasts among features passing BH q<0.05, standardized by the primary-cohort feature SD. Within-subgroup significance alone is not used to infer effect modification.\n10. **Model-implied profiles.** Phase 6 predictions with the acute diagnosis indicator set to 0 or 1 at three fixed covariate profiles. These are exploratory outcome-model outputs, not observed counterfactual ECGs; no profile-specific intervals were estimated.\n"""
(FIG/"FIGURE_CAPTIONS.md").write_text(captions,encoding="utf-8")
print(f"Wrote {len(list(TAB.glob('*.csv')))} tables and {len(list(FIG.glob('Figure*.png')))} figures to {OUT}")
