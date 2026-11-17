# Implementation plan

Original team planning notes, cleaned up and formatted on 2026-11-17. The
substance is unchanged. Where the notes describe the first prototype, the current
state may differ: `docs/audit_report.md` and `docs/completion_status.md` are the
authoritative current status, and the root `README.md` describes what is actually
implemented now.

## 0. Two problems to resolve first

- **Time resolution vs. 50-year horizon.** Seshat's main dataset is coded in
  coarse time slices (often ~100-year steps), so a 50-year horizon may not line
  up with it. Check the time-step structure of the Seshat export before fixing
  the label. If features are century-level, use a 100-year horizon, or take the
  area series from Cliopatria (yearly) and align features to the nearest slice.
- **Title vs. scope.** The proposed title says "Calibrated Transfer", but
  calibration was cut. Either drop "Calibrated" from the title or call the
  output a "model score", not a "risk estimate" or probability. Uncalibrated
  RF/LightGBM outputs are not probabilities, so they must not be labeled as
  such in the dashboard.

## 1. Repo layout

```
data/raw/        seshat/, cliopatria/, vdem/, wb/
data/processed/  panel.parquet, predictions.parquet, shap_long.parquet
src/             01_build_panel.py, 02_labels.py, 03_split.py,
                 04_train.py, 05_shap.py, 06_fp_audit.py, 07_domain_shift.py
dashboard/       .pbix + exported CSVs
```

Do everything in Python and export flat tables. Power BI should only display them.

## 2. Build the panel (polity x time)

One row per (polity_id, time_t).

- Features at t: fiscal, military, succession, administrative variables.
- Missingness: Seshat is very sparse. Keep a per-feature missing-rate table,
  drop features above roughly 60% missing, and add missing-indicator columns
  for the rest. Do not impute globally. Imputation goes inside the CV pipeline
  (section 4).
- Cliopatria join: match on name and date range, and log the unmatched
  polities. Timebox it to about one week. If it fails, fall back to Seshat's
  own area/polity-continuity variables, as planned.
- Assign a lineage_id (a polity and its predecessors/successors share one).
  It is needed for splitting.

## 3. Labels

```python
ratio = area[t+H] / area[t]          # H = horizon
y = np.where(ratio <= 0.7, "decline",
     np.where(ratio >= 1.3, "rise", "stable"))
```

- Drop rows where t+H is unobserved. Do not label them "stable".
- Check the class distribution early. Expect heavy imbalance, so use
  class_weight="balanced" and report macro-F1 and per-class PR-AUC, not accuracy.
- Overlapping windows for the same polity are highly autocorrelated. This is
  why grouped splitting is mandatory.

## 4. Leakage-safe splits

- Primary: GroupKFold (or StratifiedGroupKFold) with groups=lineage_id.
  Repeat with several seeds, since N is small.
- Temporal (if time allows): train on t < cutoff, test on t >= cutoff. Also
  drop training rows whose label window crosses the cutoff, or future area
  data leaks into training.
- Put everything in a sklearn Pipeline (imputer -> scaler -> model), so
  fitting happens only on training folds.

## 5. Models

- Baseline: logistic regression, scaled features, L2.
- Stronger model: LightGBM (or RF). Use shallow trees and strong
  regularization. With a few hundred polities, deep trees will overfit.
- Report mean +/- std across folds. Also include a majority-class baseline so
  people can see what the models actually add.

## 6. SHAP

- shap.TreeExplainer on the final model. Store output in long format:
  polity_id, time_t, feature, value, shap_value, class.
- Correlated features (many Seshat variables move together) split SHAP credit
  between them. Group features into governance/fiscal/military/succession/
  admin and report group-level SHAP as well.
- For logistic regression, use standardized coefficients.

## 7. False-positive audit (the core contribution)

- Define "confident" before looking at results, e.g. P(decline) >= 0.7 from
  out-of-fold predictions only. Using in-sample predictions invalidates the
  audit.
- FP = confident decline prediction and true label != decline.
- Compare FPs against the true positives (correctly flagged declines) using
  feature distributions and SHAP.
- Look for what the FPs have that the true positives lack. This is the "what
  protected them" finding.
- Manually review every FP case against the historical record. Some will be
  label artifacts (a polity renamed, a successor state, or area noise) rather
  than real survivals. Tag each FP as genuine_survival or label_artifact.
  This step is what separates a real audit from noise-hunting.
- Export a flag table: polity_id, time_t, p_decline, true_label, fp_flag,
  fp_type, note.

## 8. Power BI dashboard

- Import the CSVs or parquet-derived tables: predictions, shap_long, fp_cases.
- Visuals: polity slicer (and a time slicer); card for the model score; bar
  chart of SHAP values filtered by the selected polity/time; table of flagged
  FPs with cross-filtering; a scatter of score vs. outcome to show where the
  model was confidently wrong.
- Relationships: predictions 1->many shap_long on (polity_id, time_t).
- Add a caption explaining that the score is uncalibrated.

## 9. If time allows: domain-shift check

- Restrict to features present in both eras (the bridge set from V-Dem and
  World Bank).
- Per-feature standardized mean difference and KS test.
- Classifier two-sample test: train a classifier to tell historical rows from
  modern rows. AUC near 0.5 means comparable; AUC near 1.0 means not
  comparable, and transfer is unjustified. Use grouped CV here as well.
