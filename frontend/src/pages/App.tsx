import { Activity, BarChart3, Database, Plus, ShieldAlert } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { DataGrid } from "../components/DataGrid";
import { KpiPanel } from "../components/KpiPanel";
import { createColumn, createRow, createTable, listKpiDefinitions, listRows, listTables, queryKpi } from "../services/api";
import type { DynamicRow, DynamicTable, KpiResult } from "../types/api";

const demoColumns = [
  { key: "alert_name", label: "Alerte", data_type: "text" as const, required: true, position: 0 },
  { key: "endpoint", label: "Endpoint", data_type: "endpoint" as const, required: false, position: 1 },
  { key: "severity", label: "Severite", data_type: "severity" as const, required: false, position: 2 },
  { key: "status", label: "Statut", data_type: "status" as const, required: false, position: 3 },
  { key: "created_date", label: "Date", data_type: "datetime" as const, required: false, position: 4 },
];

export function App() {
  const [tables, setTables] = useState<DynamicTable[]>([]);
  const [activeTable, setActiveTable] = useState<DynamicTable | null>(null);
  const [rows, setRows] = useState<DynamicRow[]>([]);
  const [kpis, setKpis] = useState<KpiResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void bootstrap();
  }, []);

  useEffect(() => {
    if (!activeTable) return;
    void refreshRows(activeTable.id);
  }, [activeTable]);

  useEffect(() => {
    if (!activeTable || rows.length === 0) return;
    void refreshKpis(activeTable);
  }, [activeTable, rows]);

  async function bootstrap() {
    setLoading(true);
    const [tableData] = await Promise.all([listTables(), listKpiDefinitions()]);
    setTables(tableData);
    setActiveTable(tableData[0] ?? null);
    setLoading(false);
  }

  async function createDemoTable() {
    const table = await createTable({
      name: "security_alerts",
      label: "Alertes securite",
      description: "Table principale des alertes SOC",
    });
    const createdColumns = await Promise.all(
      demoColumns.map((column) =>
        createColumn(table.id, {
          ...column,
          options: column.key === "severity" ? { choices: ["low", "medium", "high", "critical"] } : undefined,
        }),
      ),
    );
    const hydrated = { ...table, columns: createdColumns };
    setTables([hydrated]);
    setActiveTable(hydrated);
  }

  async function addSampleRow() {
    if (!activeTable) return;
    await createRow(activeTable.id, {
      alert_name: "Suspicious PowerShell",
      endpoint: `srv-${Math.ceil(Math.random() * 4)}`,
      severity: ["low", "medium", "high", "critical"][Math.floor(Math.random() * 4)],
      status: Math.random() > 0.65 ? "incident" : "alert",
      created_date: new Date().toISOString(),
    });
    await refreshRows(activeTable.id);
  }

  async function refreshRows(tableId: string) {
    setRows(await listRows(tableId));
  }

  async function refreshKpis(table: DynamicTable) {
    const mapping = Object.fromEntries(table.columns.map((column) => [column.key, column.key]));
    const selected = ["alert_count", "conversion_rate", "top_endpoint", "severity_distribution"];
    const results = await Promise.all(
      selected.map((metric_key) => queryKpi({ table_id: table.id, metric_key, mapping })),
    );
    setKpis(results);
  }

  const tableCountLabel = useMemo(() => `${tables.length} table${tables.length > 1 ? "s" : ""}`, [tables.length]);

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <ShieldAlert size={26} />
          <div>
            <strong>KPI-SOC</strong>
            <span>Incident weather</span>
          </div>
        </div>
        <nav>
          <button className="nav-item active" type="button">
            <Database size={18} /> Table
          </button>
          <button className="nav-item" type="button">
            <BarChart3 size={18} /> KPI
          </button>
          <button className="nav-item" type="button">
            <Activity size={18} /> Météo
          </button>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">{tableCountLabel}</p>
            <h1>{activeTable?.label ?? "Socle incident & KPI"}</h1>
          </div>
          <div className="actions">
            {!activeTable && (
              <button className="primary" type="button" onClick={createDemoTable}>
                <Plus size={18} /> Initialiser
              </button>
            )}
            {activeTable && (
              <button className="primary" type="button" onClick={addSampleRow}>
                <Plus size={18} /> Ligne
              </button>
            )}
          </div>
        </header>

        <section className="kpi-grid">
          {kpis.map((kpi) => (
            <KpiPanel key={kpi.metric_key} result={kpi} />
          ))}
        </section>

        <section className="data-zone">
          {loading && <div className="empty-state">Chargement...</div>}
          {!loading && activeTable && <DataGrid table={activeTable} rows={rows} />}
          {!loading && !activeTable && (
            <div className="empty-state">
              <h2>Aucune table configuree</h2>
              <p>Initialisez la table SOC de demonstration pour commencer a saisir des alertes.</p>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
