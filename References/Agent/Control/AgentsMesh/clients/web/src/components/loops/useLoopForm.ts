"use client";

import { useState, useCallback, useEffect } from "react";
import { useLoopStore } from "@/stores/loop";
import { toast } from "sonner";
import type { LoopData } from "@/lib/viewModels/loop";

/**
 * useLoopForm — owns every per-field useState for the LoopCreateDialog, plus
 * the open/editLoop sync effect and the submit handler. The dialog itself is
 * left to do UI composition only.
 *
 * configValues are not owned here; the agent-config form lives in the dialog
 * (useConfigOptions). Pass the latest map into `submit(configValues)` at call
 * time so handleSubmit doesn't need to be re-bound on every keystroke.
 */
export interface UseLoopFormResult {
  // Basic fields
  name: string;
  setName: (v: string) => void;
  description: string;
  setDescription: (v: string) => void;
  promptTemplate: string;
  setPromptTemplate: (v: string) => void;

  // Pod config fields
  selectedAgentSlug: string | null;
  setSelectedAgentSlug: (v: string | null) => void;
  selectedRunnerId: number | null;
  setSelectedRunnerId: (v: number | null) => void;
  selectedRepositoryId: number | null;
  setSelectedRepositoryId: (v: number | null) => void;
  selectedBranch: string;
  setSelectedBranch: (v: string) => void;
  // Credential bundle (kind='credential') — single-select. "" = use Agent default auth.
  selectedCredentialName: string;
  setSelectedCredentialName: (v: string) => void;
  // Runtime bundles (kind='runtime') — ordered multi-select.
  selectedRuntimeBundleNames: string[];
  setSelectedRuntimeBundleNames: (v: string[]) => void;

  // Loop-specific fields
  executionMode: string;
  setExecutionMode: (v: string) => void;
  cronEnabled: boolean;
  setCronEnabled: (v: boolean) => void;
  cronExpression: string;
  setCronExpression: (v: string) => void;
  sandboxStrategy: string;
  setSandboxStrategy: (v: string) => void;
  concurrencyPolicy: string;
  setConcurrencyPolicy: (v: string) => void;
  timeoutMinutes: number;
  setTimeoutMinutes: (v: number) => void;
  callbackUrl: string;
  setCallbackUrl: (v: string) => void;
  sessionPersistence: boolean;
  setSessionPersistence: (v: boolean) => void;
  maxConcurrentRuns: number;
  setMaxConcurrentRuns: (v: number) => void;
  maxRetainedRuns: number;
  setMaxRetainedRuns: (v: number) => void;

  // Submission
  loading: boolean;
  isEdit: boolean;
  submit: (configValues: Record<string, unknown>) => Promise<void>;
}

