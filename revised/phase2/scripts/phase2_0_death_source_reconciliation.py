"""Aggregate-only reconciliation of longitudinal archive death sources.

Reads selected Parquet members from the local longitudinal RAR through Windows
tar, uses patient/admission linkage in memory, and writes only aggregate counts.
It does not build the revised common-index cohort or emit row-level records.
"""

from __future__ import annotations

import argparse
import io
import json
import subprocess
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


def read_member(archive: Path, member: str, columns: list[str] | None = None) -> pd.DataFrame:
    result = subprocess.run(
        ["tar", "-xOf", str(archive), member],
        check=True,
        capture_output=True,
    )
    table = pq.read_table(io.BytesIO(result.stdout), columns=columns)
    return table.to_pandas()


def count_row(metric: str, value: int, denominator: int, unit: str, source: str, definition: str) -> dict:
    return {
        "metric": metric,
        "value": int(value),
        "denominator": int(denominator),
        "unit": unit,
        "source": source,
        "definition": definition,
    }


def reconcile(archive: Path) -> pd.DataFrame:
    adm = read_member(
        archive,
        "longitudinal/admissions_chronology.parquet",
        ["subject_id", "hadm_id", "admittime", "dischtime", "deathtime", "hospital_expire_flag"],
    )
    obs = read_member(
        archive,
        "longitudinal/observation_end.parquet",
        ["subject_id", "in_hospital_deathtime", "dod", "observation_end"],
    )
    demo = read_member(
        archive,
        "longitudinal/patients_demographics.parquet",
        ["subject_id", "dod"],
    )
    diag = read_member(
        archive,
        "longitudinal/diagnoses_all.parquet",
        ["subject_id", "hadm_id", "icd_code", "icd_version"],
    )

    # Source keys and timestamps are checked in memory; only summaries are returned.
    rows: list[dict] = []
    adm_death = adm.loc[adm["deathtime"].notna()].copy()
    obs_dod = obs.loc[obs["dod"].notna(), ["subject_id", "dod"]].copy()
    demo_dod = demo.loc[demo["dod"].notna(), ["subject_id", "dod"]].copy()
    obs_hosp_death = obs.loc[obs["in_hospital_deathtime"].notna()].copy()
    death_row_summary = adm_death.groupby("subject_id").agg(
        rows=("deathtime", "size"), distinct_times=("deathtime", "nunique")
    )
    repeated_same_time = int(((death_row_summary["rows"] > 1) & (death_row_summary["distinct_times"] == 1)).sum())
    repeated_different_times = int(((death_row_summary["rows"] > 1) & (death_row_summary["distinct_times"] > 1)).sum())

    rows.extend(
        [
            count_row("admission_rows", len(adm), adm["hadm_id"].nunique(), "admissions", "admissions_chronology.parquet", "Rows and distinct hadm_id."),
            count_row("admissions_with_deathtime", len(adm_death), len(adm), "admissions", "admissions_chronology.parquet", "Nonmissing admission-level deathtime."),
            count_row("unique_patients_with_admission_deathtime", adm_death["subject_id"].nunique(), adm["subject_id"].nunique(), "patients", "admissions_chronology.parquet", "Distinct subjects with one or more admission deathtimes."),
            count_row("admission_deathtime_after_admit_and_by_discharge", int((adm_death["deathtime"].ge(adm_death["admittime"]) & adm_death["deathtime"].le(adm_death["dischtime"])).sum()), len(adm_death), "admissions", "admissions_chronology.parquet", "Death timestamp within that admission interval."),
            count_row("admission_deathtime_before_admit", int(adm_death["deathtime"].lt(adm_death["admittime"]).sum()), len(adm_death), "admissions", "admissions_chronology.parquet", "Death timestamp earlier than admission timestamp."),
            count_row("admission_deathtime_after_discharge", int((adm_death["dischtime"].notna() & adm_death["deathtime"].gt(adm_death["dischtime"])).sum()), len(adm_death), "admissions", "admissions_chronology.parquet", "Death timestamp later than discharge timestamp."),
            count_row("admission_deathtime_with_missing_discharge", int(adm_death["dischtime"].isna().sum()), len(adm_death), "admissions", "admissions_chronology.parquet", "Death timestamp present while dischtime is missing."),
            count_row("patients_with_multiple_admission_deathtimes", int((adm_death.groupby("subject_id").size() > 1).sum()), adm_death["subject_id"].nunique(), "patients", "admissions_chronology.parquet", "Patients with more than one admission-level death timestamp."),
            count_row("excess_admission_deathtime_rows_over_unique_patients", len(adm_death) - adm_death["subject_id"].nunique(), len(adm_death), "admission rows", "admissions_chronology.parquet", "Admission timestamp rows minus distinct patients."),
            count_row("patients_with_repeated_death_rows_same_timestamp", repeated_same_time, adm_death["subject_id"].nunique(), "patients", "admissions_chronology.parquet", "Multiple admission death rows but one distinct timestamp."),
            count_row("patients_with_repeated_death_rows_different_timestamps", repeated_different_times, adm_death["subject_id"].nunique(), "patients", "admissions_chronology.parquet", "Multiple admission death rows and multiple distinct timestamps."),
            count_row("observation_end_patients", len(obs), obs["subject_id"].nunique(), "patients", "observation_end.parquet", "Rows and distinct subject_id."),
            count_row("patients_with_observation_end_dod", len(obs_dod), len(obs), "patients", "observation_end.parquet", "Nonmissing patient-level DOD."),
            count_row("patients_with_in_hospital_death_timestamp", len(obs_hosp_death), len(obs), "patients", "observation_end.parquet", "Nonmissing patient-level in-hospital death timestamp."),
            count_row("demographics_patients", len(demo), demo["subject_id"].nunique(), "patients", "patients_demographics.parquet", "Rows and distinct subject_id."),
            count_row("patients_with_demographics_dod", len(demo_dod), len(demo), "patients", "patients_demographics.parquet", "Nonmissing patient-level DOD."),
        ]
    )

    # Compare DOD sources only on shared patient keys; dates have day precision.
    dod_join = demo.rename(columns={"dod": "demo_dod"}).merge(
        obs[["subject_id", "dod"]].rename(columns={"dod": "obs_dod"}),
        on="subject_id",
        how="inner",
        validate="one_to_one",
    )
    both = dod_join["demo_dod"].notna() & dod_join["obs_dod"].notna()
    exact = dod_join["demo_dod"].eq(dod_join["obs_dod"])
    rows.extend(
        [
            count_row("dod_source_shared_patient_keys", len(dod_join), len(demo), "patients", "patients_demographics.parquet + observation_end.parquet", "Shared subject_id keys."),
            count_row("dod_nonmissing_both_sources", int(both.sum()), len(dod_join), "patients", "patients_demographics.parquet + observation_end.parquet", "Both patient-level DOD fields nonmissing."),
            count_row("dod_exact_date_agreement", int((both & exact).sum()), int(both.sum()), "patients", "patients_demographics.parquet + observation_end.parquet", "Equal dates among shared nonmissing DOD values."),
            count_row("dod_date_disagreement", int((both & ~exact).sum()), int(both.sum()), "patients", "patients_demographics.parquet + observation_end.parquet", "Unequal dates among shared nonmissing DOD values."),
            count_row("dod_only_in_demographics", int((dod_join["demo_dod"].notna() & dod_join["obs_dod"].isna()).sum()), len(dod_join), "patients", "patients_demographics.parquet + observation_end.parquet", "DOD present only in demographics source."),
            count_row("dod_only_in_observation_end", int((dod_join["demo_dod"].isna() & dod_join["obs_dod"].notna()).sum()), len(dod_join), "patients", "patients_demographics.parquet + observation_end.parquet", "DOD present only in observation-end source."),
        ]
    )

    # First acute-coded admission across the diagnosis source (not the revised cohort).
    code = diag["icd_code"].astype("string").str.upper().str.replace(".", "", regex=False)
    version = pd.to_numeric(diag["icd_version"], errors="coerce")
    acute = ((version.eq(9) & code.str.startswith("410", na=False)) | (version.eq(10) & (code.str.startswith("I21", na=False) | code.str.startswith("I22", na=False))))
    acute_adm = diag.loc[acute, ["subject_id", "hadm_id"]].drop_duplicates().merge(
        adm[["subject_id", "hadm_id", "admittime"]],
        on=["subject_id", "hadm_id"],
        how="inner",
        validate="many_to_one",
    )
    first_acute = acute_adm.sort_values(["subject_id", "admittime", "hadm_id"]).drop_duplicates("subject_id")

    # Date-level and timestamp-level death ordering is kept separate.
    first_with_dod = first_acute.merge(obs[["subject_id", "dod"]], on="subject_id", how="left", validate="one_to_one")
    dated = first_with_dod.loc[first_with_dod["dod"].notna()].copy()
    dod_day = pd.to_datetime(dated["dod"]).dt.normalize()
    mi_day = pd.to_datetime(dated["admittime"]).dt.normalize()
    rows.extend(
        [
            count_row("patients_with_first_acute_mi_admission", len(first_acute), adm["subject_id"].nunique(), "patients", "diagnoses_all.parquet + admissions_chronology.parquet", "Distinct patients with an acute ICD-coded admission; all-history source universe, not common-index cohort."),
            count_row("first_acute_mi_patients_with_patient_dod", len(dated), len(first_acute), "patients", "diagnoses_all.parquet + admissions_chronology.parquet + observation_end.parquet", "First acute admission has nonmissing patient DOD."),
            count_row("dod_calendar_day_before_first_acute_mi_admission", int((dod_day < mi_day).sum()), len(dated), "patients", "Same sources", "DOD day strictly before first acute admission date."),
            count_row("dod_calendar_day_same_as_first_acute_mi_admission", int((dod_day == mi_day).sum()), len(dated), "patients", "Same sources", "Date-only tie; within-day ordering indeterminate."),
            count_row("dod_calendar_day_after_first_acute_mi_admission", int((dod_day > mi_day).sum()), len(dated), "patients", "Same sources", "DOD day after first acute admission date."),
        ]
    )

    first_with_death_ts = first_acute.merge(
        obs[["subject_id", "in_hospital_deathtime"]],
        on="subject_id",
        how="left",
        validate="one_to_one",
    )
    timed = first_with_death_ts.loc[first_with_death_ts["in_hospital_deathtime"].notna()]
    death_ts = pd.to_datetime(timed["in_hospital_deathtime"])
    first_mi_ts = pd.to_datetime(timed["admittime"])
    rows.extend(
        [
            count_row("first_acute_mi_patients_with_in_hospital_death_timestamp", len(timed), len(first_acute), "patients", "diagnoses_all.parquet + admissions_chronology.parquet + observation_end.parquet", "First acute admission has nonmissing patient-level in-hospital death timestamp."),
            count_row("in_hospital_death_timestamp_before_first_acute_mi_admit", int((death_ts < first_mi_ts).sum()), len(timed), "patients", "Same sources", "Timestamp strictly before first acute admission timestamp."),
            count_row("in_hospital_death_timestamp_equal_first_acute_mi_admit", int((death_ts == first_mi_ts).sum()), len(timed), "patients", "Same sources", "Exact timestamp tie."),
            count_row("in_hospital_death_timestamp_after_first_acute_mi_admit", int((death_ts > first_mi_ts).sum()), len(timed), "patients", "Same sources", "Timestamp after first acute admission timestamp."),
        ]
    )

    # Admission death timestamps versus patient-level in-hospital death timestamps.
    by_adm_patient = adm_death.sort_values("deathtime").drop_duplicates("subject_id", keep="last")
    death_join = by_adm_patient[["subject_id", "deathtime"]].merge(
        obs_hosp_death[["subject_id", "in_hospital_deathtime"]],
        on="subject_id",
        how="outer",
        validate="one_to_one",
    )
    both_ts = death_join["deathtime"].notna() & death_join["in_hospital_deathtime"].notna()
    ts_equal = pd.to_datetime(death_join["deathtime"]).eq(pd.to_datetime(death_join["in_hospital_deathtime"]))
    rows.extend(
        [
            count_row("patients_with_both_in_hospital_death_timestamps", int(both_ts.sum()), len(death_join), "patients", "admissions_chronology.parquet + observation_end.parquet", "Patient-level join of latest admission deathtime to in-hospital death timestamp."),
            count_row("exact_timestamp_agreement_between_death_sources", int((both_ts & ts_equal).sum()), int(both_ts.sum()), "patients", "admissions_chronology.parquet + observation_end.parquet", "Exact timestamp agreement among patients with both timestamps."),
            count_row("timestamp_disagreement_between_death_sources", int((both_ts & ~ts_equal).sum()), int(both_ts.sum()), "patients", "admissions_chronology.parquet + observation_end.parquet", "Different timestamps among patients with both timestamps."),
            count_row("patient_dod_same_calendar_day_as_in_hospital_timestamp", int((both_ts & pd.to_datetime(death_join["deathtime"]).dt.normalize().eq(pd.to_datetime(death_join["in_hospital_deathtime"]).dt.normalize())).sum()), int(both_ts.sum()), "patients", "admissions_chronology.parquet + observation_end.parquet", "DOD day agrees with linked timestamp day among patients with both."),
        ]
    )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, default=Path("data/raw/longitudinal.rar"))
    parser.add_argument("--output", type=Path, default=Path("revised/phase2/aggregates/death_source_reconciliation.csv"))
    args = parser.parse_args()
    if not args.archive.is_file():
        raise FileNotFoundError(f"Longitudinal archive not found: {args.archive}")
    result = reconcile(args.archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} aggregate metrics to {args.output}")


if __name__ == "__main__":
    main()
