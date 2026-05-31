"use client";

import { Badge } from "@/components/ui/badge";
import { useTranslations } from "next-intl";

const statusVariants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  open: "destructive",
  in_progress: "default",
  resolved: "secondary",
  closed: "outline",
};

export function TicketStatusBadge({ status }: { status: string }) {
  const t = useTranslations();
  const variant = statusVariants[status] || "outline";
  const label = t(`support.status.${status}` as Parameters<typeof t>[0]);
  return <Badge variant={variant}>{label}</Badge>;
}

export function TicketCategoryBadge({ category }: { category: string }) {
  const t = useTranslations();
  const label = t(`support.category.${category}` as Parameters<typeof t>[0]);
  return <Badge variant="outline">{label}</Badge>;
}

const priorityVariants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  low: "secondary",
  medium: "default",
  high: "destructive",
};

export function TicketPriorityBadge({ priority }: { priority: string }) {
  const t = useTranslations();
  const variant = priorityVariants[priority] || "outline";
  const label = t(`support.priority.${priority}` as Parameters<typeof t>[0]);
  return <Badge variant={variant}>{label}</Badge>;
}
