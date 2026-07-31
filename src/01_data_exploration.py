from pathlib import Path

import pandas as pd


# =============================================================================
# FILE PATHS
# =============================================================================

# Locate the project root regardless of where the script is executed from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "yellow_tripdata_2026-03.parquet"
)


# =============================================================================
# LOAD RAW DATA
# =============================================================================

print("=" * 80)
print("LOADING RAW DATA")
print("=" * 80)

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{DATA_FILE}\n\n"
        "Confirm that the March Parquet file is stored in data/raw."
    )

df = pd.read_parquet(DATA_FILE)

print(f"Loaded file: {DATA_FILE.name}")


# =============================================================================
# DATASET OVERVIEW
# =============================================================================

print("\n" + "=" * 80)
print("DATASET SHAPE")
print("=" * 80)

print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]}")


print("\n" + "=" * 80)
print("FIRST FIVE ROWS")
print("=" * 80)

print(df.head())


print("\n" + "=" * 80)
print("COLUMN NAMES")
print("=" * 80)

for position, column in enumerate(df.columns, start=1):
    print(f"{position:>2}. {column}")


print("\n" + "=" * 80)
print("DATA TYPES")
print("=" * 80)

print(df.dtypes)


print("\n" + "=" * 80)
print("DATAFRAME INFORMATION")
print("=" * 80)

df.info(show_counts=True)


# =============================================================================
# DATE COVERAGE
# =============================================================================

print("\n" + "=" * 80)
print("DATE COVERAGE")
print("=" * 80)

print(
    "Pickup datetime:",
    df["tpep_pickup_datetime"].min(),
    "to",
    df["tpep_pickup_datetime"].max(),
)

print(
    "Drop-off datetime:",
    df["tpep_dropoff_datetime"].min(),
    "to",
    df["tpep_dropoff_datetime"].max(),
)


# =============================================================================
# MISSING VALUES
# =============================================================================

print("\n" + "=" * 80)
print("MISSING VALUES")
print("=" * 80)

missing_summary = pd.DataFrame(
    {
        "missing_count": df.isna().sum(),
        "missing_percentage": df.isna().mean() * 100,
    }
)

missing_summary = missing_summary[
    missing_summary["missing_count"] > 0
].sort_values(
    by="missing_count",
    ascending=False,
)

if missing_summary.empty:
    print("No missing values found.")
else:
    print(missing_summary.round(2))


# =============================================================================
# DUPLICATE ROWS
# =============================================================================

print("\n" + "=" * 80)
print("DUPLICATE ROWS")
print("=" * 80)

duplicate_count = df.duplicated().sum()
duplicate_percentage = duplicate_count / len(df) * 100

print(f"Exact duplicate rows: {duplicate_count:,}")
print(f"Duplicate percentage: {duplicate_percentage:.4f}%")


# =============================================================================
# CATEGORICAL COLUMN PROFILES
# =============================================================================

print("\n" + "=" * 80)
print("CATEGORICAL COLUMN PROFILES")
print("=" * 80)

categorical_columns = [
    "VendorID",
    "RatecodeID",
    "store_and_fwd_flag",
    "payment_type",
]

for column in categorical_columns:
    print("\n" + "-" * 80)
    print(column)
    print("-" * 80)

    counts = df[column].value_counts(dropna=False)
    percentages = (
        df[column]
        .value_counts(dropna=False, normalize=True)
        .mul(100)
    )

    categorical_profile = pd.DataFrame(
        {
            "count": counts,
            "percentage": percentages,
        }
    )

    print(categorical_profile.round(2))


# =============================================================================
# NUMERICAL SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("NUMERICAL SUMMARY")
print("=" * 80)

numerical_columns = [
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "Airport_fee",
    "cbd_congestion_fee",
]

numerical_summary = df[numerical_columns].describe().T

print(numerical_summary)


# =============================================================================
# EXPLORATION COMPLETE
# =============================================================================

print("\n" + "=" * 80)
print("DATA EXPLORATION COMPLETED")
print("=" * 80)