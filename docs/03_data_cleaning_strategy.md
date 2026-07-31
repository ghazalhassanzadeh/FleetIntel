# Data Cleaning Strategy

**Project:** FleetIntel  
**Dataset:** NYC TLC Yellow Taxi Trip Records  
**Analysis Period:** March–May 2026  
**Document Version:** 1.0

---

## 1. Purpose

This document defines the cleaning rules implemented in `src/03_data_cleaning.py`.

Each rule is based on the findings documented in `02_data_validation_report.md`. Only confirmed data quality issues are addressed during the initial cleaning stage.

---

## 2. Cleaning Rules

| Validation Finding | Action | Justification | Status |
|--------------------|--------|---------------|--------|
| No duplicate records found | Keep all records | No duplicate removal is required. | Implemented |
| Trips with pickup after drop-off | Remove | Invalid timestamp order results in impossible trip durations. | Implemented |
| Trips outside the March–May 2026 analysis period | Remove | Outside the defined scope of this project. | Implemented |
| Negative trip durations | Removed through timestamp cleaning | Caused by invalid timestamp records. | Implemented |
| Create `trip_duration_minutes` | Create new column | Required for subsequent analysis and reporting. | Implemented |
| Zero-distance trips | Keep | Insufficient evidence to classify these records as invalid. | Pending |
| Extremely large trip distances | Investigate further | An outlier threshold will be defined after additional analysis. | Pending |
| Missing passenger count and related variables | Keep | Missing values follow a consistent Flex Fare pattern rather than occurring randomly. | Implemented |
| Passenger counts greater than six | Keep | Further investigation is required before deciding whether these records should be removed. | Pending |
| Negative monetary values | Keep | These values may represent refunds, corrections, or other valid financial transactions. | Implemented |
| Extreme monetary values | Investigate further | Cleaning thresholds should be based on business evidence rather than arbitrary limits. | Pending |

---

## 3. Cleaning Pipeline

The cleaning pipeline performs the following steps:

1. Load and combine the monthly datasets.
2. Remove trips with invalid timestamp order.
3. Remove trips outside the analysis period.
4. Create the `trip_duration_minutes` column.
5. Save the cleaned dataset.

---

## 4. Output

The cleaning pipeline produces:

```text
data/processed/clean_taxi_trips.parquet
```

This dataset is used in the subsequent stages of the project:

- Feature Engineering
- Exploratory Data Analysis (EDA)
- SQL
- Machine Learning
- Power BI
- Streamlit