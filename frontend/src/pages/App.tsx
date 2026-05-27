import {
  Activity,
  BarChart3,
  Database,
  Filter,
  Plus,
  RefreshCw,
  ShieldAlert,
  Trash2,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";

import { DataGrid } from "../components/DataGrid";
import { KpiPanel } from "../components/KpiPanel";
import {
  createColumn,
  createRow,
  deleteColumn,
  deleteRow,
  listKpiDefinitions,
  listRows,
  listTables,
  queryKpi,
  seedDemo,
} from "../services/api";
import type { ColumnType, DynamicColumn, DynamicRow, DynamicTable, KpiDefinition, KpiResult } from "../types/api";

const columnTypes: ColumnType[] = ["text", "number", "boolean", "date", "datetime", "enum", "severity", "endpoint", "status"];
const defaultMetricKeys = [
  "alert_count",
  "conversion_rate",
  "top_endpoint",
  "severity_distribution",
  "status_distribution",
  "alerts_over_time",
  "mean_time_to_close",
];

export function App() {
  const [tables, setTables] = useState<DynamicTable[]>([]);
  const [activeTable, setActiveTable] = useState<DynamicTable | null>(null);
  const [rows, setRows] = useState<DynamicRow[]>([]);
  const [kpiDefinitions, setKpiDefinitions] = useState<KpiDefinition[]>([]);
  const [kpis, setKpis] = useState<KpiResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState({ q: "", column: "", value: "" });
  const [columnDraft, setColumnDraft] = useState({
    key: "",
    label: "",
    data_type: "text" as ColumnType,
    required: false,
    choices: "",
  });
  const [rowDraft, setRowDraft] = useState<Record<string, string>>({});

  const bootstrap = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [tableData, definitions] = await Promise.all([listTables(), listKpiDefinitions()]);
      setTables(tableData);
      setActiveTable((current) => tableData.find((table) => table.id === current?.id) ?? tableData[0] ?? null);
      setKpiDefinitions(definitions);
    } catch (err) {
      setError(readError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  const refreshRows = useCallback(
    async (tableId = activeTable?.id) => {
      if (!tableId) return;
      const data = await listRows(tableId, {
        q: filter.q || undefined,
        column: filter.column || undefined,
        value: filter.value || undefined,
      });
      setRows(data);
    },
    [activeTable?.id, filter.column, filter.q, filter.value],
  );

  const refreshKpis = useCallback(
    async (table: DynamicTable) => {
      const mapping = Object.fromEntries(table.columns.map((column) => [column.key, column.key]));
      const filters = filter.column && filter.value ? { [filter.column]: filter.value, q: filter.q } : { q: filter.q };
      const runnable = defaultMetricKeys.filter((key) => kpiDefinitions.some((definition) => definition.key === key));
      const results = await Promise.all(
        runnable.map((metric_key) => queryKpi({ table_id: table.id, metric_key, mapping, filters })),
      );
      setKpis(results);
    },
    [filter.column, filter.q, filter.value, kpiDefinitions],
  );

  useEffect(() => {
    if (!activeTable) return;
    setRowDraft(defaultRowDraft(activeTable.columns));
    void refreshRows(activeTable.id);
  }, [activeTable, refreshRows]);

  useEffect(() => {
    if (!activeTable) return;
    void refreshKpis(activeTable);
  }, [activeTable, rows, refreshKpis]);

  async function handleSeed() {
    setError(null);
    try {
      const table = await seedDemo();
      await bootstrap();
      setActiveTable(table);
    } catch (err) {
      setError(readError(err));
    }
  }

  async function handleCreateColumn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!activeTable) return;
    setError(null);
    try {
      const options =
        columnDraft.data_type === "enum" || columnDraft.data_type === "severity" || columnDraft.data_type === "status"
          ? { choices: columnDraft.choices.split(",").map((choice) => choice.trim()).filter(Boolean) }
          : undefined;
      await createColumn(activeTable.id, {
        key: normalizeKey(columnDraft.key || columnDraft.label),
        label: columnDraft.label,
        data_type: columnDraft.data_type,
        required: columnDraft.required,
        options,
        position: activeTable.columns.length,
      });
      setColumnDraft({ key: "", label: "", data_type: "text", required: false, choices: "" });
      await bootstrap();
    } catch (err) {
      setError(readError(err));
    }
  }

  async function handleCreateRow(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!activeTable) return;
    setError(null);
    try {
      await createRow(activeTable.id, parseRowValues(activeTable.columns, rowDraft));
      setRowDraft(defaultRowDraft(activeTable.columns));
      await refreshRows(activeTable.id);
    } catch (err) {
      setError(readError(err));
    }
  }

  async function handleDeleteColumn(column: DynamicColumn) {
    if (!activeTable) return;
    setError(null);
    try {
      await deleteColumn(activeTable.id, column.id);
      await bootstrap();
    } catch (err) {
      setError(readError(err));
    }
  }

  async function handleDeleteRow(rowId: string) {
    if (!activeTable) return;
    await deleteRow(activeTable.id, rowId);
    await refreshRows(activeTable.id);
  }

  const activeColumnChoices = activeTable?.columns ?? [];
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
            <button className="ghost" type="button" onClick={() => void bootstrap()}>
              <RefreshCw size={18} /> Rafraichir
            </button>
            <button className="primary" type="button" onClick={handleSeed}>
              <Plus size={18} /> Seed SOC
            </button>
          </div>
        </header>

        {error && <div className="alert">{error}</div>}

        {activeTable && (
          <section className="control-band">
            <div className="field-group wide">
              <label htmlFor="table-select">Table</label>
              <select
                id="table-select"
                value={activeTable.id}
                onChange={(event) => setActiveTable(tables.find((table) => table.id === event.target.value) ?? null)}
              >
                {tables.map((table) => (
                  <option key={table.id} value={table.id}>
                    {table.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="field-group wide">
              <label htmlFor="global-filter">Recherche</label>
              <input
                id="global-filter"
                placeholder="Endpoint, alerte, analyste..."
                value={filter.q}
                onChange={(event) => setFilter((current) => ({ ...current, q: event.target.value }))}
              />
            </div>
            <div className="field-group">
              <label htmlFor="column-filter">Colonne</label>
              <select
                id="column-filter"
                value={filter.column}
                onChange={(event) => setFilter((current) => ({ ...current, column: event.target.value }))}
              >
                <option value="">Toutes</option>
                {activeColumnChoices.map((column) => (
                  <option key={column.id} value={column.key}>
                    {column.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="field-group">
              <label htmlFor="value-filter">Valeur</label>
              <input
                id="value-filter"
                placeholder="ex: high"
                value={filter.value}
                onChange={(event) => setFilter((current) => ({ ...current, value: event.target.value }))}
              />
            </div>
            <button className="secondary" type="button" onClick={() => void refreshRows()}>
              <Filter size={18} /> Filtrer
            </button>
          </section>
        )}

        <section className="kpi-grid">
          {kpis.map((kpi) => (
            <KpiPanel key={kpi.metric_key} result={kpi} />
          ))}
        </section>

        {activeTable && (
          <section className="editor-grid">
            <form className="tool-panel" onSubmit={handleCreateColumn}>
              <header>
                <h2>Colonnes</h2>
                <span>{activeTable.columns.length} champs</span>
              </header>
              <div className="column-list">
                {activeTable.columns.map((column) => (
                  <div className="column-chip" key={column.id}>
                    <div>
                      <strong>{column.label}</strong>
                      <span>{column.key} · {column.data_type}</span>
                    </div>
                    <button className="icon-button danger" type="button" title="Supprimer" onClick={() => void handleDeleteColumn(column)}>
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>
              <div className="form-grid">
                <input
                  placeholder="Libelle"
                  value={columnDraft.label}
                  onChange={(event) => setColumnDraft((current) => ({ ...current, label: event.target.value }))}
                  required
                />
                <input
                  placeholder="cle_api"
                  value={columnDraft.key}
                  onChange={(event) => setColumnDraft((current) => ({ ...current, key: event.target.value }))}
                />
                <select
                  value={columnDraft.data_type}
                  onChange={(event) => setColumnDraft((current) => ({ ...current, data_type: event.target.value as ColumnType }))}
                >
                  {columnTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
                <input
                  placeholder="choix enum, separes par virgule"
                  value={columnDraft.choices}
                  onChange={(event) => setColumnDraft((current) => ({ ...current, choices: event.target.value }))}
                />
              </div>
              <label className="check-line">
                <input
                  type="checkbox"
                  checked={columnDraft.required}
                  onChange={(event) => setColumnDraft((current) => ({ ...current, required: event.target.checked }))}
                />
                Obligatoire
              </label>
              <button className="secondary" type="submit">
                <Plus size={18} /> Ajouter colonne
              </button>
            </form>

            <form className="tool-panel" onSubmit={handleCreateRow}>
              <header>
                <h2>Nouvelle ligne</h2>
                <span>Saisie dynamique</span>
              </header>
              <div className="row-form">
                {activeTable.columns.map((column) => (
                  <label key={column.id}>
                    <span>{column.label}</span>
                    {renderRowInput(column, rowDraft[column.key] ?? "", (value) =>
                      setRowDraft((current) => ({ ...current, [column.key]: value })),
                    )}
                  </label>
                ))}
              </div>
              <button className="primary" type="submit">
                <Plus size={18} /> Ajouter ligne
              </button>
            </form>
          </section>
        )}

        <section className="data-zone">
          {loading && <div className="empty-state">Chargement...</div>}
          {!loading && activeTable && <DataGrid table={activeTable} rows={rows} onDeleteRow={(id) => void handleDeleteRow(id)} />}
          {!loading && !activeTable && (
            <div className="empty-state">
              <h2>Aucune table configuree</h2>
              <p>Seed SOC cree une table d'alertes, des colonnes typees et un jeu de donnees de demonstration.</p>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

function renderRowInput(column: DynamicColumn, value: string, onChange: (value: string) => void) {
  const choices = Array.isArray(column.options?.choices) ? (column.options?.choices as string[]) : [];
  if (column.data_type === "boolean") {
    return (
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">-</option>
        <option value="true">Oui</option>
        <option value="false">Non</option>
      </select>
    );
  }
  if (choices.length > 0) {
    return (
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">-</option>
        {choices.map((choice) => (
          <option key={choice} value={choice}>
            {choice}
          </option>
        ))}
      </select>
    );
  }
  return (
    <input
      type={column.data_type === "number" ? "number" : column.data_type === "date" ? "date" : "text"}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      required={column.required}
    />
  );
}

function defaultRowDraft(columns: DynamicColumn[]) {
  return Object.fromEntries(columns.map((column) => [column.key, ""]));
}

function parseRowValues(columns: DynamicColumn[], draft: Record<string, string>) {
  return Object.fromEntries(
    columns
      .map((column) => {
        const rawValue = draft[column.key];
        if (rawValue === "") return [column.key, null];
        if (column.data_type === "number") return [column.key, Number(rawValue)];
        if (column.data_type === "boolean") return [column.key, rawValue === "true"];
        return [column.key, rawValue];
      })
      .filter(([, value]) => value !== null),
  );
}

function normalizeKey(value: string) {
  const key = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return /^[a-z]/.test(key) ? key : `c_${key}`;
}

function readError(error: unknown) {
  if (typeof error === "object" && error && "message" in error) {
    return String((error as { message: unknown }).message);
  }
  return "Une erreur est survenue";
}
