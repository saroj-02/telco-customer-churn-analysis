"""
Task 1 - Data cleaning script (Telco Customer Churn).
Run from project root:  python scripts/clean_data.py
Reads  data/raw/Telco-Customer-Churn.csv
Writes data/processed/telco_churn_clean.csv and reports/cleaning_log.md
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
OUT = ROOT / "data" / "processed" / "telco_churn_clean.csv"
LOG = ROOT / "reports" / "cleaning_log.md"


def to_snake(name: str) -> str:
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name.strip())
    return re.sub(r"\W+", "_", name).lower().strip("_")


def main() -> None:
    log = []
    df = pd.read_csv(RAW)
    log.append(f"Loaded raw data: {df.shape[0]} rows x {df.shape[1]} columns")

    # 1. Standardize column names
    df.columns = [to_snake(c) for c in df.columns]
    log.append("Renamed columns to snake_case")

    # 2. Fix data types (TotalCharges arrives as text with blank strings)
    df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
    log.append("Converted total_charges from text to numeric (blanks -> NaN)")

    # 3. Missing values
    n_missing = int(df["total_charges"].isna().sum())
    log.append(f"Missing values found: {df.isna().sum()[df.isna().sum() > 0].to_dict() or 'none'}")
    if n_missing:
        # Blank TotalCharges belong to brand-new customers (tenure = 0) -> nothing billed yet
        mask = df["total_charges"].isna() & (df["tenure"] == 0)
        df.loc[mask, "total_charges"] = 0.0
        log.append(f"Filled {int(mask.sum())} total_charges blanks with 0 (customers with tenure 0)")
        remaining = int(df["total_charges"].isna().sum())
        if remaining:
            med = df["total_charges"].median()
            df["total_charges"] = df["total_charges"].fillna(med)
            log.append(f"Filled {remaining} remaining total_charges with median ({med:.2f})")

    # 4. Duplicates
    dups = int(df.duplicated().sum())
    df = df.drop_duplicates()
    id_dups = int(df.duplicated(subset="customer_id").sum())
    df = df.drop_duplicates(subset="customer_id")
    log.append(f"Removed {dups} fully duplicated rows and {id_dups} duplicate customer_ids")

    # 5. Typing
    df["senior_citizen"] = df["senior_citizen"].map({0: "No", 1: "Yes"})
    cat_cols = [c for c in df.columns if c not in ("customer_id", "tenure", "monthly_charges", "total_charges")]
    df[cat_cols] = df[cat_cols].astype("category")
    df["churn_flag"] = (df["churn"] == "Yes").astype(int)
    log.append("Converted text columns to category; senior_citizen 0/1 -> No/Yes; added churn_flag (1 = churned)")

    # 6. Outliers (IQR) - reported, not deleted (they are valid customers)
    for col in ["tenure", "monthly_charges", "total_charges"]:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n = int(((df[col] < lo) | (df[col] > hi)).sum())
        log.append(f"IQR outlier check on {col}: {n} outliers outside [{lo:.1f}, {hi:.1f}] - kept (valid values)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    log.append(f"Saved cleaned data: {df.shape[0]} rows x {df.shape[1]} columns -> {OUT.relative_to(ROOT)}")

    LOG.write_text("# Cleaning Log\n\n" + "\n".join(f"{i}. {l}" for i, l in enumerate(log, 1)) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
