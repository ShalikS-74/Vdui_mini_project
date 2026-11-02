from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
BASE_FEATURES = ["Pop", "Cap", "Hier", "Gov", "Infra", "Info", "Money"]
FEATURES = BASE_FEATURES + [f"{feature}_delta" for feature in BASE_FEATURES]


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    table = pd.read_parquet(ROOT / "data" / "table.parquet")
    cases = pd.read_csv(ROOT / "data" / "fp_cases.csv", keep_default_na=False)
    ranking = pd.read_csv(ROOT / "data" / "fp_feature_ranking.csv")
    return table, cases, ranking


@st.cache_resource
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


def contribution_frame(model: Pipeline, values: pd.DataFrame) -> pd.DataFrame:
    imputed = model.named_steps["imp"].transform(values[FEATURES])
    standardized = model.named_steps["sc"].transform(imputed)
    coefficients = model.named_steps["lr"].coef_[0]
    return pd.DataFrame(standardized * coefficients, columns=FEATURES, index=values.index)


def show_polity_browser(table: pd.DataFrame) -> None:
    st.header("Polity browser")
    polity = st.selectbox("Polity", sorted(table["polity"].unique()))
    history = table[table["polity"].eq(polity)].sort_values("century")
    st.line_chart(history.set_index("century")[BASE_FEATURES])
    st.caption(f"{len(history)} observed centuries for {polity}")


def show_fp_explorer(table: pd.DataFrame, cases: pd.DataFrame, ranking: pd.DataFrame, model: Pipeline) -> None:
    st.header("False-positive explorer")
    st.dataframe(ranking, hide_index=True, use_container_width=True)
    case_labels = [f"{row.polity} @ {row.century}" for row in cases.itertuples()]
    selected_label = st.selectbox("Case", case_labels)
    selected_case = cases.iloc[case_labels.index(selected_label)]
    row = table[(table["polity"] == selected_case.polity) & (table["century"] == selected_case.century)]
    contributions = contribution_frame(model, row).T.rename(columns={row.index[0]: "contribution"})
    contributions["absolute"] = contributions["contribution"].abs()
    contributions = contributions.sort_values("absolute", ascending=False).drop(columns="absolute")
    st.bar_chart(contributions)
    st.write(f"OOF probability: {selected_case.oof_p_decline:.3f}")
    st.write(f"Manual type: {selected_case.type or 'not reviewed'}")
    st.write(f"Note: {selected_case.note or 'not reviewed'}")


def show_what_if(table: pd.DataFrame, cases: pd.DataFrame, model: Pipeline) -> None:
    st.header("What-if")
    st.caption("Illustrative, not causal")
    case_labels = [f"{row.polity} @ {row.century}" for row in cases.itertuples()]
    selected_label = st.selectbox("Starting case", case_labels, key="what_if_case")
    selected_case = cases.iloc[case_labels.index(selected_label)]
    base = table[(table["polity"] == selected_case.polity) & (table["century"] == selected_case.century)].iloc[0]
    values = {}
    for start in range(0, len(FEATURES), 2):
        columns = st.columns(2)
        for column, feature in zip(columns, FEATURES[start:start + 2]):
            current = float(base[feature]) if pd.notna(base[feature]) else 0.0
            series = table[feature].dropna()
            lower, upper = float(series.min()), float(series.max())
            if lower == upper:
                lower -= 1.0
                upper += 1.0
            values[feature] = column.slider(feature, lower, upper, min(max(current, lower), upper), key=f"what_if_{feature}")
    probability = model.predict_proba(pd.DataFrame([values], columns=FEATURES))[0, 1]
    st.metric("Illustrative contraction probability", f"{probability:.3f}")


def main() -> None:
    st.set_page_config(page_title="Equinox contraction model", layout="wide")
    st.title("Equinox historical contraction model")
    table, cases, ranking = load_data()
    model = fit_model(table)
    show_polity_browser(table)
    show_fp_explorer(table, cases, ranking, model)
    show_what_if(table, cases, model)


if __name__ == "__main__":
    main()