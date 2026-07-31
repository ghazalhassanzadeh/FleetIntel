from pathlib import Path

import pandas as pd


# =============================================================================
# FILE PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# =============================================================================
# LOAD DATA
# =============================================================================

def load_trip_data() -> pd.DataFrame:
    """Load and combine all 2026 Yellow Taxi Parquet files."""

    trip_files = sorted(
        RAW_DATA_DIR.glob("yellow_tripdata_2026-*.parquet")
    )

    if not trip_files:
        raise FileNotFoundError(
            f"No Yellow Taxi Parquet files were found in:\n{RAW_DATA_DIR}"
        )

    print("=" * 80)
    print("INPUT FILES")
    print("=" * 80)

    dataframes = []

    for file_path in trip_files:
        print(file_path.name)

    for file_path in trip_files:
        print(f"\nLoading {file_path.name}...")

        monthly_data = pd.read_parquet(file_path)

        # Preserve the source month for traceability.
        monthly_data["source_file"] = file_path.name

        print(f"Rows loaded: {len(monthly_data):,}")

        dataframes.append(monthly_data)

    raw_df = pd.concat(dataframes, ignore_index=True)

    print("\n" + "=" * 80)
    print("COMBINED RAW DATA")
    print("=" * 80)

    print(f"Total rows: {len(raw_df):,}")
    print(f"Total columns: {raw_df.shape[1]}")
    print(
        "Memory usage: "
        f"{raw_df.memory_usage(deep=True).sum() / 1024**3:.2f} GB"
    )

    return raw_df


# =============================================================================
# DUPLICATE VALIDATION
# =============================================================================

def validate_duplicates(df: pd.DataFrame) -> None:
    """Check for exact duplicate records."""

    print("\n" + "=" * 80)
    print("DATA VALIDATION - DUPLICATE RECORDS")
    print("=" * 80)

    duplicate_count = df.duplicated().sum()
    duplicate_percentage = duplicate_count / len(df) * 100

    print(f"Exact duplicate rows: {duplicate_count:,}")
    print(f"Duplicate percentage: {duplicate_percentage:.4f}%")


# =============================================================================
# TIMESTAMP VALIDATION
# =============================================================================

def validate_timestamps(df: pd.DataFrame) -> None:
    """Validate timestamp order and investigate out-of-period records."""

    print("\n" + "=" * 80)
    print("DATA VALIDATION - TIMESTAMPS")
    print("=" * 80)

    invalid_time_order = (
        df["tpep_pickup_datetime"] >
        df["tpep_dropoff_datetime"]
    )

    invalid_count = invalid_time_order.sum()

    print(f"Trips with pickup after dropoff: {invalid_count:,}")

    print("\nPickup date range:")
    print(df["tpep_pickup_datetime"].min())
    print(df["tpep_pickup_datetime"].max())

    print("\nDrop-off date range:")
    print(df["tpep_dropoff_datetime"].min())
    print(df["tpep_dropoff_datetime"].max())

    print("\nTrips with pickup after drop-off:")
    print(
        df.loc[
            invalid_time_order,
            [
                "tpep_pickup_datetime",
                "tpep_dropoff_datetime",
                "PULocationID",
                "DOLocationID",
                "trip_distance",
                "fare_amount",
                "total_amount",
                "source_file",
            ],
        ]
    )

    old_dates = df[
        df["tpep_pickup_datetime"] < "2026-01-01"
    ]

    print("\nTrips before 2026:")
    print(len(old_dates))
    print(old_dates.head(10))


# =============================================================================
# TRIP DURATION VALIDATION
# =============================================================================

