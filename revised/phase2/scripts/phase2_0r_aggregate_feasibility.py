"""Aggregate-only Gate 0 feasibility calculations for revised Phase 2.

Patient linkage and measurements are processed in memory only. This script
never writes patient-level records; output tables are aggregate summaries.
It is not the Phase 2.1 analytical cohort builder and performs no effect
estimation.
"""
from __future__ import annotations

import argparse
import csv
import io
import math
import re
import subprocess
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


BP_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*([0-9]+(?:\.[0-9]+)?)\s*$")
BMI_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*$")
WINDOW_DAYS = 730
HORIZONS = (90, 180, 365, 730)


def parquet_member(archive: Path, member: str, columns: list[str]) -> pd.DataFrame:
    proc = subprocess.run(["tar", "-xOf", str(archive), member], check=True, capture_output=True)
    return pq.read_table(io.BytesIO(proc.stdout), columns=columns).to_pandas()


def normalize_code(code: pd.Series) -> pd.Series:
    return code.astype("string").str.upper().str.replace(".", "", regex=False)


def build_ephemeral_index(archive: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    adm_cols = ["subject_id", "hadm_id", "admittime", "dischtime", "deathtime", "hospital_expire_flag"]
    adm = parquet_member(archive, "longitudinal/admissions_chronology.parquet", adm_cols)
    diag = parquet_member(archive, "longitudinal/diagnoses_all.parquet", ["subject_id", "hadm_id", "icd_code", "icd_version"])
    code = normalize_code(diag["icd_code"])
    ver = pd.to_numeric(diag["icd_version"], errors="coerce")
    icd9, icd10 = ver.eq(9), ver.eq(10)
    diag["acute"] = (icd9 & code.str.startswith("410", na=False)) | (icd10 & (code.str.startswith("I21", na=False) | code.str.startswith("I22", na=False)))
    diag["historical"] = (icd9 & code.str.startswith("412", na=False)) | (icd10 & code.str.startswith("I252", na=False))
    diag["diabetes"] = (icd9 & code.str.startswith("250", na=False)) | (icd10 & (code.str.startswith("E08", na=False) | code.str.startswith("E09", na=False) | code.str.startswith("E10", na=False) | code.str.startswith("E11", na=False) | code.str.startswith("E12", na=False) | code.str.startswith("E13", na=False)))
    diag["hypertension"] = (icd9 & code.str.match(r"^40[1-5]", na=False)) | (icd10 & code.str.match(r"^I1[0-5]", na=False))
    diag["ckd"] = (icd9 & code.str.startswith("585", na=False)) | (icd10 & code.str.startswith("N18", na=False))
    flags = diag.groupby(["subject_id", "hadm_id"], as_index=False)[["acute", "historical", "diabetes", "hypertension", "ckd"]].max()
    adm = adm.merge(flags, on=["subject_id", "hadm_id"], how="left", validate="one_to_one")
    for c in ["acute", "historical", "diabetes", "hypertension", "ckd"]:
        adm[c] = adm[c].fillna(False).astype(bool)
    adm = adm.loc[adm["admittime"].notna()].copy()
    adm["admit_date"] = pd.to_datetime(adm["admittime"]).dt.normalize()
    first_acute = (adm.loc[adm.acute].sort_values(["subject_id", "admittime", "hadm_id"])
                  .drop_duplicates("subject_id").set_index("subject_id")["admittime"])
    adm["first_acute_time"] = adm.subject_id.map(first_acute)
    first_acute_day = first_acute.dt.normalize()
    adm["first_acute_day"] = adm.subject_id.map(first_acute_day)
    candidates = adm.loc[~adm.acute & (adm.first_acute_day.isna() | (adm.admit_date < adm.first_acute_day))].copy()
    candidates = candidates.sort_values(["subject_id", "admittime", "hadm_id"])
    tied = int(candidates.duplicated(["subject_id", "admittime"], keep=False).groupby(candidates.subject_id).any().sum())
    index = candidates.drop_duplicates("subject_id", keep="first").copy()
    index["index_date"] = index.admit_date
    index["window_start"] = index.index_date - pd.to_timedelta(WINDOW_DAYS, unit="D")
    # Conservative recorded-history exclusion through the index admission timestamp.
    history = index[["subject_id", "index_date"]].merge(
        adm[["subject_id", "admit_date", "acute", "historical"]], on="subject_id", suffixes=("_index", "_record"), how="left"
    )
    history = history.loc[history.admit_date <= history.index_date]
    prior = history.groupby("subject_id")[["acute", "historical"]].any()
    eligible_ids = prior.index[~prior.acute & ~prior.historical]
    index = index.loc[index.subject_id.isin(eligible_ids)].copy()
    index["event_time"] = index.subject_id.map(first_acute)
    index["event"] = index.event_time.notna() & (pd.to_datetime(index.event_time).dt.normalize() > index.index_date)
    index.loc[~index.event, "event_time"] = pd.NaT
    index = index.sort_values("subject_id").drop_duplicates("subject_id")
    index["window_start"] = index.index_date - pd.to_timedelta(WINDOW_DAYS, unit="D")

    # All incident-event timing remains based on the first acute-coded admission.
    out = adm[["subject_id", "hadm_id", "admittime", "dischtime", "deathtime", "hospital_expire_flag", "acute", "historical", "diabetes", "hypertension", "ckd"]].copy()
    meta = {
        "source_admissions": int(adm.hadm_id.nunique()),
        "source_patients": int(adm.subject_id.nunique()),
        "source_acute_patients": int(first_acute.index.nunique()),
        "candidate_index_patients": int(candidates.subject_id.nunique()),
        "candidate_indices_excluded_for_prior_acute_or_historical_by_calendar_date": int(len(prior.index)-len(eligible_ids)),
        "candidate_indices_with_prior_acute_by_calendar_date": int(prior.acute.sum()),
        "candidate_indices_with_prior_historical_mi_by_calendar_date": int(prior.historical.sum()),
        "candidate_indices_with_both_prior_acute_and_historical": int((prior.acute & prior.historical).sum()),
        "eligible_index_patients": int(index.subject_id.nunique()),
        "eligible_incident_cases": int(index.event.sum()),
        "eligible_no_recorded_event": int((~index.event).sum()),
        "patients_with_same_time_candidate_admissions": tied,
    }
    return index, out, meta


def collect_omr(archive: Path, index: pd.DataFrame) -> tuple[dict[int, list[tuple[date, float]]], dict[int, list[tuple[date, float]]], dict]:
    idx = index.set_index("subject_id")
    index_dates = idx.index_date.dt.date.to_dict()
    window_starts = idx.window_start.dt.date.to_dict()
    patient_ids = set(index_dates)
    bp: dict[int, list[tuple[date, float]]] = defaultdict(list)
    bmi: dict[int, list[tuple[date, float]]] = defaultdict(list)
    counts = defaultdict(int)
    proc = subprocess.Popen(["tar", "-xOf", str(archive), "omr.csv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    for chunk in pd.read_csv(proc.stdout, usecols=["subject_id", "chartdate", "result_name", "result_value"],
                             dtype={"subject_id":"Int64", "chartdate":"string", "result_name":"string", "result_value":"string"},
                             chunksize=250_000):
        chunk = chunk.loc[chunk.result_name.isin(["Blood Pressure", "BMI (kg/m2)"]) & chunk.subject_id.isin(patient_ids)].copy()
        if chunk.empty:
            continue
        chunk["day"] = pd.to_datetime(chunk.chartdate, errors="coerce").dt.date
        bad_day = chunk.day.isna()
        counts["OMR_bad_date_for_candidate_patients"] += int(bad_day.sum())
        chunk = chunk.loc[~bad_day].copy()
        chunk["index_date"] = chunk.subject_id.map(index_dates)
        chunk["window_start"] = chunk.subject_id.map(window_starts)
        b = chunk.loc[chunk.result_name.eq("Blood Pressure")].copy()
        if not b.empty:
            b = b.loc[(b.day >= b.index_date.map(lambda d:d-timedelta(days=WINDOW_DAYS))) & (b.day < b.index_date)]
            counts["bp_rows_in_window_before_qc"] += len(b)
            parsed = b.result_value.str.extract(BP_RE)
            sbp = pd.to_numeric(parsed[0], errors="coerce")
            dbp = pd.to_numeric(parsed[1], errors="coerce")
            counts["bp_unparseable"] += int(sbp.isna().sum())
            valid = sbp.notna() & dbp.notna() & sbp.between(60,260) & dbp.between(20,160) & (sbp>dbp)
            counts["bp_failed_range_or_order"] += int((sbp.notna() & dbp.notna() & ~valid).sum())
            good = b.loc[valid, ["subject_id", "day"]].copy()
            good["sbp"] = sbp.loc[valid].to_numpy()
            for sid, day, value in good.itertuples(index=False, name=None):
                bp[int(sid)].append((day, float(value)))
            counts["bp_valid_readings"] += len(good)
        m = chunk.loc[chunk.result_name.eq("BMI (kg/m2)")].copy()
        if not m.empty:
            m = m.loc[m.day < m.window_start]
            counts["bmi_rows_before_window"] += len(m)
            values = pd.to_numeric(m.result_value.str.extract(BMI_RE)[0], errors="coerce")
            counts["bmi_unparseable"] += int(values.isna().sum())
            valid = values.between(10,80)
            counts["bmi_failed_plausibility_10_80"] += int((values.notna() & ~valid).sum())
            good = m.loc[valid, ["subject_id", "day"]].copy()
            good["bmi"] = values.loc[valid].to_numpy()
            for sid, day, value in good.itertuples(index=False, name=None):
                bmi[int(sid)].append((day, float(value)))
            counts["bmi_valid_pre_window"] += len(good)
    stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    code = proc.wait()
    if code:
        raise RuntimeError(f"tar OMR stream failed ({code}): {stderr[-2000:]}")
    return bp, bmi, dict(counts)


def add_covariates(index: pd.DataFrame, adm: pd.DataFrame, archive: Path, bmi_readings: dict) -> pd.DataFrame:
    demo = parquet_member(archive, "longitudinal/patients_demographics.parquet", ["subject_id", "gender", "anchor_age", "anchor_year", "dod"])
    x = index.merge(demo, on="subject_id", how="left", validate="one_to_one")
    x["age_at_window_start"] = x.anchor_age + (x.window_start.dt.year - x.anchor_year)
    x.loc[(x.age_at_window_start < 0) | (x.age_at_window_start > 120), "age_at_window_start"] = np.nan
    x["age_group"] = np.where(x.age_at_window_start < 65, "<65", np.where(x.age_at_window_start >= 65, ">=65", "Unknown"))
    x["age_at_index"] = x.anchor_age + (x.index_date.dt.year - x.anchor_year)
    x.loc[(x.age_at_index < 0) | (x.age_at_index > 120), "age_at_index"] = np.nan
    x["age_group_at_index"] = np.where(x.age_at_index < 65, "<65", np.where(x.age_at_index >= 65, ">=65", "Unknown"))
    x["sex_group"] = x.gender.map({"M": "Male", "F": "Female"}).fillna("Other_or_missing")
    # Pre-window diagnosis history only. Existing absence means no observed code, not absence of disease.
    hx = x[["subject_id", "window_start"]].merge(
        adm[["subject_id", "admittime", "diabetes", "hypertension", "ckd"]], on="subject_id", how="left"
    )
    hx = hx.loc[hx.admittime < hx.window_start]
    hflags = hx.groupby("subject_id")[["diabetes", "hypertension", "ckd"]].any()
    for v in ("diabetes", "hypertension", "ckd"):
        x[v] = x.subject_id.map(hflags[v]).fillna(False).astype(bool)
    x["diabetes_group"] = np.where(x.diabetes, "Documented", "No_documented_history")
    ix = x[["subject_id", "admittime"]].merge(
        adm[["subject_id", "admittime", "diabetes", "hypertension", "ckd"]], on="subject_id", how="left", suffixes=("_index", "_record")
    )
    ix = ix.loc[ix.admittime_record <= ix.admittime_index]
    ixflags = ix.groupby("subject_id")[["diabetes", "hypertension", "ckd"]].any()
    for v in ("diabetes", "hypertension", "ckd"):
        x[f"{v}_documented_by_index"] = x.subject_id.map(ixflags[v]).fillna(False).astype(bool)
    x["diabetes_by_index_group"] = np.where(x.diabetes_documented_by_index, "Documented_by_index_not_pre_window", "No_documented_history_by_index")
    x["bmi"] = x.subject_id.map({sid: sorted(vals, key=lambda z: z[0])[-1][1] for sid, vals in bmi_readings.items() if vals})
    x["bmi_available"] = x.bmi.notna()
    return x


def summarize_bp(index_cov: pd.DataFrame, bp: dict[int, list[tuple[date, float]]]) -> tuple[pd.DataFrame, dict]:
    idx = index_cov.set_index("subject_id")
    records = {}
    for sid, vals in bp.items():
        ordered = sorted(vals)
        s = np.array([v for _, v in ordered], dtype=float)
        dates = [d for d, _ in ordered]
        records[sid] = {
            "n_bp": len(s), "sbp_mean": float(s.mean()), "sbp_median": float(np.median(s)),
            "sbp_sd": float(s.std(ddof=1)) if len(s) > 1 else np.nan,
            "sbp_q05": float(np.quantile(s, .05)), "sbp_q25": float(np.quantile(s, .25)),
            "sbp_q75": float(np.quantile(s, .75)), "sbp_q95": float(np.quantile(s, .95)),
            "first_bp": dates[0], "last_bp": dates[-1],
            "days_last_bp_to_index": (idx.loc[sid].index_date.date() - dates[-1]).days,
            "same_day_duplicate_count": len(s) - len(set(dates)),
            "observed_span_days": (dates[-1] - dates[0]).days,
        }
    bpdf = pd.DataFrame.from_dict(records, orient="index").rename_axis("subject_id").reset_index()
    out = index_cov.merge(bpdf, on="subject_id", how="left", validate="one_to_one")
    out["n_bp"] = out.n_bp.fillna(0).astype(int)
    out["has_bp"] = out.n_bp.gt(0)
    return out, records


def weighted_quantile(values, q):
    a = np.asarray(values, dtype=float)
    return float(np.quantile(a, q)) if len(a) else np.nan


def aggregate_thresholds(data: pd.DataFrame, bp: dict[int, list[tuple[date, float]]]) -> pd.DataFrame:
    base_n = len(data)
    base_events = int(data.event.sum())
    rows = []
    for threshold in (1, 2, 3, 4):
        z = data.loc[data.n_bp >= threshold]
        n, e = len(z), int(z.event.sum())
        def q(col, qv): return weighted_quantile(z[col].dropna(), qv)
        sbp_values = z.sbp_mean.dropna().to_numpy()
        reading = z.n_bp.to_numpy()
        gaps = z.days_last_bp_to_index.dropna().to_numpy()
        within = z.sbp_sd.dropna().to_numpy()
        rows.append({
            "minimum_valid_readings": threshold, "eligible_patients": n, "incident_first_mi_cases": e,
            "no_recorded_first_mi_before_source_end": n-e, "eligible_retention_pct_of_common_index": 100*n/base_n if base_n else np.nan,
            "case_retention_pct_of_common_index_incident_cases": 100*e/base_events if base_events else np.nan,
            "mean_patient_mean_sbp_mmhg": float(sbp_values.mean()) if len(sbp_values) else np.nan,
            "median_patient_mean_sbp_mmhg": q("sbp_mean", .5), "q05_patient_mean_sbp_mmhg": q("sbp_mean", .05),
            "q25_patient_mean_sbp_mmhg": q("sbp_mean", .25), "q75_patient_mean_sbp_mmhg": q("sbp_mean", .75),
            "q95_patient_mean_sbp_mmhg": q("sbp_mean", .95), "proportion_mean_sbp_ge_130_pct": 100*float((z.sbp_mean>=130).mean()) if n else np.nan,
            "mean_of_patient_median_sbp_mmhg":float(z.sbp_median.mean()) if n else np.nan,
            "median_of_patient_median_sbp_mmhg":q("sbp_median",.5),
            "median_valid_reading_count": q("n_bp", .5), "reading_count_q25": q("n_bp", .25), "reading_count_q75": q("n_bp", .75),
            "median_within_person_sbp_sd_mmhg": q("sbp_sd", .5), "within_person_sbp_sd_q25_mmhg":q("sbp_sd",.25), "within_person_sbp_sd_q75_mmhg":q("sbp_sd",.75),
            "median_days_last_reading_to_index": q("days_last_bp_to_index", .5),
            "last_reading_gap_q25_days": q("days_last_bp_to_index", .25), "last_reading_gap_q75_days": q("days_last_bp_to_index", .75),
            "median_readings_per_year_fixed_window": q("n_bp", .5)*365.25/WINDOW_DAYS,
            "readings_per_year_q25":q("n_bp",.25)*365.25/WINDOW_DAYS,"readings_per_year_q75":q("n_bp",.75)*365.25/WINDOW_DAYS,
            "mean_patient_mean_sbp_top_reading_decile_mmhg": float(z.loc[z.n_bp >= z.n_bp.quantile(.9), "sbp_mean"].mean()) if n else np.nan,
            "mean_patient_mean_sbp_bottom_reading_decile_mmhg": float(z.loc[z.n_bp <= z.n_bp.quantile(.1), "sbp_mean"].mean()) if n else np.nan,
            "reading_weighted_mean_sbp_mmhg": float(sum(sum(v for _,v in bp[int(sid)]) for sid in z.subject_id if int(sid) in bp)/sum(len(bp[int(sid)]) for sid in z.subject_id if int(sid) in bp)) if n else np.nan,
            "top_reading_decile_share_of_all_qualifying_readings_pct":100*sum(len(bp[int(sid)]) for sid in z.loc[z.n_bp>=z.n_bp.quantile(.9),"subject_id"] if int(sid) in bp)/sum(len(bp[int(sid)]) for sid in z.subject_id if int(sid) in bp) if n else np.nan,
            "source_patient_denominator": base_n, "source_incident_case_denominator": base_events,
            "source_end_non_event_means_no_MI_code_by_source_end_not_continuous_followup": True,
        })
    return pd.DataFrame(rows)


def group_metrics(data: pd.DataFrame, group: str, threshold: int) -> list[dict]:
    rows=[]
    for level, g in data.groupby(group, dropna=False):
        elig = g
        bp = g.loc[g.n_bp >= threshold]
        rows.append({"variable":group,"category":str(level),"bp_min_readings":threshold,"common_index_n":len(g),
                     "common_index_incident_cases":int(g.event.sum()),"bp_eligible_n":len(bp),"bp_eligible_cases":int(bp.event.sum()),
                     "no_recorded_mi_before_source_end_bp_eligible":len(bp)-int(bp.event.sum()),
                     "bp_missing_n":int((g.n_bp<threshold).sum()),"bp_missing_pct":100*float((g.n_bp<threshold).mean()) if len(g) else np.nan,
                     "bp_eligible_retention_pct":100*len(bp)/len(g) if len(g) else np.nan,
                     "median_bp_reading_count":float(bp.n_bp.median()) if len(bp) else np.nan,
                     "mean_of_patient_mean_sbp_mmhg":float(bp.sbp_mean.mean()) if len(bp) else np.nan,
                     "median_of_patient_mean_sbp_mmhg":float(bp.sbp_mean.median()) if len(bp) else np.nan,
                     "mi_events_by_365d_bp_eligible":int(bp.mi_365.sum()) if len(bp) and "mi_365" in bp else np.nan,
                     "confirmed_deaths_by_365d_bp_eligible":int(bp.death_365.sum()) if len(bp) and "death_365" in bp else np.nan,
                     "patients_with_subsequent_encounter_by_365d":int(bp.record_365.sum()) if len(bp) and "record_365" in bp else np.nan,
                     "patients_without_subsequent_encounter_by_365d":int((~bp.record_365).sum()) if len(bp) and "record_365" in bp else np.nan,
                     "death_ascertainment_available_n":int(bp.death_known.sum()) if len(bp) and "death_known" in bp else np.nan,
                     "death_ascertainment_missing_n":int((~bp.death_known).sum()) if len(bp) and "death_known" in bp else np.nan,
                     "pre_window_bmi_available_n":int(bp.bmi_available.sum()) if len(bp) else 0,
                     "pre_window_bmi_missing_pct":100*float((~bp.bmi_available).mean()) if len(bp) else np.nan,
                     "reading_count_q25":float(bp.n_bp.quantile(.25)) if len(bp) else np.nan,
                     "reading_count_q75":float(bp.n_bp.quantile(.75)) if len(bp) else np.nan,
                     "patient_mean_sbp_q05_mmhg":float(bp.sbp_mean.quantile(.05)) if len(bp) else np.nan,
                     "patient_mean_sbp_q25_mmhg":float(bp.sbp_mean.quantile(.25)) if len(bp) else np.nan,
                     "patient_mean_sbp_q75_mmhg":float(bp.sbp_mean.quantile(.75)) if len(bp) else np.nan,
                     "patient_mean_sbp_q95_mmhg":float(bp.sbp_mean.quantile(.95)) if len(bp) else np.nan,
                     "median_within_person_sbp_sd_mmhg":float(bp.sbp_sd.median()) if len(bp) else np.nan})
    return rows


def retained_excluded_metrics(data: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for threshold in (1,2,3,4):
        for status,mask in (("retained",data.n_bp>=threshold),("excluded_below_threshold",data.n_bp<threshold)):
            z=data.loc[mask]
            rows.append({"minimum_valid_readings":threshold,"selection_status":status,"patients":len(z),"incident_cases_any_recorded_followup":int(z.event.sum()),
                         "age_at_window_start_mean":float(z.age_at_window_start.mean()),"age_at_window_start_median":float(z.age_at_window_start.median()),
                         "female_pct":100*float(z.sex_group.eq("Female").mean()) if len(z) else np.nan,
                         "male_pct":100*float(z.sex_group.eq("Male").mean()) if len(z) else np.nan,
                         "diabetes_documented_by_index_pct_descriptive_only":100*float(z.diabetes_documented_by_index.mean()) if len(z) else np.nan,
                         "hypertension_documented_by_index_pct_descriptive_only":100*float(z.hypertension_documented_by_index.mean()) if len(z) else np.nan,
                         "ckd_documented_by_index_pct_descriptive_only":100*float(z.ckd_documented_by_index.mean()) if len(z) else np.nan,
                         "pre_window_bmi_available_pct":100*float(z.bmi_available.mean()) if len(z) else np.nan,
                         "mean_bp_measurement_count":float(z.n_bp.mean()) if len(z) else np.nan,
                         "mean_patient_mean_sbp_mmhg_if_measured":float(z.sbp_mean.mean()) if z.sbp_mean.notna().any() else np.nan,
                         "diagnosis_timing_note":"by-index diagnoses are descriptive selection variables only, not eligible pre-window confounders"})
    return pd.DataFrame(rows)


def followup_tables(index: pd.DataFrame, admissions: pd.DataFrame, archive: Path) -> tuple[pd.DataFrame,pd.DataFrame,dict]:
    obs = parquet_member(archive,"longitudinal/observation_end.parquet",["subject_id","last_discharge","last_admittime","in_hospital_deathtime","dod","observation_end"])
    demo = parquet_member(archive,"longitudinal/patients_demographics.parquet",["subject_id","dod"])
    x=index.merge(obs,on="subject_id",how="left",validate="one_to_one",suffixes=("","_obs")).merge(demo,on="subject_id",how="left",validate="one_to_one",suffixes=("_obs","_demo"))
    # Only agreeing nonmissing DOD dates are classified as confirmed date-level death.
    x["dod_agrees"] = x.dod_obs.notna() & x.dod_demo.notna() & (pd.to_datetime(x.dod_obs).dt.normalize()==pd.to_datetime(x.dod_demo).dt.normalize())
    x["confirmed_dod"] = pd.to_datetime(x.dod_obs).where(x.dod_agrees)
    # A timestamp is quality-screened against the patient admission chronology.
    ad=admissions.loc[admissions.deathtime.notna()].copy()
    ad["death_in_interval"] = (ad.deathtime>=ad.admittime)&(ad.dischtime.notna())&(ad.deathtime<=ad.dischtime)
    dq=ad.groupby("subject_id").agg(death_rows=("deathtime","size"),death_times=("deathtime","nunique"),any_valid_death=("death_in_interval","any"),valid_death_time=("deathtime","max"))
    x["death_rows"] = x.subject_id.map(dq.death_rows).fillna(0)
    x["distinct_death_times"] = x.subject_id.map(dq.death_times).fillna(0)
    x["valid_death_timestamp"] = x.subject_id.map(dq.any_valid_death).fillna(False).astype(bool) & x.subject_id.map(dq.death_times).fillna(0).eq(1)
    x["death_time"] = x.subject_id.map(dq.valid_death_time).where(x.valid_death_timestamp)
    x["death_date"] = x.confirmed_dod.fillna(pd.to_datetime(x.death_time))
    x["death_known"] = x.confirmed_dod.notna() | x.death_time.notna()
    def death_before_tau_and_mi(tau: int) -> pd.Series:
        end_time=pd.to_datetime(x.admittime)+pd.Timedelta(days=tau)
        has_exact=x.death_time.notna()
        exact=(has_exact & (pd.to_datetime(x.death_time)>pd.to_datetime(x.admittime)) & (pd.to_datetime(x.death_time)<=end_time) & (x.event_time.isna() | (pd.to_datetime(x.death_time)<pd.to_datetime(x.event_time))))
        dod_day=pd.to_datetime(x.confirmed_dod).dt.normalize()
        index_day=pd.to_datetime(x.index_date).dt.normalize()
        end_day=end_time.dt.normalize()
        event_day=pd.to_datetime(x.event_time).dt.normalize()
        date_only=(~has_exact & x.confirmed_dod.notna() & (dod_day>index_day) & (dod_day<end_day) & (x.event_time.isna() | (dod_day<event_day)))
        return exact | date_only
    # Record maxima are coverage descriptors only; no global administrative end is asserted.
    aa=admissions.copy()
    max_admit=pd.to_datetime(aa.admittime).max()
    max_discharge=pd.to_datetime(aa.dischtime).max()
    obs_end=pd.to_datetime(obs.observation_end,format="mixed")
    last_disc=pd.to_datetime(obs.last_discharge)
    obs_dod=pd.to_datetime(obs.dod,format="mixed")
    source_semantics={
        "observation_end_source_patients":int(len(obs)),
        "observation_end_equals_dod_day":int((obs_dod.notna() & obs_end.dt.normalize().eq(obs_dod.dt.normalize())).sum()),
        "no_dod_and_observation_end_equals_last_discharge":int((obs_dod.isna() & obs_end.eq(last_disc)).sum()),
        "global_administrative_boundary_verified":0,
    }
    rows=[]
    encounter_history=admissions.merge(x[["subject_id","admittime"]].drop_duplicates(),on="subject_id",how="inner",suffixes=("_enc","_index"))
    later=encounter_history.loc[encounter_history.admittime_enc>encounter_history.admittime_index].copy()
    later["encounter_end"] = pd.to_datetime(later.dischtime).fillna(pd.to_datetime(later.admittime_enc))
    last_later=later.groupby("subject_id").encounter_end.max()
    x["last_subsequent_encounter"] = x.subject_id.map(last_later)
    x["record_365"] = x.subject_id.isin(set(later.loc[later.admittime_enc<=later.admittime_index+pd.Timedelta(days=365),"subject_id"]))
    for tau in HORIZONS:
        end=x.admittime+pd.to_timedelta(tau,unit="D")
        ev=x.event & (pd.to_datetime(x.event_time)<=end)
        death_pre=death_before_tau_and_mi(tau)
        encounter_summary=admissions.merge(x[["subject_id","admittime"]].drop_duplicates(),on="subject_id",suffixes=("_enc","_index"),how="inner")
        encounter_summary=encounter_summary.loc[(encounter_summary.admittime_enc>encounter_summary.admittime_index)&(encounter_summary.admittime_enc<=encounter_summary.admittime_index+pd.to_timedelta(tau,unit="D"))]
        within_ids=set(encounter_summary.subject_id.unique())
        any_record=x.subject_id.isin(within_ids)
        gap=(pd.to_datetime(x.last_subsequent_encounter)-pd.to_datetime(x.admittime)).dt.total_seconds()/86400
        possible=(x.admittime+pd.to_timedelta(tau,unit="D")<=max_admit)
        observed_gap=gap.dropna().to_numpy(dtype=float)
        rows.append({"horizon_days":tau,"common_index_patients":len(x),"all_first_postindex_mi_cases_any_followup":int(x.event.sum()),
                     "first_mi_events_within_horizon":int(ev.sum()),"confirmed_deaths_before_horizon_and_before_mi":int(death_pre.sum()),
                     "patients_with_agreeing_patient_dod":int(x.confirmed_dod.notna().sum()),"patients_with_quality_screened_inhospital_death_timestamp":int(x.valid_death_timestamp.sum()),
                     "patients_with_any_recorded_admission_within_horizon":int(any_record.sum()),"patients_without_subsequent_recorded_admission_within_horizon":int((~any_record).sum()),
                     "unknown_continuous_observation_status_n":len(x),"unknown_continuous_observation_status_pct":100.0,
                     "administrative_horizon_end_before_source_max_admit_n":int(possible.sum()),"database_boundary_verified":False,
                     "patients_with_later_encounter_any_time":int(x.last_subsequent_encounter.notna().sum()),
                     "median_days_to_last_subsequent_encounter_among_observed":float(np.nanmedian(observed_gap)) if len(observed_gap) else np.nan,
                     "q25_days_to_last_subsequent_encounter_among_observed":float(np.nanquantile(observed_gap,.25)) if len(observed_gap) else np.nan,
                     "q75_days_to_last_subsequent_encounter_among_observed":float(np.nanquantile(observed_gap,.75)) if len(observed_gap) else np.nan,
                     "event_time_median_days":float((pd.to_datetime(x.loc[ev,"event_time"])-pd.to_datetime(x.loc[ev,"admittime"])).dt.total_seconds().median()/86400) if ev.any() else np.nan,
                     "event_time_q25_days":float((pd.to_datetime(x.loc[ev,"event_time"])-pd.to_datetime(x.loc[ev,"admittime"])).dt.total_seconds().quantile(.25)/86400) if ev.any() else np.nan,
                     "event_time_q75_days":float((pd.to_datetime(x.loc[ev,"event_time"])-pd.to_datetime(x.loc[ev,"admittime"])).dt.total_seconds().quantile(.75)/86400) if ev.any() else np.nan,
                     "source_max_admittime_observed_only":str(max_admit),"source_max_dischtime_observed_only":str(max_discharge),
                     "no_subsequent_admission_is_not_known_survival_or_continuous_observation":True})
    return pd.DataFrame(rows),x,{"max_admittime":str(max_admit),"max_dischtime":str(max_discharge),**source_semantics}


def support_diagnostics(data: pd.DataFrame) -> pd.DataFrame:
    """Compare held-out flexible quantile and local-neighbour support diagnostics."""
    z=data.loc[(data.n_bp>=2)&data.sbp_mean.notna()&data.age_at_window_start.notna()].copy().reset_index(drop=True)
    if len(z)<1000:
        return pd.DataFrame([{"method":"not_estimable","reason":"fewer than 1,000 candidate patients"}])
    z["shifted_sbp"] = z.sbp_mean - 10*(z.sbp_mean>=130)
    z["age_sex_profile"] = z.age_group.astype(str)+"|"+z.sex_group.astype(str)
    bmi_median=float(z.bmi.median()) if z.bmi.notna().any() else 25.0
    z["bmi_imputed"] = z.bmi.fillna(bmi_median)
    z["bmi_missing"] = z.bmi.isna().astype(int)
    z["male"] = z.sex_group.eq("Male").astype(int)
    feature_cols=["age_at_window_start","male","bmi_imputed","bmi_missing"]
    X=z[feature_cols].astype(float).to_numpy(); y=z.sbp_mean.to_numpy(); shifted=z.shifted_sbp.to_numpy()
    rng=np.random.default_rng(20261117)
    train,test=train_test_split(np.arange(len(z)),test_size=.2,random_state=20261117)
    rows=[]
    marginal_out=(shifted<np.min(y))|(shifted>np.max(y))
    rows.append({"method":"marginal_range_reference_only","settings":"Observed patient-level mean SBP global min/max; not conditional positivity evidence","n_evaluated":len(z),
                 "shifted_outside_conditional_support_n":int(marginal_out.sum()),"shifted_outside_conditional_support_pct":100*float(marginal_out.mean()),
                 "observed_sbp_outside_conditional_support_pct":0.0,"median_predicted_conditional_width_mmhg":float(np.max(y)-np.min(y)),
                 "observed_sbp_min_mmhg":float(np.min(y)),"observed_sbp_max_mmhg":float(np.max(y)),"shifted_sbp_min_mmhg":float(np.min(shifted)),"shifted_sbp_max_mmhg":float(np.max(shifted)),
                 "density_ratio_median":np.nan,"density_ratio_q05":np.nan,"density_ratio_q95":np.nan,"density_ratio_ess":np.nan,
                 "covariates_not_available_pre_window":"diabetes, hypertension, CKD (all have no documented pre-window records under earliest-index rule)"})
    # Cross-fitted-in-spirit held-out 1st/99th conditional quantiles; training is support-only.
    qlo=HistGradientBoostingRegressor(loss="quantile",quantile=.01,max_iter=120,max_leaf_nodes=15,min_samples_leaf=80,l2_regularization=5,random_state=19)
    qhi=HistGradientBoostingRegressor(loss="quantile",quantile=.99,max_iter=120,max_leaf_nodes=15,min_samples_leaf=80,l2_regularization=5,random_state=29)
    qlo.fit(X[train],y[train]); qhi.fit(X[train],y[train])
    lo,hi=qlo.predict(X[test]),qhi.predict(X[test])
    out=(shifted[test]<lo)|(shifted[test]>hi)
    rows.append({"method":"heldout_hist_gradient_boosted_conditional_quantiles","settings":"80/20 fixed patient split; q=.01/.99; age, sex, pre-window BMI+missingness","n_evaluated":len(test),
                 "shifted_outside_conditional_support_n":int(out.sum()),"shifted_outside_conditional_support_pct":100*float(out.mean()),
                 "observed_sbp_outside_conditional_support_pct":100*float(((y[test]<lo)|(y[test]>hi)).mean()),
                 "median_predicted_conditional_width_mmhg":float(np.median(hi-lo)),"density_ratio_median":np.nan,"density_ratio_q05":np.nan,"density_ratio_q95":np.nan,"density_ratio_ess":np.nan,
                 "covariates_not_available_pre_window":"diabetes, hypertension, CKD (all have no documented pre-window records under earliest-index rule)"})
    # Local conditional support/density ratio. The query's own observation is excluded.
    scaler=StandardScaler().fit(X); Xs=scaler.transform(X)
    max_k=min(251,len(z))
    nn=NearestNeighbors(n_neighbors=max_k,algorithm="brute",metric="euclidean",n_jobs=-1).fit(Xs)
    dist,ind=nn.kneighbors(Xs,return_distance=True)
    # Normally self is first; explicitly remove matching row from each neighbor set.
    nd=np.empty((len(z),max_k-1),dtype=float); ni=np.empty((len(z),max_k-1),dtype=int)
    for i in range(len(z)):
        keep=ind[i]!=i
        nd[i]=dist[i][keep][:max_k-1]; ni[i]=ind[i][keep][:max_k-1]
    for k in (100,250):
        k=min(k,nd.shape[1]); local=y[ni[:,:k]]
        q1,q99=np.quantile(local,[.01,.99],axis=1)
        bad=(shifted<q1)|(shifted>q99)
        rows.append({"method":f"local_knn_conditional_quantile_k{k}","settings":"Standardized age, sex, pre-window BMI and BMI-missing indicator; leave-self-out; local empirical q=.01/.99","n_evaluated":len(z),
                     "shifted_outside_conditional_support_n":int(bad.sum()),"shifted_outside_conditional_support_pct":100*float(bad.mean()),
                     "observed_sbp_outside_conditional_support_pct":100*float(((y<q1)|(y>q99)).mean()),"median_predicted_conditional_width_mmhg":float(np.median(q99-q1)),
                     "density_ratio_median":np.nan,"density_ratio_q05":np.nan,"density_ratio_q95":np.nan,"density_ratio_ess":np.nan,
                     "covariates_not_available_pre_window":"diabetes, hypertension, CKD (all have no documented pre-window records under earliest-index rule)"})
        if k==250:
            for profile in ("age_group","sex_group","bmi_available","age_sex_profile"):
                for level in z[profile].unique():
                    mask=z[profile].to_numpy()==level
                    rows.append({"method":"local_knn_conditional_quantile_profile_k250","settings":f"profile={profile}; category={level}; q=.01/.99; leave-self-out","n_evaluated":int(mask.sum()),
                                 "shifted_outside_conditional_support_n":int(bad[mask].sum()),"shifted_outside_conditional_support_pct":100*float(bad[mask].mean()),
                                 "observed_sbp_outside_conditional_support_pct":100*float(((y[mask]<q1[mask])|(y[mask]>q99[mask])).mean()),
                                 "median_predicted_conditional_width_mmhg":float(np.median(q99[mask]-q1[mask])),"density_ratio_median":np.nan,"density_ratio_q05":np.nan,"density_ratio_q95":np.nan,"density_ratio_ess":np.nan,
                                 "covariates_not_available_pre_window":"diabetes, hypertension, CKD have no pre-window variation"})
        if k==250:
            d=nd[:,:k]; hcov=np.maximum(d[:,-1],.05); w=np.exp(-.5*(d/hcov[:,None])**2)
            neigh_sbp=y[ni[:,:k]]
            for hsbp in (5.0,10.0):
                f0=(w*np.exp(-.5*((neigh_sbp-y[:,None])/hsbp)**2)).sum(axis=1)/w.sum(axis=1)
                f1=(w*np.exp(-.5*((neigh_sbp-shifted[:,None])/hsbp)**2)).sum(axis=1)/w.sum(axis=1)
                ratio=np.divide(f1,f0,out=np.full_like(f1,np.nan),where=f0>0)
                finite=ratio[np.isfinite(ratio)]
                ess=float((finite.sum()**2)/(np.square(finite).sum())) if len(finite) else np.nan
                rows.append({"method":f"local_knn_kernel_density_ratio_k{k}_sbp_bandwidth_{int(hsbp)}","settings":"Leave-self-out local Gaussian kernel ratio f(A_shift|L)/f(A|L); standardized L, k=250","n_evaluated":len(z),
                             "shifted_outside_conditional_support_n":np.nan,"shifted_outside_conditional_support_pct":np.nan,"observed_sbp_outside_conditional_support_pct":np.nan,
                             "median_predicted_conditional_width_mmhg":np.nan,"density_ratio_median":float(np.median(finite)),"density_ratio_q05":float(np.quantile(finite,.05)),"density_ratio_q95":float(np.quantile(finite,.95)),"density_ratio_ess":ess,
                             "density_ratio_below_0_1_pct":100*float((finite<.1).mean()),"density_ratio_above_10_pct":100*float((finite>10).mean()),
                             "density_ratio_q99":float(np.quantile(finite,.99)),"density_ratio_max":float(np.max(finite)),
                             "covariates_not_available_pre_window":"diabetes, hypertension, CKD (all have no documented pre-window records under earliest-index rule)"})
                if hsbp==10.0:
                    for band,mask in (("120_to_lt130",(y>=120)&(y<130)),("130_to_lt140",(y>=130)&(y<140)),("140_to_lt150",(y>=140)&(y<150)),("150_plus",y>=150)):
                        rr=ratio[mask]; rr=rr[np.isfinite(rr)]
                        if len(rr):
                            rows.append({"method":"local_knn_density_ratio_near_threshold","settings":f"observed SBP band {band}; local Gaussian h=10; k=250","n_evaluated":len(rr),
                                         "shifted_outside_conditional_support_n":np.nan,"shifted_outside_conditional_support_pct":np.nan,"observed_sbp_outside_conditional_support_pct":np.nan,"median_predicted_conditional_width_mmhg":np.nan,
                                         "density_ratio_median":float(np.median(rr)),"density_ratio_q05":float(np.quantile(rr,.05)),"density_ratio_q95":float(np.quantile(rr,.95)),
                                         "density_ratio_ess":float(rr.sum()**2/np.square(rr).sum()),"density_ratio_below_0_1_pct":100*float((rr<.1).mean()),"density_ratio_above_10_pct":100*float((rr>10).mean()),
                                         "density_ratio_q99":float(np.quantile(rr,.99)),"density_ratio_max":float(np.max(rr)),
                                         "covariates_not_available_pre_window":"diabetes, hypertension, CKD have no pre-window variation"})
    # Transparent subgroup diagnostics using observed local SBP ranges by predeclared covariate strata.
    for v in ("age_group","sex_group","diabetes_group","hypertension","ckd","bmi_available"):
        for level,g in z.groupby(v,dropna=False):
            shifted_g=g.sbp_mean-10*(g.sbp_mean>=130)
            rows.append({"method":"descriptive_profile_support","settings":f"profile={v}; level={level}; empirical observed min/max only (not sufficient alone)","n_evaluated":len(g),
                         "shifted_outside_conditional_support_n":int(((shifted_g<g.sbp_mean.min())|(shifted_g>g.sbp_mean.max())).sum()),
                         "shifted_outside_conditional_support_pct":100*float(((shifted_g<g.sbp_mean.min())|(shifted_g>g.sbp_mean.max())).mean()),
                         "observed_sbp_outside_conditional_support_pct":0.0,"median_predicted_conditional_width_mmhg":float(g.sbp_mean.max()-g.sbp_mean.min()),
                         "density_ratio_median":np.nan,"density_ratio_q05":np.nan,"density_ratio_q95":np.nan,"density_ratio_ess":np.nan,
                         "profile_event_n":int(g.event.sum()),"covariates_not_available_pre_window":"diabetes, hypertension, CKD are constant documented-absence indicators"})
    return pd.DataFrame(rows)


def write_csv(path: Path, rows) -> None:
    pd.DataFrame(rows).to_csv(path,index=False)


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--longitudinal",type=Path,default=Path("data/raw/longitudinal.rar"))
    ap.add_argument("--omr",type=Path,default=Path("data/raw/omr.rar"))
    ap.add_argument("--output-dir",type=Path,default=Path("revised/phase2/aggregates"))
    args=ap.parse_args()
    if not args.longitudinal.is_file() or not args.omr.is_file(): raise FileNotFoundError("Required local archive missing")
    args.output_dir.mkdir(parents=True,exist_ok=True)
    idx, adm, meta=build_ephemeral_index(args.longitudinal)
    print(f"Built transient aggregate risk set: {meta}", flush=True)
    bp,bmi,omr_counts=collect_omr(args.omr,idx)
    print(f"Streamed OMR; valid BP patients={len(bp):,}; QC counts={omr_counts}", flush=True)
    cov=add_covariates(idx,adm,args.longitudinal,bmi)
    data,_=summarize_bp(cov,bp)
    thresholds=aggregate_thresholds(data,bp)
    thresholds.to_csv(args.output_dir/"phase2_0r_bp_thresholds.csv",index=False)
    horizons, death_enriched, source_boundary=followup_tables(idx,adm,args.longitudinal)
    horizons.to_csv(args.output_dir/"phase2_0r_horizons.csv",index=False)
    detail=death_enriched.set_index("subject_id")
    data["death_known"] = data.subject_id.map(detail.death_known).fillna(False).astype(bool)
    data["death_date"] = data.subject_id.map(detail.death_date)
    data["death_time"] = data.subject_id.map(detail.death_time)
    data["confirmed_dod"] = data.subject_id.map(detail.confirmed_dod)
    data["record_365"] = data.subject_id.map(detail.record_365).fillna(False).astype(bool)
    end365=pd.to_datetime(data.admittime)+pd.Timedelta(days=365)
    data["mi_365"] = data.event & (pd.to_datetime(data.event_time)<=end365)
    exact_death=data.death_time.notna()
    exact_365=exact_death & (pd.to_datetime(data.death_time)>pd.to_datetime(data.admittime)) & (pd.to_datetime(data.death_time)<=end365) & (data.event_time.isna()|(pd.to_datetime(data.death_time)<pd.to_datetime(data.event_time)))
    dod_day=pd.to_datetime(data.confirmed_dod).dt.normalize(); index_day=pd.to_datetime(data.index_date).dt.normalize(); end_day=end365.dt.normalize(); event_day=pd.to_datetime(data.event_time).dt.normalize()
    date_365=(~exact_death)&data.confirmed_dod.notna()&(dod_day>index_day)&(dod_day<end_day)&(data.event_time.isna()|(dod_day<event_day))
    data["death_365"] = exact_365|date_365
    subgroup=[]
    for g in ("age_group","age_group_at_index","sex_group","diabetes_group","diabetes_by_index_group"):
        for t in (1,2,3,4): subgroup.extend(group_metrics(data,g,t))
    subgroup_df=pd.DataFrame(subgroup)
    subgroup_df["precision_assumption"] = "Illustrative complete independent binary outcome; p scenario only; not causal policy-effect precision"
    subgroup_df["mde_risk_difference_p01"] = np.nan
    subgroup_df["mde_risk_difference_p025"] = np.nan
    subgroup_df["mde_risk_difference_p05"] = np.nan
    subgroup_df["ci95_halfwidth_p025"] = np.nan
    from scipy.stats import norm
    for i,row in subgroup_df.iterrows():
        n1=int(row.bp_eligible_n); total=int(row.bp_min_readings and data.n_bp.ge(int(row.bp_min_readings)).sum()); n0=max(total-n1,0)
        if n1 and n0:
            se_factor=math.sqrt(1/n1+1/n0)
            for pval,col in ((.01,"mde_risk_difference_p01"),(.025,"mde_risk_difference_p025"),(.05,"mde_risk_difference_p05")):
                subgroup_df.at[i,col]=(norm.ppf(1-.05/(2*3))+norm.ppf(.8))*math.sqrt(pval*(1-pval))*se_factor
            subgroup_df.at[i,"ci95_halfwidth_p025"]=norm.ppf(.975)*math.sqrt(.025*(1-.025))*se_factor
    subgroup_df.to_csv(args.output_dir/"phase2_0r_subgroups.csv",index=False)
    retained_excluded_metrics(data).to_csv(args.output_dir/"phase2_0r_bp_retained_excluded.csv",index=False)
    support=support_diagnostics(data)
    support.to_csv(args.output_dir/"phase2_0r_conditional_support.csv",index=False)
    death_rows=[]
    def drow(metric, value, denominator, unit, definition): death_rows.append({"metric":metric,"value":int(value),"denominator":int(denominator),"unit":unit,"definition":definition})
    denom=len(death_enriched)
    drow("common_index_patients",denom,denom,"patients","Transient reconstructed common index; aggregate only")
    drow("patient_DOD_available_both_sources_and_agree",int(death_enriched.dod_agrees.sum()),denom,"patients","Nonmissing observation_end and demographics DOD agree by subject")
    drow("patient_DOD_missing_or_not_agreeing",int((~death_enriched.dod_agrees).sum()),denom,"patients","Unknown vital status; not survival")
    drow("quality_screened_unique_inhospital_death_timestamp",int(death_enriched.valid_death_timestamp.sum()),denom,"patients","Exactly one distinct admission death time, within an admission interval")
    drow("multiple_distinct_admission_death_times",int((death_enriched.distinct_death_times>1).sum()),denom,"patients","Conflicting distinct admission-level death times")
    drow("any_source_consistent_death_record",int(death_enriched.death_known.sum()),denom,"patients","DOD agreement or quality-screened in-hospital death timestamp; overlapping sources counted once")
    dod_day=pd.to_datetime(death_enriched.confirmed_dod).dt.normalize(); index_day=pd.to_datetime(death_enriched.index_date).dt.normalize()
    drow("agreeing_DOD_calendar_day_before_index",int((death_enriched.confirmed_dod.notna()&(dod_day<index_day)).sum()),int(death_enriched.dod_agrees.sum()),"patients","Date-precision DOD strictly before index date")
    drow("agreeing_DOD_same_calendar_day_as_index",int((death_enriched.confirmed_dod.notna()&(dod_day==index_day)).sum()),int(death_enriched.dod_agrees.sum()),"patients","Date-precision tie; within-day order unknown")
    drow("agreeing_DOD_calendar_day_after_index",int((death_enriched.confirmed_dod.notna()&(dod_day>index_day)).sum()),int(death_enriched.dod_agrees.sum()),"patients","Date-precision DOD strictly after index date")
    drow("quality_timestamp_before_index_time",int((death_enriched.death_time.notna()&(pd.to_datetime(death_enriched.death_time)<pd.to_datetime(death_enriched.admittime))).sum()),int(death_enriched.death_time.notna().sum()),"patients","Unique in-interval death timestamp strictly before index timestamp")
    drow("quality_timestamp_after_index_time",int((death_enriched.death_time.notna()&(pd.to_datetime(death_enriched.death_time)>pd.to_datetime(death_enriched.admittime))).sum()),int(death_enriched.death_time.notna().sum()),"patients","Unique in-interval death timestamp strictly after index timestamp")
    drow("source_boundary_unknown_continuous_followup",denom,denom,"patients","Individual observation after last encounter is unknown for all participants")
    for _,r in horizons.iterrows():
        drow(f"confirmed_death_before_MI_by_{int(r.horizon_days)}d",int(r.confirmed_deaths_before_horizon_and_before_mi),denom,"patients","Only source-consistent date/timestamp; same-day death-MI order not presumed")
    death_rows.extend([
        {"metric":"observation_end_source_patients","value":source_boundary["observation_end_source_patients"],"denominator":source_boundary["observation_end_source_patients"],"unit":"patients","definition":"Observation-end source universe; distinct subject_id rows"},
        {"metric":"observation_end_equals_dod_day","value":source_boundary["observation_end_equals_dod_day"],"denominator":source_boundary["observation_end_source_patients"],"unit":"patients","definition":"Per-patient observation_end equals recorded DOD calendar date"},
        {"metric":"no_dod_and_observation_end_equals_last_discharge","value":source_boundary["no_dod_and_observation_end_equals_last_discharge"],"denominator":source_boundary["observation_end_source_patients"],"unit":"patients","definition":"No DOD; per-patient observation_end equals last discharge, not continuous follow-up"},
        {"metric":"global_administrative_boundary_verified","value":0,"denominator":1,"unit":"verification flag","definition":"No source-wide extraction cutoff verified"},
    ])
    pd.DataFrame(death_rows).to_csv(args.output_dir/"phase2_0r_death_index_reconciliation.csv",index=False)
    # Persist a small aggregate metadata file only.
    pd.DataFrame([{"metric":k,"value":v} for k,v in {**meta,**{f"omr_{k}":v for k,v in omr_counts.items()},**{f"source_{k}":v for k,v in source_boundary.items()}}.items()]).to_csv(args.output_dir/"phase2_0r_run_metadata.csv",index=False)
    print(f"Aggregate feasibility complete: {len(idx):,} transient index-linked patients; outputs contain aggregate rows only.")
    print(f"Index reconciliation: {meta}")


if __name__=="__main__":
    main()
