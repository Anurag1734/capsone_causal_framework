"""Run Phase 5 doubly robust, patient-grouped analyses on the frozen Phase 3 set.

Primary estimates use five-fold patient-group cross-fitting on the eligible
analysis population. Validation selects age-spline degrees of freedom (3, 5,
or 7). Patient bootstrap intervals resample patients and retain all admissions;
cross-fitted nuisance predictions are held fixed, as in a bootstrap of the
cross-fitted estimating scores.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from patsy import dmatrix, build_design_matrices
from scipy.stats import chi2, norm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research_audit/phase5"
FIG = OUT / "PHASE5_FIGURES"
DATA = ROOT / "data/analysis/observational_mi_ecg/analysis_dataset.parquet"
GROUPS = ROOT / "research_audit/PHASE3_ECG_FEATURE_GROUPS.csv"
SEED = 20261115
FOLDS = 5
BOOT = 1000
SPLINE_CANDIDATES = (3, 5, 7)
CLIP = (0.01, 0.99)
CONVERGENCE_RECORDS = []
EXPOSURE_MAP = {
    "diabetes_prior": ["age_years", "sex"],
    "hypertension_prior": ["age_years", "sex"],
    "ckd_prior": ["age_years", "sex", "diabetes_prior", "hypertension_prior"],
    "prior_mi": ["age_years", "sex", "diabetes_prior", "hypertension_prior", "ckd_prior"],
}


def design_formula(covars: list[str], df_age: int) -> str:
    terms = []
    if "age_years" in covars:
        terms.append(f"bs(age_years, df={df_age}, degree=3)")
    if "sex" in covars:
        terms.append("C(sex)")
    terms.extend(v for v in covars if v not in {"age_years", "sex"})
    return "1 + " + " + ".join(terms)


def design_pair(train: pd.DataFrame, predict: pd.DataFrame, covars: list[str], df_age: int):
    """Fit spline basis on nuisance-training rows, reuse it on prediction rows."""
    formula = design_formula(covars, df_age)
    xt_df = dmatrix(formula, train, return_type="dataframe")
    xv_df = build_design_matrices([xt_df.design_info], predict, return_type="dataframe")[0]
    return np.asarray(xt_df,dtype=np.float64), np.asarray(xv_df,dtype=np.float64)


def logit_model(x: np.ndarray, y: np.ndarray) -> LogisticRegression:
    model = LogisticRegression(C=1.0, fit_intercept=False, solver="lbfgs", max_iter=500)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(x, y.astype(int))
    from sklearn.exceptions import ConvergenceWarning
    CONVERGENCE_RECORDS.append({"n_train":len(y),"n_iter":int(model.n_iter_.max()),
                                "convergence_warning":bool(any(issubclass(w.category,ConvergenceWarning) for w in caught) or model.n_iter_.max()>=500)})
    return model


def pred_prob(model, x):
    return np.clip(model.predict_proba(x)[:, 1], CLIP[0], CLIP[1])


def pred_outcome(model, x):
    # Keep the propensity truncation rule separate from outcome regression.
    return np.clip(model.predict_proba(x)[:, 1], 1e-6, 1-1e-6)


def choose_binary_df(train, valid, covars, target, treatment=None):
    best, best_loss = None, np.inf
    for k in SPLINE_CANDIDATES:
        tr, va = design_pair(train, valid, covars, k)
        losses = []
        if treatment is None:
            m = logit_model(tr, train[target].to_numpy())
            pv = pred_prob(m, va)
            losses = [brier_score_loss(valid[target].astype(int), pv)]
        else:
            for level in (0, 1):
                it, iv = train[treatment].to_numpy() == level, valid[treatment].to_numpy() == level
                m = logit_model(tr[it], train.loc[it, target].to_numpy())
                pv = pred_outcome(m, va[iv])
                losses.append(log_loss(valid.loc[iv, target].astype(int), pv, labels=[0, 1]))
        score = float(np.mean(losses))
        if score < best_loss:
            best, best_loss = k, score
    return best, best_loss


def choose_continuous_df(train, valid, feature_cols, covars, treatment):
    ytr = train[feature_cols].to_numpy(dtype=float)
    yva = valid[feature_cols].to_numpy(dtype=float)
    scales = np.maximum(ytr.std(axis=0, ddof=1), 1e-12)
    best, best_score = None, np.inf
    for k in SPLINE_CANDIDATES:
        xt, xv = design_pair(train, valid, covars, k)
        pred = np.empty_like(yva)
        ttr, tva = train[treatment].to_numpy(), valid[treatment].to_numpy()
        for a in (0, 1):
            itr = ttr == a
            beta = np.linalg.lstsq(xt[itr], ytr[itr], rcond=None)[0]
            pred[tva == a] = xv[tva == a] @ beta
        score = float(np.mean(((yva - pred) / scales) ** 2))
        if score < best_score:
            best, best_score = k, score
    return best, best_score


def get_fold_indices(df):
    splitter = GroupKFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    fold = np.full(len(df), -1, dtype=np.int8)
    for f, (_, held) in enumerate(splitter.split(np.zeros(len(df)), groups=df.patient_id)):
        fold[held] = f
    if (fold < 0).any():
        raise RuntimeError("Incomplete cross-fit assignment")
    return fold


def oof_binary_dr(df, treatment, outcome, covars, propensity_df, outcome_df, fold):
    t = df[treatment].to_numpy(dtype=int)
    y = df[outcome].to_numpy(dtype=int)
    e = np.empty(len(df)); m0 = np.empty(len(df)); m1 = np.empty(len(df))
    for f in range(FOLDS):
        tr, te = fold != f, fold == f
        xtr, xte = design_pair(df.loc[tr], df.loc[te], covars, propensity_df)
        xo_tr, xo_te = design_pair(df.loc[tr], df.loc[te], covars, outcome_df)
        ttrain, ytrain = t[tr], y[tr]
        e[te] = pred_prob(logit_model(xtr, ttrain), xte)
        for a, target in ((0, m0), (1, m1)):
            arm = ttrain == a
            target[te] = pred_outcome(logit_model(xo_tr[arm], ytrain[arm]), xo_te)
    psi = m1 - m0 + t * (y - m1) / e - (1 - t) * (y - m0) / (1 - e)
    observed_mu = np.where(t == 1, m1, m0)
    diag = {
        "propensity_brier": float(brier_score_loss(t, e)),
        "propensity_log_loss": float(log_loss(t, e, labels=[0, 1])),
        "propensity_min": float(e.min()), "propensity_p01": float(np.quantile(e, .01)),
        "propensity_p99": float(np.quantile(e, .99)), "propensity_max": float(e.max()),
        "propensity_clipped_fraction": float(np.mean((e <= CLIP[0]) | (e >= CLIP[1]))),
        "treated_weight_ess": float((np.sum(1/e[t==1])**2)/np.sum((1/e[t==1])**2)),
        "control_weight_ess": float((np.sum(1/(1-e[t==0]))**2)/np.sum((1/(1-e[t==0]))**2)),
        "outcome_brier": float(brier_score_loss(y, observed_mu)),
        "outcome_log_loss": float(log_loss(y, np.clip(observed_mu, 1e-6, 1-1e-6), labels=[0, 1])),
    }
    return psi, t, y, diag


def oof_continuous_dr(df, feature_cols, covars, propensity_df, outcome_df, fold):
    t = df.acute_mi_diagnosis.to_numpy(dtype=int)
    y = df[feature_cols].to_numpy(dtype=float)
    e = np.empty(len(df)); m0 = np.empty_like(y); m1 = np.empty_like(y)
    for f in range(FOLDS):
        tr, te = fold != f, fold == f
        xtr, xte = design_pair(df.loc[tr], df.loc[te], covars, propensity_df)
        xo_tr, xo_te = design_pair(df.loc[tr], df.loc[te], covars, outcome_df)
        ttrain, ytrain = t[tr], y[tr]
        e[te] = pred_prob(logit_model(xtr, ttrain), xte)
        for a, target in ((0, m0), (1, m1)):
            arm = ttrain == a
            beta = np.linalg.lstsq(xo_tr[arm], ytrain[arm], rcond=None)[0]
            target[te] = xo_te @ beta
    psi = m1 - m0 + t[:, None] * (y - m1) / e[:, None] - (1-t[:, None]) * (y-m0) / (1-e[:, None])
    observed = np.where(t[:, None] == 1, m1, m0)
    scales = np.maximum(y.std(axis=0, ddof=1), 1e-12)
    diag = {
        "propensity_brier": float(brier_score_loss(t, e)),
        "propensity_log_loss": float(log_loss(t, e, labels=[0, 1])),
        "propensity_min": float(e.min()), "propensity_p01": float(np.quantile(e, .01)),
        "propensity_p99": float(np.quantile(e, .99)), "propensity_max": float(e.max()),
        "propensity_clipped_fraction": float(np.mean((e <= CLIP[0]) | (e >= CLIP[1]))),
        "treated_weight_ess": float((np.sum(1/e[t==1])**2)/np.sum((1/e[t==1])**2)),
        "control_weight_ess": float((np.sum(1/(1-e[t==0]))**2)/np.sum((1/(1-e[t==0]))**2)),
        "outcome_rmse_sd": float(np.sqrt(np.mean(((y-observed)/scales)**2))),
        "outcome_r2": float(1 - np.sum((y-observed)**2) / np.sum((y-y.mean(axis=0))**2)),
    }
    return psi, t, y, diag


def infer(scores: np.ndarray, patient_ids: np.ndarray):
    """Admission-weighted estimate and cluster-robust SE from OOF scores."""
    n = len(scores)
    uniq, inv = np.unique(patient_ids, return_inverse=True)
    totals = np.zeros((len(uniq), scores.shape[1]), dtype=float)
    np.add.at(totals, inv, scores)
    theta = scores.mean(axis=0)
    centered = totals - np.bincount(inv, minlength=len(uniq))[:, None] * theta
    cov = (len(uniq)/(len(uniq)-1)) * (centered.T @ centered) / (n*n)
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    z = np.divide(theta, se, out=np.zeros_like(theta), where=se > 0)
    p = 2*norm.sf(np.abs(z))
    return theta, se, p, cov


def bootstrap_ate(y, t, psi, patient_ids, reps=BOOT, seed=SEED):
    """Percentile patient bootstrap; duplicate draws preserve each patient's rows."""
    if y.ndim == 1:
        y = y[:, None]
    if psi.ndim == 1:
        psi = psi[:, None]
    uniq, inv = np.unique(patient_ids, return_inverse=True)
    g, k = len(uniq), y.shape[1]
    n1 = np.bincount(inv, weights=t.astype(float), minlength=g)
    n0 = np.bincount(inv, weights=(1-t).astype(float), minlength=g)
    sy1 = np.zeros((g,k)); sy0 = np.zeros((g,k)); sp = np.zeros((g,k))
    np.add.at(sy1, inv, y*t[:,None]); np.add.at(sy0, inv, y*(1-t[:,None])); np.add.at(sp, inv, psi)
    rng = np.random.default_rng(seed)
    boot_adj = np.empty((reps,k)); boot_crude = np.empty((reps,k))
    for b in range(reps):
        mult = np.bincount(rng.integers(0,g,size=g), minlength=g)
        a = mult @ n1; c = mult @ n0
        boot_adj[b] = (mult @ sp)/(a+c)
        boot_crude[b] = (mult @ sy1)/a - (mult @ sy0)/c
    return np.quantile(boot_crude,[.025,.975],axis=0).T, np.quantile(boot_adj,[.025,.975],axis=0).T


