# GridPulse - Stage 3C
# Initial data-quality assessment for 2023 IESO demand data

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
file_path = PROJECT_ROOT / "data" / "raw" / "PUB_Demand_2023.csv"

#Load the original dataset
df = pd.read_csv(file_path, skiprows = 3)

#Convert dates for validation and time-series analysis
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# 1. Missing Values
print("\n1. MISSING VALUES")
print(df.isna().sum())

# 2. Duplicate date-hour combinations
print("\n2. DUPLICATE DATE-HOUR RECORDS")
duplicate_count = df.duplicated(
    subset=["Date", "Hour"]
).sum()
print("Duplicates:", duplicate_count)

# 3. Date range
print("\n3. DATE COVERAGE")
print("First date:", df["Date"].min())
print("Last date:", df["Date"].max())
print("Unique dates:", df["Date"].nunique())

# 4. Hour validity
print("\n4. HOUR VALIDITY")
print("Minimum hour:", df["Hour"].min())
print("Maximum hour:", df["Hour"].max())

invalid_hours = (~df["Hour"].between(1,24)).sum()
print("Invalid hours:", invalid_hours)

# 5. Demand statistics
print("\n5. ONTARIO DEMAND STATISTICS (MW)")
print(df["Ontario Demand"].describe())

#6. Zero or negative values
print("\n6. NON-POSITIVE DEMAND VALUES")
non_positive = (df["Ontario Demand"] <= 0).sum()
print("Count:", non_positive)

#7. Check expected hourly coverage
print("\n7. EXPECTED HOURLY COVERAGE")

expected_dates = pd.date_range(
    start="2023-01-01",
    end="2023-12-31",
    freq="D"
)

expected_index = pd.MultiIndex.from_product(
    [expected_dates, range(1, 25)],
    names=["Date", "Hour"]
)

actual_index = pd.MultiIndex.from_frame(
    df[["Date", "Hour"]]
)

missing_hours = expected_index.difference(actual_index)
unexpected_hours = actual_index.difference(expected_index)

print("Expected hourly records:", len(expected_index))
print("Actual records:", len(df))
print("Missing date-hour combinations:", len(missing_hours))
print("Unexpected date-hour combinations:", len(unexpected_hours))

if len(missing_hours) > 0:
    print("\nFirst missing combinations:")
    print(missing_hours[:10])

if len(unexpected_hours) > 0:
    print("\nFirst unexpected combinations:")
    print(unexpected_hours[:10])
