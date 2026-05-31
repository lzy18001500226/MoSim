import { PodData } from "@/lib/api";
import type { PodMode } from "@/lib/pod-modes";
import type { EnvBundleSummary } from "@/lib/viewModels/envBundleSummary";

/**
 * Validation errors for the form
 */
export interface FormValidationErrors {
  runner?: string;
  agent?: string;
  repository?: string;
  branch?: string;
  prompt?: string;
}

export interface CreatePodFormState {
  // Selection state (order: Runner -> Agent -> Others)
  selectedAgent: string | null;
  selectedRepository: number | null;
  selectedBranch: string;
  // Credential bundle (kind='credential') — single-select. Empty string
  // means "use the Agent's default authentication" (OAuth / CLI login etc.).
  selectedCredentialName: string;
  // Runtime bundle names (kind='runtime') — ordered multi-select. Each name
  // maps to a `USE_ENV_BUNDLE "..."` directive emitted AFTER the credential
  // line, so runtime preferences (model, log level, proxy) can override
  // credential defaults when keys conflict.
  selectedRuntimeBundleNames: string[];
  interactionMode: PodMode;
  prompt: string;
  alias: string;
  perpetual: boolean;

  // EnvBundles (credential + runtime kinds) available for the selected agent
  envBundles: EnvBundleSummary[];
  loadingBundles: boolean;

  // Actions
  setSelectedAgent: (slug: string | null) => void;
  setSelectedRepository: (id: number | null) => void;
  setSelectedBranch: (branch: string) => void;
  setSelectedCredentialName: (name: string) => void;
  setSelectedRuntimeBundleNames: (names: string[]) => void;
  setInteractionMode: (mode: PodMode) => void;
  setPrompt: (prompt: string) => void;
  setAlias: (alias: string) => void;
  setPerpetual: (perpetual: boolean) => void;

  // AgentFile Layer
  rawLayerMode: boolean;
  rawLayerText: string;
  agentfileLayer: string;
  setRawLayerMode: (enabled: boolean) => void;
  setRawLayerText: (text: string) => void;

  // Computed
  selectedAgentSlug: string;
  supportedModes: string[]; // parsed from agent type's supported_modes

  // Form state
  loading: boolean;
  error: string | null;
  // Non-fatal note returned by the server (e.g. "pod created, but X is degraded").
  // Distinct from `error`, which represents a request failure.
  warning: string | null;
  validationErrors: FormValidationErrors;
  isValid: boolean;

  // Actions
  reset: () => void;
  validate: () => boolean;
  submit: (
    selectedRunnerId: number | null | undefined,
    pluginConfig: Record<string, unknown>,
    options?: { ticketSlug?: string; cols?: number; rows?: number }
  ) => Promise<PodData | null>;
}