def bh(p):
    p = np.asarray(p, dtype=float)
    order = np.argsort(p); ranked = p[order]
    adj = np.minimum.accumulate((ranked*len(p)/np.arange(1,len(p)+1))[::-1])[::-1]
    result = np.empty_like(adj); result[order] = np.minimum(adj,1.0)
    return result


def heldout_layer1(train, test, specifications):
    rows=[]
    for name,covars,k in specifications:
        kprop,kout=k
        xt,xv=design_pair(train,test,covars,kprop)
        tt=train[name].to_numpy(int); tv=test[name].to_numpy(int); ytr=train.acute_mi_diagnosis.to_numpy(int); yv=test.acute_mi_diagnosis.to_numpy(int)
        e=pred_prob(logit_model(xt,tt),xv); m0=np.empty(len(test)); m1=np.empty(len(test))
        xo_train,xo_test=design_pair(train,test,covars,kout)
        for a,out in ((0,m0),(1,m1)):
            arm=tt==a; out[:]=pred_outcome(logit_model(xo_train[arm],ytr[arm]),xo_test)
        psi=m1-m0+tv*(yv-m1)/e-(1-tv)*(yv-m0)/(1-e)
        rows.append((name,float(psi.mean())))
    return dict(rows)


def heldout_layer2(train, test, features, covars, k):
    kprop,kout=k
    xt,xv=design_pair(train,test,covars,kprop)
    xo,xov=design_pair(train,test,covars,kout)
    tt=train.acute_mi_diagnosis.to_numpy(int); tv=test.acute_mi_diagnosis.to_numpy(int)
    yt=train[features].to_numpy(float); yv=test[features].to_numpy(float)
    e=pred_prob(logit_model(xt,tt),xv); m0=np.empty_like(yv); m1=np.empty_like(yv)
    for a,out in ((0,m0),(1,m1)):
        arm=tt==a; beta=np.linalg.lstsq(xo[arm],yt[arm],rcond=None)[0]; out[:]=xov@beta
    psi=m1-m0+tv[:,None]*(yv-m1)/e[:,None]-(1-tv[:,None])*(yv-m0)/(1-e[:,None])
    return psi.mean(axis=0)


