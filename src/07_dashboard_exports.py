from pathlib import Path

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = ["Pop", "Cap", "Hier", "Gov", "Infra", "Info", "Money"]
FEATURES += [f"{feature}_delta" for feature in FEATURES]


def fit_model(table: pd.DataFrame) -> Pipeline:
    model = Pipeline(
        [
            ("imp", SimpleImputer(strategy="median")),
            ("sc", StandardScaler()),
            ("lr", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=0)),
        ]
    )
    model.fit(table[FEATURES], table["contraction"])
    return model


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    dashboard = root / "dashboard"
    dashboard.mkdir(exist_ok=True)
    table = pd.read_parquet(root / "data" / "table.parquet")
    oof = pd.read_csv(root / "data" / "oof.csv", keep_default_na=False)
    cases = pd.read_csv(root / "data" / "fp_cases.csv", keep_default_na=False)
    model = fit_model(table)

    predictions = oof.rename(columns={"century": "time_t", "p": "p_contraction", "y": "contraction"})
    predictions.to_csv(dashboard / "predictions.csv", index=False)

    imputed = model.named_steps["imp"].transform(table[FEATURES])
    standardized = model.named_steps["sc"].transform(imputed)
    contributions = pd.DataFrame(
        standardized * model.named_steps["lr"].coef_[0], columns=FEATURES
    )
    shap_long = contributions.assign(
        polity=table["polity"].to_numpy(),
        time_t=table["century"].to_numpy(),
    ).melt(
        id_vars=["polity", "time_t"],
        var_name="feature",
        value_name="contribution",
    )[["polity", "time_t", "feature", "contribution"]]
    shap_long.to_csv(dashboard / "shap_long.csv", index=False)

    fp_cases = cases.rename(columns={"century": "time_t"})
    fp_cases.to_csv(dashboard / "fp_cases.csv", index=False)

    readme = """# Dashboard exports

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
"""
    (dashboard / "README.md").write_text(readme, encoding="utf-8")
    print(f"saved dashboard exports in {dashboard}")
    print(f"predictions: {len(predictions)} rows")
    print(f"shap_long: {len(shap_long)} rows")
    print(f"fp_cases: {len(fp_cases)} rows")


if __name__ == "__main__":
    main()