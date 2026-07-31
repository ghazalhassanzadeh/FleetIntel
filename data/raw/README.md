# Raw Data

This folder stores the original **NYC Taxi & Limousine Commission (TLC)** datasets used in the FleetIntel project.

The raw datasets are intentionally excluded from this Git repository to keep the repository lightweight and ensure that the data is always obtained from the official source.

Download the following files from the official NYC TLC Trip Record Data website:

https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Required files:

- `yellow_tripdata_2026-03.parquet`
- `yellow_tripdata_2026-04.parquet`
- `yellow_tripdata_2026-05.parquet`
- `taxi_zone_lookup.csv`

Place all files in this folder before running the project.

**Important:** Do not modify the raw datasets. All cleaning and transformations are performed by the FleetIntel ETL pipeline.