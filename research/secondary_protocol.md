# Secondary exploratory protocol: polity-lifetime display scenario

2November2026, fixed before fitting governance-scenario models. This is exploratory,
written after inspecting strict coverage, area-only performance and source-display
semantics. It is not preregistration or confirmatory evaluation. No parameter search.

Question: under a retrospective polity-lifetime assignment for single undated
source records, do the20preselected governance/scale features add discrimination
over the frozen area-history baseline? This is not evidence those inputs were
known or valid at the forecast origin. Keep the strict primary dataset unchanged.

- Use only `feature_support_audit.py` scenario values and marked provenance.
- Preserve all756rows, class thresholds, source hashes and split membership from
  the primary area-history study. No class/period/region selection after results.
- Models: identical balanced logistic(C1) and shallow forest(150trees,depth3,
  leaf4) with the same fold-local median imputation/missing indicators/scaling.
- Compare governance-only and area-plus-governance to existing area-only and
  majority predictions, paired on the same rows and splits. No new tuning.
- Report macro-F1/AP fold summaries and pooled seed0 OOF differences. Fixed
 1000group-bootstrap replicates with seed20261102, intervals explicitly conditional
 exploratory and not corrected for multiple comparisons. Report all four models.
- Time-plus-group holdout remains inspected exploratory evidence. Do not call it
  untouched, independent or proof of governance causality. Failure to improve is
  reported; success remains conditional on retrospective time-support assumptions.
- Source-narrative spot checks: inspect Durrani, Kushan and Eastern Han (chosen
  before model fitting because their direct professional-soldier codes are undated).
  Contrast displayed date fallback with pinned values; record source text scope,
  dates/citations when accessible. Do not convert spot checks into independent
  validation or generalize three records to the entire dataset.

Required before a forecasting claim: source-supported time bounds, reviewed
measurement/outcomes, external evaluation not repeatedly inspected, and separation
of institutions caused by growing states from institutions predicting future change.
