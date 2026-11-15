# Phase 5 Bootstrap Results

Patient-level percentile bootstrap intervals use 1,000 resamples (seed 20261115). Each draw samples the number of unique patients with replacement and includes every selected admission for each sampled patient. Cross-fitted nuisance predictions are held fixed; the bootstrap resamples cross-fitted estimating scores and crude mean-difference contributions. Intervals quantify patient-cluster sampling uncertainty conditional on those nuisance fits, not additional nuisance-refitting uncertainty.

Layer 1 includes 99,214 patient clusters; Layer 2 includes 93,946. The estimate CSVs contain bootstrap intervals for all four Layer 1 contrasts and all 95 crude and adjusted Layer 2 contrasts. Wald p-values use patient-clustered influence-score standard errors.

All 117 logistic nuisance fits recorded in `PHASE5_CONVERGENCE_AUDIT.csv` converged without a warning or iteration-limit hit; the maximum was 40 of 500 iterations. The bootstrap score calculation has no iterative fit or convergence step. Nuisance calibration and overlap diagnostics are in `PHASE5_NUISANCE_DIAGNOSTICS.csv`.
