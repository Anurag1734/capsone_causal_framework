# Phase 1-2 Audit Completion Report

The runner was updated to use the current `data/raw/longitudinal/` and `data/raw/master_dataset/` paths. It audited the diagnosis Parquet, admission chronology, master splits, threshold transcription, and streamed lab subset. Original diagnosis derivatives, master datasets, source archive, and model artifacts were not modified.

- Diagnosis flags separate acute ICD-9 410*/ICD-10 I21*/I22* from historical ICD-9 412/ICD-10 I25.2.
- 359,163 selected-item measurements were retained from the archive stream; no full 13.73 GB extraction was attempted because it exceeded available free disk.
- 38,077 admissions have a provisional first-above-cutoff candidate; thresholds are not validated and candidates are not accepted as MI onset.
- All 7,604 acute-labeled ECGs remain uncertain under the validated timing rule; 3,053 lack the legacy index time.
- No models were retrained, master datasets rebuilt, or causal effects estimated.

**Gate A:** conditional pass for descriptive ICD audit. **Gate B:** fail for validated troponin event timing. **Gate C:** hold causal MI-to-ECG analysis.
