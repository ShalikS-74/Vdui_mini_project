# Implementation Audit Report

**Project:** Beyond the Empire / Equinox contraction model  
**Audit basis:** repository source files, generated data exports, dashboard code, and
the project documents in `docs/`  
**Audit date:** 2026-11-02

## Executive summary

The repository contains a working prototype for a **binary historical contraction
classifier** and a Streamlit demonstration. It is not yet an implementation of
the full problem statement. The current prototype has:

- a 98-row, 14-feature modeling table;
- a leakage-aware preprocessing pipeline (imputation and scaling are fitted inside
  cross-validation);
- grouped and temporal split scripts;
- out-of-fold predictions;
- a false-positive ranking/export;
- dashboard CSV exports and a Streamlit UI.

The most important issue is that the generated `_delta` features use feature
values from the future time point (`t + 100`). This is target-period leakage and
means the current model results must not be presented as leakage-safe until the
feature construction is corrected and all outputs are regenerated.

## Status against the stated scope

| Area | Status | Evidence / audit result |
|---|---|---|
| Seshat-style source ingestion | **Partial** | `src/01_audit.py` and `src/02_build.py` expect `data/raw/Equinox_on_GitHub_June9_2022.xlsx`, but that input is not present in the repository. |
| Clean Seshat–Cliopatria join | **Not implemented** | No Cliopatria files, join logic, unmatched-polity log, or lineage mapping exists. The implementation uses Equinox `Terr` directly. |
| Label definition | **Implemented, but different from scope** | `Terr` is treated as log10 territory and a 30% drop is applied over an exact 100-year horizon. The documented target scope requested decline/rise/stable over 50 years. |
| Three-class outcome | **Not implemented** | The data contains only `contraction` values 0/1: 92 non-contractions and 6 contractions. |
| Missingness audit | **Partial** | Missingness is printed by `src/01_audit.py`; no persisted report, feature-removal rule, or missingness-indicator features are produced. |
| Leakage-safe feature construction | **Failed / must fix** | `src/02_build.py` shifts the feature table forward by 100 years and computes `feature(t) - feature(t+100)`. The model therefore sees future covariates. |
| Grouped validation | **Implemented, with a weaker grouping unit** | `src/03_train.py` and `src/04_splits.py` use `StratifiedGroupKFold` grouped by composite `polity`, not the planned `lineage_id`. |
| Temporal validation | **Implemented** | `src/04_splits.py` uses cutoff 800 and excludes training rows whose 100-year window crosses the cutoff. |
| Baseline logistic regression | **Implemented** | Median imputation, standardization, class weighting, and logistic regression are defined in the training scripts. |
| Stronger model | **Not implemented** | No random forest or LightGBM model exists. |
| Repeated grouped evaluation | **Partial** | Three seeds are used in `src/04_splits.py`, but results are exported as pooled predictions rather than a mean ± standard deviation report. |
| Class-imbalance metrics | **Partial** | Precision, recall, and PR-AUC are printed. Macro-F1 and per-class PR-AUC are not reported. With only 6 positive labels, estimates are highly unstable. |
| SHAP explanations | **Not implemented** | `src/05_audit.py` and `src/07_dashboard_exports.py` generate standardized coefficient contributions, not SHAP values. |
| Group-level explanations | **Not implemented** | No governance/fiscal/military/succession/administration feature groups are defined. |
| False-positive audit | **Partial** | OOF probabilities select five cases using the 95th percentile, and feature rankings are exported. The planned fixed confidence rule (`P(decline) >= 0.7`) is not used. |
| Manual FP review | **Not implemented** | `note` and `type` are blank in `data/fp_cases.csv` and `dashboard/fp_cases.csv`; no historical verification or `genuine_survival`/`label_artifact` classification is present. |
| Power BI dashboard | **Not implemented as specified** | There is no `.pbix` file. `app.py` provides a Streamlit polity browser, FP explorer, and illustrative what-if view. |
| Dashboard data exports | **Implemented** | Predictions, contribution explanations, and FP case CSVs are exported. |
| Domain-shift check | **Not implemented** | No V-Dem/World Bank bridge set, standardized mean differences, KS tests, or historical-vs-modern classifier exists. |
| Modern/USSR retrospective | **Not implemented** | No modern data or retrospective case analysis is present. |
| Probability calibration | **Intentionally omitted** | This matches the stated cut scope, but the UI currently labels an uncalibrated model output as a probability. |
| Documentation | **Partial** | The plan records intended methods and limitations, but `dashboard/README.md` contains duplicated/incomplete column text and does not fully describe the current implementation. |

