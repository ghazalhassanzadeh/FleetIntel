-- ============================================================================
-- FleetIntel SQL Analysis
-- NYC Yellow Taxi Trip Records, March-May 2026
-- ============================================================================


-- ============================================================================
-- 1. DATABASE SETUP
-- ============================================================================

CREATE DATABASE IF NOT EXISTS fleetintel;

USE fleetintel;


-- ============================================================================
-- 2. DATA VALIDATION AND DATABASE METADATA
-- ============================================================================

-- Verify total number of analytical records
SELECT
    COUNT(*) AS row_count
FROM taxi_trips;


-- Preview analytical table
SELECT *
FROM taxi_trips
LIMIT 10;


-- Review table structure
DESCRIBE taxi_trips;


-- Verify taxi-zone lookup
SELECT
    COUNT(*) AS zone_count
FROM taxi_zones;


-- Approximate FleetIntel database size
SELECT
    table_schema AS database_name,
    ROUND(
        SUM(data_length + index_length) / 1024 / 1024 / 1024,
        2
    ) AS size_gb
FROM information_schema.tables
WHERE table_schema = 'fleetintel'
GROUP BY table_schema;


-- ============================================================================
-- 3. PERFORMANCE INDEXES
-- ============================================================================

-- Indexes were created after the bulk load to improve aggregation
-- and join performance on the 11.7M-row analytical table.
--
-- These statements are intentionally commented out because indexes
-- only need to be created once.

-- CREATE INDEX idx_taxi_trips_pickup_day_name
-- ON taxi_trips (pickup_day_name);

-- CREATE INDEX idx_weekday_trip_metrics
-- ON taxi_trips (
--     pickup_day_name,
--     trip_duration_minutes,
--     trip_distance
-- );

-- CREATE INDEX idx_weekday_revenue
-- ON taxi_trips (
--     pickup_day_name,
--     total_amount
-- );

-- CREATE INDEX idx_taxi_trips_pu_location
-- ON taxi_trips (PULocationID);

-- CREATE INDEX idx_taxi_trips_do_location
-- ON taxi_trips (DOLocationID);

-- CREATE UNIQUE INDEX idx_taxi_zones_location
-- ON taxi_zones (LocationID);


-- ============================================================================
-- 4. DEMAND ANALYSIS
-- ============================================================================

-- Trips by pickup hour
SELECT
    pickup_hour,
    COUNT(*) AS trip_count
FROM taxi_trips
GROUP BY pickup_hour
ORDER BY pickup_hour;


-- Busiest pickup hours
SELECT
    pickup_hour,
    COUNT(*) AS trip_count
FROM taxi_trips
GROUP BY pickup_hour
ORDER BY trip_count DESC
LIMIT 10;


-- Trips by weekday
SELECT
    pickup_day_name,
    COUNT(*) AS trip_count
FROM taxi_trips
GROUP BY pickup_day_name
ORDER BY trip_count DESC;


-- ============================================================================
-- 5. TRIP CHARACTERISTICS
-- ============================================================================

-- Overall trip-duration characteristics
SELECT
    AVG(trip_duration_minutes) AS average_duration_minutes,
    MIN(trip_duration_minutes) AS minimum_duration_minutes,
    MAX(trip_duration_minutes) AS maximum_duration_minutes
FROM taxi_trips;


-- Positive-distance trip characteristics
SELECT
    AVG(trip_distance) AS average_distance_miles,
    MIN(trip_distance) AS minimum_distance_miles,
    MAX(trip_distance) AS maximum_distance_miles
FROM taxi_trips
WHERE trip_distance > 0;


-- Average trip characteristics by weekday
SELECT
    pickup_day_name,
    COUNT(*) AS trip_count,
    AVG(trip_duration_minutes) AS avg_duration_minutes,
    AVG(trip_distance) AS avg_distance_miles
FROM taxi_trips
GROUP BY pickup_day_name
ORDER BY trip_count DESC;


-- ============================================================================
-- 6. REVENUE AND PAYMENT ANALYSIS
-- ============================================================================

