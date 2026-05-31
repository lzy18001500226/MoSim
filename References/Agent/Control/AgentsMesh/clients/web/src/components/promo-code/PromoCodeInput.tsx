"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { validatePromoCode, redeemPromoCode } from "@/lib/api/facade/promocodeConnect";
import type { ValidatePromoCodeResponse, RedeemPromoCodeResponse } from "@/lib/api";
import { CheckCircle, XCircle, Loader2, Gift } from "lucide-react";

// Translation function type
type TranslateFunction = (key: string) => string;

interface PromoCodeInputProps {
  orgSlug: string;
  onRedeemSuccess?: (response: RedeemPromoCodeResponse) => void;
  onValidate?: (response: ValidatePromoCodeResponse) => void;
  disabled?: boolean;
  t: TranslateFunction;
}

export function PromoCodeInput({
  orgSlug,
  onRedeemSuccess,
  onValidate,
  disabled = false,
  t,
}: PromoCodeInputProps) {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validated, setValidated] = useState<ValidatePromoCodeResponse | null>(null);

  const handleValidate = async () => {
    if (!code.trim()) {
      setError(t("enterCode"));
      return;
    }

    setLoading(true);
    setError(null);
    setValidated(null);

    try {
      const response = await validatePromoCode(orgSlug, code);
      if (!response.valid) {
        setError(t(`errors.${response.messageCode}`) || t("invalid"));
        return;
      }
      setValidated(response);
      onValidate?.(response);
    } catch {
      setError(t("validateError"));
    } finally {
      setLoading(false);
    }
  };

  const handleRedeem = async () => {
    if (!validated) {
      await handleValidate();
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await redeemPromoCode(orgSlug, code);
      if (!response.success) {
        setError(t(`errors.${response.messageCode}`) || t("redeemError"));
        return;
      }
      onRedeemSuccess?.(response);
      // Reset state
      setCode("");
      setValidated(null);
    } catch {
      setError(t("redeemError"));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !loading && code.trim()) {
      if (validated) {
        handleRedeem();
      } else {
        handleValidate();
      }
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Gift className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={code}
            onChange={(e) => {
              setCode(e.target.value.toUpperCase());
              setError(null);
              setValidated(null);
            }}
            onKeyDown={handleKeyDown}
            placeholder={t("placeholder")}
            className="pl-9 uppercase"
            disabled={loading || disabled}
          />
        </div>
        <Button
          onClick={validated ? handleRedeem : handleValidate}
          disabled={loading || !code.trim() || disabled}
          variant={validated ? "default" : "secondary"}
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {validated ? t("redeeming") : t("validating")}
            </>
          ) : validated ? (
            t("redeem")
          ) : (
            t("validate")
          )}
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-sm text-destructive">
          <XCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {validated && (
        <div className="bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg p-3">
          <div className="flex items-center gap-2 text-green-800 dark:text-green-200">
            <CheckCircle className="h-4 w-4" />
            <span className="font-medium">{t("valid")}</span>
          </div>
          <p className="text-sm text-green-700 dark:text-green-300 mt-1">
            {t("plan")}: {validated.planDisplayName} · {t("duration")}: {validated.durationMonths} {t("months")}
          </p>
          <p className="text-xs text-green-600 dark:text-green-400 mt-1">
            {t("confirmRedeem")}
          </p>
        </div>
      )}
    </div>
  );
}
