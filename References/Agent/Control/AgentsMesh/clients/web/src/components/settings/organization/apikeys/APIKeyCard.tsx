"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Key, Pencil, Ban } from "lucide-react";
import type { ApiKey } from "@/lib/api/facade/apikey";
import type { TranslationFn } from "../GeneralSettings";

interface APIKeyCardProps {
  apiKey: ApiKey;
  onEdit: (apiKey: ApiKey) => void;
  onRevoke: (id: bigint) => void;
  t: TranslationFn;
}

function formatRelativeTime(dateString?: string, t?: TranslationFn): string {
  if (!dateString) return t?.("settings.apiKeys.neverUsed") || "Never used";
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);

  if (diffSec < 60) return t?.("settings.apiKeys.justNow") || "just now";
  if (diffSec < 3600) {
    const count = Math.floor(diffSec / 60);
    return t?.("settings.apiKeys.minutesAgo", { count }) || `${count}m ago`;
  }
  if (diffSec < 86400) {
    const count = Math.floor(diffSec / 3600);
    return t?.("settings.apiKeys.hoursAgo", { count }) || `${count}h ago`;
  }
  const count = Math.floor(diffSec / 86400);
  return t?.("settings.apiKeys.daysAgo", { count }) || `${count}d ago`;
}

export function APIKeyCard({ apiKey, onEdit, onRevoke, t }: APIKeyCardProps) {
  const isExpired = apiKey.expiresAt && new Date(apiKey.expiresAt) < new Date();
  const isActive = apiKey.isEnabled && !isExpired;

  return (
    <div className="flex items-center justify-between p-4 border border-border rounded-lg">
      <div className="flex items-start gap-3 min-w-0 flex-1">
        <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center flex-shrink-0 mt-0.5">
          <Key className="w-4 h-4 text-muted-foreground" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium truncate">{apiKey.name}</span>
            <code className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
              {apiKey.keyPrefix}...
            </code>
            {isActive ? (
              <Badge variant="default" className="text-xs">
                {t("settings.apiKeys.enabled")}
              </Badge>
            ) : (
              <Badge variant="secondary" className="text-xs">
                {apiKey.isEnabled
                  ? t("settings.apiKeys.expired")
                  : t("settings.apiKeys.disabled")}
              </Badge>
            )}
          </div>

          <div className="flex flex-wrap gap-1 mb-1.5">
            {apiKey.scopes.map((scope) => (
              <span
                key={scope}
                className="text-xs bg-muted text-muted-foreground px-1.5 py-0.5 rounded"
              >
                {scope}
              </span>
            ))}
          </div>

          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span>
              {t("settings.apiKeys.lastUsed", {
                time: formatRelativeTime(apiKey.lastUsedAt, t),
              })}
            </span>
            <span>·</span>
            <span>
              {apiKey.expiresAt
                ? t("settings.apiKeys.expiresAt", {
                    date: new Date(apiKey.expiresAt).toLocaleDateString(),
                  })
                : t("settings.apiKeys.neverExpires")}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1 ml-2 flex-shrink-0">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(apiKey)}
          aria-label={t("settings.apiKeys.editDialog.title")}
        >
          <Pencil className="w-4 h-4" />
        </Button>
        {apiKey.isEnabled && (
          <Button
            variant="ghost"
            size="sm"
            className="text-destructive hover:text-destructive"
            onClick={() => onRevoke(apiKey.id)}
            aria-label={t("settings.apiKeys.revokeDialog.title")}
          >
            <Ban className="w-4 h-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
