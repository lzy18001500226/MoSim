"use client";

import { useTranslations } from "next-intl";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WebhookNotRegisteredViewProps {
  loading: boolean;
  onRegister: () => Promise<void>;
}

export function WebhookNotRegisteredView({
  loading,
  onRegister,
}: WebhookNotRegisteredViewProps) {
  const t = useTranslations("repositories.webhook");

  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        {t("notRegisteredDescription")}
      </p>
      <div className="flex gap-2">
        <Button
          size="sm"
          onClick={onRegister}
          disabled={loading}
        >
          {loading ? (
            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
          ) : null}
          {t("register")}
        </Button>
      </div>
    </div>
  );
}
