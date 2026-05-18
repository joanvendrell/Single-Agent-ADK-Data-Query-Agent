from sensor_filter_agent.query_parser import parse_query


def test_valid_query_multiple_steps():
    parsed = parse_query("Show gas anomalies in Zone 2 with value above 60")
    assert parsed.is_filtering_query
    assert [(s.filter_type, s.filter_value) for s in parsed.steps] == [
        ("location", "Zone 2"),
        ("sensor_type", "gas"),
        ("anomaly_label", True),
        ("value_range", {"min": 60.0}),
    ]


def test_valid_query_between():
    parsed = parse_query("Show temperature sensors with values between 20 and 30")
    assert parsed.is_filtering_query
    assert parsed.steps[-1].filter_type == "value_range"
    assert parsed.steps[-1].filter_value == {"min": 20.0, "max": 30.0}


def test_not_anomalies():
    parsed = parse_query("Show gas readings above 50 that are not anomalies")
    assert parsed.is_filtering_query
    assert any(step.filter_type == "anomaly_label" and step.filter_value is False for step in parsed.steps)


def test_invalid_count_query():
    parsed = parse_query("How many anomalies are in Area B?")
    assert not parsed.is_filtering_query


def test_invalid_average_query():
    parsed = parse_query("What is the average temperature?")
    assert not parsed.is_filtering_query
