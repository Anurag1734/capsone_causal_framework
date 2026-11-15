"""Build a separate admission-level, diagnosis-based ECG association dataset."""

from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
LONGITUDINAL = RAW / "longitudinal"
MASTER = RAW / "master_dataset"
AUDIT = ROOT / "research_audit"
OUT = ROOT / "data" / "analysis" / "observational_mi_ecg"
SPLITS = ("train", "validation", "test")
FEATURE_PREFIXES = ("Q_Amp_", "R_Amp_", "T_Amp_", "ST_Elev_", "S_Amp_")
GLOBAL_FEATURES = {
    "QRS_Dur_Global",
    "QRS_Dur_Global_iqr",
    "QRS_Dur_Global_count",
    "RR_Mean_Global",
    "RR_Mean_Global_iqr",
}
AUDIT_FLAGS = [
    "acute_mi_this_admission",
    "historical_mi_code_this_admission",
    "prior_mi_documentation",
    "prior_diabetes_code",
    "prior_hypertension_code",
    "prior_ckd_code",
]


def _feature_group(name: str) -> tuple[str, str, str, bool, str]:
    if name.startswith("ST_Elev_"):
        return "ST", "ST-segment elevation", "ECGdeli ST elevation summary", True, "Physiological morphology"
    if name.startswith("Q_Amp_"):
        suffix = " beat-to-beat IQR" if name.endswith("_iqr") else ""
        return "Q", "Q-wave amplitude" + suffix, "ECGdeli Q-wave amplitude summary", True, "Physiological morphology"
    if name.startswith("R_Amp_"):
        suffix = " beat-to-beat IQR" if name.endswith("_iqr") else ""
        return "R", "R-wave amplitude" + suffix, "ECGdeli R-wave amplitude summary", True, "Physiological morphology"
    if name.startswith("T_Amp_"):
        suffix = " beat-to-beat IQR" if name.endswith("_iqr") else ""
        return "T", "T-wave amplitude" + suffix, "ECGdeli T-wave amplitude summary", True, "Physiological morphology"
    if name.startswith("S_Amp_"):
        suffix = " beat-to-beat IQR" if name.endswith("_iqr") else ""
        return "Other morphology", "S-wave amplitude" + suffix, "ECGdeli S-wave amplitude summary", True, "Physiological morphology"
    if name == "QRS_Dur_Global_count":
        return "Signal/measurement support", "QRS duration count variant", "Count-valued companion to the QRS duration summary; exact semantics not independently documented", False, "Technical/support metric; not a physiological outcome"
    if name.startswith("QRS_Dur_Global"):
        suffix = " beat-to-beat IQR" if name.endswith("_iqr") else ""
        return "QRS", "Global QRS duration" + suffix, "ECGdeli global QRS duration summary", True, "Physiological morphology"
    if name.startswith("RR_Mean_Global"):
        suffix = " beat-to-beat IQR" if name.endswith("_iqr") else ""
        return "RR", "Global RR interval" + suffix, "ECGdeli global RR interval summary", True, "Physiological morphology"
    raise ValueError(f"Unclassified handcrafted ECG feature: {name}")


