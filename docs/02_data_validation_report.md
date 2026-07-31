# Data Validation Report

**Project:** FleetIntel  
**Dataset:** NYC TLC Yellow Taxi Trip Records  
**Analysis Period:** March–May 2026  
**Document Version:** 1.0

---

## 1. Purpose

Before applying any cleaning or transformation steps, the raw NYC Yellow Taxi trip records were systematically validated to assess their quality and identify potential issues.

The objective of this phase was not to clean the data immediately, but to understand the dataset, distinguish expected data characteristics from actual data quality problems, and establish evidence-based cleaning decisions for the ETL pipeline.

The validation process was implemented in **`src/02_data_validation.py`**, where each data quality check was developed, reviewed, and documented before defining any cleaning rules.

---

## 2. Validation Workflow

### 2.1 Duplicate Records

#### Objective

Determine whether duplicate trips exist after combining the three monthly datasets.

#### Validation Checks

- Merge the three monthly datasets into a single DataFrame.
- Check for exact duplicate rows.

#### Findings

- Exact duplicate records: **0**

#### Decision

No duplicate removal is required.

---

### 2.2 Timestamp Validation

#### Objective

Verify that trip timestamps are logically consistent and fall within the project's analysis period.

#### Validation Checks

- Check whether pickup occurs before drop-off.
- Review the overall pickup and drop-off date ranges.
- Identify records outside the analysis period.

#### Findings

- **2 trips** had pickup timestamps after the drop-off timestamp.
- **8 trips** had pickup dates before **2026**, although this project only analyzes trips from **March to May 2026**.

#### Decision

- Remove the two records with invalid timestamp order.
- Remove the eight records outside the project period.

#### Reason

These records represent clear data inconsistencies and would negatively affect any time-based analysis.

---

### 2.3 Trip Duration Validation

#### Objective

Evaluate trip durations and identify unrealistic values.

#### Validation Checks

Trip duration was calculated using the pickup and drop-off timestamps.

The following checks were performed:

- Summary statistics
- Trips shorter than one minute
- Trips longer than six hours
- Manual review of the shortest and longest trips

#### Findings

The validation identified:

- Negative trip durations caused by the invalid timestamp records.
- Trips lasting several days while having relatively small fares.
- A large number of trips shorter than one minute.

#### Decision

- Invalid durations will be resolved through timestamp cleaning.
- Extremely long trips require further investigation before defining an outlier threshold.
- Very short trips will be retained until additional business validation is performed.

---

### 2.4 Trip Distance Validation

#### Objective

Assess the quality of recorded trip distances.

#### Validation Checks

- Summary statistics
- Negative distances
- Zero-distance trips
- Manual review of the largest recorded distances

#### Findings

- Negative trip distances: **0**
- Zero-distance trips: **327,756**
- Several trips exceeded **250,000 miles** while having realistic trip durations and fares.

#### Decision

- Keep zero-distance trips for further investigation.
- Investigate unrealistic distance values before defining an outlier threshold.

#### Reason

The combination of extremely large distances with otherwise realistic trip durations strongly suggests data recording errors rather than valid taxi trips.

---

### 2.5 Passenger Count Validation

#### Objective

Validate passenger-count values and identify unrealistic records.

#### Validation Checks

- Summary statistics
- Missing values
- Zero passengers
- Negative values
- Passenger counts greater than six

#### Findings

- Missing values: **2,700,905**
- Zero passengers: **37,192**
- Negative passenger counts: **0**
- Passenger counts greater than six: **11**

The majority of trips contained one or two passengers.

#### Decision

- Keep missing passenger counts until missing-value patterns are fully evaluated.
- Investigate passenger counts greater than six before determining whether they represent valid trips or data errors.
- Keep zero passenger counts pending further investigation.

---

### 2.6 Monetary Variables Validation

#### Objective

Assess the quality of all monetary variables used for financial analysis.

#### Validation Checks

The following variables were validated:

- Fare Amount
- Tip Amount
- Total Amount
- Tolls
- Extra Charges
- Taxes
- Airport Fee
- Congestion Surcharge
- CBD Congestion Fee

For each variable, the following checks were performed:

- Summary statistics
- Negative values
- Zero values
- Manual review of the largest recorded values

#### Findings

The validation identified:

- Negative values in several monetary variables.
- Extremely large monetary values in a small number of records.
- Large numbers of zero values for optional charges such as tips and tolls.

#### Decision

- Do not remove negative monetary values during the initial cleaning stage.
- Investigate extreme monetary values before defining outlier thresholds.
- Keep zero values, as many represent legitimate business scenarios.

#### Reason

Negative values may represent refunds, corrections, or other valid financial transactions rather than data quality issues.

---

### 2.7 Missing Values Validation

#### Objective

Determine whether missing values occur randomly or follow a consistent pattern.

#### Validation Checks

- Summarize missing values across all variables.
- Compare variables with identical missing-value counts.
- Investigate the characteristics of affected records.

#### Findings

The following variables each contained **2,700,905 missing values (22.75%)**:

- passenger_count
- RatecodeID
- store_and_fwd_flag
- congestion_surcharge
- Airport_fee

Further investigation showed that:

- All missing values occurred in exactly the same rows.
- All affected records had **payment_type = 0**.

#### Decision

Keep these records.

#### Reason

The missing values follow a consistent pattern and appear to represent a specific transaction type (commonly referred to as **Flex Fare trips**) rather than random missing data.

---

## 3. Proposed Cleaning Decisions

| Validation Area | Proposed Decision |
|-----------------|-------------------|
| Duplicate records | Keep all records |
| Invalid timestamp order | Remove |
| Records outside project period | Remove |
| Invalid trip durations | Resolved through timestamp cleaning |
| Zero-distance trips | Keep for further investigation |
| Unrealistic trip distances | Investigate before defining thresholds |
| Missing passenger counts | Keep |
| Passenger counts greater than six | Investigate |
| Negative monetary values | Keep |
| Extreme monetary values | Investigate before defining thresholds |
| Flex Fare missing values | Keep |

---

## 4. Transition to Data Cleaning

The validation phase provided a structured assessment of the raw dataset and established the data quality issues that require attention before analysis.

The next stage of the ETL pipeline (`src/03_data_cleaning.py`) will implement the confirmed cleaning decisions documented in this report.

Only cleaning rules supported by the validation findings will be implemented. This approach ensures that every transformation in the ETL pipeline is transparent, reproducible, and based on observed data quality issues rather than assumptions.