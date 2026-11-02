# Secondary retrospective governance scenario

2November2026. Exploratory. Protocol `research/secondary_protocol.md` was committed
at e53ec707da851dcc657e70602200d0ffdc57afe7 before fitting these models.
It was written after primary area-history results and feature-coverage inspection,
so it is not preregistration or a newly untouched holdout.

The scenario uses the20already-selected governance/scale features, with exactly
one source record and both dates null optionally assigned across the polity
lifetime. Source flags, inferred/unknown codes and partial dates are not relaxed.
These are **retrospective assumptions**, not verified past-only measurements.

## All fixed-model results

Macro-F1, fixed operational three-class area-change labels:

|Model/input|Grouped fold mean,15folds|Time-plus-group holdout|
|---|---:|---:|
|Majority, original|0.279|0.285|
|Area-only logistic, original|0.290|0.226|
|Area-only forest, original|0.327|0.287|
|Governance-scenario logistic|0.290|0.247|
|Governance-scenario forest|0.313|0.317|
|Area+governance-scenario logistic|0.301|0.290|
|Area+governance-scenario forest|0.375|0.312|

All use identical primary split memberships, not resampled to make a comparison
favorable. Grouped predictions contain every756rows once per seed/model. The
historical holdout contains94rows per model, with shared groups removed from train.
This remains a small, selected sample with correlated histories and only30groups
containing decline. No calibration or modern-transfer claim is made.

For combined forest versus area-only forest, pooled seed0 OOF macro-F1 difference
is0.063, with a conditional paired group-bootstrap95%descriptive interval
[0.019,0.108]. The other three model/input comparisons with their corresponding
area-only model have intervals including zero. All four intervals are reported
in `scenario_bootstrap.csv`, not selected for significance. They are not corrected
for multiple comparisons, do not propagate historical boundary/time error, and do
not make the already-inspected holdout independent.

The combined forest's time-plus-group macro-F1 increases from0.287to0.312, a small
absolute difference. Its decline AP falls from0.411to0.173; governance-only forest
has decline AP0.131. Gains in one aggregate metric are not universal improvement,
reliable decline detection, proof that governance causes stability, or evidence
these features were available before outcomes. The intended empirical contribution
must survive the measurement-support and label-sensitivity concerns.

## Three source-narrative spot checks, chosen before fitting

The live professional-soldier API records for the three prespecified polities
all retain null year_from/year_to, tagTRS and no uncertainty/dispute flags. Their
polity pages display full lifetimes via the documented gray-date fallback.

|Polity|Source description inspected|What remains unresolved|
|---|---|---|
|Durrani|Roughly one in three military members were full-time professional fighters; cites Barfield, Afghanistan: A Cultural and Political History,pp98-99|Description does not explicitly date whole-lifetime prevalence; cited book pages not independently inspected|
|Kushan|Some evidence of guild soldiers protecting guild property in peace and provided to the state in war; cites UNESCO Silk Road chapter,p304|Whether this supports full-time professionals throughout35-319CE is not independently adjudicated; original chapter not inspected|
|Eastern Han|Description begins "Western Han" and cites conscript training plus the Northern Army stationed at the capital, referencing Peers1995,p13and Bielenstein1986,p512|Possible temporal scope mismatch with an Eastern Han record. This is a review flag, not a confirmed coding error; original works not inspected|

The third case illustrates why copying polity dates is not equivalent to source
adjudication. Do not silently fix the source or extend a potentially earlier-period
statement into a later polity. No source values or historical labels were changed
from these checks. Three convenience-selected records do not estimate overall
error, and these are not independent historian judgments.

## Interpretation and next decision

There is a **conditional exploratory signal** under the retrospective polity-wide
scenario. That is worth investigating, not announcing as successful forecasting.
The stronger claim remains unsupported until source time bounds and historical
labels are reviewed. Keep strict coverage, area-only negative/weak results and
all scenario results together. Additional model tuning on these outcomes would
not solve the principal measurement problem.

The immediate scientific next step is a reviewable time-support sample stratified
by source provenance, feature and period, with adjudication before a new confirmatory
evaluation. An independent historian should settle the Eastern Han scope flag and
other ambiguous records. This work has not contacted source authors, submitted a
paper, paid for sources, or requested another person's time on the user's behalf.

## Reproduction

Run primary construction/evaluation, then feature-support audit, then:

```sh
python research/evaluate_governance_scenario.py
```

No new hyperparameters, row filters or class thresholds are selected. Full per-row
predictions and membership logs regenerate locally; small summary/interval outputs
are committed. Model preprocessing is fit only on the training partition.

Source evidence inspected2November2026:
- https://seshat-db.com/api/sc/professional-soldiers/?page_size=1000 (first100records include all three cases; the504count is not the number retrieved in one page)
- https://seshat-db.com/core/polity/af_durrani_emp/
- https://www.seshat-db.com/core/polity/127
- https://www.seshat-db.com/core/polity/253
- Pinned official display-template source and source-methods report linked in `feature_time_support.md`.

Source descriptions and cited-book references above are what the source API states,
not a claim that the original cited works were independently read or verified.
