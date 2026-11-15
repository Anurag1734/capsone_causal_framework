# Abstract

## Background

Acute myocardial infarction (MI) is associated with electrocardiographic abnormalities, but admission-level ECG morphology analyses in electronic health records face confounding, selection, coding, and event-timing limitations. We examined recorded risk-factor histories and ECG feature differences within a prespecified two-layer observational framework using MIMIC-IV and MIMIC-IV-ECG.

## Methods

The adult-admission denominator comprised 431,231 admissions. An eligible in-episode ECG was available for 191,275 admissions (44.36%), representing 99,214 patients. The primary ECG comparison included 7,353 admissions with an acute MI code and 159,713 clean comparison admissions; 24,209 admissions with prior MI history only were kept separate. Layer 1 estimated adjusted admission-level risk differences between recorded histories of diabetes, hypertension, chronic kidney disease (CKD), or prior MI and acute MI coding. Layer 2 estimated adjusted mean differences in 95 handcrafted ECG features between acute-code admissions and clean controls. Five-fold patient-group cross-fitted augmented inverse probability weighting (AIPW) was used, with patient-cluster bootstrap intervals and false discovery rate (FDR) control for the 95 feature family. Sensitivity analyses assessed unmeasured confounding, ECG selection, broader same-admission MI coding, and age and sex effect modification.

## Results

Layer 1 adjusted risk differences were +0.69 percentage points for diabetes (95% CI 0.42 to 0.95), −0.51 points for hypertension (−0.70 to −0.30), and −0.17 points for CKD (−0.59 to 0.31); prior MI history was associated with +5.48 points and interpreted descriptively. In Layer 2 (167,066 admissions, 93,946 patients), 67/95 features passed BH FDR 5% (66 physiological features and one technical/support feature). The largest standardized adjusted contrasts included ST_Elev_I (−0.346 SD), T_Amp_I (−0.336 SD), T_Amp_aVR (+0.327 SD), and ST_Elev_aVF (−0.302 SD). Mean absolute ST and T contrasts were 0.162 and 0.129 SD. Selection weighting preserved 89/95 directions; the median absolute shift was 0.009 SD, and 66/67 primary discoveries also passed weighted FDR. A broader current-admission code definition preserved 85/95 directions but attenuated mean absolute ST/T contrasts to 0.126/0.108 SD. Direct interaction tests identified 11 age and 13 sex contrasts after BH correction. Approximate Layer 1 E-values were modest for diabetes (1.66; nearest-null CI 1.48) and hypertension (1.57; 1.39); CKD's interval included the null.

## Conclusions

Among ECG-selected adult inpatient admissions, recorded acute MI coding was associated with a structured, lead-dependent pattern of ST/T and other ECG feature differences after adjustment. The central ST/T pattern was reasonably stable to measured-covariate selection weighting and remained visible under broader coding, with attenuation. These findings are observational associations. MI onset relative to the selected ECG is unknown, so temporal ordering and causal effects are not established. The results do not define a universal MI ECG signature or establish literature-based novelty.
