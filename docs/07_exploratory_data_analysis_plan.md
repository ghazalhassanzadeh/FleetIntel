# Exploratory Data Analysis Plan

## Purpose

The purpose of the exploratory data analysis (EDA) phase is to understand the characteristics of the cleaned taxi dataset and identify patterns, trends, and relationships that provide business value.

The findings from this phase will support the SQL analysis, Power BI dashboard, Streamlit application, and machine learning models developed later in the project.

---

# Business Questions

The exploratory analysis will answer the following questions.

## Demand

- When are taxi trips most frequent?
- How does demand vary by hour of the day?
- How does demand differ between weekdays and weekends?

## Revenue

- During which hours is the highest revenue generated?
- How do fares vary across trip distances?
- What are the tipping patterns?

## Trip Characteristics

- What is the distribution of trip duration?
- What is the distribution of trip distance?
- What are the most common passenger counts?

## Operational Performance

- What is the average trip speed?
- How does average speed vary throughout the day?
- Which pickup and drop-off zones are busiest?

---

# Planned Visualizations

| Business Question | Visualization |
|-------------------|---------------|
| Trips by hour | Bar chart |
| Trips by weekday | Bar chart |
| Weekend vs weekday demand | Bar chart |
| Trip distance distribution | Histogram |
| Trip duration distribution | Histogram |
| Fare distribution | Histogram |
| Revenue by hour | Line chart |
| Average fare by hour | Line chart |
| Average speed by hour | Line chart |
| Passenger count distribution | Bar chart |
| Top pickup zones | Horizontal bar chart |
| Top drop-off zones | Horizontal bar chart |
| Fare vs distance | Scatter plot |
| Tip percentage distribution | Histogram |

---

# Expected Deliverables

The EDA phase will produce:

- Summary statistics
- Business insights
- Publication-quality visualizations
- Reusable code for future analysis
- Findings that support dashboard development and machine learning