"use client";

import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";
import { LoopData } from "@/stores/loop";
import { Search, Plus } from "lucide-react";
import { useTranslations } from "next-intl";

interface LoopListSidebarProps {
  loops: LoopData[];
  selectedSlug?: string | null;
  onSelect: (slug: string) => void;
  onCreate: () => void;
}

type Group = "enabled" | "disabled" | "archived";

function groupOf(loop: LoopData): Group {
  return loop.status as Group;
}

function formatRelativeShort(iso?: string | null): string {
  if (!iso) return "—";
  const date = new Date(iso);
  const diff = Date.now() - date.getTime();
  const h = Math.floor(diff / (60 * 60 * 1000));
  if (h < 1) return `${Math.max(1, Math.floor(diff / 60000))}m`;
  if (h < 24) return `${h}h`;
  const d = Math.floor(h / 24);
  if (d < 7) return `${d}d`;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function LoopRow({
  loop,
  isActive,
  onClick,
}: {
  loop: LoopData;
  isActive: boolean;
  onClick: () => void;
}) {
  const dotColor =
    loop.status === "enabled"
      ? "bg-success"
      : loop.status === "disabled"
      ? "bg-muted-foreground/40"
      : "bg-muted-foreground/30";
  const lastMeta = loop.last_run_at
    ? formatRelativeShort(loop.last_run_at)
    : loop.status === "disabled"
    ? "paused"
    : "—";

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "w-full rounded-md px-2.5 py-2 text-left transition-colors",
        isActive ? "bg-accent" : "hover:bg-muted",
      )}
    >
      <div className="flex items-center gap-2">
        <span className={cn("h-2 w-2 flex-shrink-0 rounded-full", dotColor)} />
        <div className="min-w-0 flex-1 space-y-0.5">
          <div className="flex items-center justify-between gap-2">
            <span
              className={cn(
                "truncate text-[13px] leading-none",
                isActive ? "font-semibold text-foreground" : "text-foreground",
              )}
            >
              {loop.name}
            </span>
            <span className="font-mono text-[10px] text-muted-foreground/80">{lastMeta}</span>
          </div>
          <div className="font-mono text-[11px] text-muted-foreground/80 truncate">{loop.slug}</div>
        </div>
      </div>
    </button>
  );
}

export function LoopListSidebar({ loops, selectedSlug, onSelect, onCreate }: LoopListSidebarProps) {
  const t = useTranslations();
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    if (!query) return loops;
    const q = query.toLowerCase();
    return loops.filter(
      (l) => l.name.toLowerCase().includes(q) || l.slug.toLowerCase().includes(q),
    );
  }, [loops, query]);

  const groups = useMemo(() => {
    const map: Record<Group, LoopData[]> = { enabled: [], disabled: [], archived: [] };
    for (const loop of filtered) map[groupOf(loop)].push(loop);
    return map;
  }, [filtered]);

  const sectionLabel: Record<Group, string> = {
    enabled: t("loops.groups.enabled"),
    disabled: t("loops.groups.disabled"),
    archived: t("loops.groups.archived"),
  };

  return (
    <div className="flex h-full w-full flex-col border-r border-border bg-muted/30">
      {/* Search + New Loop (per design search_area) */}
      <div className="flex flex-col gap-2 p-3">
        <div className="flex h-8 items-center gap-2 rounded-md border border-border bg-background px-2.5">
          <Search className="h-3.5 w-3.5 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("loops.searchPlaceholder")}
            className="flex-1 bg-transparent text-[13px] outline-none placeholder:text-muted-foreground"
          />
        </div>
        <button
          type="button"
          onClick={onCreate}
          className="flex h-[30px] items-center justify-center gap-1.5 rounded-md bg-primary text-[13px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover"
        >
          <Plus className="h-3.5 w-3.5" />
          {t("loops.createLoop")}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto pb-2">
        {(["enabled", "disabled", "archived"] as const).map((g) => {
          if (groups[g].length === 0) return null;
          return (
            <div key={g}>
              <div className="px-4 pb-1.5 pt-3 text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground/80">
                {sectionLabel[g]}
              </div>
              <ul className="space-y-0.5 px-2">
                {groups[g].map((loop) => (
                  <li key={loop.id}>
                    <LoopRow
                      loop={loop}
                      isActive={loop.slug === selectedSlug}
                      onClick={() => onSelect(loop.slug)}
                    />
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
        {filtered.length === 0 && (
          <div className="px-4 py-10 text-center text-[12px] text-muted-foreground">
            {query ? t("loops.noMatch") : t("loops.emptyTitle")}
          </div>
        )}
      </div>

      {/* Sort footer per design */}
      <div className="flex items-center gap-2 border-t border-border px-3 py-2.5 text-[12px] text-muted-foreground">
        <span>{t("loops.sortRecent")}</span>
        <div className="flex-1" />
        <button type="button" className="rounded px-1 text-base hover:bg-muted">
          ⋯
        </button>
      </div>
    </div>
  );
}
