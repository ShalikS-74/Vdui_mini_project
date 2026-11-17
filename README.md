# Beyond the Empire

A reproducible, exploratory historical contraction model with held-out explanations
and a false-positive review workflow. **Not research-ready or a modern risk model.**

## Run

Python 3.10 or newer:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/bundled_exports.py  # restore bundled exports for offline demo
python src/pipeline.py        # optional full scientific rebuild from source
python powerbi/build_project.py
pytest -q
streamlit run app.py
```

The pipeline downloads the official, commit-pinned Equinox spreadsheet when absent,
then regenerates all artifacts. Network access is needed on the first run.
`data/run_metadata.json` records source URL, SHA-256, configuration and class counts.
The source is CC BY-NC-SA according to its README. See `docs/data_provenance.md`.

## What is implemented

- Exact +100-year labels from observed log10 territory: decline <= 0.7 area ratio.
  Missing future area is censored, never silently labeled stable.
- Current features and exact previous-century differences. Regression tests prove
  that changing future features does not change current model inputs.
- Missingness filter (>60% removed), indicators, imputation and scaling learned
  inside each training fold.
- Logistic, shallow random forest and majority baseline, three grouped seeds;
  temporal holdout with label-window purge. Grouping is observed PolID across NGA,
  **not verified predecessor/successor lineage**.
- Fold macro-F1 and per-class AP, mean/std/count, individual predictions and splits.
- Actual fold-specific linear SHAP, reconstructing each displayed seed-0 OOF
  score in log-odds; feature-group exports with literal, cautious group names.
- Fixed >=0.70 OOF false-positive queue, validated, persistent sourced-review input.
- Tested Streamlit explorer, audit queue, evaluation and downloads.
- Power BI PBIP candidate with model, pages and visuals. **Schema-checked, not
  opened/rendered in Power BI Desktop. Not a verified dashboard or a PBIX.**
  Run `python powerbi/build_project.py` to materialize it. See `powerbi/README.md` for exact remaining steps.

## Current evidence, not a performance claim

98 labeled rows, 6 contractions. Grouped fold mean macro-F1: logistic 0.452,
forest 0.472, majority 0.483. The models do not beat the majority baseline on this
metric. Fold results are highly unstable; some contain no positives. Undefined AP
is omitted and its valid-fold count is shown. Repeated folds are correlated and
standard deviations are not confidence intervals. Fourteen seed-0 confident
false positives await historical review; none is labeled a genuine survival.

## Target experiments

```sh
python src/pipeline.py --target three-class --horizon 100
python src/pipeline.py --target three-class --horizon 50
```

Alternative runs use separate output folders and never replace dashboard data.
The exact 50-year run has no matched observations in this source and fails clearly;
it does not interpolate labels. The century-level experiment does not establish
approval to replace the proposal's 50-year target. User/team scope remains open.

## Research and completion status

Read `docs/completion_status.md` and `docs/research_plan.md`. Historical review,
verified continuity, broader outcome coverage, exact target feasibility and
Power BI Desktop validation remain open. No publishability, novelty, protective
factor, calibrated probability or modern transfer is claimed. The initial audit's
future-delta diagnosis was reversed: shifting source time forward for an equality
join retrieves the past, not the future. Its original text is retained, with a
prominent correction and tests. No code is merged to main by this work.

Canonical branch exports use `data/table.csv`; the older tracked parquet is a
legacy snapshot until `python src/pipeline.py` regenerates it. Rebuild or run the
offline restore before using parquet directly. The dashboard uses flat CSVs.

## Expanded exploratory50-year study

`research/README.md` gives pinned-source reproduction commands, `research/protocol.md`
records choices fixed before fitting the expanded models, and
`docs/research_findings.md` reports the results and open gates. The756candidate
observations make the area-change target feasible, but strict governance coverage
is sparse and the time-plus-group forest does not materially beat majority.
This is a separate experiment, not a replacement of the old dashboard and not a
claim of publishable results. Small summaries are in `data/research50/`; rerunning
creates full panel, lineage/exclusion logs, per-fold membership and predictions.
