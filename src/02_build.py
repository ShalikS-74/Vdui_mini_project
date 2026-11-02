from pathlib import Path

import numpy as np
import pandas as pd


SHEET = "AggrSCWarAgriRelig"
KEYS = ["NGA", "PolID", "Time"]
FEATURES = ["Pop", "Cap", "Hier", "Gov", "Infra", "Info", "Money"]
HORIZON = 100
CONTRACTION_THRESHOLD = np.log10(0.7)


def load_equinoxtable(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name=SHEET).replace(-999, np.nan)
    if "uniq" in frame.columns:
        frame = frame[frame["uniq"].astype(str).str.lower().ne("n")].copy()
    frame["Time"] = pd.to_numeric(frame["Time"], errors="coerce")
    for column in FEATURES + ["Terr"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.sort_values(["PolID", "Time"]).reset_index(drop=True)


def build_table(frame: pd.DataFrame) -> pd.DataFrame:
    current = frame[KEYS + FEATURES + ["Terr"]].copy()
    future = current[["NGA", "PolID", "Time", "Terr"]].rename(
        columns={"Time": "next_time", "Terr": "next_Terr"}
    )
    labeled = current.assign(next_time=current["Time"] + HORIZON).merge(
        future, on=["NGA", "PolID", "next_time"], how="left"
    )
    labeled["terr_change"] = labeled["next_Terr"] - labeled["Terr"]
    labeled["y"] = (labeled["terr_change"] <= CONTRACTION_THRESHOLD).astype("Int64")

    deltas = current[["NGA", "PolID", "Time"] + FEATURES].copy()
    deltas["Time"] = deltas["Time"] + HORIZON
    deltas = deltas.rename(columns={column: f"{column}_prev" for column in FEATURES})
    labeled = labeled.merge(deltas, on=["NGA", "PolID", "Time"], how="left")
    for feature in FEATURES:
        labeled[f"{feature}_delta"] = labeled[feature] - labeled[f"{feature}_prev"]

    table = labeled.dropna(subset=["Terr", "next_Terr", "y"]).copy()
    table["contraction"] = table["y"].astype(int)
    output_columns = ["NGA", "PolID", "Time", "contraction"]
    output_columns += FEATURES + [f"{feature}_delta" for feature in FEATURES]
    table = table[output_columns].rename(columns={"Time": "century"})
    table["polity"] = table["NGA"] + "::" + table["PolID"]
    table = table.drop(columns=["PolID"]).rename(columns={"NGA": "nga"})
    table = table[["nga", "polity", "century", "contraction"] + FEATURES + [
        f"{feature}_delta" for feature in FEATURES
    ]]
    return table.sort_values(["polity", "century"]).reset_index(drop=True)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "data" / "raw" / "Equinox_on_GitHub_June9_2022.xlsx"
    output = root / "data" / "table.parquet"
    output.parent.mkdir(parents=True, exist_ok=True)

    frame = load_equinoxtable(source)
    table = build_table(frame)
    table.to_parquet(output, index=False)
    print(f"saved: {output}")
    print(f"table shape: {table.shape}")
    print("class counts:")
    print(table["contraction"].value_counts().sort_index().to_string())
    print("features: current values plus first differences from the previous observed century")
    print("assumptions: exact +100-year matches are required; missing labels are censored and dropped;")
    print("Terr is log10-scaled, so contraction uses next Terr - current Terr <= log10(0.7).")


if __name__ == "__main__":
    main()