## Current generated outputs

| Artifact | Current contents |
|---|---|
| `data/table.parquet` | 98 labeled polity-century rows; binary target; seven current features plus seven `_delta` features |
| `data/oof.csv` | 98 grouped out-of-fold predictions |
| `data/splits.csv` | Grouped and temporal train/test memberships |
| `data/split_predictions.csv` | 294 grouped and 47 temporal predictions |
| `data/fp_cases.csv` | 5 OOF-selected false-positive cases, all awaiting manual review |
| `data/fp_feature_ranking.csv` | 14 feature-level comparison rows |
| `dashboard/predictions.csv` | Flat export of OOF predictions and features |
| `dashboard/shap_long.csv` | 1,372 coefficient-contribution rows, not SHAP |
| `dashboard/fp_cases.csv` | Dashboard copy of the five unreviewed cases |

## Findings requiring action

### 1. Release blocker: future feature leakage

In `src/02_build.py`, the delta frame is shifted with:

```python
deltas["Time"] = deltas["Time"] + HORIZON
```

and then merged onto the current row. Consequently, a row at time `t` receives
the feature values from `t + 100`, and its delta is computed against those future
values. This is inconsistent with the stated “features at `t`” design and
invalidates the leakage-safe claim. Deltas should instead be based on `t` and a
prior observed time, or removed until a clearly defined past-only feature window
is implemented. All parquet, prediction, audit, and dashboard exports then need
to be regenerated.

### 2. The model target does not match the proposal

The proposal describes decline, rise, and stable at a 50-year horizon. The code
implements only a binary contraction/non-contraction label at an exact 100-year
horizon. This is a legitimate simplification, but it must be explicitly approved
as the project target or replaced before reporting results against the original
scope.

### 3. Explanations are mislabeled in the product surface

The dashboard export code correctly states that the values are coefficient-times-
standardized-feature contributions, but the application displays them as model
contributions and the file is named `shap_long.csv`. They are not SHAP values.
The UI also displays an “Illustrative contraction probability” although the
project intentionally excludes calibration. Use “model score” unless calibration
is added, and rename or clearly relabel the explanation export.

### 4. The false-positive audit is not complete

The cases are selected from OOF predictions, which is the correct basis, but the
threshold is data-dependent (the OOF 95th percentile) rather than the documented
pre-specified 0.7 rule. The five cases have no manual historical review, no
artifact/survival tag, and no protective-factor conclusion. Therefore the core
claimed contribution is currently an export for review, not a completed audit.

## Recommended completion order

1. Fix the future-feature leakage and regenerate every downstream artifact.
2. Confirm the final target: binary 100-year contraction or three-class 50-year
   decline/rise/stable.
3. Add a reproducible source-data/data-download decision, or commit a documented
   input acquisition step; currently a clean checkout cannot rebuild the table.
4. Add lineage IDs if predecessor/successor grouping is required; otherwise state
   that the grouping unit is the observed composite polity key.
5. Complete manual review and classification of every false-positive case.
6. Replace “SHAP” terminology with coefficient-contribution terminology, or add
   actual SHAP computation.
7. Decide whether Streamlit is the accepted dashboard deliverable. If Power BI
   is mandatory, create and version the `.pbix` or document why it is excluded.
8. Treat domain shift, modern indicators, USSR retrospective analysis, calibration,
   and a stronger model as future work unless the scope is expanded.

## Overall assessment

**Prototype maturity:** demonstrable baseline, not research-ready.  
**Core functionality:** partially implemented.  
**Current result validity:** blocked by future covariate leakage and the very small
positive class.  
**Best defensible claim today:** the repository demonstrates a binary, exploratory
historical contraction pipeline with grouped/temporal split scaffolding and an
unreviewed false-positive export. It does not yet support calibrated modern-risk
transfer claims or a completed explainable false-positive study.
