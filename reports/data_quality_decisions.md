# GridPulse — Data Quality and Processing Decisions

## Decision 001: Missing Hourly Demand Observation

**Dataset:** IESO Historical Hourly Demand, 2023–2025

**Issue identified:** The 2025 dataset contains 8,759 records instead of the expected 8,760.

**Affected observation:** May 1, 2025, Hour Ending 01.

**Investigation:** Both `PUB_Demand_2025.csv` and `PUB_Demand_2025_v396.csv` were examined. Neither contained the missing observation. All 8,759 shared date-hour records had identical demand measurements.

**Decision:** Restore the missing date-hour identifier in the processed dataset while leaving Ontario Demand and Market Demand as missing values.

**Implementation:** Use a complete date-hour index and introduce an `is_missing_source_record` indicator.

**Rationale:** Preserve chronological integrity without presenting an estimated measurement as an observation. This also prevents row-position shifts from silently misaligning later lag features.

**Remaining consideration:** Evaluate how the missing value affects forecasting features and model evaluation. Do not impute the value or use it as ground truth without further justification.

**Source:** Independent Electricity System Operator, historical hourly demand reports.

**Status:** Implemented and validated.

**Validation outcome:** The consolidated dataset contains 26,304 chronological date-hour records, including 26,303 original observations and one explicitly marked missing-source record. The original demand values were retained without imputation.

**Processed dataset:** `data/processed/ontario_demand_2023_2025.csv`

**Reproducible scripts:**
- `src/build_demand_dataset.py`
- `src/validate_processed_data.py`

**Remaining limitations:** Hour-ending and timezone alignment must be resolved before merging with weather data. The missing demand observation has not been estimated or recovered.