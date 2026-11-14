# GridPulse - Initial Electricity Demand Data Inspection
# Stage 3B: Loading and understanding the raw IESO dataset

from pathlib import Path
import pandas as pd

# Step 1: Identify the project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#Step 2: Construct the dataset path
file_path = PROJECT_ROOT / "data" / "raw" / "PUB_Demand_2023.csv"

#Step 3: Load the CSV, skipping the first three metadata rows
df = pd.read_csv(file_path, skiprows=3)

#Step 4: Display the first five records
print("\nFIRST FIVE ROWS:")
print(df.head())

#Step 5: Display the dataset dimensions
print("\nDATASET SHAPE:")
print(df.shape)

#Step 6: Display column names
print("\nCOLUMN NAMES:")
print(df.columns.tolist())

#Step 7: Inspect data types
print("\nDATA TYPES:")
print(df.dtypes)

#Step 8: Display a structural summary
print("\nDATAFRAME INFORMATION:")
df.info()