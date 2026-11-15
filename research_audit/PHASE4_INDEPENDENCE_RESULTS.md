# Phase 4 Conditional Independence Results

## Data and diagnostic

The diagnostic used `analysis_dataset.parquet` as finalized in Phase 3, filtered to `source_master_split == train` and `primary_analysis_eligible == True`. This yielded **116,935 admissions from 65,778 patients**: 5,171 acute-MI admissions and 111,764 clean comparisons. No data were rebuilt, and no validation/test rows were used.

For each physiological feature, least-squares residuals were computed after conditioning on acute MI diagnosis, age represented by a five-degree-of-freedom cubic spline, recorded sex, prior diabetes, prior hypertension, prior CKD, and prior MI. Pairwise residual Pearson correlation is the primary dependence measure; residual Spearman correlation is reported as a rank-based robustness measure. All 94 physiological features were included, giving 4,371 unique pairs. `QRS_Dur_Global_count` is technical support and was excluded from this physiological independence screen.

This is a practical diagnostic, not a formal conditional-independence test under arbitrary nonlinear models or unmeasured causes. No p-values are used to judge graph fit. Correlation flags at |r| >= 0.05 and |r| >= 0.10 are screening thresholds, not clinical thresholds.

## Results

- Median absolute residual Pearson correlation: **0.067**.
- 95th percentile: **0.459**.
- Maximum: **0.876** (R_Amp_III and R_Amp_aVL; residual Spearman rho 0.857).
- **2,628 / 4,371 (60.1%)** pairs had |r| >= 0.05.
- **1,673 / 4,371 (38.3%)** pairs had |r| >= 0.10.
- The strongest observed pairs include R_Amp_III/R_Amp_aVL (r=0.876), R_Amp_III/R_Amp_aVF (r=-0.852), R_Amp_V5/R_Amp_V6 (r=0.818), R_Amp_II/R_Amp_aVL (r=0.817), and T_Amp_V5/T_Amp_V6 (r=0.810). Rank-based correlations were similarly strong for these pairs.

## Practical interpretation

The pairwise results are not practically consistent with the sparse measured-parent implication that all distinct ECG features become independent after adjustment for MI and measured baseline factors. Dependence remains widespread and often large. This is an empirical contradiction of that **restricted factorization**.

The findings do not establish that the full causal graph is wrong. ECG features from the same tracing share electrical substrate and lead geometry; summary and IQR features can share source measurements. Unmeasured illness severity and conditioning on ECG availability can also leave or induce dependence. Those explanations are plausible but are not separately testable with the current selected dataset. The graph therefore remains a transparent working graph for review, with the measured-parent-only independence claim recorded as not supported. No edges were added or reoriented from this diagnostic.

## Other conditional-independence questions

- **Layer 1 risk factor and acute-MI pairs:** no independence is implied because the roadmap proposes a causal link. The training associations are not estimated in this phase.
- **Diabetes/hypertension ordering:** neither candidate ordering makes the pair independent given age and sex; this dataset cannot discover direction. Keep both orderings as roadmap sensitivities.
- **Prior MI and current MI:** the roadmap treats this as descriptive, not a causal discovery question. Do not infer direction from conditional independence tests.
- **MI and ECG outcomes:** independence is not implied by the proposed Layer 2 graph, which includes MI -> ECG.
- **ECG selection:** selection is constant among records in the analysis Parquet, so conditioning on the selection variable cannot be diagnosed from that file. The Phase 3 all-admission report is the available selection evidence. Severity/symptom pathways are unmeasured.

See `PHASE4_CONDITIONAL_INDEPENDENCE_TESTS.csv` for the complete 4,371-pair diagnostic results.
