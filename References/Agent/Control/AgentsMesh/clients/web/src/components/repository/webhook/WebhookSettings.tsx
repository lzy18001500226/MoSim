"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { RefreshCw } from "lucide-react";
import type { RepositoryData } from "@/lib/viewModels/repository";
import { useWebhookState } from "./useWebhookState";
import { WebhookStatusBadge } from "./WebhookStatusBadge";
import { WebhookRegisteredView } from "./WebhookRegisteredView";
import { WebhookManualSetupForm } from "./WebhookManualSetupForm";
import { WebhookNotRegisteredView } from "./WebhookNotRegisteredView";
import { WebhookErrorView } from "./WebhookErrorView";

export interface WebhookSettingsProps {
  repository: RepositoryData;
  onUpdate?: () => void;
}

export function WebhookSettings({ repository, onUpdate }: WebhookSettingsProps) {
  const t = useTranslations("repositories.webhook");
  const {
    state,
    status,
    secretData,
    error,
    loading,
    handleRegister,
    handleDelete,
    handleMarkConfigured,
    loadStatus,
  } = useWebhookState(repository.id, onUpdate);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  if (state === "loading") {
    return (
      <div className="p-4 border border-border rounded-lg">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span className="text-sm text-muted-foreground">{t("loading")}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 border border-border rounded-lg space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium">{t("title")}</h3>
        <WebhookStatusBadge state={state} />
      </div>

      {error && (
        <div className="p-3 bg-destructive/10 text-destructive text-sm rounded">
          {error}
        </div>
      )}

      {state === "registered" && status && (
        <WebhookRegisteredView
          status={status}
          loading={loading}
          onReregister={handleRegister}
          onDelete={handleDelete}
        />
      )}

      {state === "needs_manual_setup" && secretData && (
        <WebhookManualSetupForm
          secretData={secretData}
          loading={loading}
          onMarkConfigured={handleMarkConfigured}
          onRetry={handleRegister}
        />
      )}

      {state === "not_registered" && (
        <WebhookNotRegisteredView
          loading={loading}
          onRegister={handleRegister}
        />
      )}

      {state === "error" && (
        <WebhookErrorView
          loading={loading}
          onRetry={loadStatus}
        />
      )}
    </div>
  );
}

export default WebhookSettings;
