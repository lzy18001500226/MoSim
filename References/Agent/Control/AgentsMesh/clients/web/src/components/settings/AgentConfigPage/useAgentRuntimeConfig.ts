import { useCallback, useState } from "react";
import { type ConfigField, type AgentData } from "@/lib/api";
import {
  getAgentConfigSchema,
  getUserAgentConfig,
  setUserAgentConfig,
} from "@/lib/api/facade/agentConnect";
import { useCurrentOrg } from "@/stores/auth";
import type { AgentConfigMessages } from "./useAgentConfigMessages";

export interface AgentRuntimeConfigState {
  configFields: ConfigField[];
  configValues: Record<string, unknown>;
  savingConfig: boolean;
}

export interface AgentRuntimeConfigActions {
  loadRuntimeConfig: (agent: AgentData) => Promise<void>;
  handleConfigChange: (fieldName: string, value: unknown) => void;
  handleSaveConfig: (agent: AgentData) => Promise<void>;
}

/**
 * Owns the agent-schema-driven runtime config slice (the "Runtime
 * Configuration" section).
 *
 * Distinct from runtime *bundles* (which are user-defined KV groups): this
 * is the typed config schema declared by the agent itself — fields with
 * labels, defaults, validation. The schema comes from the agent service;
 * user-customised values are persisted via `set_user_config`.
 */
export function useAgentRuntimeConfig(
  msgs: AgentConfigMessages,
  t: (key: string) => string
): AgentRuntimeConfigState & AgentRuntimeConfigActions {
  const [configFields, setConfigFields] = useState<ConfigField[]>([]);
  const [configValues, setConfigValues] = useState<Record<string, unknown>>({});
  const [savingConfig, setSavingConfig] = useState(false);
  const currentOrg = useCurrentOrg();

  const loadRuntimeConfig = useCallback(async (agent: AgentData) => {
    const orgSlug = currentOrg?.slug;
    if (!orgSlug) {
      setConfigFields([]);
      setConfigValues({});
      return;
    }
    const schemaRes = await getAgentConfigSchema(orgSlug, agent.slug).catch(
      () => ({ fields: [] as ConfigField[] }),
    );
    const fields: ConfigField[] = schemaRes.fields || [];
    setConfigFields(fields);

    // Seed defaults from schema, then merge user-saved overrides on top.
    const defaults: Record<string, unknown> = {};
    for (const f of fields) {
      if (f.default !== undefined) defaults[f.name] = f.default;
    }

    try {
      const userConfig = await getUserAgentConfig(agent.slug);
      if (userConfig.config_values) {
        setConfigValues({ ...defaults, ...userConfig.config_values });
      } else {
        setConfigValues(defaults);
      }
    } catch {
      // No saved config yet — defaults stand.
      setConfigValues(defaults);
    }
  }, [currentOrg]);

  const handleConfigChange = useCallback((fieldName: string, value: unknown) => {
    setConfigValues((prev) => ({ ...prev, [fieldName]: value }));
  }, []);

  // Filter undefined (a field was never touched) but keep empty strings
  // ("Follow Runner" model option) and false (disabled toggles).
  const handleSaveConfig = useCallback(async (agent: AgentData) => {
    try {
      setSavingConfig(true);
      msgs.setError(null);
      const cleaned: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(configValues)) {
        if (v !== undefined) cleaned[k] = v;
      }
      await setUserAgentConfig(agent.slug, cleaned);
      msgs.reportSuccess(t("settings.agentConfig.configSaved"));
    } catch (err) {
      msgs.reportError(err, t, "settings.agentConfig.configSaveFailed");
    } finally {
      setSavingConfig(false);
    }
  }, [configValues, msgs, t]);

  return {
    configFields,
    configValues,
    savingConfig,
    loadRuntimeConfig,
    handleConfigChange,
    handleSaveConfig,
  };
}
