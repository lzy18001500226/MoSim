import { useState, useCallback, useMemo, useEffect } from "react";
import { PodData, AgentData, RepositoryData } from "@/lib/api";
import { usePodCreationStore } from "@/stores/podCreation";
import { buildAgentfileLayer } from "@/lib/agentfile-layer";
import { POD_MODE_PTY } from "@/lib/pod-modes";
import type { PodMode } from "@/lib/pod-modes";
import { submitCreatePod } from "./useCreatePodFormSubmit";
import { usePrefsAutoFill, useEnvBundles } from "./useCreatePodFormEffects";
import type { CreatePodFormState, FormValidationErrors } from "./useCreatePodFormTypes";

// Re-export types for consumers
export type { CreatePodFormState, FormValidationErrors } from "./useCreatePodFormTypes";

/**
 * Hook to manage Create Pod form state and submission.
 *
 * EnvBundle attachment is split into two dimensions mirroring the dialog UI:
 *   - `selectedCredentialName` (single): API credential bundle.
 *   - `selectedRuntimeBundleNames` (ordered list): runtime preference bundles.
 *
 * On submit, the two are merged at the AgentFile layer with credential
 * first and runtime bundles after — so runtime preferences (model, log
 * level) can override credential defaults on conflicting keys.
 */
export function useCreatePodForm(
  availableAgents: AgentData[],
  repositories: RepositoryData[],
  onSuccess?: (pod: PodData) => void,
  configValues?: Record<string, unknown>,
  overrides?: { repositoryId?: number | null },
): CreatePodFormState {
  const { setLastChoices } = usePodCreationStore();

  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [selectedRepository, setSelectedRepository] = useState<number | null>(null);
  const [selectedBranch, setSelectedBranch] = useState<string>("");
  const [interactionMode, setInteractionMode] = useState<PodMode>(POD_MODE_PTY);
  const [prompt, setPrompt] = useState<string>("");
  const [alias, setAlias] = useState<string>("");
  const [perpetual, setPerpetual] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<FormValidationErrors>({});

  // AgentFile Layer state
  const [rawLayerMode, setRawLayerModeState] = useState(false);
  const [rawLayerText, setRawLayerText] = useState("");

  // EnvBundles for the selected agent
  const bundles = useEnvBundles(selectedAgent);

  // Auto-fill from saved preferences
  const prefsInitializedRef = usePrefsAutoFill(
    availableAgents, repositories, setSelectedAgent, setSelectedRepository, setSelectedBranch,
    overrides,
  );

  // Compute agent slug from selected agent
  const selectedAgentSlug = useMemo(() => {
    if (!selectedAgent) return "";
    return availableAgents.find((a) => a.slug === selectedAgent)?.slug || "";
  }, [selectedAgent, availableAgents]);

  // Parse supported modes from selected agent type
  const supportedModes = useMemo(() => {
    if (!selectedAgent) return [POD_MODE_PTY];
    const agent = availableAgents.find((a) => a.slug === selectedAgent);
    const raw = agent?.supported_modes;
    const modes = Array.isArray(raw)
      ? raw.map((m: string) => m.trim()).filter(Boolean)
      : (typeof raw === "string" ? raw.split(",").map((m: string) => m.trim()).filter(Boolean) : []);
    return modes.length > 0 ? modes : [POD_MODE_PTY];
  }, [selectedAgent, availableAgents]);

  const isValid = useMemo(() => selectedAgent !== null && selectedAgent !== "", [selectedAgent]);

  // Reset agent selection when available agents change
  useEffect(() => {
    if (selectedAgent && !availableAgents.find(a => a.slug === selectedAgent)) {
      setSelectedAgent(null);
      bundles.setEnvBundles([]);
      bundles.setSelectedCredentialName("");
      bundles.setSelectedRuntimeBundleNames([]);
      setInteractionMode(POD_MODE_PTY);
    }
  }, [availableAgents, selectedAgent, bundles]);

  // Auto-set interaction mode when agent changes based on supported modes
  useEffect(() => {
    if (!selectedAgent) { setInteractionMode(POD_MODE_PTY); return; }
    if (!supportedModes.includes(interactionMode)) {
      setInteractionMode(supportedModes[0] as PodMode);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAgent, supportedModes]);

  // Auto-select default branch when repository is selected
  useEffect(() => {
    if (!selectedRepository) { setSelectedBranch(""); return; }
    const repo = repositories.find((r) => r.id === selectedRepository);
    if (repo?.default_branch) setSelectedBranch(repo.default_branch);
  }, [selectedRepository, repositories]);

  // Clear validation error when field changes
  useEffect(() => {
    if (selectedAgent && validationErrors.agent) {
      setValidationErrors((prev) => ({ ...prev, agent: undefined }));
    }
  }, [selectedAgent, validationErrors.agent]);

  const validate = useCallback((): boolean => {
    const errors: FormValidationErrors = {};
    if (!selectedAgent) errors.agent = "Please select an agent";
    if (selectedRepository && !selectedBranch.trim()) {
      errors.branch = "Branch name is recommended when using a repository";
    }
    if (selectedBranch.trim() && !/^[a-zA-Z0-9._/-]+$/.test(selectedBranch)) {
      errors.branch = "Branch name contains invalid characters";
    }
    setValidationErrors(errors);
    return Object.keys(errors).filter(k => errors[k as keyof FormValidationErrors]).length === 0;
  }, [selectedAgent, selectedRepository, selectedBranch]);

  const reset = useCallback(() => {
    setSelectedAgent(null);
    setSelectedRepository(null);
    setSelectedBranch("");
    bundles.setSelectedCredentialName("");
    bundles.setSelectedRuntimeBundleNames([]);
    bundles.setEnvBundles([]);
    setInteractionMode(POD_MODE_PTY);
    setPrompt("");
    setAlias("");
    setPerpetual(false);
    setError(null);
    setWarning(null);
    setValidationErrors({});
    setRawLayerModeState(false);
    setRawLayerText("");
    prefsInitializedRef.current = false;
  }, [bundles, prefsInitializedRef]);

  // AgentFile Layer: compute from form fields
  const generatedLayer = useMemo(() => {
    const repoSlug = selectedRepository
      ? repositories.find((r) => r.id === selectedRepository)?.slug
      : undefined;
    return buildAgentfileLayer({
      configValues: configValues ?? {},
      repositorySlug: repoSlug,
      branchName: selectedBranch || undefined,
      interactionMode,
      credentialBundleName: bundles.selectedCredentialName || undefined,
      runtimeBundleNames: bundles.selectedRuntimeBundleNames.length > 0
        ? bundles.selectedRuntimeBundleNames
        : undefined,
      prompt: prompt || undefined,
    });
  }, [
    configValues, selectedRepository, repositories, selectedBranch,
    bundles.selectedCredentialName, bundles.selectedRuntimeBundleNames,
    interactionMode, prompt,
  ]);

  const agentfileLayer = rawLayerMode ? rawLayerText : generatedLayer;

  const setRawLayerMode = useCallback((enabled: boolean) => {
    if (enabled && !rawLayerText) {
      setRawLayerText(generatedLayer);
    }
    setRawLayerModeState(enabled);
  }, [generatedLayer, rawLayerText]);

  const submit = useCallback(
    async (
      selectedRunnerId: number | null | undefined,
      pluginConfig: Record<string, unknown>,
      options?: { ticketSlug?: string; cols?: number; rows?: number }
    ): Promise<PodData | null> => {
      if (!validate()) return null;
      if (!selectedAgent) { setError("Please select an agent"); return null; }
      setLoading(true);
      setError(null);
      setWarning(null);
      try {
        const result = await submitCreatePod({
          selectedAgent, alias, perpetual, selectedRunnerId,
          agentfileLayer: agentfileLayer || undefined, options,
        });
        if (result) {
          setLastChoices({
            lastAgentSlug: selectedAgent,
            lastRepositoryId: selectedRepository,
            lastCredentialName: bundles.selectedCredentialName,
            lastRuntimeBundleNames: bundles.selectedRuntimeBundleNames,
            lastBranchName: selectedBranch || null,
          });
          if (result.warning) setWarning(result.warning);
          onSuccess?.(result.pod);
        }
        return result?.pod ?? null;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to create pod";
        setError(message);
        console.error("Failed to create pod:", err);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [
      selectedAgent, selectedRepository, selectedBranch,
      bundles.selectedCredentialName, bundles.selectedRuntimeBundleNames,
      alias, perpetual, agentfileLayer, onSuccess, validate, setLastChoices,
    ]
  );

  return {
    selectedAgent, selectedRepository, selectedBranch,
    selectedCredentialName: bundles.selectedCredentialName,
    selectedRuntimeBundleNames: bundles.selectedRuntimeBundleNames,
    interactionMode, prompt, alias, perpetual,
    envBundles: bundles.envBundles, loadingBundles: bundles.loadingBundles,
    setSelectedAgent, setSelectedRepository, setSelectedBranch,
    setSelectedCredentialName: bundles.setSelectedCredentialName,
    setSelectedRuntimeBundleNames: bundles.setSelectedRuntimeBundleNames,
    setInteractionMode, setPrompt, setAlias, setPerpetual, selectedAgentSlug, supportedModes,
    loading, error, warning, validationErrors, isValid, reset, validate, submit,
    // AgentFile Layer
    rawLayerMode, rawLayerText, agentfileLayer, setRawLayerMode, setRawLayerText,
  };
}
