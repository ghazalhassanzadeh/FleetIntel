from pathlib import Path

import pandas as pd


# =============================================================================
# FILE PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = PROCESSED_DATA_DIR / "clean_taxi_trips.parquet"


# =============================================================================
# LOAD DATA
# =============================================================================

def load_trip_data() -> pd.DataFrame:
    """Load and combine all monthly taxi datasets."""

    trip_files = sorted(
        RAW_DATA_DIR.glob("yellow_tripdata_2026-*.parquet")
    )

    if not trip_files:
        raise FileNotFoundError(
            f"No Yellow Taxi Parquet files were found in:\n{RAW_DATA_DIR}"
        )

    dataframes = []

    for file_path in trip_files:

        monthly_data = pd.read_parquet(file_path)

        monthly_data["source_file"] = file_path.name

        dataframes.append(monthly_data)

    raw_df = pd.concat(
        dataframes,
        ignore_index=True,
    )

    print(f"Loaded {len(raw_df):,} records.")

    return raw_df


# =============================================================================
# REMOVE INVALID TIMESTAMPS
# =============================================================================

def remove_invalid_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Remove trips where pickup occurs after drop-off."""

    original_rows = len(df)

    df = df[
        df["tpep_pickup_datetime"] <=
        df["tpep_dropoff_datetime"]
    ].copy()

    removed_rows = original_rows - len(df)

    print("\n" + "=" * 80)
    print("REMOVE INVALID TIMESTAMPS")
    print("=" * 80)

    print(f"Rows removed: {removed_rows:,}")
    print(f"Remaining rows: {len(df):,}")

    return df


# =============================================================================
# REMOVE RECORDS OUTSIDE PROJECT PERIOD
# =============================================================================

def remove_records_outside_project_period(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Keep only trips with pickup timestamps from March through May 2026."""

    original_rows = len(df)

    start_date = pd.Timestamp("2026-03-01")
    end_date = pd.Timestamp("2026-06-01")

    df = df[
        (df["tpep_pickup_datetime"] >= start_date)
        & (df["tpep_pickup_datetime"] < end_date)
    ].copy()

    removed_rows = original_rows - len(df)

    print("\n" + "=" * 80)
    print("REMOVE RECORDS OUTSIDE PROJECT PERIOD")
    print("=" * 80)

    print(f"Rows removed: {removed_rows:,}")
    print(f"Remaining rows: {len(df):,}")

    return df


# =============================================================================
# CREATE TRIP DURATION
# =============================================================================

def create_trip_duration(df: pd.DataFrame) -> pd.DataFrame:
    """Create trip duration in minutes."""

    df = df.copy()

    df["trip_duration_minutes"] = (
        df["tpep_dropoff_datetime"] -
        df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    print("\n" + "=" * 80)
    print("CREATE TRIP DURATION")
    print("=" * 80)

    print("Column created: trip_duration_minutes")

    return df


# =============================================================================
# REMOVE INVALID TRIP DURATIONS
# =============================================================================

def remove_invalid_trip_durations(df: pd.DataFrame) -> pd.DataFrame:
    """Remove trips with non-positive or implausibly long durations."""

    original_rows = len(df)

    df = df[
        (df["trip_duration_minutes"] > 0)
        & (df["trip_duration_minutes"] <= 360)
    ].copy()

    removed_rows = original_rows - len(df)

    print("\n" + "=" * 80)
    print("REMOVE INVALID TRIP DURATIONS")
    print("=" * 80)

    print(f"Rows removed: {removed_rows:,}")
    print(f"Remaining rows: {len(df):,}")

    return df


# =============================================================================
# REMOVE IMPLAUSIBLE TRIP SPEEDS
# =============================================================================

def remove_implausible_trip_speeds(df: pd.DataFrame) -> pd.DataFrame:
    """Remove trips with implausibly high average speeds."""

    original_rows = len(df)

    duration_hours = df["trip_duration_minutes"] / 60

    average_speed_mph = (
        df["trip_distance"] / duration_hours
    )

    df = df[
        (df["trip_distance"] == 0)
        | (average_speed_mph <= 100)
    ].copy()

    removed_rows = original_rows - len(df)

    print("\n" + "=" * 80)
    print("REMOVE IMPLAUSIBLE TRIP SPEEDS")
    print("=" * 80)

    print(f"Rows removed: {removed_rows:,}")
    print(f"Remaining rows: {len(df):,}")

    return df


# =============================================================================
# SAVE CLEAN DATA
# =============================================================================

def save_clean_data(df: pd.DataFrame) -> None:
    """Save the cleaned dataset."""

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        OUTPUT_FILE,
        index=False,
    )

    print("\n" + "=" * 80)
    print("SAVE CLEAN DATA")
    print("=" * 80)

    print(f"Dataset saved to:\n{OUTPUT_FILE}")
    print(f"Final rows: {len(df):,}")


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def main() -> None:
    """Run the data cleaning pipeline."""

    df = load_trip_data()

    df = remove_invalid_timestamps(df)

    df = remove_records_outside_project_period(df)

    df = create_trip_duration(df)

    df = remove_invalid_trip_durations(df)

    df = remove_implausible_trip_speeds(df)

    save_clean_data(df)


if __name__ == "__main__":
    main()