# Toward a useful, defensible research contribution

**Aim, not a claim:** an audited account of when a historical area-contraction
classifier is confidently wrong, separating measured non-contractions from
identity/coverage artifacts. Novelty is not established without a literature
review. A dashboard alone does not make the result publishable.

## Evidence gates

1. **Sampling and labels first.** Compare all source rows, rows with territory,
   exact future matches, and exclusions at polity transitions. Audit Terr coding.
   Resolve 50-year feasibility using an appropriately resolved area source, not
   interpolation. Record label definition and protocol before looking at results.
2. **Continuity.** Build a sourced, versioned predecessor/successor mapping; let
   a domain reviewer verify it. Do not equate a geographic NGA to a lineage or
   automatically use fuzzy polity names as truth. Repeat held-out evaluation with
   genuine continuity groups before claiming leakage-safe research results.
3. **Adequate outcomes.** Six positives fail the original <30-positive gate.
   Expand source coverage or adopt a separately justified crisis-onset target.
   Do not optimize thresholds on this test sample or change the target just to
   get attractive results. Treat target changes as a new registered experiment.
4. **FP case evidence.** Review each queue entry against a time-specific source,
   area coding and continuity record. Record source URL, note and unresolved
   ambiguity in data/manual_reviews.csv. Non-contraction alone is not survival.
   Two reviewers and a disagreement log would improve reliability. No inferred
   historical verdicts or causal claims from SHAP.
5. **Predictive value.** Compare majority, logistic and shallow forest on the same
   held-out folds. Report macro-F1 and AP, prevalence and valid fold counts.
   Current macro-F1 does not beat majority. With more independent groups, use
   group-aware uncertainty estimates and a truly untouched temporal evaluation.
6. **Presentation.** Verify Power BI Desktop before claiming delivery. Keep all
   scores uncalibrated, explanations associational, and limitations visible.
7. **Literature and write-up.** Establish related work on historical state
   contraction, survival bias and model-error audits before saying 'novel'. If
   data gates pass, write a methods/results/limitations study. A negative result
   can be informative, but its publishability is for reviewers to judge.

Domain shift and modern retrospective come only after a documented construct-
valid bridge exists. No current-governing-country scoring is part of this work.
