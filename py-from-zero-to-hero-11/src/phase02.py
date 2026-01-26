import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional


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
    for (year, month), count in sorted(counter.items(), key=lambda x: (x[0][0] or 0, x[0][1] or 0)):
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


def main() -> None:
    # phase02 sits in the same folder level as phase01,
    # so output.json is assumed to be one level up in the project.
    base_dir = Path(__file__).resolve().parents[1]
    json_path = base_dir / "src" / "output.json"

    results = load_results(json_path)

    # High-level summaries
    summarize_basic(results)
    summarize_errors(results, max_examples=5)

    # Analytical summaries
    summarize_by_year_month(results)
    summarize_by_city(results)
    summarize_by_occurrence(results)
    summarize_by_city_and_year(results)


if __name__ == "__main__":
    main()
