export type ColumnType =
  | "text"
  | "number"
  | "boolean"
  | "date"
  | "datetime"
  | "enum"
  | "severity"
  | "endpoint"
  | "status";

export interface DynamicColumn {
  id: string;
  table_id: string;
  key: string;
  label: string;
  data_type: ColumnType;
  required: boolean;
  options?: Record<string, unknown>;
  position: number;
  created_at?: string;
  updated_at?: string;
}

export interface DynamicTable {
  id: string;
  name: string;
  label: string;
  description?: string;
  columns: DynamicColumn[];
}

export interface DynamicRow {
  id: string;
  table_id: string;
  values: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface RowQuery {
  q?: string;
  column?: string;
  value?: string;
  limit?: number;
  offset?: number;
}

export interface KpiDefinition {
  key: string;
  label: string;
  description: string;
  chart_type: "stat" | "bar" | "line" | "pie" | "table";
  required_columns: string[];
}

export interface KpiResult {
  metric_key: string;
  label: string;
  chart_type: "stat" | "bar" | "line" | "pie" | "table";
  value: unknown;
  series: Array<{ label: string; value: number }>;
}

export interface SekoiaImportPayload {
  table_id: string;
  api_key: string;
  base_url: string;
  limit: number;
  query_params: Record<string, string>;
  mapping: Record<string, string>;
}

export interface SekoiaImportResult {
  imported: number;
  skipped: number;
  endpoint: string;
  sample: Array<Record<string, unknown>>;
}
