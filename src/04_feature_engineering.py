from pathlib import Path

import numpy as np
import pandas as pd


# =============================================================================
# FILE PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_FILE = PROCESSED_DATA_DIR / "clean_taxi_trips.parquet"
OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "feature_engineered_taxi_trips.parquet"
)


# =============================================================================
# LOAD CLEAN DATA
# =============================================================================

def load_clean_data() -> pd.DataFrame:
    """Load the cleaned taxi dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset was not found:\n{INPUT_FILE}\n"
            "Run src/03_data_cleaning.py first."
        )

    df = pd.read_parquet(INPUT_FILE)

    print("=" * 80)
    print("LOAD CLEAN DATA")
    print("=" * 80)
    print(f"Rows loaded: {len(df):,}")
    print(f"Columns loaded: {df.shape[1]}")

    return df


# =============================================================================
# CREATE TIME FEATURES
# =============================================================================

def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create time-based features from the pickup timestamp."""

    df = df.copy()

    pickup_datetime = df["tpep_pickup_datetime"]

    df["pickup_date"] = pickup_datetime.dt.date
    df["pickup_hour"] = pickup_datetime.dt.hour
    df["pickup_day_name"] = pickup_datetime.dt.day_name()
    df["is_weekend"] = pickup_datetime.dt.dayofweek >= 5

    print("\n" + "=" * 80)
    print("CREATE TIME FEATURES")
    print("=" * 80)
    print(
        "Created: pickup_date, pickup_hour, "
        "pickup_day_name, is_weekend"
    )

    return df


# =============================================================================
# CREATE TRIP FEATURES
# =============================================================================

def create_trip_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create trip-performance features."""

    df = df.copy()

    duration_hours = df["trip_duration_minutes"] / 60

    df["average_speed_mph"] = np.where(
        (duration_hours > 0) & (df["trip_distance"] > 0),
        df["trip_distance"] / duration_hours,
        np.nan,
    )

    print("\n" + "=" * 80)
    print("CREATE TRIP FEATURES")
    print("=" * 80)
    print("Created: average_speed_mph")

    return df


# =============================================================================
# CREATE FINANCIAL FEATURES
# =============================================================================

def create_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create fare and tipping features."""

    df = df.copy()

    df["fare_per_mile"] = np.where(
        df["trip_distance"] > 0,
        df["fare_amount"] / df["trip_distance"],
        np.nan,
    )

    df["fare_per_minute"] = np.where(
        df["trip_duration_minutes"] > 0,
        df["fare_amount"] / df["trip_duration_minutes"],
        np.nan,
    )

    df["tip_percentage"] = np.where(
        df["fare_amount"] > 0,
        df["tip_amount"] / df["fare_amount"] * 100,
        np.nan,
    )

    print("\n" + "=" * 80)
    print("CREATE FINANCIAL FEATURES")
    print("=" * 80)
    print("Created: fare_per_mile, fare_per_minute, tip_percentage")

    return df


# =============================================================================
# SAVE FEATURE-ENGINEERED DATA
# =============================================================================

def save_feature_engineered_data(df: pd.DataFrame) -> None:
    """Save the feature-engineered dataset."""

    df.to_parquet(
        OUTPUT_FILE,
        index=False,
    )

    print("\n" + "=" * 80)
    print("SAVE FEATURE-ENGINEERED DATA")
    print("=" * 80)
    print(f"Dataset saved to:\n{OUTPUT_FILE}")

    print("\n" + "=" * 80)
    print("FEATURE ENGINEERING SUMMARY")
    print("=" * 80)

    print(f"Output rows: {len(df):,}")
    print(f"Output columns: {df.shape[1]:,}")

    print("\nNew features created:")

    new_features = [
        "pickup_date",
        "pickup_hour",
        "pickup_day_name",
        "is_weekend",
        "average_speed_mph",
        "fare_per_mile",
        "fare_per_minute",
        "tip_percentage",
    ]

    for feature in new_features:
        print(f" - {feature}")


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def main() -> None:
    """Run the feature engineering pipeline."""

    df = load_clean_data()
    df = create_time_features(df)
    df = create_trip_features(df)
    df = create_financial_features(df)

    save_feature_engineered_data(df)


if __name__ == "__main__":
    main()