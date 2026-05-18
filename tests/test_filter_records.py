from sensor_filter_agent.tools import filter_records


def test_filter_location_area_a():
    records = filter_records("location", "Area A")
    assert records
    assert all(row["location"] == "Area A" for row in records)


def test_filter_chained_gas_area_a():
    records = filter_records("location", "Area A")
    records = filter_records("sensor_type", "gas", previous_results=records)
    assert records
    assert all(row["location"] == "Area A" and row["sensor_type"] == "gas" for row in records)


def test_filter_value_range_min():
    records = filter_records("value_range", {"min": 60})
    assert records
    assert all(row["value"] >= 60 for row in records)


def test_filter_no_results_returns_empty_list():
    records = filter_records("location", "Unknown Area")
    assert records == []


def test_filter_not_anomalies_supported_for_assignment_example():
    records = filter_records("anomaly_label", False)
    assert records
    assert all(row["anomaly_label"] is False for row in records)
