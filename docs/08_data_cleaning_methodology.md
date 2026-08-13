# Data Cleaning Methodology

This document summarizes the main data-quality checks and cleaning decisions used in FleetIntel.

## Source Data

The project uses NYC TLC Yellow Taxi Trip Records for March, April, and May 2026.

Before cleaning, the combined raw dataset contained **11,874,527 records**.

## Validation

The raw data was checked for:

- duplicate records
- invalid pickup and drop-off timestamps
- records outside the project period
- invalid and extreme trip durations
- zero and extreme trip distances
- implausible distance-duration combinations
- missing passenger counts
- unusual passenger counts
- negative and extreme monetary values
- shared missing-value patterns

## Cleaning Rules

### Project Period

Only trips with pickup timestamps between March 1 and May 31, 2026 were retained.

### Timestamp Order

Trips where the pickup timestamp occurred after the drop-off timestamp were removed.

### Trip Duration

Trip duration was calculated from the pickup and drop-off timestamps.

Trips were removed when:

- duration was less than or equal to 0 minutes
- duration exceeded 360 minutes

The six-hour upper threshold was used as a conservative limit to remove clearly implausible multi-hour and multi-day records while retaining unusual but potentially valid trips.

### Implausible Trip Speeds

Average speed was calculated from trip distance and duration.

Trips with an implied average speed above **100 mph** were removed. The deliberately high threshold was used to identify clearly inconsistent distance-duration combinations without aggressively filtering unusual trips.

### Zero-Distance Trips

Zero-distance records were retained because they may represent valid TLC records such as cancelled or administrative trips.

They are excluded where a positive distance is required for a specific metric, such as fare per mile or average speed.

### Missing Passenger Counts

Missing passenger counts were retained rather than imputed or used as a reason to remove the entire trip.

The missing values were strongly associated with a broader reporting pattern across several TLC fields, so assigning an artificial passenger count would introduce information that is not present in the source data.

### Financial Records

Negative monetary values were not used as a reason to remove the complete trip record.

For revenue and tipping analyses, metric-specific filters are applied instead. For example, revenue distributions use positive total amounts, and tipping analysis focuses on valid credit-card trips.

## Final Dataset

After cleaning, the dataset contains:

**11,718,495 trips**

This corresponds to approximately **98.7% of the original records**, preserving the large majority of the source data while removing records that could materially distort duration, speed, and operational analyses.