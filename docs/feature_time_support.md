# Feature time support: strict primary versus source-display sensitivity

2 November2026. Coverage analysis only. No new models, and no replacement of
strict primary feature values or earlier area-history evaluation.

The pinned workbook contains many feature records with null year_from/year_to.
The official Durrani Empire page, however, displays Professional Soldier=Present
for1747-1826. Its pinned workbook record has both dates null. Inspection of the
official site's pinned `_years_block_new_obj.html` confirms that when a feature's
year_from is null, its polity's start/end dates are shown in silver text. An
unqualified scrape of the displayed dates would lose this distinction.

This resolves the display behavior, **not** the historical time support. The
underlying common model permits null years. The site fallback does not prove that
a historian independently dated the feature throughout the polity lifetime. It
also is not evidence that the trait was measured before the forecast origin.

## Implemented coverage sensitivity

`research/feature_support_audit.py` allows a deliberately narrower scenario than
the website display: exactly one source record for the polity/feature, both dates
null, no disputed/uncertain flag, and a single numeric point or direct P/A code.
Assign it across registered polity duration, with provenance explicitly marked
`polity_lifetime_display_assumption`. Preserve explicit strict values. Do not
extend partial dates, ignore conflicting records or reinterpret inferred/unknown
codes. This creates a separate coverage audit, not silently dated training data.

- Strict primary:144/756rows with any of the20fixed governance/scale features.
- Display-assumption scenario:727/756rows with any feature.
- Administrative level:10strict versus362scenario rows.
- Professional soldiers:13strict versus331scenario rows.
- Full-time bureaucrats:2strict versus396scenario rows.

The increase demonstrates that **time-support policy is a major analysis choice**.
It does not demonstrate reliable historical prediction. Even source-backed
polity-wide states can encode hindsight about a trait adopted late in a reign.
The release-methods report says changes are generally recorded around100-200years;
the workbook omits explanatory narratives and references, which must be read on
the source system. A50-year model cannot assume finer measurement precision.

## Next defensible test

Before modeling a polity-wide scenario, freeze a distinct exploratory protocol
and keep its claim explicitly retrospective. Compare governance features against
the already-defined area-history baseline using exactly the same fixed splits;
report all results, including negative results, plus the strict-policy coverage.
Any governance claim must survive a source-record time-support review and new
independent validation. Do not relabel the existing inspected holdout confirmatory.

Where the source narrative identifies only a point-in-time presence, record that
bound rather than extending it backwards. Where the narrative explicitly supports
whole-polity presence/absence, preserve its citations and uncertainty. Independent
expert review is still a different step from this automated/source-code check.

Reproduce after building panel.csv:

```sh
python research/feature_support_audit.py --polaris-path data/raw/Polaris2026.xlsx
```

The exact pinned workbook hash is required. Row-level audit records preserve both
strict and scenario values with their provenance; small summaries are committed.
No model is fitted by this script.

Sources inspected:
- https://seshat-db.com/core/polity/af_durrani_emp/ (live displayed feature dates and historical narrative, inspected2November2026)
- https://raw.githubusercontent.com/Seshat-Global-History-Databank/seshat/1f847d95e224860115a3dc358165380fe5487bcd/seshat/apps/core/templates/core/partials/_years_block_new_obj.html (pinned official template, polity-date fallback)
- https://raw.githubusercontent.com/Seshat-Global-History-Databank/seshat/1f847d95e224860115a3dc358165380fe5487bcd/seshat/apps/core/models.py (nullable feature year fields)
- https://escholarship.org/content/qt9wj6z91m/qt9wj6z91m.pdf (Polaris release-methods paper, variable-change temporal scale and omitted narratives/references)
- https://seshat-db.com/core/all_datatypes/ (official code/tag distinctions)

Live source values may differ from the frozen workbook. The comparison establishes
how missing dates are displayed, not equivalence of all current and pinned records.
