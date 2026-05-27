import { flexRender, getCoreRowModel, useReactTable, type ColumnDef } from "@tanstack/react-table";
import { Trash2 } from "lucide-react";
import { useMemo } from "react";

import type { DynamicRow, DynamicTable } from "../types/api";

interface Props {
  table: DynamicTable;
  rows: DynamicRow[];
  onDeleteRow: (rowId: string) => void;
}

export function DataGrid({ table, rows, onDeleteRow }: Props) {
  const columns = useMemo<ColumnDef<DynamicRow>[]>(
    () => [
      ...table.columns.map((column) => ({
          accessorFn: (row: DynamicRow) => row.values[column.key],
          id: column.key,
          header: column.label,
          cell: (info: { getValue: () => unknown }) => formatValue(info.getValue()),
        })),
      {
        id: "actions",
        header: "",
        cell: ({ row }) => (
          <button className="icon-button danger" type="button" title="Supprimer" onClick={() => onDeleteRow(row.original.id)}>
            <Trash2 size={16} />
          </button>
        ),
      },
    ],
    [table.columns],
  );

  const instance = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className="table-shell">
      <div className="table-toolbar">
        <div>
          <strong>{table.label}</strong>
          <span>{rows.length} lignes</span>
        </div>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            {instance.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id}>{flexRender(header.column.columnDef.header, header.getContext())}</th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {instance.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                ))}
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td className="no-rows" colSpan={Math.max(columns.length, 1)}>
                  Aucune ligne pour le moment
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "boolean") return value ? "Oui" : "Non";
  return String(value);
}
