# Completion status

## Verified engineering

Rebuild from official pinned raw source; fold-local preprocessing; past-only
features; conservative PolID grouping; repeated and temporal evaluations; majority
and forest baselines; actual held-out linear SHAP; fixed-threshold OOF audit;
Streamlit smoke tests and UI; reproducible metadata; Power BI PBIR JSON schema
validation. See tests and generated metrics, not the old audit counts.

## Still blocking full proposal / publication readiness

1. Exact 50-year labels remain unavailable from the legacy Equinox input. The
   separate pinned Polaris/Clio extension now supplies 756 area-change candidates
   with three classes, but continuing-ID selection and sparse strictly dated
   governance features limit that study. See docs/research_findings.md.
2. True lineage continuity: no verified predecessor/successor table. An unchanged
   polity-ID-only join misses transitions and can bias labels toward continuations.
3. All 14 confident false-positive cases require source-based manual review.
   No causal protective factor or genuine-survival claim is warranted.
4. Legacy Equinox has six contractions and majority wins its grouped macro-F1.
   The expanded area-history model has 59 decline rows in 30 groups, bootstrap
   improvement intervals containing zero, and almost no gain in time-plus-group
   holdout. A useful governance/collapse prediction claim remains unsupported.
5. Power BI project candidate needs Desktop open, DataRoot update, refresh,
   relationship/visual inspection and save to PBIX. No Desktop renderer is
   available in this execution environment; this step is not done.
6. Modern bridge, domain shift and USSR retrospective have not been implemented.
   No modern transfer or calibrated risk claim is made.
7. Literature review is needed before claiming novelty or selecting a venue.

No fabricated label interpolation, lineage links, historical reviews, literature
citations, Power BI success or publication outcomes are used to hide these gaps.

Expanded construction/evaluation is reproducible with pinned hashes, protocol,
split membership, missingness/exclusion logs and 18 tests. The app separates its
research summary tab from legacy predictions and SHAP explanations.

Source adjudication now includes consecutive-release checks, explicit component
relationships, terminal-window exclusions, CrisisDB coverage and hypothetical
label sensitivity. See label_adjudication.md and related_work.md. These checks
are not independent human review, and no models were tuned during them.

Official site source confirms a polity-lifetime display fallback for undated
features. A provenance-marked coverage sensitivity is now separate from strict
inputs; no new model fit. See feature_time_support.md.

The separately frozen retrospective governance scenario now reports all fixed
models on the original splits, without tuning. There is a conditional combined-
forest signal, but unclear historical timing and weaker holdout decline AP prevent
a forecasting claim. Source-narrative spot checks are not independent adjudication.
See secondary_results.md; prior strict and area-only results remain intact.

A fixed 120-record, outcome-blinded time-support review package is now prepared in
research/review with reproducible stratified sampling and blank adjudication
fields. No reviewer has been contacted. It needs two independent judgments,
source citations/pages and disagreement handling before it becomes review evidence.
No further model fitting is planned without those measurement/source inputs.

## 2026-11-17 documentation/dashboard/paper pass

- Documentation cleanup: restored missing whitespace across all docs (numbers
  and units had lost separating spaces), removed escape artifacts from the
  problem statement, and rewrote the raw planning chat log
  (`docs/implementation.txt`) as a clean `docs/implementation_plan.md`. Its
  false-positive explainer section is marked superseded: it described the old
  5-case percentile selection and full-data coefficient contributions, replaced
  by the fixed >=0.70 OOF queue and true fold-specific SHAP. No quantitative
  claim was changed; every number was re-verified against the committed CSVs.
- Streamlit dashboard: added a reading guide (polity/OOF/SHAP/uncalibrated
  glossary), the majority-baseline macro-F1 as a headline metric, an observed
  territory trend next to the score trend, sorted SHAP bars, flattened metric
  tables and an explicit audit-threshold reference. All 18 tests pass.
- Power BI: added visual titles, the planned score-by-year scatter on the audit
  page (using a new `Mean model score` measure), richer captions and tab order.
  Committed files keep Desktop-added lineageTags and annotations; the generator
  does not emit them (see powerbi/README.md). Still not rendered in Desktop.
- `paper/` now holds an IEEE-style draft built only from verified numbers.
