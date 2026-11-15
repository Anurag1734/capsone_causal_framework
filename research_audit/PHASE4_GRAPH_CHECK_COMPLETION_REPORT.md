# Phase 4 Completion Report - Draw and Check the Causal Graph

## Completed outputs

1. `PHASE4_FINAL_CAUSAL_GRAPH.md` - proposed two-layer graph, Mermaid visualization, selection mechanism, assumptions, and timing limits.
2. `PHASE4_ADJUSTMENT_SETS.csv` - four Layer 1 exposure rows plus one Layer 2 row for each of the 95 existing handcrafted features.
3. `PHASE4_GRAPH_RATIONALE.md` - variable roles, adjustment rationale, selection, and test interpretation.
4. `PHASE4_CONDITIONAL_INDEPENDENCE_TESTS.csv` - 4,371 physiological feature-pair dependence diagnostics on training data.
5. `PHASE4_INDEPENDENCE_RESULTS.md` - sample, methods, results, practical interpretation, and untestable implications.
6. This completion report.

## Graph and adjustment sets

Layer 1 preserves the roadmap's exact sets: diabetes -> acute MI adjusted for age/sex; hypertension -> acute MI adjusted for age/sex; CKD -> acute MI adjusted for age/sex/diabetes/hypertension; prior MI -> acute MI adjusted for age/sex/diabetes/hypertension/CKD. The prior-MI relation is descriptive only. Diabetes and hypertension are not adjusted for CKD, and CKD is not adjusted for prior MI. Alternative diabetes/hypertension orderings remain sensitivity graphs.

Layer 2 represents acute MI diagnosis, age, sex, prior diabetes, prior hypertension, prior CKD, prior MI, the 95 handcrafted ECG outcomes, and selection into the ECG cohort. Each feature's set is age (flexible), sex, diabetes, hypertension, CKD, and prior MI. `QRS_Dur_Global_count` is marked technical/support. The 64 beta-VAE dimensions remain excluded.

The MI-to-ECG arrow is the roadmap's proposed direction, not a conclusion supported by timing data. Phase 3 establishes only that the chosen ECG was in the admission episode; it does not establish MI onset relative to that ECG. All Phase 4 empirical work is restricted to selected ECG admissions and does not identify effects for all admissions or the community.

## Independence checks

On 116,935 training primary-cohort admissions from 65,778 patients, the measured-parent-only Layer 2 representation's feature-pair independence implication was assessed for 94 physiological features. There were 4,371 pairs. Median |partial r| was 0.067, the 95th percentile was 0.459, and maximum |r| was 0.876. A total of 60.1% of pairs had |r| >= 0.05 and 38.3% had |r| >= 0.10. Rank-based residual correlations agreed with the strongest Pearson results.

This contradicts the sparse measured-parent-only factorization in practical terms. Shared waveform physiology, lead structure, common source measurements, latent severity, and ECG selection may explain the residual dependence. These possibilities cannot be separated with available variables. The draft graph was not silently changed; its independence implication and this contradiction are documented for review.

Layer 1 exposure-outcome and MI-feature independence is not implied because the graph proposes causal arrows. The alternative diabetes/hypertension orderings, prior MI relationship, and the selection collider cannot be discovered by conditional independence checks with the available selected dataset. The Phase 3 selection-bias report is reused without rebuilding or repeating its audit.

## Ready for Phase 5

The graph and exposure-specific adjustment schedules are locked as the Phase 4 proposal. The training diagnostics and unresolved graph implication are documented for review. Phase 5 effect estimation has **not** been started. Before Phase 5, review whether to retain the proposed MI-to-ECG causal interpretation given unknown event timing, and whether to treat ECG feature dependence as expected shared measurement structure in the Layer 2 model. No roadmap change has been made or requires approval to complete Phase 4; those are explicit review decisions before making stronger causal claims.

## Reproducibility

`create_phase4_deliverables.py` reads the finalized Phase 3 dataset and existing feature-group dictionary, filters only the original training split and primary analysis cohort, computes the stated residual correlations, and writes the adjustment and independence CSVs. It does not write to or rebuild the Parquet, selection cohort, baseline models, or latent embeddings.
