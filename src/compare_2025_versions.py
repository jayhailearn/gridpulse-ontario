
# GridPulse - Stage 3E.2
# Compare official 2025 IESO demand reports

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

files = {
    "Original": "PUB_Demand_2025.csv",
    "Versioned": "PUB_Demand_2025_v396.csv"
}

datasets = {}

for label, filename in files.items():

    file_path = RAW_DIR / filename

    df = pd.read_csv(file_path, skiprows=3)

    df["Date"] = pd.to_datetime(df["Date"])

    datasets[label] = df

    # Check whether May 1, hour ending 1 exists
    record = df[
        (df["Date"] == pd.Timestamp("2025-05-01"))
        & (df["Hour"] == 1)
    ]

    print(f"\n{'=' * 50}")
    print(f"{label.upper()} REPORT")
    print(f"{'=' * 50}")

    print("Filename:", filename)
    print("Total records:", len(df))
    print("Duplicate date-hour records:",
          df.duplicated(["Date", "Hour"]).sum())

    print("\nMay 1, 2025 - Hour Ending 1:")

    if record.empty:
        print("NOT FOUND")
    else:
        print(record.to_string(index=False))

# Compare the two files by date and hour
comparison = datasets["Original"].merge(
    datasets["Versioned"],
    on=["Date", "Hour"],
    how="outer",
    suffixes=("_original", "_versioned"),
    indicator=True,
    validate="one_to_one"
)

print("\n" + "=" * 50)
print("CROSS-VERSION COMPARISON")
print("=" * 50)

print("\nRecord availability:")
print(comparison["_merge"].value_counts())

# Find demand values changed between versions
both = comparison[
    comparison["_merge"] == "both"
].copy()

changed = both[
    (both["Ontario Demand_original"]
     != both["Ontario Demand_versioned"])
    |
    (both["Market Demand_original"]
     != both["Market Demand_versioned"])
]

print("\nRecords with changed demand measurements:",
      len(changed))

if not changed.empty:
    print("\nFirst 10 changed records:")
    print(changed.head(10).to_string(index=False))

print("\nComparison complete.")
print("Original source files remain unchanged.")
