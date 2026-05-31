import { useCallback, useState } from "react";
import type { AgentData } from "@/lib/api";
import {
  listEnvBundles,
  createEnvBundle,
  updateEnvBundle,
  deleteEnvBundle,
  setPrimaryEnvBundle,
} from "@/lib/api/facade/envBundleConnect";
import type { RuntimeBundleViewModel, RuntimeBundleFormData } from "./types";
import type { AgentConfigMessages } from "./useAgentConfigMessages";
import { toRuntimeBundle } from "./envBundleWire";

export interface RuntimeBundlesState {
  runtimeBundles: RuntimeBundleViewModel[];
}

export interface RuntimeBundlesActions {
  loadRuntimeBundles: (agent: AgentData) => Promise<void>;
  handleSaveRuntimeBundle: (
    data: RuntimeBundleFormData,
    editingBundle: RuntimeBundleViewModel | null,
    agent: AgentData
  ) => Promise<void>;
  handleSetRuntimePrimary: (id: number) => Promise<void>;
  handleClearRuntimePrimary: () => Promise<void>;
  handleDeleteRuntimeBundle: (id: number) => Promise<void>;
}

/**
 * Owns the runtime-kind EnvBundle slice of the agent config page.
 *
 * Runtime bundles hold plaintext preferences (model overrides, log levels,
 * proxy hosts). They share the wire shape with credentials but values
 * round-trip via `configured_values`, so the list UI shows the actual KV
 * pairs instead of just key names.
 */
export function useRuntimeBundles(
  msgs: AgentConfigMessages,
  t: (key: string) => string
): RuntimeBundlesState & RuntimeBundlesActions {
  const [runtimeBundles, setRuntimeBundles] = useState<RuntimeBundleViewModel[]>([]);

  const loadRuntimeBundles = useCallback(async (agent: AgentData) => {
    try {
      const res = await listEnvBundles({ kind: "runtime", agentSlug: agent.slug })
        .catch(() => ({ items: [] }));
      setRuntimeBundles((res.items ?? []).map((b) => toRuntimeBundle(b, agent.slug)));
    } catch (err) {
      msgs.reportError(err, t, "settings.agentConfig.loadFailed");
    }
  }, [msgs, t]);

  const handleSetRuntimePrimary = useCallback(async (id: number) => {
    try {
      msgs.setError(null);
      await setPrimaryEnvBundle(BigInt(id));
      setRuntimeBundles((prev) =>
        prev.map((b) => ({ ...b, is_default: b.id === id }))
      );
      msgs.reportSuccess(t("settings.agentConfig.runtimeBundles.defaultSet"));
    } catch (err) {
      msgs.reportError(err, t, "settings.agentConfig.runtimeBundles.failedToSetDefault");
    }
  }, [msgs, t]);

  const handleClearRuntimePrimary = useCallback(async () => {
    try {
      msgs.setError(null);
      const current = runtimeBundles.find((b) => b.is_default);
      if (current) {
        await updateEnvBundle(BigInt(current.id), { kindPrimary: false });
      }
      setRuntimeBundles((prev) =>
        prev.map((b) => (b.is_default ? { ...b, is_default: false } : b))
      );
      msgs.reportSuccess(t("settings.agentConfig.runtimeBundles.defaultSet"));
    } catch (err) {
      msgs.reportError(err, t, "settings.agentConfig.runtimeBundles.failedToSetDefault");
    }
  }, [runtimeBundles, msgs, t]);

  const handleDeleteRuntimeBundle = useCallback(async (id: number) => {
    try {
      msgs.setError(null);
      await deleteEnvBundle(BigInt(id));
      setRuntimeBundles((prev) => prev.filter((b) => b.id !== id));
      msgs.reportSuccess(t("settings.agentConfig.runtimeBundles.deleted"));
    } catch (err) {
      msgs.reportError(err, t, "settings.agentConfig.runtimeBundles.failedToDelete");
    }
  }, [msgs, t]);

  // Runtime values are plaintext, but the wire payload still uses the same
  // `data` map as credential — the backend tells them apart by `kind`.
  const handleSaveRuntimeBundle = useCallback(
    async (
      data: RuntimeBundleFormData,
      editingBundle: RuntimeBundleViewModel | null,
      agent: AgentData
    ) => {
      if (editingBundle) {
        await updateEnvBundle(BigInt(editingBundle.id), {
          name: data.name,
          description: data.description || undefined,
          hasData: Object.keys(data.data).length > 0,
          data: Object.keys(data.data).length > 0 ? data.data : undefined,
        });
        msgs.reportSuccess(t("settings.agentConfig.runtimeBundles.updated"));
      } else {
        await createEnvBundle({
          agentSlug: agent.slug,
          name: data.name,
          description: data.description || undefined,
          kind: "runtime",
          data: data.data,
        });
        msgs.reportSuccess(t("settings.agentConfig.runtimeBundles.created"));
      }
      await loadRuntimeBundles(agent);
    },
    [loadRuntimeBundles, msgs, t]
  );

  return {
    runtimeBundles,
    loadRuntimeBundles,
    handleSaveRuntimeBundle,
    handleSetRuntimePrimary,
    handleClearRuntimePrimary,
    handleDeleteRuntimeBundle,
  };
}
