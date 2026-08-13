from pathlib import Path
import os

import pandas as pd
import pyarrow.parquet as pq
from dotenv import load_dotenv
from sqlalchemy import (
    URL,
    Boolean,
    Date,
    DateTime,
    Float,
    SmallInteger,
    String,
    create_engine,
    inspect,
    text,
)


# =============================================================================
# FILE PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DATA_DIR
    / "feature_engineered_taxi_trips.parquet"
)

ZONE_LOOKUP_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "taxi_zone_lookup.csv"
)

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

load_dotenv(PROJECT_ROOT / ".env")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

TABLE_NAME = "taxi_trips"
ZONE_TABLE_NAME = "taxi_zones"
CHUNK_SIZE = 100_000
SQL_INSERT_CHUNK_SIZE = 1_000


# =============================================================================
# MYSQL DATA TYPES
# =============================================================================

MYSQL_DTYPES = {
    "VendorID": SmallInteger(),
    "tpep_pickup_datetime": DateTime(),
    "tpep_dropoff_datetime": DateTime(),
    "passenger_count": SmallInteger(),
    "trip_distance": Float(),
    "RatecodeID": SmallInteger(),
    "store_and_fwd_flag": String(1),
    "PULocationID": SmallInteger(),
    "DOLocationID": SmallInteger(),
    "payment_type": SmallInteger(),
    "fare_amount": Float(),
    "extra": Float(),
    "mta_tax": Float(),
    "tip_amount": Float(),
    "tolls_amount": Float(),
    "improvement_surcharge": Float(),
    "total_amount": Float(),
    "congestion_surcharge": Float(),
    "Airport_fee": Float(),
    "cbd_congestion_fee": Float(),
    "source_file": String(100),
    "trip_duration_minutes": Float(),
    "pickup_date": Date(),
    "pickup_hour": SmallInteger(),
    "pickup_day_name": String(9),
    "is_weekend": Boolean(),
    "average_speed_mph": Float(),
    "fare_per_mile": Float(),
    "fare_per_minute": Float(),
    "tip_percentage": Float(),
}


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
# CREATE DATABASE ENGINE
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
# TEST DATABASE CONNECTION
# =============================================================================

def test_mysql_connection(engine) -> None:
    """Test the connection to the FleetIntel MySQL database."""

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        print("=" * 80)
        print("MYSQL CONNECTION TEST")
        print("=" * 80)
        print(f"Connection successful: {result.scalar() == 1}")


# =============================================================================
# GET SOURCE ROW COUNT
# =============================================================================

def get_source_row_count() -> int:
    """Return the number of rows in the Parquet file without loading it."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Feature-engineered dataset was not found:\n"
            f"{INPUT_FILE}\n"
            "Run src/04_feature_engineering.py first."
        )

    parquet_file = pq.ParquetFile(INPUT_FILE)

    return parquet_file.metadata.num_rows


# =============================================================================
# LOAD FEATURE-ENGINEERED DATA
# =============================================================================

def load_feature_engineered_data() -> pd.DataFrame:
    """Load the feature-engineered taxi dataset from Parquet."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Feature-engineered dataset was not found:\n"
            f"{INPUT_FILE}\n"
            "Run src/04_feature_engineering.py first."
        )

    df = pd.read_parquet(INPUT_FILE)

    print("\n" + "=" * 80)
    print("LOAD FEATURE-ENGINEERED DATA")
    print("=" * 80)
    print(f"Rows loaded: {len(df):,}")
    print(f"Columns loaded: {df.shape[1]}")

    return df


# =============================================================================
# LOAD TAXI ZONE LOOKUP
# =============================================================================

def load_taxi_zones(engine) -> None:
    """Load the TLC taxi-zone lookup table into MySQL."""

    if not ZONE_LOOKUP_FILE.exists():
        raise FileNotFoundError(
            f"Taxi zone lookup file was not found:\n"
            f"{ZONE_LOOKUP_FILE}"
        )

    zones_df = pd.read_csv(ZONE_LOOKUP_FILE)

    print("\n" + "=" * 80)
    print("LOAD TAXI ZONES")
    print("=" * 80)

    print(f"Rows loaded: {len(zones_df):,}")
    print(f"Columns loaded: {zones_df.shape[1]}")

    zones_df.to_sql(
        name=ZONE_TABLE_NAME,
        con=engine,
        if_exists="replace",
        index=False,
    )

    print(f"Table created: {ZONE_TABLE_NAME}")


