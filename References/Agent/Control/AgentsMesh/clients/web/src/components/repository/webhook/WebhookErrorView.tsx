"use client";

import { useTranslations } from "next-intl";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WebhookErrorViewProps {
  loading: boolean;
  onRetry: () => Promise<void>;
}

export function WebhookErrorView({ loading, onRetry }: WebhookErrorViewProps) {
  const t = useTranslations("repositories.webhook");

  return (
    <div className="flex gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={onRetry}
        disabled={loading}
      >
        <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
        {t("retry")}
      </Button>
    </div>
  );
}
