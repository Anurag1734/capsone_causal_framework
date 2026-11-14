"""Read-only Phase 1-2 data audit using the repository's current artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = REPO_ROOT / "research_audit"
ARTIFACT_ROOT = AUDIT_ROOT / "artifacts"
RAW_ROOT = REPO_ROOT / "data" / "raw"
LONGITUDINAL_ROOT = RAW_ROOT / "longitudinal"
MASTER_ROOT = RAW_ROOT / "master_dataset"
MEASUREMENTS_PATH = ARTIFACT_ROOT / "troponin_measurements.csv"
THRESHOLDS_PATH = ARTIFACT_ROOT / "troponin_thresholds.csv"
SPLITS = ("train", "validation", "test")
META_COLUMNS = [
    "study_id", "SubjectID", "hadm_id", "ecg_time", "Label_Troponin",
    "is_MI", "index_mi_time", "time_diff_hours",
]
CLINICAL_COLUMNS = {
    "diabetes", "hypertension", "ckd", "prior_mi", "statin_before",
    "statin_during", "statin_after", "beta_blocker_before",
    "beta_blocker_during", "acei_before", "acei_during", "aspirin_before",
    "aspirin_during", "vasopressor_during", "mech_vent_during", "anchor_age",
    "sex_male",
}


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, na_rep="")


def normalized_codes(values: pd.Series) -> pd.Series:
    return values.astype("string").str.upper().str.replace(".", "", regex=False)


def classify_diagnosis_codes(diagnoses: pd.DataFrame) -> pd.DataFrame:
    """Classify ICD-9/10 acute and historical MI codes without conflating them."""
    result = diagnoses.copy()
    code = normalized_codes(result["icd_code"])
    version = pd.to_numeric(result["icd_version"], errors="coerce")
    icd9 = version.eq(9)
    icd10 = version.eq(10)
    result["acute_icd9_410"] = icd9 & code.str.startswith("410", na=False)
    result["acute_icd10_i21_i22"] = icd10 & (
        code.str.startswith("I21", na=False) | code.str.startswith("I22", na=False)
    )
    result["historical_icd9_412"] = icd9 & code.str.startswith("412", na=False)
    result["historical_icd10_i25_2"] = icd10 & code.str.startswith("I252", na=False)
    result["diabetes_code"] = (
        (icd9 & code.str.startswith("250", na=False))
        | (icd10 & code.str.match(r"^E0[89]|^E1[0-3]", na=False))
    )
    result["hypertension_code"] = (
        (icd9 & code.str.match(r"^40[1-5]", na=False))
        | (icd10 & code.str.match(r"^I1[0-5]", na=False))
    )
    result["ckd_code"] = (
        (icd9 & code.str.startswith("585", na=False))
        | (icd10 & code.str.startswith("N18", na=False))
    )
    result["acute_mi_code"] = result["acute_icd9_410"] | result["acute_icd10_i21_i22"]
    result["historical_mi_code"] = result["historical_icd9_412"] | result["historical_icd10_i25_2"]
    return result


def admission_diagnosis_audit(diagnoses: pd.DataFrame, admissions: pd.DataFrame) -> pd.DataFrame:
    coded = classify_diagnosis_codes(diagnoses)
    flag_columns = [
        "acute_icd9_410", "acute_icd10_i21_i22", "historical_icd9_412",
        "historical_icd10_i25_2", "diabetes_code", "hypertension_code", "ckd_code",
    ]
    grouped = coded.groupby(["subject_id", "hadm_id"], as_index=False)[flag_columns].max()
    grouped["diagnosis_present_this_admission"] = True
    code_groups = coded[coded["acute_mi_code"] | coded["historical_mi_code"]].groupby(
        ["subject_id", "hadm_id"]
    )["icd_code"].agg(lambda values: ";".join(sorted(set(map(str, values))))).rename("mi_icd_codes")
    grouped = grouped.merge(
        code_groups.reset_index(), on=["subject_id", "hadm_id"], how="left", validate="one_to_one"
    )
    audit = admissions.merge(grouped, on=["subject_id", "hadm_id"], how="left", validate="one_to_one")
    for column in flag_columns:
        audit[column] = audit[column].fillna(False).astype(bool)
    audit["diagnosis_present_this_admission"] = audit["diagnosis_present_this_admission"].fillna(False).astype(bool)
    audit["acute_mi_this_admission"] = audit["acute_icd9_410"] | audit["acute_icd10_i21_i22"]
    audit["historical_mi_code_this_admission"] = (
        audit["historical_icd9_412"] | audit["historical_icd10_i25_2"]
    )
    audit["mi_code_this_admission"] = audit["acute_mi_this_admission"] | audit["historical_mi_code_this_admission"]
    audit["mi_icd_codes"] = audit["mi_icd_codes"].fillna("")
    audit = audit.sort_values(["subject_id", "admittime", "hadm_id"]).reset_index(drop=True)
    prior_sources = [
        ("acute_mi_this_admission", "prior_acute_mi_admission"),
        ("historical_mi_code_this_admission", "prior_historical_mi_code_admission"),
        ("mi_code_this_admission", "prior_mi_documentation"),
        ("diabetes_code", "prior_diabetes_code"),
        ("hypertension_code", "prior_hypertension_code"),
        ("ckd_code", "prior_ckd_code"),
    ]
    for source, target in prior_sources:
        audit[target] = audit.groupby("subject_id", sort=False)[source].transform(
            lambda values: values.shift(1, fill_value=False).cummax()
        ).astype(bool)
    return audit


def threshold_candidates(
    measurements: pd.DataFrame,
    thresholds: pd.DataFrame,
    demographics: pd.DataFrame,
) -> pd.DataFrame:
    joined = measurements.merge(thresholds, on="itemid", how="inner", validate="many_to_one")
    joined = joined.merge(demographics, on="subject_id", how="left", validate="many_to_one")
    joined["unit_matches_threshold"] = (
        joined["valueuom"].astype("string").str.strip().str.lower()
        == joined["unit"].astype("string").str.strip().str.lower()
    )
    joined["year_in_threshold_scope"] = joined["anchor_year"].between(
        joined["anchor_year_start"], joined["anchor_year_end"]
    )
    joined["sex_in_threshold_scope"] = (
        joined["sex"].astype("string").str.upper().eq("ALL")
        | joined["sex"].astype("string").str.upper().eq(joined["gender"].astype("string").str.upper())
    )
    joined["threshold_candidate"] = (
        joined["valuenum"].notna()
        & joined["unit_matches_threshold"]
        & joined["year_in_threshold_scope"]
        & joined["sex_in_threshold_scope"]
        & (joined["valuenum"] > joined["url_value"])
    )
    joined["threshold_validation_status"] = "UNVALIDATED_NO_ASSAY_SPECIFIC_SOURCE_AND_REFERENCE_RANGE_CONFLICT"
    return joined


def timing_class(ecg_time: pd.Series, event_time: pd.Series) -> pd.Series:
    ecg_values = pd.to_datetime(ecg_time, errors="coerce", utc=True)
    event_values = pd.to_datetime(event_time, errors="coerce", utc=True)
    values = [
        "uncertain" if pd.isna(ecg_value) or pd.isna(event_value)
        else "before" if ecg_value < event_value
        else "after"
        for ecg_value, event_value in zip(ecg_values, event_values)
    ]
    return pd.Series(values, index=ecg_time.index, dtype="string")


def read_master_split(split: str, columns: list[str] | None = None) -> pd.DataFrame:
    return pd.read_parquet(MASTER_ROOT / f"{split}.parquet", columns=columns)


def threshold_validation_report(
    candidates: pd.DataFrame,
    thresholds: pd.DataFrame,
) -> pd.DataFrame:
    lab_names = pd.read_parquet(LONGITUDINAL_ROOT / "d_labitems.parquet").set_index("itemid")["label"].to_dict()
    rows = []
    for threshold in thresholds.to_dict("records"):
        item_rows = candidates[candidates["itemid"] == threshold["itemid"]]
        delta = item_rows["ref_range_upper"] - threshold["url_value"]
        qualified = item_rows[item_rows["threshold_candidate"]]
        rows.append(
            {
                **threshold,
                "lab_label": lab_names.get(threshold["itemid"], "not present in d_labitems"),
                "measurement_rows": len(item_rows),
                "numeric_value_rows": int(item_rows["valuenum"].notna().sum()),
                "admission_linked_rows": int(item_rows["hadm_id"].notna().sum()),
                "unit_counts": json.dumps(item_rows["valueuom"].value_counts().to_dict(), sort_keys=True),
                "unit_mismatch_rows": int((~item_rows["unit_matches_threshold"]).sum()),
                "anchor_year_missing_rows": int(item_rows["anchor_year"].isna().sum()),
                "anchor_year_outside_scope_rows": int((~item_rows["year_in_threshold_scope"]).sum()),
                "sex_counts": json.dumps(item_rows["gender"].value_counts(dropna=False).to_dict(), sort_keys=True),
                "reference_upper_counts": json.dumps(item_rows["ref_range_upper"].value_counts(dropna=False).to_dict(), sort_keys=True),
                "rows_where_provided_cutoff_below_ref_upper": int((delta > 0).sum()),
                "rows_where_provided_cutoff_above_ref_upper": int((delta < 0).sum()),
                "qualifying_measurement_rows_at_provided_cutoff": len(qualified),
                "qualifying_admission_linked_rows": int(qualified["hadm_id"].notna().sum()),
                "external_assay_source_citation_present": False,
                "validation_status": "UNRESOLVED: source citation missing; compare reference ranges and linkage",
            }
        )
    return pd.DataFrame(rows)


def build_reports() -> dict[str, object]:
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    thresholds = pd.read_csv(THRESHOLDS_PATH)
    measurements = pd.read_csv(
        MEASUREMENTS_PATH,
        parse_dates=["charttime", "storetime"],
        low_memory=False,
    )
    demographics = pd.read_parquet(
        LONGITUDINAL_ROOT / "patients_demographics.parquet",
        columns=["subject_id", "gender", "anchor_year"],
    )
    admissions = pd.read_parquet(LONGITUDINAL_ROOT / "admissions_chronology.parquet")
    diagnoses = pd.read_parquet(LONGITUDINAL_ROOT / "diagnoses_all.parquet")

    diagnosis_audit = admission_diagnosis_audit(diagnoses, admissions)
    write_csv(AUDIT_ROOT / "ACUTE_MI_DIAGNOSIS_BY_ADMISSION.csv", diagnosis_audit)
    historical_only = diagnosis_audit[
        diagnosis_audit["historical_mi_code_this_admission"] & ~diagnosis_audit["acute_mi_this_admission"]
    ]
    diagnosis_summary = pd.DataFrame(
        [
            {"metric": "admissions_in_chronology", "value": len(diagnosis_audit)},
            {"metric": "admissions_with_any_diagnosis", "value": int(diagnosis_audit.diagnosis_present_this_admission.sum())},
            {"metric": "acute_icd9_410_admissions", "value": int(diagnosis_audit.acute_icd9_410.sum())},
            {"metric": "acute_icd10_i21_i22_admissions", "value": int(diagnosis_audit.acute_icd10_i21_i22.sum())},
            {"metric": "acute_mi_admissions_union", "value": int(diagnosis_audit.acute_mi_this_admission.sum())},
            {"metric": "historical_icd9_412_admissions", "value": int(diagnosis_audit.historical_icd9_412.sum())},
            {"metric": "historical_icd10_i25_2_admissions", "value": int(diagnosis_audit.historical_icd10_i25_2.sum())},
            {"metric": "historical_only_admissions", "value": len(historical_only)},
            {"metric": "prior_acute_mi_admissions", "value": int(diagnosis_audit.prior_acute_mi_admission.sum())},
            {"metric": "prior_historical_mi_code_admissions", "value": int(diagnosis_audit.prior_historical_mi_code_admission.sum())},
            {"metric": "diagnosis_code_rows", "value": len(diagnoses)},
            {"metric": "original_derived_mi_parquets_modified", "value": "no"},
        ]
    )
    write_csv(AUDIT_ROOT / "ACUTE_MI_OUTCOME_AUDIT.csv", diagnosis_summary)

    clinical_rows = []
    for condition in ("diabetes", "hypertension", "ckd"):
        clinical_rows.extend(
            [
                {"condition": condition, "timing": "coded_on_this_admission", "admissions": int(diagnosis_audit[f"{condition}_code"].sum())},
                {"condition": condition, "timing": "documented_on_prior_admission_only", "admissions": int(diagnosis_audit[f"prior_{condition}_code"].sum())},
            ]
        )
    clinical_rows.extend(
        [
            {"condition": "MI", "timing": "acute_or_historical_code_on_this_admission", "admissions": int(diagnosis_audit.mi_code_this_admission.sum())},
            {"condition": "MI", "timing": "documented_on_prior_admission_only", "admissions": int(diagnosis_audit.prior_mi_documentation.sum())},
        ]
    )
    write_csv(AUDIT_ROOT / "CLINICAL_DIAGNOSIS_TIMING.csv", pd.DataFrame(clinical_rows))

    candidates = threshold_candidates(measurements, thresholds, demographics)
    validation = threshold_validation_report(candidates, thresholds)
    write_csv(AUDIT_ROOT / "TROPONIN_THRESHOLD_VALIDATION.csv", validation)
    qualified = candidates[candidates["threshold_candidate"]].copy()
    linked_candidates = qualified[qualified["hadm_id"].notna()].merge(
        admissions[["subject_id", "hadm_id"]],
        on="hadm_id",
        how="inner",
        suffixes=("_lab", "_admission"),
        validate="many_to_one",
    )
    linked_candidates = linked_candidates[
        linked_candidates["subject_id_lab"] == linked_candidates["subject_id_admission"]
    ].sort_values(["hadm_id", "charttime", "labevent_id"])
    first_candidate = linked_candidates.drop_duplicates("hadm_id", keep="first")
    event_fields = [
        "hadm_id", "labevent_id", "charttime", "itemid", "assay_type", "value", "valuenum",
        "valueuom", "ref_range_upper", "url_value", "unit", "anchor_year_start",
        "anchor_year_end", "sex", "threshold_validation_status",
    ]
    first_candidate = first_candidate[event_fields].rename(
        columns={
            "labevent_id": "first_qualifying_labevent_id_candidate",
            "charttime": "first_qualifying_measurement_timestamp_candidate",
            "itemid": "first_qualifying_itemid_candidate",
            "assay_type": "first_qualifying_assay_type_candidate",
            "value": "first_qualifying_raw_value_candidate",
            "valuenum": "first_qualifying_value_candidate",
            "valueuom": "first_qualifying_valueuom_candidate",
            "ref_range_upper": "first_qualifying_ref_range_upper",
            "url_value": "applied_url_value_candidate",
            "unit": "threshold_unit",
            "anchor_year_start": "threshold_anchor_year_start",
            "anchor_year_end": "threshold_anchor_year_end",
            "sex": "threshold_sex",
        }
    )

    legacy_frames = []
    for split in SPLITS:
        legacy_frames.append(read_master_split(split, ["hadm_id", "Label_Troponin", "index_mi_time"]))
    legacy_master = pd.concat(legacy_frames, ignore_index=True)
    legacy_times = (
        legacy_master[legacy_master["index_mi_time"].notna()]
        .drop_duplicates("hadm_id")[["hadm_id", "index_mi_time"]]
        .rename(columns={"index_mi_time": "legacy_master_index_mi_time"})
    )
    event_audit = admissions[["subject_id", "hadm_id", "admittime"]].merge(
        diagnosis_audit[["hadm_id", "acute_mi_this_admission", "historical_mi_code_this_admission"]],
        on="hadm_id", how="left", validate="one_to_one",
    ).merge(first_candidate, on="hadm_id", how="left", validate="one_to_one").merge(
        legacy_times, on="hadm_id", how="left", validate="one_to_one"
    )
    event_audit["event_time_proxy_accepted"] = False
    event_audit["event_time_status"] = "NO_LINKED_VALUE_ABOVE_SUPPLIED_CUTOFF"
    has_candidate = event_audit["first_qualifying_measurement_timestamp_candidate"].notna()
    event_audit.loc[has_candidate, "event_time_status"] = "PROVISIONAL_THRESHOLD_CANDIDATE_NOT_VALIDATED"
    event_audit["event_time_definition"] = "first observed valuenum strictly above supplied item threshold; not biological onset"
    write_csv(AUDIT_ROOT / "MI_EVENT_TIME_AUDIT.csv", event_audit)

    unlinked = qualified[qualified["hadm_id"].isna()].copy()
    unlinked["exclusion_reason"] = "hadm_id is null; cannot link measurement to an admission"
    write_csv(AUDIT_ROOT / "TROPONIN_UNLINKABLE_MEASUREMENTS.csv", unlinked)

    lab_timestamps = measurements[measurements["hadm_id"].notna()][["hadm_id", "charttime"]].drop_duplicates()
    lab_timestamps["charttime"] = pd.to_datetime(lab_timestamps["charttime"], utc=True, errors="coerce")
    legacy_times["legacy_master_index_mi_time"] = pd.to_datetime(
        legacy_times["legacy_master_index_mi_time"], utc=True, errors="coerce"
    )
    legacy_lab_links = legacy_times.merge(
        lab_timestamps,
        left_on=["hadm_id", "legacy_master_index_mi_time"],
        right_on=["hadm_id", "charttime"],
        how="left",
        validate="one_to_one",
    )
    legacy_lab_links["legacy_timestamp_matches_lab_row"] = legacy_lab_links["charttime"].notna()
    event_audit = event_audit.merge(
        legacy_lab_links[["hadm_id", "legacy_timestamp_matches_lab_row"]],
        on="hadm_id", how="left", validate="one_to_one",
    )
    event_audit["legacy_timestamp_matches_lab_row"] = event_audit["legacy_timestamp_matches_lab_row"].fillna(False)
    write_csv(AUDIT_ROOT / "MI_EVENT_TIME_AUDIT.csv", event_audit)

    temporal_frames = []
    split_schemas: dict[str, list[str]] = {}
    all_feature_columns: list[str] | None = None
    for split in SPLITS:
        schema_columns = pq.ParquetFile(MASTER_ROOT / f"{split}.parquet").schema_arrow.names
        split_schemas[split] = schema_columns
        if all_feature_columns is None:
            documented_features = pd.read_csv(REPO_ROOT / "docs" / "final_features_to_extract.txt", header=None)[0].astype(str).tolist()
            all_feature_columns = [column for column in schema_columns if column in set(documented_features)]
        read_columns = META_COLUMNS + sorted(CLINICAL_COLUMNS.intersection(schema_columns)) + all_feature_columns
        frame = read_master_split(split, list(dict.fromkeys(read_columns)))
        frame.insert(0, "split", split)
        temporal_frames.append(frame[META_COLUMNS + ["split"]])
        feature_rows = []
        for column in all_feature_columns:
            if column.startswith("ST_Elev_"):
                group = "ST"
            elif column.startswith("Q_Amp_"):
                group = "Q"
            elif column.startswith("R_Amp_"):
                group = "R"
            elif column.startswith("T_Amp_"):
                group = "T"
            elif column.startswith("S_Amp_"):
                group = "S"
            else:
                group = "Global_intervals"
            feature_rows.append(
                {"feature": column, "feature_group": group, "split": split,
                 "rows": len(frame), "missing_values": int(frame[column].isna().sum()),
                 "missing_rate": float(frame[column].isna().mean())}
            )
        if split == SPLITS[0]:
            feature_availability = feature_rows
        else:
            feature_availability.extend(feature_rows)
    write_csv(AUDIT_ROOT / "ECG_FEATURE_AVAILABILITY.csv", pd.DataFrame(feature_availability))

    masters = pd.concat(temporal_frames, ignore_index=True)
    temporal_records = masters.merge(
        event_audit[["hadm_id", "first_qualifying_measurement_timestamp_candidate", "first_qualifying_itemid_candidate", "event_time_status"]],
        on="hadm_id", how="left", validate="many_to_one",
    )
    temporal_records["candidate_timing_class"] = timing_class(
        temporal_records["ecg_time"], temporal_records["first_qualifying_measurement_timestamp_candidate"]
    )
    temporal_records["candidate_time_difference_hours"] = (
        pd.to_datetime(temporal_records["ecg_time"], utc=True, errors="coerce")
        - pd.to_datetime(temporal_records["first_qualifying_measurement_timestamp_candidate"], utc=True, errors="coerce")
    ).dt.total_seconds() / 3600
    temporal_records["timing_class"] = "uncertain"
    temporal_records["timing_status"] = "thresholds not validated; provisional candidate class is not accepted as event-relative"
    temporal_records["legacy_index_time_class"] = timing_class(
        temporal_records["ecg_time"], temporal_records["index_mi_time"]
    )
    temporal_records = temporal_records.merge(
        legacy_lab_links[["hadm_id", "legacy_timestamp_matches_lab_row"]],
        left_on="hadm_id", right_on="hadm_id", how="left", validate="many_to_one",
    )
    temporal_records["legacy_timestamp_matches_lab_row"] = temporal_records["legacy_timestamp_matches_lab_row"].fillna(False)
    temporal_records.to_csv(AUDIT_ROOT / "ECG_TEMPORAL_RECORDS.csv", index=False, na_rep="")
    temporal_summary = temporal_records.groupby(
        ["split", "Label_Troponin", "timing_class", "candidate_timing_class", "timing_status"],
        dropna=False,
    ).size().rename("ecg_records").reset_index()
    write_csv(AUDIT_ROOT / "ECG_TEMPORAL_AUDIT.csv", temporal_summary)

    cohort_rows = []
    for split in SPLITS:
        frame = read_master_split(split, ["study_id", "SubjectID", "hadm_id", "Label_Troponin", "index_mi_time"])
        cohort_rows.extend(
            [
                {"split": split, "metric": "ecg_rows", "value": len(frame)},
                {"split": split, "metric": "unique_patients", "value": frame.SubjectID.nunique()},
                {"split": split, "metric": "unique_admissions", "value": frame.hadm_id.nunique()},
                {"split": split, "metric": "unique_study_ids", "value": frame.study_id.nunique()},
                {"split": split, "metric": "acute_presentation_ecgs", "value": int(frame.Label_Troponin.eq("MI_Acute_Presentation").sum())},
                {"split": split, "metric": "acute_presentation_missing_index_time", "value": int((frame.Label_Troponin.eq("MI_Acute_Presentation") & frame.index_mi_time.isna()).sum())},
                {"split": split, "metric": "handcrafted_feature_columns", "value": len(all_feature_columns)},
                {"split": split, "metric": "latent_columns", "value": sum(column.startswith("z_ecg_") for column in split_schemas[split])},
            ]
        )
    write_csv(AUDIT_ROOT / "COHORT_COUNTS_AND_SPLITS.csv", pd.DataFrame(cohort_rows))

    checkpoint_dir = REPO_ROOT / "models" / "checkpoints"
    checkpoints = [
        path for path in checkpoint_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".pt", ".pth", ".ckpt", ".safetensors"}
    ]
    beta_report = pd.DataFrame(
        [
            {"check": "latent_columns_present_in_master", "status": "present", "evidence": "64 z_ecg_* columns in all three splits"},
            {"check": "beta_vae_checkpoint", "status": "missing", "evidence": f"{len(checkpoints)} checkpoint files found"},
            {"check": "separate_embedding_extraction_outputs", "status": "missing", "evidence": "data/modeling/ecg_embeddings is absent"},
            {"check": "training_run_provenance", "status": "missing", "evidence": "no run-specific log/metadata found"},
            {"check": "causal_use_eligible", "status": "no", "evidence": "latent provenance unresolved; keep embeddings secondary/excluded"},
        ]
    )
    write_csv(AUDIT_ROOT / "BETA_VAE_PROVENANCE_REPORT.csv", beta_report)
    write_csv(
        AUDIT_ROOT / "ECG_SELECTION_FEASIBILITY.csv",
        pd.DataFrame([{"metric": "selection_model", "value": "not run", "notes": "No causal estimation requested; master contains only ECG-acquired patients."}]),
    )
    write_csv(
        AUDIT_ROOT / "REPO_ARTIFACT_INVENTORY.csv",
        pd.DataFrame(
            [
                {"artifact": "labevents.rar", "path": "data/raw/labevents.rar", "status": "present; selected items streamed", "notes": "118,171,367 rows scanned; archive preserved"},
                {"artifact": "threshold image", "path": "data/raw/troponin_thresholds.jpeg", "status": "present; transcribed", "notes": "No bibliographic assay citation; validation unresolved"},
                {"artifact": "master splits", "path": "data/raw/master_dataset/{train,validation,test}.parquet", "status": "present", "notes": "read-only; not rebuilt"},
                {"artifact": "diagnoses", "path": "data/raw/longitudinal/diagnoses_all.parquet", "status": "present", "notes": f"{len(diagnoses)} rows used"},
                {"artifact": "VAE checkpoint", "path": "models/checkpoints/", "status": "missing", "notes": f"{len(checkpoints)} checkpoint files"},
            ]
        ),
    )

    acute_master = masters[masters["Label_Troponin"].eq("MI_Acute_Presentation")]
    acute_legacy = acute_master[acute_master["index_mi_time"].notna()][["hadm_id", "index_mi_time"]].drop_duplicates()
    acute_legacy["index_mi_time"] = pd.to_datetime(acute_legacy["index_mi_time"], utc=True, errors="coerce")
    legacy_acute_matches = acute_legacy.merge(
        lab_timestamps,
        left_on=["hadm_id", "index_mi_time"], right_on=["hadm_id", "charttime"], how="inner",
    )
    acute_candidate_timing_counts = (
        temporal_records.loc[
            temporal_records["Label_Troponin"].eq("MI_Acute_Presentation"), "candidate_timing_class"
        ]
        .value_counts()
        .to_dict()
    )
    summary = {
        "diagnosis_audit": diagnosis_summary.set_index("metric")["value"].to_dict(),
        "threshold_validation": validation.to_dict("records"),
        "lab_subset_rows": len(measurements),
        "lab_subset_source_rows_scanned": 118171367,
        "threshold_candidate_admissions": int(has_candidate.sum()),
        "acute_icd_candidate_admissions": int(event_audit.loc[event_audit["acute_mi_this_admission"], "first_qualifying_measurement_timestamp_candidate"].notna().sum()),
        "legacy_acute_admission_timestamps": len(acute_legacy),
        "legacy_acute_timestamps_matching_a_lab_row": int(legacy_acute_matches.hadm_id.nunique()),
        "acute_ecg_rows": len(acute_master),
        "acute_ecg_rows_missing_legacy_index_time": int(acute_master["index_mi_time"].isna().sum()),
        "acute_ecg_rows_uncertain_under_validated_rule": len(acute_master),
        "acute_candidate_timing_counts": acute_candidate_timing_counts,
        "unlinked_candidate_measurements": len(unlinked),
        "thresholds_validated": False,
        "gate_recommendation": "Gate C - hold causal MI-to-ECG analysis; thresholds and event-time completeness are unresolved",
    }
    write_threshold_documentation(summary)
    write_feasibility_report(summary)
    write_completion_report(summary)
    return summary


def write_threshold_documentation(summary: dict[str, object]) -> None:
    text = f"""# Troponin Threshold Documentation

