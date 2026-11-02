# Label adjudication and sensitivity audit

2 November2026. These are automated source/consistency checks. They are not
independent expert review and do not settle what a historical collapse means.
No models were refitted or selected during this audit.

## Defensible outcome and termination policy

Keep the primary label named **continuing-ID mapped area change over50years**.
A registry end date is not evidence of collapse. A name change, dynasty change,
conquest, incorporation, fragmentation and substantial institutional transformation
can have different meanings. The PNAS survival study explicitly distinguishes
state termination from societal collapse and reports sensitivity to periodization.
The Seshat codebook permits fuzzy/overlapping polity durations. Cliopatria describes
gaps when a smaller entity is incorporated and later reappears.

Therefore:

- Do not assign zero area, stable status or collapse to a missing future record.
- Do not extend registry dates or silently join successor areas. One-to-many
  succession cannot be treated as a single polity's growth/shrinkage without a
  declared unit-of-analysis rule and source review.
- Preserve two distinct future endpoints if pursuing a revised study: geographical
  extent of the continuing political unit, and historically coded political
  termination/transition. Never use the first as an automatic proxy for the second.
- For every proposed successor label, record source polity IDs, dates and their
  uncertainty, relationship type, sources supporting continuity/termination,
  reviewer judgments and disagreement. Source records flag candidates; review
  decides eligibility before model outcomes are examined.
- When crisis dates span the forecast boundary, use interval-censored event time
  in a suitable survival design, or exclude ambiguous windows under a fixed rule.
  Do not pick a convenient midpoint to produce a crisp50-year positive label.
- A negative crisis label requires evidence that the relevant outcome was observed
  absent in the observation window. No crisis record means unlabelled, not absent.

The terminal-window audit finds592registry-grid windows whose future endpoint
exceeds their polity's registered end. Of these,267have a unique current geometry.
They are outside the current continuing-ID study. These counts describe windows,
not592distinct terminations or267collapse events. The current primary constructor
never generated them as candidates; the audit now makes that selection visible.

## CrisisDB cross-check

The Polaris workbook's CrisisDB-consequences sheet has166records, including six
with direct Collapse=P, oneIP, oneIA, oneSUand157A. These are selected crisis
annotations, not a complete observed cohort of all polity-years. There are95
candidate panel/source-crisis window overlaps when either linked ID is considered,
but **zero overlaps with the six direct-P collapse records**.

Cahokia, Tiwanaku and Wari lack direct geometry matches in this source. Early
Valois France has several simultaneously mapped entities/composites rather than
one unambiguous area. The Inca panel has a1450-1500growth window but not the later
source-coded1528-1570crisis window under the continuing-ID policy. Thus the panel
cannot validate collapse sensitivity using these records. It is not evidence of
no collapse. `direct_collapse_coverage.csv` preserves the exact source rows and
eligibility checks for review. The two Wari annotations are separate source rows,
not two independent polities. No historical cause or coding-error verdict is made.

## Composite geometry and split groups

The Cliopatria paper explains that parenthesized composite polygons duplicate
member polygons. Never sum every same-ID row: that can double-count an empire,
member, relation or alternative extent. The primary analysis requires exactly one
active POLITY record. A future reviewed composite policy must distinguish the
political unit of interest and test duplicates/topological union, rather than
choosing whichever area yields a desired outcome.

Explicit Components/MemberOf links generate1210distinct registry edge/basis
records in the audit;18cross the original registry-level groups. Those18link
Bohemia/Moravia to Holy Roman Empire periods. Transitive strengthening across all
registry IDs leaves **113eligible-panel groups unchanged**. This checks paths
through ineligible IDs as well. It does not establish that all related histories
are separated: shared sources, regions, common shocks and incomplete links remain.

## Label-only sensitivity, no score optimization

The data paper says historical boundary uncertainty is unquantified. The following
are hypothetical stress tests, **not error estimates or confidence intervals**.
With independent endpoint area errors bounded by±epsilon, the ratio range is
r*(1-epsilon)/(1+epsilon) through r*(1+epsilon)/(1-epsilon). A label is invariant
only if its full range stays in the same operational class.

|Hypothetical endpoint-area bound|Decline invariant/59|Rise invariant/92|Stable invariant/605|
|---|---:|---:|---:|
|±5%|42|80|579|
|±10%|34|68|524|
|±20%|25|47|0|

Independent errors are conservative for perfectly correlated endpoint errors;
correlation itself is unknown. Actual border errors need not be multiplicative.
A lack of invariance is possible threshold sensitivity, not a probability of a
wrong label. No perturbation level is selected as the correct historical error.

We also shift **both** current/future lookups by the same±1,±10or±25years while
respecting registry bounds. Labels must agree at negative, zero and positive
shifts; unavailable/ambiguous shifted endpoints count as noninvariant. For declines,
41/59are invariant at±1year,20/59at±10years and3/59at±25years. This combines timing
sensitivity and eligibility change; it is not a pure error rate. The50-year grid
phase and irregular source boundary timing deserve explicit future review.

## Source-release sensitivity

Pinned currentv0.2.1has756rows; priorv0.2.0has754. All754common polity/year labels
are unchanged, with two current-only rows. This is a limited consecutive-release
check, not independent-source replication and not a guarantee of label accuracy.
Both releases share underlying sources. Hashes and releases are recorded in the
audit script/manifest; row-level comparisons regenerate from the pinned inputs.

## Reproduction and evidence

After constructing the primary panel, run:

```sh
python research/adjudication_audit.py --polaris-path data/raw/Polaris2026.xlsx --clio-path data/raw/cliopatria.geojson.zip --previous-path /path/to/v0.2.0.zip
```

The previous file is from official revision
ad28a691b7c07c1fca89d0e0636d324667d2a258, SHA256
`d01ae3a20d358cc5d54f69d9d725d390767d9c8759ac89ad6f90c58d106f3370`.
Use its exact `cliopatria.geojson.zip`; download only from the official repository.
All three input hashes are checked. Outputs include row-level release comparisons,
terminal-window review queue, crisis overlaps, direct-collapse coverage, component
links, strengthened groups, region-selection and stress summaries. They are
candidate adjudication evidence, never completed review labels.

Sources:
- https://www.nature.com/articles/s41597-025-04516-9 , primary data/methods, especially composite geometry, temporal gaps and unquantified border uncertainty.
- https://github.com/Seshat-Global-History-Databank/cliopatria , pinned data and release history.
- https://github.com/Seshat-Global-History-Databank/build_polaris_dataset , pinned workbook, crisis annotations, relationships and dates.
- https://seshat-db.com/codebook , polity definitions, fuzzy dates, unknown/inferred codes.
- https://www.pnas.org/doi/10.1073/pnas.2218834120 , state termination versus collapse and periodization sensitivity.
