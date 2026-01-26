import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Optional: month number -> name (if you want nicer output)
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


def load_results(json_path: Path) -> List[Dict[str, Any]]:
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# -------------------------------------------------------------------
# TEXTUAL SUMMARIES (same as before)
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
    failures = [r for r in results if not r.get("Success")]
    if not failures:
        print("=== ERRORS ===")
        print("No failures. 🎉")
        print()
        return

    print("=== ERRORS (examples) ===")
    for idx, item in enumerate(failures[:max_examples], start=1):
        source = item.get("source", "<unknown>")
        error = item.get("ERROR", "<no error message>")
        print(f"{idx:2}. File: {source}")
        print(f"    Error: {error}")
    if len(failures) > max_examples:
        print(f"... and {len(failures) - max_examples} more failures.")
    print()


def summarize_by_year_month(results: List[Dict[str, Any]]) -> None:
    counter: Counter[Tuple[Optional[int], Optional[int]]] = Counter()

    for r in results:
        if not r.get("Success"):
            continue  # skip failed ones from the metrics
        year = r.get("year")
        month = r.get("month")
        counter[(year, month)] += 1

    print("=== CASES BY YEAR / MONTH ===")
    for (year, month), count in sorted(
        counter.items(),
        key=lambda x: (x[0][0] or 0, x[0][1] or 0),
    ):
        year_str = str(year) if year is not None else "Unknown year"
        if isinstance(month, int):
            month_str = MONTH_NAMES.get(month, f"Month {month}")
        else:
            month_str = "Unknown month"
        print(f"{year_str:<12} {month_str:<12} -> {count}")
    print()


def summarize_by_city(results: List[Dict[str, Any]]) -> None:
    counter: Counter[str] = Counter()

    for r in results:
        if not r.get("Success"):
            continue
        city = r.get("city") or "Unknown"
        counter[city] += 1

    print("=== CASES BY CITY ===")
    for city, count in counter.most_common():
        print(f"{city:<25} -> {count}")
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
    # Optional extra: breakdown by city + year
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
# PLOTTING DASHBOARD WITH PLOTLY
# -------------------------------------------------------------------
def build_dashboard(results: List[Dict[str, Any]]) -> None:
    # Convert to DataFrame for easier aggregations
    df = pd.DataFrame(results)

    if df.empty:
        print("No data available to plot.")
        return

    # Use only successful records
    df_success = df[df["Success"] == True].copy()  # noqa: E712

    if df_success.empty:
        print("No successful records to plot.")
        return

    # ------------------------------
    # Aggregations for charts
    # ------------------------------

    # 1) Cases per city
    cases_city = (
        df_success
        .groupby("city", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    cases_city["city"] = cases_city["city"].fillna("Unknown")

    # 2) Cases per occurrence type
    cases_occ = (
        df_success
        .groupby("occurrence", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    cases_occ["occurrence"] = cases_occ["occurrence"].fillna("Unknown")

    # 3) Cases per year-month
    # Guard: year / month might be None
    df_success["year"] = df_success["year"].fillna(0).astype(int)
    df_success["month"] = df_success["month"].fillna(0).astype(int)

    cases_year_month = (
        df_success
        .groupby(["year", "month"])
        .size()
        .reset_index(name="count")
        .sort_values(["year", "month"])
    )

    # Create a label like "2023-03" or "Unknown" if missing
    def ym_label(row):
        year = row["year"]
        month = row["month"]
        if year == 0 or month == 0:
            return "Unknown"
        return f"{int(year):04d}-{int(month):02d}"

    cases_year_month["label"] = cases_year_month.apply(ym_label, axis=1)

    # 4) Cases per city x year (for heatmap)
    cases_city_year = (
        df_success
        .groupby(["city", "year"])
        .size()
        .reset_index(name="count")
    )
    cases_city_year["city"] = cases_city_year["city"].fillna("Unknown")

    pivot_city_year = (
        cases_city_year
        .pivot(index="city", columns="year", values="count")
        .fillna(0)
        .sort_index()
    )

    # ------------------------------
    # Create 2x2 subplot dashboard
    # ------------------------------
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Cases per City",
            "Cases per Occurrence Type",
            "Cases per Year-Month",
            "Cases per City and Year (Heatmap)",
        ),
        specs=[
            [{"type": "xy"},       {"type": "xy"}],
            [{"type": "xy"},       {"type": "heatmap"}],
        ],
    )

    # (1) Bar chart: Cases per City (row 1, col 1)
    fig.add_trace(
        go.Bar(
            x=cases_city["city"],
            y=cases_city["count"],
            name="Cases per City",
        ),
        row=1,
        col=1,
    )

    # (2) Bar chart: Cases per Occurrence Type (row 1, col 2)
    fig.add_trace(
        go.Bar(
            x=cases_occ["occurrence"],
            y=cases_occ["count"],
            name="Cases per Occurrence",
        ),
        row=1,
        col=2,
    )

    # (3) Bar chart: Cases per Year-Month (row 2, col 1)
    fig.add_trace(
        go.Bar(
            x=cases_year_month["label"],
            y=cases_year_month["count"],
            name="Cases per Year-Month",
        ),
        row=2,
        col=1,
    )

    # (4) Heatmap: Cases per City and Year (row 2, col 2)
    if not pivot_city_year.empty:
        fig.add_trace(
            go.Heatmap(
                z=pivot_city_year.values,
                x=[str(c) for c in pivot_city_year.columns],
                y=pivot_city_year.index.tolist(),
                coloraxis="coloraxis",
                name="City-Year Heatmap",
            ),
            row=2,
            col=2,
        )

    # ------------------------------
    # Layout / axes
    # ------------------------------
    fig.update_layout(
        title="Police Cases Overview",
        height=900,
        showlegend=False,
        coloraxis=dict(colorscale="Blues"),
        margin=dict(l=40, r=40, t=80, b=40),
    )

    fig.update_xaxes(title_text="City", row=1, col=1)
    fig.update_yaxes(title_text="Number of Cases", row=1, col=1)

    fig.update_xaxes(title_text="Occurrence Type", row=1, col=2)
    fig.update_yaxes(title_text="Number of Cases", row=1, col=2)

    fig.update_xaxes(title_text="Year-Month", row=2, col=1)
    fig.update_yaxes(title_text="Number of Cases", row=2, col=1)

    fig.update_xaxes(title_text="Year", row=2, col=2)
    fig.update_yaxes(title_text="City", row=2, col=2)

    # Render interactive dashboard
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
    summarize_by_year_month(results)
    summarize_by_city(results)
    summarize_by_occurrence(results)
    summarize_by_city_and_year(results)

    # -------- Visual dashboard with Plotly --------
    build_dashboard(results)


if __name__ == "__main__":
    main()
