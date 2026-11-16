# Focused Literature Review

**Scope.** This is a focused, narrative comparison to support manuscript positioning, not a registered or exhaustive systematic review. Search and screening should be updated and documented before journal submission. The review distinguishes ECG prediction/classification, MI ECG morphology/outcome characterization, EHR causal modeling, and the current project's admission-level adjusted association target.

## Evidence map and relevance

| Literature area | Representative evidence | Relationship to this study |
|---|---|---|
| Data resources | MIMIC-IV describes the critical-care EHR resource [6]. MIMIC-IV-ECG describes roughly 800,000 linked 12-lead recordings and the waveform resource [7]. | Establishes data context, not the validity of this cohort's diagnosis-feature estimand. |
| Clinical interpretation | The Fourth Universal Definition integrates ECG with clinical and biomarker criteria [1]. AHA/ACCF/HRS ECG standardization reviews acute ischemia/infarction patterns [2]. | ST/T morphology is clinically relevant but context- and lead-dependent; ECG changes alone do not establish MI onset or every diagnosis. |
| ECG classification/prediction | Liu et al. evaluated a deep learning AMI detection algorithm [3]. Zworth et al. reviewed ML for ACS diagnosis from ECG [4]; Fawzy et al. reviewed AI-based 12-lead ECG models for ACS diagnosis [5]. | These studies address predictive/classification performance. They do not answer the same adjusted continuous-feature association question. |
| ECG morphology and prognosis | Hathaway et al. studied the prognostic significance of the initial ECG in AMI [10]. Kuch et al. described presenting ECG morphology classes and outcomes in MI [11]. | Prior work already links ECG patterns to clinical context/outcomes, limiting any broad claim that MI ECG morphology has not been studied. |
| Close MIMIC-IV neighbor | Simeon et al. (2026) used structured ECG features among 2,159 ICU patients to distinguish type 1 from type 2 MI [12]. | A close resource and feature-based near-neighbor. Different sample and subtype target; it weakens broad novelty claims and warrants direct comparison in final submission. |
| ECG foundation models | Goonewardena et al. trained a self-supervised ECG foundation model with MIMIC-IV-ECG signals for diagnostic and perfusion prediction tasks [13]. | Shares the data source but uses waveform representations and predictive targets, not this project's prespecified handcrafted-feature association estimands. |
| Causal DAG methods | DAG reporting and adjustment guidance emphasizes explicit assumptions and careful adjustment [8,9]. Hernán et al. discuss target-trial emulation for causal questions [14]. | Supports transparent estimand and assumption reporting. The present same-admission timing does not meet the information needed to establish event-before-ECG ordering. |
| MI causal/diagnostic networks | Yazdani et al. modeled cardiovascular risk-factor causal networks [15]. A 2026 iScience study modeled an EHR causal network for emergency-department AMI diagnosis [16]. | Shows related causal-network research exists; neither alone establishes that this study's observational contrast is identified or novel. |

## Synthesis and manuscript implications

ECG-based MI/ACS prediction is an active literature, and prior work has evaluated MI ECG morphology and prognosis. Recent work also shares MIMIC-IV-ECG or structured ECG features, including a close 2026 comparison of type 1 versus type 2 MI [12]. The present project differs in its two-layer design, admission-level coded contrasts, 95 handcrafted continuous features, and explicit sensitivity analyses. Those distinctions are not sufficient to establish priority or novelty. The manuscript should state that it provides a focused empirical characterization and avoid “first,” “novel,” or “unprecedented” unless a submission-ready search finds and compares all close prior work.

Classification studies should not be used as validation of the association estimates, and causal DAG literature should not be used to imply identification. The manuscript should present the DAG as an assumption map, report that the ECG and MI diagnosis are contemporaneous at the admission level, and retain the unknown onset-to-ECG interval as a principal limitation.

## References

