from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SEEDS = [0, 1, 2]
N_SPLITS = 5
TEMPORAL_CUTOFF = 800
HORIZON = 100
FEATURES = ["Pop", "Cap", "Hier", "Gov", "Infra", "Info", "Money"]
FEATURES += [f"{feature}_delta" for feature in FEATURES]


def make_pipeline(seed: int) -> Pipeline:
    return Pipeline(
        [
            ("imp", SimpleImputer(strategy="median")),
            ("sc", StandardScaler()),
            (
                "lr",
                LogisticRegression(
                    class_weight="balanced", max_iter=1000, random_state=seed
                ),
            ),
        ]
    )


def grouped_splits(table: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    rows = []
    predictions = []
    x_values = table[FEATURES]
    y_values = table["contraction"].astype(int)
    groups = table["polity"]
    for seed in SEEDS:
        splitter = StratifiedGroupKFold(
            n_splits=N_SPLITS, shuffle=True, random_state=seed
        )
        for fold, (train_index, test_index) in enumerate(
            splitter.split(x_values, y_values, groups=groups)
        ):
            train_groups = set(groups.iloc[train_index])
            test_groups = set(groups.iloc[test_index])
            assert train_groups.isdisjoint(test_groups)
            for index in train_index:
                rows.append({"protocol": "grouped", "seed": seed, "fold": fold, "row": index, "partition": "train"})
            for index in test_index:
                rows.append({"protocol": "grouped", "seed": seed, "fold": fold, "row": index, "partition": "test"})

            model = make_pipeline(seed)
            model.fit(x_values.iloc[train_index], y_values.iloc[train_index])
            probabilities = model.predict_proba(x_values.iloc[test_index])[:, 1]
            for index, probability in zip(test_index, probabilities):
                predictions.append(
                    {
                        "protocol": "grouped",
                        "seed": seed,
                        "fold": fold,
                        "row": index,
                        "y": int(y_values.iloc[index]),
                        "p": probability,
                    }
                )
    return rows, predictions


def temporal_split(table: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    train_mask = table["century"] < TEMPORAL_CUTOFF
    test_mask = table["century"] >= TEMPORAL_CUTOFF
    train_window_safe = table["century"] + HORIZON < TEMPORAL_CUTOFF
    train_index = table.index[train_mask & train_window_safe].to_numpy()
    test_index = table.index[test_mask].to_numpy()
    assert set(train_index).isdisjoint(test_index)
    assert (table.loc[train_index, "century"] + HORIZON < TEMPORAL_CUTOFF).all()
    rows = [
        {"protocol": "temporal", "seed": 0, "fold": 0, "row": index, "partition": "train"}
        for index in train_index
    ]
    rows += [
        {"protocol": "temporal", "seed": 0, "fold": 0, "row": index, "partition": "test"}
        for index in test_index
    ]
    model = make_pipeline(0)
    model.fit(table.loc[train_index, FEATURES], table.loc[train_index, "contraction"])
    probabilities = model.predict_proba(table.loc[test_index, FEATURES])[:, 1]
    predictions = [
        {
            "protocol": "temporal",
            "seed": 0,
            "fold": 0,
            "row": index,
            "y": int(table.loc[index, "contraction"]),
            "p": probability,
        }
        for index, probability in zip(test_index, probabilities)
    ]
    return rows, predictions


def print_metrics(predictions: pd.DataFrame) -> None:
    for protocol, values in predictions.groupby("protocol"):
        y_true = values["y"]
        probabilities = values["p"]
        predictions_at_half = (probabilities >= 0.5).astype(int)
        print(f"{protocol}: n={len(values)}, positives={int(y_true.sum())}")
        print(
            "  precision={:.4f}, recall={:.4f}, PR-AUC={:.4f}".format(
                precision_score(y_true, predictions_at_half, zero_division=0),
                recall_score(y_true, predictions_at_half, zero_division=0),
                average_precision_score(y_true, probabilities),
            )
        )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    table = pd.read_parquet(root / "data" / "table.parquet").reset_index(drop=True)
    split_rows, grouped_predictions = grouped_splits(table)
    temporal_rows, temporal_predictions = temporal_split(table)
    pd.DataFrame(split_rows + temporal_rows).to_csv(root / "data" / "splits.csv", index=False)
    predictions = pd.DataFrame(grouped_predictions + temporal_predictions)
    predictions.to_csv(root / "data" / "split_predictions.csv", index=False)
    print_metrics(predictions)
    print(f"saved: {root / 'data' / 'splits.csv'}")
    print(f"saved: {root / 'data' / 'split_predictions.csv'}")
    print(
        f"temporal cutoff: {TEMPORAL_CUTOFF}; training rows with century + {HORIZON} "
        "at or beyond the cutoff were removed."
    )
    print("assumption: the existing 100-year label window is the temporal leakage boundary.")
    print("caution: only 6 positive labels exist, so repeated-fold metrics are unstable.")


if __name__ == "__main__":
    main()