"use client";

import React from "react";

import type { Block } from "@/lib/viewModels/blockstore";

import { BlockChrome } from "../editor/BlockChrome";
import { useBlockstoreDispatch } from "../editor/useBlockstoreDispatch";

// DividerRenderer is a purely visual horizontal rule. No editable content,
// no text, no nested children. Kept minimal so the surrounding BlockChrome
// handles delete / duplicate / reorder uniformly.
export function DividerRenderer({ block }: { block: Block }) {
  const dispatch = useBlockstoreDispatch(block.workspace_id);
  const handleDelete = () => {
    void dispatch.detachChild(block.id);
    void dispatch.removeBlock(block.id);
  };
  return (
    <BlockChrome
      className="py-2"
      blockID={block.id}
      onDelete={handleDelete}
      onDuplicate={() => void dispatch.duplicate(block.id)}
    >
      <hr className="border-border" />
    </BlockChrome>
  );
}
