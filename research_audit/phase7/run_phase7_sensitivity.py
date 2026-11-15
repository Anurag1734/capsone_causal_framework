"""Phase 7 sensitivity analyses using finalized Phase 3-6 artifacts.

Only the nuisance scores needed for new prespecified sensitivity estimands are
recomputed. The Phase 3 cohort and Phase 5 primary estimates are never rebuilt.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research_audit/phase7'; FIG=OUT/'PHASE7_FIGURES'
DATA=ROOT/'data/analysis/observational_mi_ecg/analysis_dataset.parquet'
sys.path.insert(0,str(ROOT/'research_audit/phase5'))
import run_phase5_estimation as p5
BOOT=500; SEED=20261115
FEATURES=pd.read_csv(ROOT/'research_audit/PHASE3_ECG_FEATURE_GROUPS.csv')
FEATURES_LIST=FEATURES.feature.tolist()
L1_MAP=p5.EXPOSURE_MAP
L2_COV=['age_years','sex','diabetes_prior','hypertension_prior','ckd_prior','prior_mi']

def bh(p): return p5.bh(np.asarray(p,float))

def generic_oof_continuous(df, feature_cols, treatment, covars, prop_df, outcome_df):
    t=df[treatment].to_numpy(int); y=df[feature_cols].to_numpy(float); fold=df.crossfit_fold.to_numpy(int)
    e=np.empty(len(df)); m0=np.empty_like(y); m1=np.empty_like(y)
    for f in range(p5.FOLDS):
        tr,te=fold!=f,fold==f
        xtr,xte=p5.design_pair(df.loc[tr],df.loc[te],covars,prop_df)
        otr,ote=p5.design_pair(df.loc[tr],df.loc[te],covars,outcome_df)
        tt,yy=t[tr],y[tr]
        e[te]=p5.pred_prob(p5.logit_model(xtr,tt),xte)
        for a,target in ((0,m0),(1,m1)):
            arm=tt==a
            beta=np.linalg.lstsq(otr[arm],yy[arm],rcond=None)[0]
            target[te]=ote@beta
    psi=m1-m0+t[:,None]*(y-m1)/e[:,None]-(1-t[:,None])*(y-m0)/(1-e[:,None])
    return psi,t,y,e

def cluster_inference(scores, patient_ids, weights=None):
    if scores.ndim==1: scores=scores[:,None]
    n,k=scores.shape
    w=np.ones(n) if weights is None else np.asarray(weights,float)
    totalw=w.sum(); q=scores*w[:,None]
    uniq,inv=np.unique(patient_ids,return_inverse=True)
    sums=np.zeros((len(uniq),k)); ws=np.bincount(inv,weights=w,minlength=len(uniq))
    np.add.at(sums,inv,q)
    theta=q.sum(axis=0)/totalw
    centered=sums-ws[:,None]*theta
    cov=(len(uniq)/(len(uniq)-1))*(centered.T@centered)/(totalw**2)
    se=np.sqrt(np.maximum(np.diag(cov),0)); z=np.divide(theta,se,out=np.zeros_like(theta),where=se>0)
    return theta,se,2*norm.sf(abs(z)),cov

def cluster_bootstrap(scores, patient_ids, weights=None, reps=BOOT, seed=SEED):
    if scores.ndim==1: scores=scores[:,None]
    n,k=scores.shape; w=np.ones(n) if weights is None else np.asarray(weights,float)
    uniq,inv=np.unique(patient_ids,return_inverse=True); g=len(uniq)
    sums=np.zeros((g,k)); wsum=np.bincount(inv,weights=w,minlength=g)
    np.add.at(sums,inv,scores*w[:,None])
    rng=np.random.default_rng(seed); draws=np.empty((reps,k))
    for b in range(reps):
        m=np.bincount(rng.integers(0,g,size=g),minlength=g)
        draws[b]=(m@sums)/(m@wsum)
    return np.quantile(draws,[.025,.975],axis=0).T

def weighted_crude_ci(y,t,weights,patients,reps=BOOT,seed=SEED):
    y=y if y.ndim==2 else y[:,None]; n,k=y.shape
    uniq,inv=np.unique(patients,return_inverse=True); g=len(uniq)
    w1=weights*t; w0=weights*(1-t)
    sy1=np.zeros((g,k)); sy0=np.zeros((g,k)); sw1=np.bincount(inv,weights=w1,minlength=g); sw0=np.bincount(inv,weights=w0,minlength=g)
    np.add.at(sy1,inv,y*w1[:,None]); np.add.at(sy0,inv,y*w0[:,None])
    rng=np.random.default_rng(seed); draws=np.empty((reps,k))
    for b in range(reps):
        m=np.bincount(rng.integers(0,g,size=g),minlength=g)
        draws[b]=(m@sy1)/(m@sw1)-(m@sy0)/(m@sw0)
    return np.quantile(draws,[.025,.975],axis=0).T

def records_from_dr(df, feature_cols, treatment, scores, y, t, weights=None, seed=SEED):
    theta,se,p,_=cluster_inference(scores,df.patient_id.to_numpy(),weights)
    ci=cluster_bootstrap(scores,df.patient_id.to_numpy(),weights,seed=seed)
    if y.ndim==1: y=y[:,None]
    if weights is None: weights=np.ones(len(df))
    cr=[]; crse=[]; crp=[]
    for j in range(y.shape[1]):
        mu1=np.average(y[t==1,j],weights=weights[t==1]); mu0=np.average(y[t==0,j],weights=weights[t==0])
        est=mu1-mu0
        infl=est+t*(y[:,j]-mu1)/np.average(t,weights=weights)-(1-t)*(y[:,j]-mu0)/(1-np.average(t,weights=weights))
        _,s,pp,_=cluster_inference(infl[:,None],df.patient_id.to_numpy(),weights)
        cr.append(est); crse.append(s[0]); crp.append(pp[0])
    cci=weighted_crude_ci(y,t,weights,df.patient_id.to_numpy(),seed=seed+1)
    sd=y.std(axis=0,ddof=1)
    return pd.DataFrame({'feature':feature_cols,'n_admissions':len(df),'n_patients':df.patient_id.nunique(),'exposed_n':int(t.sum()),'control_n':int((1-t).sum()),'missing_n':df[feature_cols].isna().sum().to_numpy(),'crude_effect':cr,'crude_ci_lower':cci[:,0],'crude_ci_upper':cci[:,1],'crude_cluster_se':crse,'crude_p_value':crp,'adjusted_effect':theta,'ci_lower':ci[:,0],'ci_upper':ci[:,1],'cluster_robust_se':se,'p_value':p,'outcome_sd':sd,'standardized_effect':theta/sd})

def build_selection_weights(data):
    audit_path=ROOT/'research_audit/ACUTE_MI_DIAGNOSIS_BY_ADMISSION.csv'
    cols=['subject_id','hadm_id','acute_mi_this_admission','historical_mi_code_this_admission','prior_mi_documentation','prior_diabetes_code','prior_hypertension_code','prior_ckd_code']
    audit=pd.read_csv(audit_path,usecols=cols)
    demo=pd.read_parquet(ROOT/'data/raw/longitudinal/patients_demographics.parquet',columns=['subject_id','gender','anchor_age'])
    adm=audit.merge(demo,on='subject_id',how='left',validate='many_to_one')
    adm=adm[adm.anchor_age.ge(18)].copy()
    selected_ids=set(data.admission_id.to_numpy())
    adm['has_eligible_ecg']=adm.hadm_id.isin(selected_ids).astype(int)
    gender=adm.gender.astype('string').str.upper()
    x=pd.DataFrame(index=adm.index)
    x['age_years']=adm.anchor_age.astype(float)
    x['sex_female']=gender.eq('F').astype(int); x['sex_male']=gender.eq('M').astype(int); x['sex_missing_or_other']=(~gender.isin(['F','M'])).astype(int)
    mapping={'acute_mi_this_admission':'acute_mi_diagnosis','historical_mi_code_this_admission':'historical_mi_this_admission','prior_mi_documentation':'prior_mi','prior_diabetes_code':'diabetes_prior','prior_hypertension_code':'hypertension_prior','prior_ckd_code':'ckd_prior'}
    for source,target in mapping.items(): x[target]=adm[source].fillna(False).astype(int)
    sel=LogisticRegression(max_iter=1000,solver='lbfgs')
    sel.fit(x,adm.has_eligible_ecg)
    adm['selection_propensity']=sel.predict_proba(x)[:,1]
    rate=adm.has_eligible_ecg.mean(); adm['stabilized_selection_weight']=rate/adm.selection_propensity
    chosen=adm[adm.has_eligible_ecg==1]
    weight_map=chosen.set_index('hadm_id').stabilized_selection_weight
    selected=data.copy(); selected['selection_weight']=selected.admission_id.map(weight_map)
    if selected.selection_weight.isna().any(): raise ValueError('Selected admission missing selection weight')
    def smd(a,b):
        pooled=np.sqrt((np.var(a,ddof=1)+np.var(b,ddof=1))/2)
        return (np.mean(a)-np.mean(b))/pooled if pooled else 0
    cal=[]
    for name,values in [('age',adm.anchor_age),('female',gender.eq('F').astype(float)),('acute_mi',x.acute_mi_diagnosis),('historical_mi_this_admission',x.historical_mi_this_admission),('diabetes',x.diabetes_prior),('hypertension',x.hypertension_prior),('ckd',x.ckd_prior),('prior_mi',x.prior_mi)]:
        v=values.loc[chosen.index].to_numpy(float); w=chosen.stabilized_selection_weight.to_numpy()
        meanw=np.average(v,weights=w); varw=np.average((v-meanw)**2,weights=w)
        s=np.sqrt((varw+np.var(values.to_numpy(float),ddof=1))/2)
        cal.append({'variable':name,'selected_unweighted_mean':float(v.mean()),'all_admission_mean':float(values.mean()),'selected_weighted_mean':float(meanw),'unweighted_smd':float(smd(v,values.to_numpy(float))),'weighted_smd':float((meanw-values.mean())/s if s else 0)})
    diag={'denominator_n':len(adm),'selected_n':len(chosen),'selection_rate':rate,'propensity_min':float(adm.selection_propensity.min()),'propensity_p01':float(adm.selection_propensity.quantile(.01)),'propensity_median':float(adm.selection_propensity.median()),'propensity_p99':float(adm.selection_propensity.quantile(.99)),'propensity_max':float(adm.selection_propensity.max()),'weight_min':float(chosen.stabilized_selection_weight.min()),'weight_p99':float(chosen.stabilized_selection_weight.quantile(.99)),'weight_max':float(chosen.stabilized_selection_weight.max()),'weight_ess':float(chosen.stabilized_selection_weight.sum()**2/(chosen.stabilized_selection_weight.pow(2).sum()))}
    return selected,diag,pd.DataFrame(cal)

def evalue(rr):
    rr=float(rr)
    if not np.isfinite(rr) or rr<=0: return np.nan
    r=max(rr,1/rr)
    return r+np.sqrt(r*(r-1)) if r>=1 else 1.0

def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    data=pd.read_parquet(DATA)
    features=FEATURES_LIST
    folds=pd.read_csv(p5.OUT/'PHASE5_CROSSFIT_FOLD_ASSIGNMENTS.csv')[['patient_id','crossfit_fold']]
    data=data.merge(folds,on='patient_id',validate='many_to_one')
    prim=data[data.primary_analysis_eligible].copy()
    primary_l1=pd.read_csv(p5.OUT/'PHASE5_LAYER1_EFFECT_ESTIMATES.csv')
    primary_l2=pd.read_csv(p5.OUT/'PHASE5_LAYER2_FDR_RESULTS.csv')
    primary_groups=pd.read_csv(p5.OUT/'PHASE5_FEATURE_GROUP_RESULTS.csv')
    tune=pd.read_csv(p5.OUT/'PHASE5_VALIDATION_MODEL_SELECTION.csv').set_index('analysis')
    prop_df=int(tune.loc['layer2_propensity','propensity_age_spline_df']); out_df=int(tune.loc['layer2_outcome','outcome_age_spline_df'])
    # 7A: E-values for binary Layer 1 only; additive omitted-confounder tipping products for continuous Layer 2.
    e_rows=[]
    for _,r in primary_l1.iterrows():
        sub=data[data[r.exposure]==0]; p0=float(sub.acute_mi_diagnosis.mean()); rd=float(r.adjusted_risk_difference)
        rr=1+rd/p0 if p0>0 else np.nan
        lrr=1+float(r.adjusted_ci_lower)/p0; urr=1+float(r.adjusted_ci_upper)/p0
        eci=1.0 if lrr<=1<=urr else evalue(lrr if rr>1 else urr)
        applicable=r.exposure!='prior_mi'
        e_rows.append({'layer':'Layer 1','exposure_or_feature':r.exposure,'feature_group':'','estimate_risk_difference':rd,'ci_lower':r.adjusted_ci_lower,'ci_upper':r.adjusted_ci_upper,'baseline_unexposed_risk':p0,'converted_risk_ratio_approx':rr if applicable else np.nan,'e_value_point':evalue(rr) if applicable else np.nan,'e_value_ci_nearest_null':eci if applicable else np.nan,'evalue_applicable':applicable,'interpretation':'Approximate RD-to-RR conversion using observed unexposed risk; prior MI is descriptive and no causal E-value is interpreted.' if applicable else 'Prior MI is descriptive by roadmap; E-value causal interpretation not applied.'})
    for _,r in primary_l2.iterrows():
        d=abs(float(r.standardized_effect)); lo=float(r.ci_lower/r.outcome_sd); hi=float(r.ci_upper/r.outcome_sd)
        to_null=0.0 if lo<=0<=hi else min(abs(lo),abs(hi))
        e_rows.append({'layer':'Layer 2','exposure_or_feature':r.feature,'feature_group':r.feature_group,'estimate_standardized_mean_difference':r.standardized_effect,'ci_lower_standardized':lo,'ci_upper_standardized':hi,'e_value_point':np.nan,'e_value_ci_nearest_null':np.nan,'evalue_applicable':False,'continuous_outcome_bias_to_null_sd':d,'ci_bias_to_include_null_sd':to_null,'required_U_outcome_SD_for_10pp_MI_imbalance':d/.10,'required_U_outcome_SD_for_20pp_MI_imbalance':d/.20,'required_U_outcome_SD_for_50pp_MI_imbalance':d/.50,'required_U_outcome_SD_for_20pp_imbalance_to_move_CI_to_null':to_null/.20,'interpretation':'E-values do not directly apply to continuous feature mean differences. Product tipping calculation assumes a binary unmeasured factor U; confounding bias = conditional MI-group prevalence difference in U times U-associated feature shift (SD units).'})
    ev=pd.DataFrame(e_rows); ev.to_csv(OUT/'PHASE7_EVALUE_RESULTS.csv',index=False)

    # 7B: reproduce Phase 3 admission-level selection score from existing corrected audit,
    # then transport Phase 5 AIPW scores with stabilized inverse-selection weights.
    weighted_data,selection_diag,calibration=build_selection_weights(data)
    wprim=weighted_data[weighted_data.primary_analysis_eligible].copy()
    psi_sel,t_sel,y_sel,e_sel=generic_oof_continuous(wprim,features,'acute_mi_diagnosis',L2_COV,prop_df,out_df)
    wt=wprim.selection_weight.to_numpy()
    sel_results=records_from_dr(wprim,features,'acute_mi_diagnosis',psi_sel,y_sel,t_sel,weights=wt,seed=SEED+700)
    sel_results['feature_group']=FEATURES.set_index('feature').loc[sel_results.feature,'feature_group'].to_numpy()
    sel_results=sel_results.merge(primary_l2[['feature','adjusted_effect','ci_lower','ci_upper','p_value','q_value','significant_bh_fdr_05']],on='feature',suffixes=('_selection_weighted','_primary'))
    sel_results['weighted_direction_matches_primary']=np.sign(sel_results.adjusted_effect_selection_weighted)==np.sign(sel_results.adjusted_effect_primary)
    sel_results['weighted_abs_effect_change_sd']=(sel_results.adjusted_effect_selection_weighted-sel_results.adjusted_effect_primary)/sel_results.outcome_sd
    sel_results['weighted_q_value']=bh(sel_results.p_value_selection_weighted)
    sel_results['weighted_significant_bh_05']=sel_results.weighted_q_value<.05
    sel_results['selection_rate']=selection_diag['selection_rate']; sel_results['weight_ess']=selection_diag['weight_ess']
    sel_results.to_csv(OUT/'PHASE7_SELECTION_SENSITIVITY_RESULTS.csv',index=False)
    calibration.to_csv(OUT/'PHASE7_SELECTION_COVARIATE_BALANCE.csv',index=False)

    # 7C: broad current-admission MI codes = acute codes OR historical MI code on this admission.
    # Historical/prior-only nonacute admissions remain outside the case/control contrast.
    data['broad_mi_current']=data.acute_mi_diagnosis.astype(bool)|data.historical_mi_this_admission.astype(bool)
    clean=(data.primary_analysis_eligible)&(~data.acute_mi_diagnosis.astype(bool))
    broad_case=data.broad_mi_current.astype(bool)
    broad_l2=data[broad_case|clean].copy()
    psi_b,t_b,y_b,e_b=generic_oof_continuous(broad_l2,features,'broad_mi_current',L2_COV,prop_df,out_df)
    broad2=records_from_dr(broad_l2,features,'broad_mi_current',psi_b,y_b,t_b,seed=SEED+800)
    broad2['layer']='Layer 2'; broad2['definition']='Broad current MI: acute OR historical MI code on this admission'
    broad2['feature_group']=FEATURES.set_index('feature').loc[broad2.feature,'feature_group'].to_numpy()
    broad2['q_value']=bh(broad2.p_value); broad2['significant_bh_fdr_05']=broad2.q_value<.05
    l1b=[]
    for ix,(ex,covars) in enumerate(L1_MAP.items()):
        kprop=int(tune.loc[ex,'propensity_age_spline_df']); kout=int(tune.loc[ex,'outcome_age_spline_df'])
        psi,t,y,diag=p5.oof_binary_dr(data,ex,'broad_mi_current',covars,kprop,kout,data.crossfit_fold.to_numpy(int))
        theta,se,pv,_=p5.infer(psi[:,None],data.patient_id.to_numpy())
        ci=p5.bootstrap_ate(y,t,psi,data.patient_id.to_numpy(),reps=BOOT,seed=SEED+810+ix)[1]
        l1b.append({'layer':'Layer 1','exposure':ex,'feature':'','definition':'Broad current MI: acute OR historical MI code on this admission','n_admissions':len(data),'n_patients':data.patient_id.nunique(),'exposed_n':int(t.sum()),'control_n':int((1-t).sum()),'outcome_prevalence':float(y.mean()),'adjusted_effect':theta[0],'ci_lower':ci[0,0],'ci_upper':ci[0,1],'cluster_robust_se':se[0],'p_value':pv[0],'q_value':np.nan,'significant_bh_fdr_05':False})
    broad1=pd.DataFrame(l1b)
    alt2=broad2.rename(columns={'adjusted_effect':'adjusted_effect','ci_lower':'ci_lower','ci_upper':'ci_upper'})
    broad2['exposure']='broad_mi_current'
    alt=pd.concat([broad1, broad2],ignore_index=True,sort=False)
    alt.to_csv(OUT/'PHASE7_ALTERNATIVE_MI_RESULTS.csv',index=False)

    # 7D: age <65 / >=65 and recorded sex F/M. Age cut point is an implementation choice;
    # the original roadmap specified age/sex subgroups but no age boundary.
    subgroup_defs={
        'age_<65':(prim.age_years<65,['age_years','sex','diabetes_prior','hypertension_prior','ckd_prior','prior_mi']),
        'age_>=65':(prim.age_years>=65,['age_years','sex','diabetes_prior','hypertension_prior','ckd_prior','prior_mi']),
        'sex_F':(prim.sex=='F',['age_years','diabetes_prior','hypertension_prior','ckd_prior','prior_mi']),
        'sex_M':(prim.sex=='M',['age_years','diabetes_prior','hypertension_prior','ckd_prior','prior_mi']),
    }
    sub_records=[]; sub_scores={}; sub_meta={}
    for ix,(label,(mask,covars)) in enumerate(subgroup_defs.items()):
        sub=prim.loc[mask].copy()
        psi,t,y,e=generic_oof_continuous(sub,features,'acute_mi_diagnosis',covars,prop_df,out_df)
        theta,se,pv,_=p5.infer(psi,sub.patient_id.to_numpy())
        q=bh(pv); sd=y.std(axis=0,ddof=1)
        for j,feat in enumerate(features):
            sub_records.append({'subgroup':label,'feature':feat,'feature_group':FEATURES.set_index('feature').loc[feat,'feature_group'],'n_admissions':len(sub),'n_patients':sub.patient_id.nunique(),'mi_cases':int(t.sum()),'controls':int((1-t).sum()),'exposed_prevalence':float(t.mean()),'adjusted_effect':theta[j],'ci_lower':theta[j]-1.96*se[j],'ci_upper':theta[j]+1.96*se[j],'cluster_robust_se':se[j],'p_value':pv[j],'q_value_bh_within_subgroup':q[j],'significant_bh_05':q[j]<.05,'low_case_count':int(t.sum())<100,'standardized_effect':theta[j]/sd[j]})
        sub_scores[label]=(sub,psi,theta)
        sub_meta[label]={'n':len(sub),'patients':sub.patient_id.nunique(),'cases':int(t.sum()),'controls':int((1-t).sum())}
    subgroup=pd.DataFrame(sub_records)
    # Interaction / difference-in-subgroup-estimates tests with patient-clustered influence variance.
    interactions=[]
    for comp,a,b in [('age_>=65 minus age_<65','age_>=65','age_<65'),('sex_M minus sex_F','sex_M','sex_F')]:
        da,sa,ta=sub_scores[a]; db,sb,tb=sub_scores[b]
        delta=ta-tb
        pats=np.union1d(da.patient_id.to_numpy(),db.patient_id.to_numpy()); invmap={v:i for i,v in enumerate(pats)}
        ia=np.array([invmap[x] for x in da.patient_id]); ib=np.array([invmap[x] for x in db.patient_id])
        inf=np.zeros((len(pats),len(features)))
        np.add.at(inf,ia,(sa-ta)/len(da)); np.add.at(inf,ib,-(sb-tb)/len(db))
        se=np.sqrt((len(pats)/(len(pats)-1))*np.sum(inf**2,axis=0)); pv=2*norm.sf(np.divide(abs(delta),se,out=np.zeros_like(se),where=se>0)); q=bh(pv)
        for j,feat in enumerate(features): interactions.append({'contrast':comp,'feature':feat,'feature_group':FEATURES.set_index('feature').loc[feat,'feature_group'],'n_patients_union':len(pats),'estimate_difference':delta[j],'ci_lower':delta[j]-1.96*se[j],'ci_upper':delta[j]+1.96*se[j],'cluster_robust_se':se[j],'interaction_p_value':pv[j],'interaction_q_value_bh':q[j],'interaction_significant_bh_05':q[j]<.05})
    subgroup.to_csv(OUT/'PHASE7_SUBGROUP_RESULTS.csv',index=False)
    interaction_df=pd.DataFrame(interactions); interaction_df.to_csv(OUT/'PHASE7_SUBGROUP_INTERACTIONS.csv',index=False)

    # Consolidated long-form reference versus sensitivity table.
    compare=[]
    for _,r in primary_l1.iterrows():
        compare.append({'layer':'Layer 1','sensitivity':'primary acute MI definition','subgroup':'','feature':'','estimate':r.adjusted_risk_difference,'ci_lower':r.adjusted_ci_lower,'ci_upper':r.adjusted_ci_upper,'primary_estimate':r.adjusted_risk_difference,'primary_ci_lower':r.adjusted_ci_lower,'primary_ci_upper':r.adjusted_ci_upper,'direction_matches_primary':True,'p_value':r.adjusted_p_value})
    for _,r in primary_l2.iterrows():
        compare.append({'layer':'Layer 2','sensitivity':'primary acute MI definition','subgroup':'','feature':r.feature,'feature_group':r.feature_group,'estimate':r.adjusted_effect,'ci_lower':r.ci_lower,'ci_upper':r.ci_upper,'primary_estimate':r.adjusted_effect,'primary_ci_lower':r.ci_lower,'primary_ci_upper':r.ci_upper,'direction_matches_primary':True,'p_value':r.p_value,'q_value':r.q_value})
    for _,r in alt.iterrows():
        if r.layer=='Layer 1':
            pr=primary_l1.loc[primary_l1.exposure==r.exposure].iloc[0]; feat=''
        else:
            pr=primary_l2.loc[primary_l2.feature==r.feature].iloc[0]; feat=r.feature
        compare.append({'layer':r.layer,'sensitivity':'broad current MI codes','subgroup':'','feature':feat,'estimate':r.adjusted_effect,'ci_lower':r.ci_lower,'ci_upper':r.ci_upper,'primary_estimate':pr.adjusted_risk_difference if r.layer=='Layer 1' else pr.adjusted_effect,'primary_ci_lower':pr.adjusted_ci_lower if r.layer=='Layer 1' else pr.ci_lower,'primary_ci_upper':pr.adjusted_ci_upper if r.layer=='Layer 1' else pr.ci_upper,'direction_matches_primary':np.sign(r.adjusted_effect)==np.sign(pr.adjusted_risk_difference if r.layer=='Layer 1' else pr.adjusted_effect),'p_value':r.p_value,'q_value':r.q_value if r.layer=='Layer 2' else np.nan})
    for _,r in sel_results.iterrows():
        pr=primary_l2.loc[primary_l2.feature==r.feature].iloc[0]
        compare.append({'layer':'Layer 2','sensitivity':'inverse-probability ECG selection weighting','subgroup':'','feature':r.feature,'feature_group':r.feature_group,'estimate':r.adjusted_effect_selection_weighted,'ci_lower':r.ci_lower_selection_weighted,'ci_upper':r.ci_upper_selection_weighted,'primary_estimate':pr.adjusted_effect,'primary_ci_lower':pr.ci_lower,'primary_ci_upper':pr.ci_upper,'direction_matches_primary':r.weighted_direction_matches_primary,'p_value':r.p_value_selection_weighted,'q_value':r.weighted_q_value})
    for _,r in subgroup.iterrows():
        pr=primary_l2.loc[primary_l2.feature==r.feature].iloc[0]
        compare.append({'layer':'Layer 2','sensitivity':'subgroup estimate','subgroup':r.subgroup,'feature':r.feature,'feature_group':r.feature_group,'estimate':r.adjusted_effect,'ci_lower':r.ci_lower,'ci_upper':r.ci_upper,'primary_estimate':pr.adjusted_effect,'primary_ci_lower':pr.ci_lower,'primary_ci_upper':pr.ci_upper,'direction_matches_primary':np.sign(r.adjusted_effect)==np.sign(pr.adjusted_effect),'p_value':r.p_value,'q_value':r.q_value_bh_within_subgroup})
    for _,r in interaction_df.iterrows():
        compare.append({'layer':'Layer 2','sensitivity':'subgroup interaction contrast','subgroup':r.contrast,'feature':r.feature,'feature_group':r.feature_group,'estimate':r.estimate_difference,'ci_lower':r.ci_lower,'ci_upper':r.ci_upper,'p_value':r.interaction_p_value,'q_value':r.interaction_q_value_bh})
    comparison=pd.DataFrame(compare)
    comparison['standardized_difference_from_primary']=np.where((comparison.layer=='Layer 2')&comparison.feature.notna(),(comparison.estimate-comparison.primary_estimate)/comparison.merge(primary_l2[['feature','outcome_sd']],on='feature',how='left').outcome_sd, np.nan)
    comparison.to_csv(OUT/'PHASE7_PRIMARY_VS_SENSITIVITY_COMPARISON.csv',index=False)

    # Results summaries.
    sig_primary=set(primary_l2.loc[primary_l2.significant_bh_fdr_05,'feature'])
    sig_sel=set(sel_results.loc[sel_results.weighted_significant_bh_05,'feature'])
    broad_sig=set(broad2.loc[broad2.significant_bh_fdr_05,'feature'])
    overlap_sel=len(sig_primary&sig_sel); overlap_broad=len(sig_primary&broad_sig)
    sel_same=int(sel_results.weighted_direction_matches_primary.sum())
    sel_med=float(sel_results.weighted_abs_effect_change_sd.abs().median())
    alt_same=int((np.sign(broad2.adjusted_effect)==np.sign(broad2.feature.map(primary_l2.set_index('feature').adjusted_effect))).sum())
    alt_sig=len(broad_sig)
    # Figures.
    top=primary_l2[primary_l2.feature.isin(['ST_Elev_I','ST_Elev_aVR','ST_Elev_aVF','ST_Elev_V5','T_Amp_I','T_Amp_aVR','T_Amp_V5','T_Amp_V6'])].copy()
    m=top.merge(sel_results[['feature','adjusted_effect_selection_weighted','ci_lower_selection_weighted','ci_upper_selection_weighted']],on='feature')
    fig,ax=plt.subplots(figsize=(9,6)); yloc=np.arange(len(m))
    ax.scatter(m.adjusted_effect/m.outcome_sd,yloc,label='Primary Phase 5',marker='o')
    ax.scatter(m.adjusted_effect_selection_weighted/m.outcome_sd,yloc,label='Selection weighted',marker='s')
    ax.axvline(0,color='black',lw=.7); ax.set_yticks(yloc,m.feature); ax.set_xlabel('Adjusted contrast (outcome SD)'); ax.set_title('Selection-weighted sensitivity: selected ST/T features'); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'selection_weighted_key_features.png',dpi=180); plt.close(fig)
    m2=top.merge(broad2[['feature','adjusted_effect','outcome_sd']],on='feature',suffixes=('_primary','_broad'))
    fig,ax=plt.subplots(figsize=(9,6)); yloc=np.arange(len(m2))
    ax.scatter(m2.adjusted_effect_primary/m2.outcome_sd_primary,yloc,label='Acute-only primary')
    ax.scatter(m2.adjusted_effect_broad/m2.outcome_sd_broad,yloc,label='Broad current MI')
    ax.axvline(0,color='black',lw=.7); ax.set_yticks(yloc,m2.feature); ax.set_xlabel('Adjusted contrast (outcome SD)'); ax.set_title('Alternative current-admission MI definition'); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'broad_code_key_features.png',dpi=180); plt.close(fig)
    for contrast,a,b in [('Age: >=65 vs <65','age_>=65','age_<65'),('Sex: M vs F','sex_M','sex_F')]:
        aa=subgroup[subgroup.subgroup==a].set_index('feature'); bb=subgroup[subgroup.subgroup==b].set_index('feature')
        show=list(primary_l2.nlargest(12,'standardized_effect').feature)+list(primary_l2.nsmallest(12,'standardized_effect').feature)
        show=list(dict.fromkeys(show)); xx=aa.loc[show].standardized_effect; yy=bb.loc[show].standardized_effect
        fig,ax=plt.subplots(figsize=(6,6)); ax.scatter(xx,yy)
        lim=max(np.max(np.abs(np.r_[xx,yy])),.1); ax.plot([-lim,lim],[-lim,lim],ls='--',color='gray'); ax.axhline(0,color='black',lw=.5); ax.axvline(0,color='black',lw=.5)
        for feat in show[:6]: ax.annotate(feat,(aa.loc[feat].standardized_effect,bb.loc[feat].standardized_effect),fontsize=6)
        ax.set_xlabel(f'{a} (SD units)'); ax.set_ylabel(f'{b} (SD units)'); ax.set_title(contrast); fig.tight_layout(); fig.savefig(FIG/('subgroup_'+a.replace(' ','_').replace('>','gt').replace('<','lt')+'.png'),dpi=180); plt.close(fig)

    # Phase documents.
    evalue_text=(
        "# Phase 7A - Unmeasured-Confounding Sensitivity\n\n"
        "## E-values for Layer 1\n\n"
        "E-values are calculated only for the first three Layer 1 binary-exposure/binary-outcome contrasts. Adjusted risk differences are converted approximately to risk ratios using the observed acute-MI risk among unexposed admissions as the baseline risk; the Phase 5 cross-fitted standardized risk under exposure=0 was not saved. This conversion is therefore an explicit approximation, not an exact adjusted RR. Prior MI remains descriptive and receives no causal E-value interpretation. The CSV gives point E-values and the E-value for the confidence limit nearest the null. An E-value describes the minimum joint strength of association on the RR scale that an unmeasured confounder would need with exposure and outcome, conditional on measured factors, to explain away the association; it does not prove that such confounding is absent.\n\n"
        "## Continuous Layer 2 outcomes\n\n"
        "E-values are not defined for these continuous feature mean differences without an arbitrary dichotomization or another model. Instead, the CSV reports an additive omitted-binary-confounder tipping calculation for all 95 features. If U differs in prevalence between acute-MI and control admissions by Delta_U, and is associated with a feature by gamma SD units, the illustrative bias product is Delta_U x gamma. The table reports the gamma required to move each Phase 5 standardized estimate to zero at 10, 20, and 50 percentage-point U-prevalence differences; it also reports the bias needed to move the nearest confidence limit to zero. This is a transparent sensitivity scale, not an estimated confounder model.\n\n"
        "The strongest ST/T contrasts require larger bias products to reach zero than small effects, but even these can be explained by a sufficiently strong, highly imbalanced unmeasured factor. Unmeasured smoking, BMI/lipids, acute severity, and selection processes remain plausible. Unknown ECG/MI ordering is not addressed by E-values or the tipping calculation."
    )
    (OUT/'PHASE7_UNMEASURED_CONFOUNDING.md').write_text(evalue_text)
    selection_text=(
        "# Phase 7B - ECG-Selection Sensitivity\n\n"
        f"The finalized Phase 3 denominator contains {selection_diag['denominator_n']:,} adult admissions; {selection_diag['selected_n']:,} had an eligible ECG ({selection_diag['selection_rate']:.2%}). Phase 3 found selected admissions were older (SMD 0.524), more often coded acute MI (0.109), and had higher recorded comorbidity/prior-MI prevalence (SMDs 0.198-0.270 for major history flags). These are observed selection differences, not proof of bias direction.\n\n"
        "## Weighted sensitivity\n\n"
        "The existing corrected all-admission diagnosis audit and Phase 3 selected-admission IDs were reused; no ECG eligibility rules or Phase 3 dataset were rebuilt. A logistic selection model reproduced the Phase 3 predictor set: age, recorded sex, current acute MI, current historical-MI code, and prior diabetes, hypertension, CKD, and MI. Stabilized inverse-selection weights (selection rate divided by predicted selection probability) were applied to the Phase 5 cross-fitted AIPW feature scores. This changes the target toward all adult admissions under conditional exchangeability/selection-at-random assumptions. The weighted effect results are compared with Phase 5 in `PHASE7_SELECTION_SENSITIVITY_RESULTS.csv`; post-weight covariate balance is in `PHASE7_SELECTION_COVARIATE_BALANCE.csv`.\n\n"
        f"The selection model yielded propensity range {selection_diag['propensity_min']:.3f}-{selection_diag['propensity_max']:.3f}, selected-weight 99th percentile {selection_diag['weight_p99']:.2f}, maximum {selection_diag['weight_max']:.2f}, and ESS {selection_diag['weight_ess']:,.0f} of {selection_diag['selected_n']:,}. After weighting, {int(calibration.weighted_smd.abs().lt(.1).sum())}/{len(calibration)} observed covariates had |SMD|<0.10. For 95 ECG features, {sel_same}/95 weighted estimates retained the primary direction; median absolute shift was {sel_med:.3f} outcome SD. {overlap_sel}/{len(sig_primary)} primary BH-significant features also passed weighted BH FDR.\n\n"
        "## Limits\n\n"
        "This is an assumption-dependent sensitivity analysis, not a correction guaranteed to eliminate selection bias. The propensity model is fitted on recorded variables only; unmeasured severity, symptoms, care pathway, clinician ordering, outpatient history, or ECG availability mechanisms can violate conditional selection exchangeability. The selected sample has no ECG features for nonselected admissions, so transport depends entirely on measured predictors and observed support. The Phase 3 selection report's 44.36% selection rate remains the target-population limitation. No timing or causal-ordering assumption is resolved."
    )
    (OUT/'PHASE7_ECG_SELECTION_SENSITIVITY.md').write_text(selection_text)
    alt_text=(
        "# Phase 7C - Alternative MI Outcome-Code Definition\n\n"
        "The roadmap specifies acute-MI-code-only versus a broad MI-code definition but does not enumerate the broader code list. This sensitivity operationalizes broad current-admission MI using the existing finalized audit field `mi_code_this_admission`: acute ICD-9 410*/ICD-10 I21*/I22* OR historical ICD-9 412/ICD-10 I25.2 on the same admission. This is the broadest current-admission definition supported by the accepted Phase 3 flags. Historical/prior-only nonacute admissions remain outside the Layer 2 case/control contrast; clean controls remain admissions without documented current or prior MI. This choice is documented rather than silently changing the primary acute definition.\n\n"
        f"The broad Layer 2 cohort has {len(broad_l2):,} admissions ({int(t_b.sum()):,} broad current-MI cases; {int((1-t_b).sum()):,} clean controls), compared with {len(prim):,} primary admissions ({int(prim.acute_mi_diagnosis.sum()):,} acute cases). Broad-definition prevalence in this comparison is {t_b.mean():.2%}. {alt_same}/95 adjusted feature estimates retained the acute-only primary direction; {alt_sig}/95 features passed BH FDR under the broad definition versus {len(sig_primary)} physiological+technical primary significant features.\n\n"
        "Layer 1 broad-outcome contrasts use the same selected-admission population and Phase 4 exposure-specific sets, redefining the current-admission outcome as acute OR historical code; prior MI stays descriptive. Full counts, estimates, patient intervals, and feature multiplicity results are in `PHASE7_ALTERNATIVE_MI_RESULTS.csv`. The broad definition mixes acute and old-MI diagnoses and is intentionally a coding sensitivity, not a new primary clinical estimand. It does not imply event timing."
    )
    (OUT/'PHASE7_ALTERNATIVE_MI_DEFINITIONS.md').write_text(alt_text)
    age_text=(
        "# Phase 7D - Age and Sex Subgroups\n\n"
        "The roadmap requests age and sex subgroups but gives no age boundary. We prespecified <65 versus >=65 years as a conventional split and recorded sex F versus M using the finalized Phase 3 field. No rows with missing/other sex were present in the primary Phase 3 cohort. Layer 2 outcomes and acute-only definition are unchanged. Each subgroup used the same six measured covariates when estimable: age modeled flexibly, sex omitted when constant within sex strata, and prior diabetes, hypertension, CKD, and MI. Five-fold patient-group cross-fitting and patient-clustered Wald intervals were used. BH correction was applied within each subgroup across 95 features; interaction contrasts compare subgroup estimates and receive BH correction across 95 features for each age/sex contrast.\n\n"
        "| Subgroup | Admissions | Patients | Acute MI cases | Clean controls |\n|---|---:|---:|---:|---:|\n"
        + ''.join(f"| {k} | {v['n']:,} | {v['patients']:,} | {v['cases']:,} | {v['controls']:,} |\n" for k,v in sub_meta.items())
        + "\nFull adjusted effects, 95% intervals, p-values, within-subgroup q-values, and low-case flags are in `PHASE7_SUBGROUP_RESULTS.csv`; interaction contrasts are in `PHASE7_SUBGROUP_INTERACTIONS.csv`. Do not infer heterogeneity from one subgroup being significant and another not. Interpret the direct interaction estimates and intervals.\n\n"
        + f"After BH correction, {int(((interaction_df.contrast=='age_>=65 minus age_<65') & interaction_df.interaction_significant_bh_05).sum())} age-interaction features and {int(((interaction_df.contrast=='sex_M minus sex_F') & interaction_df.interaction_significant_bh_05).sum())} sex-interaction features passed q<0.05. These are exploratory multiplicity-adjusted subgroup comparisons; feature dependence and limited overlap remain."
    )
    (OUT/'PHASE7_AGE_SEX_SUBGROUP_ANALYSIS.md').write_text(age_text)

    stability_sel=sel_same/95; broad_rate=alt_same/95
    (OUT/'PHASE7_ROBUSTNESS_ASSESSMENT.md').write_text(
        "# Phase 7 Robustness Assessment\n\n"
        "## Findings across sensitivity analyses\n\n"
        f"- **Unmeasured confounding:** Layer 1 RR-scale E-values are modest and rely on approximate RD-to-RR conversion; prior MI is descriptive. Continuous Layer 2 features use additive binary-U tipping products rather than E-values. These show how strong a prevalence imbalance and feature association would need to be to explain estimates, but do not establish absence of U.\n"
        f"- **ECG selection:** IP selection weighting was possible from the Phase 3 all-admission denominator. The 44.36% selection rate and covariate imbalance remain important. Weighted estimates retained direction for {sel_same}/95 features; {overlap_sel}/{len(sig_primary)} primary FDR hits also remained weighted-FDR significant. The target-population result depends on selection-at-random conditional on measured predictors.\n"
        f"- **Alternative MI codes:** broad definition included historical MI codes on the current admission, while prior-only/history-only nonacute admissions stayed outside the contrast. {alt_same}/95 feature directions matched primary; {alt_sig}/95 broad estimates passed BH FDR. This definition is less specific to acute MI and is only a sensitivity.\n"
        f"- **Age/sex:** subgroup counts and adjusted estimates are reported with direct interaction contrasts. q-values and intervals, not within-group significance comparisons, determine heterogeneity.\n"
        f"- **Main features:** inspect ST/T feature contrasts in the primary-versus-sensitivity table and figures. Phase 4 residual dependence means related leads/features are not independent replications.\n\n"
        "## Gate 2 decision\n\n"
        "**Gate 2: partially satisfied.** Several central ST/T direction patterns persist across selection weighting, broader current-code sensitivity, and held-out Phase 5 checks, and subgroup interaction tests directly assess heterogeneity. However, the E-value calculation is approximate for Layer 1; a binary-U bias grid cannot rule out unmeasured confounding; selection weighting relies on a measured-only model and limited overlap; some subgroup estimates may be unstable; acute-vs-broad coding changes the estimand; and MI onset relative to ECG remains unknown. These checks do not establish causal identification, and cannot satisfy the stronger claim that the observed ECG differences were caused by MI.\n\n"
        "The project can proceed to an observational Phase 8 write-up after review if it is framed as adjusted diagnosis-feature associations, clearly states the remaining limitations, and avoids temporal/causal claims. The original causal novelty framing is not supported by these data. Phase 8 has not been started."
    )
    (OUT/'PHASE7_COMPLETION_REPORT.md').write_text(
        "# Phase 7 Completion Report\n\n"
        "## Work completed\n\n"
        "1. Unmeasured confounding: Layer 1 approximate E-values where binary RR assumptions permit; Layer 2 additive binary-U tipping products because E-values do not apply to continuous feature differences.\n"
        "2. ECG selection: reused the Phase 3 all-admission audit and selected IDs, fit the documented measured-covariate propensity, and compared inverse-selection-weighted AIPW contrasts with Phase 5.\n"
        "3. Alternative MI codes: compared acute-only primary with broad current-admission acute OR historical codes, keeping prior-only cases out of controls.\n"
        "4. Age/sex subgroups: <65 vs >=65 and F vs M, with cluster intervals and direct interaction tests.\n"
        "5. Consolidated primary-versus-sensitivity results, figures, run metadata, and script were saved. No Phase 1-6 primary output or Phase 3 dataset was rebuilt; only nuisance score computations required for the new sensitivity estimands were recomputed. No Phase 8 work began.\n\n"
        "## Key numbers\n\n"
        f"Primary Layer 2 cohort: {len(prim):,} admissions, {int(prim.acute_mi_diagnosis.sum()):,} acute cases. Broad current-code cohort: {len(broad_l2):,} admissions, {int(t_b.sum()):,} cases. ECG selection denominator: {selection_diag['denominator_n']:,}; selected {selection_diag['selected_n']:,} ({selection_diag['selection_rate']:.2%}). Selection-weighted estimates retained direction in {sel_same}/95 features; broad-code estimates in {alt_same}/95. Age/sex group sizes and interaction summaries are in their dedicated report.\n\n"
        "## Gate 2 and Phase 8 recommendation\n\n"
        "Gate 2 is **partially satisfied**, not fully passed: some ST/T patterns are stable, but selection, confounding, limited overlap, coding specificity, subgroup uncertainty, residual feature dependence, and unknown MI/ECG timing remain. An observational association paper may proceed after review and explicit reframing; causal MI-to-ECG claims are not justified. Phase 8 has not started. See `PHASE7_ROBUSTNESS_ASSESSMENT.md`.\n\n"
        "## Outputs\n\n"
        "- `PHASE7_UNMEASURED_CONFOUNDING.md`\n- `PHASE7_EVALUE_RESULTS.csv`\n- `PHASE7_ECG_SELECTION_SENSITIVITY.md`\n- `PHASE7_SELECTION_SENSITIVITY_RESULTS.csv`\n- `PHASE7_SELECTION_COVARIATE_BALANCE.csv`\n- `PHASE7_ALTERNATIVE_MI_DEFINITIONS.md`\n- `PHASE7_ALTERNATIVE_MI_RESULTS.csv`\n- `PHASE7_AGE_SEX_SUBGROUP_ANALYSIS.md`\n- `PHASE7_SUBGROUP_RESULTS.csv`\n- `PHASE7_SUBGROUP_INTERACTIONS.csv`\n- `PHASE7_PRIMARY_VS_SENSITIVITY_COMPARISON.csv`\n- `PHASE7_ROBUSTNESS_ASSESSMENT.md`\n- `PHASE7_FIGURES/` (selection, coding, age and sex plots)\n- `run_phase7_sensitivity.py` and `PHASE7_RUN_METADATA.json`\n"
    )
    meta={'seed':SEED,'bootstrap_repetitions':BOOT,'crossfit_folds':p5.FOLDS,'selection_model':selection_diag,'broad_code_definition':'acute_mi_diagnosis OR historical_mi_this_admission; clean controls unchanged; prior-only nonacute history excluded','age_boundary':65,'sex_groups':['F','M'],'layer2_primary_n':len(prim),'layer2_primary_mi_cases':int(prim.acute_mi_diagnosis.sum()),'selection_weight_ess':selection_diag['weight_ess']}
    (OUT/'PHASE7_RUN_METADATA.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps({'selection':selection_diag,'selection_direction_same':sel_same,'selection_sig_overlap':overlap_sel,'broad_n':len(broad_l2),'broad_cases':int(t_b.sum()),'broad_direction_same':alt_same,'broad_fdr_sig':alt_sig,'subgroups':sub_meta,'interaction_sig':{c:int(((interaction_df.contrast==c)&interaction_df.interaction_significant_bh_05).sum()) for c in interaction_df.contrast.unique()}},indent=2))

if __name__=='__main__': main()
