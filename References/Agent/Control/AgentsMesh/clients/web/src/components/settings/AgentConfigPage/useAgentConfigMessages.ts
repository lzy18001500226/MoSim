import { useCallback, useState } from "react";
import { toast } from "sonner";
import { getLocalizedErrorMessage } from "@/lib/api/errors";

/**
 * Shared error/success surface used by every sub-hook on the agent config
 * page. The page wants a single AlertMessage at the top regardless of
 * which sub-feature fired the success/failure, so this is centralised.
 *
 * Why a separate hook (not inline `useState`s): the sub-hooks
 * (`useCredentialBundles`, `useRuntimeBundles`, `useAgentRuntimeConfig`)
 * all need to surface "operation X succeeded" / "operation Y failed";
 * threading the same setters into each would duplicate logic and risk
 * divergence (one hook auto-clears after 3s, another doesn't, etc.).
 * Centralising here keeps that contract uniform.
 */
export interface AgentConfigMessages {
  error: string | null;
  success: string | null;
  setError: (msg: string | null) => void;
  setSuccess: (msg: string | null) => void;
  /**
   * Standard failure handler: log to console, surface localized message in
   * both the page banner and a toast. Returns the resolved message so
   * callers can chain (or ignore).
   */
  reportError: (err: unknown, t: (key: string) => string, fallbackKey: string) => string;
  /**
   * Set a transient success message that auto-clears after the given
   * timeout (default 3s). Replaces any previously-set success.
   */
  reportSuccess: (msg: string, timeoutMs?: number) => void;
}

export function useAgentConfigMessages(): AgentConfigMessages {
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const reportError = useCallback(
    (err: unknown, t: (key: string) => string, fallbackKey: string): string => {
      console.error(fallbackKey, err);
      const msg = getLocalizedErrorMessage(err, t, t(fallbackKey));
      setError(msg);
      toast.error(msg);
      return msg;
    },
    []
  );

  const reportSuccess = useCallback((msg: string, timeoutMs = 3000) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(null), timeoutMs);
  }, []);

  return { error, success, setError, setSuccess, reportError, reportSuccess };
}