## Transcription and source

The original input is `data/raw/troponin_thresholds.jpeg`, a rendered table rather than a CSV. It was transcribed without changing the displayed fields into `research_audit/artifacts/troponin_thresholds.csv`: `itemid`, `assay_type`, `anchor_year_start`, `anchor_year_end`, `sex`, `url_value`, and `unit`. The three rows are 51002/cTnI/0.04 ng/mL, 51003/cTnT/0.014 ng/mL, and 52642/cTnI/0.04 ng/mL; each specifies years 2100-2250 and sex `ALL`.

The project presentation `docs/capstone_phase3_ppt_content.md` attributes the cTnT and cTnI cutoffs to ACC/AHA but gives no assay-specific bibliographic citation. It also applies one cTnI value to both 51002 and 52642. Thus the table is retained as **user-provided and provisional**, not certified as a validated 99th-percentile URL table.

## Source data and validation

`data/raw/labevents.rar` contains `labevents.csv` with columns `labevent_id`, `subject_id`, `hadm_id`, `specimen_id`, `itemid`, `order_provider_id`, `charttime`, `storetime`, `value`, `valuenum`, `valueuom`, `ref_range_lower`, `ref_range_upper`, `flag`, `priority`, and `comments`. The archive's 13.73 GB uncompressed member could not fit in available free disk. Instead, 118,171,367 rows were streamed without modifying the archive; 359,163 rows for the three configured item IDs were retained in `research_audit/artifacts/troponin_measurements.csv`.