# =============================================================================
# CHECK MYSQL TABLE
# =============================================================================

def mysql_table_exists(engine) -> bool:
    """Return True if the target MySQL table already exists."""

    inspector = inspect(engine)

    return inspector.has_table(
        TABLE_NAME,
        schema=MYSQL_DATABASE,
    )


# =============================================================================
# GET EXISTING MYSQL ROW COUNT
# =============================================================================

def get_existing_mysql_row_count(engine) -> int:
    """Return the current number of rows in the MySQL taxi table."""

    if not mysql_table_exists(engine):
        return 0

    query = text(
        f"SELECT COUNT(*) FROM {TABLE_NAME}"
    )

    with engine.connect() as connection:
        row_count = connection.execute(query).scalar()

    return int(row_count)


# =============================================================================
# LOAD DATA TO MYSQL
# =============================================================================

def load_data_to_mysql(
    df: pd.DataFrame,
    engine,
) -> None:
    """Load or resume loading the analytical taxi dataset into MySQL."""

    total_rows = len(df)
    existing_rows = get_existing_mysql_row_count(engine)

    print("\n" + "=" * 80)
    print("LOAD DATA TO MYSQL")
    print("=" * 80)

    print(f"Target table: {TABLE_NAME}")
    print(f"Source rows: {total_rows:,}")
    print(f"Existing MySQL rows: {existing_rows:,}")
    print(f"Rows remaining: {total_rows - existing_rows:,}")
    print(f"Chunk size: {CHUNK_SIZE:,}")

    if existing_rows > total_rows:
        raise ValueError(
            "MySQL contains more rows than the source dataset."
        )

    if existing_rows == total_rows:
        print("MySQL already contains the complete dataset.")
        return

    for start in range(
        existing_rows,
        total_rows,
        CHUNK_SIZE,
    ):
        end = min(
            start + CHUNK_SIZE,
            total_rows,
        )

        chunk = df.iloc[start:end].copy()

        if_exists = (
            "replace"
            if existing_rows == 0 and start == 0
            else "append"
        )

        chunk.to_sql(
            name=TABLE_NAME,
            con=engine,
            if_exists=if_exists,
            index=False,
            dtype=MYSQL_DTYPES,
            chunksize=SQL_INSERT_CHUNK_SIZE,
        )

        print(
            f"Loaded rows "
            f"{start + 1:,} - {end:,} "
            f"({end / total_rows:.1%})"
        )


# =============================================================================
# VERIFY MYSQL LOAD
# =============================================================================

def verify_mysql_load(
    engine,
    expected_rows: int,
) -> None:
    """Verify that MySQL contains the expected number of rows."""

    mysql_row_count = get_existing_mysql_row_count(engine)

    print("\n" + "=" * 80)
    print("VERIFY MYSQL LOAD")
    print("=" * 80)

    print(f"Expected rows: {expected_rows:,}")
    print(f"MySQL rows: {mysql_row_count:,}")

    if mysql_row_count != expected_rows:
        raise ValueError(
            "MySQL row count does not match the source dataset."
        )

    print("Row-count verification successful.")


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def main() -> None:
    """Load FleetIntel analytical tables into MySQL."""

    validate_database_configuration()

    engine = create_mysql_engine()

    try:
        test_mysql_connection(engine)

        expected_rows = get_source_row_count()
        existing_rows = get_existing_mysql_row_count(engine)

        print("\n" + "=" * 80)
        print("CHECK TAXI TRIP TABLE")
        print("=" * 80)

        print(f"Source rows: {expected_rows:,}")
        print(f"Existing MySQL rows: {existing_rows:,}")

        if existing_rows == expected_rows:
            print("MySQL already contains the complete taxi trip dataset.")

        else:
            df = load_feature_engineered_data()

            load_data_to_mysql(
                df,
                engine,
            )

            verify_mysql_load(
                engine,
                expected_rows=expected_rows,
            )

        load_taxi_zones(engine)

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()