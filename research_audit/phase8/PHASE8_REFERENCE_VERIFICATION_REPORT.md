# Phase 8 Reference Verification Report

**Scope:** 17 numbered sources in the literature review, citations in the manuscript, and corresponding BibTeX records. Metadata was compared with publisher pages, PubMed, or the source repository record. Citation relevance was assessed against the nearby manuscript statement. This was a focused check of the existing bibliography, not a systematic literature search.

## Summary

- **17 references checked; 17 verified as identifiable records with matching DOI and core bibliographic metadata.**
- **11 BibTeX entries corrected** for inaccurate/incomplete author, title, journal, issue, page/article-number, or item-type metadata: references 2–7, 9–10, and 15–17.
- **0 unresolved records.** Reference 7 is a PhysioNet dataset record, not a journal article; its BibTeX type and citation format now reflect that.
- The citation numbering 1–17 is consistent between the manuscript's numeric citations and the literature review. The bibliography records source 7 as PhysioNet v1.0; it is not described as a Scientific Data journal article.

## Reference-by-reference status

| No. | Verification result | Citation relevance to manuscript |
|---:|---|---|
| 1 | Verified. Title, seven named authors, *European Heart Journal* 2019;40(3):237–269, DOI 10.1093/eurheartj/ehy462. | Supports the statement that MI diagnosis integrates clinical/ECG evidence. |
| 2 | Corrected and verified against JACC publisher record. Expanded the official title and corrected the author list to the JACC record; *JACC* 2009;53(11):1003–1011, DOI 10.1016/j.jacc.2008.12.016. | Supports clinical context for ischemic/infarction ECG interpretation. The paper is not evidence for this study's association estimand. |
| 3 | Corrected and verified. Exact title is “A deep learning algorithm for detecting acute myocardial infarction”; complete author list and *EuroIntervention* 2021;17(9):765–773 added. | Supports the example of ECG-based diagnostic prediction/classification. |
| 4 | Corrected and verified. Exact title, full six-author list, journal (*Canadian Journal of Emergency Medicine*), volume/issue/pages 25(10):818–827 added. | Supports the review of ML for ACS diagnosis from a 12-lead ECG. |
| 5 | Corrected and verified. Fawzy et al. are the authors; exact title, *Journal of the American College of Emergency Physicians Open* 2025;6(5):100240 added. | Supports the systematic review of AI ECG diagnostic models. |
| 6 | Corrected and verified. Full 13-author list for MIMIC-IV added; *Scientific Data* 2023;10:1, DOI 10.1038/s41597-022-01899-x. | Supports the MIMIC-IV resource description. |
| 7 | Corrected and verified against the PhysioNet v1.0 record, including 16 contributors and DOI 10.13026/4nqg-sb35. Reclassified from journal article to dataset record. | Supports the MIMIC-IV-ECG resource description; it does not validate the analytic cohort or effect estimates. |
| 8 | Verified. Full author list and *International Journal of Epidemiology* 2021;50(2):620–632, DOI 10.1093/ije/dyaa213. | Supports DAG/adjustment reporting context. |
| 9 | Corrected and verified. Author order is Feeney, Hartwig, Davies; *BMJ* 2025;388:e078226, DOI 10.1136/bmj-2023-078226. | Supports DAG use and the need to present assumptions explicitly. |
| 10 | Corrected and verified against JAMA publisher record; complete named author list plus GUSTO-I investigator group, *JAMA* 1998;279(5):387–391, DOI 10.1001/jama.279.5.387. | Supports prior ECG morphology/prognostic literature. |
| 11 | Verified. *American Journal of Cardiology* 2007;100(7):1056–1060, DOI 10.1016/j.amjcard.2007.04.054; six named authors/order match the index record. | Supports prior work on presenting ECG patterns and outcomes in MI. |
| 12 | Verified. Full title and four authors, *American Journal of Cardiology* 2026;269:131–136, DOI 10.1016/j.amjcard.2026.03.064. | Supports the close MIMIC/structured-feature subtype-analysis comparison; not the same target estimand. |
| 13 | Verified. Ten authors, *NEJM AI* 2025;2(12), DOI 10.1056/aioa2500164. | Supports a foundation-model ECG prediction example; it is not evidence for the observational association target. |
| 14 | Verified. Hernán, Wang, Leaf; *JAMA* 2022;328(24):2446–2447, DOI 10.1001/jama.2022.21383. | Supports target-trial/causal-question framing; it does not imply this analysis is causally identified. |
| 15 | Corrected and verified. Exact title is “Generating a robust statistical causal structure over 13 cardiovascular disease risk factors using genomics data”; four authors and *Journal of Biomedical Informatics* 2016;60:114–119 added. | Supports existence of related causal-network research, not causal validity or novelty of this study. |
| 16 | Corrected and verified. Six authors and *iScience* 2026;29(5):115742 added; DOI 10.1016/j.isci.2026.115742. | Supports existence of related EHR-based AMI causal-network research, not causal validity or novelty of this study. |
| 17 | Corrected and verified. Expanded official STROBE title; *The Lancet* 2007;370(9596):1453–1457, DOI 10.1016/S0140-6736(07)61602-X. | Supports observational reporting guidance only; STROBE does not establish causal validity. |

## Sources checked

Primary/publisher or reliable index records used include [JACC for reference 2](https://www.jacc.org/doi/10.1016/j.jacc.2008.12.016), [PubMed for the Fourth Universal Definition](https://pubmed.ncbi.nlm.nih.gov/30165617/), [PubMed for references 3–5](https://pubmed.ncbi.nlm.nih.gov/33840640/), [PubMed for the DAG guide](https://pubmed.ncbi.nlm.nih.gov/40118502/), [JAMA for reference 10](https://jamanetwork.com/journals/jama/fullarticle/187197), [PubMed for reference 12](https://pubmed.ncbi.nlm.nih.gov/41935766/), [PubMed for reference 13](https://pubmed.ncbi.nlm.nih.gov/41446031/), [PubMed for reference 15](https://pubmed.ncbi.nlm.nih.gov/26827624/), [PubMed for reference 16](https://pubmed.ncbi.nlm.nih.gov/42100736/), [PhysioNet for reference 7](https://physionet.org/content/mimic-iv-ecg/1.0/), and [PubMed for STROBE](https://pubmed.ncbi.nlm.nih.gov/18064739/).

Before submission, format all records to the target journal style and refresh any literature search used for novelty positioning. The evidence supports a cautious, non-priority positioning only.