def _standardized_difference(left: pd.Series, right: pd.Series) -> float:
    left = pd.to_numeric(left, errors="coerce").dropna().astype(float)
    right = pd.to_numeric(right, errors="coerce").dropna().astype(float)
    if left.empty or right.empty:
        return np.nan
    pooled_sd = np.sqrt((left.var(ddof=1) + right.var(ddof=1)) / 2)
    if not np.isfinite(pooled_sd) or pooled_sd == 0:
        return 0.0 if left.mean() == right.mean() else np.nan
    return float((left.mean() - right.mean()) / pooled_sd)


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, na_rep="")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _selection_diagnostics(admissions: pd.DataFrame) -> pd.DataFrame:
    adult = admissions.loc[admissions["anchor_age"].notna() & admissions["anchor_age"].ge(18)].copy()
    has_ecg = adult["has_eligible_ecg"].astype(bool)
    selected = adult.loc[has_ecg]
    not_selected = adult.loc[~has_ecg]
    rows: list[dict[str, object]] = []

    def add_continuous(name: str, values: pd.Series) -> None:
        left = values.loc[has_ecg]
        right = values.loc[~has_ecg]
        rows.append(
            {
                "metric": name,
                "with_ecg_n": int(left.notna().sum()),
                "with_ecg_value": float(left.mean()),
                "without_ecg_n": int(right.notna().sum()),
                "without_ecg_value": float(right.mean()),
                "standardized_mean_difference": _standardized_difference(left, right),
                "missing_with_ecg": int(left.isna().sum()),
                "missing_without_ecg": int(right.isna().sum()),
            }
        )

    def add_binary(name: str, values: pd.Series) -> None:
        values = values.astype("boolean")
        left = values.loc[has_ecg]
        right = values.loc[~has_ecg]
        rows.append(
            {
                "metric": name,
                "with_ecg_n": int(left.notna().sum()),
                "with_ecg_value": float(left.mean()),
                "without_ecg_n": int(right.notna().sum()),
                "without_ecg_value": float(right.mean()),
                "standardized_mean_difference": _standardized_difference(
                    left.astype(float), right.astype(float)
                ),
                "missing_with_ecg": int(left.isna().sum()),
                "missing_without_ecg": int(right.isna().sum()),
            }
        )

    add_continuous("age_years", adult["anchor_age"])
    add_binary("sex_female", adult["gender"].astype("string").str.upper().eq("F").astype("boolean"))
    for column in [
        "acute_mi_diagnosis",
        "historical_mi_this_admission",
        "diabetes_prior",
        "hypertension_prior",
        "ckd_prior",
        "prior_mi",
    ]:
        add_binary(column, adult[column])

    selected_sex = selected["gender"].astype("string").str.upper().fillna("MISSING")
    not_selected_sex = not_selected["gender"].astype("string").str.upper().fillna("MISSING")
    for category in ("F", "M", "MISSING"):
        rows.append(
            {
                "metric": f"sex_category_{category}",
                "with_ecg_n": len(selected),
                "with_ecg_value": float(selected_sex.eq(category).mean()),
                "without_ecg_n": len(not_selected),
                "without_ecg_value": float(not_selected_sex.eq(category).mean()),
                "standardized_mean_difference": np.nan,
                "missing_with_ecg": int(selected_sex.eq("MISSING").sum()),
                "missing_without_ecg": int(not_selected_sex.eq("MISSING").sum()),
                "notes": "Category proportion; SMD is separately reported for female versus other.",
            }
        )

    model_data = adult[
        [
            "has_eligible_ecg",
            "anchor_age",
            "gender",
            "acute_mi_diagnosis",
            "historical_mi_this_admission",
            "diabetes_prior",
            "hypertension_prior",
            "ckd_prior",
            "prior_mi",
        ]
    ].copy()
    model_x = pd.DataFrame(index=model_data.index)
    model_x["age_years"] = model_data["anchor_age"].astype(float)
    gender = model_data["gender"].astype("string").str.upper()
    model_x["sex_female"] = gender.eq("F").astype(int)
    model_x["sex_male"] = gender.eq("M").astype(int)
    model_x["sex_missing_or_other"] = (~gender.isin(["F", "M"])).astype(int)
    for column in [
        "acute_mi_diagnosis",
        "historical_mi_this_admission",
        "diabetes_prior",
        "hypertension_prior",
        "ckd_prior",
        "prior_mi",
    ]:
        model_x[column] = model_data[column].astype(int)

    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        selection_model = LogisticRegression(max_iter=1000, solver="lbfgs")
        selection_model.fit(model_x, model_data["has_eligible_ecg"].astype(int))
    propensity = pd.Series(selection_model.predict_proba(model_x)[:, 1], index=adult.index)
    p_selected = propensity.loc[has_ecg]
    p_not_selected = propensity.loc[~has_ecg]
    overlap_low = max(float(p_selected.min()), float(p_not_selected.min()))
    overlap_high = min(float(p_selected.max()), float(p_not_selected.max()))
    inverse_weights = 1 / p_selected
    stabilized_weights = (float(has_ecg.mean())) / p_selected
    weight_ess = float(inverse_weights.sum() ** 2 / (inverse_weights.pow(2).sum()))
    stabilized_ess = float(stabilized_weights.sum() ** 2 / (stabilized_weights.pow(2).sum()))
    selection_rows = [
        ("adult_admissions", len(adult), "Admissions with nonmissing anchor age >= 18"),
        ("adult_admissions_with_eligible_ecg", int(has_ecg.sum()), "At least one ECG within ED/admission-to-discharge interval"),
        ("adult_admissions_without_eligible_ecg", int((~has_ecg).sum()), "No master ECG within the defined episode"),
        ("ecg_selection_rate", float(has_ecg.mean()), "Proportion of adult admissions with an eligible ECG"),
        ("selection_propensity_with_ecg_min", float(p_selected.min()), "Predicted from logistic ECG-selection diagnostic model"),
        ("selection_propensity_with_ecg_p01", float(p_selected.quantile(0.01)), "Predicted from logistic ECG-selection diagnostic model"),
        ("selection_propensity_with_ecg_median", float(p_selected.median()), "Predicted from logistic ECG-selection diagnostic model"),
        ("selection_propensity_with_ecg_p99", float(p_selected.quantile(0.99)), "Predicted from logistic ECG-selection diagnostic model"),
        ("selection_propensity_with_ecg_max", float(p_selected.max()), "Predicted from logistic ECG-selection diagnostic model"),
        ("selection_propensity_without_ecg_min", float(p_not_selected.min()), "Predicted from logistic ECG-selection diagnostic model"),
        ("selection_propensity_without_ecg_median", float(p_not_selected.median()), "Predicted from logistic ECG-selection diagnostic model"),
        ("selection_propensity_without_ecg_max", float(p_not_selected.max()), "Predicted from logistic ECG-selection diagnostic model"),
        ("common_propensity_support_lower", overlap_low, "Intersection of observed fitted-propensity ranges"),
        ("common_propensity_support_upper", overlap_high, "Intersection of observed fitted-propensity ranges"),
        ("common_propensity_support_nonempty", bool(overlap_low <= overlap_high), "Range-overlap diagnostic; not proof of conditional positivity"),
        ("unweighted_ecg_sample_ess", float(len(selected)), "Selected-admission sample size"),
        ("inverse_probability_weight_ess_unstabilized", weight_ess, "Diagnostic only; no weights applied to outcome estimates"),
        ("inverse_probability_weight_ess_stabilized", stabilized_ess, "Diagnostic only; no weights applied to outcome estimates"),
        ("inverse_probability_weight_max", float(inverse_weights.max()), "Diagnostic only; no trimming rule applied"),
        ("inverse_probability_weight_p99", float(inverse_weights.quantile(0.99)), "Diagnostic only; no trimming rule applied"),
    ]
    rows.extend(
        {
            "metric": name,
            "with_ecg_n": "",
            "with_ecg_value": value,
            "without_ecg_n": "",
            "without_ecg_value": "",
            "standardized_mean_difference": "",
            "missing_with_ecg": "",
            "missing_without_ecg": "",
            "notes": note,
        }
        for name, value, note in selection_rows
    )
    result = pd.DataFrame(rows)
    if "notes" not in result.columns:
        result["notes"] = ""
    return result


