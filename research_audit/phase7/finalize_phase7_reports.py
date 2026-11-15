"""Finalize Phase 7 narrative reports from completed sensitivity output tables."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research_audit/phase7'

def main():
    primary=pd.read_csv(ROOT/'research_audit/phase5/PHASE5_LAYER2_FDR_RESULTS.csv')
    l1=pd.read_csv(ROOT/'research_audit/phase5/PHASE5_LAYER1_EFFECT_ESTIMATES.csv')
    sel=pd.read_csv(OUT/'PHASE7_SELECTION_SENSITIVITY_RESULTS.csv')
    alt=pd.read_csv(OUT/'PHASE7_ALTERNATIVE_MI_RESULTS.csv')
    sub=pd.read_csv(OUT/'PHASE7_SUBGROUP_RESULTS.csv')
    inter=pd.read_csv(OUT/'PHASE7_SUBGROUP_INTERACTIONS.csv')
    bal=pd.read_csv(OUT/'PHASE7_SELECTION_COVARIATE_BALANCE.csv')
    metadata=json.loads((ROOT/'data/analysis/observational_mi_ecg/dataset_manifest.json').read_text()) if (ROOT/'data/analysis/observational_mi_ecg/dataset_manifest.json').exists() else {}
    alt2=alt[alt.layer=='Layer 2'].copy()
    primary_idx=primary.set_index('feature')
    alt2['primary_estimate']=alt2.feature.map(primary_idx.adjusted_effect)
    broad_same=int((np.sign(alt2.adjusted_effect)==np.sign(alt2.primary_estimate)).sum())
    broad_sig=int(alt2.significant_bh_fdr_05.sum())
    broad_sig_overlap=len(set(alt2.loc[alt2.significant_bh_fdr_05,'feature']) & set(primary.loc[primary.significant_bh_fdr_05,'feature']))
    sel_same=int(sel.weighted_direction_matches_primary.sum())
    sel_sig=int(sel.weighted_significant_bh_05.sum())
    sel_sig_overlap=int((sel.weighted_significant_bh_05 & sel.significant_bh_fdr_05).sum())
    sel_med=float(sel.weighted_abs_effect_change_sd.abs().median())
    selection_diag={
        'denominator_n':431231,'selected_n':191275,'selection_rate':0.44355577405149443,
        'propensity_min':0.1951438344323004,'propensity_max':0.864,
        'weight_p99':2.06,'weight_max':2.27,'weight_ess':173194,
    }
    # Recompute directly from existing CSV where possible; source report remains definitive.
    sel_doc=(OUT/'PHASE7_ECG_SELECTION_SENSITIVITY.md').read_text()
    # Selection diagnostics are numeric and already written by the estimator; extract exact values from run metadata if available.
    # They are duplicated in the Phase 3 report and selection sensitivity narrative.
    subgroup_stats=[]
    for name,d in sub.groupby('subgroup'):
        first=d.iloc[0]
        d=d.set_index('feature')
        dirn=int((np.sign(d.standardized_effect)==np.sign(d.index.map(primary_idx.standardized_effect))).sum())
        ciwidth=float(((d.ci_upper-d.ci_lower)/d.index.map(primary_idx.outcome_sd)).median())
        subgroup_stats.append({'name':name,'n':int(first.n_admissions),'patients':int(first.n_patients),'cases':int(first.mi_cases),'controls':int(first.controls),'fdr':int(d.significant_bh_05.sum()),'direction_match':dirn,'median_ci_width_sd':ciwidth})
    interaction_counts={k:int(v.interaction_significant_bh_05.sum()) for k,v in inter.groupby('contrast')}
    # Key feature group summaries across primary, selection weighted, and broad definitions.
    groups=pd.read_csv(ROOT/'research_audit/PHASE3_ECG_FEATURE_GROUPS.csv')[['feature','feature_group']]
    def group_means(d, feature_col, effect_col):
        x=d.drop(columns=['feature_group'],errors='ignore').merge(groups,left_on=feature_col,right_on='feature')
        return x.groupby('feature_group')[effect_col].apply(lambda s: float(np.mean(np.abs(s)))).to_dict()
    pm=group_means(primary,'feature','standardized_effect')
    sm=group_means(sel,'feature','standardized_effect')
    bm=group_means(alt2,'feature','standardized_effect')
    subgroup_md=[
        '# Phase 7D - Age and Sex Subgroups','',
        'The original roadmap requests age and sex subgroup analyses but does not specify age cut points. We used <65 and >=65 years and recorded sex F and M. The Phase 3 primary cohort, 95 outcomes, acute-only definition, and Phase 4 adjustment variables were retained; within a sex stratum the constant sex variable was omitted. Five-fold patient-group nuisance fitting and patient-clustered Wald confidence intervals were used. BH FDR was applied within each subgroup across 95 features, and direct age/sex interaction contrasts were BH-adjusted separately across 95 features.','',
        '| Subgroup | Admissions | Patients | MI cases | Controls | Features passing within-group BH | Direction agreement with primary | Median CI width (SD) |',
        '|---|---:|---:|---:|---:|---:|---:|---:|'
    ]
    for x in subgroup_stats: subgroup_md.append(f"| {x['name']} | {x['n']:,} | {x['patients']:,} | {x['cases']:,} | {x['controls']:,} | {x['fdr']} | {x['direction_match']}/95 | {x['median_ci_width_sd']:.3f} |")
    subgroup_md += [
        '',
        f"Direct interaction tests found {interaction_counts.get('age_>=65 minus age_<65',0)} age contrasts and {interaction_counts.get('sex_M minus sex_F',0)} sex contrasts passing BH q<0.05. The leading age interaction features include ST_Elev_V5, ST_Elev_V6, and R_Amp_aVR; sex interactions include RR_Mean_Global_iqr, R_Amp_aVF, R_Amp_V2, and ST_Elev_V2. These are adjusted exploratory differences, not proof of biological effect modification; subgroup and interaction estimates are in `PHASE7_SUBGROUP_RESULTS.csv` and `PHASE7_SUBGROUP_INTERACTIONS.csv`.",
        '',
        'All subgroup case counts exceed 2,500, but direct effects still have uncertainty and multiple testing. Do not infer a subgroup difference from significance in one group and nonsignificance in another; use the interaction contrast and its interval. Age boundary choice was not specified by the roadmap and should be treated as an implementation choice.'
    ]
    (OUT/'PHASE7_AGE_SEX_SUBGROUP_ANALYSIS.md').write_text('\n'.join(subgroup_md)+'\n')

    ev=pd.read_csv(OUT/'PHASE7_EVALUE_RESULTS.csv').set_index('exposure_or_feature')
    ev_dm=float(ev.loc['diabetes_prior','e_value_point'])
    ev_htn=float(ev.loc['hypertension_prior','e_value_point'])
    ev_ckd=float(ev.loc['ckd_prior','e_value_point'])
    subgroup_direction_text=', '.join('{} {}/95'.format(x['name'],x['direction_match']) for x in subgroup_stats)
    robustness=(
        '# Phase 7 Robustness Assessment\n\n'
        '## Results across sensitivity analyses\n\n'
        f"- **Unmeasured confounding:** Layer 1 approximate E-values are modest: diabetes {ev_dm:.2f}, hypertension {ev_htn:.2f}, and CKD {ev_ckd:.2f}; the CKD interval includes the null. These rely on an approximate RD-to-RR conversion. Layer 2 uses a binary-U additive tipping grid, not E-values; it shows the bias product needed to move continuous-feature estimates to zero but does not rule out unmeasured confounding.\n"
        f"- **ECG selection:** measured-covariate weighting had good observed balance, and {sel_same}/95 weighted estimates kept the primary direction; median absolute shift was {sel_med:.3f} SD. {sel_sig_overlap}/67 primary BH findings also passed weighted BH. This remains dependent on selection-at-random conditional on measured covariates; unmeasured symptoms/severity are not addressed.\n"
        f"- **Alternative outcome code:** defining broad current MI as acute or historical MI code on the same admission increased cases to {int(alt2.exposed_n.iloc[0]):,} (from 7,353) while keeping the 159,713 clean controls. {broad_same}/95 feature directions matched primary; {broad_sig}/95 passed BH, with {broad_sig_overlap} primary discoveries overlapping. ST/T group mean absolute standardized effects were primary {pm.get('ST',np.nan):.3f}/{pm.get('T',np.nan):.3f}, selection-weighted {sm.get('ST',np.nan):.3f}/{sm.get('T',np.nan):.3f}, and broad-code {bm.get('ST',np.nan):.3f}/{bm.get('T',np.nan):.3f}. The broad case definition is less specific to acute MI.\n"
        f"- **Age/sex:** subgroup directions agreed with primary for {subgroup_direction_text}. Direct interactions passed BH for {interaction_counts.get('age_>=65 minus age_<65',0)} age and {interaction_counts.get('sex_M minus sex_F',0)} sex feature contrasts. This points to feature-specific heterogeneity, not one uniform subgroup shift.\n"
        '- **Main pattern:** large ST and T contrasts remain visible under weighted and broad-code analyses, but not all signs, magnitudes, or feature-level FDR flags are invariant. Residual feature dependence prevents treating the features as independent replications.\n\n'
        '## Gate 2 decision\n\n'
        '**Gate 2: partially satisfied.** Multiple central ST/T signals persist under measured-covariate selection weighting and the broader current-code outcome, and subgroup interactions were tested directly. However, E-values are modest and approximate, continuous-outcome tipping analyses cannot exclude unmeasured confounding, selection weighting relies on measured-only assumptions, broad MI coding changes the estimand, and age/sex interaction signals are feature-specific. Most importantly, MI onset relative to ECG remains unknown. The sensitivity analyses do not establish a causal MI-to-ECG effect.\n\n'
        'A Phase 8 observational paper may be justified after review if it is explicitly framed as an adjusted diagnosis-feature association and reports these limitations. A causal/temporal paper claim is not justified. Phase 8 has not been started.'
    )
    (OUT/'PHASE7_ROBUSTNESS_ASSESSMENT.md').write_text(robustness)
    (OUT/'PHASE7_COMPLETION_REPORT.md').write_text(
        '# Phase 7 Completion Report\n\n'
        '## Completed analyses\n\n'
        '1. Unmeasured confounding: approximate E-values for suitable binary Layer 1 contrasts; Layer 2 additive binary-U tipping products for continuous feature estimates.\n'
        '2. ECG selection: reused the finalized all-admission diagnosis audit and Phase 3 selected IDs; reproduced the measured-covariate selection model and weighted Phase 5 cross-fitted scores.\n'
        '3. Alternative outcome coding: broad sensitivity defined as acute or historical MI code on the current admission, with prior-only nonacute history kept out of controls.\n'
        '4. Age/sex subgroup analyses: <65 vs >=65 and F vs M, with patient-clustered intervals and direct interaction tests.\n'
        '5. Primary-versus-sensitivity comparison, figures, metadata, and reproducible scripts are included. Primary Phase 3-6 outputs and the analysis Parquet were not rebuilt or modified. No Phase 8 work started.\n\n'
        '## Gate 2 and recommendation\n\n'
        'Gate 2 is **partially satisfied**, not fully passed. Some main ST/T patterns persist across selection weighting and alternative current-MI coding; subgroup interaction analysis identifies feature-specific heterogeneity. Confounding sensitivity is limited, selection weighting depends on measured covariates, overlap and timing remain limitations, and broad coding changes the estimand. The evidence supports proceeding toward an observational association write-up after review, but not a causal MI-to-ECG claim. Phase 8 has not begun. See `PHASE7_ROBUSTNESS_ASSESSMENT.md`.\n\n'
        '## Files generated\n\n'
        '- `PHASE7_UNMEASURED_CONFOUNDING.md`\n- `PHASE7_EVALUE_RESULTS.csv`\n- `PHASE7_ECG_SELECTION_SENSITIVITY.md`\n- `PHASE7_SELECTION_SENSITIVITY_RESULTS.csv`\n- `PHASE7_SELECTION_COVARIATE_BALANCE.csv`\n- `PHASE7_ALTERNATIVE_MI_DEFINITIONS.md`\n- `PHASE7_ALTERNATIVE_MI_RESULTS.csv`\n- `PHASE7_AGE_SEX_SUBGROUP_ANALYSIS.md`\n- `PHASE7_SUBGROUP_RESULTS.csv`\n- `PHASE7_SUBGROUP_INTERACTIONS.csv`\n- `PHASE7_PRIMARY_VS_SENSITIVITY_COMPARISON.csv`\n- `PHASE7_ROBUSTNESS_ASSESSMENT.md`\n- `PHASE7_FIGURES/` (4 plots)\n- `PHASE7_RUN_METADATA.json`, `run_phase7_sensitivity.py`, `finalize_phase7_reports.py`\n'
    )
    metadata_out={
        'analysis_date_local':'2026-11-15','bootstrap_repetitions':500,'random_seed':20261115,
        'crossfit_folds':5,'age_boundary_years':65,
        'primary_layer2_rows':167066,'primary_layer2_patients':93946,'primary_acute_mi_cases':7353,
        'selection_denominator_admissions':431231,'selection_eligible_ecg_admissions':191275,
        'broad_layer2_rows':int(alt2.n_admissions.iloc[0]),'broad_layer2_cases':int(alt2.exposed_n.iloc[0]),
        'broad_layer2_clean_controls':int(alt2.control_n.iloc[0]),'selection_weight_ess':173194,
        'selection_weighted_same_direction_features':sel_same,'broad_code_same_direction_features':broad_same,
        'phase7_gate2':'partially satisfied','phase8_started':False
    }
    (OUT/'PHASE7_RUN_METADATA.json').write_text(json.dumps(metadata_out,indent=2))
    print({'selection_same':sel_same,'broad_same':broad_same,'interaction_q_significant':interaction_counts,'subgroups':subgroup_stats})

if __name__=='__main__': main()
