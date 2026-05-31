"use client";

import { useState, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useTranslations } from "next-intl";
import {
  getRepositoryWebhookStatus,
  registerRepositoryWebhook,
  deleteRepositoryWebhook,
  markRepositoryWebhookConfigured,
  getRepositoryWebhookSecret,
} from "@/lib/api/connect/repositoryConnect";
import { useCurrentOrg } from "@/stores/auth";
import type { WebhookStatus, RepositoryData } from "@/lib/viewModels/repository";
import { cn } from "@/lib/utils";
import { getLocalizedErrorMessage } from "@/lib/api/errors";
import { toast } from "sonner";
import { RefreshCw, Loader2 } from "lucide-react";
import {
  WebhookStatusDisplay,
  WebhookActiveInfo,
  WebhookManualSetup,
  WebhookActions,
  type WebhookSecretInfo,
  type WebhookActionType,
  type CopiedField,
} from "./webhook";

interface WebhookSettingsCardProps {
  repository: RepositoryData;
  onStatusChange?: () => void;
}

export function WebhookSettingsCard({
  repository,
  onStatusChange,
}: WebhookSettingsCardProps) {
  const t = useTranslations();
  const currentOrg = useCurrentOrg();
  const orgSlug = currentOrg?.slug ?? "";
  const [status, setStatus] = useState<WebhookStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<WebhookActionType>(null);
  const [error, setError] = useState<string | null>(null);
  const [secretInfo, setSecretInfo] = useState<WebhookSecretInfo | null>(null);
  const [showSecret, setShowSecret] = useState(false);
  const [copied, setCopied] = useState<CopiedField>(null);

  const loadStatus = useCallback(async () => {
    if (!orgSlug) return;
    try {
      setLoading(true);
      setError(null);
      const res = await getRepositoryWebhookStatus(orgSlug, repository.id);
      setStatus(res);
    } catch (err) {
      const msg = getLocalizedErrorMessage(err, t, t("repositories.webhook.retry"));
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }, [repository.id, t, orgSlug]);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  const handleRegister = useCallback(async () => {
    if (!orgSlug) return;
    try {
      setActionLoading("register");
      setError(null);
      await registerRepositoryWebhook(orgSlug, repository.id);
      await loadStatus();
      onStatusChange?.();
    } catch (err) {
      const msg = getLocalizedErrorMessage(err, t, t("repositories.detail.webhookFailed"));
      setError(msg);
      toast.error(msg);
    } finally {
      setActionLoading(null);
    }
  }, [repository.id, loadStatus, onStatusChange, t, orgSlug]);

  const handleDelete = useCallback(async () => {
    if (!orgSlug) return;
    try {
      setActionLoading("delete");
      setError(null);
      await deleteRepositoryWebhook(orgSlug, repository.id);
      setSecretInfo(null);
      setShowSecret(false);
      await loadStatus();
      onStatusChange?.();
    } catch (err) {
      const msg = getLocalizedErrorMessage(err, t, t("repositories.detail.webhookFailed"));
      setError(msg);
      toast.error(msg);
    } finally {
      setActionLoading(null);
    }
  }, [repository.id, loadStatus, onStatusChange, t, orgSlug]);

  const handleMarkConfigured = useCallback(async () => {
    if (!orgSlug) return;
    try {
      setActionLoading("markConfigured");
      setError(null);
      await markRepositoryWebhookConfigured(orgSlug, repository.id);
      setShowSecret(false);
      await loadStatus();
      onStatusChange?.();
    } catch (err) {
      const msg = getLocalizedErrorMessage(err, t, t("repositories.detail.webhookFailed"));
      setError(msg);
      toast.error(msg);
    } finally {
      setActionLoading(null);
    }
  }, [repository.id, loadStatus, onStatusChange, t, orgSlug]);

  const handleGetSecret = useCallback(async () => {
    if (!orgSlug) return;
    try {
      setActionLoading("getSecret");
      setError(null);
      const res = await getRepositoryWebhookSecret(orgSlug, repository.id);
      setSecretInfo({
        url: res.webhook_url,
        secret: res.webhook_secret,
        events: res.events,
      });
      setShowSecret(true);
    } catch (err) {
      const msg = getLocalizedErrorMessage(err, t, t("repositories.detail.webhookFailed"));
      setError(msg);
      toast.error(msg);
    } finally {
      setActionLoading(null);
    }
  }, [repository.id, t, orgSlug]);

  const handleCopy = useCallback(
    async (text: string, type: "url" | "secret") => {
      try {
        await navigator.clipboard.writeText(text);
        setCopied(type);
        setTimeout(() => setCopied(null), 2000);
      } catch {
      }
    },
    []
  );

  if (loading) {
    return (
      <div className="border border-border rounded-lg p-6 md:col-span-2">
        <h3 className="font-semibold mb-4">{t("repositories.webhook.title")}</h3>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-5 h-5 animate-spin mr-2" />
          <span className="text-muted-foreground text-sm">
            {t("repositories.webhook.loading")}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="border border-border rounded-lg p-6 md:col-span-2">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">{t("repositories.webhook.title")}</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={loadStatus}
          disabled={!!actionLoading}
        >
          <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
        </Button>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive text-sm px-3 py-2 rounded mb-4">
          {error}
        </div>
      )}

      {/* Status display */}
      <WebhookStatusDisplay status={status} t={t} />

      {/* Active webhook info */}
      {status && <WebhookActiveInfo status={status} t={t} />}

      {/* Manual setup instructions */}
      {status?.needs_manual_setup && (
        <WebhookManualSetup
          repository={repository}
          secretInfo={secretInfo}
          showSecret={showSecret}
          copied={copied}
          actionLoading={actionLoading}
          onGetSecret={handleGetSecret}
          onCopy={handleCopy}
          t={t}
        />
      )}

      {/* Not registered state */}
      {!status?.registered && !status?.needs_manual_setup && (
        <div className="text-sm text-muted-foreground mb-4">
          {t("repositories.webhook.notRegisteredDescription")}
        </div>
      )}

      {/* Action buttons */}
      <WebhookActions
        status={status}
        actionLoading={actionLoading}
        onRegister={handleRegister}
        onDelete={handleDelete}
        onMarkConfigured={handleMarkConfigured}
        t={t}
      />
    </div>
  );
}

export default WebhookSettingsCard;
