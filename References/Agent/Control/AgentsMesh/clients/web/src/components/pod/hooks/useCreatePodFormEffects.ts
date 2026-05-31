import { useState, useEffect, useRef } from "react";
import type { AgentData, RepositoryData, EnvBundleSummary } from "@/lib/api";
import { listEnvBundles } from "@/lib/api/facade/envBundleConnect";
import { usePodCreationStore } from "@/stores/podCreation";

/**
 * Hook managing auto-fill from saved preferences when agents/repos become available.
 * Returns a ref that tracks whether preferences have been initialized.
 *
 * `overrides` lets callers declare explicit context (e.g. ticket repository) that
 * must beat saved prefs. When a field is provided here, the matching pref branch
 * is skipped so the explicit value can be applied by its own initializer without
 * a race against this effect.
 */
export function usePrefsAutoFill(
  availableAgents: AgentData[],
  repositories: RepositoryData[],
  setSelectedAgent: (slug: string | null) => void,
  setSelectedRepository: (id: number | null) => void,
  setSelectedBranch: (branch: string) => void,
  overrides?: { repositoryId?: number | null },
) {
  const { lastAgentSlug, lastRepositoryId, lastBranchName } = usePodCreationStore();
  const prefsInitializedRef = useRef(false);
  const overrideRepositoryId = overrides?.repositoryId ?? null;
  useEffect(() => {
    if (prefsInitializedRef.current || availableAgents.length === 0) return;

    if (lastAgentSlug && availableAgents.find(a => a.slug === lastAgentSlug)) {
      setSelectedAgent(lastAgentSlug);
    }
    if (
      !overrideRepositoryId &&
      lastRepositoryId &&
      repositories.find(r => r.id === lastRepositoryId)
    ) {
      setSelectedRepository(lastRepositoryId);
    }
    if (lastBranchName) {
      setSelectedBranch(lastBranchName);
    }

    prefsInitializedRef.current = true;
  }, [availableAgents, repositories, lastAgentSlug, lastRepositoryId, lastBranchName, overrideRepositoryId, setSelectedAgent, setSelectedRepository, setSelectedBranch]);

  return prefsInitializedRef;
}

/**
 * Hook that loads EnvBundles available for the selected agent — both
 * credential kind (API keys, encrypted server-side) and runtime kind
 * (model overrides, log levels, plaintext).
 *
 * Returns split selection state to mirror the dialog UI:
 *   - `selectedCredentialName`: single value, "" = use Agent default auth
 *   - `selectedRuntimeBundleNames`: ordered multi-select (later overrides earlier)
 *
 * Persisted preferences (`lastCredentialName`, `lastRuntimeBundleNames`) are
 * restored as the initial selection; if absent, falls back to the
 * `kind_primary=true` bundle of each kind (so a "default" set propagates).
 */
export function useEnvBundles(selectedAgent: string | null) {
  const { lastCredentialName, lastRuntimeBundleNames } = usePodCreationStore();
  const [envBundles, setEnvBundles] = useState<EnvBundleSummary[]>([]);
  const [loadingBundles, setLoadingBundles] = useState(false);
  const [selectedCredentialName, setSelectedCredentialName] = useState<string>("");
  const [selectedRuntimeBundleNames, setSelectedRuntimeBundleNames] = useState<string[]>([]);

  useEffect(() => {
    if (!selectedAgent) {
      setEnvBundles([]);
      setSelectedCredentialName("");
      setSelectedRuntimeBundleNames([]);
      return;
    }

    const load = async () => {
      setLoadingBundles(true);
      try {
        // Load both kinds in parallel. Failure of one shouldn't take out
        // the other (credential may be empty while runtime has entries).
        const [credRes, runtimeRes] = await Promise.all([
          listEnvBundles({ kind: "credential", agentSlug: selectedAgent }).catch(() => ({ items: [] })),
          listEnvBundles({ kind: "runtime", agentSlug: selectedAgent }).catch(() => ({ items: [] })),
        ]);
        const mapBundle = (b: {
          id: bigint;
          agentSlug?: string;
          name: string;
          kind: string;
          kindPrimary: boolean;
          configuredFields: string[];
        }): EnvBundleSummary => ({
          id: Number(b.id),
          name: b.name,
          agent_slug: b.agentSlug ?? selectedAgent,
          kind: b.kind,
          kind_primary: b.kindPrimary,
          configured_fields:
            b.configuredFields.length > 0 ? b.configuredFields : undefined,
        });
        const credBundles: EnvBundleSummary[] = (credRes.items ?? []).map(mapBundle);
        const runtimeBundles: EnvBundleSummary[] = (runtimeRes.items ?? []).map(mapBundle);
        setEnvBundles([...credBundles, ...runtimeBundles]);

        // Credential auto-select: saved pref (if still exists) → kind_primary → "".
        const credNames = new Set(credBundles.map((b) => b.name));
        if (lastCredentialName && credNames.has(lastCredentialName)) {
          setSelectedCredentialName(lastCredentialName);
        } else {
          const primaryCred = credBundles.find((b) => b.kind_primary);
          setSelectedCredentialName(primaryCred?.name ?? "");
        }

        // Runtime auto-select: saved prefs (filtered to still-existing) → all
        // primary runtime bundles → empty.
        const runtimeNames = new Set(runtimeBundles.map((b) => b.name));
        const savedRuntime = (lastRuntimeBundleNames ?? []).filter((n) => runtimeNames.has(n));
        if (savedRuntime.length > 0) {
          setSelectedRuntimeBundleNames(savedRuntime);
        } else {
          setSelectedRuntimeBundleNames(
            runtimeBundles.filter((b) => b.kind_primary).map((b) => b.name)
          );
        }
      } catch (err) {
        console.error("Failed to load env bundles:", err);
        setEnvBundles([]);
        setSelectedCredentialName("");
        setSelectedRuntimeBundleNames([]);
      } finally {
        setLoadingBundles(false);
      }
    };

    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAgent]);

  return {
    envBundles,
    setEnvBundles,
    loadingBundles,
    selectedCredentialName,
    setSelectedCredentialName,
    selectedRuntimeBundleNames,
    setSelectedRuntimeBundleNames,
  };
}
