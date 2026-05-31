"use client";

import React, { useState } from "react";

import type { Block } from "@/lib/viewModels/blockstore";
import { BLOCK_TYPE_TASK } from "@/lib/viewModels/blockstore";
import { cn } from "@/lib/utils";

import { NestChildren } from "../BlockRenderer";
import { BlockChrome } from "../editor/BlockChrome";
import { CommentsSection } from "../editor/CommentsSection";
import { EditableText } from "../editor/EditableText";
import { SlashMenu } from "../editor/SlashMenu";
import { standardSlashOptions } from "../editor/slashOptions";
import { useAutoFocusIfPending } from "../editor/useAutoFocus";
import { useBlockstoreDispatch } from "../editor/useBlockstoreDispatch";

type TaskStatus = "todo" | "in_progress" | "done";

export function TaskRenderer({ block, depth }: { block: Block; depth: number }) {
  const dispatch = useBlockstoreDispatch(block.workspace_id);
  const autoFocus = useAutoFocusIfPending(block.id);
  const title = (block.data?.title as string | undefined) ?? "";
  const status = ((block.data?.status as string | undefined) ?? "todo") as TaskStatus;
  const done = status === "done";
  const [slashOpen, setSlashOpen] = useState(false);

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
      <div className="flex items-center gap-2 rounded px-1 py-0.5 hover:bg-accent/40">
        <input
          type="checkbox"
          checked={done}
          onChange={() => {
            const next: TaskStatus = done ? "todo" : "done";
            dispatch.updateBlockData(block.id, { status: next });
          }}
          className="h-4 w-4"
        />
        <EditableText
          className={cn(
            "flex-1 outline-none",
            done && "text-muted-foreground line-through",
          )}
          placeholder="New task"
          value={title}
          autoFocus={autoFocus}
          onChange={(next) => dispatch.updateBlockData(block.id, { title: next }, { text: next })}
          onEnter={() => {
            void dispatch.insertSiblingAfter(block.id, BLOCK_TYPE_TASK, { title: "", status: "todo" }, { text: "" });
          }}
          onBackspaceEmpty={handleDelete}
          onSlashOnEmpty={() => setSlashOpen(true)}
        />
      </div>
      {slashOpen && (
        <div className="absolute left-8 top-full z-50 mt-1">
          <SlashMenu
            open
            options={standardSlashOptions(dispatch, block.id)}
            onClose={() => setSlashOpen(false)}
          />
        </div>
      )}
      <div className="pl-6">
        <NestChildren parentID={block.id} depth={depth} />
        <CommentsSection blockID={block.id} workspaceID={block.workspace_id} />
      </div>
    </BlockChrome>
  );
}
