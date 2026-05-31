"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Runner, getRunnerStatusInfo } from "@/stores/runner";
import { isVersionOutdated } from "@/lib/utils/version";
import { getLocalRunnerService } from "@agentsmesh/service-runtime";
import type { TranslationFn } from "../GeneralSettings";

interface RunnerCardProps {
  runner: Runner;
  onEdit: (runner: Runner) => void;
  onDelete: () => void;
  formatLastSeen: (dateString?: string) => string;
  t: TranslationFn;
  latestRunnerVersion?: string;
}

function useLocalNodeId(): string | null {
  const [nodeId, setNodeId] = useState<string | null>(null);
  useEffect(() => {
    const svc = getLocalRunnerService();
    if (!svc) return;
    let cancelled = false;
    void svc.local_node_id().then((id: string | null) => {
      if (!cancelled) setNodeId(id);
    });
    return () => {
      cancelled = true;
    };
  }, []);
  return nodeId;
}

export function RunnerCard({
  runner,
  onEdit,
  onDelete,
  formatLastSeen,
  t,
  latestRunnerVersion,
}: RunnerCardProps) {
  const statusInfo = getRunnerStatusInfo(runner.status as "online" | "offline" | "maintenance" | "busy");
  const localNodeId = useLocalNodeId();
  const isThisMachine = localNodeId !== null && localNodeId === runner.node_id;

  return (
    <div
      className={`p-4 border rounded-lg ${
        runner.is_enabled ? "border-border" : "border-border bg-muted/50"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-medium">{runner.node_id}</span>
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${statusInfo?.color}`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${statusInfo?.dotColor}`} />
              {statusInfo?.label}
            </span>
            {isThisMachine && (
              <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                This Mac
              </span>
            )}
            {!runner.is_enabled && (
              <span className="text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 px-2 py-0.5 rounded">
                {t("settings.runnersSection.disabled")}
              </span>
            )}
          </div>
          {runner.description && (
            <p className="text-sm text-muted-foreground mt-1">
              {runner.description}
            </p>
          )}
          <div className="flex items-center gap-4 text-sm text-muted-foreground mt-2">
            <span>
              {t("settings.runnersSection.pods")} {runner.current_pods} / {runner.max_concurrent_pods}
            </span>
            {runner.runner_version && (
              <span className="flex items-center gap-1">
                v{runner.runner_version}
                {isVersionOutdated(runner.runner_version, latestRunnerVersion) && (
                  <span className="px-1.5 py-0.5 text-[10px] font-medium rounded bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
                    {t("settings.runnersSection.upgradeAvailable")}
                  </span>
                )}
              </span>
            )}
            <span>{t("settings.runnersSection.lastSeen")} {formatLastSeen(runner.last_heartbeat)}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => onEdit(runner)}>
            {t("settings.runnersSection.edit")}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-destructive hover:text-destructive"
            onClick={onDelete}
          >
            {t("settings.runnersSection.delete")}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default RunnerCard;
