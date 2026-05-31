"use client";

import { useTranslations } from "next-intl";
import { RefreshCw, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { WebhookStatus } from "@/lib/viewModels/repository";

interface WebhookRegisteredViewProps {
  status: WebhookStatus;
  loading: boolean;
  onReregister: () => Promise<void>;
  onDelete: () => Promise<void>;
}

export function WebhookRegisteredView({
  status,
  loading,
  onReregister,
  onDelete,
}: WebhookRegisteredViewProps) {
  const t = useTranslations("repositories.webhook");

  return (
    <div className="space-y-3">
      <div className="text-sm text-muted-foreground">
        <p>URL: {status.webhook_url}</p>
        <p>{t("events")}: {status.events?.join(", ")}</p>
      </div>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onReregister}
          disabled={loading}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          {t("reregister")}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onDelete}
          disabled={loading}
          className="text-destructive hover:text-destructive"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          {t("delete")}
        </Button>
      </div>
    </div>
  );
}
