
# GridPulse - Stage 3F
# Validate the processed demand dataset after saving it

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

file_path = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ontario_demand_2023_2025.csv"
)

# Load the processed dataset
df = pd.read_csv(
    file_path,
    parse_dates=["Date"],
    dtype={
        "Hour": "int64",
        "Market Demand": "Int64",
        "Ontario Demand": "Int64",
        "is_missing_source_record": "boolean"
    }
)

print("\nPROCESSED DATA VALIDATION")
print("=" * 50)

# 1. Verify dataset dimensions
assert len(df) == 26304
print("Row count: PASS")

# 2. Verify unique date-hour combinations
assert not df[["Date", "Hour"]].duplicated().any()
print("Unique date-hour keys: PASS")

# 3. Verify chronological ordering
ordered = df.sort_values(
    ["Date", "Hour"]
).reset_index(drop=True)

assert df.equals(ordered)
print("Chronological ordering: PASS")

# 4. Verify expected coverage
expected_dates = pd.date_range(
    "2023-01-01",
    "2025-12-31",
    freq="D"
)

expected_index = pd.MultiIndex.from_product(
    [expected_dates, range(1, 25)],
    names=["Date", "Hour"]
)

actual_index = pd.MultiIndex.from_frame(
    df[["Date", "Hour"]]
)

assert expected_index.equals(actual_index)
print("Hourly coverage: PASS")

# 5. Verify missing-source records
missing = df[df["is_missing_source_record"]]

assert len(missing) == 1
assert missing.iloc[0]["Date"] == pd.Timestamp("2025-05-01")
assert missing.iloc[0]["Hour"] == 1

assert missing[
    ["Market Demand", "Ontario Demand"]
].isna().all().all()

print("Missing-source identification: PASS")

# 6. Verify all observed demand values
observed = df[~df["is_missing_source_record"]]

assert observed[
    ["Market Demand", "Ontario Demand"]
].notna().all().all()

print("Observed demand completeness: PASS")

print("\nALL VALIDATION CHECKS PASSED")
print("Records:", len(df))
print("Original observations:", len(observed))
print("Missing source observations:", len(missing))
print("\nData types:")
print(df.dtypes)
