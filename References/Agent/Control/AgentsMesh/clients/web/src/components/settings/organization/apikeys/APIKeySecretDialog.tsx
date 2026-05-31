"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Check, Copy } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import type { TranslationFn } from "../GeneralSettings";

interface APIKeySecretDialogProps {
  rawKey: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  t: TranslationFn;
}

export function APIKeySecretDialog({ rawKey, open, onOpenChange, t }: APIKeySecretDialogProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(rawKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy to clipboard:", err);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("settings.apiKeys.secretDialog.title")}</DialogTitle>
          <DialogDescription>
            {t("settings.apiKeys.secretDialog.description")}
          </DialogDescription>
        </DialogHeader>

        <div className="px-6 py-4 space-y-4">
          <div className="bg-muted p-3 rounded-lg flex items-center justify-between gap-2">
            <code className="text-sm break-all flex-1 select-all">{rawKey}</code>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="flex-shrink-0"
              aria-label={t("settings.apiKeys.secretDialog.copy")}
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </Button>
          </div>
          <Button className="w-full" onClick={() => onOpenChange(false)}>
            {t("settings.apiKeys.secretDialog.done")}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
