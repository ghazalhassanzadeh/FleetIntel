from pathlib import Path
import os

import pandas as pd
import pyarrow.parquet as pq
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


# =============================================================================
# PROJECT / FILE CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "feature_engineered_taxi_trips.parquet"
)

PICKUP_SUMMARY_TABLE = "pickup_location_summary"
ROUTE_SUMMARY_TABLE = "route_summary"

BATCH_SIZE = 250_000


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

load_dotenv(PROJECT_ROOT / ".env")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


# =============================================================================
# VALIDATE DATABASE CONFIGURATION
# =============================================================================

def validate_database_configuration() -> None:
    """Ensure all required MySQL environment variables are available."""

    required_variables = {
        "MYSQL_HOST": MYSQL_HOST,
        "MYSQL_PORT": MYSQL_PORT,
        "MYSQL_USER": MYSQL_USER,
        "MYSQL_PASSWORD": MYSQL_PASSWORD,
        "MYSQL_DATABASE": MYSQL_DATABASE,
    }

    missing_variables = [
        name
        for name, value in required_variables.items()
        if not value
    ]

    if missing_variables:
        raise ValueError(
            "Missing required environment variables: "
            + ", ".join(missing_variables)
        )


# =============================================================================
# VALIDATE INPUT FILE
# =============================================================================

