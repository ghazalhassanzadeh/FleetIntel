# Feature Engineering Plan

## Purpose

This document defines the features created in `src/04_feature_engineering.py`.

The features support time-based demand analysis, trip performance analysis, financial analysis, Power BI reporting, and machine learning.

## Planned Features

| Feature | Description | Purpose |
|---|---|---|
| `pickup_hour` | Hour extracted from pickup time | Analyze hourly demand |
| `pickup_day_name` | Day of the week | Compare demand across weekdays |
| `pickup_date` | Calendar date of pickup | Analyze daily trends |
| `is_weekend` | Weekend indicator | Compare weekday and weekend activity |
| `average_speed_mph` | Distance divided by duration | Analyze trip efficiency and detect unusual trips |
| `fare_per_mile` | Fare divided by distance | Compare fare efficiency |
| `fare_per_minute` | Fare divided by duration | Analyze pricing relative to trip time |
| `tip_percentage` | Tip divided by fare | Analyze tipping behavior |

## Output

The feature engineering pipeline will create:

`data/processed/feature_engineered_taxi_trips.parquet`