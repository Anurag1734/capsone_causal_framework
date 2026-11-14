"""Validate configured troponin thresholds and admission-level linkage.

Reads only audit subsets and source Parquets. It does not assign missing source
hadm_id values, rebuild master data, or estimate causal effects.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "research_audit"
ARTIFACTS = AUDIT / "artifacts"
MEASUREMENTS_PATH = ARTIFACTS / "troponin_measurements.csv"
THRESHOLDS_PATH = ARTIFACTS / "troponin_thresholds.csv"
DIAGNOSIS_PATH = ROOT / "data" / "raw" / "longitudinal" / "d_labitems.parquet"
DEMOGRAPHICS_PATH = ROOT / "data" / "raw" / "longitudinal" / "patients_demographics.parquet"
ADMISSIONS_PATH = ROOT / "data" / "raw" / "longitudinal" / "admissions_chronology.parquet"


def build_interval_linkage(
    measurements_without_hadm: pd.DataFrame,
    admissions: pd.DataFrame,
) -> pd.DataFrame:
    """Count timestamp interval candidates without assigning source hadm_id."""
    needed_admissions = admissions[
        ["subject_id", "hadm_id", "admittime", "edregtime", "dischtime"]
    ].copy()
    needed_admissions["interval_start"] = needed_admissions["edregtime"].fillna(
        needed_admissions["admittime"]
    )
    possible = measurements_without_hadm[
        ["labevent_id", "subject_id", "charttime"]
    ].merge(needed_admissions, on="subject_id", how="left", suffixes=("_lab", "_admission"))
    possible["ed_discharge_match"] = (
        possible["charttime"].ge(possible["interval_start"])
        & possible["charttime"].le(possible["dischtime"])
    ).fillna(False)
    possible["inpatient_match"] = (
        possible["charttime"].ge(possible["admittime"])
        & possible["charttime"].le(possible["dischtime"])
    ).fillna(False)

    event_ids = measurements_without_hadm[["labevent_id"]].drop_duplicates()
    ed_counts = (
        possible[possible["ed_discharge_match"]]
        .groupby("labevent_id")["hadm_id"]
        .nunique()
        .rename("ed_discharge_candidate_count")
    )
    inpatient_counts = (
        possible[possible["inpatient_match"]]
        .groupby("labevent_id")["hadm_id"]
        .nunique()
        .rename("inpatient_candidate_count")
    )
    unique_ed_hadm = (
        possible[possible["ed_discharge_match"]]
        .groupby("labevent_id")["hadm_id"]
        .agg(lambda ids: int(ids.iloc[0]) if ids.nunique() == 1 else pd.NA)
        .rename("unique_interval_candidate_hadm_id")
    )
    result = event_ids.merge(ed_counts, on="labevent_id", how="left").merge(
        inpatient_counts, on="labevent_id", how="left"
    ).merge(unique_ed_hadm, on="labevent_id", how="left")
    result[["ed_discharge_candidate_count", "inpatient_candidate_count"]] = result[
        ["ed_discharge_candidate_count", "inpatient_candidate_count"]
    ].fillna(0).astype("int64")
    result["interval_link_status"] = "no_interval_match"
    result.loc[result["ed_discharge_candidate_count"].eq(1), "interval_link_status"] = "unique_interval_candidate"
    result.loc[result["ed_discharge_candidate_count"].gt(1), "interval_link_status"] = "ambiguous_multiple_intervals"
    return result


def numeric_stat(values: pd.Series, quantile: float) -> float | None:
    valid = values.dropna()
    return float(valid.quantile(quantile)) if len(valid) else None


def run() -> None:
    thresholds = pd.read_csv(THRESHOLDS_PATH)
    measurements = pd.read_csv(
        MEASUREMENTS_PATH,
        usecols=[
            "labevent_id", "subject_id", "hadm_id", "itemid", "charttime", "storetime",
            "value", "valuenum", "valueuom", "ref_range_lower", "ref_range_upper", "flag",
        ],
        parse_dates=["charttime", "storetime"],
        low_memory=False,
    )
    lab_items = pd.read_parquet(DIAGNOSIS_PATH)
    demographics = pd.read_parquet(
        DEMOGRAPHICS_PATH, columns=["subject_id", "gender", "anchor_year"]
    )
    admissions = pd.read_parquet(
        ADMISSIONS_PATH,
        columns=["subject_id", "hadm_id", "admittime", "edregtime", "dischtime"],
    )
    measurements = measurements.merge(demographics, on="subject_id", how="left", validate="many_to_one")
    measurements = measurements.merge(
        thresholds, on="itemid", how="left", validate="many_to_one", suffixes=("", "_threshold")
    )
    labels = lab_items.set_index("itemid")["label"].to_dict()
    fluids = lab_items.set_index("itemid")["fluid"].to_dict()
    categories = lab_items.set_index("itemid")["category"].to_dict()

    diagnostic_rows = []
    linkage_rows = []
    threshold_rows = []
    missing_hadm_linkage = []
    for threshold in thresholds.to_dict("records"):
        item = int(threshold["itemid"])
        group = measurements[measurements["itemid"] == item].copy()
        numeric = group["valuenum"]
        unit_match = group["valueuom"].astype("string").str.strip().str.lower().eq(
            str(threshold["unit"]).strip().lower()
        )
        year_in_scope = group["anchor_year"].between(
            threshold["anchor_year_start"], threshold["anchor_year_end"]
        )
        sex_in_scope = (
            str(threshold["sex"]).upper() == "ALL"
        ) | group["gender"].astype("string").str.upper().eq(str(threshold["sex"]).upper())
        candidate = (
            numeric.notna()
            & unit_match
            & year_in_scope
            & sex_in_scope
            & numeric.gt(threshold["url_value"])
        )
        reference_values = group["ref_range_upper"].dropna().unique().tolist()
        numeric_values = numeric.dropna()
        diagnostic_rows.append(
            {
                **threshold,
                "dictionary_label": labels.get(item, "not found"),
                "dictionary_fluid": fluids.get(item, "not found"),
                "dictionary_category": categories.get(item, "not found"),
                "measurement_rows": len(group),
                "unique_labevent_ids": int(group["labevent_id"].nunique()),
                "numeric_valuenum_rows": int(numeric.notna().sum()),
                "null_valuenum_rows": int(numeric.isna().sum()),
                "raw_value_null_rows": int(group["value"].isna().sum()),
                "unit_counts": "; ".join(
                    f"{unit}={count}" for unit, count in group["valueuom"].value_counts(dropna=False).items()
                ),
                "ref_range_lower_values": "; ".join(map(str, sorted(group["ref_range_lower"].dropna().unique()))),
                "ref_range_upper_values": "; ".join(map(str, sorted(reference_values))),
                "charttime_min": group["charttime"].min(),
                "charttime_max": group["charttime"].max(),
                "anchor_year_min": group["anchor_year"].min(),
                "anchor_year_max": group["anchor_year"].max(),
                "sex_counts": "; ".join(
                    f"{sex}={count}" for sex, count in group["gender"].value_counts(dropna=False).items()
                ),
                "hadm_id_present_rows": int(group["hadm_id"].notna().sum()),
                "hadm_id_missing_rows": int(group["hadm_id"].isna().sum()),
                "unique_patients": int(group["subject_id"].nunique()),
                "unique_direct_hadm_ids": int(group["hadm_id"].nunique()),
                "value_min": float(numeric_values.min()) if len(numeric_values) else None,
                "value_p01": numeric_stat(numeric, 0.01),
                "value_p05": numeric_stat(numeric, 0.05),
                "value_p25": numeric_stat(numeric, 0.25),
                "value_median": numeric_stat(numeric, 0.50),
                "value_p75": numeric_stat(numeric, 0.75),
                "value_p90": numeric_stat(numeric, 0.90),
                "value_p95": numeric_stat(numeric, 0.95),
                "value_p99": numeric_stat(numeric, 0.99),
                "value_max": float(numeric_values.max()) if len(numeric_values) else None,
                "rows_above_supplied_cutoff": int(candidate.sum()),
                "rows_above_recorded_ref_range_upper": int(
                    (numeric.notna() & numeric.gt(group["ref_range_upper"])).sum()
                ),
            }
        )

        direct = group[group["hadm_id"].notna()].merge(
            admissions[["subject_id", "hadm_id"]],
            on="hadm_id",
            how="left",
            suffixes=("_lab", "_admission"),
            indicator=True,
        )
        direct_valid = direct["_merge"].eq("both") & direct["subject_id_lab"].eq(direct["subject_id_admission"])
        missing = group[group["hadm_id"].isna()]
        interval = build_interval_linkage(missing, admissions) if len(missing) else pd.DataFrame(
            columns=["labevent_id", "ed_discharge_candidate_count", "inpatient_candidate_count", "unique_interval_candidate_hadm_id", "interval_link_status"]
        )
        if len(interval):
            detail = missing[["labevent_id", "subject_id", "itemid", "charttime", "valuenum", "valueuom"]].merge(
                interval, on="labevent_id", validate="one_to_one"
            )
            missing_hadm_linkage.append(detail)
        ed_counts = interval["ed_discharge_candidate_count"].value_counts().to_dict() if len(interval) else {}
        inpatient_counts = interval["inpatient_candidate_count"].value_counts().to_dict() if len(interval) else {}
        linkage_rows.append(
            {
                "itemid": item,
                "dictionary_label": labels.get(item, "not found"),
                "measurement_rows": len(group),
                "direct_hadm_rows": int(group["hadm_id"].notna().sum()),
                "direct_hadm_rows_matching_chronology_and_subject": int(direct_valid.sum()),
                "direct_hadm_rows_unmatched_or_subject_mismatch": int((~direct_valid).sum()),
                "missing_hadm_rows": len(missing),
                "unique_ed_to_discharge_interval_candidates": int(ed_counts.get(1, 0)),
                "multiple_ed_to_discharge_interval_candidates": int(sum(count for candidates, count in ed_counts.items() if candidates > 1)),
                "no_ed_to_discharge_interval_candidate": int(ed_counts.get(0, 0)),
                "unique_inpatient_interval_candidates": int(inpatient_counts.get(1, 0)),
                "multiple_inpatient_interval_candidates": int(sum(count for candidates, count in inpatient_counts.items() if candidates > 1)),
                "no_inpatient_interval_candidate": int(inpatient_counts.get(0, 0)),
                "linkage_policy": "direct hadm_id plus subject match is confirmed; interval-only matches are candidates and do not overwrite source hadm_id",
            }
        )

        issue = {
            51002: "The item exists in d_labitems but has no observations in the complete streamed labevents source. The available artifacts do not establish whether it was not collected, unused in this extract, or absent for another source-specific reason; assay/reference range cannot be assessed.",
            51003: "No platform-specific URL citation. Configured 0.014 ng/mL differs from recorded ref_range_upper=0.01 for all observations; request text reports 0.015, which does not match the retained source subset.",
            52642: "No platform-specific URL citation. Configured 0.04 ng/mL is below recorded ref_range_upper=0.08 for all observations; all rows lack hadm_id and none fall within any patient's ED/admission interval.",
        }[item]
        threshold_rows.append(
            {
                **threshold,
                "dictionary_label": labels.get(item, "not found"),
                "source_reference": "data/raw/troponin_thresholds.jpeg (no bibliographic reference shown); docs/capstone_phase3_ppt_content.md gives a generic ACC/AHA attribution only",
                "recorded_ref_range_upper_values": "; ".join(map(str, sorted(reference_values))),
                "validated_url_value": "",
                "accepted_for_primary_event_time": False,
                "validation_status": "UNRESOLVED",
                "reason": issue,
            }
        )

    diagnostics = pd.DataFrame(diagnostic_rows)
    linkage = pd.DataFrame(linkage_rows)
    validated = pd.DataFrame(threshold_rows)
    diagnostics.to_csv(AUDIT / "TROPONIN_ITEM_DIAGNOSTICS.csv", index=False, na_rep="")
    linkage.to_csv(AUDIT / "TROPONIN_ADMISSION_LINKAGE.csv", index=False, na_rep="")
    validated.to_csv(AUDIT / "VALIDATED_TROPONIN_THRESHOLDS.csv", index=False, na_rep="")
    if missing_hadm_linkage:
        pd.concat(missing_hadm_linkage, ignore_index=True).to_csv(
            ARTIFACTS / "troponin_missing_hadm_interval_linkage.csv", index=False, na_rep=""
        )

    diagnosis_audit = pd.read_csv(AUDIT / "ACUTE_MI_OUTCOME_AUDIT.csv").set_index("metric")["value"]
    temporal = pd.read_csv(AUDIT / "ECG_TEMPORAL_AUDIT.csv")
    candidate_timing = pd.read_csv(AUDIT / "ECG_TEMPORAL_AUDIT.csv")
    item_link = linkage.set_index("itemid")
    text = f"""# Troponin Assay Validation