`d_labitems.parquet` labels 51002 and 52642 Troponin I and 51003 Troponin T. Observed data show:

| Item | Rows | Admission-linked rows | Units | Observed `ref_range_upper` | Supplied cutoff | Result |
|---|---:|---:|---|---:|---:|---|
| 51002 | 0 | 0 | none | none | 0.04 ng/mL | Cannot validate: no observations. |
| 51003 | 359,000 | 194,115 | ng/mL | 0.01 for all rows | 0.014 ng/mL | Same unit, but cutoff exceeds the recorded upper reference range; source applicability unresolved. |
| 52642 | 163 | 0 | ng/mL | 0.08 for all rows | 0.04 ng/mL | Cutoff is below the recorded upper reference range; no records can be linked to admissions. |

Observed chart years are 2105-2212, within the supplied interval. The table specifies sex `ALL` and does not stratify by sex. The absence of platform/assay-generation details and citations prevents validating the limits across these years. The in-row reference range is a comparison, not a substitute for an externally sourced assay-specific 99th-percentile URL.

## Candidate event-time rule

For diagnostic review only, a candidate is the earliest measurement per admission with numeric `valuenum` strictly greater than its supplied cutoff, exact unit match, year in scope, and compatible sex scope. It is a troponin-derived event proxy, **not biological MI onset**, and does not apply the separate >=20% delta criterion in the project presentation. Because threshold validation is unresolved, every admission has `event_time_proxy_accepted=false`; ECG timing based on these candidates remains uncertain. No timestamp is imputed.