1. Thygesen K, Alpert JS, Jaffe AS, et al. Fourth Universal Definition of Myocardial Infarction (2018). *European Heart Journal*. 2019;40(3):237–269. doi:10.1093/eurheartj/ehy462.
2. Wagner GS, Macfarlane P, Wellens H, et al. AHA/ACCF/HRS recommendations for the standardization and interpretation of the electrocardiogram: Part VI: acute ischemia/infarction: a scientific statement from the American Heart Association Electrocardiography and Arrhythmias Committee, Council on Clinical Cardiology; the American College of Cardiology Foundation; and the Heart Rhythm Society: endorsed by the International Society for Computerized Electrocardiology. *Journal of the American College of Cardiology*. 2009;53(11):1003–1011. doi:10.1016/j.jacc.2008.12.016.
3. Liu WC, Lin CS, Tsai CS, et al. A deep learning algorithm for detecting acute myocardial infarction. *EuroIntervention*. 2021;17(9):765–773. doi:10.4244/EIJ-D-20-01155.
4. Zworth M, Kareemi H, Boroumand S, et al. Machine learning for the diagnosis of acute coronary syndrome using a 12-lead ECG: a systematic review. *Canadian Journal of Emergency Medicine*. 2023;25(10):818–827. doi:10.1007/s43678-023-00572-5.
5. Fawzy A, Malik A, Diaz-Martinez JP, Orchanian-Cheff A, Masood S. The accuracy of artificial intelligence-based models applied to 12-lead electrocardiograms for the diagnosis of acute coronary syndrome: a systematic review. *Journal of the American College of Emergency Physicians Open*. 2025;6(5):100240. doi:10.1016/j.acepjo.2025.100240.
6. Johnson A, Bulgarelli L, Pollard T, et al. MIMIC-IV, a freely accessible electronic health record dataset. *Scientific Data*. 2023;10:1. doi:10.1038/s41597-022-01899-x.
7. Gow B, Pollard T, Nathanson LA, et al. *MIMIC-IV-ECG: Diagnostic Electrocardiogram Matched Subset*. PhysioNet, version 1.0; 2023. doi:10.13026/4nqg-sb35.
8. Tennant PWG, Murray EJ, Arnold KF, et al. Use of directed acyclic graphs (DAGs) to identify confounders in applied health research: review and recommendations. *International Journal of Epidemiology*. 2021;50(2):620–632. doi:10.1093/ije/dyaa213.
9. Feeney T, Hartwig FP, Davies NM. How to use directed acyclic graphs: guide for clinical researchers. *BMJ*. 2025;388:e078226. doi:10.1136/bmj-2023-078226.
10. Hathaway WR, Peterson ED, Wagner GS, et al. Prognostic significance of the initial electrocardiogram in patients with acute myocardial infarction. *JAMA*. 1998;279(5):387–391. doi:10.1001/jama.279.5.387.
11. Kuch B, von Scheidt W, Kling B, Heier M, Hoermann A, Meisinger C. Characteristics and outcome of patients with acute myocardial infarction according to presenting electrocardiogram (from the MONICA/KORA Augsburg Myocardial Infarction Registry). *American Journal of Cardiology*. 2007;100(7):1056–1060. doi:10.1016/j.amjcard.2007.04.054.
12. Simeon MJ, Lee SK, Yee BF, Seto AH. Associations between electrocardiographic features and type 1 and type 2 myocardial infarction in critically ill patients. *American Journal of Cardiology*. 2026;269:131–136. doi:10.1016/j.amjcard.2026.03.064.
13. Goonewardena et al. Self-supervised foundation model for electrocardiography using MIMIC-IV-ECG. *NEJM AI*. 2025. doi:10.1056/aioa2500164.
14. Hernán MA, Wang W, Leaf DE. Target trial emulation: a framework for causal inference from observational data. *JAMA*. 2022;328(24):2446–2447. doi:10.1001/jama.2022.21383.
15. Yazdani A, Yazdani A, Samiei A, Boerwinkle E. Generating a robust statistical causal structure over 13 cardiovascular disease risk factors using genomics data. *Journal of Biomedical Informatics*. 2016;60:114–119. doi:10.1016/j.jbi.2016.01.012.
16. Li BY, Li XQ, Jiang YT, Li XY, Tian ZX, Kang R. Electronic medical record-based causal network modeling for acute myocardial infarction diagnosis in the emergency department. *iScience*. 2026;29(5):115742. doi:10.1016/j.isci.2026.115742.
17. von Elm E, Altman DG, Egger M, et al. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *The Lancet*. 2007;370(9596):1453–1457. doi:10.1016/S0140-6736(07)61602-X.

**Reference verification note:** Confirm author order and complete metadata for references 3–5, 9, 12, 15, and 16 against publisher/index records during submission preparation. This focused review is not a systematic search.
