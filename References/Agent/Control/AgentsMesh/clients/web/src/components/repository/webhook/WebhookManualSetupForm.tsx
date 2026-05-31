"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Copy, Check, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { WebhookSecretResponse } from "@/lib/viewModels/repository";

interface WebhookManualSetupFormProps {
  secretData: WebhookSecretResponse;
  loading: boolean;
  onMarkConfigured: () => Promise<void>;
  onRetry: () => Promise<void>;
}

export function WebhookManualSetupForm({
  secretData,
  loading,
  onMarkConfigured,
  onRetry,
}: WebhookManualSetupFormProps) {
  const t = useTranslations("repositories.webhook");
  const [copied, setCopied] = useState<"url" | "secret" | null>(null);

  const copyToClipboard = async (text: string, type: "url" | "secret") => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className="space-y-4">
      <div className="p-3 bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 text-sm rounded">
        {t("manualSetupInstructions")}
      </div>

      <div className="space-y-3">
        <div>
          <label className="text-xs font-medium text-muted-foreground">URL</label>
          <div className="flex items-center gap-2 mt-1">
            <code className="flex-1 p-2 bg-muted rounded text-xs break-all">
              {secretData.webhook_url}
            </code>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(secretData.webhook_url, "url")}
            >
              {copied === "url" ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        <div>
          <label className="text-xs font-medium text-muted-foreground">Secret</label>
          <div className="flex items-center gap-2 mt-1">
            <code className="flex-1 p-2 bg-muted rounded text-xs font-mono">
              {secretData.webhook_secret}
            </code>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(secretData.webhook_secret, "secret")}
            >
              {copied === "secret" ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        <div>
          <label className="text-xs font-medium text-muted-foreground">{t("events")}</label>
          <p className="text-sm mt-1">{secretData.events.join(", ")}</p>
        </div>
      </div>

      <div className="flex gap-2">
        <Button
          size="sm"
          onClick={onMarkConfigured}
          disabled={loading}
        >
          {t("markConfigured")}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          disabled={loading}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          {t("tryAgain")}
        </Button>
      </div>
    </div>
  );
}