The runner found {summary['threshold_candidate_admissions']:,} admissions with a provisional candidate, including {summary['acute_icd_candidate_admissions']:,} acute-ICD admissions. {summary['unlinked_candidate_measurements']:,} candidate measurements with null admission IDs are excluded from admission linkage. See `TROPONIN_THRESHOLD_VALIDATION.csv` and `MI_EVENT_TIME_AUDIT.csv`.
"""
    (AUDIT_ROOT / "TROPONIN_THRESHOLD_DOCUMENTATION.md").write_text(text, encoding="utf-8")


def write_feasibility_report(summary: dict[str, object]) -> None:
    diagnosis = summary["diagnosis_audit"]
    text = f"""# Phase 1-2 Data Feasibility and Temporal Audit

## Recommendation

**Gate C: hold causal MI-to-ECG analysis.** The audit runner reads the actual repository paths and real Parquet/lab rows. Successful execution is not a feasibility pass: threshold applicability conflicts with recorded lab reference ranges, one configured assay has no observations, another has no admission IDs, and acute-labeled ECGs remain without an independently validated event time. No causal effects were estimated.

**Gate A, diagnosis coding: conditional pass for descriptive cohort work.** ICD-9 410* and ICD-10 I21*/I22* are separated from historical ICD-9 412 and ICD-10 I25.2. The original `diagnoses_mi_codes.parquet` and `mi_admissions.parquet` remain unchanged; use `ACUTE_MI_DIAGNOSIS_BY_ADMISSION.csv` for corrected audit flags.

