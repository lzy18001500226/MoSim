"use client";

import type { LoopRunData, RunStatus } from "@/stores/loop";
import { formatDuration, formatTimeAgo } from "@/lib/utils/time";
import { cn } from "@/lib/utils";

interface LoopRunCardProps {
  run: LoopRunData;
  t: (key: string, values?: Record<string, string | number>) => string;
  onOpen?: (run: LoopRunData) => void;
  onCancel?: (runId: number) => void;
}

const RUN_DOT: Record<RunStatus, string> = {
  completed: "bg-success",
  running: "bg-[#0969DA]",
  pending: "bg-[#D29922]",
  timeout: "bg-[#D29922]",
  failed: "bg-destructive",
  cancelled: "bg-muted-foreground",
  skipped: "bg-muted-foreground/60",
};

const RUN_TONE: Record<RunStatus, { wrap: string; title: string; sub: string }> = {
  completed: {
    wrap: "bg-card border-border",
    title: "text-foreground",
    sub: "text-muted-foreground",
  },
  running: {
    wrap: "bg-[#DDF4FF]/40 border-[#0969DA]/40",
    title: "text-[#0550AE]",
    sub: "text-[#0550AE]",
  },
  pending: {
    wrap: "bg-[#FFFBEB] border-[#D29922]/50",
    title: "text-[#9A6700]",
    sub: "text-[#9A6700]",
  },
  timeout: {
    wrap: "bg-[#FFFBEB] border-[#D29922]/50",
    title: "text-[#9A6700]",
    sub: "text-[#9A6700]",
  },
  failed: {
    wrap: "bg-card border-destructive/40",
    title: "text-destructive",
    sub: "text-muted-foreground",
  },
  cancelled: {
    wrap: "bg-card border-border",
    title: "text-foreground",
    sub: "text-muted-foreground",
  },
  skipped: {
    wrap: "bg-card border-border",
    title: "text-muted-foreground",
    sub: "text-muted-foreground",
  },
};

function triggerLabel(t: LoopRunCardProps["t"], type: string) {
  switch (type) {
    case "cron":
      return t("loops.triggerTypeCron");
    case "api":
      return t("loops.triggerTypeApi");
    default:
      return t("loops.triggerTypeManual");
  }
}

export function LoopRunCard({ run, t, onOpen, onCancel }: LoopRunCardProps) {
  const tone = RUN_TONE[run.status] ?? RUN_TONE.completed;
  const statusKey = `loops.status${run.status.charAt(0).toUpperCase()}${run.status.slice(1)}`;
  const isRunning = run.status === "running" || run.status === "pending";
  const started = run.started_at ? formatTimeAgo(run.started_at, t) : "—";
  const duration = run.duration_sec ? formatDuration(run.duration_sec) : null;

  const summaryParts = [
    started,
    duration ?? undefined,
    triggerLabel(t, run.trigger_type),
  ].filter(Boolean) as string[];

  return (
    <div className={cn("flex items-center gap-3 rounded-md border p-3", tone.wrap)}>
      <span className={cn("h-2 w-2 flex-shrink-0 rounded-full", RUN_DOT[run.status] ?? "bg-muted-foreground")} />

      <div className="min-w-0 flex-1">
        <div className={cn("text-[13px] font-medium", tone.title)}>
          #{run.run_number} · {t(statusKey)}
        </div>
        <div className={cn("truncate text-[11px]", tone.sub)}>{summaryParts.join(" · ")}</div>
      </div>

      <div className="hidden min-w-0 shrink-0 flex-col gap-0.5 md:flex md:w-[180px]">
        {run.pod_key ? (
          <>
            <span className="truncate font-mono text-xs text-foreground">{run.pod_key}</span>
            <span className="truncate font-mono text-[11px] text-muted-foreground">
              {run.autopilot_controller_key ? "autopilot" : "pod"}
            </span>
          </>
        ) : (
          <span className="font-mono text-xs text-muted-foreground">—</span>
        )}
      </div>

      <div className="hidden min-w-0 shrink-0 flex-col gap-0.5 lg:flex lg:w-[220px]">
        <span className="truncate text-xs text-foreground">
          {run.exit_summary || run.error_message || t("loops.noArtifact")}
        </span>
        {run.resolved_prompt && (
          <span className="truncate font-mono text-[11px] text-muted-foreground">
            {run.resolved_prompt.split("\n")[0].slice(0, 42)}
          </span>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-2">
        {isRunning && onCancel && (
          <button
            type="button"
            onClick={() => onCancel(run.id)}
            className="rounded-md border border-border px-2 py-1 text-xs text-destructive hover:bg-destructive/10"
          >
            {t("common.cancel")}
          </button>
        )}
        {onOpen && (
          <button
            type="button"
            onClick={() => onOpen(run)}
            className="text-xs font-medium text-primary hover:underline"
          >
            {run.pod_key ? t("loops.openRun") : t("loops.viewLogs")} →
          </button>
        )}
      </div>
    </div>
  );
}
