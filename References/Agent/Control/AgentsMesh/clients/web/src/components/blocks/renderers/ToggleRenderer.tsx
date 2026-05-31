"use client";

import React from "react";
import { ChevronRight } from "lucide-react";

import type { Block } from "@/lib/viewModels/blockstore";
import { BLOCK_TYPE_PARAGRAPH } from "@/lib/viewModels/blockstore";
import { cn } from "@/lib/utils";

import { NestChildren } from "../BlockRenderer";
import { BlockChrome } from "../editor/BlockChrome";
import { CommentsSection } from "../editor/CommentsSection";
import { EditableText } from "../editor/EditableText";
import { useAutoFocusIfPending } from "../editor/useAutoFocus";
import { useBlockstoreDispatch } from "../editor/useBlockstoreDispatch";

// ToggleRenderer hides / shows its nest children based on data.collapsed.
// Clicking the chevron flips state via updateBlockData — the state lives
// in the block itself so the collapsed/open choice is shared across clients.
export function ToggleRenderer({ block, depth }: { block: Block; depth: number }) {
  const dispatch = useBlockstoreDispatch(block.workspace_id);
  const autoFocus = useAutoFocusIfPending(block.id);
  const summary = (block.data?.summary as string | undefined) ?? "";
  const collapsed = (block.data?.collapsed as boolean | undefined) ?? false;

  const handleDelete = () => {
    void dispatch.detachChild(block.id);
    void dispatch.removeBlock(block.id);
  };

  return (
    <BlockChrome
      className="flex flex-col gap-1"
      blockID={block.id}
      onDelete={handleDelete}
      onDuplicate={() => void dispatch.duplicate(block.id)}
      onToggleVisibility={(next) => void dispatch.setBlockVisibility(block.id, next)}
    >
      <div className="flex items-start gap-1">
        <button
          type="button"
          onClick={() => dispatch.updateBlockData(block.id, { collapsed: !collapsed })}
          className={cn(
            "mt-0.5 text-muted-foreground transition-transform hover:text-foreground",
            !collapsed && "rotate-90",
          )}
          aria-label={collapsed ? "Expand" : "Collapse"}
        >
          <ChevronRight className="h-4 w-4" />
        </button>
        <EditableText
          className="flex-1 outline-none"
          placeholder="Toggle…"
          value={summary}
          autoFocus={autoFocus}
          onChange={(next) => dispatch.updateBlockData(block.id, { summary: next }, { text: next })}
          onEnter={() => {
            void dispatch.insertChild(block.id, BLOCK_TYPE_PARAGRAPH, { text: "" }, { text: "" });
          }}
          onBackspaceEmpty={handleDelete}
        />
      </div>
      {!collapsed && (
        <div className="pl-5">
          <NestChildren parentID={block.id} depth={depth} />
        </div>
      )}
      <CommentsSection blockID={block.id} workspaceID={block.workspace_id} />
    </BlockChrome>
  );
}
