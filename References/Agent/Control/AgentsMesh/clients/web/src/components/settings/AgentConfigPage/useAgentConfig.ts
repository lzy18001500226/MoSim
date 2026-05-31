"use client";

import { useCallback, useEffect, useState } from "react";
import type { AgentData } from "@/lib/api";
import { listAgents } from "@/lib/api/facade/agentConnect";
import { useCurrentOrg } from "@/stores/auth";
import type {
  AgentConfigState,
  AgentConfigActions,
  CredentialFormData,
  RuntimeBundleFormData,
  RuntimeBundleViewModel,
} from "./types";
import type { CredentialProfileViewModel } from "../_shared/credentialViewModel";
import { useAgentConfigMessages } from "./useAgentConfigMessages";
import { useCredentialBundles } from "./useCredentialBundles";
import { useRuntimeBundles } from "./useRuntimeBundles";
import { useAgentRuntimeConfig } from "./useAgentRuntimeConfig";

/**
 * Facade hook for the per-agent settings page. Composes three independent
 * slice hooks behind a single state/action surface so the rest of the
 * AgentConfigPage component tree stays unchanged:
 *
 *   - useCredentialBundles     — credential-kind EnvBundles (encrypted)
 *   - useRuntimeBundles        — runtime-kind EnvBundles (plaintext)
 *   - useAgentRuntimeConfig    — typed agent-schema runtime config values
 *
 * Plus `useAgentConfigMessages` for the shared error/success banner.
 *
 * The facade owns:
 *   - Agent identity resolution (`agentSlug` → `AgentData`)
 *   - Page-level loading flag (true until *every* slice has loaded once)
 *   - Triggering each slice's load on agent change
 */
export function useAgentConfig(
  agentSlug: string,
  t: (key: string) => string
): AgentConfigState & AgentConfigActions {
  const [loading, setLoading] = useState(true);
  const [agent, setAgent] = useState<AgentData | null>(null);
  const currentOrg = useCurrentOrg();

  const msgs = useAgentConfigMessages();
  const creds = useCredentialBundles(msgs, t);
  const runtime = useRuntimeBundles(msgs, t);
  const cfg = useAgentRuntimeConfig(msgs, t);

  // Resolve the agent + fan out to every slice. Sequential agent lookup,
  // then parallel slice loads (each slice owns its own error fallback so
  // one failing won't take down the rest).
  const loadData = useCallback(async () => {
    if (!currentOrg) {
      setLoading(false);
      return;
    }
    setLoading(true);
    msgs.setError(null);

    try {
      const agentsRes = await listAgents(currentOrg.slug);
      const allAgents: AgentData[] = [
        ...agentsRes.builtin_agents,
        ...agentsRes.custom_agents,
        ...agentsRes.agents,
      ];
      const found = allAgents.find((a) => a.slug === agentSlug);
      if (!found) {
        msgs.setError(t("settings.agentConfig.agentNotFound"));
        setAgent(null);
        return;
      }
      setAgent(found);
      await Promise.all([
        creds.loadCredentialBundles(found),
        runtime.loadRuntimeBundles(found),
        cfg.loadRuntimeConfig(found),
      ]);
    } catch (err) {
      msgs.reportError(err, t, "settings.agentConfig.loadFailed");
    } finally {
      setLoading(false);
    }
    // creds/runtime/cfg are stable identity-by-reference (useCallback inside);
    // exhaustive-deps would still flag them so we list them explicitly.
  }, [agentSlug, t, creds, runtime, cfg, msgs, currentOrg]);

  useEffect(() => {
    loadData();
    // We intentionally re-run only on agentSlug / org change, not on identity
    // churn of the helper hooks (their handlers are stable enough that
    // re-loading would create thrash).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentSlug, currentOrg?.slug]);

  // Surface adapters: call-site components still pass the bare profile/
  // bundle/id; the facade injects the current agent so slice hooks don't
  // need to store it themselves.
  const handleSaveProfile = useCallback(
    (data: CredentialFormData, editingProfile: CredentialProfileViewModel | null) => {
      if (!agent) return Promise.resolve();
      return creds.handleSaveProfile(data, editingProfile, agent);
    },
    [agent, creds]
  );

  const handleSaveRuntimeBundle = useCallback(
    (data: RuntimeBundleFormData, editingBundle: RuntimeBundleViewModel | null) => {
      if (!agent) return Promise.resolve();
      return runtime.handleSaveRuntimeBundle(data, editingBundle, agent);
    },
    [agent, runtime]
  );

  const handleSaveConfig = useCallback(() => {
    if (!agent) return Promise.resolve();
    return cfg.handleSaveConfig(agent);
  }, [agent, cfg]);

  return {
    // State
    loading,
    savingConfig: cfg.savingConfig,
    agent,
    configFields: cfg.configFields,
    configValues: cfg.configValues,
    credentialProfiles: creds.credentialProfiles,
    noPrimaryBundle: creds.noPrimaryBundle,
    runtimeBundles: runtime.runtimeBundles,
    error: msgs.error,
    success: msgs.success,

    // Actions — credential
    handleClearPrimaryBundle: creds.handleClearPrimaryBundle,
    handleSetDefault: creds.handleSetDefault,
    handleDeleteProfile: creds.handleDeleteProfile,
    handleSaveProfile,

    // Actions — runtime bundles
    handleSetRuntimePrimary: runtime.handleSetRuntimePrimary,
    handleClearRuntimePrimary: runtime.handleClearRuntimePrimary,
    handleDeleteRuntimeBundle: runtime.handleDeleteRuntimeBundle,
    handleSaveRuntimeBundle,

    // Actions — agent runtime config
    handleConfigChange: cfg.handleConfigChange,
    handleSaveConfig,

    // UI
    setError: msgs.setError,
    setSuccess: msgs.setSuccess,
    loadData,
  };
}
