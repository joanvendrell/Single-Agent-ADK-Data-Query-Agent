from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .config import VALID_SENSOR_TYPES


@dataclass(frozen=True)
class FilterStep:
    filter_type: str
    filter_value: Any


@dataclass(frozen=True)
class ParsedQuery:
    is_filtering_query: bool
    reason: str
    steps: list[FilterStep]


INVALID_PATTERNS = [
    r"\bhow many\b",
    r"\bcount\b",
    r"\baverage\b",
    r"\bmean\b",
    r"\bmedian\b",
    r"\bminimum\b",
    r"\bmaximum\b",
    r"\bmin\b(?!\s*\d)",
    r"\bmax\b(?!\s*\d)",
    r"\bsum\b",
    r"\btotal\b",
    r"\bplot\b",
    r"\bchart\b",
]


def parse_query(query: str) -> ParsedQuery:
    """Small deterministic parser used by the CLI/tests.

    The ADK agent is still responsible for interpreting natural language during
    normal ADK execution. This parser gives you a reproducible local runner and
    clear failure cases for the report.
    """
    q = query.strip()
    q_lower = q.casefold()

    if any(re.search(pattern, q_lower) for pattern in INVALID_PATTERNS):
        return ParsedQuery(False, "The query asks for calculation, aggregation, or visualization.", [])

    steps: list[FilterStep] = []

    # Locations from the provided dataset.
    for location in ["Area A", "Area B", "Zone 1", "Zone 2"]:
        if location.casefold() in q_lower:
            steps.append(FilterStep("location", location))
            break

    for sensor_type in sorted(VALID_SENSOR_TYPES):
        if re.search(rf"\b{re.escape(sensor_type)}\b", q_lower):
            steps.append(FilterStep("sensor_type", sensor_type))
            break

    # Important: detect "not anomalies" before "anomalies".
    if re.search(r"\bnot\s+anomal(?:y|ies)\b|\bnon[-\s]?anomal", q_lower):
        steps.append(FilterStep("anomaly_label", False))
    elif re.search(r"\banomal(?:y|ies|ous)\b", q_lower):
        steps.append(FilterStep("anomaly_label", True))

    between = re.search(r"\bbetween\s+(-?\d+(?:\.\d+)?)\s+(?:and|to)\s+(-?\d+(?:\.\d+)?)", q_lower)
    above = re.search(r"\b(?:above|over|greater than|at least)\s+(-?\d+(?:\.\d+)?)", q_lower)
    below = re.search(r"\b(?:below|under|less than|at most)\s+(-?\d+(?:\.\d+)?)", q_lower)

    if between:
        low, high = sorted([float(between.group(1)), float(between.group(2))])
        steps.append(FilterStep("value_range", {"min": low, "max": high}))
    elif above:
        steps.append(FilterStep("value_range", {"min": float(above.group(1))}))
    elif below:
        steps.append(FilterStep("value_range", {"max": float(below.group(1))}))

    if not steps:
        return ParsedQuery(False, "No supported filtering criterion was detected.", [])

    return ParsedQuery(True, "Filtering query detected.", steps)