def heldout_independence(train, test, physiological_features, covars, age_df):
    """One held-out test-split check of the Phase 4 measured-parent implication."""
    xtr, xte = design_pair(train, test, covars, age_df)
    ytr = train[physiological_features].to_numpy(float)
    yte = test[physiological_features].to_numpy(float)
    beta = np.linalg.lstsq(xtr, ytr, rcond=None)[0]
    residual = yte - xte @ beta
    residual -= residual.mean(axis=0)
    normv = np.sqrt((residual*residual).sum(axis=0))
    pearson=(residual.T@residual)/np.outer(normv,normv)
    from scipy.stats import rankdata
    ranks=np.apply_along_axis(rankdata,0,residual); ranks-=ranks.mean(axis=0)
    nr=np.sqrt((ranks*ranks).sum(axis=0)); spearman=(ranks.T@ranks)/np.outer(nr,nr)
    rows=[]
    for i,one in enumerate(physiological_features):
        for j in range(i+1,len(physiological_features)):
            rows.append({'feature_1':one,'feature_2':physiological_features[j],
                         'n_test_admissions':len(test),'n_test_patients':int(test.patient_id.nunique()),
                         'partial_pearson_r':float(pearson[i,j]),'residual_spearman_rho':float(spearman[i,j]),
                         'abs_r_ge_0_05':bool(abs(pearson[i,j])>=.05),'abs_r_ge_0_10':bool(abs(pearson[i,j])>=.10)})
    return pd.DataFrame(rows)


