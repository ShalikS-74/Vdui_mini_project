# Expanded study protocol, fixed before expanded model evaluation

2026-11-02. This protocol is exploratory, written after seeing the old Equinox
baseline and expanded label counts, but before fitting any Polaris/Clio model.
It is not retrospective preregistration or independent confirmatory evidence.

## Question and limits

Can historical area dynamics improve prediction of the next 50-year area-change
class for source-ID-linked, continuing historical polities? This is narrower than
predicting state collapse and does not establish governance causes or modern risk.
Separately, quantify whether strictly dated governance measures even have enough
coverage for the proposal's intended model. Do not substitute undated codes,
range midpoints, inferred presence or future values without an explicit sensitivity
policy. No modern-country scores. Missing future geometry is censored, not decline.

## Frozen construction

- Pinned official Polaris2026 and Cliopatria0.2.1 revisions and hashes.
- Only direct SeshatID links; exactly one positive POLITY area at t and t+50.
  No sum of ambiguous components, fuzzy names or interpolated areas.
- 50-year grid, registry lifespan bounds, current year<=1900 and target<=1900.
- Decline ratio<=0.7, rise>=1.3, otherwise stable. No threshold search.
- Feature experiment: log10 current area, log10 prior area(t-50), past50 log-area
  difference, historical age at t. Prior geometry must satisfy the same unique
  record rule. Raw area at t+50 and outcome are prohibited model inputs.
- Governance-feature coverage reported separately. It must not be represented as
  a successful governance model just because an area-history model works.
- Conservative connected groups use exact predecessor/successor registry names
  and shared Cliopatria Names. These are splitting safeguards, not verified
  successor-area labels. Export all source edges and unresolved links.

## Evaluation

- Primary exploratory metric macro-F1 for three classes; class AP and prevalence
  also reported. No accuracy-led claims.
- Identical five grouped folds, seeds0,1,2, with all preprocessing fitted on train.
- Stable-majority baseline, balanced logistic(C=1,max_iter3000), shallow forest
  (150trees,max_depth3,min_samples_leaf4,class_weight balanced). No tuning.
- Compare governance-strict coverage, but do not fit a high-dimensional model on
  largely empty feature rows simply to obtain a result.
- Temporal holdout cut1500: train labels end<1500, test current>=1500 and
  target<=1900; additionally remove all test groups from training. If any training
  class disappears, report insufficient data rather than relax the split.
- Paired group-bootstrap metric differences using seed0 OOF,1000replicates,
  seed20261102. Descriptive intervals conditional on this sample, not proof of
  novelty or full sampling uncertainty. Show unique decline groups and class
  counts. Missing-class resamples use fixed three-class macro-F1.
- Do not select model/feature threshold based on final holdout results. Later
  revisions require a new exploratory version and new independent validation.

## Required before a research-grade claim

Source/label reviews, release-to-release sensitivity, exclusion/selection audit,
reviewed lineage and termination policy, two-reviewer historical FP annotation,
robustness to boundary/area uncertainty, prior-work comparison and PowerBI render
verification. An apparently positive exploratory score cannot waive these gates.
