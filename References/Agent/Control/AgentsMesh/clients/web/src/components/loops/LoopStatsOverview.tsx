"use client";

import type { LoopData } from "@/stores/loop";
import { formatDuration } from "@/lib/utils/time";
import { cn } from "@/lib/utils";

interface LoopStatsOverviewProps {
  loop: LoopData;
  t: (key: string) => string;
}

const BREAKDOWN_ROWS: { key: "successful_runs" | "failed_runs" | "active_run_count"; labelKey: string; color: string }[] = [
  { key: "successful_runs", labelKey: "loops.statusCompleted", color: "bg-success" },
  { key: "active_run_count", labelKey: "loops.statusRunning", color: "bg-[#D29922]" },
  { key: "failed_runs", labelKey: "loops.statusFailed", color: "bg-destructive" },
];

export function LoopStatsOverview({ loop, t }: LoopStatsOverviewProps) {
  const successRate = loop.total_runs > 0
    ? Math.round((loop.successful_runs / loop.total_runs) * 100)
    : 0;
  const avg = loop.avg_duration_sec != null ? Math.round(loop.avg_duration_sec) : 0;

  return (
    <div className="rounded-md border border-border bg-card p-4">
      <h3 className="mb-3 text-[13px] font-semibold text-foreground">{t("loops.overviewTitle")}</h3>

      <div className="mb-3 flex items-start justify-between">
        <div className="flex flex-col gap-0.5">
          <span className="text-[11px] text-muted-foreground">{t("loops.totalRuns")}</span>
          <span className="text-[20px] font-semibold leading-tight text-foreground">{loop.total_runs}</span>
        </div>
        <div className="flex flex-col gap-0.5">
          <span className="text-[11px] text-muted-foreground">{t("loops.success")}</span>
          <span className="text-[20px] font-semibold leading-tight text-success">
            {loop.successful_runs}
            {loop.total_runs > 0 && <span className="ml-1 text-[13px] font-medium">· {successRate}%</span>}
          </span>
        </div>
        <div className="flex flex-col gap-0.5">
          <span className="text-[11px] text-muted-foreground">{t("loops.avgDuration")}</span>
          <span className="text-[20px] font-semibold leading-tight text-foreground">
            {avg > 0 ? formatDuration(avg) : "—"}
          </span>
        </div>
      </div>

      <div className="my-3 h-px bg-border" />

      <div className="flex flex-col gap-2">
        {BREAKDOWN_ROWS.map((row) => (
          <div key={row.key} className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <span className={cn("h-2 w-2 rounded-full", row.color)} />
              <span className="text-xs text-foreground">{t(row.labelKey)}</span>
            </div>
            <span className="font-mono text-xs text-muted-foreground">{loop[row.key] ?? 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
