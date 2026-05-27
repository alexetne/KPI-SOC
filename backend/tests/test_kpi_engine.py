from app.services.kpi_engine import compute_kpi


def test_alert_count() -> None:
    result = compute_kpi("alert_count", [{"a": 1}, {"a": 2}], {})

    assert result.value == 2


def test_conversion_rate() -> None:
    result = compute_kpi(
        "conversion_rate",
        [{"status": "alert"}, {"status": "incident"}, {"status": "confirme"}],
        {"status": "status"},
    )

    assert result.value == 66.67


def test_top_endpoint() -> None:
    result = compute_kpi(
        "top_endpoint",
        [{"host": "srv-1"}, {"host": "srv-2"}, {"host": "srv-1"}],
        {"endpoint": "host"},
    )

    assert result.value == "srv-1"
