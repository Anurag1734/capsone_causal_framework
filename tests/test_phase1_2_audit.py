import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research_audit.phase1_2_audit_runner import (
    admission_diagnosis_audit,
    classify_diagnosis_codes,
    threshold_candidates,
    timing_class,
)
from research_audit.phase2b_troponin_audit import build_interval_linkage


def test_acute_and_historical_mi_codes_are_separate():
    diagnoses = pd.DataFrame(
        {
            "icd_version": [9, 9, 10, 10, 10],
            "icd_code": ["41091", "412", "I21A1", "I25.2", "I10"],
        }
    )

    classified = classify_diagnosis_codes(diagnoses)

    assert classified["acute_mi_code"].tolist() == [True, False, True, False, False]
    assert classified["historical_mi_code"].tolist() == [False, True, False, True, False]


def test_prior_mi_uses_only_earlier_admissions():
    admissions = pd.DataFrame(
        {
            "subject_id": [1, 1, 1],
            "hadm_id": [10, 11, 12],
            "admittime": pd.to_datetime(["2100-01-01", "2101-01-01", "2102-01-01"]),
        }
    )
    diagnoses = pd.DataFrame(
        {
            "subject_id": [1, 1],
            "hadm_id": [10, 11],
            "icd_version": [9, 10],
            "icd_code": ["412", "I21A1"],
        }
    )

    audit = admission_diagnosis_audit(diagnoses, admissions).set_index("hadm_id")

    assert bool(audit.loc[10, "historical_mi_code_this_admission"])
    assert not bool(audit.loc[10, "prior_mi_documentation"])
    assert bool(audit.loc[11, "acute_mi_this_admission"])
    assert bool(audit.loc[11, "prior_historical_mi_code_admission"])
    assert bool(audit.loc[12, "prior_acute_mi_admission"])


def test_non_mi_diagnoses_are_retained_in_admission_audit():
    admissions = pd.DataFrame(
        {"subject_id": [2], "hadm_id": [20], "admittime": pd.to_datetime(["2100-01-01"])}
    )
    diagnoses = pd.DataFrame(
        {"subject_id": [2], "hadm_id": [20], "icd_version": [10], "icd_code": ["I10"]}
    )

    audit = admission_diagnosis_audit(diagnoses, admissions)

    assert len(audit) == 1
    assert bool(audit.loc[0, "diagnosis_present_this_admission"])
    assert not bool(audit.loc[0, "acute_mi_this_admission"])


def test_threshold_candidates_require_strict_cutoff_unit_and_year():
    measurements = pd.DataFrame(
        {
            "itemid": [51003, 51003, 51003],
            "subject_id": [1, 1, 1],
            "hadm_id": [10, 10, 10],
            "valuenum": [0.014, 0.015, 0.02],
            "valueuom": ["ng/mL", "ng/mL", "ng/L"],
        }
    )
    thresholds = pd.DataFrame(
        {
            "itemid": [51003], "assay_type": ["cTnT"],
            "anchor_year_start": [2100], "anchor_year_end": [2250],
            "sex": ["ALL"], "url_value": [0.014], "unit": ["ng/mL"],
        }
    )
    demographics = pd.DataFrame(
        {"subject_id": [1], "gender": ["F"], "anchor_year": [2150]}
    )

    candidates = threshold_candidates(measurements, thresholds, demographics)

    assert candidates["threshold_candidate"].tolist() == [False, True, False]


def test_timing_class_reports_before_after_and_uncertain():
    ecg_times = pd.Series(pd.to_datetime(["2100-01-01 00:00", "2100-01-01 02:00", None]))
    event_times = pd.Series(pd.to_datetime(["2100-01-01 01:00", "2100-01-01 01:00", None]))

    assert timing_class(ecg_times, event_times).tolist() == ["before", "after", "uncertain"]

def test_missing_hadm_interval_linkage_does_not_assign_ambiguous_admissions():
    measurements = pd.DataFrame(
        {
            "labevent_id": [1, 2, 3],
            "subject_id": [1, 2, 3],
            "charttime": pd.to_datetime(["2150-01-02", "2150-01-02", "2150-01-02"]),
        }
    )
    admissions = pd.DataFrame(
        {
            "subject_id": [1, 2, 3, 3],
            "hadm_id": [10, 20, 30, 31],
            "admittime": pd.to_datetime(["2150-01-01", "2150-02-01", "2150-01-01", "2150-01-02"]),
            "edregtime": pd.to_datetime(["2150-01-01", "2150-02-01", "2150-01-01", "2150-01-02"]),
            "dischtime": pd.to_datetime(["2150-01-03", "2150-02-03", "2150-01-04", "2150-01-05"]),
        }
    )

    linkage = build_interval_linkage(measurements, admissions).set_index("labevent_id")

    assert linkage.loc[1, "interval_link_status"] == "unique_interval_candidate"
    assert linkage.loc[1, "unique_interval_candidate_hadm_id"] == 10
    assert linkage.loc[2, "interval_link_status"] == "no_interval_match"
    assert linkage.loc[2, "unique_interval_candidate_hadm_id"] is pd.NA or pd.isna(
        linkage.loc[2, "unique_interval_candidate_hadm_id"]
    )
    assert linkage.loc[3, "interval_link_status"] == "ambiguous_multiple_intervals"
    assert pd.isna(linkage.loc[3, "unique_interval_candidate_hadm_id"])