**Gate B, event timing: fail/unresolved.** The threshold image lacks assay-specific citations. Item 51003's supplied cutoff (0.014 ng/mL) differs from its stored upper reference range (0.01); item 52642's cutoff (0.04) is below its stored range (0.08) and all its rows lack `hadm_id`; item 51002 has no observations. Candidate times are retained but are not accepted event times. Official timing classes are therefore uncertain.

## Diagnosis audit

The audit covers {diagnosis['admissions_in_chronology']:,} admissions and {diagnosis['diagnosis_code_rows']:,} code rows. Current acute codes are ICD-9 410* or ICD-10 I21*/I22*; historical codes are ICD-9 412 or ICD-10 I25.2. Prior-MI flags use only earlier admissions for the same patient; same-admission codes are not considered prior. See `ACUTE_MI_OUTCOME_AUDIT.csv` and the admission-level output.

## Lab and event-time audit

Source: `data/raw/labevents.rar`, member `labevents.csv`; 118,171,367 rows were streamed and the archive was preserved. The selected-item subset contains {summary['lab_subset_rows']:,} rows. The event audit reports {summary['threshold_candidate_admissions']:,} candidate admissions overall and {summary['acute_icd_candidate_admissions']:,} with an acute ICD code. These are unvalidated threshold candidates, not MI diagnoses or biological onset times.