## Decision

No configured threshold is validated for primary event-time reconstruction. The table is preserved as supplied, but all three rows are explicitly unresolved in `VALIDATED_TROPONIN_THRESHOLDS.csv`; no value is promoted to a validated URL.

## Sources and interpretation

- The complete visible seven-column configuration was transcribed from `data/raw/troponin_thresholds.jpeg` to `research_audit/artifacts/troponin_thresholds.csv`. It specifies item, assay label, anchor-year range, sex, `url_value`, and unit. It contains no manufacturer/platform, method, citation, or provenance field.
- `data/raw/longitudinal/d_labitems.parquet` provides item labels (`Troponin I` or `Troponin T`), fluid (`Blood`), and category (`Chemistry`); it does not identify assay platform or generation.
- `labevents.csv` supplies per-row `ref_range_lower` and `ref_range_upper`. These are recorded laboratory reference bounds in the source rows, not automatically interchangeable with the assay-specific 99th-percentile URL used for research classification.
- The project presentation (`docs/capstone_phase3_ppt_content.md`) attributes 0.014 ng/mL for troponin T and 0.040 ng/mL for troponin I to ACC/AHA but gives no assay-specific source. Its attribution is insufficient to validate the values for these item IDs.
- The Fourth Universal Definition of MI states the general cardiac-troponin principle: myocardial injury is defined relative to the assay's 99th-percentile upper reference limit, and MI additionally requires clinical evidence of ischemia. Reference: Thygesen K, et al. *Fourth Universal Definition of Myocardial Infarction (2018).* Circulation. 2018;138:e618-e651. doi:10.1161/CIR.0000000000000617. This is general diagnostic guidance, not evidence for the three configured numeric values or MIMIC assay platforms.

