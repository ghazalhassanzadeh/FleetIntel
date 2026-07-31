# FleetIntel

# FleetIntel

## 1. Project Vision

FleetIntel is an end-to-end business intelligence platform built on official NYC Yellow Taxi trip data.

The project demonstrates the complete data analytics workflow, from raw data engineering and SQL analysis to statistical analysis, machine learning, interactive dashboards, and a Streamlit application.

Its goal is to transform millions of raw trip records into actionable insights that support operational, financial, and customer-focused decision-making.

---

## 2. Stakeholders

FleetIntel is designed from the perspective of a Business Intelligence team supporting taxi fleet operations. It provides data-driven insights for multiple business functions, including:

- **Fleet Operations Managers** – monitor demand, trip activity, and operational efficiency.
- **Business Intelligence Analysts** – analyze performance trends and support strategic decision-making.
- **Finance Managers** – monitor revenue, fares, tips, and overall financial performance.
- **Marketing & Customer Growth Teams** – understand customer travel patterns and identify opportunities to improve customer acquisition and service offerings.

---

## 3. Business Problem

Taxi companies collect millions of trip records every month, but raw operational data alone provides limited business value.

FleetIntel addresses this challenge by transforming raw trip data into meaningful business intelligence that helps stakeholders understand demand patterns, operational efficiency, revenue drivers, and customer behavior.

The project demonstrates how data analytics can support informed business decisions across multiple areas of fleet management.

---

## 4. Project Objectives

The objectives of FleetIntel are to:

- Build a reproducible ETL pipeline for cleaning and preparing taxi trip data.
- Explore operational, financial, and customer travel patterns.
- Generate meaningful business KPIs through SQL and Python.
- Apply statistical analysis to validate business insights.
- Develop a machine learning model for predictive analytics.
- Present findings through an interactive Power BI dashboard and Streamlit application.

---

## 5. Business Questions

FleetIntel aims to answer the following business questions to support data-driven decision-making.

### Operations

1. When are taxi demand and trip volume highest throughout the day and week?

2. Which pickup and dropoff zones experience the highest trip activity?

3. Which routes are the busiest and how do travel patterns vary across the city?

### Financial Performance

4. Which pickup and dropoff locations generate the highest revenue?

5. How do fare amount, tips, and total revenue vary by time of day and location?

6. Which payment methods are used most frequently, and how do they influence tipping behavior?

### Customer Behavior

7. What are the most common trip distances and passenger counts?

8. How do customer travel patterns change by hour, weekday, and location?

9. Which trip characteristics are associated with higher tip amounts?

### Predictive Analytics

10. Can trip duration be accurately predicted using information available before the trip begins?


## 6. Dataset Overview

FleetIntel uses the official **NYC Taxi & Limousine Commission (TLC) Yellow Taxi Trip Records**, which provide detailed information about individual taxi trips across New York City.

### Data Source

- **Provider:** NYC Taxi & Limousine Commission (TLC)
- **Official Website:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **Data Format:** Apache Parquet (.parquet)
- **Lookup Table:** `taxi_zone_lookup.csv`

### Dataset Used

This project analyzes the following monthly datasets:

- `yellow_tripdata_2026-03.parquet`
- `yellow_tripdata_2026-04.parquet`
- `yellow_tripdata_2026-05.parquet`

Together, these files contain millions of individual taxi trips and represent a large sample of real-world transportation activity.

### Key Information Available

The dataset includes information related to:

- Trip timestamps (pickup and dropoff)
- Pickup and dropoff locations
- Trip distance
- Passenger count
- Fare amount
- Tip amount
- Total trip cost
- Payment method
- Additional charges (airport, congestion, tolls)

These variables enable the analysis of operational performance, financial metrics, customer travel behavior, and predictive modeling.