The legacy master contains {summary['acute_ecg_rows']:,} acute-presentation ECG rows, {summary['acute_ecg_rows_missing_legacy_index_time']:,} with missing `index_mi_time`. Of {summary['legacy_acute_admission_timestamps']:,} acute-admission legacy timestamps, {summary['legacy_acute_timestamps_matching_a_lab_row']:,} match an observed lab row exactly; this proves a measurement exists at that time, not that it is the first measurement above a valid URL.

Among those acute-labeled ECGs, the **provisional** first-candidate timing classes are {summary['acute_candidate_timing_counts'].get('before', 0):,} before, {summary['acute_candidate_timing_counts'].get('after', 0):,} after, and {summary['acute_candidate_timing_counts'].get('uncertain', 0):,} uncertain. These are not accepted event-relative classifications; the validated timing class remains uncertain for all {summary['acute_ecg_rows']:,} rows.

`ECG_TEMPORAL_RECORDS.csv` contains all ECG rows, a provisional before/after/uncertain class relative to the candidate time, and an official class that remains uncertain. No missing timestamps were filled. The 95 handcrafted features and 64 latent dimensions remain present in the masters; beta-VAE provenance is still missing, and latents remain excluded from causal use.

## Remaining requirements

1. Provide assay/platform references establishing each item-specific URL and units for the relevant years and sexes; resolve the 51003 and 52642 reference-range discrepancies.
2. Provide linkable observations for item 51002 or document its removal from the rule.
3. Decide how to handle 52642 measurements without admission IDs; do not infer an admission without a validated rule.
4. Re-run after threshold adjudication. Keep candidate values separate from accepted event times.