## Item findings

| Item | Dictionary label | Configured assay/cutoff | Rows / numeric | Unit | Recorded `ref_range_upper` | Decision |
|---|---|---|---:|---|---|---|
| 51002 | {labels.get(51002, 'Troponin I')} | cTnI / 0.04 ng/mL | 0 / 0 | no observations | none | Unresolved; cannot assess applicability. |
| 51003 | {labels.get(51003, 'Troponin T')} | cTnT / 0.014 ng/mL | 359,000 / 149,109 | ng/mL | 0.01 for all 359,000 rows | Unresolved; configured cutoff is above the recorded upper reference for every row. The user-provided 0.015 value is not present in the retained source subset. |
| 52642 | {labels.get(52642, 'Troponin I')} | cTnI / 0.04 ng/mL | 163 / 163 | ng/mL | 0.08 for all 163 rows | Unresolved; configured cutoff is below the recorded upper reference, platform is unknown, and no row has an admission ID. |

All observed configured-item measurements use `ng/mL`. The table's applicability is 2100-2250 and sex `ALL`; observed data years are within that range and both sexes occur for items 51003 and 52642. This does not establish that one sex-agnostic cutoff or one unchanged assay URL is appropriate over the full interval.

Item 51002 is present in `d_labitems.parquet` but has no rows in the complete streamed `labevents.csv` member. The available source files do not establish whether it was not collected, unused in this extract, or absent for another source-specific reason; no result values or reference bounds can be inferred.