-- Revenue by pickup hour
SELECT
    pickup_hour,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS average_revenue_per_trip,
    COUNT(*) AS trip_count
FROM taxi_trips
WHERE total_amount > 0
GROUP BY pickup_hour
ORDER BY total_revenue DESC;


-- Revenue by weekday
SELECT
    pickup_day_name,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS average_revenue_per_trip,
    COUNT(*) AS trip_count
FROM taxi_trips
WHERE total_amount > 0
GROUP BY pickup_day_name
ORDER BY total_revenue DESC;


-- Payment method distribution
SELECT
    CASE payment_type
        WHEN 0 THEN 'Flex Fare'
        WHEN 1 THEN 'Credit card'
        WHEN 2 THEN 'Cash'
        WHEN 3 THEN 'No charge'
        WHEN 4 THEN 'Dispute'
        WHEN 5 THEN 'Unknown'
        WHEN 6 THEN 'Voided trip'
        ELSE 'Other'
    END AS payment_method,
    COUNT(*) AS trip_count
FROM taxi_trips
GROUP BY payment_type
ORDER BY trip_count DESC;


-- Tipping behavior for valid credit-card trips
SELECT
    COUNT(*) AS credit_card_trips,
    SUM(
        CASE
            WHEN tip_amount > 0 THEN 1
            ELSE 0
        END
    ) AS tipped_trips,
    AVG(tip_percentage) AS average_tip_percentage
FROM taxi_trips
WHERE payment_type = 1
  AND fare_amount > 0
  AND tip_amount >= 0
  AND tip_percentage IS NOT NULL;


-- ============================================================================
-- 7. OPERATIONAL PERFORMANCE
-- ============================================================================

-- Average operational metrics by pickup hour
--
-- Trips below 0.1 mile are excluded only from the fare-per-mile
-- calculation because near-zero distances create extreme ratios.
SELECT
    pickup_hour,
    AVG(average_speed_mph) AS average_speed_mph,
    AVG(
        CASE
            WHEN trip_distance >= 0.1
            THEN fare_per_mile
            ELSE NULL
        END
    ) AS average_fare_per_mile,
    AVG(fare_per_minute) AS average_fare_per_minute,
    COUNT(*) AS trip_count
FROM taxi_trips
GROUP BY pickup_hour
ORDER BY pickup_hour;


-- Rank operating hours by average speed
WITH hourly_speed AS (
    SELECT
        pickup_hour,
        AVG(average_speed_mph) AS average_speed_mph
    FROM taxi_trips
    WHERE average_speed_mph IS NOT NULL
    GROUP BY pickup_hour
)
SELECT
    pickup_hour,
    average_speed_mph,
    RANK() OVER (
        ORDER BY average_speed_mph DESC
    ) AS speed_rank
FROM hourly_speed
ORDER BY speed_rank;


-- Weekday versus weekend comparison
SELECT
    CASE
        WHEN is_weekend = 1 THEN 'Weekend'
        ELSE 'Weekday'
    END AS period,
    COUNT(*) AS trip_count,
    AVG(trip_duration_minutes) AS avg_duration_minutes,
    AVG(trip_distance) AS avg_distance_miles,
    AVG(average_speed_mph) AS avg_speed_mph,
    AVG(
        CASE
            WHEN total_amount > 0
            THEN total_amount
            ELSE NULL
        END
    ) AS avg_revenue_per_trip
FROM taxi_trips
GROUP BY is_weekend
ORDER BY is_weekend;


-- Revenue efficiency by pickup hour
SELECT
    pickup_hour,
    AVG(
        CASE
            WHEN trip_distance >= 0.1
            THEN fare_per_mile
            ELSE NULL
        END
    ) AS avg_fare_per_mile,
    AVG(fare_per_minute) AS avg_fare_per_minute
FROM taxi_trips
GROUP BY pickup_hour
ORDER BY pickup_hour;


-- ============================================================================
-- 8. FARE-PER-MILE VALIDATION
-- ============================================================================