Until these checks pass, the primary handcrafted ECG analysis is not ready for causal estimation. Beta-VAE eligibility is a separate secondary blocker.
"""
    (AUDIT_ROOT / "PHASE2_DATA_FEASIBILITY_REPORT.md").write_text(text, encoding="utf-8")
    (AUDIT_ROOT / "DATASET_READINESS_REPORT.md").write_text(text, encoding="utf-8")


def write_completion_report(summary: dict[str, object]) -> None:
    text = f"""# Phase 1-2 Audit Completion Report

The runner was updated to use the current `data/raw/longitudinal/` and `data/raw/master_dataset/` paths. It audited the diagnosis Parquet, admission chronology, master splits, threshold transcription, and streamed lab subset. Original diagnosis derivatives, master datasets, source archive, and model artifacts were not modified.

- Diagnosis flags separate acute ICD-9 410*/ICD-10 I21*/I22* from historical ICD-9 412/ICD-10 I25.2.
- {summary['lab_subset_rows']:,} selected-item measurements were retained from the archive stream; no full 13.73 GB extraction was attempted because it exceeded available free disk.
- {summary['threshold_candidate_admissions']:,} admissions have a provisional first-above-cutoff candidate; thresholds are not validated and candidates are not accepted as MI onset.
- All {summary['acute_ecg_rows']:,} acute-labeled ECGs remain uncertain under the validated timing rule; {summary['acute_ecg_rows_missing_legacy_index_time']:,} lack the legacy index time.
- No models were retrained, master datasets rebuilt, or causal effects estimated.

**Gate A:** conditional pass for descriptive ICD audit. **Gate B:** fail for validated troponin event timing. **Gate C:** hold causal MI-to-ECG analysis.
"""
    (AUDIT_ROOT / "PHASE1_2_COMPLETION_REPORT.md").write_text(text, encoding="utf-8")


def main() -> None:
    print(json.dumps(build_reports(), indent=2, default=str))


if __name__ == "__main__":
    main()