export function useLoopForm(args: {
  open: boolean;
  editLoop?: LoopData;
  onCreated: (createdLoop?: LoopData) => void;
  t: (key: string) => string;
}): UseLoopFormResult {
  const { open, editLoop, onCreated, t } = args;
  const createLoop = useLoopStore((s) => s.createLoop);
  const updateLoop = useLoopStore((s) => s.updateLoop);
  const isEdit = !!editLoop;

  const [loading, setLoading] = useState(false);

  // Basics
  const [name, setName] = useState(editLoop?.name || "");
  const [description, setDescription] = useState(editLoop?.description || "");
  const [promptTemplate, setPromptTemplate] = useState(editLoop?.prompt_template || "");

  // Pod config
  const [selectedAgentSlug, setSelectedAgentSlug] = useState<string | null>(editLoop?.agent_slug || null);
  const [selectedRunnerId, setSelectedRunnerId] = useState<number | null>(editLoop?.runner_id || null);
  const [selectedRepositoryId, setSelectedRepositoryId] = useState<number | null>(editLoop?.repository_id || null);
  const [selectedBranch, setSelectedBranch] = useState(editLoop?.branch_name || "");
  // Credential / runtime bundles are initialized empty here. LoopCreateDialog
  // reconciles them from editLoop.used_env_bundles once the bundle list has
  // loaded (so we can classify each name by kind).
  const [selectedCredentialName, setSelectedCredentialName] = useState<string>("");
  const [selectedRuntimeBundleNames, setSelectedRuntimeBundleNames] = useState<string[]>([]);

  // Loop-only
  const [executionMode, setExecutionMode] = useState<string>(editLoop?.execution_mode || "autopilot");
  const [cronEnabled, setCronEnabled] = useState(!!editLoop?.cron_expression);
  const [cronExpression, setCronExpression] = useState(editLoop?.cron_expression || "");
  const [sandboxStrategy, setSandboxStrategy] = useState<string>(editLoop?.sandbox_strategy || "persistent");
  const [concurrencyPolicy, setConcurrencyPolicy] = useState<string>(editLoop?.concurrency_policy || "skip");
  const [timeoutMinutes, setTimeoutMinutes] = useState(editLoop?.timeout_minutes || 60);
  const [callbackUrl, setCallbackUrl] = useState(editLoop?.callback_url || "");
  const [sessionPersistence, setSessionPersistence] = useState(editLoop?.session_persistence ?? true);
  const [maxConcurrentRuns, setMaxConcurrentRuns] = useState(editLoop?.max_concurrent_runs || 1);
  const [maxRetainedRuns, setMaxRetainedRuns] = useState(editLoop?.max_retained_runs || 0);

  // Sync form state when the dialog opens. We deliberately depend on `open`
  // only — `editLoop` reference can churn (useCurrentLoop returns a fresh
  // JSON.parse on every store tick), and re-running this effect on every
  // churn would clobber user edits (or the LoopCreateDialog reconcile that
  // patches credential/runtime picks from `used_env_bundles` after bundles
  // load). Capture the snapshot once at open time.
  useEffect(() => {
    if (!open) return;
    setName(editLoop?.name || "");
    setDescription(editLoop?.description || "");
    setPromptTemplate(editLoop?.prompt_template || "");
    setSelectedAgentSlug(editLoop?.agent_slug || null);
    setSelectedRunnerId(editLoop?.runner_id || null);
    setSelectedRepositoryId(editLoop?.repository_id || null);
    setSelectedBranch(editLoop?.branch_name || "");
    // Reset bundle picks; LoopCreateDialog reconciles them after bundles load.
    setSelectedCredentialName("");
    setSelectedRuntimeBundleNames([]);
    setExecutionMode(editLoop?.execution_mode || "autopilot");
    setCronEnabled(!!editLoop?.cron_expression);
    setCronExpression(editLoop?.cron_expression || "");
    setSandboxStrategy(editLoop?.sandbox_strategy || "persistent");
    setConcurrencyPolicy(editLoop?.concurrency_policy || "skip");
    setTimeoutMinutes(editLoop?.timeout_minutes || 60);
    setCallbackUrl(editLoop?.callback_url || "");
    setSessionPersistence(editLoop?.session_persistence ?? true);
    setMaxConcurrentRuns(editLoop?.max_concurrent_runs || 1);
    setMaxRetainedRuns(editLoop?.max_retained_runs || 0);
    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const submit = useCallback(
    async (configValues: Record<string, unknown>) => {
      if (!name.trim() || !promptTemplate.trim() || !selectedAgentSlug) return;

      setLoading(true);
      try {
        const data = {
          name: name.trim(),
          description: description || undefined,
          agent_slug: selectedAgentSlug,
          prompt_template: promptTemplate,
          runner_id: selectedRunnerId || undefined,
          repository_id: selectedRepositoryId || undefined,
          branch_name: selectedBranch || undefined,
          // Merge credential first + runtime bundles after. Send always so
          // create and update are symmetric: [] explicitly clears.
          used_env_bundles: [selectedCredentialName, ...selectedRuntimeBundleNames].filter(Boolean),
          config_overrides:
            Object.keys(configValues).length > 0 ? configValues : undefined,
          execution_mode: executionMode,
          cron_expression: cronEnabled && cronExpression ? cronExpression : "",
          sandbox_strategy: sandboxStrategy,
          concurrency_policy: concurrencyPolicy,
          timeout_minutes: timeoutMinutes,
          callback_url: callbackUrl || undefined,
          session_persistence: sessionPersistence,
          max_concurrent_runs: maxConcurrentRuns,
          max_retained_runs: maxRetainedRuns,
        };

        if (isEdit && editLoop) {
          await updateLoop(editLoop.slug, data);
          toast.success(t("loops.updated"));
          onCreated();
        } else {
          const res = await createLoop(data);
          toast.success(t("loops.created"));
          onCreated(res.loop);
        }
      } catch (err) {
        toast.error(isEdit ? t("loops.updateFailed") : t("loops.createFailed"), {
          description: (err as Error).message,
        });
      } finally {
        setLoading(false);
      }
    },
    [
      name, description, promptTemplate, selectedAgentSlug, selectedRunnerId,
      selectedRepositoryId, selectedBranch, selectedCredentialName, selectedRuntimeBundleNames,
      executionMode, cronEnabled, cronExpression, sandboxStrategy,
      concurrencyPolicy, timeoutMinutes, callbackUrl, sessionPersistence,
      maxConcurrentRuns, maxRetainedRuns, isEdit, editLoop,
      createLoop, updateLoop, onCreated, t,
    ]
  );

  return {
    name, setName,
    description, setDescription,
    promptTemplate, setPromptTemplate,
    selectedAgentSlug, setSelectedAgentSlug,
    selectedRunnerId, setSelectedRunnerId,
    selectedRepositoryId, setSelectedRepositoryId,
    selectedBranch, setSelectedBranch,
    selectedCredentialName, setSelectedCredentialName,
    selectedRuntimeBundleNames, setSelectedRuntimeBundleNames,
    executionMode, setExecutionMode,
    cronEnabled, setCronEnabled,
    cronExpression, setCronExpression,
    sandboxStrategy, setSandboxStrategy,
    concurrencyPolicy, setConcurrencyPolicy,
    timeoutMinutes, setTimeoutMinutes,
    callbackUrl, setCallbackUrl,
    sessionPersistence, setSessionPersistence,
    maxConcurrentRuns, setMaxConcurrentRuns,
    maxRetainedRuns, setMaxRetainedRuns,
    loading, isEdit, submit,
  };
}
