import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  ArrowLeft,
  Play,
  Pencil,
  Loader2,
  MoreHorizontal,
  Power,
  Trash2,
} from "lucide-react";
import type { LoopData } from "@/stores/loop";

interface LoopHeaderProps {
  loop: LoopData;
  triggering: boolean;
  t: (key: string) => string;
  onBack?: () => void;
  onTrigger: () => void;
  onEdit: () => void;
  onEnable: () => void;
  onDisable: () => void;
  onDelete: () => void;
}

function formatNextRun(nextAt?: string): string | null {
  if (!nextAt) return null;
  const next = new Date(nextAt);
  const diffMs = next.getTime() - Date.now();
  if (diffMs <= 0) return null;
  const hours = Math.floor(diffMs / (60 * 60 * 1000));
  const minutes = Math.floor((diffMs % (60 * 60 * 1000)) / (60 * 1000));
  if (hours > 24) return `${Math.floor(hours / 24)}d ${hours % 24}h`;
  return `${hours}h ${minutes}m`;
}

export function LoopHeader({
  loop,
  triggering,
  t,
  onBack,
  onTrigger,
  onEdit,
  onEnable,
  onDisable,
  onDelete,
}: LoopHeaderProps) {
  const isEnabled = loop.status === "enabled";
  const isAutopilot = loop.execution_mode === "autopilot";
  const nextRun = formatNextRun(loop.next_run_at);

  return (
    <header className="mb-6 border-b border-border pb-5">
      {onBack && (
        <button
          className="mb-3 inline-flex items-center gap-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
          onClick={onBack}
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          {t("loops.back")}
        </button>
      )}

      <div className="flex items-start justify-between gap-6">
        {/* Left: status dot + title + chips + slug + meta row */}
        <div className="min-w-0 flex-1 space-y-2.5">
          <div className="flex flex-wrap items-center gap-2.5">
            <span
              className={cn(
                "h-2.5 w-2.5 flex-shrink-0 rounded-full",
                isEnabled ? "bg-success" : "bg-muted-foreground/40",
              )}
            />
            <h1 className="truncate text-[20px] font-semibold text-foreground">{loop.name}</h1>
            <span
              className={cn(
                "inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium",
                isEnabled
                  ? "bg-[color:var(--color-success)]/10 text-success"
                  : "bg-muted text-muted-foreground",
              )}
            >
              {isEnabled ? t("loops.statusEnabled") : t("loops.statusDisabled")}
            </span>
            {isAutopilot && (
              <span className="inline-flex items-center rounded-full bg-accent px-2.5 py-0.5 text-[11px] font-medium text-accent-foreground">
                {t("loops.autopilot")}
              </span>
            )}
          </div>

          <div className="font-mono text-xs text-muted-foreground">{loop.slug}</div>

          {/* Meta row */}
          <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs">
            {loop.cron_expression && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">{t("loops.schedule")}</span>
                <span className="font-medium text-foreground">{loop.cron_expression}</span>
              </div>
            )}
            {nextRun && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">{t("loops.next")}</span>
                <span className="font-medium text-foreground">in {nextRun}</span>
              </div>
            )}
            {loop.agent_slug && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">{t("loops.agent")}</span>
                <span className="font-mono font-medium text-foreground">{loop.agent_slug}</span>
              </div>
            )}
            {loop.description && (
              <span className="truncate text-muted-foreground">{loop.description}</span>
            )}
          </div>
        </div>

        {/* Right: big Run now CTA + secondary actions */}
        <div className="flex w-[240px] shrink-0 flex-col items-end gap-2">
          <Button
            onClick={onTrigger}
            disabled={!isEnabled || triggering || loop.active_run_count >= loop.max_concurrent_runs}
            className="h-10 w-full gap-2 text-sm font-semibold shadow-sm"
          >
            {triggering ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            {t("loops.runNow")}
          </Button>
          <div className="flex items-center gap-1.5">
            {isEnabled ? (
              <Button variant="outline" size="sm" onClick={onDisable} className="h-7 px-3 text-xs gap-1">
                <Power className="h-3 w-3" />
                {t("loops.disable")}
              </Button>
            ) : (
              <Button variant="outline" size="sm" onClick={onEnable} className="h-7 px-3 text-xs gap-1">
                <Power className="h-3 w-3" />
                {t("loops.enable")}
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={onEdit} className="h-7 px-3 text-xs gap-1">
              <Pencil className="h-3 w-3" />
              {t("common.edit")}
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon" className="h-7 w-7">
                  <MoreHorizontal className="h-3.5 w-3.5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={onDelete}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  {t("common.delete")}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  );
}
