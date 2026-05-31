"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";

import { blockstoreApi } from "@/lib/api/facade/blockstoreApi";
import type { SearchHit } from "@/lib/viewModels/blockstore";
import { getErrorMessage } from "@/lib/utils";

interface SearchPanelProps {
  workspaceID: string;
  open: boolean;
  onClose: () => void;
  onJumpToBlock?: (blockID: string) => void;
}

// SearchPanel renders a floating semantic search over one workspace. Opens
// on Cmd/Ctrl+K, closes on Esc. Debounces the input 220 ms so typing fast
// doesn't fire a request per keystroke. Empty query → zero results, no call.
export function SearchPanel({ workspaceID, open, onClose, onJumpToBlock }: SearchPanelProps) {
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<SearchHit[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    const timer = setTimeout(() => inputRef.current?.focus(), 0);
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  const runSearch = useCallback(
    async (q: string) => {
      const trimmed = q.trim();
      if (!trimmed) {
        setHits([]);
        setError(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const res = await blockstoreApi.semanticSearch(workspaceID, trimmed, { topK: 10 });
        setHits(res.hits || []);
      } catch (e) {
        setError(getErrorMessage(e, "Search failed"));
        setHits([]);
      } finally {
        setLoading(false);
      }
    },
    [workspaceID],
  );

  useEffect(() => {
    if (!open) return;
    const timer = setTimeout(() => runSearch(query), 220);
    return () => clearTimeout(timer);
  }, [query, open, runSearch]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 pt-24"
      onClick={onClose}
    >
      <div
        className="w-full max-w-xl rounded-lg border bg-background shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="border-b p-3">
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search blocks semantically…"
            className="w-full bg-transparent text-sm outline-none"
          />
        </div>
        <SearchResults
          loading={loading}
          error={error}
          hits={hits}
          query={query}
          onPick={(id) => {
            onJumpToBlock?.(id);
            onClose();
          }}
        />
        <div className="border-t p-2 text-xs text-muted-foreground">
          Semantic search · Esc to close
        </div>
      </div>
    </div>
  );
}

function SearchResults({
  loading,
  error,
  hits,
  query,
  onPick,
}: {
  loading: boolean;
  error: string | null;
  hits: SearchHit[];
  query: string;
  onPick: (blockID: string) => void;
}) {
  if (error) {
    return <div className="p-4 text-sm text-destructive">{error}</div>;
  }
  if (loading) {
    return <div className="p-4 text-sm text-muted-foreground">Searching…</div>;
  }
  if (!query.trim()) {
    return (
      <div className="p-4 text-sm text-muted-foreground">
        Type a phrase to search. Matches are ranked by meaning, not just keywords.
      </div>
    );
  }
  if (hits.length === 0) {
    return <div className="p-4 text-sm text-muted-foreground">No matches.</div>;
  }
  return (
    <ul className="max-h-96 overflow-y-auto">
      {hits.map((hit) => (
        <li key={hit.block_id}>
          <button
            type="button"
            onClick={() => onPick(hit.block_id)}
            className="flex w-full flex-col gap-1 border-b p-3 text-left text-sm hover:bg-muted"
          >
            <div className="flex items-center gap-2">
              <span className="rounded bg-muted px-1.5 py-0.5 text-xs uppercase text-muted-foreground">
                {hit.type}
              </span>
              <span className="text-xs text-muted-foreground">
                score {hit.score.toFixed(2)}
              </span>
            </div>
            <span
              className="line-clamp-2"
              dangerouslySetInnerHTML={{ __html: highlight(hit.snippet, query) }}
            />
          </button>
        </li>
      ))}
    </ul>
  );
}

// highlight wraps every case-insensitive occurrence of `q` tokens in <mark>.
// Tokens are whitespace-split; punctuation is stripped to match the backend's
// tokenizer so visual highlights align with what actually contributed to the
// score. Output is HTML-escaped before mark insertion.
function highlight(snippet: string, q: string): string {
  const escaped = escapeHTML(snippet);
  const tokens = q
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length >= 2);
  if (tokens.length === 0) return escaped;
  const pattern = new RegExp(`(${tokens.map(escapeRegex).join("|")})`, "gi");
  return escaped.replace(pattern, "<mark>$1</mark>");
}

function escapeHTML(s: string): string {
  return s
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
