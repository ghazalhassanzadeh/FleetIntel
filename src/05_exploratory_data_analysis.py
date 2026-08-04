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

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

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


# =============================================================================
# TRIP CHARACTERISTICS
# =============================================================================


# =============================================================================
# REVENUE ANALYSIS
# =============================================================================


# =============================================================================
# OPERATIONAL PERFORMANCE
# =============================================================================


# =============================================================================
# MAIN WORKFLOW
# =============================================================================


def main() -> None:
    """Run the exploratory data analysis workflow."""

    df = load_feature_engineered_data()
    analyze_demand_by_hour(df)


if __name__ == "__main__":
    main()