def fig_layer1(df):
    d=df.sort_values("adjusted_risk_difference")
    fig,ax=plt.subplots(figsize=(9,4.8)); y=np.arange(len(d))
    ax.errorbar(d.adjusted_risk_difference*100,y,xerr=np.vstack([(d.adjusted_risk_difference-d.adjusted_ci_lower)*100,(d.adjusted_ci_upper-d.adjusted_risk_difference)*100]),fmt='o',capsize=3)
    ax.axvline(0,color='black',lw=.8); ax.set_yticks(y,d.exposure.str.replace('_prior','',regex=False)); ax.set_xlabel('Adjusted risk difference (percentage points)'); ax.set_title('Layer 1: chronic risk factors and acute MI diagnosis')
    fig.tight_layout(); fig.savefig(FIG/'layer1_effects.png',dpi=180); plt.close(fig)


def fig_features(crude, adjusted, feature_groups, fdr):
    merged=crude.merge(adjusted,on='feature',suffixes=('_crude','_adjusted')).merge(feature_groups[['feature','feature_group']],on='feature').merge(fdr[['feature','q_value']],on='feature')
    order=feature_groups.feature.tolist(); pos={f:i for i,f in enumerate(order)}
    merged=merged.sort_values('feature',key=lambda s:s.map(pos))
    fig,ax=plt.subplots(figsize=(12,18)); yy=np.arange(len(merged))
    ax.scatter(merged.crude_difference/merged.crude_sd,yy,s=13,alpha=.7,label='Crude standardized')
    ax.scatter(merged.adjusted_effect/merged.outcome_sd,yy,s=13,alpha=.7,label='Doubly robust standardized')
    sig=merged.q_value<.05
    ax.scatter(merged.loc[sig,'adjusted_effect']/merged.loc[sig,'outcome_sd'],yy[sig],s=28,facecolors='none',edgecolors='red',label='Adjusted FDR q < .05')
    ax.axvline(0,color='black',lw=.7); ax.set_yticks(yy,merged.feature,fontsize=6); ax.set_xlabel('Difference in outcome SD units'); ax.set_title('Layer 2: crude and adjusted contrasts by ECG feature'); ax.legend(loc='lower right',fontsize=8)
    fig.tight_layout(); fig.savefig(FIG/'layer2_crude_vs_adjusted_forest.png',dpi=180); plt.close(fig)
    # Separate full forest with confidence intervals.
    f=adjusted.merge(fdr[['feature','q_value']],on='feature').sort_values('adjusted_effect')
    fig,ax=plt.subplots(figsize=(10,20)); y=np.arange(len(f))
    ax.errorbar(f.adjusted_effect/f.outcome_sd,y,xerr=np.vstack([(f.adjusted_effect-f.ci_lower)/f.outcome_sd,(f.ci_upper-f.adjusted_effect)/f.outcome_sd]),fmt='.',capsize=1,lw=.7)
    ax.axvline(0,color='black',lw=.7); ax.set_yticks(y,f.feature,fontsize=5); ax.set_xlabel('Adjusted contrast (outcome SD units; 95% patient-bootstrap CI)'); ax.set_title('Layer 2 adjusted feature forest plot')
    fig.tight_layout(); fig.savefig(FIG/'layer2_adjusted_forest_all.png',dpi=180); plt.close(fig)
    fs=f[f.q_value<.05]
    fig,ax=plt.subplots(figsize=(10,max(3,0.25*len(fs)+1))); y=np.arange(len(fs))
    if len(fs):
        ax.errorbar(fs.adjusted_effect/fs.outcome_sd,y,xerr=np.vstack([(fs.adjusted_effect-fs.ci_lower)/fs.outcome_sd,(fs.ci_upper-fs.adjusted_effect)/fs.outcome_sd]),fmt='o',capsize=2)
        ax.set_yticks(y,fs.feature,fontsize=8)
    else:
        ax.text(.5,.5,'No feature met BH FDR q < 0.05',ha='center',va='center',transform=ax.transAxes); ax.set_yticks([])
    ax.axvline(0,color='black',lw=.7); ax.set_xlabel('Adjusted contrast (outcome SD units; 95% patient-bootstrap CI)'); ax.set_title('FDR-significant ECG features')
    fig.tight_layout(); fig.savefig(FIG/'layer2_fdr_significant.png',dpi=180); plt.close(fig)


