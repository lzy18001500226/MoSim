"use client";

import React from "react";

import type { Block, ViewColumn, ViewSpec } from "@/lib/viewModels/blockstore";
import { useBlockTypeSpec } from "@/lib/blockstore/useBlockTypeSpec";
import { cn } from "@/lib/utils";

import { FieldRenderer } from "../editor/FieldRenderer";
import { useBlockstoreDispatch } from "../editor/useBlockstoreDispatch";

import { SummaryBar } from "./SummaryBar";
import { ViewHeader } from "./ViewListFallback";
import { useViewBlocks } from "./useViewBlocks";

// TableView projects source blocks as rows. Column selection priority:
//   1. spec.columns (view author override)
//   2. Source type's registered column schema (auto-wide OKR table shows
//      title / quarter / progress even without explicit spec.columns)
//   3. Legacy ["title","status"] fallback for hardcoded task type
// Cells delegate to FieldRenderer so select / date / user columns get the
// right widget instead of a raw text input.
export function TableView({ viewBlock, spec }: { viewBlock: Block; spec: ViewSpec }) {
  const rows = useViewBlocks(spec, viewBlock.workspace_id);
  const sourceSpec = useBlockTypeSpec(viewBlock.workspace_id, spec.source_type);
  const dispatch = useBlockstoreDispatch(viewBlock.workspace_id);

  const columns: ViewColumn[] = resolveColumns(spec, sourceSpec);
  const columnSpecMap = new Map<string, (typeof sourceSpec extends infer S
    ? S extends { columns?: Array<infer C> } ? C : never
    : never)>();
  for (const c of sourceSpec?.columns ?? []) columnSpecMap.set(c.key, c);

  return (
    <section className="flex flex-col gap-3">
      <ViewHeader title={spec.title ?? `${spec.source_type} · table`} count={rows.length} />
      <SummaryBar blocks={rows} summaryColumns={spec.summary_columns ?? []} />
      <div className="overflow-x-auto rounded border border-border">
        <table className="w-full text-sm">
          <thead className="border-b border-border bg-muted/30 text-left">
            <tr>
              {columns.map((c) => (
                <th key={c.key} className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {c.label ?? columnSpecMap.get(c.key)?.label ?? c.key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={row.id} className={cn(idx % 2 === 0 && "bg-muted/10")}>
                {columns.map((c) => {
                  const colSpec = columnSpecMap.get(c.key);
                  return (
                    <td key={c.key} className="border-b border-border px-3 py-1.5 align-top">
                      {colSpec ? (
                        <FieldRenderer
                          column={colSpec}
                          value={row.data?.[c.key]}
                          onChange={(next) => dispatch.updateBlockData(row.id, { [c.key]: next })}
                        />
                      ) : (
                        <CellEditor
                          value={(row.data?.[c.key] as string | undefined) ?? ""}
                          onCommit={(next) => dispatch.updateBlockData(row.id, { [c.key]: next })}
                        />
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function resolveColumns(
  spec: ViewSpec,
  sourceSpec: ReturnType<typeof useBlockTypeSpec>,
): ViewColumn[] {
  if (spec.columns?.length) return spec.columns;
  if (sourceSpec?.columns?.length) {
    return sourceSpec.columns
      .filter((c) => !c.deprecated)
      .map((c) => ({ key: c.key, label: c.label }));
  }
  return [{ key: "title" }, { key: "status" }];
}

function CellEditor({ value, onCommit }: { value: string; onCommit: (next: string) => void }) {
  const [local, setLocal] = React.useState(value);
  React.useEffect(() => setLocal(value), [value]);
  return (
    <input
      type="text"
      value={local}
      onChange={(e) => setLocal(e.target.value)}
      onBlur={() => { if (local !== value) onCommit(local); }}
      onKeyDown={(e) => {
        if (e.key === "Enter") (e.currentTarget as HTMLInputElement).blur();
      }}
      className="w-full bg-transparent outline-none focus:ring-1 focus:ring-ring focus:ring-offset-0"
    />
  );
}
