"""Aggregate-only temporal audit of prepared inpatient disease diagnoses.

Uses the existing Phase 2.0-R index reconstruction in memory and exports one
aggregate row per disease. Patient-level identifiers and records are never
written. This is a source feasibility audit, not cohort construction or effect
estimation.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from phase2_0r_aggregate_feasibility import build_ephemeral_index  # noqa: E402


DISEASES = {
    "diabetes": ("ICD-9 250*", "ICD-10 E08*–E13*"),
    "hypertension": ("ICD-9 401*–405*", "ICD-10 I10*–I15*"),
    "ckd": ("ICD-9 585*", "ICD-10 N18*"),
}


def main() -> None:
    repo = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser()
    parser.add_argument("--longitudinal", type=Path, default=repo / "data/raw/longitudinal.rar")
    parser.add_argument(
        "--output",
        type=Path,
        default=repo / "revised/phase2/aggregates/PHASE2_BASELINE_DIAGNOSIS_TEMPORAL_SUMMARY.csv",
    )
    args = parser.parse_args()

    index, admissions, metadata = build_ephemeral_index(args.longitudinal)
    risk = index[["subject_id", "index_date", "window_start"]].copy()
    rows: list[dict[str, object]] = []
    for name, (icd9, icd10) in DISEASES.items():
        flagged = admissions.loc[admissions[name], ["subject_id", "admittime"]].copy()
        flagged["diagnosis_admission_date"] = pd.to_datetime(flagged["admittime"]).dt.normalize()
        source_people = int(flagged.subject_id.nunique())
        source_admissions = int(len(flagged))
        linked = flagged.merge(risk, on="subject_id", how="inner", validate="many_to_one")
        before = linked.diagnosis_admission_date < linked.window_start
        in_window = (
            (linked.diagnosis_admission_date >= linked.window_start)
            & (linked.diagnosis_admission_date < linked.index_date)
        )
        on_index = linked.diagnosis_admission_date == linked.index_date
        after = linked.diagnosis_admission_date > linked.index_date
        rows.append(
            {
                "disease": "CKD" if name == "ckd" else name,
                "icd9_rule": icd9,
                "icd10_rule": icd10,
                "source_admissions_with_diagnosis": source_admissions,
                "source_patients_with_diagnosis": source_people,
                "common_index_denominator": int(len(risk)),
                "eligible_people_ever_documented_across_source_admissions": int(linked.subject_id.nunique()),
                "eligible_people_with_diagnosis_before_window_start": int(linked.loc[before, "subject_id"].nunique()),
                "eligible_people_with_diagnosis_in_window_before_index": int(linked.loc[in_window, "subject_id"].nunique()),
                "eligible_people_with_diagnosis_on_index_date": int(linked.loc[on_index, "subject_id"].nunique()),
                "eligible_people_with_diagnosis_after_index": int(linked.loc[after, "subject_id"].nunique()),
                "earliest_diagnosis_admission_date_in_eligible_linkage": (
                    linked.diagnosis_admission_date.min().date().isoformat() if not linked.empty else ""
                ),
                "latest_diagnosis_admission_date_in_eligible_linkage": (
                    linked.diagnosis_admission_date.max().date().isoformat() if not linked.empty else ""
                ),
                "negative_disease_absence_indicator_supported": False,
                "source_and_timing_note": (
                    "diagnoses_all linked to admissions_chronology by patient/admission; "
                    "admission date is documentation proxy, not onset; counts include post-index records; "
                    "no code does not establish disease absence"
                ),
            }
        )

    output = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    print(
        f"Wrote {len(output)} disease-level aggregate rows; "
        f"common-index denominator={metadata['eligible_index_patients']}; "
        f"eligible before-window diagnosis counts are "
        f"{output['eligible_people_with_diagnosis_before_window_start'].tolist()}"
    )


if __name__ == "__main__":
    main()
