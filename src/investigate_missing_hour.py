
# GridPulse - Stage 3E.1
# Investigating the missing date-hour combination in 2025

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

file_path = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "PUB_Demand_2025.csv"
)

# Load source data
df = pd.read_csv(file_path, skiprows=3)

df["Date"] = pd.to_datetime(df["Date"])

# Generate every expected date-hour combination
expected_dates = pd.date_range(
    start="2025-01-01",
    end="2025-12-31",
    freq="D"
)

expected_index = pd.MultiIndex.from_product(
    [expected_dates, range(1, 25)],
    names=["Date", "Hour"]
)

actual_index = pd.MultiIndex.from_frame(
    df[["Date", "Hour"]]
)

# Identify missing records
missing = expected_index.difference(actual_index)

print("\nMISSING DATE-HOUR COMBINATIONS")
print(missing)

# Show records around each missing hour
for date, hour in missing:

    print("\n" + "=" * 50)
    print("MISSING OBSERVATION")
    print("=" * 50)

    print("Date:", date.date())
    print("Hour:", hour)

    # Examine all records on the affected date
    day_records = df[df["Date"] == date].copy()

    print("\nALL RECORDS ON AFFECTED DATE:")
    print(day_records.to_string(index=False))

    print("\nNUMBER OF RECORDS ON THIS DATE:")
    print(len(day_records))

    print("\nAVAILABLE HOURS:")
    print(sorted(day_records["Hour"].tolist()))

    # Display nearby rows in the original sequence
    print("\nNEIGHBOURING RECORDS:")

    position = expected_index.get_loc((date, hour))

    nearby_keys = expected_index[
        max(0, position - 3): position + 4
    ]

    nearby_index = pd.MultiIndex.from_frame(
        df[["Date", "Hour"]]
    )

    nearby = df[nearby_index.isin(nearby_keys)]

    print(nearby.to_string(index=False))

# Inspect daylight-saving transition dates
print("\n" + "=" * 50)
print("DAYLIGHT SAVING TIME INVESTIGATION")
print("=" * 50)

dst_dates = ["2025-03-09", "2025-11-02"]

for date_string in dst_dates:

    date = pd.Timestamp(date_string)

    records = df[df["Date"] == date]

    print(f"\nDate: {date_string}")
    print("Number of records:", len(records))
    print("Hours:", sorted(records["Hour"].tolist()))