- State the result plainly either way.

## 10. USSR retrospective

Before committing to this, verify that both Seshat-style features and V-Dem
coverage exist for the USSR in the years leading up to 1991. Seshat's coverage
of modern polities is thin, and V-Dem codes different constructs, which is
exactly what the domain-shift check measures. If the shift check says "not
comparable", the USSR case becomes a demonstration of that limit, not a
validation.

## 11. Suggested timeline (12 weeks)

| Weeks | Work |
|---|---|
| 1-2 | Seshat export, time-step check, panel, missingness report |
| 3 | Cliopatria join, with fallback decision at end of week |
| 4 | Labels, class distribution, splits |
| 5-6 | LR + LightGBM, grouped CV |
| 7 | SHAP |
| 8-9 | FP audit and manual review |
| 10 | Power BI dashboard |
| 11 | Domain shift and temporal split (if time allows) |
| 12 | Writeup, buffer |

The riskiest assumption is the label and time-resolution mismatch in section 0.
Settle it in week 1, because everything downstream depends on it.

## Dataset notes: Cliopatria and Archigos

The original scope names two external datasets, Cliopatria and Archigos.
Neither is needed for the simplified plan.

**Cliopatria (historical polity borders).** An open geospatial dataset of
states, political groups, events and rulers from 3400 BCE to 2024 CE, part of
the Seshat project. GitHub: Seshat-Global-History-Databank/cliopatria (the
docs say downloading from GitHub is usually faster than the API). Zenodo
v0.0.1 (Aug 2024): https://zenodo.org/records/13363121 (49.2 MB zip). Format:
a single GeoJSON file, so polygon areas are computed directly (use an
equal-area projection) to get territory over time.

Why the join is risky: Seshat's feature data has no geographic extent, so the
two must be linked. A Seshat-Cliopatria hackathon page describes this as a
separate tool-building task, involving finding which Cliopatria polities are
missing from Seshat and inferring predecessor/successor links from geographic
overlap and time continuity.

**Archigos (political leaders).** A dataset of effective leaders for 188
countries, 1875-2004, coding how and when each came to power and left office.
Maintainer page: https://rochester.edu/college/faculty/hgoemans/data.htm.
Version 4.1 runs to 31 Dec 2015, in Stata format. Easier access: the R
package peacesciencer ships a subset (3,409 observations, 11 variables) at
https://rdrr.io/cran/peacesciencer/man/archigos.html. Extending it to
2016-2026 is costly: the data stops at 2015, so extension means hand-coding
about ten more years of leader transitions across all countries.

What this means:

- Archigos covers only modern states. It is irrelevant to a Seshat-based
  historical model; it was only ever for the modern "bridge" features, which
  the simplified plan cuts.
- Cliopatria supplies labels, not features. The simplified plan takes labels
  from Equinox's own Terr variable, so no join is needed.
- The other datasets in the original document (V-Dem, World Bank, CrisisDB)
  are also outside the simplified plan, except CrisisDB for manually
  annotating flagged cases.

If the team insists on Cliopatria, treat it as a stretch goal after the
baseline works. (Note: the later research extension did adopt Cliopatria
geometry for the separate 50-year study; see `research/README.md`.)

## Glossary

A **polity** is any independent political unit: a state, kingdom, empire,
city-state, or similar - a politically organized society that governs itself
and is not under a higher authority. In this data, each polity is one named
entity, like the Roman Empire, the Ming Dynasty, or the Inca Empire. The term
is used instead of "country" or "state" because many historical units are not
countries in the modern sense, and the word fits all of them. A
**polity-century** (or polity-time row) is one such polity at one point in
time; the same polity can appear many times.

## Historical note: the first false-positive explainer (superseded)

The first prototype exported a feature-ranking CSV comparing 5 confident
false positives against 6 observed contractions, using coefficient-times-value
contributions from a full-data fit. Its reading was:

- Hierarchy was the strongest separator: false positives had higher hierarchy
  values and larger positive hierarchy contributions.
- Population was similarly important: false positives had higher population
  values and larger positive population contributions.
- Capital size differed substantially between the groups, but its contribution
  was negative because its logistic coefficient offsets contraction risk, so
  it did not explain the mistake.
- Money and information variables contributed slightly more to false-positive
  predictions; governance contributed more toward actual contractions.
- The delta features contributed very little in this small dataset.

The takeaway hypothesis was that the model tended to flag large, populous,
highly layered polities as about to shrink, and some of those did not.

That explainer is superseded and must not be quoted as a current result:

- It described the old percentile-based 5-case selection; the current audit
  uses the pre-specified OOF score >= 0.70 rule (14 cases, all pending review).
- Its values came from a full-data fit for explanation only; current exports
  use actual out-of-fold linear SHAP from the training fold models.
- Those were coefficient contributions, not SHAP values.
- The sample was 5 false positives and 6 contractions; one polity more or less
  could change the ranking. It was a hint about where to look, not a finding,
  and not causal. "Big polities have more territory to lose" is an alternative
  explanation for the same pattern.

For the writeup, treat any such contributions as illustrative, then
investigate 3-5 of the flagged polities individually. That case-by-case work
is the real audit.
