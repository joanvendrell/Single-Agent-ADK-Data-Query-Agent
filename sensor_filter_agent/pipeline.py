from __future__ import annotations

from .query_parser import ParsedQuery, parse_query
from .tools import filter_records


def run_filter_pipeline(query: str) -> tuple[ParsedQuery, list[dict]]:
    """Parse a query and apply one filter per tool call."""
    parsed = parse_query(query)
    if not parsed.is_filtering_query:
        return parsed, []

    results = None
    for step in parsed.steps:
        results = filter_records(
            filter_type=step.filter_type,
            filter_value=step.filter_value,
            previous_results=results,
        )
    return parsed, results or []


def format_records(records: list[dict], limit: int = 20) -> str:
    """Format final records for terminal output."""
    if not records:
        return "No matching records found."

    visible = records[:limit]
    lines = [f"Found {len(records)} matching record(s). Showing first {len(visible)}:"]
    for idx, row in enumerate(visible, start=1):
        lines.append(
            f"{idx}. asset_id={row.get('asset_id')}, location={row.get('location')}, "
            f"timestamp={row.get('timestamp')}, sensor_type={row.get('sensor_type')}, "
            f"value={row.get('value')}, anomaly_label={row.get('anomaly_label')}"
        )
    return "\n".join(lines)
