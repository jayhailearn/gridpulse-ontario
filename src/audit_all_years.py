
# GridPulse - Stage 3D
# Multi-year electricity demand data-quality audit

from pathlib import Path
import calendar
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

YEARS = [2023, 2024, 2025]

EXPECTED_COLUMNS = [
    "Date",
    "Hour",
    "Market Demand",
    "Ontario Demand"
]

audit_results = []

for year in YEARS:

    print(f"\n{'=' * 55}")
    print(f"DATA QUALITY AUDIT: {year}")
    print(f"{'=' * 55}")

    file_path = RAW_DATA_DIR / f"PUB_Demand_{year}.csv"

    # Load the annual dataset
    df = pd.read_csv(file_path, skiprows=3)

    # Check whether the expected columns exist
    schema_valid = df.columns.tolist() == EXPECTED_COLUMNS

    if not schema_valid:
        raise ValueError(
            f"Unexpected columns in {year}: {df.columns.tolist()}"
        )

    # Convert dates and numerical columns
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for column in ["Hour", "Market Demand", "Ontario Demand"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # General quality checks
    missing_values = int(df.isna().sum().sum())

    duplicates = int(
        df.duplicated(subset=["Date", "Hour"]).sum()
    )

    invalid_hours = int(
        (df["Hour"].notna() & ~df["Hour"].between(1, 24)).sum()
    )

    non_positive = int(
        (df["Ontario Demand"].notna() &
         (df["Ontario Demand"] <= 0)).sum()
    )

    # Generate expected date-hour combinations
    expected_dates = pd.date_range(
        start=f"{year}-01-01",
        end=f"{year}-12-31",
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

    expected_rows = len(expected_index)
    actual_rows = len(df)

    # Summary statistics
    mean_demand = df["Ontario Demand"].mean()
    min_demand = df["Ontario Demand"].min()
    max_demand = df["Ontario Demand"].max()

    # Final preliminary audit decision
    passed = (
        schema_valid
        and missing_values == 0
        and duplicates == 0
        and invalid_hours == 0
        and non_positive == 0
        and len(missing_hours) == 0
        and len(unexpected_hours) == 0
        and actual_rows == expected_rows
    )

    print("Leap year:", calendar.isleap(year))
    print("Expected records:", expected_rows)
    print("Actual records:", actual_rows)
    print("Missing values:", missing_values)
    print("Duplicate date-hour records:", duplicates)
    print("Invalid hours:", invalid_hours)
    print("Non-positive Ontario demand:", non_positive)
    print("Missing date-hour combinations:", len(missing_hours))
    print("Unexpected date-hour combinations:", len(unexpected_hours))

    print(f"Mean demand: {mean_demand:,.2f} MW")
    print(f"Minimum demand: {min_demand:,.0f} MW")
    print(f"Maximum demand: {max_demand:,.0f} MW")

    print("Preliminary audit:", "PASS" if passed else "REVIEW")

    # Store the results
    audit_results.append({
        "Year": year,
        "Expected Records": expected_rows,
        "Actual Records": actual_rows,
        "Missing Values": missing_values,
        "Duplicates": duplicates,
        "Missing Hours": len(missing_hours),
        "Unexpected Hours": len(unexpected_hours),
        "Invalid Hours": invalid_hours,
        "Non-Positive Demand": non_positive,
        "Mean Demand (MW)": round(mean_demand, 2),
        "Minimum Demand (MW)": min_demand,
        "Maximum Demand (MW)": max_demand,
        "Audit Status": "PASS" if passed else "REVIEW"
    })

# Create a consolidated summary table
audit_summary = pd.DataFrame(audit_results)

print("\n" + "=" * 55)
print("CONSOLIDATED AUDIT SUMMARY")
print("=" * 55)
print(audit_summary.to_string(index=False))

print("\nTotal records:", audit_summary["Actual Records"].sum())
