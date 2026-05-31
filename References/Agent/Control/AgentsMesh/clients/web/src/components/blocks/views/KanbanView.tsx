"use client";

import React from "react";

import type { Block, ViewSpec } from "@/lib/viewModels/blockstore";
import { useBlockTypeSpec } from "@/lib/blockstore/useBlockTypeSpec";
import { cn } from "@/lib/utils";

import { BlockRenderer } from "../BlockRenderer";
import { useBlockstoreDispatch } from "../editor/useBlockstoreDispatch";

import { ViewHeader } from "./ViewListFallback";
import { SummaryBar } from "./SummaryBar";
import { groupBlocks, useViewBlocks } from "./useViewBlocks";

// Fallback order for the hardcoded 'task.status' kanban when no schema is
// registered for the source type. Schema-driven types use their select
// options as the authoritative column order.
const DEFAULT_STATUS_ORDER = ["todo", "in_progress", "done", "—"];

export function KanbanView({ viewBlock, spec }: { viewBlock: Block; spec: ViewSpec }) {
  const items = useViewBlocks(spec, viewBlock.workspace_id);
  const groupKey = spec.group_by ?? "status";
  const groups = groupBlocks(items, groupKey);
  const sourceSpec = useBlockTypeSpec(viewBlock.workspace_id, spec.source_type);
  const columns = orderedColumns(groups, spec, sourceSpec, groupKey);
  const dispatch = useBlockstoreDispatch(viewBlock.workspace_id);

  return (
    <section className="flex flex-col gap-3">
      <ViewHeader
        title={spec.title ?? `${spec.source_type} · kanban by ${groupKey}`}
        count={items.length}
      />
      <SummaryBar blocks={items} summaryColumns={spec.summary_columns ?? []} />
      <div className="flex gap-3 overflow-x-auto pb-2">
        {columns.map((col) => (
          <KanbanColumn
            key={col}
            groupKey={groupKey}
            columnValue={col}
            blocks={groups[col] ?? []}
            onAdd={() => {
              const data: Record<string, unknown> = {
                title: "",
                [groupKey]: col === "—" ? "" : col,
              };
              void dispatch.insertChild(viewBlock.id, spec.source_type, data);
            }}
          />
        ))}
      </div>
    </section>
  );
}

// orderedColumns resolves the kanban column order in priority:
//   1. Explicit spec.column_order override (for view authors who want to
//      pin a custom sequence).
//   2. The source type's select column options (schema-driven — OKR by
//      quarter lays out Q1/Q2/Q3/Q4 even with zero records in some).
//   3. The legacy status heuristic (task.status backward compat).
function orderedColumns(
  groups: Record<string, Block[]>,
  spec: ViewSpec,
  sourceSpec: ReturnType<typeof useBlockTypeSpec>,
  groupKey: string,
): string[] {
  const fromData = (spec as unknown as { column_order?: string[] }).column_order;
  if (fromData?.length) return fromData;
  const col = sourceSpec?.columns?.find((c) => c.key === groupKey);
  if (col && (col.type === "select" || col.type === "multi_select") && col.options?.length) {
    const known = col.options.map((o) => o.value);
    const extras = Object.keys(groups).filter((k) => !known.includes(k) && k !== "—");
    return [...known, ...extras, "—"];
  }
  const known = DEFAULT_STATUS_ORDER.filter((c) => c in groups || c === "todo");
  const extras = Object.keys(groups).filter((k) => !known.includes(k));
  return [...known, ...extras];
}

function KanbanColumn({
  groupKey,
  columnValue,
  blocks,
  onAdd,
}: {
  groupKey: string;
  columnValue: string;
  blocks: Block[];
  onAdd: () => void;
}) {
  return (
    <div className="flex w-72 shrink-0 flex-col gap-2 rounded-md border border-border bg-muted/20 p-2">
      <div className="flex items-baseline justify-between px-1">
        <span className={cn("text-xs font-semibold uppercase tracking-wide", columnBadgeClass(columnValue))}>
          {displayValue(columnValue)}
        </span>
        <span className="text-xs text-muted-foreground">{blocks.length}</span>
      </div>
      <div className="flex flex-col gap-2">
        {blocks.map((b) => (
          <div key={b.id} className="rounded border border-border bg-background p-2 shadow-sm">
            <BlockRenderer blockID={b.id} depth={0} />
          </div>
        ))}
      </div>
      <button
        type="button"
        onClick={onAdd}
        className="rounded border border-dashed border-muted-foreground/30 px-2 py-1 text-xs text-muted-foreground hover:border-muted-foreground/60 hover:text-foreground"
      >
        + {groupKey}:{displayValue(columnValue)}
      </button>
    </div>
  );
}

function columnBadgeClass(value: string): string {
  switch (value) {
    case "todo": return "text-slate-500";
    case "in_progress": return "text-amber-600";
    case "done": return "text-emerald-600";
    default: return "text-muted-foreground";
  }
}

function displayValue(v: string): string {
  if (!v || v === "—") return "unset";
  return v;
}
