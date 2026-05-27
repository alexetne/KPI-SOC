import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { KpiResult } from "../types/api";

const colors = ["#2563eb", "#059669", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"];

interface Props {
  result: KpiResult;
}

export function KpiPanel({ result }: Props) {
  return (
    <article className="kpi-card">
      <header>
        <span>{result.label}</span>
        <strong>{String(result.value ?? "-")}</strong>
      </header>
      {result.chart_type === "bar" && (
        <ResponsiveContainer width="100%" height={120}>
          <BarChart data={result.series}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="label" hide />
            <YAxis hide />
            <Tooltip />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      )}
      {result.chart_type === "line" && (
        <ResponsiveContainer width="100%" height={120}>
          <LineChart data={result.series}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="label" hide />
            <YAxis hide />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#059669" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
      {result.chart_type === "pie" && (
        <ResponsiveContainer width="100%" height={120}>
          <PieChart>
            <Pie data={result.series} dataKey="value" nameKey="label" outerRadius={46}>
              {result.series.map((entry, index) => (
                <Cell key={entry.label} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      )}
    </article>
  );
}
