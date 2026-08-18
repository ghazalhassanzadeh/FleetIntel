# Feature Engineering

## Purpose

This document summarizes the features created in `src/04_feature_engineering.py`.

These features were added to support demand analysis, operational performance, financial analysis, SQL analysis, and Power BI reporting.

## Engineered Features

| Feature | Description | Purpose |
|---|---|---|
| `pickup_hour` | Hour extracted from the pickup timestamp | Analyze hourly demand patterns |
| `pickup_day_name` | Day of the week | Compare demand across weekdays |
| `pickup_date` | Calendar date of pickup | Analyze daily trends |
| `is_weekend` | Indicates whether the trip occurred on a weekend | Compare weekday and weekend activity |
| `average_speed_mph` | Average trip speed calculated from distance and duration | Analyze trip efficiency and speed patterns |
| `fare_per_mile` | Fare amount divided by trip distance | Analyze fare relative to distance |
| `fare_per_minute` | Fare amount divided by trip duration | Analyze fare relative to trip time |
| `tip_percentage` | Tip amount as a percentage of fare | Analyze tipping behavior |

## Output

The feature engineering pipeline creates:

`data/processed/feature_engineered_taxi_trips.parquet`

This dataset is used in the subsequent analysis and reporting stages of the project.