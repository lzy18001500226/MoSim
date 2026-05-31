"use client";

import { useTranslations } from "next-intl";
import type { TicketRelation } from "@/lib/viewModels/ticket";
import { ChevronRight, Link2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface RelationsListProps {
  relations: TicketRelation[];
  onTicketClick: (slug: string) => void;
  compact?: boolean;
  className?: string;
}

export function RelationsList({
  relations,
  onTicketClick,
  compact = false,
  className,
}: RelationsListProps) {
  const t = useTranslations();

  if (relations.length === 0) return null;

  if (compact) {
    return (
      <div className={cn("space-y-2", className)}>
        <label className="text-[11px] font-medium text-muted-foreground/70 uppercase tracking-wider flex items-center gap-1">
          <Link2 className="h-3 w-3" />
          {t("tickets.detail.related")}
        </label>
        <div className="space-y-1">
          {relations.map((relation) => {
            const targetTicket = relation.target_ticket;
            if (!targetTicket) return null;
            return (
              <button
                key={relation.id}
                className="w-full px-2.5 py-1.5 flex items-center gap-2 hover:bg-muted/50 rounded-md transition-colors text-left group"
                onClick={() => onTicketClick(targetTicket.slug)}
              >
                <span className="text-[10px] text-muted-foreground capitalize bg-muted/70 px-1.5 py-0.5 rounded">
                  {relation.relation_type}
                </span>
                <span className="font-mono text-xs text-muted-foreground">
                  {targetTicket.slug}
                </span>
                <span className="flex-1 truncate text-sm">{targetTicket.title}</span>
                <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/50 opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <p className="text-xs font-medium text-muted-foreground/70 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
        <Link2 className="h-3.5 w-3.5" />
        {t("tickets.detail.related")} ({relations.length})
      </p>
      <div className="rounded-xl border border-border/50 divide-y divide-border/40 overflow-hidden bg-card shadow-sm">
        {relations.map((relation) => {
          const targetTicket = relation.target_ticket;
          if (!targetTicket) return null;
          return (
            <button
              key={relation.id}
              type="button"
              className="w-full text-left px-3.5 py-2.5 hover:bg-muted/30 transition-colors flex items-center gap-2.5 group"
              onClick={() => onTicketClick(targetTicket.slug)}
            >
              <span className="text-[10px] text-muted-foreground/70 capitalize bg-muted/60 px-1.5 py-0.5 rounded shrink-0">
                {relation.relation_type}
              </span>
              <code className="font-mono text-[11px] text-muted-foreground/60">
                {targetTicket.slug}
              </code>
              <span className="flex-1 truncate text-sm">{targetTicket.title}</span>
              <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/30 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default RelationsList;
