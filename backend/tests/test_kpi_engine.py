from app.services.kpi_engine import apply_filters, compute_kpi


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


def test_status_distribution() -> None:
    result = compute_kpi(
        "status_distribution",
        [{"status": "new"}, {"status": "incident"}, {"status": "incident"}],
        {"status": "status"},
    )

    assert result.series[0] == {"label": "incident", "value": 2}


def test_mean_time_to_close() -> None:
    result = compute_kpi(
        "mean_time_to_close",
        [
            {"created": "2026-05-27T08:00:00+00:00", "closed": "2026-05-27T12:00:00+00:00"},
            {"created": "2026-05-27T08:00:00+00:00", "closed": "2026-05-27T10:00:00+00:00"},
        ],
        {"created_date": "created", "closed_date": "closed"},
    )

    assert result.value == 3


def test_apply_filters_global_and_exact() -> None:
    rows = [
        {"endpoint": "srv-1", "severity": "high"},
        {"endpoint": "srv-2", "severity": "low"},
    ]

    assert apply_filters(rows, {"q": "srv", "severity": "high"}) == [{"endpoint": "srv-1", "severity": "high"}]
