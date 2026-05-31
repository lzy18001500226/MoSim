"use client";

import React, { useRef, useState } from "react";
import { FileText, Upload } from "lucide-react";

import type { Block } from "@/lib/viewModels/blockstore";
import { uploadImage } from "@/lib/api/facade/file";
import { cn, getErrorMessage } from "@/lib/utils";

import { BlockChrome } from "../editor/BlockChrome";
import { CommentsSection } from "../editor/CommentsSection";
import { useBlockstoreDispatch } from "../editor/useBlockstoreDispatch";

// FileRenderer is a generic attachment row: icon + name + size + download
// link. Reuses the image upload endpoint (server-side allow-list already
// includes common doc / archive types).
export function FileRenderer({ block }: { block: Block }) {
  const dispatch = useBlockstoreDispatch(block.workspace_id);
  const url = (block.data?.url as string | undefined) ?? "";
  const name = (block.data?.name as string | undefined) ?? "";
  const size = (block.data?.size as number | undefined) ?? 0;
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = () => {
    void dispatch.detachChild(block.id);
    void dispatch.removeBlock(block.id);
  };

  const onPick = async (file: File) => {
    setError(null);
    setUploading(true);
    try {
      const uploaded = await uploadImage(file);
      await dispatch.updateBlockData(
        block.id,
        { url: uploaded, name: file.name, size: file.size, mime: file.type },
        { text: file.name },
      );
    } catch (e) {
      setError(getErrorMessage(e, "Upload failed"));
    } finally {
      setUploading(false);
    }
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
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 rounded-md border border-border bg-muted/30 p-3 hover:bg-muted/50"
        >
          <FileText className="h-5 w-5 shrink-0 text-muted-foreground" />
          <div className="flex flex-col">
            <span className="text-sm">{name}</span>
            {size > 0 && (
              <span className="text-xs text-muted-foreground">{formatBytes(size)}</span>
            )}
          </div>
        </a>
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
          className={cn(
            "flex w-full items-center gap-2 rounded-md border border-dashed border-border bg-muted/30 p-3 text-sm text-muted-foreground hover:bg-muted/50",
            uploading && "opacity-50",
          )}
        >
          {uploading ? <Upload className="h-4 w-4 animate-pulse" /> : <FileText className="h-4 w-4" />}
          <span>{uploading ? "Uploading…" : "Click to upload file"}</span>
        </button>
      )}
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) void onPick(file);
          e.target.value = "";
        }}
      />
      {error && <p className="mt-1 text-xs text-destructive">{error}</p>}
      <CommentsSection blockID={block.id} workspaceID={block.workspace_id} />
    </BlockChrome>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
