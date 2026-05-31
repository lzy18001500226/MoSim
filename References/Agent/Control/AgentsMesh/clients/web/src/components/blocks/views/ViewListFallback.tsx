"use client";

import React from "react";

import type { Block, ViewSpec } from "@/lib/viewModels/blockstore";

import { BlockRenderer } from "../BlockRenderer";
import { useViewBlocks } from "./useViewBlocks";

// ViewListFallback renders source blocks as a flat list. Used when the spec's
// layout is "list" or unknown — callers see something sensible rather than an
// empty div.
export function ViewListFallback({ viewBlock, spec }: { viewBlock: Block; spec: ViewSpec }) {
  const items = useViewBlocks(spec, viewBlock.workspace_id);
  return (
    <section className="flex flex-col gap-2">
      <ViewHeader title={spec.title ?? `${spec.source_type} · list`} count={items.length} />
      {items.length === 0 ? (
        <EmptyHint sourceType={spec.source_type} />
      ) : (
        <div className="flex flex-col gap-1">
          {items.map((b) => (
            <BlockRenderer key={b.id} blockID={b.id} depth={0} />
          ))}
        </div>
      )}
    </section>
  );
}

export function ViewHeader({ title, count }: { title: string; count: number }) {
  return (
    <div className="flex items-baseline justify-between">
      <h3 className="text-sm font-semibold text-foreground/90">{title}</h3>
      <span className="text-xs text-muted-foreground">{count}</span>
    </div>
  );
}

export function EmptyHint({ sourceType }: { sourceType: string }) {
  return (
    <div className="rounded border border-dashed border-muted-foreground/40 p-3 text-xs text-muted-foreground">
      No <code className="font-mono">{sourceType}</code> blocks match this view.
    </div>
  );
}
