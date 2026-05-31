"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

/**
 * LoopScheduleSection — the "loop-only" half of the create dialog.
 *
 * Covers cron scheduling, execution mode, sandbox strategy, concurrency
 * policy, timeout, retention, session persistence and the webhook URL.
 * Pure stateless presentation: parent owns state and passes setters.
 */
interface LoopScheduleSectionProps {
  cronEnabled: boolean;
  onCronEnabledChange: (v: boolean) => void;
  cronExpression: string;
  onCronExpressionChange: (v: string) => void;

  executionMode: string;
  onExecutionModeChange: (v: string) => void;

  sandboxStrategy: string;
  onSandboxStrategyChange: (v: string) => void;

  concurrencyPolicy: string;
  onConcurrencyPolicyChange: (v: string) => void;

  timeoutMinutes: number;
  onTimeoutMinutesChange: (v: number) => void;

  maxConcurrentRuns: number;
  onMaxConcurrentRunsChange: (v: number) => void;

  maxRetainedRuns: number;
  onMaxRetainedRunsChange: (v: number) => void;

  sessionPersistence: boolean;
  onSessionPersistenceChange: (v: boolean) => void;

  callbackUrl: string;
  onCallbackUrlChange: (v: string) => void;

  t: (key: string) => string;
}

export function LoopScheduleSection({
  cronEnabled,
  onCronEnabledChange,
  cronExpression,
  onCronExpressionChange,
  executionMode,
  onExecutionModeChange,
  sandboxStrategy,
  onSandboxStrategyChange,
  concurrencyPolicy,
  onConcurrencyPolicyChange,
  timeoutMinutes,
  onTimeoutMinutesChange,
  maxConcurrentRuns,
  onMaxConcurrentRunsChange,
  maxRetainedRuns,
  onMaxRetainedRunsChange,
  sessionPersistence,
  onSessionPersistenceChange,
  callbackUrl,
  onCallbackUrlChange,
  t,
}: LoopScheduleSectionProps) {
  return (
    <div className="border-t border-border pt-4 space-y-4">
      {/* Cron scheduling (optional, API trigger is always available) */}
      <div className="flex items-center justify-between">
        <div>
          <Label>{t("loops.enableCron")}</Label>
          <p className="text-xs text-muted-foreground">{t("loops.apiAlwaysAvailable")}</p>
        </div>
        <Switch checked={cronEnabled} onCheckedChange={onCronEnabledChange} />
      </div>

      {cronEnabled && (
        <div className="space-y-1.5">
          <Label>{t("loops.cronExpression")}</Label>
          <Input
            value={cronExpression}
            onChange={(e) => onCronExpressionChange(e.target.value)}
            placeholder="0 9 * * *"
            className="font-mono"
          />
          <p className="text-xs text-muted-foreground">{t("loops.cronHelp")}</p>
        </div>
      )}

      {/* Execution Mode */}
      <div className="space-y-1.5">
        <Label>{t("loops.executionMode")}</Label>
        <Select value={executionMode} onValueChange={onExecutionModeChange}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="autopilot">{t("loops.modeAutopilot")}</SelectItem>
            <SelectItem value="direct">{t("loops.modeDirect")}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Sandbox & Concurrency */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <Label>{t("loops.sandboxStrategy")}</Label>
          <Select value={sandboxStrategy} onValueChange={onSandboxStrategyChange}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="persistent">{t("loops.sandboxPersistent")}</SelectItem>
              <SelectItem value="fresh">{t("loops.sandboxFresh")}</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-1.5">
          <Label>{t("loops.concurrency")}</Label>
          <Select value={concurrencyPolicy} onValueChange={onConcurrencyPolicyChange}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="skip">{t("loops.policySkip")}</SelectItem>
              <SelectItem value="queue" disabled>
                {t("loops.policyQueue")} ({t("loops.comingSoon")})
              </SelectItem>
              <SelectItem value="replace" disabled>
                {t("loops.policyReplace")} ({t("loops.comingSoon")})
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Timeout & Max Concurrent */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <Label>{t("loops.timeout")}</Label>
          <div className="flex items-center gap-2">
            <Input
              type="number"
              min={1}
              max={1440}
              value={timeoutMinutes}
              onChange={(e) =>
                onTimeoutMinutesChange(Math.max(1, parseInt(e.target.value) || 60))
              }
              className="w-24"
            />
            <span className="text-sm text-muted-foreground">{t("loops.minutes")}</span>
          </div>
        </div>
        <div className="space-y-1.5">
          <Label>{t("loops.maxConcurrentRuns")}</Label>
          <Input
            type="number"
            min={1}
            max={10}
            value={maxConcurrentRuns}
            onChange={(e) => onMaxConcurrentRunsChange(parseInt(e.target.value) || 1)}
            className="w-24"
          />
        </div>
      </div>

      {/* Run History Limit */}
      <div className="space-y-1.5">
        <Label>{t("loops.maxRetainedRuns")}</Label>
        <div className="flex items-center gap-2">
          <Input
            type="number"
            min={0}
            max={10000}
            value={maxRetainedRuns}
            onChange={(e) =>
              onMaxRetainedRunsChange(Math.max(0, parseInt(e.target.value) || 0))
            }
            className="w-24"
          />
          <span className="text-sm text-muted-foreground">
            {maxRetainedRuns === 0 ? t("loops.unlimited") : ""}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">{t("loops.maxRetainedRunsHelp")}</p>
      </div>

      {/* Session Persistence */}
      {sandboxStrategy === "persistent" && (
        <div className="flex items-center justify-between">
          <div>
            <Label>{t("loops.sessionPersistence")}</Label>
            <p className="text-xs text-muted-foreground">{t("loops.sessionPersistenceHelp")}</p>
          </div>
          <Switch checked={sessionPersistence} onCheckedChange={onSessionPersistenceChange} />
        </div>
      )}

      {/* Webhook URL */}
      <div className="space-y-1.5">
        <Label>{t("loops.callbackUrl")}</Label>
        <Input
          type="url"
          value={callbackUrl}
          onChange={(e) => onCallbackUrlChange(e.target.value)}
          placeholder={t("loops.callbackUrlPlaceholder")}
        />
        <p className="text-xs text-muted-foreground">{t("loops.callbackUrlHelp")}</p>
      </div>
    </div>
  );
}