The exact distributions, numeric missingness, timestamps, unit/reference counts, and row-level linkage counts are in `TROPONIN_ITEM_DIAGNOSTICS.csv`. No threshold is inferred, optimized, or changed.
"""
    (AUDIT / "TROPONIN_ASSAY_VALIDATION.md").write_text(text, encoding="utf-8")

    acute_admissions = int(diagnosis_audit["acute_mi_admissions_union"])
    master_ecgs = int(temporal["ecg_records"].sum())
    acute_ecgs = int(temporal.loc[temporal["Label_Troponin"].eq("MI_Acute_Presentation"), "ecg_records"].sum())
    text = f"""# Event-Time Coverage and Gate B

## Recommendation

**Gate B remains FAIL / HOLD.** No item has an authoritative item/platform-specific threshold validated against the provided configuration, assay metadata, unit, year, and sex applicability. Therefore, the number of admissions with a **valid** qualifying measurement is 0, and the number with a **reliable first qualifying measurement timestamp under a validated threshold** is 0. Do not treat the provisional candidates or legacy master timestamps as accepted event times.

## Linkage coverage

Direct source `hadm_id` plus `subject_id` matches are confirmed against `admissions_chronology.parquet`. For item 51003, {int(item_link.loc[51003, 'direct_hadm_rows_matching_chronology_and_subject']):,} rows have a direct matching admission. Of the 164,885 rows without `hadm_id`, {int(item_link.loc[51003, 'unique_ed_to_discharge_interval_candidates']):,} match exactly one patient's ED-registration/admission-to-discharge interval, {int(item_link.loc[51003, 'multiple_ed_to_discharge_interval_candidates']):,} match multiple intervals, and {int(item_link.loc[51003, 'no_ed_to_discharge_interval_candidate']):,} match none. These interval results are candidates only; source `hadm_id` values were not filled.