def validate_trip_duration(df: pd.DataFrame) -> pd.Series:
    """Calculate and validate trip duration in minutes."""

    print("\n" + "=" * 80)
    print("DATA VALIDATION - TRIP DURATION")
    print("=" * 80)

    trip_duration = (
        df["tpep_dropoff_datetime"] -
        df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    print(trip_duration.describe())

    print("\nTrips longer than 6 hours:")
    print((trip_duration > 360).sum())

    print("\nTrips shorter than 1 minute:")
    print((trip_duration < 1).sum())

    duration_df = df.assign(
        trip_duration_minutes=trip_duration
    )

    print("\nFive shortest trips:")
    print(
        duration_df.nsmallest(
            5,
            "trip_duration_minutes",
        )[
            [
                "tpep_pickup_datetime",
                "tpep_dropoff_datetime",
                "trip_duration_minutes",
                "trip_distance",
                "fare_amount",
                "total_amount",
                "source_file",
            ]
        ]
    )

    print("\nFive longest trips:")
    print(
        duration_df.nlargest(
            5,
            "trip_duration_minutes",
        )[
            [
                "tpep_pickup_datetime",
                "tpep_dropoff_datetime",
                "trip_duration_minutes",
                "trip_distance",
                "fare_amount",
                "total_amount",
                "source_file",
            ]
        ]
    )

    return trip_duration


# =============================================================================
# TRIP DISTANCE VALIDATION
# =============================================================================

def validate_trip_distance(
    df: pd.DataFrame,
    trip_duration: pd.Series,
) -> None:
    """Validate trip distance and inspect extreme values."""

    print("\n" + "=" * 80)
    print("DATA VALIDATION - TRIP DISTANCE")
    print("=" * 80)

    print(df["trip_distance"].describe())

    negative_distance = (df["trip_distance"] < 0).sum()
    zero_distance = (df["trip_distance"] == 0).sum()

    print(f"\nNegative trip distances: {negative_distance:,}")
    print(f"Zero-distance trips: {zero_distance:,}")

    distance_df = df.assign(
        trip_duration_minutes=trip_duration
    )

    print("\nFive longest trips by distance:")
    print(
        distance_df.nlargest(
            5,
            "trip_distance",
        )[
            [
                "trip_distance",
                "trip_duration_minutes",
                "fare_amount",
                "total_amount",
                "source_file",
            ]
        ]
    )


# =============================================================================
# PASSENGER COUNT VALIDATION
# =============================================================================

def validate_passenger_count(df: pd.DataFrame) -> None:
    """Validate passenger-count values and missing records."""

    print("\n" + "=" * 80)
    print("DATA VALIDATION - PASSENGER COUNT")
    print("=" * 80)

    print(df["passenger_count"].describe())

    missing_count = df["passenger_count"].isna().sum()
    zero_count = (df["passenger_count"] == 0).sum()
    negative_count = (df["passenger_count"] < 0).sum()
    above_six_count = (df["passenger_count"] > 6).sum()

    print(f"\nMissing passenger counts: {missing_count:,}")
    print(f"Zero passenger counts: {zero_count:,}")
    print(f"Negative passenger counts: {negative_count:,}")
    print(f"Passenger counts above 6: {above_six_count:,}")

    print("\nPassenger-count distribution:")
    print(
        df["passenger_count"]
        .value_counts(dropna=False)
        .sort_index()
    )


# =============================================================================
# MONETARY VARIABLES VALIDATION
# =============================================================================

def validate_monetary_variables(df: pd.DataFrame) -> None:
    """Validate monetary variables used for financial analysis."""

    monetary_columns = [
        "fare_amount",
        "tip_amount",
        "total_amount",
        "tolls_amount",
        "extra",
        "mta_tax",
        "improvement_surcharge",
        "congestion_surcharge",
        "Airport_fee",
        "cbd_congestion_fee",
    ]

    print("\n" + "=" * 80)
    print("MONETARY VARIABLES VALIDATION")
    print("=" * 80)

    for column in monetary_columns:

        print("\n" + "-" * 80)
        print(column.upper())
        print("-" * 80)

        print(df[column].describe())

        negative_values = (df[column] < 0).sum()
        zero_values = (df[column] == 0).sum()

        print(f"\nNegative values: {negative_values:,}")
        print(f"Zero values: {zero_values:,}")

        print("\nFive largest values:")

        print(
            df.nlargest(
                5,
                column,
            )[
                [
                    column,
                    "trip_distance",
                    "fare_amount",
                    "tip_amount",
                    "total_amount",
                    "source_file",
                ]
            ]
        )


# =============================================================================
# MISSING VALUES VALIDATION
# =============================================================================

def validate_missing_values(df: pd.DataFrame) -> None:
    """Summarize missing values and investigate shared missingness patterns."""

    print("\n" + "=" * 80)
    print("MISSING VALUES VALIDATION")
    print("=" * 80)

    missing_summary = pd.DataFrame(
        {
            "missing_count": df.isna().sum(),
            "missing_percentage": df.isna().mean().mul(100),
        }
    )

    missing_summary = missing_summary[
        missing_summary["missing_count"] > 0
    ].sort_values(
        "missing_count",
        ascending=False,
    )

    print(missing_summary.round(2))

    related_columns = [
        "passenger_count",
        "RatecodeID",
        "store_and_fwd_flag",
        "congestion_surcharge",
        "Airport_fee",
    ]

    all_related_missing = (
        df[related_columns]
        .isna()
        .all(axis=1)
    )

    print(
        "\nRows where all five related variables are missing: "
        f"{all_related_missing.sum():,}"
    )

    print("\nPayment types among those rows:")
    print(
        df.loc[
            all_related_missing,
            "payment_type",
        ].value_counts(dropna=False)
    )

    print("\nVendors among those rows:")
    print(
        df.loc[
            all_related_missing,
            "VendorID",
        ].value_counts(dropna=False)
    )


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def main() -> None:
    """Run all data validation checks."""

    raw_df = load_trip_data()

    validate_duplicates(raw_df)
    validate_timestamps(raw_df)

    trip_duration = validate_trip_duration(raw_df)

    validate_trip_distance(
        raw_df,
        trip_duration,
    )

    validate_passenger_count(raw_df)

    validate_monetary_variables(raw_df)

    validate_missing_values(raw_df)

    

if __name__ == "__main__":
    main()
