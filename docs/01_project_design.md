# FleetIntel

## 1. Project Vision

FleetIntel is an end-to-end data analytics and business intelligence project built on official NYC Yellow Taxi trip data.

The project covers the analytics workflow from raw data validation, cleaning, and feature engineering to exploratory analysis, SQL analysis, and interactive reporting in Power BI.

The goal is to transform millions of raw taxi trip records into useful insights about demand, operations, locations, and revenue.

---

## 2. Stakeholders

FleetIntel is designed from the perspective of a Business Intelligence team supporting taxi operations. The analysis is relevant to several business functions:

- **Fleet Operations Managers** – understand demand patterns, trip activity, and operational efficiency.
- **Business Intelligence Analysts** – analyze performance trends and support data-driven decision-making.
- **Finance Managers** – monitor revenue and identify important revenue patterns.
- **Business and Planning Teams** – understand travel patterns across times and locations to support operational planning.

---

## 3. Business Problem

Taxi operations generate millions of trip records, but raw trip data alone is difficult to use for business decisions.

FleetIntel transforms this data into structured analytical datasets, KPIs, SQL summaries, and interactive visualizations.

The project focuses on understanding:

- when taxi demand is highest
- where trips are concentrated
- which routes are most frequently used
- how operational performance changes throughout the day and week
- when and where revenue is generated

---

## 4. Project Objectives

The objectives of FleetIntel are to:

- Build a reproducible data pipeline for validating, cleaning, and transforming NYC Yellow Taxi data.
- Create useful analytical features for demand, operational, and financial analysis.
- Explore the dataset using Python and statistical summaries.
- Use SQL to answer business questions and create reusable analytical summaries.
- Develop meaningful KPIs for taxi operations.
- Build an interactive Power BI dashboard for exploring demand, location, operational efficiency, and revenue.
- Present the analysis in a clear and reproducible GitHub portfolio project.

---

## 5. Business Questions

FleetIntel focuses on four main analytical areas.

### Demand

1. When is taxi demand highest throughout the day?
2. How does trip volume change across days of the week?
3. How does daily trip volume change during the analysis period?

### Location and Routes

4. Which boroughs and service zones generate the most pickup activity?
5. Which pickup zones are the busiest?
6. Which pickup-to-dropoff routes have the highest trip volumes?

### Operational Efficiency

7. How does average taxi speed change throughout the day?
8. How does average speed vary across days of the week?
9. How does average trip duration change by hour?
10. How does fare per mile vary throughout the day?

### Revenue

11. During which hours is the most revenue generated?
12. How does revenue vary across days of the week?
13. Which pickup zones generate the most revenue?
14. How does average revenue per trip change throughout the day?

---

## 6. Dataset Overview

FleetIntel uses official **NYC Taxi & Limousine Commission (TLC) Yellow Taxi Trip Records**.

### Data Source

- **Provider:** NYC Taxi & Limousine Commission (TLC)
- **Data:** Yellow Taxi Trip Records
- **Format:** Apache Parquet
- **Location lookup:** `taxi_zone_lookup.csv`

### Analysis Period

The project analyzes three months of Yellow Taxi data:

- March 2026
- April 2026
- May 2026

The combined raw dataset contains **11,874,527 trip records**.

After data validation and cleaning, **11,718,495 trips** were retained for further analysis.

### Key Information

The source data includes:

- pickup and dropoff timestamps
- pickup and dropoff location IDs
- trip distance
- passenger count
- fare amount
- tip amount
- total amount
- payment type
- tolls and additional charges

Additional analytical features were created during the feature engineering stage, including trip duration, average speed, time-based variables, fare per mile, and tip percentage.