# FleetIntel

FleetIntel is an end-to-end data analytics project based on New York City Yellow Taxi trip data.

The project analyzes more than 11 million taxi trips from March to May 2026 to explore demand patterns, trip characteristics, revenue, and operational performance.

The workflow covers the full analytics process, from raw data validation and cleaning to feature engineering, exploratory analysis, SQL analysis, and dashboard development.

## Project Goals

The project focuses on a few practical questions:

- When is taxi demand highest and lowest?
- How does demand change by hour and day of the week?
- What does a typical taxi trip look like in terms of distance and duration?
- How do revenue and average trip value change throughout the day?
- How do payment methods and tipping behavior differ?
- How does average travel speed change by time of day?
- How do weekday and weekend trips compare?
- Which periods combine high demand with lower operating speeds?

## Dataset

FleetIntel uses the official **NYC Taxi & Limousine Commission (TLC) Yellow Taxi Trip Records**.

**Official source:**  
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

The analysis uses Yellow Taxi trip records for:

- March 2026
- April 2026
- May 2026

The following source files are used:

- `yellow_tripdata_2026-03.parquet`
- `yellow_tripdata_2026-04.parquet`
- `yellow_tripdata_2026-05.parquet`
- `taxi_zone_lookup.csv`

The raw trip files contain information such as pickup and drop-off timestamps, trip distance, pickup and drop-off locations, passenger count, payment type, fares, tips, tolls, and surcharges.

The raw datasets are not stored in this repository. They can be downloaded from the official TLC website and placed in:

```text
data/raw/
```

## Data Pipeline

The project is organized as a sequence of Python scripts so that each stage of the analysis can be reproduced separately.

### 1. Data Exploration

The raw monthly Parquet files are inspected to understand their structure, data types, missing values, and basic distributions.

### 2. Data Validation

Potential data-quality problems are investigated before cleaning. This includes checks for invalid trip durations, implausible trip distances, unusual passenger counts, and other extreme values.

### 3. Data Cleaning

The cleaning pipeline:

- removes trips where pickup occurs after drop-off
- keeps records within the March-May 2026 analysis period
- calculates trip duration
- removes invalid trip durations
- removes trips with implausible calculated speeds

After cleaning, the analytical dataset contains **11,718,495 trips**.

### 4. Feature Engineering

Additional variables are created for later analysis, including:

- `pickup_date`
- `pickup_hour`
- `pickup_day_name`
- `is_weekend`
- `average_speed_mph`
- `fare_per_mile`
- `fare_per_minute`
- `tip_percentage`

### 5. Exploratory Data Analysis

Python is used to analyze and visualize:

- hourly and weekday demand
- trip distance and duration
- payment methods and tipping
- revenue patterns
- average travel speed
- relationships between trip distance and duration

Generated figures are stored in:

```text
reports/figures/
```

### 6. SQL Analysis

The feature-engineered dataset is loaded into a local MySQL database for SQL-based analysis.

SQL queries cover demand, trip characteristics, revenue, operational performance, and combined business metrics. The analysis also uses CTEs, conditional aggregation, and window functions.

SQL scripts are stored in:

```text
sql/
```

### 7. Power BI

The final stage of the project will use Power BI to build an interactive dashboard around the main demand, revenue, and operational KPIs.

## Tools

- Python
- Pandas
- NumPy
- Matplotlib
- PyArrow
- MySQL
- SQL
- SQLAlchemy
- Power BI
- Git / GitHub

## Repository Structure

```text
FleetIntel/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── notebooks/
├── powerbi/
├── reports/
│   └── figures/
├── sql/
│   └── fleetintel_analysis.sql
├── src/
│   ├── 01_data_exploration.py
│   ├── 02_data_validation.py
│   ├── 03_data_cleaning.py
│   ├── 04_feature_engineering.py
│   ├── 05_exploratory_data_analysis.py
│   └── 06_load_to_mysql.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Project Status

Data preparation, cleaning, feature engineering, and Python exploratory analysis are complete.

The MySQL and SQL analysis stage is currently in progress. The final Power BI dashboard will be added after the SQL analysis is complete.