-- Inspect overall fare-per-mile range
SELECT
    MIN(fare_per_mile) AS min_fare_per_mile,
    AVG(fare_per_mile) AS avg_fare_per_mile,
    MAX(fare_per_mile) AS max_fare_per_mile
FROM taxi_trips
WHERE fare_per_mile IS NOT NULL;


-- Distribution of very short trips
SELECT
    COUNT(*) AS total_trips,
    SUM(
        CASE
            WHEN trip_distance = 0 THEN 1
            ELSE 0
        END
    ) AS zero_distance,
    SUM(
        CASE
            WHEN trip_distance > 0
             AND trip_distance < 0.1
            THEN 1
            ELSE 0
        END
    ) AS under_01_mile,
    SUM(
        CASE
            WHEN trip_distance >= 0.1
             AND trip_distance < 0.5
            THEN 1
            ELSE 0
        END
    ) AS between_01_and_05,
    SUM(
        CASE
            WHEN trip_distance >= 0.5
            THEN 1
            ELSE 0
        END
    ) AS at_least_05_mile
FROM taxi_trips;


-- Fare-per-mile sensitivity: all positive-distance trips
SELECT
    COUNT(*) AS trip_count,
    AVG(fare_per_mile) AS avg_fare_per_mile
FROM taxi_trips
WHERE trip_distance > 0
  AND fare_per_mile IS NOT NULL;


-- Fare-per-mile sensitivity: minimum distance 0.1 mile
SELECT
    COUNT(*) AS trip_count,
    AVG(fare_per_mile) AS avg_fare_per_mile
FROM taxi_trips
WHERE trip_distance >= 0.1
  AND fare_per_mile IS NOT NULL;


-- Fare-per-mile sensitivity: minimum distance 0.5 mile
SELECT
    COUNT(*) AS trip_count,
    AVG(fare_per_mile) AS avg_fare_per_mile
FROM taxi_trips
WHERE trip_distance >= 0.5
  AND fare_per_mile IS NOT NULL;


-- Fare-per-mile sensitivity: minimum distance 1 mile
SELECT
    COUNT(*) AS trip_count,
    AVG(fare_per_mile) AS avg_fare_per_mile
FROM taxi_trips
WHERE trip_distance >= 1
  AND fare_per_mile IS NOT NULL;


-- ============================================================================
-- 9. ADVANCED BUSINESS ANALYSIS
-- ============================================================================

-- Rank pickup hours by demand
WITH hourly_demand AS (
    SELECT
        pickup_hour,
        COUNT(*) AS trip_count
    FROM taxi_trips
    GROUP BY pickup_hour
)
SELECT
    pickup_hour,
    trip_count,
    RANK() OVER (
        ORDER BY trip_count DESC
    ) AS demand_rank
FROM hourly_demand
ORDER BY demand_rank;


-- Rank pickup hours by total revenue
WITH hourly_revenue AS (
    SELECT
        pickup_hour,
        SUM(total_amount) AS total_revenue
    FROM taxi_trips
    WHERE total_amount > 0
    GROUP BY pickup_hour
)
SELECT
    pickup_hour,
    total_revenue,
    RANK() OVER (
        ORDER BY total_revenue DESC
    ) AS revenue_rank
FROM hourly_revenue
ORDER BY revenue_rank;


-- Compare demand rank and revenue rank by pickup hour
WITH hourly_metrics AS (
    SELECT
        pickup_hour,
        COUNT(*) AS trip_count,
        SUM(
            CASE
                WHEN total_amount > 0
                THEN total_amount
                ELSE 0
            END
        ) AS total_revenue
    FROM taxi_trips
    GROUP BY pickup_hour
),
ranked_metrics AS (
    SELECT
        pickup_hour,
        trip_count,
        total_revenue,
        RANK() OVER (
            ORDER BY trip_count DESC
        ) AS demand_rank,
        RANK() OVER (
            ORDER BY total_revenue DESC
        ) AS revenue_rank
    FROM hourly_metrics
)
SELECT
    pickup_hour,
    trip_count,
    total_revenue,
    demand_rank,
    revenue_rank
