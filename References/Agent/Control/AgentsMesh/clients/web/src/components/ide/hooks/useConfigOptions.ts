import { useState, useEffect, useCallback } from "react";
import { getAgentConfigSchema, getUserAgentConfig } from "@/lib/api/facade/agentConnect";
import { useCurrentOrg } from "@/stores/auth";
import type { ConfigField } from "@/lib/api";

export interface ConfigOptionsState {
  fields: ConfigField[];
  loading: boolean;
  config: Record<string, unknown>;
  updateConfig: (fieldName: string, value: unknown) => void;
  resetConfig: () => void;
}

function deriveModelField(models: unknown): ConfigField | null {
  const modelList = Array.isArray(models) ? models.filter((m): m is string => typeof m === "string") : [];
  if (modelList.length === 0) {
    return null;
  }
  return {
    name: "model",
    type: "select",
    default: "",
    options: modelList.map((m) => ({ value: m })),
  };
}

/**
 * Hook to manage agent config options and configuration
 * Loads config schema from Backend when agent is selected
 *
 * Configuration priority (high to low):
 * 1. User overrides in the form
 * 2. User personal config (from personal settings)
 * 3. Backend ConfigSchema defaults
 *
 * Special handling for model_list fields: derives a `model` select
 * field from the models list for runtime selection (not persisted to user config).
 */
export function useConfigOptions(
  runnerId: number | null,
  agentSlug?: string | null
): ConfigOptionsState {
  const [fields, setFields] = useState<ConfigField[]>([]);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState<Record<string, unknown>>({});
  const currentOrg = useCurrentOrg();

  useEffect(() => {
    let cancelled = false;

    const loadOptions = async () => {
      if (!agentSlug || !currentOrg) {
        setFields([]);
        setConfig({});
        return;
      }

      setLoading(true);
      try {
        const schema = await getAgentConfigSchema(currentOrg.slug, agentSlug).catch(
          () => ({ fields: [] as ConfigField[] }),
        );

        if (cancelled) return;

        const baseFields = schema.fields || [];

        const mergedConfig: Record<string, unknown> = {};
        for (const field of baseFields) {
          if (field.default !== undefined) {
            mergedConfig[field.name] = field.default;
          }
        }

        try {
          const userConfig = await getUserAgentConfig(agentSlug);
          if (!cancelled && userConfig.config_values) {
            const overrides = userConfig.config_values;

            for (const field of baseFields) {
              if (overrides[field.name] !== undefined) {
                mergedConfig[field.name] = overrides[field.name];
              }
            }
          }
        } catch {
        }

        if (!cancelled) {
          const modelsField = baseFields.find((f: ConfigField) => f.type === "model_list");
          const modelField = modelsField ? deriveModelField(mergedConfig[modelsField.name]) : null;

          const allFields = modelField ? [...baseFields, modelField] : baseFields;

          setFields(allFields);
          setConfig(mergedConfig);
        }
      } catch (err) {
        if (cancelled) return;
        console.error("Failed to load config schema:", err);
        setFields([]);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadOptions();

    return () => {
      cancelled = true;
    };
  }, [agentSlug, currentOrg]);

  const updateConfig = useCallback(
    (fieldName: string, value: unknown) => {
      setConfig((prev) => {
        const updated = { ...prev, [fieldName]: value };

        if (fieldName === "models") {
          const modelsField = fields.find((f) => f.type === "model_list");
          if (modelsField) {
            const modelField = deriveModelField(value);
            if (modelField) {
              const modelList = Array.isArray(value) ? value.filter((m): m is string => typeof m === "string") : [];
              const currentModel = prev["model"] as string;
              if (currentModel && !modelList.includes(currentModel)) {
                updated["model"] = "";
              }
              setFields((currentFields) => {
                const baseFields = currentFields.filter((f) => f.name !== "model");
                return [...baseFields, modelField];
              });
            }
          }
        }

        return updated;
      });
    },
    [fields]
  );

  const resetConfig = useCallback(() => {
    setConfig({});
    setFields([]);
  }, []);

  return { fields, loading, config, updateConfig, resetConfig };
}
