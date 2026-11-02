from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SEED = 0
FP_QUANTILE = 0.95
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


def standardized_difference(first: pd.Series, second: pd.Series) -> float:
    pooled_sd = np.sqrt((first.var(ddof=1) + second.var(ddof=1)) / 2)
    if not np.isfinite(pooled_sd) or pooled_sd == 0:
        return 0.0
    return float((first.mean() - second.mean()) / pooled_sd)


def contribution_text(contributions: pd.Series) -> str:
    top = contributions.abs().sort_values(ascending=False).head(3).index
    return "; ".join(f"{feature}={contributions[feature]:+.4f}" for feature in top)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    oof = pd.read_csv(root / "data" / "oof.csv")
    table = pd.read_parquet(root / "data" / "table.parquet")
    data = table.merge(oof[["polity", "century", "p"]], on=["polity", "century"])

    cutoff = float(oof["p"].quantile(FP_QUANTILE))
    print(f"FP cutoff fixed before case inspection: p >= {cutoff:.6f} (OOF 95th percentile)")
    data["fp_flag"] = ((data["contraction"] == 0) & (data["p"] >= cutoff)).astype(int)
    data["tp_flag"] = ((data["contraction"] == 1) & (data["p"] >= cutoff)).astype(int)

    x_values = data[FEATURES]
    y_values = data["contraction"].astype(int)
    model = make_pipeline()
    model.fit(x_values, y_values)
    standardized = model.named_steps["sc"].transform(
        model.named_steps["imp"].transform(x_values)
    )
    imputed = model.named_steps["imp"].transform(x_values)
    coefficients = pd.Series(model.named_steps["lr"].coef_[0], index=FEATURES)
    contributions = pd.DataFrame(standardized, columns=FEATURES, index=data.index).mul(coefficients)

    fp_rows = data["fp_flag"].eq(1)
    tp_rows = data["tp_flag"].eq(1)
    comparison_tp_rows = data["contraction"].eq(1)
    rankings = []
    for feature in FEATURES:
        rankings.append(
            {
                "feature": feature,
                "fp_mean": model.named_steps["imp"].transform(x_values[fp_rows]).mean(axis=0)[FEATURES.index(feature)] if fp_rows.any() else np.nan,
                "tp_mean": imputed[comparison_tp_rows].mean(axis=0)[FEATURES.index(feature)] if comparison_tp_rows.any() else np.nan,
                "standardized_difference": standardized_difference(
                    pd.Series(imputed[fp_rows, FEATURES.index(feature)]),
                    pd.Series(imputed[comparison_tp_rows, FEATURES.index(feature)]),
                ) if fp_rows.any() and comparison_tp_rows.any() else np.nan,
                "fp_mean_contribution": contributions.loc[fp_rows, feature].mean() if fp_rows.any() else np.nan,
                "tp_mean_contribution": contributions.loc[comparison_tp_rows, feature].mean() if comparison_tp_rows.any() else np.nan,
            }
        )
    ranking = pd.DataFrame(rankings)
    ranking["contribution_difference"] = ranking["fp_mean_contribution"] - ranking["tp_mean_contribution"]
    ranking["rank_score"] = ranking["contribution_difference"].abs()
    ranking = ranking.sort_values("rank_score", ascending=False).drop(columns="rank_score")
    ranking.to_csv(root / "data" / "fp_feature_ranking.csv", index=False)

    cases = data.loc[fp_rows, ["polity", "century", "p", "contraction"]].copy()
    cases["true_label"] = np.where(cases["contraction"].eq(1), "contraction", "survival")
    cases["fp_flag"] = 1
    cases["top3_coefficient_features"] = [contribution_text(contributions.loc[index]) for index in cases.index]
    cases["note"] = ""
    cases["type"] = ""
    cases = cases.rename(columns={"p": "oof_p_decline"})[
        ["polity", "century", "oof_p_decline", "true_label", "fp_flag", "top3_coefficient_features", "note", "type"]
    ]
    cases.to_csv(root / "data" / "fp_cases.csv", index=False)

    print(f"FP cases: {len(cases)}; TP cases above cutoff: {int(tp_rows.sum())}")
    print(ranking.head(5).to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print(f"saved: {root / 'data' / 'fp_feature_ranking.csv'}")
    print(f"saved: {root / 'data' / 'fp_cases.csv'}")
    print("assumption: coefficient contributions use standardized, median-imputed features from a full-data fit for explanation only;")
    print("case selection remains based exclusively on out-of-fold probabilities.")


if __name__ == "__main__":
    main()