FROM ranked_metrics
ORDER BY pickup_hour;


-- Identify high-demand hours with below-average speed
WITH hourly_performance AS (
    SELECT
        pickup_hour,
        COUNT(*) AS trip_count,
        AVG(average_speed_mph) AS avg_speed_mph
    FROM taxi_trips
    WHERE average_speed_mph IS NOT NULL
    GROUP BY pickup_hour
),
overall_metrics AS (
    SELECT
        AVG(trip_count) AS avg_trip_count,
        AVG(avg_speed_mph) AS avg_hourly_speed
    FROM hourly_performance
)
SELECT
    hp.pickup_hour,
    hp.trip_count,
    hp.avg_speed_mph
FROM hourly_performance AS hp
CROSS JOIN overall_metrics AS om
WHERE hp.trip_count > om.avg_trip_count
  AND hp.avg_speed_mph < om.avg_hourly_speed
ORDER BY hp.trip_count DESC;


-- Best revenue-generating hours relative to trip volume
SELECT
    pickup_hour,
    COUNT(*) AS trip_count,
    SUM(total_amount) AS total_revenue,
    SUM(total_amount) / COUNT(*) AS avg_revenue_per_trip
FROM taxi_trips
WHERE total_amount > 0
GROUP BY pickup_hour
ORDER BY avg_revenue_per_trip DESC;


-- ============================================================================
-- 10. LOCATION AND ZONE ANALYSIS
-- ============================================================================

-- Location-level and route-level summary tables are generated by
-- src/07_create_sql_summaries.py to avoid repeatedly aggregating the
-- 11.7M-row fact table for expensive geographic analyses.


-- Most common pickup zones
SELECT
    z.Borough,
    z.Zone,
    s.trip_count
FROM pickup_location_summary AS s
INNER JOIN taxi_zones AS z
    ON s.PULocationID = z.LocationID
ORDER BY s.trip_count DESC
LIMIT 10;


-- Most common drop-off zones
WITH dropoff_counts AS (
    SELECT
        DOLocationID,
        SUM(trip_count) AS trip_count
    FROM route_summary
    GROUP BY DOLocationID
)
SELECT
    z.Borough,
    z.Zone,
    dc.trip_count
FROM dropoff_counts AS dc
INNER JOIN taxi_zones AS z
    ON dc.DOLocationID = z.LocationID
ORDER BY dc.trip_count DESC
LIMIT 10;


-- Trip demand by pickup borough
SELECT
    z.Borough,
    SUM(s.trip_count) AS trip_count
FROM pickup_location_summary AS s
INNER JOIN taxi_zones AS z
    ON s.PULocationID = z.LocationID
GROUP BY z.Borough
ORDER BY trip_count DESC;


-- Revenue by pickup borough
SELECT
    z.Borough,
    SUM(s.trip_count) AS trip_count,
    SUM(s.positive_revenue_trips) AS positive_revenue_trips,
    SUM(s.total_revenue) AS total_revenue,
    SUM(s.total_revenue)
        / NULLIF(
            SUM(s.positive_revenue_trips),
            0
        ) AS avg_revenue_per_trip
FROM pickup_location_summary AS s
INNER JOIN taxi_zones AS z
    ON s.PULocationID = z.LocationID
GROUP BY z.Borough
ORDER BY total_revenue DESC;


-- Most common origin-destination zone pairs
SELECT
    pu.Borough AS pickup_borough,
    pu.Zone AS pickup_zone,
    do.Borough AS dropoff_borough,
    do.Zone AS dropoff_zone,
    rs.trip_count
FROM route_summary AS rs
INNER JOIN taxi_zones AS pu
    ON rs.PULocationID = pu.LocationID
INNER JOIN taxi_zones AS do
    ON rs.DOLocationID = do.LocationID
ORDER BY rs.trip_count DESC
LIMIT 20;