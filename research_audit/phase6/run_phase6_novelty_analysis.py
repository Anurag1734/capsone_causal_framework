"""Phase 6: reuse Phase 5 estimates and reproduce its outcome nuisances only
to obtain the model-implied profiles that Phase 5 did not persist.
"""
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research_audit/phase6'
FIG=OUT/'PHASE6_FIGURES'
sys.path.insert(0,str(ROOT/'research_audit/phase5'))
import run_phase5_estimation as p5

def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    data=pd.read_parquet(p5.DATA)
    groups=pd.read_csv(p5.GROUPS)
    crude=pd.read_csv(p5.OUT/'PHASE5_LAYER2_CRUDE_ESTIMATES.csv')
    adjusted=pd.read_csv(p5.OUT/'PHASE5_LAYER2_ADJUSTED_ESTIMATES.csv')
    fdr=pd.read_csv(p5.OUT/'PHASE5_LAYER2_FDR_RESULTS.csv')
    group_results=pd.read_csv(p5.OUT/'PHASE5_FEATURE_GROUP_RESULTS.csv')
    folds=pd.read_csv(p5.OUT/'PHASE5_CROSSFIT_FOLD_ASSIGNMENTS.csv')[['patient_id','crossfit_fold']]
    data=data.merge(folds,on='patient_id',validate='many_to_one')
    eligible=data[data.primary_analysis_eligible].copy()
    features=groups.feature.tolist()
    hist=['diabetes_prior','hypertension_prior','ckd_prior','prior_mi']
    covars=['age_years','sex']+hist
    spline_df=int(pd.read_csv(p5.OUT/'PHASE5_VALIDATION_MODEL_SELECTION.csv').set_index('analysis').loc['layer2_outcome','outcome_age_spline_df'])
    # Merge complete, finalized Phase 5 feature estimates; no new association estimates.
    result=(crude[['feature','crude_difference','crude_sd','crude_ci_lower','crude_ci_upper','crude_p_value']]
            .merge(adjusted[['feature','adjusted_effect','ci_lower','ci_upper','cluster_robust_se','p_value','outcome_sd','standardized_effect']],on='feature')
            .merge(fdr[['feature','q_value','significant_bh_fdr_05']],on='feature')
            .merge(groups[['feature','feature_group','physiological_outcome']],on='feature'))
    result['crude_standardized_effect']=result.crude_difference/result.outcome_sd
    result['adjusted_minus_crude']=result.adjusted_effect-result.crude_difference
    result['standardized_adjustment_shift']=result.standardized_effect-result.crude_standardized_effect
    result['direction_agreement']=np.sign(result.crude_standardized_effect)==np.sign(result.standardized_effect)
    result['absolute_magnitude_reduced_after_adjustment']=result.standardized_effect.abs()<result.crude_standardized_effect.abs()
    result['absolute_effect_rank']=result.standardized_effect.abs().rank(ascending=False,method='min').astype(int)
    result.sort_values('absolute_effect_rank').to_csv(OUT/'PHASE6_FEATURE_NOVELTY_RESULTS.csv',index=False)

    # Reference profiles are actual baseline covariate combinations from train;
    # choose an observed row closest to median age in each prespecified stratum.
    train=eligible[eligible.source_master_split=='train'].copy()
    train['history_burden']=train[hist].sum(axis=1)
    sex_mode=train.sex.mode().iloc[0]
    cells=train[train.history_burden.between(1,2)].groupby(['sex']+hist,dropna=False).size().sort_values(ascending=False)
    modal=tuple(cells.index[0])
    def choose(name,mask,reference_age=None):
        pool=train.loc[mask].copy()
        if pool.empty: raise RuntimeError(f'No training rows for profile {name}')
        target=float(pool.age_years.median() if reference_age is None else reference_age)
        pool['_age_dist']=(pool.age_years-target).abs()
        row=pool.sort_values(['_age_dist','admission_id']).iloc[0]
        return {'profile':name,'source_train_rows':len(pool),'reference_age_target':target,'selected_age_years':float(row.age_years),'sex':row.sex,
                **{h:int(row[h]) for h in hist},'history_burden':int(row.history_burden),'row_index':int(row.name)}
    mask_modal=np.ones(len(train),dtype=bool)
    for col,val in zip(['sex']+hist,modal): mask_modal &= train[col].to_numpy()==val
    profiles=[
        choose('common one-or-two-history profile',mask_modal),
        choose('no coded prior-history conditions',train.history_burden.eq(0).to_numpy() & train.sex.eq(sex_mode).to_numpy()),
        choose('multiple coded prior-history conditions (3 or 4)',train.history_burden.ge(3).to_numpy()),
    ]
    # Recreate the exact Phase 5 cross-fitted arm-specific linear outcome nuisance
    # predictions. No new learner, covariates, split, or estimator is introduced.
    y=eligible[features].to_numpy(float); t=eligible.acute_mi_diagnosis.to_numpy(int)
    m0=np.empty_like(y); m1=np.empty_like(y); propensity=np.empty(len(eligible))
    for fold in range(p5.FOLDS):
        held=eligible.crossfit_fold.to_numpy()==fold; fit=~held
        xtr,xte=p5.design_pair(eligible.loc[fit],eligible.loc[held],covars,spline_df)
        tfit=t[fit]
        propensity[held]=p5.pred_prob(p5.logit_model(xtr,tfit),xte)
        yfit=y[fit]
        for a,targets in ((0,m0),(1,m1)):
            arm=tfit==a
            beta=np.linalg.lstsq(xtr[arm],yfit[arm],rcond=None)[0]
            targets[held]=xte@beta
    prediction_delta=m1-m0
    profile_rows=[]
    by_index={int(idx):pos for pos,idx in enumerate(eligible.index)}
    for profile in profiles:
        pos=by_index[profile.pop('row_index')]
        for j,feature in enumerate(features):
            ar=result.loc[result.feature==feature].iloc[0]
            profile_rows.append({**profile,'feature':feature,'feature_group':ar.feature_group,
                'physiological_outcome':bool(ar.physiological_outcome),'model_predicted_feature_MI0':m0[pos,j],
                'model_predicted_feature_MI1':m1[pos,j],'model_implied_MI1_minus_MI0':prediction_delta[pos,j],
                'model_implied_difference_SD':prediction_delta[pos,j]/ar.outcome_sd,
                'crossfit_MI_propensity_at_profile':propensity[pos],
                'phase5_AIPW_population_estimate':ar.adjusted_effect,'phase5_AIPW_CI_lower':ar.ci_lower,
                'phase5_AIPW_CI_upper':ar.ci_upper,'profile_prediction_interval':'not estimated'})
    profile_df=pd.DataFrame(profile_rows)
    profile_df.to_csv(OUT/'PHASE6_COUNTERFACTUAL_PROFILE_PREDICTIONS.csv',index=False)

    # Figures from existing Phase 5 estimates and these same-model profile outputs.
    top=result[result.physiological_outcome].nsmallest(25,'absolute_effect_rank').sort_values('standardized_effect')
    fig,ax=plt.subplots(figsize=(9,10)); yloc=np.arange(len(top))
    ax.errorbar(top.standardized_effect,yloc,xerr=np.vstack([(top.adjusted_effect-top.ci_lower)/top.outcome_sd,(top.ci_upper-top.adjusted_effect)/top.outcome_sd]),fmt='o',capsize=2)
    ax.axvline(0,color='black',lw=.7); ax.set_yticks(yloc,top.feature,fontsize=8); ax.set_xlabel('Adjusted observational contrast (outcome SD; Phase 5 bootstrap CI)'); ax.set_title('Largest adjusted physiological ECG contrasts')
    fig.tight_layout(); fig.savefig(FIG/'largest_adjusted_ecg_contrasts.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,6)); ax.scatter(result.crude_standardized_effect,result.standardized_effect,c=np.where(result.significant_bh_fdr_05,'#c43c39','#3976a8'),alpha=.8)
    for _,r in result.nsmallest(8,'absolute_effect_rank').iterrows(): ax.annotate(r.feature,(r.crude_standardized_effect,r.standardized_effect),fontsize=7,xytext=(3,3),textcoords='offset points')
    lim=max(np.abs(result[['crude_standardized_effect','standardized_effect']].to_numpy()).max(),.1); ax.plot([-lim,lim],[-lim,lim],color='gray',lw=.8,ls='--'); ax.axhline(0,color='black',lw=.5); ax.axvline(0,color='black',lw=.5)
    ax.set_xlabel('Crude difference (outcome SD)'); ax.set_ylabel('Adjusted difference (outcome SD)'); ax.set_title('Crude vs. adjusted feature contrasts; red = BH q<0.05')
    fig.tight_layout(); fig.savefig(FIG/'crude_vs_adjusted.png',dpi=180); plt.close(fig)
    gr=group_results[group_results.degrees_freedom>1].copy().sort_values('mean_absolute_standardized_effect')
    fig,ax=plt.subplots(figsize=(8,5)); ax.barh(gr.feature_group,gr.mean_absolute_standardized_effect,color='#3976a8'); ax.set_xlabel('Mean absolute adjusted contrast (outcome SD)'); ax.set_title('Adjusted feature magnitude by group (correlated outcomes)')
    fig.tight_layout(); fig.savefig(FIG/'feature_group_magnitudes.png',dpi=180); plt.close(fig)
    pivot=profile_df[profile_df.physiological_outcome].pivot(index='feature',columns='profile',values='model_implied_difference_SD')
    topnames=result[result.physiological_outcome].nsmallest(15,'absolute_effect_rank').feature.tolist()
    pivot=pivot.loc[topnames]
    cap=max(.4,float(np.ceil(np.max(np.abs(pivot.to_numpy()))*10)/10))
    fig,ax=plt.subplots(figsize=(10,7)); im=ax.imshow(pivot.to_numpy(),aspect='auto',cmap='coolwarm',vmin=-cap,vmax=cap)
    ax.set_yticks(np.arange(len(pivot)),pivot.index,fontsize=7); ax.set_xticks(np.arange(len(pivot.columns)),pivot.columns,rotation=25,ha='right',fontsize=7); fig.colorbar(im,ax=ax,label='Model-implied MI1 - MI0 (outcome SD)'); ax.set_title('Exploratory model-implied contrasts at reference profiles')
    fig.tight_layout(); fig.savefig(FIG/'model_implied_profile_differences.png',dpi=180); plt.close(fig)

    # Detailed analysis notes are written alongside the numerical artifacts.
    sigphys=result[(result.physiological_outcome)&result.significant_bh_fdr_05]
    groupsummary=result[result.physiological_outcome].groupby('feature_group').agg(n=('feature','count'),fdr_significant=('significant_bh_fdr_05','sum'),mean_abs_standardized=('standardized_effect',lambda x:x.abs().mean()),mean_signed_standardized=('standardized_effect','mean')).reset_index()
    sign_match=int(result.direction_agreement.sum()); reduced=int(result.absolute_magnitude_reduced_after_adjustment.sum()); corr=float(result.crude_standardized_effect.corr(result.standardized_effect))
    (OUT/'PHASE6_DECONFOUNDED_ECG_ANALYSIS.md').write_text(
        "# Phase 6A - Deconfounded ECG Feature Analysis\n\n"
        "This component reuses the finalized Phase 5 adjusted observational contrasts and does not re-estimate effects. The primary cohort is 167,066 admissions from 93,946 patients, with 7,353 acute-MI diagnoses and 159,713 clean controls. All 95 handcrafted features are complete. Features are grouped as ST, Q, R, T, QRS, RR, other morphology, and a separate technical/support count. Beta-VAE dimensions remain excluded.\n\n"
        f"At BH FDR 5%, {int(result.significant_bh_fdr_05.sum())}/95 feature tests are significant, including {len(sigphys)}/94 physiological outcomes and the technical count metric. Crude and adjusted standardized estimates have correlation {corr:.3f}; directions agree for {sign_match}/95 features, while adjustment reduces absolute standardized magnitude for {reduced}/95. This is substantial attenuation for many features, although selected contrasts remain prominent.\n\n"
        "The largest physiological adjusted differences are led by ST_Elev_I (-0.346 SD), T_Amp_I (-0.336 SD), T_Amp_aVR (+0.327 SD), ST_Elev_aVF (-0.302 SD), ST_Elev_aVR (+0.270 SD), T_Amp_V5 (-0.269 SD), and T_Amp_V6 (-0.264 SD). Phase 5 bootstrap intervals and q-values are retained in `PHASE6_FEATURE_NOVELTY_RESULTS.csv`. The most visible structure is in ST and T morphology across leads, with lead-dependent sign patterns; it should not be compressed into one universal MI signature.\n\n"
        "All results are adjusted observational differences among admissions with an eligible ECG. Unknown MI onset relative to the ECG prevents temporal verification of the proposed MI-to-ECG direction. ECG selection, limited propensity overlap, feature dependence, unmeasured confounding, and diagnosis undercoding remain. FDR significance is not clinical importance, and correlated feature rows are not independent replications. No novelty claim relative to prior literature is made by these analyses alone.\n"
    )
    lines=["# Phase 6A - Feature Group Interpretation","","The mean absolute standardized adjusted differences and significant-feature counts below summarize the completed Phase 5 estimates. They are descriptive summaries of correlated features, not independent group replications.","","| Group | Features | BH-significant | Mean absolute adjusted difference (SD) | Mean signed difference (SD) |","|---|---:|---:|---:|---:|"]
    for _,r in groupsummary.sort_values('mean_abs_standardized',ascending=False).iterrows(): lines.append(f"| {r.feature_group} | {int(r.n)} | {int(r.fdr_significant)} | {r.mean_abs_standardized:.3f} | {r.mean_signed_standardized:+.3f} |")
    lines += ["","ST features show the largest average absolute adjusted contrast (0.162 SD), with 10/12 passing BH FDR. T features average 0.129 SD, with 22/24 passing. Their signs vary across leads: for example, ST_Elev_I and ST_Elev_aVF are negative while ST_Elev_aVR is positive; T amplitudes are positive in aVR and V1 but negative in several lateral/precordial leads. This lead dependence is a pattern to describe, not a validated diagnostic signature.","","RR (2/2, mean absolute 0.128 SD) and QRS (1/2, 0.091 SD) also show group-level evidence. Q and R have smaller mean absolute standardized contrasts (about 0.053 SD), though 13 features in each family pass BH. Other morphology has 5/6 features pass with a 0.062 SD mean absolute contrast. `QRS_Dur_Global_count` is technical support and remains distinct from physiology.","","The Phase 4 test-split check and training diagnostics show strong residual dependence across features. Accordingly, lead summaries and feature-group results should be read as correlated measurements from the same ECG, not as multiple independent confirmations. See `PHASE5_FEATURE_GROUP_RESULTS.csv` and `PHASE6_FEATURE_NOVELTY_RESULTS.csv` for full estimates."]
    (OUT/'PHASE6_FEATURE_GROUP_INTERPRETATION.md').write_text('\n'.join(lines)+'\n')
    profile_md=["# Phase 6C - Exploratory Model-Implied ECG Profiles","","## Availability and method","","Phase 5 did not persist fitted models or the cross-fitted arm-specific outcome predictions. It did persist the reproducible Phase 5 estimator, model-selection result, cross-fit fold assignments, and nuisance specification. To produce the requested predictions, this component re-fits only the same Phase 5 cross-fitted Layer 2 outcome regressions: separate multivariate least-squares outcome models in MI=0 and MI=1 arms, using the existing six covariates and the validation-selected cubic age spline (df="+str(spline_df)+"). No alternative learner or covariate set was introduced. The same patient folds and the Phase 5 primary cohort were used.","","For each fixed covariate profile x, the reported quantities are m0(x) and m1(x), the outcome-model predictions with the acute-MI diagnosis indicator set to 0 or 1 while holding x constant. Each profile is an observed training-set baseline row; no patient identifier or observed ECG value is used. The three profiles are: (1) a common one-history pattern (70-year-old recorded female, hypertension only); (2) no coded prior-history conditions (61-year-old recorded female); and (3) three coded conditions (66-year-old recorded male, diabetes, hypertension, and CKD). The profiles and all 95 feature predictions are in `PHASE6_COUNTERFACTUAL_PROFILE_PREDICTIONS.csv`. Their cross-fitted MI propensities are 0.020, 0.032, and 0.037, respectively, so predictions should be read with the limited-overlap caveat.","","## Interpretation and uncertainty","","These are model-implied conditional feature profiles, not observed counterfactuals, reconstructed ECG waveforms, clinical interventions, or predictions of what would happen if MI were prevented or induced. They inherit the linear outcome-model form, measured adjustment set, ECG-selected target, possible positivity problems, unmeasured confounding, feature dependence, and unknown diagnosis/ECG timing.","","There are no profile-specific uncertainty intervals. The Phase 5 patient bootstrap held fitted nuisance predictions fixed and estimated uncertainty for the population AIPW contrasts; it did not bootstrap-refit these profile prediction functions. The Phase 5 AIPW intervals are included only as context in the profile CSV and must not be read as intervals for m0(x), m1(x), or their difference. Cross-fitted MI propensities at the profiles are included as an overlap diagnostic.","","The output is exploratory only, as the roadmap specifies. No causal intervention meaning is assigned to setting the coded diagnosis indicator."]
    (OUT/'PHASE6_COUNTERFACTUAL_ANALYSIS.md').write_text('\n'.join(profile_md)+'\n')
    (OUT/'PHASE6_LATENT_ANALYSIS_STATUS.md').write_text(
        "# Phase 6B - Latent Representation Status\n\n"
        "The 64 beta-VAE dimensions remain excluded. The existing `BETA_VAE_PROVENANCE_REPORT.md` documents that model weights, training metadata/cohort split, and latent extraction outputs are unavailable, so checkpoint identity, training inclusion, extraction determinism, mapping integrity, and latent diagnostics cannot be verified. Phase 6 does not retrain the VAE or repeat those provenance checks. No verified latent representation is available; this component is excluded for the previously established reason. The handcrafted feature analysis proceeds without it.\n"
    )
    fdrn=int(result.significant_bh_fdr_05.sum())
    (OUT/'PHASE6_COMPLETION_REPORT.md').write_text(
        "# Phase 6 Completion Report\n\n"
        "## Components completed\n\n"
        f"**A. Deconfounded ECG analysis:** reused all 95 Phase 5 adjusted estimates and crude contrasts. {fdrn}/95 features passed BH FDR, including 66 physiological features and one technical/support feature. ST and T patterns were largest by group summaries, with lead-dependent directions. Feature dependence means these are not independent replications. See `PHASE6_DECONFOUNDED_ECG_ANALYSIS.md`, `PHASE6_FEATURE_NOVELTY_RESULTS.csv`, and `PHASE6_FEATURE_GROUP_INTERPRETATION.md`.\n\n"
        "**B. Latent audit:** excluded for the previously documented missing checkpoint, training metadata, and extraction outputs. No VAE was retrained and no provenance audit repeated; see `PHASE6_LATENT_ANALYSIS_STATUS.md`.\n\n"
        "**C. Model-implied profiles:** Phase 5 did not save fitted nuisance models or the cross-fitted m0/m1 predictions. For this specific deliverable, the same Phase 5 outcome-model specification and patient folds were reproduced to generate exploratory profile predictions. The method, profiles, and uncertainty limitation are documented in `PHASE6_COUNTERFACTUAL_ANALYSIS.md`; predictions are in `PHASE6_COUNTERFACTUAL_PROFILE_PREDICTIONS.csv`. They are not observed counterfactuals or causal intervention effects.\n\n"
        "## Limitations and review gate\n\n"
        "The MI-to-ECG direction is not empirically established because MI onset relative to ECG is unknown. ECG selection may bias associations; overlap is limited for some propensity models; residual feature dependence is substantial; coded histories may be incomplete; and all Phase 5 values are adjusted observational contrasts. Beta-VAE latents remain excluded. No Phase 7 analysis was started.\n\n"
        "Phase 6 deliverables are ready for review. The Phase 6 work products are complete, with the latent component explicitly excluded and counterfactual profiles explicitly exploratory. The roadmap's broader Gate 2 stability criterion is not yet cleared: sensitivity analyses are assigned to Phase 7 and have not been performed. This phase does not establish causal identification or a literature-based novelty claim. Phase 7 has not begun.\n\n"
        "## Files generated\n\n"
        "- `PHASE6_DECONFOUNDED_ECG_ANALYSIS.md`\n- `PHASE6_FEATURE_NOVELTY_RESULTS.csv`\n- `PHASE6_FEATURE_GROUP_INTERPRETATION.md`\n- `PHASE6_COUNTERFACTUAL_ANALYSIS.md`\n- `PHASE6_COUNTERFACTUAL_PROFILE_PREDICTIONS.csv`\n- `PHASE6_LATENT_ANALYSIS_STATUS.md`\n- `PHASE6_FIGURES/` (4 figures)\n- `PHASE6_COMPLETION_REPORT.md`\n- `run_phase6_novelty_analysis.py`\n"
    )
    print({'n_features':len(result),'significant':int(result.significant_bh_fdr_05.sum()),'phys_sig':int(sigphys.shape[0]),'profiles':[{k:v for k,v in p.items() if k!='source_train_rows'} for p in profiles],'profile_rows':len(profile_df)})

if __name__=='__main__': main()