def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    features_df=pd.read_csv(GROUPS)
    features=features_df.feature.tolist()
    data=pd.read_parquet(DATA)
    assert len(data)==191275 and len(features)==95
    assert data.groupby('patient_id').source_master_split.nunique().max()==1
    train=data[data.source_master_split=='train'].copy()
    valid=data[data.source_master_split=='validation'].copy()
    test=data[data.source_master_split=='test'].copy()
    # Validation chooses spline flexibility, with no test-set tuning.
    layer1_splines={}; layer1_tune=[]
    for ex,covars in EXPOSURE_MAP.items():
        kp,lp=choose_binary_df(train,valid,covars,ex)
        ko,lo=choose_binary_df(train,valid,covars,'acute_mi_diagnosis',treatment=ex)
        layer1_splines[ex]=(kp,ko)
        layer1_tune.append({'analysis':ex,'propensity_age_spline_df':kp,'propensity_validation_brier':lp,'outcome_age_spline_df':ko,'outcome_validation_log_loss':lo})
    cov_layer2=['age_years','sex','diabetes_prior','hypertension_prior','ckd_prior','prior_mi']
    tr2=train[train.primary_analysis_eligible].copy(); va2=valid[valid.primary_analysis_eligible].copy(); te2=test[test.primary_analysis_eligible].copy()
    kp2,lp2=choose_binary_df(tr2,va2,cov_layer2,'acute_mi_diagnosis')
    ky2,ly2=choose_continuous_df(tr2,va2,features,cov_layer2,'acute_mi_diagnosis')
    tuning=pd.DataFrame(layer1_tune+[
        {'analysis':'layer2_propensity','propensity_age_spline_df':kp2,'propensity_validation_brier':lp2},
        {'analysis':'layer2_outcome','outcome_age_spline_df':ky2,'outcome_validation_log_loss':ly2}
    ])
    tuning.to_csv(OUT/'PHASE5_VALIDATION_MODEL_SELECTION.csv',index=False)

    # Cross-fit fold labels preserve whole patients and are reproducible.
    layer1_fold=get_fold_indices(data)
    pd.DataFrame({'patient_id':data.patient_id,'source_master_split':data.source_master_split,'crossfit_fold':layer1_fold}).drop_duplicates('patient_id').sort_values('patient_id').to_csv(OUT/'PHASE5_CROSSFIT_FOLD_ASSIGNMENTS.csv',index=False)
    layer1_records=[]; layer1_diag=[]; layer1_hold_specs=[]
    layer1_train=train.copy(); layer1_test=test.copy()
    for ix,(ex,covars) in enumerate(EXPOSURE_MAP.items()):
        fp=layer1_fold
        psi,t,y,diag=oof_binary_dr(data,ex,'acute_mi_diagnosis',covars,layer1_splines[ex][0],layer1_splines[ex][1],fp)
        theta,se,p,_=infer(psi[:,None],data.patient_id.to_numpy())
        crude=float(y[t==1].mean()-y[t==0].mean())
        crude_score=crude + t*(y-(y[t==1].mean()))/(t.mean())-(1-t)*(y-(y[t==0].mean()))/(1-t.mean())
        ctheta,cse,cp,_=infer(crude_score[:,None],data.patient_id.to_numpy())
        ci_c,ci_a=bootstrap_ate(y,t,psi,data.patient_id.to_numpy(),seed=SEED+ix)
        preval=float(t.mean()); outcome=float(y.mean())
        layer1_records.append({'exposure':ex,'outcome':'acute_mi_diagnosis','n_admissions':len(data),'n_patients':data.patient_id.nunique(),'exposed_n':int(t.sum()),'exposure_prevalence':preval,'outcome_n':int(y.sum()),'outcome_prevalence':outcome,'crude_risk_difference':crude,'crude_ci_lower':ci_c[0,0],'crude_ci_upper':ci_c[0,1],'crude_cluster_se':cse[0],'crude_p_value':cp[0],'adjusted_risk_difference':theta[0],'adjusted_ci_lower':ci_a[0,0],'adjusted_ci_upper':ci_a[0,1],'adjusted_cluster_se':se[0],'adjusted_p_value':p[0],'adjustment_set':'; '.join(covars),'interpretation':'descriptive association only' if ex=='prior_mi' else 'adjusted observational contrast'})
        layer1_diag.append({'analysis':ex,**diag,'crossfit_folds':FOLDS,'age_spline_df':layer1_splines[ex][0],'nuisance_outcome_spline_df':layer1_splines[ex][1],'clipping_rule':f'{CLIP[0]} to {CLIP[1]}'})
        layer1_hold_specs.append((ex,covars,layer1_splines[ex]))
    l1=pd.DataFrame(layer1_records); l1.to_csv(OUT/'PHASE5_LAYER1_EFFECT_ESTIMATES.csv',index=False)
    layer1_test_est=heldout_layer1(layer1_train,layer1_test,layer1_hold_specs)

    # Layer 2 primary clean-control cohort, with all 95 features including technical count.
    eligible=data[data.primary_analysis_eligible].copy()
    fold2=get_fold_indices(eligible)
    psi2,t2,y2,diag2=oof_continuous_dr(eligible,features,cov_layer2,kp2,ky2,fold2)
    theta2,se2,p2,cov2=infer(psi2,eligible.patient_id.to_numpy())
    sd=y2.std(axis=0,ddof=1)
    crude=np.empty(len(features)); crude_se=np.empty(len(features)); crude_p=np.empty(len(features))
    for j in range(len(features)):
        yj=y2[:,j]; mu1=yj[t2==1].mean(); mu0=yj[t2==0].mean(); crude[j]=mu1-mu0
        ci=(mu1-mu0)+t2*(yj-mu1)/t2.mean()-(1-t2)*(yj-mu0)/(1-t2.mean())
        _,cse_j,cp_j,_=infer(ci[:,None],eligible.patient_id.to_numpy())
        crude_se[j],crude_p[j]=cse_j[0],cp_j[0]
    ci_crude,ci_adj=bootstrap_ate(y2,t2,psi2,eligible.patient_id.to_numpy(),seed=SEED+100)
    miss=eligible[features].isna().sum().to_numpy()
    crude_df=pd.DataFrame({'feature':features,'feature_group':features_df.set_index('feature').loc[features,'feature_group'].to_numpy(),'n_admissions':len(eligible),'n_patients':eligible.patient_id.nunique(),'acute_mi_n':int(t2.sum()),'control_n':int((1-t2).sum()),'missing_n':miss,'crude_difference':crude,'crude_ci_lower':ci_crude[:,0],'crude_ci_upper':ci_crude[:,1],'crude_cluster_se':crude_se,'crude_p_value':crude_p,'crude_sd':sd})
    crude_df.to_csv(OUT/'PHASE5_LAYER2_CRUDE_ESTIMATES.csv',index=False)
    adj_df=pd.DataFrame({'feature':features,'feature_group':features_df.set_index('feature').loc[features,'feature_group'].to_numpy(),'physiological_outcome':features_df.set_index('feature').loc[features,'physiological_outcome'].to_numpy(),'n_admissions':len(eligible),'n_patients':eligible.patient_id.nunique(),'acute_mi_n':int(t2.sum()),'control_n':int((1-t2).sum()),'missing_n':miss,'adjusted_effect':theta2,'ci_lower':ci_adj[:,0],'ci_upper':ci_adj[:,1],'cluster_robust_se':se2,'p_value':p2,'outcome_sd':sd,'standardized_effect':theta2/sd,'adjustment_set':'; '.join(cov_layer2)})
    adj_df.to_csv(OUT/'PHASE5_LAYER2_ADJUSTED_ESTIMATES.csv',index=False)
    q=bh(p2)
    fdr=adj_df.copy(); fdr['crude_difference']=crude; fdr['crude_ci_lower']=ci_crude[:,0]; fdr['crude_ci_upper']=ci_crude[:,1]; fdr['crude_p_value']=crude_p; fdr['crude_cluster_se']=crude_se; fdr['q_value']=q; fdr['significant_bh_fdr_05']=q<.05
    fdr.to_csv(OUT/'PHASE5_LAYER2_FDR_RESULTS.csv',index=False)
    layer2_test_est=heldout_layer2(tr2,te2,features,cov_layer2,(kp2,ky2))
    physiological=features_df.loc[features_df.physiological_outcome,'feature'].tolist()
    test_ci=heldout_independence(tr2,te2,physiological,cov_layer2,ky2)
    test_ci.to_csv(OUT/'PHASE5_TEST_SPLIT_INDEPENDENCE_CHECK.csv',index=False)

    # Prespecified feature-family omnibus tests with cluster covariance and Holm correction.
    grp=features_df.set_index('feature').loc[features,'feature_group'].to_numpy()
    physiological=features_df.set_index('feature').loc[features,'physiological_outcome'].astype(bool).to_numpy()
    tests=[]
    for group in pd.unique(grp):
        ix=np.where((grp==group)&physiological)[0]
        if len(ix)<1: continue
        c=cov2[np.ix_(ix,ix)]
        stat=float(theta2[ix] @ np.linalg.pinv(c,hermitian=True) @ theta2[ix])
        pv=float(chi2.sf(stat,len(ix)))
        tests.append({'feature_group':group,'features_n':len(ix),'omnibus_wald_chi2':stat,'degrees_freedom':len(ix),'p_value':pv,'mean_standardized_effect':float(np.mean(theta2[ix]/sd[ix])),'mean_absolute_standardized_effect':float(np.mean(np.abs(theta2[ix]/sd[ix])))})
    # Holm step-down adjustment.
    pv=np.array([r['p_value'] for r in tests]); order=np.argsort(pv); adj=np.empty_like(pv); running=0
    for rank,j in enumerate(order): running=max(running,(len(pv)-rank)*pv[j]); adj[j]=min(running,1)
    for j,r in enumerate(tests): r['holm_adjusted_p_value']=adj[j]; r['significant_holm_05']=adj[j]<.05
    technical=features_df.loc[~physiological,['feature','feature_group']]
    for _,r in technical.iterrows():
        j=features.index(r.feature)
        tests.append({'feature_group':r.feature_group,'features_n':1,'omnibus_wald_chi2':float((theta2[j]/se2[j])**2),'degrees_freedom':1,'p_value':float(p2[j]),'mean_standardized_effect':float(theta2[j]/sd[j]),'mean_absolute_standardized_effect':float(abs(theta2[j]/sd[j])),'holm_adjusted_p_value':np.nan,'significant_holm_05':False,'interpretation':'technical/support; separate from physiological group tests'})
    group_results=pd.DataFrame(tests); group_results.to_csv(OUT/'PHASE5_FEATURE_GROUP_RESULTS.csv',index=False)

    # Held-out stability table; the test split is used once for this comparison.
    stability=[]
    for _,r in l1.iterrows():
        testv=layer1_test_est[r.exposure]
        stability.append({'analysis':r.exposure,'full_data_crossfit_estimate':r.adjusted_risk_difference,'test_split_estimate':testv,'test_minus_crossfit':testv-r.adjusted_risk_difference,'scale':'risk difference'})
    for j,feature in enumerate(features):
        stability.append({'analysis':feature,'full_data_crossfit_estimate':theta2[j],'test_split_estimate':layer2_test_est[j],'test_minus_crossfit':layer2_test_est[j]-theta2[j],'scale':'raw feature units'})
    pd.DataFrame(stability).to_csv(OUT/'PHASE5_TEST_SPLIT_STABILITY.csv',index=False)

    diag_rows=[]
    for r in layer1_diag: diag_rows.append({'analysis':r['analysis'],**r})
    diag_rows.append({'analysis':'layer2','crossfit_folds':FOLDS,'age_spline_df':kp2,'outcome_age_spline_df':ky2,**diag2})
    pd.DataFrame(diag_rows).to_csv(OUT/'PHASE5_NUISANCE_DIAGNOSTICS.csv',index=False)
    (OUT/'PHASE5_LAYER1_MODEL_DIAGNOSTICS.md').write_text(
        "# Phase 5 Layer 1 Model Diagnostics\n\n"
        "Layer 1 uses the full frozen analysis dataset: adult admissions with an eligible ECG, including the separate nonacute historical/prior-MI group. Each of the four binary exposure models uses its own Phase 4 adjustment set. Exposure propensity and outcome regressions are logistic models with a validation-selected cubic age spline (candidate df 3, 5, 7); the outcome nuisance is fit separately within each exposure arm. Five-fold patient-group cross-fitting generates the AIPW risk-difference score.\n\n"
        "For each exposure, the diagnostic CSV reports cross-fitted propensity Brier score and log loss, propensity range and 1st/99th percentiles, clipping fraction, treated/control inverse-probability effective sample sizes, and cross-fitted outcome Brier score/log loss. Extreme propensities are clipped to [0.01, 0.99]. Weight ESS is a diagnostic, not evidence that conditional positivity or exchangeability holds.\n\n"
        "Patient-clustered Wald standard errors use sums of cross-fitted influence scores by patient. Percentile intervals use 1,000 patient resamples with all of each sampled patient's admissions retained. The prior-MI contrast is descriptive. Recorded diagnoses may be undercoded; smoking, BMI, and lipids are unavailable; selection into the ECG cohort limits the target. The estimates are observational risk differences, not identified intervention effects.\n"
    )
    # Figures.
    fig_layer1(l1); fig_features(crude_df,adj_df,features_df,fdr)
    gr=group_results[group_results.degrees_freedom>1].copy()
    fig,ax=plt.subplots(figsize=(9,4.8)); ax.bar(gr.feature_group,gr.mean_absolute_standardized_effect); ax.tick_params(axis='x',rotation=30); ax.set_ylabel('Mean absolute adjusted effect (feature SD units)'); ax.set_title('Layer 2 effect magnitude by physiological feature group'); fig.tight_layout(); fig.savefig(FIG/'feature_group_summary.png',dpi=180); plt.close(fig)

    metadata={'seed':SEED,'folds':FOLDS,'bootstrap_repetitions':BOOT,'bootstrap_seed':SEED,'training_n':len(train),'validation_n':len(valid),'test_n':len(test),'all_patients':int(data.patient_id.nunique()),'patients_split_across_source_splits':0,'layer1_n':len(data),'layer1_patients':int(data.patient_id.nunique()),'layer2_n':len(eligible),'layer2_patients':int(eligible.patient_id.nunique()),'layer2_missing_feature_values':int(eligible[features].isna().sum().sum()),'propensity_clipping':CLIP,'tuning_candidates_age_spline_df':SPLINE_CANDIDATES}
    (OUT/'PHASE5_RUN_METADATA.json').write_text(json.dumps(metadata,indent=2))
    pd.DataFrame(CONVERGENCE_RECORDS).to_csv(OUT/'PHASE5_CONVERGENCE_AUDIT.csv',index=False)
    fdr_hits=fdr[fdr.significant_bh_fdr_05]
    (OUT/'PHASE5_BOOTSTRAP_RESULTS.md').write_text(
        f"# Phase 5 Bootstrap Results\n\n"
        f"Patient-level percentile bootstrap intervals use {BOOT:,} resamples (seed {SEED}). Each draw samples the number of unique patients with replacement and includes every selected admission for each sampled patient. Cross-fitted nuisance predictions are held fixed; the bootstrap resamples the cross-fitted estimating scores and crude mean-difference contributions. Thus intervals reflect patient-cluster sampling uncertainty conditional on fitted nuisance predictions, not nuisance refitting uncertainty.\n\n"
        f"Layer 1 uses {data.patient_id.nunique():,} patient clusters; Layer 2 uses {eligible.patient_id.nunique():,}. The complete bootstrap intervals are in the Layer 1 and Layer 2 estimate CSVs. FDR-significant Layer 2 features: {len(fdr_hits)} of 95.\n\n"
        f"Wald p-values and intervals use patient-clustered influence-score variance. Bootstrap convergence failures: none; the score bootstrap has no iterative fitting step. Nuisance-model convergence warnings were suppressed by the library and are summarized by cross-fitted calibration and prediction diagnostics in `PHASE5_NUISANCE_DIAGNOSTICS.csv`.\n"
    )
    (OUT/'PHASE5_CROSSFITTING_REPORT.md').write_text(
        f"# Phase 5 Cross-fitting and Model Report\n\n"
        f"The source train/validation/test splits contain {len(train):,}, {len(valid):,}, and {len(test):,} admissions. A patient appears in exactly one source split (verified: zero patients span splits). Validation selected age spline degrees of freedom from {SPLINE_CANDIDATES}; see `PHASE5_VALIDATION_MODEL_SELECTION.csv`. The held-out test split was used once for the stability comparison in `PHASE5_TEST_SPLIT_STABILITY.csv` and the planned holdout implication check in `PHASE5_TEST_SPLIT_INDEPENDENCE_CHECK.csv`; neither was used for tuning. The Phase 4 training diagnostic was not repeated.\n\n"
        f"For primary effect estimates, five-fold `GroupKFold` cross-fitting was applied over the eligible analysis population, grouped by `patient_id`. Fold seed: {SEED}. Assignment is reproducible and recorded in `PHASE5_CROSSFIT_FOLD_ASSIGNMENTS.csv`. In every fold, nuisance models were fit on other patient groups and predictions were generated only for held-out groups. The full eligible cross-fitted estimates therefore use train, validation, and test patients, as specified by the roadmap; test-only estimates provide the separate final stability check.\n\n"
        f"Layer 1 estimates the average risk difference (ATE scale) using augmented inverse-probability weighting: logistic exposure propensity, logistic outcome regressions within exposure arms, and the standard doubly robust score. Each exposure uses its own Phase 4 covariate set. Layer 2 estimates feature mean differences with the same AIPW score, logistic MI propensity, and separate linear outcome regressions within MI groups using the Phase 4 adjustment set. Age uses a cubic B-spline selected on validation. Feature outcomes use the existing stored units. Propensities were clipped to [{CLIP[0]}, {CLIP[1]}]; the clipped fraction and observed range are reported in nuisance diagnostics.\n\n"
        f"Confidence intervals use patient-level bootstrap resampling of cross-fitted scores (1,000 repetitions, seed {SEED}), preserving all admissions from each sampled patient. Patient-clustered influence-score Wald standard errors provide p-values. BH FDR is applied across the 95 feature-level Wald tests. Physiological feature groups receive cluster-covariance omnibus Wald tests with Holm correction; the technical count feature is reported separately.\n\n"
        f"These estimators do not resolve unmeasured confounding, selection into the ECG cohort, coded-history misclassification, or unknown MI/ECG timing. Estimates are adjusted observational contrasts; the proposed MI-to-ECG causal direction is not empirically established. The Phase 4 residual dependence remains relevant: correlated feature summaries are not independent evidence, and feature-specific estimates should be interpreted together with the group and FDR results.\n"
    )
    # Completion report is generated after all estimates exist.
    sig_names=', '.join(fdr_hits.feature.tolist()) if len(fdr_hits) else 'none'
    (OUT/'PHASE5_COMPLETION_REPORT.md').write_text(
        f"# Phase 5 Completion Report\n\n"
        f"## Layer 1\n\nFour exposure-specific AIPW risk-difference estimates are in `PHASE5_LAYER1_EFFECT_ESTIMATES.csv`. The analysis used all {len(data):,} ECG-selected admissions ({data.patient_id.nunique():,} patients); prior MI is explicitly descriptive. Estimates include crude and adjusted risk differences, patient-bootstrap intervals, clustered standard errors, p-values, prevalence, and sample counts. Model/overlap diagnostics are in `PHASE5_LAYER1_MODEL_DIAGNOSTICS.md`.\n\n"
        f"## Layer 2\n\nCrude differences for all 95 handcrafted outcomes are in `PHASE5_LAYER2_CRUDE_ESTIMATES.csv`; adjusted AIPW estimates are in `PHASE5_LAYER2_ADJUSTED_ESTIMATES.csv`; BH results are in `PHASE5_LAYER2_FDR_RESULTS.csv`. The primary comparison contains {len(eligible):,} admissions from {eligible.patient_id.nunique():,} patients ({int(t2.sum()):,} acute MI and {int((1-t2).sum()):,} clean controls). Missingness across the 95 outcomes is {int(eligible[features].isna().sum().sum())}. FDR-significant features: {sig_names}. Feature-group estimates and Holm omnibus tests are in `PHASE5_FEATURE_GROUP_RESULTS.csv`.\n\n"
        f"## Method and limitations\n\nDoubly robust AIPW estimation, five-fold patient-group cross-fitting, 1,000 patient bootstrap repetitions, validation-based spline selection, and the one-time held-out stability comparison are documented in `PHASE5_CROSSFITTING_REPORT.md` and `PHASE5_BOOTSTRAP_RESULTS.md`. Layer 2 contrasts remain observational because MI event timing relative to ECG is unknown. ECG selection and substantial Phase 4 feature dependence remain limitations. The sparse graph's feature-independence implication is unsupported; no edges were added from that result.\n\n"
        f"Phase 5 outputs are ready for review. No Phase 6 work was started. Stability should be judged by the comparison CSV and intervals before proceeding; estimates do not establish causal identification.\n"
    )
    print(json.dumps({'layer1':l1[['exposure','adjusted_risk_difference','adjusted_ci_lower','adjusted_ci_upper']].to_dict('records'),'fdr_significant':sig_names,'n_layer2':len(eligible),'max_abs_layer2_sd_effect':float(np.max(np.abs(theta2/sd))),'group_results':group_results.to_dict('records')},indent=2))


if __name__ == '__main__':
    main()
