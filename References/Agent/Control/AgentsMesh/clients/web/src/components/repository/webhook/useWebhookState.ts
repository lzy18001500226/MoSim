"use client";

import { useState, useCallback } from "react";
import { WebhookStatus, WebhookSecretResponse } from "@/lib/api";
import {
  getRepositoryWebhookStatus,
  getRepositoryWebhookSecret,
  registerRepositoryWebhook,
  deleteRepositoryWebhook,
  markRepositoryWebhookConfigured,
} from "@/lib/api/facade/repositoryConnect";
import { useCurrentOrg } from "@/stores/auth";
import { WebhookState, WebhookSettingsState, WebhookSettingsActions } from "./types";

export interface UseWebhookStateResult extends WebhookSettingsState, WebhookSettingsActions {}

export function useWebhookState(repositoryId: number, onUpdate?: () => void): UseWebhookStateResult {
  const currentOrg = useCurrentOrg();
  const orgSlug = currentOrg?.slug ?? "";
  const [state, setState] = useState<WebhookState>("loading");
  const [status, setStatus] = useState<WebhookStatus | null>(null);
  const [secretData, setSecretData] = useState<WebhookSecretResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadStatus = useCallback(async () => {
    if (!orgSlug) return;
    setState("loading");
    setError(null);
    try {
      const res = await getRepositoryWebhookStatus(orgSlug, repositoryId);
      setStatus(res);

      if (res.registered && res.is_active) {
        setState("registered");
      } else if (res.needs_manual_setup) {
        setState("needs_manual_setup");
        try {
          const secretRes = await getRepositoryWebhookSecret(orgSlug, repositoryId);
          setSecretData(secretRes);
        } catch {
        }
      } else {
        setState("not_registered");
      }
    } catch (err) {
      console.error("Failed to load webhook status:", err);
      setError("Failed to load webhook status");
      setState("error");
    }
  }, [repositoryId, orgSlug]);

  const handleRegister = useCallback(async () => {
    if (!orgSlug) return;
    setLoading(true);
    setError(null);
    try {
      await registerRepositoryWebhook(orgSlug, repositoryId);
      onUpdate?.();
      await loadStatus();
    } catch (err) {
      console.error("Failed to register webhook:", err);
      setError("Failed to register webhook");
    } finally {
      setLoading(false);
    }
  }, [repositoryId, onUpdate, loadStatus, orgSlug]);

  const handleDelete = useCallback(async () => {
    if (!orgSlug) return;
    setLoading(true);
    setError(null);
    try {
      await deleteRepositoryWebhook(orgSlug, repositoryId);
      setState("not_registered");
      setStatus(null);
      setSecretData(null);
      onUpdate?.();
    } catch (err) {
      console.error("Failed to delete webhook:", err);
      setError("Failed to delete webhook");
    } finally {
      setLoading(false);
    }
  }, [repositoryId, onUpdate, orgSlug]);

  const handleMarkConfigured = useCallback(async () => {
    if (!orgSlug) return;
    setLoading(true);
    setError(null);
    try {
      await markRepositoryWebhookConfigured(orgSlug, repositoryId);
      setState("registered");
      onUpdate?.();
      await loadStatus();
    } catch (err) {
      console.error("Failed to mark webhook as configured:", err);
      setError("Failed to mark webhook as configured");
    } finally {
      setLoading(false);
    }
  }, [repositoryId, onUpdate, loadStatus, orgSlug]);

  return {
    state,
    status,
    secretData,
    error,
    loading,
    handleRegister,
    handleDelete,
    handleMarkConfigured,
    loadStatus,
  };
}
