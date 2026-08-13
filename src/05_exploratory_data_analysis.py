from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import pandas as pd


# =============================================================================
# FILE PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

INPUT_FILE = (
    PROCESSED_DATA_DIR
    / "feature_engineered_taxi_trips.parquet"
)

# =============================================================================
# LOAD FEATURE-ENGINEERED DATA
# =============================================================================

def load_feature_engineered_data() -> pd.DataFrame:
    """Load the feature-engineered taxi dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Feature-engineered dataset was not found:\n{INPUT_FILE}\n"
            "Run src/04_feature_engineering.py first."
        )

    df = pd.read_parquet(INPUT_FILE)

    print("=" * 80)
    print("LOAD FEATURE-ENGINEERED DATA")
    print("=" * 80)
    print(f"Rows loaded: {len(df):,}")
    print(f"Columns loaded: {df.shape[1]}")

    return df


# =============================================================================
# DEMAND ANALYSIS
# =============================================================================

def analyze_demand_by_hour(df: pd.DataFrame) -> None:
    """Analyze taxi trip demand by pickup hour."""

    hourly_demand = (
        df.groupby("pickup_hour")
        .size()
        .rename("trip_count")
        .reset_index()
    )

    peak_hour_row = hourly_demand.loc[
        hourly_demand["trip_count"].idxmax()
    ]

    lowest_hour_row = hourly_demand.loc[
        hourly_demand["trip_count"].idxmin()
    ]

    print("\n" + "=" * 80)
    print("DEMAND ANALYSIS - TRIPS BY HOUR")
    print("=" * 80)

    print(hourly_demand.to_string(index=False))

    print(
        f"\nPeak demand hour: "
        f"{int(peak_hour_row['pickup_hour']):02d}:00"
    )
    print(
        f"Trips during peak hour: "
        f"{int(peak_hour_row['trip_count']):,}"
    )

    print(
        f"\nLowest demand hour: "
        f"{int(lowest_hour_row['pickup_hour']):02d}:00"
    )
    print(
        f"Trips during lowest-demand hour: "
        f"{int(lowest_hour_row['trip_count']):,}"
    )

    print("\nInterpretation:")
    print(
        "Demand increases steadily from the early morning and reaches "
        f"its highest level at {int(peak_hour_row['pickup_hour']):02d}:00. "
        f"The lowest demand occurs at "
        f"{int(lowest_hour_row['pickup_hour']):02d}:00."
    )

    figure_path = FIGURES_DIR / "trips_by_hour.png"

    plt.figure(figsize=(12, 6))
    plt.bar(
        hourly_demand["pickup_hour"],
        hourly_demand["trip_count"],
        width=0.8,
        edgecolor="black",
    )

    plt.title("NYC Yellow Taxi Trips by Pickup Hour")
    plt.xlabel("Pickup Hour")
    plt.ylabel("Number of Trips")
    plt.xticks(range(24))
    plt.gca().yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


def analyze_demand_by_weekday(df: pd.DataFrame) -> None:
    """Analyze taxi trip demand by weekday."""

    weekday_demand = (
        df.groupby("pickup_day_name")
        .size()
        .rename("trip_count")
        .reset_index()
    )

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    weekday_demand["pickup_day_name"] = pd.Categorical(
        weekday_demand["pickup_day_name"],
        categories=weekday_order,
        ordered=True,
    )

    weekday_demand = weekday_demand.sort_values(
        "pickup_day_name"
    ).reset_index(drop=True)

    peak_day_row = weekday_demand.loc[
        weekday_demand["trip_count"].idxmax()
    ]

    lowest_day_row = weekday_demand.loc[
        weekday_demand["trip_count"].idxmin()
    ]

    print("\n" + "=" * 80)
    print("DEMAND ANALYSIS - TRIPS BY WEEKDAY")
    print("=" * 80)

    print(weekday_demand.to_string(index=False))
    print(
        f"\nBusiest weekday: "
        f"{peak_day_row['pickup_day_name']}"
    )
    print(
        f"Trips on busiest weekday: "
        f"{int(peak_day_row['trip_count']):,}"
    )

    print(
        f"\nQuietest weekday: "
        f"{lowest_day_row['pickup_day_name']}"
    )
    print(
        f"Trips on quietest weekday: "
        f"{int(lowest_day_row['trip_count']):,}"
    )

    print("\nInterpretation:")
    print(
        f"Taxi demand is lowest on "
        f"{lowest_day_row['pickup_day_name']} and increases toward "
        f"{peak_day_row['pickup_day_name']}, before declining later in the week."
    )

    figure_path = FIGURES_DIR / "trips_by_weekday.png"

    plt.figure(figsize=(10, 6))

    plt.bar(
        weekday_demand["pickup_day_name"],
        weekday_demand["trip_count"],
        width=0.7,
        edgecolor="black",
    )

    plt.title("NYC Yellow Taxi Trips by Pickup Weekday")
    plt.xlabel("Weekday")
    plt.ylabel("Number of Trips")

    plt.gca().yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


# =============================================================================
# TRIP CHARACTERISTICS
# =============================================================================

def analyze_trip_duration(df: pd.DataFrame) -> None:
    """Analyze the distribution of taxi trip durations."""

    trip_duration = df["trip_duration_minutes"]

    mean_duration = trip_duration.mean()
    median_duration = trip_duration.median()
    percentile_95 = trip_duration.quantile(0.95)

    print("\n" + "=" * 80)
    print("TRIP CHARACTERISTICS - TRIP DURATION")
    print("=" * 80)

    print(f"Average trip duration: {mean_duration:.2f} minutes")
    print(f"Median trip duration: {median_duration:.2f} minutes")
    print(f"95th percentile: {percentile_95:.2f} minutes")

    print("\nInterpretation:")
    print(
        f"A typical taxi trip lasts about {median_duration:.1f} minutes. "
        f"The average is higher at {mean_duration:.1f} minutes, indicating "
        "a right-skewed distribution driven by longer trips."
    )   

    figure_path = FIGURES_DIR / "trip_duration_distribution.png"

    plt.figure(figsize=(10, 6))

    plt.hist(
        trip_duration,
        bins=50,
        range=(0, percentile_95),
    )

    plt.axvline(
        median_duration,
        linestyle="--",
        label=f"Median: {median_duration:.1f} min",
    )

    plt.title("Distribution of NYC Yellow Taxi Trip Duration")
    plt.xlabel("Trip Duration (Minutes)")
    plt.ylabel("Number of Trips")

    plt.gca().yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


def analyze_trip_distance(df: pd.DataFrame) -> None:
    """Analyze the distribution of taxi trip distances."""

    positive_distance = df.loc[
        df["trip_distance"] > 0,
        "trip_distance",
    ]

    mean_distance = positive_distance.mean()
    median_distance = positive_distance.median()
    percentile_95 = positive_distance.quantile(0.95)

    print("\n" + "=" * 80)
    print("TRIP CHARACTERISTICS - TRIP DISTANCE")
    print("=" * 80)

    print(f"Average trip distance: {mean_distance:.2f} miles")
    print(f"Median trip distance: {median_distance:.2f} miles")
    print(f"95th percentile: {percentile_95:.2f} miles")

    print("\nInterpretation:")
    print(
        f"A typical positive-distance trip covers about "
        f"{median_distance:.1f} miles. The higher average of "
        f"{mean_distance:.1f} miles indicates a right-skewed distribution "
        "with a smaller number of substantially longer trips."
    )

    figure_path = FIGURES_DIR / "trip_distance_distribution.png"

    plt.figure(figsize=(10, 6))

    plt.hist(
        positive_distance,
        bins=50,
        range=(0, percentile_95),
    )

    plt.axvline(
        median_distance,
        linestyle="--",
        label=f"Median: {median_distance:.1f} miles",
    )

    plt.title("Distribution of NYC Yellow Taxi Trip Distance")
    plt.xlabel("Trip Distance (Miles)")
    plt.ylabel("Number of Trips")

    plt.gca().yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


def analyze_distance_duration_relationship(
    df: pd.DataFrame,
) -> None:
    """Analyze the relationship between trip distance and duration."""

    relationship_df = df.loc[
        (df["trip_distance"] > 0)
        & (df["trip_duration_minutes"] > 0),
        [
            "trip_distance",
            "trip_duration_minutes",
        ],
    ].copy()

    distance_99 = relationship_df["trip_distance"].quantile(0.99)
    duration_99 = relationship_df[
        "trip_duration_minutes"
    ].quantile(0.99)

    plot_data = relationship_df[
        (relationship_df["trip_distance"] <= distance_99)
        & (
            relationship_df["trip_duration_minutes"]
            <= duration_99
        )
    ]

    correlation = relationship_df[
        [
            "trip_distance",
            "trip_duration_minutes",
        ]
    ].corr().iloc[0, 1]

    print("\n" + "=" * 80)
    print("TRIP CHARACTERISTICS - DISTANCE VS DURATION")
    print("=" * 80)

    print(
        f"Pearson correlation between distance and duration: "
        f"{correlation:.3f}"
    )

    print("\nInterpretation:")
    print(
        f"Trip distance and duration show a strong positive relationship "
        f"(Pearson r = {correlation:.3f}), meaning longer-distance trips "
        "generally also require more travel time."
    )

    sample_size = min(
        100_000,
        len(plot_data),
    )

    plot_sample = plot_data.sample(
        n=sample_size,
        random_state=42,
    )

    figure_path = (
        FIGURES_DIR
        / "trip_distance_vs_duration.png"
    )

    plt.figure(figsize=(10, 6))

    plt.scatter(
        plot_sample["trip_distance"],
        plot_sample["trip_duration_minutes"],
        alpha=0.15,
        s=10,
    )

    plt.title("NYC Yellow Taxi Trip Distance vs. Duration")
    plt.xlabel("Trip Distance (Miles)")
    plt.ylabel("Trip Duration (Minutes)")

    plt.gca().set_axisbelow(True)
    plt.grid(
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


# =============================================================================
# REVENUE ANALYSIS
# =============================================================================

def analyze_trip_revenue(df: pd.DataFrame) -> None:
    """Analyze the distribution of positive trip revenue."""

    positive_revenue = df.loc[
        df["total_amount"] > 0,
        "total_amount",
    ]

    mean_revenue = positive_revenue.mean()
    median_revenue = positive_revenue.median()
    percentile_95 = positive_revenue.quantile(0.95)

    print("\n" + "=" * 80)
    print("REVENUE ANALYSIS - TRIP REVENUE")
    print("=" * 80)

    print(f"Average total amount: ${mean_revenue:.2f}")
    print(f"Median total amount: ${median_revenue:.2f}")
    print(f"95th percentile: ${percentile_95:.2f}")

    print("\nInterpretation:")
    print(
        f"The median positive trip revenue is ${median_revenue:.2f}, while "
        f"the higher average of ${mean_revenue:.2f} indicates that "
        "higher-value trips pull the revenue distribution upward."
    )

    figure_path = FIGURES_DIR / "trip_revenue_distribution.png"

    plt.figure(figsize=(10, 6))

    plt.hist(
        positive_revenue,
        bins=50,
        range=(0, percentile_95),
    )

    plt.axvline(
        median_revenue,
        linestyle="--",
        label=f"Median: ${median_revenue:.2f}",
    )

    plt.title("Distribution of NYC Yellow Taxi Trip Revenue")
    plt.xlabel("Total Amount ($)")
    plt.ylabel("Number of Trips")

    plt.gca().yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


def analyze_revenue_by_hour(df: pd.DataFrame) -> None:
    """Analyze positive taxi revenue by pickup hour."""

    revenue_data = df.loc[
        df["total_amount"] > 0
    ]

    hourly_revenue = (
        revenue_data.groupby("pickup_hour")["total_amount"]
        .sum()
        .rename("total_revenue")
        .reset_index()
    )

    peak_revenue_row = hourly_revenue.loc[
        hourly_revenue["total_revenue"].idxmax()
    ]

    print("\n" + "=" * 80)
    print("REVENUE ANALYSIS - REVENUE BY HOUR")
    print("=" * 80)

    print(hourly_revenue.to_string(index=False))

    print(
        f"\nHighest-revenue pickup hour: "
        f"{int(peak_revenue_row['pickup_hour']):02d}:00"
    )
    print(
        f"Revenue during that hour: "
        f"${peak_revenue_row['total_revenue']:,.2f}"
    )

    print("\nInterpretation:")
    print(
        f"Revenue reaches its highest level at "
        f"{int(peak_revenue_row['pickup_hour']):02d}:00, one hour before "
        "the 18:00 peak in trip demand. This indicates that the "
        "highest-demand hour is not necessarily the highest-revenue hour."
    )

    figure_path = FIGURES_DIR / "revenue_by_hour.png"

    plt.figure(figsize=(12, 6))

    plt.bar(
        hourly_revenue["pickup_hour"],
        hourly_revenue["total_revenue"],
        width=0.8,
    )

    plt.title("NYC Yellow Taxi Revenue by Pickup Hour")
    plt.xlabel("Pickup Hour")
    plt.ylabel("Total Revenue ($)")
    plt.xticks(range(24))

    plt.gca().yaxis.set_major_formatter(
        StrMethodFormatter("${x:,.0f}")
    )

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


def analyze_payment_methods(df: pd.DataFrame) -> None:
    """Analyze the distribution of taxi payment methods."""

    payment_labels = {
        0: "Flex Fare",
        1: "Credit card",
        2: "Cash",
        3: "No charge",
        4: "Dispute",
        5: "Unknown",
        6: "Voided trip",
    }

    payment_counts = (
        df["payment_type"]
        .value_counts()
        .rename_axis("payment_type")
        .reset_index(name="trip_count")
    )

    payment_counts["payment_method"] = (
        payment_counts["payment_type"]
        .map(payment_labels)
        .fillna("Other")
    )

    payment_counts["trip_percentage"] = (
        payment_counts["trip_count"]
        / payment_counts["trip_count"].sum()
        * 100
    )

    payment_counts = payment_counts.sort_values(
        "trip_count",
        ascending=False,
    ).reset_index(drop=True)

    print("\n" + "=" * 80)
    print("REVENUE ANALYSIS - PAYMENT METHODS")
    print("=" * 80)

    print(
        payment_counts[
            [
                "payment_method",
                "trip_count",
                "trip_percentage",
            ]
        ].to_string(
            index=False,
            formatters={
                "trip_percentage": lambda x: f"{x:.2f}%"
            },
        )
    )

    figure_path = FIGURES_DIR / "payment_methods.png"

    plt.figure(figsize=(10, 6))

    plt.bar(
        payment_counts["payment_method"],
        payment_counts["trip_count"],
        width=0.7,
    )

    plt.title("NYC Yellow Taxi Trips by Payment Method")
    plt.xlabel("Payment Method")
    plt.ylabel("Number of Trips")

    plt.xticks(
        rotation=30,
        ha="right",
    )

    plt.gca().yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


def analyze_tipping_behavior(df: pd.DataFrame) -> None:
    """Analyze tipping behavior for valid credit-card trips."""

    valid_tips = df.loc[
        (df["payment_type"] == 1)
        & (df["fare_amount"] > 0)
        & (df["tip_amount"] >= 0)
        & (df["tip_percentage"].notna()),
        "tip_percentage",
    ]

    median_tip_percentage = valid_tips.median()
    percentile_95 = valid_tips.quantile(0.95)

    tipped_trip_percentage = (
        (valid_tips > 0).mean() * 100
    )

    print("\n" + "=" * 80)
    print("REVENUE ANALYSIS - TIPPING BEHAVIOR")
    print("=" * 80)

    print(
        f"Median tip percentage: "
        f"{median_tip_percentage:.2f}%"
    )
    print(
        f"Credit-card trips with a positive recorded tip: "
        f"{tipped_trip_percentage:.2f}%"
    )
    print(
        f"95th percentile of tip percentage: "
        f"{percentile_95:.2f}%"
    )

    print("\nInterpretation:")
    print(
        f"Among valid credit-card trips, "
        f"{tipped_trip_percentage:.1f}% include a positive recorded tip, "
        f"with a median tip rate of {median_tip_percentage:.1f}%."
    )

    figure_path = FIGURES_DIR / "tip_percentage_distribution.png"

    plt.figure(figsize=(10, 6))

    plt.hist(
        valid_tips,
        bins=50,
        range=(0, percentile_95),
    )

    plt.axvline(
        median_tip_percentage,
        linestyle="--",
        label=f"Median: {median_tip_percentage:.1f}%",
    )

    plt.title("Distribution of NYC Yellow Taxi Tip Percentage")
    plt.xlabel("Tip Percentage")
    plt.ylabel("Number of Trips")

    plt.gca().yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


# =============================================================================
# OPERATIONAL PERFORMANCE
# =============================================================================

def analyze_average_speed(df: pd.DataFrame) -> None:
    """Analyze the distribution of average taxi trip speeds."""

    valid_speed = df.loc[
        df["average_speed_mph"].notna(),
        "average_speed_mph",
    ]

    mean_speed = valid_speed.mean()
    median_speed = valid_speed.median()
    percentile_95 = valid_speed.quantile(0.95)

    print("\n" + "=" * 80)
    print("OPERATIONAL PERFORMANCE - AVERAGE SPEED")
    print("=" * 80)

    print(f"Average trip speed: {mean_speed:.2f} mph")
    print(f"Median trip speed: {median_speed:.2f} mph")
    print(f"95th percentile: {percentile_95:.2f} mph")

    print("\nInterpretation:")
    print(
        f"The median trip speed is {median_speed:.1f} mph, compared with "
        f"an average of {mean_speed:.1f} mph, reflecting generally low "
        "urban operating speeds across taxi trips."
    )

    figure_path = FIGURES_DIR / "average_speed_distribution.png"

    plt.figure(figsize=(10, 6))

    plt.hist(
        valid_speed,
        bins=50,
        range=(0, percentile_95),
    )

    plt.axvline(
        median_speed,
        linestyle="--",
        label=f"Median: {median_speed:.1f} mph",
    )

    plt.title("Distribution of NYC Yellow Taxi Average Trip Speed")
    plt.xlabel("Average Speed (mph)")
    plt.ylabel("Number of Trips")

    plt.gca().yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


def analyze_speed_by_hour(df: pd.DataFrame) -> None:
    """Analyze median average trip speed by pickup hour."""

    speed_by_hour = (
        df.dropna(subset=["average_speed_mph"])
        .groupby("pickup_hour")["average_speed_mph"]
        .median()
        .rename("median_speed_mph")
        .reset_index()
    )

    fastest_hour_row = speed_by_hour.loc[
        speed_by_hour["median_speed_mph"].idxmax()
    ]

    slowest_hour_row = speed_by_hour.loc[
        speed_by_hour["median_speed_mph"].idxmin()
    ]

    print("\n" + "=" * 80)
    print("OPERATIONAL PERFORMANCE - SPEED BY HOUR")
    print("=" * 80)

    print(speed_by_hour.to_string(index=False))

    print(
        f"\nFastest median-speed hour: "
        f"{int(fastest_hour_row['pickup_hour']):02d}:00"
    )
    print(
        f"Median speed: "
        f"{fastest_hour_row['median_speed_mph']:.2f} mph"
    )

    print(
        f"\nSlowest median-speed hour: "
        f"{int(slowest_hour_row['pickup_hour']):02d}:00"
    )
    print(
        f"Median speed: "
        f"{slowest_hour_row['median_speed_mph']:.2f} mph"
    )

    print("\nInterpretation:")
    print(
        f"Median trip speed is highest at "
        f"{int(fastest_hour_row['pickup_hour']):02d}:00 "
        f"({fastest_hour_row['median_speed_mph']:.1f} mph) and lowest at "
        f"{int(slowest_hour_row['pickup_hour']):02d}:00 "
        f"({slowest_hour_row['median_speed_mph']:.1f} mph), showing a clear "
        "variation in operating conditions throughout the day."
    )

    figure_path = FIGURES_DIR / "median_speed_by_hour.png"

    plt.figure(figsize=(12, 6))

    plt.plot(
        speed_by_hour["pickup_hour"],
        speed_by_hour["median_speed_mph"],
        marker="o",
    )

    plt.title("Median NYC Yellow Taxi Trip Speed by Pickup Hour")
    plt.xlabel("Pickup Hour")
    plt.ylabel("Median Average Speed (mph)")
    plt.xticks(range(24))

    plt.gca().set_axisbelow(True)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nFigure saved to:\n{figure_path}")


def analyze_fare_efficiency(df: pd.DataFrame) -> None:
    """Analyze fare efficiency using fare per mile and fare per minute."""

    valid_fare_per_mile = df.loc[
        (df["fare_per_mile"].notna())
        & (df["fare_per_mile"] > 0),
        "fare_per_mile",
    ]

    valid_fare_per_minute = df.loc[
        (df["fare_per_minute"].notna())
        & (df["fare_per_minute"] > 0),
        "fare_per_minute",
    ]

    median_fare_per_mile = valid_fare_per_mile.median()
    median_fare_per_minute = valid_fare_per_minute.median()

    print("\n" + "=" * 80)
    print("OPERATIONAL PERFORMANCE - FARE EFFICIENCY")
    print("=" * 80)

    print(
        f"Median fare per mile: "
        f"${median_fare_per_mile:.2f}"
    )
    print(
        f"Median fare per minute: "
        f"${median_fare_per_minute:.2f}"
    )

    print("\nInterpretation:")
    print(
        f"The median fare rate is ${median_fare_per_mile:.2f} per mile "
        f"and ${median_fare_per_minute:.2f} per minute, providing two "
        "complementary measures of trip-level fare efficiency."
    )


def analyze_weekday_weekend_performance(
    df: pd.DataFrame,
) -> None:
    """Compare key trip metrics between weekdays and weekends."""

    comparison = (
        df.groupby("is_weekend")
        .agg(
            trip_count=("trip_duration_minutes", "size"),
            median_duration_minutes=(
                "trip_duration_minutes",
                "median",
            ),
            median_distance_miles=(
                "trip_distance",
                "median",
            ),
            median_speed_mph=(
                "average_speed_mph",
                "median",
            ),
            median_total_amount=(
                "total_amount",
                "median",
            ),
        )
        .reset_index()
    )

    comparison["period"] = comparison["is_weekend"].map(
        {
            False: "Weekday",
            True: "Weekend",
        }
    )

    comparison = comparison[
        [
            "period",
            "trip_count",
            "median_duration_minutes",
            "median_distance_miles",
            "median_speed_mph",
            "median_total_amount",
        ]
    ]

    print("\n" + "=" * 80)
    print("OPERATIONAL PERFORMANCE - WEEKDAY VS WEEKEND")
    print("=" * 80)

    print(
        comparison.to_string(
            index=False,
            formatters={
                "trip_count": lambda x: f"{x:,.0f}",
                "median_duration_minutes": lambda x: f"{x:.2f}",
                "median_distance_miles": lambda x: f"{x:.2f}",
                "median_speed_mph": lambda x: f"{x:.2f}",
                "median_total_amount": lambda x: f"${x:.2f}",
            },
        )
    )

    print("\nInterpretation:")
    print(
        "Weekend trips are typically slightly shorter in duration but longer "
        "in distance and faster than weekday trips, while weekday trips have "
        "a slightly higher median total amount."
    )


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def main() -> None:
    """Run the exploratory data analysis workflow."""

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_feature_engineered_data()

    # Demand analysis
    analyze_demand_by_hour(df)
    analyze_demand_by_weekday(df)

    # Trip characteristics
    analyze_trip_duration(df)
    analyze_trip_distance(df)
    analyze_distance_duration_relationship(df)

    # Revenue analysis
    analyze_trip_revenue(df)
    analyze_revenue_by_hour(df)
    analyze_payment_methods(df)
    analyze_tipping_behavior(df)

    # Operational performance
    analyze_average_speed(df)
    analyze_speed_by_hour(df)
    analyze_fare_efficiency(df)
    analyze_weekday_weekend_performance(df)


if __name__ == "__main__":
    main()