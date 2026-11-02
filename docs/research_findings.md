# Research extension: what the evidence supports

2 November 2026. Exploratory, not confirmatory or submission-ready.

The new official Polaris and Cliopatria sources make the original exact50-year,
three-class area-change target technically feasible for a selected historical
sample. They do not yet yield a defensible governance or collapse-risk model.
The honest result is a reproducible feasibility study with weak exploratory
predictive performance, plus a concrete coverage and selection-bias audit.

## Evidence now implemented

| Item | Result | Interpretation |
|---|---:|---|
| Polaris registry |626polities|Source registry, not training rows|
| Direct SeshatID matches |342polities|Before unique-area and endpoint exclusions|
| Exact50-year candidate rows |756|605stable,92rise,59decline|
| Conservative linked groups |113|Only30groups have a decline row|
| Any strictly dated governance/scale feature |144rows|Most candidate rows have no usable governance measurement|
| Grouped forest macro-F1 |0.327|Majority0.279; across15folds,3seeds|
| Grouped logistic macro-F1 |0.290|No tuned hyperparameters|
| Time-plus-group holdout forest |0.287|Majority0.285; essentially no improvement|
| Time-plus-group holdout logistic |0.226|Worse than majority|

The forest uses only current area, past area, past area change and historical age.
It does not demonstrate governance effects. Its seed0 pooled OOF macro-F1 difference
from majority is0.030; the paired group-bootstrap95% descriptive interval is
[-0.014,0.084]. Logistic's interval is[-0.021,0.094]. Both include zero.
Fold-average differences and pooled seed0 bootstrap differences are different
estimands and are not interchangeable. These intervals are conditional exploratory
summaries, not a complete uncertainty estimate or proof of no effect.

## Why strict governance coverage stays low

The official builder preserves source year bounds, uncertain/disputed flags and
coded values. The codebook distinguishes temporal ranges from uncertainty in
values, direct presence from inferred presence, and unknown from absent. We accept
one dated, undisputed, non-uncertain record covering the observation time, with a
single numeric value or direct P/A code. We do not take a range midpoint, convert
unknown into absent, or silently stretch undated codes across a polity lifetime.
The current codebook inspection did not settle how every undated workbook record
should apply in time. Relaxing that rule is an unresolved source interpretation,
not a model-tuning choice. Population has38strict rows, capital population61,
administrative level10, military level7and professional soldiers13.

## Scope and biases that remain

- Labels are area contraction/growth, not historically verified collapse, survival,
  institutional success or civilian welfare. Thresholds0.7and1.3are operational
  study choices, not validated historical event definitions.
- Direct ID identity avoids speculative name crosswalks but does not settle all
  overlapping geometries. Multiple active geometries are rejected, never summed.
- Requiring a future area under the same ID selects continuing mapped polities.
  Polity termination and identity transitions are censored. This selection can
  exclude exactly the collapse events the original proposal wants to study.
- Geometry timestamps represent source reconstructions. A50-year lookup does not
  create50-year measurement accuracy, independent observations, or dated evidence
  about the true timing of change. Boundary error is not propagated yet.
- Exact predecessor/successor-name and shared-map-name components are safeguards
  for splits, not validated continuity labels. Unresolved links are exported.
- Known historical features are retrospective reconstructions. Past-only time
  fields prevent simple future-feature leakage, not hindsight bias in sources.
- No source-release sensitivity, independent historical adjudication, prospective
  validation, calibration, external-region validation or causal design is done.

## Ranked path to stronger evidence

1. Review the50-year labels and exclusions with a historian. Resolve composite
   geometry, polity termination and source-ID succession before expanding claims.
   Use two reviewers, cited evidence and disagreement tracking. Do not hand-label
   events after seeing which labels make a model look better.
2. Confirm undated/ranged coding semantics against source records and maintainers.
   Then freeze a justified uncertainty policy and governance-feature design.
3. Freeze a new protocol, compare source releases and held-out regions/periods, and
   evaluate matched baselines with dependence-aware intervals. New exploratory
   decisions require new validation, not reuse of a repeatedly inspected holdout.
4. Evaluate an audit/benchmark contribution: reproducible eligibility, missingness,
   temporal support and lineage-sensitive evaluation may be useful even if no
   predictor improves. Novelty needs a focused related-work review and is not
   established by combining existing datasets.

The original dashboard remains the Equinox feasibility baseline. The expanded
50-year summaries are separate to prevent its rows, explanations or denominators
from being confused with this new experiment. PowerBI project source is available;
PowerBI Desktop refresh and visual rendering remain unverified.

## Source ledger

- [Official Polaris builder and workbook](https://github.com/Seshat-Global-History-Databank/build_polaris_dataset), primary data/code, pinned55ca5fb. Registry, values, flags and dates.
- [Official Cliopatria source](https://github.com/Seshat-Global-History-Databank/cliopatria), primary data/code, pinned5f43337. Direct SeshatID and area interval records.
- [Cliopatria data paper](https://www.nature.com/articles/s41597-025-04516-9), Scientific Data2025, primary methods. Spatial/temporal reconstruction scope and dataset design.
- [Seshat codebook](https://seshat-db.com/codebook), official documentation, inspected2Nov2026. Time ranges, uncertainty, disagreement and inferred-value conventions.
- [Seshat data release page](https://seshatdatabank.info/data), official release information, inspected2Nov2026. Current Polaris release route.
- [Equinox source](https://github.com/seshatdb/Equinox_Data), official data/code. Legacy baseline provenance and eligibility audit.
- [Seshat selection/missingness study](https://escholarship.org/uc/item/4b11h9k0), scholarly critical analysis. Selection and missingness are concerns to examine, not fixed by adding rows.
- [Historical polity survival analysis](https://www.pnas.org/doi/10.1073/pnas.2218834120), primary research. Related outcome framing; this extension does not reproduce it or establish novelty against it.

Source confidence is high for what the retrieved files contain, limited for their
historical completeness and for unresolved coding/continuity interpretations.
Pinned raw URLs and SHA256 appear in `data/research50/manifest.json`.