For item 52642, all 163 rows lack `hadm_id`; all 163 have zero matching ED/admission intervals. Patient ID alone cannot establish their admissions. The row-level interval results are retained in `artifacts/troponin_missing_hadm_interval_linkage.csv`.

## Admission and ECG counts

- Acute ICD-coded admissions under ICD-9 410* / ICD-10 I21*/I22*: **{acute_admissions:,}**.
- Acute ICD-coded admissions with a usable validated event-time proxy: **0**.
- Acute ICD-coded admissions without a usable validated event-time proxy: **{acute_admissions:,}**.
- Master ECG rows: **{master_ecgs:,}**; acute-presentation label rows: **{acute_ecgs:,}**.
- ECGs classifiable before/after a validated proxy: **0 / 0**. Official uncertain: **{master_ecgs:,}** overall, including **{acute_ecgs:,}** acute-presentation rows.

The prior audit's threshold-only candidates are not validated events. It reports 38,077 direct-hadm candidate admissions and 10,099 among acute ICD admissions. Among acute-labeled ECGs, candidate-relative counts were 4,929 before, 1,857 after, and 818 uncertain; all remain officially uncertain because the thresholds are unresolved. The legacy master has 3,053 acute-labeled ECG rows with no `index_mi_time`. The 3,269 non-null acute-admission legacy timestamps match a troponin row at that time, but the match does not establish that the row is the first qualifying measurement under a valid URL.

## Meaning and limits

Even after threshold adjudication, the first above-URL `charttime` is a **troponin-derived event-time proxy**, not biological MI onset. A single above-URL measurement can indicate myocardial injury but does not alone establish acute MI; serial change and clinical/ischemic evidence remain relevant. No timestamp has been invented and no uncertain ECG has been classified as pre- or post-MI.

The threshold image does not cite assay-specific primary references. Item 51003's observed `ref_range_upper` is 0.01 ng/mL in all rows, not the 0.015 stated in the task summary; item 52642's configured 0.04 is below its recorded 0.08. Resolve these against the actual assay/platform documentation before reopening Gate B.
"""
    (AUDIT / "EVENT_TIME_COVERAGE_REPORT.md").write_text(text, encoding="utf-8")

    readiness_path = AUDIT / "DATASET_READINESS_REPORT.md"
    readiness = readiness_path.read_text(encoding="utf-8")
    marker = "## Phase 2B - Threshold and Event-Time Feasibility"
    update = f"""{marker}

**Gate B recommendation: FAIL / HOLD.** No configured item has a validated assay-specific URL; no admission has a reliable first qualifying timestamp under a validated threshold. All {master_ecgs:,} ECG rows remain uncertain relative to a validated proxy. See `TROPONIN_ASSAY_VALIDATION.md` and `EVENT_TIME_COVERAGE_REPORT.md`.

The retained lab source reports item 51003 `ref_range_upper=0.01 ng/mL` for all rows, whereas the task summary states 0.015. Item 52642 remains `0.08 ng/mL` with 163/163 records lacking `hadm_id`; none overlap any patient-specific ED/admission interval. Item 51003 has unique interval candidates among some missing-ID rows, but those were not assigned to source records.
"""
    if marker in readiness:
        readiness = readiness.split(marker, 1)[0].rstrip()
    readiness_path.write_text(readiness.rstrip() + "\n\n" + update, encoding="utf-8")


if __name__ == "__main__":
    run()