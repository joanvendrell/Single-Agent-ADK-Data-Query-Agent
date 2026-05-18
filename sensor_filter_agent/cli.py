from __future__ import annotations

from .pipeline import format_records, run_filter_pipeline

DECLINE_MESSAGE = (
    "I can only answer filtering questions about sensor records using location, "
    "sensor_type, value_range, and anomaly_label. I cannot perform counts, "
    "averages, aggregations, charts, or general conversation."
)


def main() -> None:
    print("Sensor Filter Agent CLI")
    print("Type a filtering query, or type 'exit'.")

    while True:
        query = input("\nQuery> ").strip()
        if query.casefold() in {"exit", "quit"}:
            break

        parsed, records = run_filter_pipeline(query)
        if not parsed.is_filtering_query:
            print(f"Declined: {parsed.reason}")
            print(DECLINE_MESSAGE)
            continue

        print("Tool calls:")
        for step in parsed.steps:
            print(f"- filter_records(filter_type={step.filter_type!r}, filter_value={step.filter_value!r})")
        print(format_records(records))


if __name__ == "__main__":
    main()