def _variable_dictionary(dataset: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    definitions = {
        "patient_id": ("identifier", "int64", "Master SubjectID", "Patient identifier; repeated across admissions.", "Cluster inference by patient."),
        "admission_id": ("identifier", "int64", "Master hadm_id", "Hospital admission identifier; unique in the analysis dataset.", "Analysis unit identifier."),
        "ecg_id": ("identifier", "int64", "Master study_id", "ECG study identifier of the selected record.", "One selected ECG per admission."),
        "ecg_time": ("timestamp", "datetime", "Master ecg_time", "Timestamp of the selected ECG.", "Selection/provenance only; not an MI event time."),
        "source_master_split": ("provenance", "string", "Master train/validation/test parquet", "Source split containing the selected ECG row.", "Source provenance only; not an analysis split."),
        "ecg_count_in_admission": ("selection", "int64", "Filtered master ECG rows", "Number of ECG rows in the defined encounter interval for this admission.", "Describes repeated ECG handling."),
        "ecg_selection_rank": ("selection", "int64", "Deterministic rule", "Rank of selected ECG; always 1 after sorting by timestamp then study_id.", "One row per admission."),
        "ecg_selection_rule": ("selection", "string", "Deterministic rule", "Earliest in-encounter ECG; ties broken by lowest study_id.", "Outcome-independent selection."),
        "age_years": ("adjustment", "numeric", "patients_demographics.anchor_age", "MIMIC anchor age; top-coded/deidentified according to source conventions.", "Baseline candidate adjustment variable."),
        "sex": ("adjustment", "category", "patients_demographics.gender", "Recorded M/F category; not an intervention.", "Baseline candidate adjustment variable."),
        "acute_mi_diagnosis": ("exposure", "boolean", "Corrected admission diagnosis audit", "Acute ICD-9 410* or ICD-10 I21*/I22* on this admission.", "Primary exposure; no troponin labels."),
        "historical_mi_this_admission": ("diagnosis", "boolean", "Corrected admission diagnosis audit", "ICD-9 412 or ICD-10 I25.2 on this admission.", "Kept distinct from acute MI."),
        "historical_mi_documented": ("adjustment", "boolean", "Corrected admission diagnosis audit", "Historical MI code on this admission or MI documented in an earlier admission.", "Descriptive/history adjustment; not an outcome."),
        "prior_mi": ("adjustment", "boolean", "Corrected admission diagnosis audit", "Any acute or historical MI diagnosis documented in an earlier admission.", "Baseline candidate adjustment variable."),
        "diabetes_prior": ("adjustment", "boolean", "Corrected admission diagnosis audit", "Diabetes code documented in an earlier admission.", "Baseline candidate adjustment variable."),
        "hypertension_prior": ("adjustment", "boolean", "Corrected admission diagnosis audit", "Hypertension code documented in an earlier admission.", "Baseline candidate adjustment variable."),
        "ckd_prior": ("adjustment", "boolean", "Corrected admission diagnosis audit", "CKD code documented in an earlier admission.", "Baseline candidate adjustment variable."),
        "mi_diagnosis_group": ("cohort", "category", "Derived from corrected diagnosis flags", "acute_mi, historical_or_prior_mi_no_acute, or no_documented_mi.", "Keeps historical/prior MI distinct."),
        "primary_analysis_eligible": ("cohort", "boolean", "Derived cohort rule", "Adult ECG admission; acute MI cases or nonacute admissions without documented current/prior MI.", "Primary binary comparison eligibility."),
        "feature_complete": ("quality", "boolean", "Derived from the 95 handcrafted features", "True when all 95 feature values are finite and nonmissing.", "Data completeness check; does not determine cohort eligibility."),
    }
    for variable, (role, data_type, source, definition, use) in definitions.items():
        series = dataset[variable]
        rows.append(
            {
                "variable": variable,
                "role": role,
                "data_type": data_type,
                "source": source,
                "definition": definition,
                "analysis_use": use,
                "missing_n": int(series.isna().sum()),
                "missing_rate": float(series.isna().mean()),
                "feature_group": "",
            }
        )
    for feature in feature_columns:
        group, subfamily, description, physiological, role = _feature_group(feature)
        series = dataset[feature]
        rows.append(
            {
                "variable": feature,
                "role": "technical/support" if not physiological else "ECG outcome",
                "data_type": str(series.dtype),
                "source": "Existing master ECG feature",
                "definition": f"{subfamily}; {description}. Unit retained as stored in the master; not independently verified here.",
                "analysis_use": role,
                "missing_n": int(series.isna().sum()),
                "missing_rate": float(series.isna().mean()),
                "feature_group": group,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    feature_names = pq.read_schema(MASTER / "train.parquet").names
    feature_columns = [
        name
        for name in feature_names
        if name.startswith(FEATURE_PREFIXES) or name in GLOBAL_FEATURES
    ]
    if len(feature_columns) != 95:
        raise ValueError(f"Expected 95 handcrafted features; found {len(feature_columns)}.")

    master_frames = []
    for split in SPLITS:
        frame = pd.read_parquet(
            MASTER / f"{split}.parquet",
            columns=["study_id", "SubjectID", "hadm_id", "ecg_time", *feature_columns],
        )
        frame["source_master_split"] = split
        master_frames.append(frame)
    ecgs = pd.concat(master_frames, ignore_index=True)
    if ecgs["study_id"].isna().any() or ecgs["study_id"].duplicated().any():
        raise ValueError("Master ECG study_id must be nonmissing and unique across splits.")
    if ecgs[["SubjectID", "hadm_id", "ecg_time"]].isna().any().any():
        raise ValueError("Master patient, admission, and ECG time fields must be complete.")
    ecgs["ecg_time"] = pd.to_datetime(ecgs["ecg_time"], errors="raise")

    admissions = pd.read_parquet(
        LONGITUDINAL / "admissions_chronology.parquet",
        columns=["subject_id", "hadm_id", "admittime", "dischtime", "edregtime"],
    )
    if admissions["hadm_id"].isna().any() or admissions["hadm_id"].duplicated().any():
        raise ValueError("Admission chronology must have a unique, nonmissing hadm_id.")
    audit = pd.read_csv(AUDIT / "ACUTE_MI_DIAGNOSIS_BY_ADMISSION.csv")
    if audit["hadm_id"].duplicated().any():
        raise ValueError("Corrected admission diagnosis audit must have unique hadm_id.")
    if not set(AUDIT_FLAGS).issubset(audit.columns):
        raise ValueError("Corrected admission diagnosis audit is missing required flags.")
    audit_columns = ["subject_id", "hadm_id", *AUDIT_FLAGS]
    admission_data = admissions.merge(
        audit[audit_columns],
        on=["subject_id", "hadm_id"],
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    if not admission_data["_merge"].eq("both").all():
        raise ValueError("Diagnosis audit must cover every admission in the chronology.")
    admission_data = admission_data.drop(columns="_merge")
    if admission_data[AUDIT_FLAGS].isna().any().any():
        raise ValueError("Diagnosis flags must be populated for every admission.")
    admission_data[AUDIT_FLAGS] = admission_data[AUDIT_FLAGS].astype(bool)

    demographics = pd.read_parquet(
        LONGITUDINAL / "patients_demographics.parquet",
        columns=["subject_id", "anchor_age", "gender"],
    )
    if demographics["subject_id"].duplicated().any():
        raise ValueError("Patient demographics must have one row per subject_id.")
    admission_data = admission_data.merge(
        demographics,
        on="subject_id",
        how="left",
        validate="many_to_one",
    )
    admission_data["acute_mi_diagnosis"] = admission_data["acute_mi_this_admission"]
    admission_data["historical_mi_this_admission"] = admission_data[
        "historical_mi_code_this_admission"
    ]
    admission_data["historical_mi_documented"] = (
        admission_data["historical_mi_code_this_admission"]
        | admission_data["prior_mi_documentation"]
    )
    admission_data["prior_mi"] = admission_data["prior_mi_documentation"]
    admission_data["diabetes_prior"] = admission_data["prior_diabetes_code"]
    admission_data["hypertension_prior"] = admission_data["prior_hypertension_code"]
    admission_data["ckd_prior"] = admission_data["prior_ckd_code"]

    ecg_admissions = ecgs.merge(
        admissions,
        left_on="hadm_id",
        right_on="hadm_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    if not ecg_admissions["_merge"].eq("both").all():
        raise ValueError("Every master ECG admission must exist in the admission chronology.")
    subject_mismatch = ecg_admissions["SubjectID"].ne(ecg_admissions["subject_id"])
    if subject_mismatch.any():
        raise ValueError(f"Found {int(subject_mismatch.sum())} master ECG patient/admission mismatches.")
    episode_end = pd.to_datetime(ecg_admissions["dischtime"], errors="coerce")
    admission_start = pd.to_datetime(ecg_admissions["admittime"], errors="coerce")
    ed_registration = pd.to_datetime(ecg_admissions["edregtime"], errors="coerce")
    invalid_ed_registration = ed_registration.isna() | ed_registration.gt(episode_end)
    episode_start = ed_registration.where(~invalid_ed_registration, admission_start)
    invalid_ed_registration_rows = int(
        (ed_registration.notna() & ed_registration.gt(episode_end)).sum()
    )
    missing_episode_bounds = int((episode_start.isna() | episode_end.isna()).sum())
    invalid_episode_bounds = int(episode_start.gt(episode_end).sum())
    in_episode = (
        ecg_admissions["ecg_time"].ge(episode_start)
        & ecg_admissions["ecg_time"].le(episode_end)
    )
    outside_episode_rows = int((~in_episode).sum())
    eligible_ecgs = ecg_admissions.loc[in_episode].drop(columns="_merge").copy()
    if eligible_ecgs.empty:
        raise ValueError("No master ECG records fall within an ED/admission-to-discharge interval.")
    eligible_ecgs = eligible_ecgs.sort_values(
        ["hadm_id", "ecg_time", "study_id", "source_master_split"],
        kind="mergesort",
    )
    ecg_count_by_admission = eligible_ecgs.groupby("hadm_id", sort=False).size()
    selected = eligible_ecgs.drop_duplicates("hadm_id", keep="first").copy()
    selected["ecg_count_in_admission"] = selected["hadm_id"].map(ecg_count_by_admission).astype("int64")
    selected["ecg_selection_rank"] = 1
    selected["ecg_selection_rule"] = "earliest_in_encounter; ties by lowest study_id"

    flags = admission_data[
        [
            "subject_id",
            "hadm_id",
            "acute_mi_diagnosis",
            "historical_mi_code_this_admission",
            "historical_mi_documented",
            "prior_mi",
            "diabetes_prior",
            "hypertension_prior",
            "ckd_prior",
            "anchor_age",
            "gender",
        ]
    ]
    selected = selected.merge(
        flags,
        on=["subject_id", "hadm_id"],
        how="left",
        validate="one_to_one",
    )
    adult = selected["anchor_age"].notna() & selected["anchor_age"].ge(18)
    selected = selected.loc[adult].copy()
    selected = selected.rename(
        columns={
            "SubjectID": "patient_id",
            "hadm_id": "admission_id",
            "study_id": "ecg_id",
            "anchor_age": "age_years",
            "gender": "sex",
            "historical_mi_code_this_admission": "historical_mi_this_admission",
        }
    )
    selected["mi_diagnosis_group"] = np.select(
        [
            selected["acute_mi_diagnosis"],
            selected["historical_mi_documented"],
        ],
        [
            "acute_mi",
            "historical_or_prior_mi_no_acute",
        ],
        default="no_documented_mi",
    )
    selected["primary_analysis_eligible"] = selected["acute_mi_diagnosis"] | (
        ~selected["historical_mi_documented"]
    )
    selected["feature_complete"] = np.isfinite(
        selected[feature_columns].to_numpy(dtype=float)
    ).all(axis=1)

    output_columns = [
        "patient_id",
        "admission_id",
        "ecg_id",
        "ecg_time",
        "source_master_split",
        "ecg_count_in_admission",
        "ecg_selection_rank",
        "ecg_selection_rule",
        "acute_mi_diagnosis",
        "historical_mi_this_admission",
        "historical_mi_documented",
        "prior_mi",
        "diabetes_prior",
        "hypertension_prior",
        "ckd_prior",
        "age_years",
        "sex",
        "mi_diagnosis_group",
        "primary_analysis_eligible",
        "feature_complete",
        *feature_columns,
    ]
    dataset = selected[output_columns].copy()
    if dataset["admission_id"].duplicated().any():
        raise ValueError("Analysis dataset contains more than one selected ECG per admission.")
    if dataset["ecg_id"].duplicated().any():
        raise ValueError("Selected ECG identifiers must be unique.")

    eligible_admissions = admission_data["anchor_age"].notna() & admission_data["anchor_age"].ge(18)
    admission_data["has_eligible_ecg"] = admission_data["hadm_id"].isin(
        set(eligible_ecgs["hadm_id"])
    )
    admission_data["historical_mi_documented"] = (
        admission_data["historical_mi_code_this_admission"]
        | admission_data["prior_mi_documentation"]
    )
    selection_table = _selection_diagnostics(admission_data)

    primary = dataset.loc[dataset["primary_analysis_eligible"]]
    counts = [
        ("all_admissions_in_chronology", len(admission_data), "Full admission denominator"),
        ("adult_admissions_with_age", int(eligible_admissions.sum()), "Anchor age nonmissing and >=18"),
        ("adult_ineligible_admissions", int((admission_data["anchor_age"].isna() | admission_data["anchor_age"].lt(18)).sum()), "Anchor age missing or below 18"),
        ("master_ecg_rows_all_splits", len(ecgs), "Rows read from existing train/validation/test masters"),
        ("master_ecg_rows_edregtime_after_discharge", invalid_ed_registration_rows, "Invalid ED registration boundary; inpatient admission time used instead"),
        ("master_ecg_rows_missing_episode_boundary", missing_episode_bounds, "Missing ED/admission start or discharge boundary"),
        ("master_ecg_rows_invalid_episode_boundary_excluded", invalid_episode_bounds, "Admission start remained after discharge after fallback"),
        ("master_ecg_rows_outside_episode", outside_episode_rows, "Excluded from ECG selection; outside ED/admission-to-discharge interval"),
        ("master_ecg_rows_inside_episode", len(eligible_ecgs), "Eligible in-encounter ECG candidates"),
        ("adult_admissions_with_eligible_ecg", int(admission_data.loc[eligible_admissions, "has_eligible_ecg"].sum()), "At least one in-encounter ECG"),
        ("adult_admissions_without_eligible_ecg", int((~admission_data.loc[eligible_admissions, "has_eligible_ecg"]).sum()), "No in-encounter master ECG"),
        ("adult_selected_ecg_admissions", len(dataset), "One earliest ECG per adult admission"),
        ("adult_selected_patients", int(dataset["patient_id"].nunique()), "Patients represented in selected ECG dataset"),
        ("adult_acute_mi_ecg_admissions", int(dataset["acute_mi_diagnosis"].sum()), "Acute ICD diagnosis and selected ECG"),
        ("adult_historical_or_prior_mi_no_acute_admissions", int((dataset["mi_diagnosis_group"] == "historical_or_prior_mi_no_acute").sum()), "Separate history group, retained for sensitivity analyses"),
        ("adult_no_documented_mi_ecg_admissions", int((dataset["mi_diagnosis_group"] == "no_documented_mi").sum()), "No acute or documented historical/prior MI"),
        ("primary_analysis_eligible_admissions", len(primary), "Acute cases or clean no-history comparison admissions"),
        ("primary_analysis_acute_cases", int(primary["acute_mi_diagnosis"].sum()), "Primary acute diagnosis group"),
        ("primary_analysis_comparison_admissions", int((~primary["acute_mi_diagnosis"]).sum()), "No acute or documented historical/prior MI"),
        ("primary_analysis_patients", int(primary["patient_id"].nunique()), "May include repeat admissions; cluster by patient"),
        ("usable_complete_feature_records", int(dataset["feature_complete"].sum()), "All 95 feature values finite and nonmissing"),
        ("selected_ecg_rows_per_admission", int(dataset["admission_id"].nunique()), "Must equal one"),
        ("selected_ecg_rows_per_ecg_id", int(dataset["ecg_id"].nunique()), "Must equal one"),
        ("admissions_with_repeated_ecg_records", int((ecg_count_by_admission > 1).sum()), "Additional ECG rows not selected for primary dataset"),
    ]
    _write_csv(
        pd.DataFrame(counts, columns=["metric", "value", "definition"]),
        OUT / "cohort_counts.csv",
    )
    _write_csv(selection_table, OUT / "selection_diagnostics.csv")

    missing_rows = []
    for column in output_columns:
        series = dataset[column]
        missing_rows.append(
            {
                "variable": column,
                "rows": len(dataset),
                "missing_n": int(series.isna().sum()),
                "missing_rate": float(series.isna().mean()),
                "nonfinite_n": int(
                    (~np.isfinite(series.to_numpy(dtype=float))).sum()
                    if pd.api.types.is_numeric_dtype(series)
                    else 0
                ),
            }
        )
    _write_csv(pd.DataFrame(missing_rows), OUT / "dataset_missingness.csv")

    group_rows = []
    for feature in feature_columns:
        group, subfamily, description, physiological, analysis_role = _feature_group(feature)
        group_rows.append(
            {
                "feature": feature,
                "feature_group": group,
                "subfamily": subfamily,
                "description": description,
                "physiological_outcome": physiological,
                "analysis_role": analysis_role,
                "primary_inference_family": "95-feature multiplicity family; interpret technical/support metrics separately",
                "recorded_unit": "As stored in the master; not independently verified",
            }
        )
    feature_groups = pd.DataFrame(group_rows)
    _write_csv(feature_groups, AUDIT / "PHASE3_ECG_FEATURE_GROUPS.csv")
    dictionary = _variable_dictionary(dataset, feature_columns)
    _write_csv(dictionary, AUDIT / "PHASE3_VARIABLE_DICTIONARY.csv")

    output_path = OUT / "analysis_dataset.parquet"
    dataset.to_parquet(output_path, index=False)
    quality = [
        ("all_admissions_have_diagnosis_audit_row", bool(len(admission_data) == len(admissions)), "Admission diagnosis coverage"),
        ("master_patient_admission_links_match", True, "Every master SubjectID matches chronology subject_id"),
        ("master_ecg_episode_boundaries_complete", bool(missing_episode_bounds == 0), "All ECG-linked admissions have start and discharge times"),
        ("invalid_master_episode_rows_excluded", invalid_episode_bounds, "Admission start remained after discharge even after fallback"),
        ("selected_ecg_episode_boundaries_ordered", bool((episode_start.loc[in_episode] <= episode_end.loc[in_episode]).all()), "All selected ECGs have ordered episode bounds"),
        ("master_study_id_unique", True, "Verified across source splits"),
        ("analysis_admission_id_unique", bool(not dataset["admission_id"].duplicated().any()), "One row per admission"),
        ("analysis_ecg_id_unique", bool(not dataset["ecg_id"].duplicated().any()), "One ECG selected once"),
        ("analysis_feature_count_95", bool(len(feature_columns) == 95), "Handcrafted feature count"),
        ("analysis_feature_complete_rows", int(dataset["feature_complete"].sum()), "All 95 outcomes finite and nonmissing"),
        ("analysis_feature_incomplete_rows", int((~dataset["feature_complete"]).sum()), "Retained; no silent row deletion"),
        ("beta_vae_latents_included", False, "Excluded because provenance is unresolved"),
        ("troponin_labels_or_event_times_included", False, "Excluded from primary diagnosis-based dataset"),
        ("original_master_splits_modified", False, "Read-only input"),
        ("diagnosis_parquets_modified", False, "Read-only inputs"),
    ]
    _write_csv(
        pd.DataFrame(quality, columns=["check", "result", "notes"]),
        OUT / "data_quality_checks.csv",
    )

    manifest = {
        "dataset_path": str(output_path.relative_to(ROOT)),
        "row_count": len(dataset),
        "column_count": len(dataset.columns),
        "feature_count": len(feature_columns),
        "selected_ecg_per_admission": "earliest timestamp from valid ED registration (otherwise admission time) through discharge; ties by lowest study_id",
        "diagnosis_source": "research_audit/ACUTE_MI_DIAGNOSIS_BY_ADMISSION.csv",
        "master_sources": [f"data/raw/master_dataset/{split}.parquet" for split in SPLITS],
        "other_sources": [
            "data/raw/longitudinal/admissions_chronology.parquet",
            "data/raw/longitudinal/patients_demographics.parquet",
        ],
        "troponin_based_outcome_or_event_time_used": False,
        "beta_vae_latents_included": False,
        "dataset_sha256": _sha256(output_path),
        "columns": output_columns,
    }
    (OUT / "dataset_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "dataset": str(output_path),
                "rows": len(dataset),
                "columns": len(dataset.columns),
                "patients": int(dataset["patient_id"].nunique()),
                "admissions": int(dataset["admission_id"].nunique()),
                "primary_eligible": len(primary),
                "primary_cases": int(primary["acute_mi_diagnosis"].sum()),
                "primary_comparators": int((~primary["acute_mi_diagnosis"]).sum()),
                "complete_feature_records": int(dataset["feature_complete"].sum()),
                "outside_episode_ecgs": outside_episode_rows,
                "sha256": manifest["dataset_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
