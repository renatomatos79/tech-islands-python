import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Mapping month names
MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

# ------------------------------------------------------------------------------
# This function loads the output.json file and mapp it into a List of Dicionary
# So then, we are able to access any JSON field using row.get("Field Name")
# ------------------------------------------------------------------------------
def load_results(json_path: Path) -> List[Dict[str, Any]]:
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# -------------------------------------------------------------------
# TEXTUAL SUMMARIES
# -------------------------------------------------------------------
def summarize_basic(results: List[Dict[str, Any]]) -> None:
    total = len(results)
    success_count = sum(1 for r in results if r.get("Success"))
    error_count = total - success_count

    print("=== OVERALL SUMMARY ===")
    print(f"Total records:      {total}")
    print(f"Successful records: {success_count}")
    print(f"Failed records:     {error_count}")
    print()


def summarize_errors(results: List[Dict[str, Any]], max_examples: int = 10) -> None:
    """
    Prints a human-readable summary of failed document extractions.
    """

    # Extract only the entries where the pipeline flagged the item as failed.
    # We inspect the "Success" boolean field that phase01 generated.
    # If Success == False, we consider it a failure.
    failures = [r for r in results if not r.get("Success")]

    # If we don't have any failures at all, we simply show a friendly message
    # and exit early because there's nothing else to enumerate.
    if not failures:
        print("=== ERRORS ===")
        print("No failures. :)")
        print()
        return

    print("=== ERRORS (examples) ===")

    # We only show up to `max_examples` errors to avoid spamming the console.
    for idx, item in enumerate(failures[:max_examples], start=1):

        # We try to extract optional metadata to help debugging:
        #   - source: which file failed (path/filename)
        #   - ERROR: the exception message captured during extraction
        source = item.get("source", "<unknown>")
        error = item.get("ERROR", "<no error message>")

        # Example output:
        #  1. File: case_041.pdf
        #      Error: NetworkTimeout: llama backend not responding
        print(f"{idx:2}. File: {source}")
        print(f"    Error: {error}")

    # If the number of failures was greater than what we printed,
    if len(failures) > max_examples:
        print(f"... and {len(failures) - max_examples} more failures.")

    # Final newline for cleaner terminal formatting
    print()


def summarize_by_city(results: List[Dict[str, Any]]) -> None:
    """
    Aggregates the number of successful cases per city and prints a summary table.
    """

    # We use a Counter, which is a convenient dictionary subclass that automatically counts occurrences of keys. 
    # Example:
    #   counter["São Paulo"] += 1
    #   counter["Santos"] += 1
    # and so on.
    counter: Counter[str] = Counter()

    # Iterate through all result records 
    for r in results:
        # Skip rows flagged as failed extractions ("Success" == False),
        if not r.get("Success"):
            continue

        # Extract the city field. If the field is None or missing,
        # we normalize it to "Unknown" so it still contributes to the count.
        city = r.get("city") or "Unknown"

        # Increase the count for that city.
        counter[city] += 1

    print("=== CASES BY CITY ===")

    # We print results sorted by frequency, highest first.
    # Counter.most_common() returns items ordered by descending count.
    for city, count in counter.most_common():
        print(f"{city:<25} -> {count}")

    # Blank line at the end for better terminal readability.
    print()



def summarize_by_occurrence(results: List[Dict[str, Any]]) -> None:
    counter: Counter[str] = Counter()

    for r in results:
        if not r.get("Success"):
            continue
        occurrence = r.get("occurrence") or "Unknown"
        counter[occurrence] += 1

    print("=== CASES BY OCCURRENCE TYPE ===")
    for occ, count in counter.most_common():
        print(f"{occ:<30} -> {count}")
    print()


def summarize_by_city_and_year(results: List[Dict[str, Any]]) -> None:
    grouped: Dict[str, Counter[int]] = defaultdict(Counter)

    for r in results:
        if not r.get("Success"):
            continue
        city = r.get("city") or "Unknown"
        year = r.get("year") or 0
        grouped[city][year] += 1

    print("=== CASES BY CITY AND YEAR ===")
    for city, year_counter in grouped.items():
        print(f"- {city}:")
        for year, count in sorted(year_counter.items()):
            if year == 0:
                label = "Unknown year"
            else:
                label = str(year)
            print(f"    {label:<12} -> {count}")
    print()

