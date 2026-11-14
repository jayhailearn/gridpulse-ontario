
# GridPulse - Stage 3E.3
# Build a validated hourly Ontario demand dataset: 2023-2025

from pathlib import Path
import pandas as pd

# --------------------------------------------------
# 1. Define project paths and expected schema
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

YEARS = [2023, 2024, 2025]

COLUMNS = [
    "Date",
    "Hour",
    "Market Demand",
    "Ontario Demand"
]

# --------------------------------------------------
# 2. Load the annual files
# --------------------------------------------------

annual_data = []

for year in YEARS:

    file_path = RAW_DIR / f"PUB_Demand_{year}.csv"

    df = pd.read_csv(file_path, skiprows=3)

    if df.columns.tolist() != COLUMNS:
        raise ValueError(f"Unexpected schema in {year}")

    df["Date"] = pd.to_datetime(
        df["Date"], errors="raise"
    )

    for col in ["Hour", "Market Demand", "Ontario Demand"]:
        df[col] = pd.to_numeric(df[col], errors="raise")

    if not df["Hour"].between(1, 24).all():
        raise ValueError(f"Invalid hour identifiers in {year}")

    if df[["Date", "Hour"]].duplicated().any():
        raise ValueError(f"Duplicate date-hour keys in {year}")

    if not df["Date"].dt.year.eq(year).all():
        raise ValueError(f"Unexpected dates in {year}")

    annual_data.append(df)

    print(f"Loaded {year}: {len(df):,} records")

# --------------------------------------------------
# 3. Concatenate all three datasets
# --------------------------------------------------

combined = pd.concat(
    annual_data,
    ignore_index=True
)

combined = combined.sort_values(
    ["Date", "Hour"]
).reset_index(drop=True)

assert len(combined) == 26303
assert not combined[["Date", "Hour"]].duplicated().any()
assert not combined[COLUMNS].isna().any().any()

print("\nOriginal combined records:", len(combined))

# --------------------------------------------------
# 4. Create the expected hourly index
# --------------------------------------------------

expected_dates = pd.date_range(
    start="2023-01-01",
    end="2025-12-31",
    freq="D"
)

expected_index = pd.MultiIndex.from_product(
    [expected_dates, range(1, 25)],
    names=["Date", "Hour"]
)

# Mark observations actually present in the source
combined["source_present"] = True

# Index by date and hour, then restore missing keys
complete = (
    combined
    .set_index(["Date", "Hour"])
    .reindex(expected_index)
    .reset_index()
)

# --------------------------------------------------
# 5. Create missing-source flag
# --------------------------------------------------

complete["is_missing_source_record"] = (
    complete["source_present"].isna()
)

complete = complete.drop(columns=["source_present"])

# Preserve whole-number demand measurements
for col in ["Market Demand", "Ontario Demand"]:
    complete[col] = complete[col].astype("Int64")

# --------------------------------------------------
# 6. Validate the resulting dataset
# --------------------------------------------------

assert len(complete) == 26304

assert not complete[["Date", "Hour"]].duplicated().any()

assert complete["is_missing_source_record"].sum() == 1

missing_record = complete[
    complete["is_missing_source_record"]
]

assert missing_record.iloc[0]["Date"] == pd.Timestamp(
    "2025-05-01"
)

assert missing_record.iloc[0]["Hour"] == 1

assert missing_record[
    ["Market Demand", "Ontario Demand"]
].isna().all().all()

# --------------------------------------------------
# 7. Save processed data
# --------------------------------------------------

output_path = (
    PROCESSED_DIR / "ontario_demand_2023_2025.csv"
)

complete.to_csv(output_path, index=False)

print("\nDATASET VALIDATION COMPLETE")
print("Total rows:", len(complete))
print(
    "Missing source records:",
    complete["is_missing_source_record"].sum()
)

print("\nMissing observation:")
print(missing_record.to_string(index=False))

print("\nOutput file:")
print(output_path)

print("\nFirst five rows:")
print(complete.head().to_string(index=False))

print("\nLast five rows:")
print(complete.tail().to_string(index=False))
