from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SEED = 0
FEATURES = ["Pop", "Cap", "Hier", "Gov", "Infra", "Info", "Money"]
FEATURES += [f"{feature}_delta" for feature in FEATURES]


def make_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("imp", SimpleImputer(strategy="median")),
            ("sc", StandardScaler()),
            (
                "lr",
                LogisticRegression(
                    class_weight="balanced", max_iter=1000, random_state=SEED
                ),
            ),
        ]
    )


def evaluate(y_true: pd.Series, probabilities: np.ndarray) -> None:
    base_rate = float(y_true.mean())
    predictions = (probabilities >= 0.5).astype(int)
    baseline_probabilities = np.full(len(y_true), base_rate)
    baseline_predictions = np.ones(len(y_true), dtype=int) if base_rate >= 0.5 else np.zeros(
        len(y_true), dtype=int
    )
    results = pd.DataFrame(
        [
            {
                "model": "logistic_regression",
                "precision": precision_score(y_true, predictions, zero_division=0),
                "recall": recall_score(y_true, predictions, zero_division=0),
                "pr_auc": average_precision_score(y_true, probabilities),
            },
            {
                "model": "base_rate_baseline",
                "precision": precision_score(y_true, baseline_predictions, zero_division=0),
                "recall": recall_score(y_true, baseline_predictions, zero_division=0),
                "pr_auc": average_precision_score(y_true, baseline_probabilities),
            },
        ]
    )
    print("OOF metrics (no accuracy reported):")
    print(results.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print(f"base rate: {base_rate:.4f}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    table_path = root / "data" / "table.parquet"
    output_path = root / "data" / "oof.csv"
    table = pd.read_parquet(table_path)
    table = table.dropna(subset=["contraction", "polity", "century"]).reset_index(drop=True)
    x_values = table[FEATURES]
    y_values = table["contraction"].astype(int)
    groups = table["polity"]

    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    splits = list(splitter.split(x_values, y_values, groups=groups))
    for train_index, test_index in splits:
        train_groups = set(groups.iloc[train_index])
        test_groups = set(groups.iloc[test_index])
        assert train_groups.isdisjoint(test_groups)

    probabilities = cross_val_predict(
        make_pipeline(),
        x_values,
        y_values,
        groups=groups,
        cv=splits,
        method="predict_proba",
    )[:, 1]
    evaluate(y_values, probabilities)

    oof = table[["polity", "century", "contraction"] + FEATURES].copy()
    oof.insert(2, "y", oof.pop("contraction"))
    oof.insert(3, "p", probabilities)
    oof.to_csv(output_path, index=False)
    print(f"saved: {output_path}")
    print(f"rows: {len(oof)}; folds: {len(splits)}; groups: {groups.nunique()}")
    print("assumptions: one composite (NGA, PolID) polity key; OOF probabilities use grouped folds;")
    print("imputation and scaling are fit inside each training fold only.")
    print("caution: only 6 positive labels remain, so fold metrics are unstable and descriptive.")


if __name__ == "__main__":
    main()