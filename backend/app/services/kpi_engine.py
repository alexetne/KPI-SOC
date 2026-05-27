from collections import Counter
from datetime import datetime
from typing import Any

from app.schemas.kpi import KpiDefinition, KpiResult

KPI_DEFINITIONS = [
    KpiDefinition(
        key="alert_count",
        label="Nombre d'alertes",
        description="Compte les lignes d'alertes sur le perimetre courant.",
        chart_type="stat",
        required_columns=[],
    ),
    KpiDefinition(
        key="conversion_rate",
        label="Taux de conversion",
        description="Part des alertes converties en incident confirme.",
        chart_type="stat",
        required_columns=["status"],
    ),
    KpiDefinition(
        key="top_endpoint",
        label="Endpoint le plus bruyant",
        description="Identifie l'endpoint qui genere le plus d'alertes.",
        chart_type="bar",
        required_columns=["endpoint"],
    ),
    KpiDefinition(
        key="severity_distribution",
        label="Repartition par severite",
        description="Compte les alertes par niveau de severite.",
        chart_type="pie",
        required_columns=["severity"],
    ),
    KpiDefinition(
        key="alerts_over_time",
        label="Alertes dans le temps",
        description="Compte les alertes par jour sur une colonne date.",
        chart_type="line",
        required_columns=["created_date"],
    ),
    KpiDefinition(
        key="status_distribution",
        label="Repartition par statut",
        description="Compte les alertes par statut operationnel.",
        chart_type="bar",
        required_columns=["status"],
    ),
    KpiDefinition(
        key="mean_time_to_close",
        label="Temps moyen de cloture",
        description="Calcule le delai moyen entre creation et cloture en heures.",
        chart_type="stat",
        required_columns=["created_date", "closed_date"],
    ),
]


def list_kpi_definitions() -> list[KpiDefinition]:
    return KPI_DEFINITIONS


def compute_kpi(metric_key: str, rows: list[dict[str, Any]], mapping: dict[str, str]) -> KpiResult:
    definition = next((item for item in KPI_DEFINITIONS if item.key == metric_key), None)
    if definition is None:
        raise ValueError(f"Unknown metric: {metric_key}")

    if metric_key == "alert_count":
        return KpiResult(
            metric_key=metric_key,
            label=definition.label,
            chart_type=definition.chart_type,
            value=len(rows),
        )

    if metric_key == "conversion_rate":
        status_column = mapping.get("status")
        converted = [
            row for row in rows if str(row.get(status_column, "")).lower() in {"incident", "confirmed", "confirme"}
        ]
        value = round((len(converted) / len(rows)) * 100, 2) if rows else 0
        return KpiResult(
            metric_key=metric_key,
            label=definition.label,
            chart_type=definition.chart_type,
            value=value,
            series=[{"label": "Converties", "value": len(converted)}, {"label": "Total", "value": len(rows)}],
        )

    if metric_key == "top_endpoint":
        endpoint_column = mapping.get("endpoint")
        counter = Counter(row.get(endpoint_column, "N/A") for row in rows)
        series = [{"label": label, "value": value} for label, value in counter.most_common(10)]
        return KpiResult(
            metric_key=metric_key,
            label=definition.label,
            chart_type=definition.chart_type,
            value=series[0]["label"] if series else None,
            series=series,
        )

    if metric_key == "severity_distribution":
        severity_column = mapping.get("severity")
        counter = Counter(row.get(severity_column, "N/A") for row in rows)
        series = [{"label": label, "value": value} for label, value in counter.items()]
        return KpiResult(
            metric_key=metric_key,
            label=definition.label,
            chart_type=definition.chart_type,
            value=len(series),
            series=series,
        )

    if metric_key == "alerts_over_time":
        date_column = mapping.get("created_date")
        counter: Counter[str] = Counter()
        for row in rows:
            raw_value = row.get(date_column)
            if not raw_value:
                continue
            try:
                day = datetime.fromisoformat(str(raw_value).replace("Z", "+00:00")).date().isoformat()
            except ValueError:
                day = str(raw_value)[:10]
            counter[day] += 1
        series = [{"label": label, "value": counter[label]} for label in sorted(counter)]
        return KpiResult(
            metric_key=metric_key,
            label=definition.label,
            chart_type=definition.chart_type,
            value=sum(counter.values()),
            series=series,
        )

    if metric_key == "status_distribution":
        status_column = mapping.get("status")
        counter = Counter(row.get(status_column, "N/A") for row in rows)
        series = [{"label": label, "value": value} for label, value in counter.most_common()]
        return KpiResult(
            metric_key=metric_key,
            label=definition.label,
            chart_type=definition.chart_type,
            value=len(series),
            series=series,
        )

    if metric_key == "mean_time_to_close":
        created_column = mapping.get("created_date")
        closed_column = mapping.get("closed_date")
        durations = []
        for row in rows:
            created = _parse_datetime(row.get(created_column))
            closed = _parse_datetime(row.get(closed_column))
            if created and closed and closed >= created:
                durations.append((closed - created).total_seconds() / 3600)
        value = round(sum(durations) / len(durations), 2) if durations else 0
        return KpiResult(
            metric_key=metric_key,
            label=definition.label,
            chart_type=definition.chart_type,
            value=value,
            series=[{"label": "Heures", "value": value}],
        )

    raise ValueError(f"Metric not implemented: {metric_key}")


def apply_filters(rows: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
    if not filters:
        return rows

    filtered = rows
    q = str(filters.get("q", "")).strip().lower()
    if q:
        filtered = [row for row in filtered if q in " ".join(str(value).lower() for value in row.values())]

    for key, expected in filters.items():
        if key in {"q", "limit", "offset"} or expected in {None, ""}:
            continue
        filtered = [row for row in filtered if str(row.get(key, "")).lower() == str(expected).lower()]

    return filtered


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
