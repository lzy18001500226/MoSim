"use client";

import React from "react";

import type { Block, ViewSpec } from "@/lib/viewModels/blockstore";

import { GalleryView } from "./GalleryView";
import { KanbanView } from "./KanbanView";
import { TableView } from "./TableView";
import { TimelineView } from "./TimelineView";
import { TreeView } from "./TreeView";
import { ViewListFallback } from "./ViewListFallback";

// Dispatch a `view` block to the matching layout renderer.
// Unknown layouts fall back to a plain ViewListFallback so a bad Agent-authored
// view still renders rather than throwing.
export function ViewRenderer({ block }: { block: Block }) {
  const spec = (block.data as unknown) as ViewSpec;
  if (!spec || !spec.source_type || !spec.layout) {
    return <MalformedView />;
  }
  switch (spec.layout) {
    case "kanban":
      return <KanbanView viewBlock={block} spec={spec} />;
    case "table":
      return <TableView viewBlock={block} spec={spec} />;
    case "timeline":
      return <TimelineView viewBlock={block} spec={spec} />;
    case "tree":
      return <TreeView viewBlock={block} spec={spec} />;
    case "gallery":
      return <GalleryView viewBlock={block} spec={spec} />;
    case "list":
    default:
      return <ViewListFallback viewBlock={block} spec={spec} />;
  }
}

function MalformedView() {
  return (
    <div className="rounded border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
      View block is missing required data fields (source_type, layout).
    </div>
  );
}
