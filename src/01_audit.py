from pathlib import Path

import numpy as np
import pandas as pd


SEED = 0
SHEET = "AggrSCWarAgriRelig"
FEATURES = ["Pop", "Cap", "Hier", "Gov", "Infra", "Info", "Money"]
KEYS = ["NGA", "PolID", "Time"]


def load_source(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name=SHEET)
    frame = frame.replace(-999, np.nan)
    before = len(frame)
    if "uniq" in frame.columns:
        frame = frame[frame["uniq"].astype(str).str.lower().ne("n")].copy()
    print(f"source sheet: {SHEET}")
    print(f"rows before filler removal: {before}")
    print(f"rows after filler removal: {len(frame)}")
    return frame


def print_audit(frame: pd.DataFrame) -> None:
    print(f"shape: {frame.shape}")
    print("dtypes:")
    print(frame.dtypes.to_string())
    missing = frame.isna().mean().sort_values(ascending=False)
    print("missing rate per column:")
    print(missing.to_string())

    terr = pd.to_numeric(frame["Terr"], errors="coerce").dropna()
    print(f"Terr non-missing range: {terr.min()} to {terr.max()}")
    print("Terr interpretation: values are consistent with log10 territory area;")
    print("the 30% contraction threshold is log10(0.7) = "
          f"{np.log10(0.7):.6f}, not -0.30.")

    times = pd.to_numeric(frame["Time"], errors="coerce").dropna().drop_duplicates().sort_values()
    spacing = times.diff().dropna()
    print(f"time points: {len(times)}; spacing counts:")
    print(spacing.value_counts().sort_index().to_string())
    if len(spacing) and spacing.eq(100).all():
        print("century spacing: regular 100-year steps")
    else:
        print("century spacing: irregular or not exclusively 100-year steps")


def compute_labels(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame[["NGA", "PolID", "Time", "Terr"]].copy()
    work["Time"] = pd.to_numeric(work["Time"], errors="coerce")
    work["Terr"] = pd.to_numeric(work["Terr"], errors="coerce")
    future = work[["NGA", "PolID", "Time", "Terr"]].rename(
        columns={"Time": "next_time", "Terr": "next_terr"}
    )
    work["next_time"] = work["Time"] + 100
    work = work.merge(future, on=["NGA", "PolID", "next_time"], how="left")
    work["terr_change"] = work["next_terr"] - work["Terr"]
    work["contraction"] = (work["terr_change"] <= np.log10(0.7)).astype("Int64")
    labeled = work.dropna(subset=["Terr", "next_terr"]).copy()
    labeled["contraction"] = (labeled["terr_change"] <= np.log10(0.7)).astype(int)
    print(f"labeled rows with observed next-century Terr: {len(labeled)}")
    print("class counts:")
    print(labeled["contraction"].value_counts().sort_index().rename(index={0: "0", 1: "1"}).to_string())
    positives = int(labeled["contraction"].sum())
    print(f"positive count: {positives}")
    if positives < 30:
        print("GATE: fewer than 30 positives; stop and consider CrisisDB crisis-onset labels.")
    else:
        print("GATE: passed; proceed with the Equinox contraction label.")
    return labeled


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "data" / "raw" / "Equinox_on_GitHub_June9_2022.xlsx"
    frame = load_source(source)
    print_audit(frame)
    compute_labels(frame)
    print(f"features for later steps: {', '.join(FEATURES)}")
    print("assumptions: (NGA, PolID) is the polity key; Time is in years; label horizon is +100 years.")


if __name__ == "__main__":
    main()