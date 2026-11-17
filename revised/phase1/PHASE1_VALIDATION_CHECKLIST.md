# Phase 1 Validation Checklist

Use this before approving Phase 2. Status now is **documented** unless marked otherwise; a protocol description is not evidence that the item has passed.

## Cohort and coding

- [ ] Apply identical eligibility and index-date algorithm to cases and controls.
- [ ] Cases indexed at earliest eligible nonacute admission before first acute-MI-coded admission.
- [ ] Controls indexed at earliest eligible admission without looking forward to require never-MI status.
- [ ] Exclude documented acute MI (`410*`, `I21*`, `I22*`) and historical MI (`412`, `I25.2`) on/before index.
- [ ] Verify first acute MI occurs strictly after index; later events do not create repeat primary outcomes.
- [ ] Confirm event is admission-based proxy and report no-code status as undocumented, not known never-MI.
- [ ] Reconcile aggregate cohort flow to authoritative counts; do not substitute 5,008/4,797 event-anchored counts.
- [ ] Resolve prior-MI covariate/exclusion conflict (currently omitted from primary adjustment).

## Exposure

- [ ] Verify OMR SBP/DBP parsing from `SBP/DBP`, units, duplicate handling, and QC bounds.
- [ ] Verify `chartdate < index_date`; same-day records excluded.
- [ ] Apply `[index_date - 730 days, index_date)` as primary candidate and prespecify 1-/3-year alternatives.
- [ ] Compute count, arithmetic mean, median, variability, frequency, and missingness without publishing row-level values.
- [ ] Team approves minimum measurement count and documents resulting population/selection impact.
- [ ] Approve covariate temporal cutoff; verify diagnosis/BMI/medication covariates precede the exposure window, not merely index.
- [ ] Check influence of frequent measurements and exposure reliability.
- [ ] Keep aggregate feasibility counts distinct from final denominator.

## Intervention, support, and DAG

- [ ] Confirm reference `d0(A)=A` and candidate `d1(A)=A-10` when `A>=130`, else `A`.
- [ ] Confirm intervention described as one-time measured baseline modified policy, not sustained regimen/prescription.
- [ ] Evaluate conditional SBP density, overlap, shifted-value support, unsupported fraction, tails, and profile-level violations.
- [ ] Do not declare positivity from marginal bins or global min–max.
- [ ] Obtain approval for any restriction/trimming or alternative stochastic intervention.
- [ ] Review hypertension timing, BMI, medication roles and alternative DAGs; do not adjust all nodes automatically.
- [ ] Retain smoking/lipids as unavailable confounding; do not fabricate values.

## Outcome, horizon, death, censoring

- [ ] Research team approves horizon after aggregate coverage review (365 days is only a candidate).
- [ ] Confirm first acute MI outcome coding and date linkage.
- [ ] Reconcile death fields at consistent patient/admission unit; do not mix 27,980, 8,592, and 8,598 as one universe.
- [ ] Decide whether death data support competing-risk cumulative incidence; quantify underascertainment sensitivity.
- [ ] Define end of source observation and administrative censoring; do not interpret missing death as survival.
- [ ] Assess informative loss to observation and censoring positivity.

## Estimation and heterogeneity (future phase only)

- [ ] Statistical review approves target-specific g-computation and any AIPW/IPW formulation for the deterministic policy and competing events.
- [ ] Prespecify patient-level folds/cross-fitting; no patient appears in multiple folds.
- [ ] Prespecify patient-level bootstrap or justified cluster uncertainty method.
- [ ] Report policy risks, RD, secondary RR, and uncertainty intervals.
- [ ] Set precision target (interval width or minimum detectable interaction) before subgroup estimation.
- [ ] Prespecify age (<65/≥65), sex, diabetes, omnibus/direct interaction tests and multiplicity control.
- [ ] Evaluate calibration, functional form, balance, overlap, weights, effective sample size, missingness, unmeasured confounding, and selection weighting assumptions.
- [ ] Identify external clinical benchmark with population/intervention caveats.

## Separate modules / governance

- [ ] Keep BP-to-ECG population and denominator separate; define index ECG, gap, eligibility, DAG, completeness and multiplicity later.
- [ ] Do not create individual scenario estimator before valid population analysis; enforce uncertainty/support flags and research-only language.
- [ ] Confirm no patient-level data in revised output and no original Phase 1–9 artifacts modified.
- [ ] No β-VAE pipeline search, audit, training or checkpoint validation.

## Current Phase 1 validation result

Document-to-document consistency was reviewed for time zero, target population, BP window and QC, intervention, MI coding, prior-MI exclusion, horizon, estimand, covariates, competing death, and Phase 1 boundaries. Agreement is recorded in `PHASE1_COMPLETION_REPORT.md`. Empirical checks listed above remain future requirements; no model or effect test was performed.
