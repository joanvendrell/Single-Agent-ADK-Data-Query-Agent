from __future__ import annotations
from typing import Any, Optional, Union
import pandas as pd
import json
from .config import DATA_PATH, VALID_FILTER_TYPES

Record = dict[str, Any]
FilterValue = Union[str, float, bool, dict[str, float]]


def _load_full_dataset() -> pd.DataFrame:
    """Load the full Excel dataset and normalize output-friendly types."""
    df = pd.read_excel(DATA_PATH)
    required = ["asset_id", "location", "timestamp", "sensor_type", "value", "anomaly_label"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    return df[required]


def _records_to_dataframe(records: list[Record]) -> pd.DataFrame:
    return pd.DataFrame(records)


def _clean_records(df: pd.DataFrame) -> list[Record]:
    """Convert pandas values to JSON/tool-call friendly Python values."""
    if df.empty:
        return []

    out = df.copy()
    if "timestamp" in out.columns:
        out["timestamp"] = out["timestamp"].astype(str)
    if "value" in out.columns:
        out["value"] = out["value"].astype(float)
    if "anomaly_label" in out.columns:
        out["anomaly_label"] = out["anomaly_label"].astype(bool)
    return out.to_dict(orient="records")


def filter_records(
    filter_type: str,
    filter_value: FilterValue,
    previous_results: Optional[list[Record]] = None,
) -> list[Record]:
    """Apply exactly one filter to the sensor dataset.

    Args:
        filter_type: One of "location", "sensor_type", "value_range", or "anomaly_label".
        filter_value: For location/sensor_type, a string. For value_range, a dict with
            optional min/max keys. For anomaly_label, a boolean. This implementation
            accepts True and False so queries like "not anomalies" can be answered.
        previous_results: Optional records from a previous filtering call. When None,
            the tool loads data/sensor_data.xlsx and filters the full dataset.

    Returns:
        A list of dictionaries matching the single criterion. No row limit is applied.
    """
    if filter_type not in VALID_FILTER_TYPES:
        raise ValueError(f"Invalid filter_type: {filter_type}")

    df = _load_full_dataset() if previous_results is None else _records_to_dataframe(previous_results)

    if df.empty:
        return []

    if filter_type == "location":
        if not isinstance(filter_value, str):
            raise TypeError("location filter_value must be a string")
        mask = df["location"].astype(str).str.casefold() == filter_value.casefold()

    elif filter_type == "sensor_type":
        if not isinstance(filter_value, str):
            raise TypeError("sensor_type filter_value must be a string")
        mask = df["sensor_type"].astype(str).str.casefold() == filter_value.casefold()

    elif filter_type == "anomaly_label":
        if not isinstance(filter_value, bool):
            raise TypeError("anomaly_label filter_value must be a boolean")
        mask = df["anomaly_label"].astype(bool) == filter_value

    else:  # value_range
        if not isinstance(filter_value, dict):
            raise TypeError("value_range filter_value must be a dict with optional min/max keys")
        min_value = filter_value.get("min")
        max_value = filter_value.get("max")
        if min_value is None and max_value is None:
            raise ValueError("value_range requires at least one of min or max")

        values = pd.to_numeric(df["value"], errors="coerce")
        mask = pd.Series(True, index=df.index)
        if min_value is not None:
            mask &= values >= float(min_value)
        if max_value is not None:
            mask &= values <= float(max_value)

    return _clean_records(df.loc[mask])

def filter_records_adk(
    filter_type: str,
    filter_value: str = "",
    min_value: float = -1e308,
    max_value: float = 1e308,
    anomaly_label: bool = False,
    previous_results_json: str = "",
) -> str:
    """
    ADK-compatible wrapper around filter_records.

    This wrapper avoids complex Python type hints such as Union[str, float, dict]
    and Optional[List[dict]], because ADK/LiteLLM tools are more reliable with
    simple JSON-compatible arguments.
    """
    import json

    previous_results = None

    if previous_results_json:
        if isinstance(previous_results_json, str):
            previous_results = json.loads(previous_results_json)
        else:
            previous_results = previous_results_json

        # Sometimes the model/tool layer may pass {"records": [...]} or {"result": [...]}
        if isinstance(previous_results, dict):
            if "records" in previous_results:
                previous_results = previous_results["records"]
            elif "result" in previous_results:
                previous_results = previous_results["result"]
            else:
                # If it is a single record dictionary, wrap it as a list.
                previous_results = [previous_results]

        # If a JSON string was nested inside the result, parse it again.
        if isinstance(previous_results, str):
            previous_results = json.loads(previous_results)

        if isinstance(previous_results, dict):
            previous_results = [previous_results]

    if filter_type == "location":
        result = filter_records(
            filter_type="location",
            filter_value=filter_value,
            previous_results=previous_results,
        )

    elif filter_type == "sensor_type":
        result = filter_records(
            filter_type="sensor_type",
            filter_value=filter_value,
            previous_results=previous_results,
        )

    elif filter_type == "anomaly_label":
        result = filter_records(
            filter_type="anomaly_label",
            filter_value=anomaly_label,
            previous_results=previous_results,
        )

    elif filter_type == "value_range":
        value_range = {}

        if min_value != -1e308:
            value_range["min"] = min_value

        if max_value != 1e308:
            value_range["max"] = max_value

        result = filter_records(
            filter_type="value_range",
            filter_value=value_range,
            previous_results=previous_results,
        )

    else:
        raise ValueError(
            "filter_type must be one of: location, sensor_type, value_range, anomaly_label"
        )

    return json.dumps(result, default=str)