"use client";

import React from "react";
import { ExternalLink, Link2 } from "lucide-react";

import type { Block } from "@/lib/viewModels/blockstore";
import { isSafeURL, sanitizeURL } from "@/lib/blockstore/urlGuard";

import { BlockChrome } from "../editor/BlockChrome";
import { CommentsSection } from "../editor/CommentsSection";
import { useBlockstoreDispatch } from "../editor/useBlockstoreDispatch";

// BookmarkRenderer is a compact "link preview" card. Phase 4 keeps it
// client-driven: the user (or Agent) writes title / description / image
// explicitly. A server-side Open-Graph fetcher can populate these later
// without changing the block shape.
export function BookmarkRenderer({ block }: { block: Block }) {
  const dispatch = useBlockstoreDispatch(block.workspace_id);
  const url = (block.data?.url as string | undefined) ?? "";
  const title = (block.data?.title as string | undefined) ?? "";
  const description = (block.data?.description as string | undefined) ?? "";
  const image = (block.data?.image as string | undefined) ?? "";

  const handleDelete = () => {
    void dispatch.detachChild(block.id);
    void dispatch.removeBlock(block.id);
  };

  const onPasteUrl = () => {
    const next = window.prompt("Bookmark URL:", url);
    if (!next) return;
    if (!isSafeURL(next)) {
      window.alert("Only http(s) URLs are allowed.");
      return;
    }
    dispatch.updateBlockData(
      block.id,
      { url: next, title: title || next },
      { text: next },
    );
  };

  return (
    <BlockChrome
      className=""
      blockID={block.id}
      onDelete={handleDelete}
      onDuplicate={() => void dispatch.duplicate(block.id)}
      onToggleVisibility={(next) => void dispatch.setBlockVisibility(block.id, next)}
    >
      {url ? (
        <a
          href={sanitizeURL(url) || "#"}
          target="_blank"
          rel="noopener noreferrer"
          className="flex gap-3 overflow-hidden rounded-md border border-border hover:bg-muted/30"
        >
          {image && isSafeURL(image) && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={image} alt="" className="h-24 w-32 shrink-0 object-cover" />
          )}
          <div className="flex min-w-0 flex-1 flex-col justify-between gap-1 p-3">
            <div>
              <p className="truncate text-sm font-medium">{title || url}</p>
              {description && (
                <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                  {description}
                </p>
              )}
            </div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <ExternalLink className="h-3 w-3" />
              <span className="truncate">{url}</span>
            </div>
          </div>
        </a>
      ) : (
        <button
          type="button"
          onClick={onPasteUrl}
          className="flex w-full items-center gap-2 rounded-md border border-dashed border-border bg-muted/30 p-3 text-sm text-muted-foreground hover:bg-muted/50"
        >
          <Link2 className="h-4 w-4" />
          <span>Paste a URL to bookmark</span>
        </button>
      )}
      <CommentsSection blockID={block.id} workspaceID={block.workspace_id} />
    </BlockChrome>
  );
}
