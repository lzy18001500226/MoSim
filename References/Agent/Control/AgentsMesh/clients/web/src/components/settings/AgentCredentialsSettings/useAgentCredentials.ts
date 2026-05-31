"use client";

import { useState, useEffect, useCallback } from "react";
import { type AgentData } from "@/lib/api";
import {
  listEnvBundles,
  createEnvBundle,
  updateEnvBundle,
  deleteEnvBundle,
  setPrimaryEnvBundle,
  type EnvBundle,
} from "@/lib/api/facade/envBundleConnect";
import { listAgents } from "@/lib/api/facade/agentConnect";
import { useCurrentOrg } from "@/stores/auth";
import type { AgentCredentialsState, AgentCredentialsActions, CredentialFormData } from "./types";
import type {
  CredentialProfileViewModel,
  CredentialProfilesByAgent,
} from "../_shared/credentialViewModel";

// The settings page still thinks in per-agent groups, so this hook adapts
// EnvBundle rows into the settings-private CredentialProfileViewModel grouped
// by agent slug.

function bundleToProfile(b: EnvBundle): CredentialProfileViewModel {
  return {
    id: Number(b.id),
    agent_slug: b.agentSlug ?? "",
    name: b.name,
    description: b.description ?? undefined,
    is_default: b.kindPrimary,
    is_active: b.isActive,
    configured_fields: b.configuredFields.length > 0 ? b.configuredFields : undefined,
    configured_values:
      Object.keys(b.configuredValues).length > 0 ? b.configuredValues : undefined,
    created_at: b.createdAt,
    updated_at: b.updatedAt,
  };
}

function groupByAgent(bundles: EnvBundle[]): CredentialProfilesByAgent[] {
  const groups: Record<string, CredentialProfilesByAgent> = {};
  for (const b of bundles) {
    const slug = b.agentSlug ?? "";
    if (!groups[slug]) {
      groups[slug] = { agent_slug: slug, agent_name: "", profiles: [] };
    }
    groups[slug].profiles.push(bundleToProfile(b));
  }
  return Object.values(groups);
}

export function useAgentCredentials(
  t: (key: string) => string
): AgentCredentialsState & AgentCredentialsActions {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [profilesByAgent, setProfilesByAgent] = useState<CredentialProfilesByAgent[]>([]);
  const [agents, setAgents] = useState<AgentData[]>([]);
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());
  const [agentsWithoutPrimaryBundle, setAgentsWithoutPrimaryBundle] = useState<Set<string>>(new Set());
  const currentOrg = useCurrentOrg();

  const loadData = useCallback(async () => {
    if (!currentOrg) {
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      setError(null);

      const [bundlesRes, agentsRes] = await Promise.all([
        listEnvBundles({ kind: "credential" }),
        listAgents(currentOrg.slug),
      ]);

      const grouped = groupByAgent(bundlesRes.items || []);
      setProfilesByAgent(grouped);
      const agentList = [
        ...agentsRes.builtin_agents,
        ...agentsRes.custom_agents,
        ...agentsRes.agents,
      ];
      setAgents(agentList);

      const noPrimarySet = new Set<string>();
      agentList.forEach((a: AgentData) => noPrimarySet.add(a.slug));
      grouped.forEach((g) => {
        if (g.profiles.some((p) => p.is_default)) {
          noPrimarySet.delete(g.agent_slug);
        }
      });
      setAgentsWithoutPrimaryBundle(noPrimarySet);

      const expandedIds = new Set<string>();
      if (agentList.length > 0) expandedIds.add(agentList[0].slug);
      grouped.forEach((g) => {
        if (g.profiles.length > 0) expandedIds.add(g.agent_slug);
      });
      setExpandedAgents(expandedIds);
    } catch (err) {
      console.error("Failed to load env bundles:", err);
      setError(t("settings.agentCredentials.failedToLoad"));
    } finally {
      setLoading(false);
    }
  }, [t, currentOrg]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const toggleAgent = useCallback((agentSlug: string) => {
    setExpandedAgents((prev) => {
      const next = new Set(prev);
      if (next.has(agentSlug)) next.delete(agentSlug);
      else next.add(agentSlug);
      return next;
    });
  }, []);

  const handleClearPrimaryBundle = useCallback(async (agentSlug: string) => {
    try {
      setError(null);
      const group = profilesByAgent.find((g) => g.agent_slug === agentSlug);
      const currentDefault = group?.profiles.find((p) => p.is_default);
      if (currentDefault) {
        await updateEnvBundle(BigInt(currentDefault.id), { kindPrimary: false });
      }
      setSuccess(t("settings.agentCredentials.defaultSet"));
      await loadData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error("Failed to clear primary bundle:", err);
      setError(t("settings.agentCredentials.failedToSetDefault"));
    }
  }, [profilesByAgent, loadData, t]);

  const handleSetDefault = useCallback(async (profileId: number) => {
    try {
      setError(null);
      await setPrimaryEnvBundle(BigInt(profileId));
      setSuccess(t("settings.agentCredentials.defaultSet"));
      await loadData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error("Failed to set primary:", err);
      setError(t("settings.agentCredentials.failedToSetDefault"));
    }
  }, [loadData, t]);

  const handleDelete = useCallback(async (profileId: number) => {
    try {
      setError(null);
      await deleteEnvBundle(BigInt(profileId));
      setSuccess(t("settings.agentCredentials.profileDeleted"));
      await loadData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error("Failed to delete bundle:", err);
      setError(t("settings.agentCredentials.failedToDelete"));
    }
  }, [loadData, t]);

  const handleSaveProfile = useCallback(async (
    agentSlug: string,
    data: CredentialFormData,
    editingProfile: CredentialProfileViewModel | null
  ) => {
    try {
      if (editingProfile) {
        await updateEnvBundle(BigInt(editingProfile.id), {
          name: data.name,
          description: data.description || undefined,
          hasData: Object.keys(data.credentials).length > 0,
          data: Object.keys(data.credentials).length > 0 ? data.credentials : undefined,
        });
        setSuccess(t("settings.agentCredentials.profileUpdated"));
      } else {
        await createEnvBundle({
          agentSlug,
          name: data.name,
          description: data.description || undefined,
          kind: "credential",
          data: data.credentials,
        });
        setSuccess(t("settings.agentCredentials.profileCreated"));
      }
      await loadData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error("Failed to save env bundle:", err);
      throw err;
    }
  }, [loadData, t]);

  const getProfilesForAgent = useCallback((agentSlug: string): CredentialProfileViewModel[] => {
    const group = profilesByAgent.find((g) => g.agent_slug === agentSlug);
    return group?.profiles || [];
  }, [profilesByAgent]);

  return {
    loading, error, success,
    profilesByAgent, agents, expandedAgents, agentsWithoutPrimaryBundle,
    toggleAgent, handleClearPrimaryBundle, handleSetDefault,
    handleDelete, handleSaveProfile, getProfilesForAgent,
    setError, setSuccess,
  };
}
