"""Build canonical aggregate feasibility tables in ``aggregates/``."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "aggregates"


def main() -> None:
    bp = pd.read_csv(AGG / "phase2_0r_bp_thresholds.csv").rename(columns={
        "eligible_retention_pct_of_common_index": "eligible_retention_pct_of_authoritative_common_index_168915",
        "case_retention_pct_of_common_index_incident_cases": "case_retention_pct_of_authoritative_incident_cases_3207",
        "no_recorded_first_mi_before_source_end": "no_recorded_first_mi_by_source_end_not_verified_followup",
    })
    bp["source_members"] = "longitudinal/admissions_chronology.parquet; diagnoses_all.parquet; patients_demographics.parquet; OMR omr.csv"
    bp["population_definition"] = "common index; no documented acute or historical MI on/before index; OMR exposure window candidate"
    bp["bp_window_and_qc"] = "[index_date-730 days,index_date); chartdate < index_date; parsed SBP 60-260, DBP 20-160, SBP>DBP"
    bp["units"] = "SBP/DBP mmHg; gaps days; frequency readings per 365.25 days"
    bp["missingness_interpretation"] = "No qualifying valid OMR reading is missing exposure; no recorded MI by source end is not known event-free follow-up"
    bp.to_csv(AGG / "PHASE2_BP_THRESHOLD_COMPARISON.csv", index=False)
    horizons = pd.read_csv(AGG / "phase2_0r_horizons.csv").rename(columns={
        "administrative_horizon_end_before_source_max_admit_n": "horizon_end_calendar_date_le_global_record_max_not_verified_opportunity_n",
        "patients_with_any_recorded_admission_within_horizon": "patients_with_any_later_recorded_admission_within_horizon",
        "patients_without_subsequent_recorded_admission_within_horizon": "patients_without_later_recorded_admission_within_horizon",
    })
    horizons["source_members"] = "longitudinal/admissions_chronology.parquet; diagnoses_all.parquet; observation_end.parquet; patients_demographics.parquet"
    horizons["event_definition"] = "first ICD-9 410* or ICD-10 I21*/I22* admission strictly after index calendar date"
    horizons["time_unit_and_origin"] = "elapsed days from index admission timestamp; fixed horizons 90/180/365/730"
    horizons["followup_missingness_definition"] = "no continuous observation indicator; no subsequent admission is not survival or MI-free"
    horizons.to_csv(AGG / "PHASE2_FOLLOWUP_HORIZON_COMPARISON.csv", index=False)
    old = pd.read_csv(AGG / "death_source_reconciliation.csv")
    current = pd.read_csv(AGG / "phase2_0r_death_index_reconciliation.csv")
    old["scope"] = "source_universe_or_all_history_as_stated_in_definition"
    old["source"] = old["source"].fillna("source-specific table in metric definition")
    current["source"] = "transient common-index aggregate linkage; selected longitudinal archive members"
    current["scope"] = "reconciled_common_index_168915"
    current.loc[current.metric.str.startswith("observation_end_") | current.metric.str.startswith("no_dod_and_") | current.metric.eq("global_administrative_boundary_verified"), "scope"] = "observation_end_source_universe_180733"
    columns = ["scope", "metric", "value", "denominator", "unit", "source", "definition"]
    pd.concat([old[columns], current[columns]], ignore_index=True).to_csv(AGG / "PHASE2_DEATH_SOURCE_COMPARISON.csv", index=False)
    support = pd.read_csv(AGG / "phase2_0r_conditional_support.csv")
    support["candidate_population"] = "40,346 patients with >=2 valid OMR readings; outcome not used"
    support["exposure_and_policy"] = "patient-level mean SBP in 730-day window; d1(A)=A-10 I(A>=130)"
    support["available_covariates"] = "age at window start, recorded sex, pre-window BMI plus missingness"
    support["unavailable_pre_window_covariates"] = "diabetes, hypertension, CKD have no documented pre-window variation"
    support.to_csv(AGG / "PHASE2_CONDITIONAL_SUPPORT_DIAGNOSTICS.csv", index=False)
    subgroup = pd.read_csv(AGG / "phase2_0r_subgroups.csv")
    subgroup["source_members"] = "longitudinal/admissions_chronology.parquet; diagnoses_all.parquet; patients_demographics.parquet; OMR omr.csv; observation_end.parquet"
    subgroup["event_unit"] = "patient with first acute-MI-coded admission; counts are descriptive, not causal effects"
    subgroup["precision_unit"] = "risk-difference scale under stated hypothetical binomial assumptions; not policy-effect power"
    subgroup.to_csv(AGG / "PHASE2_SUBGROUP_PRECISION_TABLE.csv", index=False)
    selected = pd.read_csv(AGG / "phase2_0r_bp_retained_excluded.csv")
    selected["source_members"] = "same aggregate common-index and OMR processing as PHASE2_BP_THRESHOLD_COMPARISON.csv"
    selected["diagnosis_timing_note"] = "diagnoses by index are descriptive selection variables only, not pre-window confounders"
    selected.to_csv(AGG / "PHASE2_BP_RETAINED_EXCLUDED.csv", index=False)
    print("Built canonical aggregate-only tables under revised/phase2/aggregates/.")


if __name__ == "__main__":
    main()
