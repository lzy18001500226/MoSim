import type { CredentialProfileViewModel } from "../../_shared/credentialViewModel";
import type {
  CredentialFormSpec,
  CustomEnvEntry,
  OneOfCredentialField,
} from "./types";
import { getEnvKeysFromSpec } from "./index";

export interface CredentialFormState {
  values: Record<string, string>;
  selectedOneOf: Record<string, string>;
  customEnv: CustomEnvEntry[];
}

function newId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function defaultOneOfSelection(field: OneOfCredentialField): string {
  return field.options[0]?.envKey ?? "";
}

export function emptyFormState(spec: CredentialFormSpec): CredentialFormState {
  const selectedOneOf: Record<string, string> = {};
  for (const field of spec.fields) {
    if (field.kind === "oneof") {
      selectedOneOf[field.group] = defaultOneOfSelection(field);
    }
  }
  return { values: {}, selectedOneOf, customEnv: [] };
}

export function initFormStateFromProfile(
  spec: CredentialFormSpec,
  profile: CredentialProfileViewModel | null
): CredentialFormState {
  if (!profile) return emptyFormState(spec);

  const declaredKeys = getEnvKeysFromSpec(spec);
  const configuredFields = new Set(profile.configured_fields ?? []);
  const configuredValues = profile.configured_values ?? {};
  const values: Record<string, string> = {};
  const selectedOneOf: Record<string, string> = {};

  for (const field of spec.fields) {
    if (field.kind === "oneof") {
      const presentOption = field.options.find((o) => configuredFields.has(o.envKey));
      const target = presentOption?.envKey ?? defaultOneOfSelection(field);
      selectedOneOf[field.group] = target;
      if (presentOption?.kind === "text" && configuredValues[target]) {
        values[target] = configuredValues[target];
      }
    } else if (field.kind === "text" && configuredValues[field.envKey]) {
      values[field.envKey] = configuredValues[field.envKey];
    }
  }

  const customEnv: CustomEnvEntry[] = [];
  for (const key of configuredFields) {
    if (declaredKeys.has(key)) continue;
    customEnv.push({
      id: newId(),
      key,
      value: configuredValues[key] ?? "",
    });
  }

  return { values, selectedOneOf, customEnv };
}

// Collect the form state into the wire payload `Record<envKey, value>`.
// Only non-empty values are kept. For "oneof" groups only the selected option
// contributes; siblings are dropped so a leftover Auth Token doesn't leak when
// the user switched back to API Key.
export function buildCredentialsPayload(
  spec: CredentialFormSpec,
  state: CredentialFormState
): Record<string, string> {
  const out: Record<string, string> = {};

  for (const field of spec.fields) {
    if (field.kind === "oneof") {
      const sel = state.selectedOneOf[field.group];
      if (!sel) continue;
      const v = state.values[sel];
      if (v) out[sel] = v;
    } else {
      const v = state.values[field.envKey];
      if (v) out[field.envKey] = v;
    }
  }

  for (const entry of state.customEnv) {
    const key = entry.key.trim();
    if (!key || !entry.value) continue;
    out[key] = entry.value;
  }

  return out;
}
