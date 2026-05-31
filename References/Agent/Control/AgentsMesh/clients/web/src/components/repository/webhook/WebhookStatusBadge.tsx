"use client";

import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { useTranslations } from "next-intl";
import { WebhookState } from "./types";

interface WebhookStatusBadgeProps {
  state: WebhookState;
}

export function WebhookStatusBadge({ state }: WebhookStatusBadgeProps) {
  const t = useTranslations("repositories.webhook");

  const renderIcon = () => {
    switch (state) {
      case "registered":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "needs_manual_setup":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case "not_registered":
        return <XCircle className="h-5 w-5 text-muted-foreground" />;
      default:
        return null;
    }
  };

  const renderText = () => {
    switch (state) {
      case "registered":
        return t("status.registered");
      case "needs_manual_setup":
        return t("status.needsManualSetup");
      case "not_registered":
        return t("status.notRegistered");
      default:
        return "";
    }
  };

  return (
    <div className="flex items-center gap-2">
      {renderIcon()}
      <span className="text-sm">{renderText()}</span>
    </div>
  );
}
