import axios from "axios";

import type {
  DynamicColumn,
  DynamicRow,
  DynamicTable,
  KpiDefinition,
  KpiResult,
  RowQuery,
  SekoiaImportPayload,
  SekoiaImportResult,
} from "../types/api";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
});

export async function listTables(): Promise<DynamicTable[]> {
  const { data } = await api.get<DynamicTable[]>("/tables");
  return data;
}

export async function createTable(payload: {
  name: string;
  label: string;
  description?: string;
}): Promise<DynamicTable> {
  const { data } = await api.post<DynamicTable>("/tables", payload);
  return data;
}

export async function createColumn(
  tableId: string,
  payload: Omit<DynamicColumn, "id" | "table_id">,
): Promise<DynamicColumn> {
  const { data } = await api.post<DynamicColumn>(`/tables/${tableId}/columns`, payload);
  return data;
}

export async function patchColumn(
  tableId: string,
  columnId: string,
  payload: Partial<Omit<DynamicColumn, "id" | "table_id" | "key">>,
): Promise<DynamicColumn> {
  const { data } = await api.patch<DynamicColumn>(`/tables/${tableId}/columns/${columnId}`, payload);
  return data;
}

export async function deleteColumn(tableId: string, columnId: string): Promise<void> {
  await api.delete(`/tables/${tableId}/columns/${columnId}`);
}

export async function listRows(tableId: string, query: RowQuery = {}): Promise<DynamicRow[]> {
  const { data } = await api.get<DynamicRow[]>(`/tables/${tableId}/rows`, { params: query });
  return data;
}

export async function createRow(tableId: string, values: Record<string, unknown>): Promise<DynamicRow> {
  const { data } = await api.post<DynamicRow>(`/tables/${tableId}/rows`, { values });
  return data;
}

export async function patchRow(tableId: string, rowId: string, values: Record<string, unknown>): Promise<DynamicRow> {
  const { data } = await api.patch<DynamicRow>(`/tables/${tableId}/rows/${rowId}`, { values });
  return data;
}

export async function deleteRow(tableId: string, rowId: string): Promise<void> {
  await api.delete(`/tables/${tableId}/rows/${rowId}`);
}

export async function seedDemo(): Promise<DynamicTable> {
  const { data } = await api.post<DynamicTable>("/demo/seed");
  return data;
}

export async function listKpiDefinitions(): Promise<KpiDefinition[]> {
  const { data } = await api.get<KpiDefinition[]>("/kpis/definitions");
  return data;
}

export async function queryKpi(payload: {
  table_id: string;
  metric_key: string;
  mapping: Record<string, string>;
  filters?: Record<string, unknown>;
}): Promise<KpiResult> {
  const { data } = await api.post<KpiResult>("/kpis/query", payload);
  return data;
}

export async function importSekoiaAlerts(payload: SekoiaImportPayload): Promise<SekoiaImportResult> {
  const { data } = await api.post<SekoiaImportResult>("/integrations/sekoia/import-alerts", payload);
  return data;
}
