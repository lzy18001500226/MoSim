"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import type { TicketCommit } from "@/lib/viewModels/ticket";
import { GitCommit } from "lucide-react";
import { cn } from "@/lib/utils";

interface CommitsListProps {
  commits: TicketCommit[];
  viewAllLink?: string;
  maxItems?: number;
  compact?: boolean;
  className?: string;
}

function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDay = Math.floor(diffMs / 86400000);

  if (diffDay > 30) {
    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  }
  if (diffDay > 0) return `${diffDay}d ago`;
  const diffHr = Math.floor(diffMs / 3600000);
  if (diffHr > 0) return `${diffHr}h ago`;
  return "just now";
}

export function CommitsList({
  commits,
  viewAllLink,
  maxItems = 5,
  compact = false,
  className,
}: CommitsListProps) {
  const t = useTranslations();

  if (commits.length === 0) return null;

  const displayCommits = compact ? commits.slice(0, maxItems) : commits;
  const hasMore = compact && commits.length > maxItems;

  if (compact) {
    return (
      <div className={cn("space-y-2", className)}>
        <label className="text-[11px] font-medium text-muted-foreground/70 uppercase tracking-wider flex items-center gap-1">
          <GitCommit className="h-3 w-3" />
          {t("tickets.detail.commits")}
        </label>
        <div className="space-y-1">
          {displayCommits.map((commit) => (
            <div key={commit.id} className="px-2.5 py-1.5 rounded-md hover:bg-muted/30 transition-colors">
              <div className="flex items-start gap-2">
                <code className="font-mono text-[10px] text-muted-foreground shrink-0">
                  {commit.commit_sha.substring(0, 7)}
                </code>
                <div className="flex-1 min-w-0">
                  <p className="truncate text-sm">{commit.commit_message}</p>
                  <p className="text-[11px] text-muted-foreground/70 mt-0.5">
                    {commit.author_name} · {commit.committed_at ? formatRelativeDate(commit.committed_at) : "N/A"}
                  </p>
                </div>
              </div>
            </div>
          ))}
          {hasMore && viewAllLink && (
            <Link
              href={viewAllLink}
              className="block text-xs text-primary hover:underline px-2.5 py-1"
            >
              {t("common.viewAll")} ({commits.length})
            </Link>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <p className="text-xs font-medium text-muted-foreground/70 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
        <GitCommit className="h-3.5 w-3.5" />
        {t("tickets.detail.commits")} ({commits.length})
      </p>
      <div className="rounded-xl border border-border/50 divide-y divide-border/40 overflow-hidden bg-card shadow-sm">
        {commits.map((commit) => (
          <div key={commit.id} className="px-3.5 py-2.5 hover:bg-muted/20 transition-colors">
            <div className="flex items-start gap-2.5">
              <code className="font-mono text-[11px] bg-muted/50 px-1.5 py-0.5 rounded text-muted-foreground/70 shrink-0">
                {commit.commit_sha.substring(0, 7)}
              </code>
              <div className="flex-1 min-w-0">
                <p className="text-sm truncate">{commit.commit_message}</p>
                <p className="text-xs text-muted-foreground/50 mt-0.5">
                  {commit.author_name} · {commit.committed_at ? formatRelativeDate(commit.committed_at) : "N/A"}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CommitsList;
