from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dynamic_table import DynamicColumn, DynamicRow, DynamicTable

DEMO_COLUMNS = [
    {
        "key": "alert_name",
        "label": "Alerte",
        "data_type": "text",
        "required": True,
        "position": 0,
    },
    {
        "key": "endpoint",
        "label": "Endpoint",
        "data_type": "endpoint",
        "required": False,
        "position": 1,
    },
    {
        "key": "severity",
        "label": "Severite",
        "data_type": "severity",
        "required": False,
        "options": {"choices": ["low", "medium", "high", "critical"]},
        "position": 2,
    },
    {
        "key": "status",
        "label": "Statut",
        "data_type": "status",
        "required": False,
        "options": {"choices": ["new", "triage", "alert", "incident", "closed", "false_positive"]},
        "position": 3,
    },
    {
        "key": "source",
        "label": "Source",
        "data_type": "enum",
        "required": False,
        "options": {"choices": ["EDR", "SIEM", "NDR", "IAM", "Cloud"]},
        "position": 4,
    },
    {
        "key": "analyst",
        "label": "Analyste",
        "data_type": "text",
        "required": False,
        "position": 5,
    },
    {
        "key": "created_date",
        "label": "Creation",
        "data_type": "datetime",
        "required": False,
        "position": 6,
    },
    {
        "key": "closed_date",
        "label": "Cloture",
        "data_type": "datetime",
        "required": False,
        "position": 7,
    },
]

ALERT_NAMES = [
    "Suspicious PowerShell",
    "Impossible travel",
    "Malware blocked",
    "Privilege escalation",
    "Beaconing pattern",
    "Credential stuffing",
    "Data exfiltration suspicion",
]
ENDPOINTS = ["srv-auth-01", "lap-fin-22", "srv-web-03", "mac-exec-07", "srv-db-02"]
SEVERITIES = ["low", "medium", "high", "critical"]
STATUSES = ["new", "triage", "alert", "incident", "closed", "false_positive"]
SOURCES = ["EDR", "SIEM", "NDR", "IAM", "Cloud"]
ANALYSTS = ["Nadia", "Eliott", "Samir", "Julia"]


def seed_security_alerts(db: Session) -> DynamicTable:
    table = db.scalar(select(DynamicTable).where(DynamicTable.name == "security_alerts"))
    if table is None:
        table = DynamicTable(
            name="security_alerts",
            label="Alertes securite",
            description="Table principale des alertes et incidents SOC",
        )
        db.add(table)
        db.flush()

    existing_columns = {
        column.key
        for column in db.scalars(select(DynamicColumn).where(DynamicColumn.table_id == table.id)).all()
    }
    for column in DEMO_COLUMNS:
        if column["key"] not in existing_columns:
            db.add(DynamicColumn(table_id=table.id, **column))

    existing_rows = db.scalars(select(DynamicRow).where(DynamicRow.table_id == table.id)).all()
    if not existing_rows:
        now = datetime.now(UTC)
        for index in range(42):
            created = now - timedelta(days=index % 21, hours=index * 2)
            status = STATUSES[index % len(STATUSES)]
            closed = created + timedelta(hours=4 + (index % 18)) if status in {"closed", "incident"} else None
            db.add(
                DynamicRow(
                    table_id=table.id,
                    values={
                        "alert_name": ALERT_NAMES[index % len(ALERT_NAMES)],
                        "endpoint": ENDPOINTS[index % len(ENDPOINTS)],
                        "severity": SEVERITIES[index % len(SEVERITIES)],
                        "status": status,
                        "source": SOURCES[index % len(SOURCES)],
                        "analyst": ANALYSTS[index % len(ANALYSTS)],
                        "created_date": created.isoformat(),
                        "closed_date": closed.isoformat() if closed else None,
                    },
                )
            )

    db.commit()
    db.refresh(table)
    return table