def validate_input_file() -> None:
    """Ensure the processed Parquet dataset exists."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset was not found:\n"
            f"{INPUT_FILE}\n"
            "Run src/04_feature_engineering.py first."
        )


# =============================================================================
# GET SOURCE ROW COUNT
# =============================================================================

def get_source_row_count() -> int:
    """Return the number of rows in the processed Parquet dataset."""

    parquet_file = pq.ParquetFile(INPUT_FILE)

    return parquet_file.metadata.num_rows


# =============================================================================
# CREATE MYSQL ENGINE
# =============================================================================

def create_mysql_engine():
    """Create a SQLAlchemy engine for the FleetIntel MySQL database."""

    connection_url = URL.create(
        drivername="mysql+mysqlconnector",
        username=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        database=MYSQL_DATABASE,
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True,
    )


# =============================================================================
# TEST MYSQL CONNECTION
# =============================================================================

def test_mysql_connection(engine) -> None:
    """Test the MySQL connection."""

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

    print("=" * 80)
    print("MYSQL CONNECTION TEST")
    print("=" * 80)
    print(f"Connection successful: {result.scalar() == 1}")


# =============================================================================
# CREATE PICKUP LOCATION SUMMARY
# =============================================================================

def create_pickup_location_summary() -> pd.DataFrame:
    """Create pickup-location demand and revenue metrics."""

    print("\n" + "=" * 80)
    print("CREATE PICKUP LOCATION SUMMARY")
    print("=" * 80)

    parquet_file = pq.ParquetFile(INPUT_FILE)

    summaries = []

    for batch_number, batch in enumerate(
        parquet_file.iter_batches(
            batch_size=BATCH_SIZE,
            columns=[
                "PULocationID",
                "total_amount",
            ],
        ),
        start=1,
    ):
        chunk = batch.to_pandas()

        chunk["positive_revenue"] = (
            chunk["total_amount"]
            .where(
                chunk["total_amount"] > 0,
                0,
            )
        )

        chunk["positive_revenue_trip"] = (
            chunk["total_amount"] > 0
        ).astype("int64")

        summary = (
            chunk
            .groupby(
                "PULocationID",
                dropna=False,
            )
            .agg(
                trip_count=(
                    "PULocationID",
                    "size",
                ),
                total_revenue=(
                    "positive_revenue",
                    "sum",
                ),
                positive_revenue_trips=(
                    "positive_revenue_trip",
                    "sum",
                ),
            )
            .reset_index()
        )

        summaries.append(summary)

        print(
            f"Processed pickup batch "
            f"{batch_number:,}"
        )

    combined = pd.concat(
        summaries,
        ignore_index=True,
    )

    final_summary = (
        combined
        .groupby(
            "PULocationID",
            dropna=False,
        )
        .agg(
            trip_count=(
                "trip_count",
                "sum",
            ),
            total_revenue=(
                "total_revenue",
                "sum",
            ),
            positive_revenue_trips=(
                "positive_revenue_trips",
                "sum",
            ),
        )
        .reset_index()
    )

    final_summary["avg_revenue_per_trip"] = (
        final_summary["total_revenue"]
        .div(
            final_summary[
                "positive_revenue_trips"
            ].replace(0, pd.NA)
        )
    )

    print(
        f"Pickup summary rows created: "
        f"{len(final_summary):,}"
    )

    print(
        f"Trips represented: "
        f"{final_summary['trip_count'].sum():,}"
    )

    return final_summary


# =============================================================================
# CREATE ROUTE SUMMARY
# =============================================================================

def create_route_summary() -> pd.DataFrame:
    """Create origin-destination trip counts."""

    print("\n" + "=" * 80)
    print("CREATE ROUTE SUMMARY")
    print("=" * 80)

    parquet_file = pq.ParquetFile(INPUT_FILE)

    summaries = []

    for batch_number, batch in enumerate(
        parquet_file.iter_batches(
            batch_size=BATCH_SIZE,
            columns=[
                "PULocationID",
                "DOLocationID",
            ],
        ),
        start=1,
    ):
        chunk = batch.to_pandas()

        summary = (
            chunk
            .groupby(
                [
                    "PULocationID",
                    "DOLocationID",
                ],
                dropna=False,
            )
            .size()
            .reset_index(
                name="trip_count"
            )
        )

        summaries.append(summary)

        print(
            f"Processed route batch "
            f"{batch_number:,}"
        )

    combined = pd.concat(
        summaries,
        ignore_index=True,
    )

    final_summary = (
        combined
        .groupby(
            [
                "PULocationID",
                "DOLocationID",
            ],
            dropna=False,
        )
        .agg(
            trip_count=(
                "trip_count",
                "sum",
            )
        )
        .reset_index()
    )

    print(
        f"Route summary rows created: "
        f"{len(final_summary):,}"
    )

    print(
        f"Trips represented: "
        f"{final_summary['trip_count'].sum():,}"
    )

    return final_summary


# =============================================================================
# LOAD PICKUP SUMMARY TO MYSQL
# =============================================================================

def load_pickup_summary_to_mysql(
    summary_df: pd.DataFrame,
    engine,
) -> None:
    """Load pickup-location summary data into MySQL."""

    print("\n" + "=" * 80)
    print("LOAD PICKUP LOCATION SUMMARY TO MYSQL")
    print("=" * 80)

    summary_df.to_sql(
        name=PICKUP_SUMMARY_TABLE,
        con=engine,
        if_exists="replace",
        index=False,
    )

    print(
        f"Table created: "
        f"{PICKUP_SUMMARY_TABLE}"
    )


# =============================================================================
# LOAD ROUTE SUMMARY TO MYSQL
# =============================================================================

def load_route_summary_to_mysql(
    summary_df: pd.DataFrame,
    engine,
) -> None:
    """Load route summary data into MySQL."""

    print("\n" + "=" * 80)
    print("LOAD ROUTE SUMMARY TO MYSQL")
    print("=" * 80)

    summary_df.to_sql(
        name=ROUTE_SUMMARY_TABLE,
        con=engine,
        if_exists="replace",
        index=False,
    )

    print(
        f"Table created: "
        f"{ROUTE_SUMMARY_TABLE}"
    )


# =============================================================================
# VERIFY PICKUP SUMMARY TABLE
# =============================================================================

def verify_pickup_summary_table(
    engine,
    expected_rows: int,
) -> None:
    """Verify the pickup-location summary table."""

    query = text(
        f"""
        SELECT
            COUNT(*) AS location_count,
            SUM(trip_count) AS total_trips
        FROM {PICKUP_SUMMARY_TABLE}
        """
    )

    with engine.connect() as connection:
        result = (
            connection
            .execute(query)
            .mappings()
            .one()
        )

    location_count = int(
        result["location_count"]
    )

    total_trips = int(
        result["total_trips"]
    )

    print("\n" + "=" * 80)
    print("VERIFY PICKUP LOCATION SUMMARY")
    print("=" * 80)

    print(
        f"Location rows: "
        f"{location_count:,}"
    )

    print(
        f"Trips represented: "
        f"{total_trips:,}"
    )

    if total_trips != expected_rows:
        raise ValueError(
            "Pickup summary trip count does not "
            "match the source dataset."
        )

    print(
        "Pickup summary verification successful."
    )


# =============================================================================
# VERIFY ROUTE SUMMARY TABLE
# =============================================================================

def verify_route_summary_table(
    engine,
    expected_rows: int,
) -> None:
    """Verify the origin-destination route summary table."""

    query = text(
        f"""
        SELECT
            COUNT(*) AS route_count,
            SUM(trip_count) AS total_trips
        FROM {ROUTE_SUMMARY_TABLE}
        """
    )

    with engine.connect() as connection:
        result = (
            connection
            .execute(query)
            .mappings()
            .one()
        )

    route_count = int(
        result["route_count"]
    )

    total_trips = int(
        result["total_trips"]
    )

    print("\n" + "=" * 80)
    print("VERIFY ROUTE SUMMARY")
    print("=" * 80)

    print(
        f"Route rows: "
        f"{route_count:,}"
    )

    print(
        f"Trips represented: "
        f"{total_trips:,}"
    )

    if total_trips != expected_rows:
        raise ValueError(
            "Route summary trip count does not "
            "match the source dataset."
        )

    print(
        "Route summary verification successful."
    )


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def main() -> None:
    """Create and load FleetIntel SQL summary tables."""

    validate_database_configuration()
    validate_input_file()

    expected_rows = get_source_row_count()

    print("=" * 80)
    print("SOURCE DATASET")
    print("=" * 80)
    print(
        f"Expected source rows: "
        f"{expected_rows:,}"
    )

    engine = create_mysql_engine()

    try:
        test_mysql_connection(engine)

        pickup_summary_df = (
            create_pickup_location_summary()
        )

        load_pickup_summary_to_mysql(
            pickup_summary_df,
            engine,
        )

        verify_pickup_summary_table(
            engine,
            expected_rows=expected_rows,
        )

        route_summary_df = (
            create_route_summary()
        )

        load_route_summary_to_mysql(
            route_summary_df,
            engine,
        )

        verify_route_summary_table(
            engine,
            expected_rows=expected_rows,
        )

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()