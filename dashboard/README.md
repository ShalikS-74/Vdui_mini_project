# Dashboard exports

These flat CSVs are exported for dashboard tools. The consistent record key is
`polity` plus `time_t` (the observed century).

## Tables

### `predictions.csv`

One row per labeled polity-century observation and its out-of-fold prediction.

Columns: `polity`, `century`, `contraction`, `p_contraction`, the seven current
Columns: `polity`, `time_t`, `contraction`, `p_contraction`, the seven current
features, and their seven `_delta` features. The source column is retained as
`time_t` for joins with the other tables.

### `shap_long.csv`

Long-form standardized logistic coefficient contributions for the full-data
explanation fit. Columns: `polity`, `time_t`, `feature`, `contribution`.

Despite the historical filename, this project does not use SHAP; these are
coefficient-times-standardized-feature contributions, not SHAP values.

### `fp_cases.csv`

OOF false-positive review cases. Columns: `polity`, `time_t`,
`oof_p_decline`, `true_label`, `fp_flag`, `top3_coefficient_features`, `note`,
and `type`. `note` and `type` are intentionally blank for manual review.

## Relationships

Join `predictions.csv` and `shap_long.csv` on `polity` and
Join all three tables on `polity` and `time_t`.