# -------------------------------------------------------------------
# PLOTTING dashboard using PLOTLY library already mentioned in the folder 00
# -------------------------------------------------------------------
def build_dashboard(results: List[Dict[str, Any]]) -> None:
    """
    Builds and renders a multi-panel analytical dashboard using Plotly.
    The dashboard summarizes crime reports across different dimensions
    (city, occurrence type, time, and year-over-year comparisons).
    """

    # Convert list of dictionaries into a DataFrame for easier grouping,
    # aggregation, pivoting and sorting.
    df = pd.DataFrame(results)

    # If nothing came from phase01, there is no value in plotting.
    if df.empty:
        print("No data available to plot.")
        return

    # Keep only successfully processed documents.
    df_success = df[df["Success"] == True].copy()  # noqa: E712 -> explicit equality for clarity

    # If all records failed, we skip plotting to avoid empty charts.
    if df_success.empty:
        print("No successful records to plot.")
        return

    # ------------------------------
    # Aggregations for charts
    # ------------------------------
    # Each chart below corresponds to one or more aggregations produced
    # using groupby() and pivot() operations.

    # (1) Cases per city (geographic distribution)
    cases_city = (
        df_success
        .groupby("city", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    # Normalize missing cities to "Unknown" for consistent visualization.
    cases_city["city"] = cases_city["city"].fillna("Unknown")

    # (2) Cases per occurrence type (crime distribution)
    cases_occ = (
        df_success
        .groupby("occurrence", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    cases_occ["occurrence"] = cases_occ["occurrence"].fillna("Unknown")

    # (3) Cases per year-month (temporal trend)
    df_success["year"] = df_success["year"].fillna(0).astype(int)
    df_success["month"] = df_success["month"].fillna(0).astype(int)

    cases_year_month = (
        df_success
        .groupby(["year", "month"])
        .size()
        .reset_index(name="count")
        .sort_values(["year", "month"])
    )

    # Create a YYYY-MM label for plotting. Unknown entries are preserved as "Unknown".
    def ym_label(row):
        year = row["year"]
        month = row["month"]
        if year == 0 or month == 0:
            return "Unknown"
        return f"{int(year):04d}-{int(month):02d}"

    cases_year_month["label"] = cases_year_month.apply(ym_label, axis=1)

    # (4) Cases per city × year (used for heatmap visualization)
    cases_city_year = (
        df_success
        .groupby(["city", "year"])
        .size()
        .reset_index(name="count")
    )
    cases_city_year["city"] = cases_city_year["city"].fillna("Unknown")

    # Pivot to make cities become rows and years become columns.
    pivot_city_year = (
        cases_city_year
        .pivot(index="city", columns="year", values="count")
        .fillna(0)
        .sort_index()
    )

    # (5) Cases per occurrence × year (2022 vs 2023 vs 2024 comparison)
    cases_occ_year = (
        df_success[df_success["year"].isin([2022, 2023, 2024])]
        .groupby(["occurrence", "year"])
        .size()
        .reset_index(name="count")
    )
    cases_occ_year["occurrence"] = cases_occ_year["occurrence"].fillna("Unknown")

    pivot_occ_year = (
        cases_occ_year
        .pivot(index="occurrence", columns="year", values="count")
        .fillna(0)
        .sort_index()
    )

    # ----------------------------------------------------------------------
    # DASHBOARD LAYOUT (3 rows × 2 columns)
    # ----------------------------------------------------------------------
    # Row 1: city distribution and occurrence distribution
    # Row 2: time trend        and city-year heatmap
    # Row 3: year-over-year crime comparison (dedicated line to this chart)
    # ----------------------------------------------------------------------
    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            "Cases per City (All Years)",
            "Cases per Occurrence Type (All Years)",
            "Cases per Year-Month",
            "Cases per City and Year (Heatmap)",
            "Cases per Occurrence by Year",
        ),
        specs=[
            [{"type": "xy"},       {"type": "xy"}],
            [{"type": "xy"},       {"type": "heatmap"}],
            [{"type": "xy", "colspan": 2}, None],
        ],
    )

    # (1) Cases per City — Bar Chart
    fig.add_trace(
        go.Bar(
            x=cases_city["city"],
            y=cases_city["count"],
            name="Cases per City",
        ),
        row=1, col=1,
    )

    # (2) Cases per Occurrence Type — Bar Chart
    fig.add_trace(
        go.Bar(
            x=cases_occ["occurrence"],
            y=cases_occ["count"],
            name="Cases per Occurrence",
        ),
        row=1, col=2,
    )

    # (3) Cases per Year-Month — Line Chart (trend view)
    fig.add_trace(
        go.Scatter(
            x=cases_year_month["label"],
            y=cases_year_month["count"],
            mode="lines+markers",
            name="Cases per Year-Month",
            marker=dict(size=8),
            line=dict(width=2),
        ),
        row=2, col=1,
    )

    # (4) City × Year — Heatmap (trend + geography interaction)
    if not pivot_city_year.empty:
        fig.add_trace(
            go.Heatmap(
                z=pivot_city_year.values,
                x=[str(y) for y in pivot_city_year.columns],
                y=pivot_city_year.index.tolist(),
                coloraxis="coloraxis",
                name="City-Year Heatmap",
            ),
            row=2, col=2,
        )

    # (5) Occurrence × Year — Grouped Bar Chart (YoY comparison)
    if not pivot_occ_year.empty:
        occ_index = pivot_occ_year.index.tolist()

        # Helper function to return values per year or zeros if that year didn't appear.
        def get_year_values(year: int) -> List[float]:
            return pivot_occ_year[year].tolist() if year in pivot_occ_year.columns else [0] * len(occ_index)

        # Manual palette for clarity (can be adjusted later)
        year_configs = [
            (2022, "2022", "blue"),
            (2023, "2023", "red"),
            (2024, "2024", "green"),
        ]

        for year, label, color in year_configs:
            fig.add_trace(
                go.Bar(
                    x=occ_index,
                    y=get_year_values(year),
                    name=label,           
                    marker_color=color,  
                ),
                row=3, col=1,
            )

    # Layout, axes, legend & sizing
    fig.update_layout(
        title="Police Cases Overview",
        height=1200,
        coloraxis=dict(colorscale="Blues"),
        margin=dict(l=40, r=40, t=80, b=40),
        barmode="group",  # Ensures bars in row 3 appear grouped side-by-side
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
        )
    )

    # Label axes for all charts for readability
    fig.update_xaxes(title_text="City", row=1, col=1)
    fig.update_yaxes(title_text="Number of Cases", row=1, col=1)

    fig.update_xaxes(title_text="Occurrence Type", row=1, col=2)
    fig.update_yaxes(title_text="Number of Cases", row=1, col=2)

    fig.update_xaxes(title_text="Year-Month", row=2, col=1)
    fig.update_yaxes(title_text="Number of Cases", row=2, col=1)

    fig.update_xaxes(title_text="Year", row=2, col=2)
    fig.update_yaxes(title_text="City", row=2, col=2)

    fig.update_xaxes(title_text="Occurrence Type", row=3, col=1)
    fig.update_yaxes(title_text="Number of Cases", row=3, col=1)

    # Render the full interactive dashboard.
    fig.show()

def main() -> None:
    # Adjust this to your structure if needed:
    # phase02 sits in src/, output.json in project root or src/
    base_dir = Path(__file__).resolve().parents[1]
    json_path = base_dir / "src" / "output.json"
    # If your file lives in src/output.json, then:
    # json_path = base_dir / "src" / "output.json"

    results = load_results(json_path)

    # -------- Text summaries in terminal --------
    summarize_basic(results)
    summarize_errors(results, max_examples=5)
    summarize_by_city(results)
    summarize_by_occurrence(results)
    summarize_by_city_and_year(results)

    # -------- Visual dashboard with Plotly --------
    build_dashboard(results)


if __name__ == "__main__":
    main()
