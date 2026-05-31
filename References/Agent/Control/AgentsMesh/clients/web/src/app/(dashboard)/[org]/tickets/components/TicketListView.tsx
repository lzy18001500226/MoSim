"use client";

import { useTicketPrefetch } from "@/hooks/useTicketPrefetch";
import type { Ticket } from "@/stores/ticket";
import { StatusIcon, PriorityIcon, getStatusDisplayInfo } from "@/components/tickets";
import { cn } from "@/lib/utils";

interface TicketListViewProps {
  tickets: Ticket[];
  selectedSlug: string | null;
  onTicketClick: (ticket: Ticket) => void;
  t: (key: string) => string;
}

function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffDay > 30) return date.toLocaleDateString();
  if (diffDay > 0) return `${diffDay}d ago`;
  if (diffHr > 0) return `${diffHr}h ago`;
  if (diffMin > 0) return `${diffMin}m ago`;
  return "just now";
}

export function TicketListView({ tickets, selectedSlug, onTicketClick, t }: TicketListViewProps) {
  const { prefetchOnHover, cancelPrefetch } = useTicketPrefetch();

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <div className="overflow-auto max-h-full">
        <table className="w-full">
          <thead className="bg-muted/50 sticky top-0 z-10">
            <tr>
              <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide w-40">
                {t("tickets.listView.id")}
              </th>
              <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                {t("tickets.listView.titleColumn")}
              </th>
              <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide w-32">
                {t("tickets.listView.status")}
              </th>
              <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide w-28">
                {t("tickets.listView.priority")}
              </th>
              <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide w-28">
                {t("tickets.detail.assignees")}
              </th>
              <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide w-24">
                {t("tickets.listView.created")}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {tickets.map((ticket) => {
              const isSelected = ticket.slug === selectedSlug;
              const statusInfo = getStatusDisplayInfo(ticket.status);
              return (
                <tr
                  key={ticket.id}
                  className={cn(
                    "cursor-pointer transition-all duration-150",
                    isSelected
                      ? "bg-primary/10 hover:bg-primary/15"
                      : "hover:bg-muted/50"
                  )}
                  onClick={() => onTicketClick(ticket)}
                  onMouseEnter={() => prefetchOnHover(ticket.slug)}
                  onMouseLeave={cancelPrefetch}
                >
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <code className={cn(
                        "text-sm font-mono",
                        isSelected ? "text-primary font-medium" : "text-primary"
                      )}>
                        {ticket.slug}
                      </code>
                    </div>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="text-sm text-foreground line-clamp-1">
                      {ticket.title}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className={cn(
                        "inline-flex items-center gap-1.5 px-2 py-0.5 text-xs rounded-full font-medium",
                        statusInfo.bgColor,
                        statusInfo.color
                      )}
                    >
                      <StatusIcon status={ticket.status} size="xs" />
                      {t(`tickets.status.${ticket.status}`)}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-1.5">
                      <PriorityIcon priority={ticket.priority} size="sm" />
                      <span className="text-sm text-muted-foreground">
                        {t(`tickets.priority.${ticket.priority}`)}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex -space-x-1.5">
                      {ticket.assignees?.slice(0, 3).map((assignee) => (
                        <div
                          key={assignee.user_id}
                          className="w-6 h-6 rounded-full border-2 border-background overflow-hidden"
                          title={assignee.user?.name || assignee.user?.username}
                        >
                          {assignee.user?.avatar_url ? (
                            /* eslint-disable-next-line @next/next/no-img-element */
                            <img
                              src={assignee.user.avatar_url}
                              alt={assignee.user?.username}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full bg-primary/10 flex items-center justify-center text-[10px] font-medium text-primary">
                              {(assignee.user?.name || assignee.user?.username || "?")[0].toUpperCase()}
                            </div>
                          )}
                        </div>
                      ))}
                      {ticket.assignees && ticket.assignees.length > 3 && (
                        <div className="w-6 h-6 rounded-full border-2 border-background bg-muted flex items-center justify-center text-[10px]">
                          +{ticket.assignees.length - 3}
                        </div>
                      )}
                      {(!ticket.assignees || ticket.assignees.length === 0) && (
                        <span className="text-xs text-muted-foreground/50">—</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className="text-sm text-muted-foreground"
                      title={ticket.created_at ? new Date(ticket.created_at).toLocaleString() : undefined}
                    >
                      {ticket.created_at ? formatRelativeDate(ticket.created_at) : "—"}
                    </span>
                  </td>
                </tr>
              );
            })}
            {tickets.length === 0 && (
              <tr>
                <td
                  colSpan={6}
                  className="px-4 py-8 text-center text-muted-foreground"
                >
                  {t("tickets.listView.noTickets")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
