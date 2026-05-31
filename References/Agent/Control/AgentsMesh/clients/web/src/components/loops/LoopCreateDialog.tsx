"use client";

import React, { useEffect, useState } from "react";
import {
  ResponsiveDialog,
  ResponsiveDialogContent,
  ResponsiveDialogHeader,
  ResponsiveDialogTitle,
  ResponsiveDialogBody,
  ResponsiveDialogFooter,
} from "@/components/ui/responsive-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";

// Reuse Pod creation components
import { usePodCreationData } from "@/components/pod/hooks";
import { useConfigOptions } from "@/components/ide/hooks";
import { AgentSelect } from "@/components/pod/CreatePodForm/AgentSelect";
import { PromptInput } from "@/components/pod/CreatePodForm/PromptInput";
import type { LoopData } from "@/lib/viewModels/loop";

import { useLoopForm } from "./useLoopForm";
import { useLoopEnvBundles } from "./useLoopEnvBundles";
import { LoopPodConfigSection } from "./LoopPodConfigSection";
import { LoopScheduleSection } from "./LoopScheduleSection";

interface LoopCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: (createdLoop?: LoopData) => void;
  editLoop?: LoopData;
}

/**
 * LoopCreateDialog — orchestrates the create/edit form for a Loop.
 *
 * State + submission live in `useLoopForm`; bundle loading in
 * `useLoopEnvBundles`; the runtime/config section in `LoopPodConfigSection`;
 * the cron/policy/timeout fields in `LoopScheduleSection`. This file does
 * dialog wrapping + side-effects that bridge Loop state with the shared
 * Pod-creation data hook.
 */
export function LoopCreateDialog({
  open,
  onOpenChange,
  onCreated,
  editLoop,
}: LoopCreateDialogProps) {
  const t = useTranslations();
  const form = useLoopForm({ open, editLoop, onCreated, t });

  const {
    runners,
    repositories,
    selectedRunner,
    setSelectedRunnerId: setPodSelectedRunnerId,
    availableAgents,
  } = usePodCreationData(open);

  // Mirror runner selection into the Pod data hook so it can refresh agents.
  useEffect(() => {
    setPodSelectedRunnerId(form.selectedRunnerId);
  }, [form.selectedRunnerId, setPodSelectedRunnerId]);

  const {
    fields: configFields,
    loading: loadingConfig,
    config: configValues,
    updateConfig: handleConfigChange,
  } = useConfigOptions(selectedRunner?.id || null, form.selectedAgentSlug);

  // Restore config_overrides from editLoop once the schema has loaded.
  const [configOverridesRestored, setConfigOverridesRestored] = useState(false);
  useEffect(() => {
    if (!open) {
      setConfigOverridesRestored(false);
      return;
    }
    if (editLoop?.config_overrides && configFields.length > 0 && !configOverridesRestored) {
      Object.entries(editLoop.config_overrides).forEach(([key, value]) => {
        handleConfigChange(key, value);
      });
      setConfigOverridesRestored(true);
    }
  }, [open, editLoop, configFields, configOverridesRestored, handleConfigChange]);

  // Auto-fill branch when repository changes.
  useEffect(() => {
    if (!form.selectedRepositoryId) {
      form.setSelectedBranch("");
      return;
    }
    const repo = repositories.find((r) => r.id === form.selectedRepositoryId);
    if (repo?.default_branch) {
      form.setSelectedBranch(repo.default_branch);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.selectedRepositoryId, repositories]);

  const { envBundles, loadingBundles } = useLoopEnvBundles({
    open,
    agentSlug: form.selectedAgentSlug,
  });

  // Edit mode: reconcile `editLoop.used_env_bundles: string[]` into the
  // dialog's split state (credential single + runtime multi) once the bundle
  // list is loaded (we need each name's kind to classify it).
  useEffect(() => {
    if (!open || !editLoop || envBundles.length === 0) return;
    const kindByName = new Map(envBundles.map((b) => [b.name, b.kind]));
    const saved = editLoop.used_env_bundles ?? [];
    const credName = saved.find((n) => kindByName.get(n) === "credential") ?? "";
    const runtimeNames = saved.filter((n) => kindByName.get(n) === "runtime");
    form.setSelectedCredentialName(credName);
    form.setSelectedRuntimeBundleNames(runtimeNames);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, editLoop, envBundles]);

  // Reset agent if not available in current runner's agents (after agents load).
  useEffect(() => {
    if (
      availableAgents.length > 0 &&
      form.selectedAgentSlug &&
      !availableAgents.find((a) => a.slug === form.selectedAgentSlug)
    ) {
      form.setSelectedAgentSlug(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [availableAgents, form.selectedAgentSlug]);

  const dialogTitle = form.isEdit ? t("loops.editLoop") : t("loops.createLoop");

  return (
    <ResponsiveDialog open={open} onOpenChange={onOpenChange}>
      <ResponsiveDialogContent className="max-w-lg">
        <ResponsiveDialogHeader onClose={() => onOpenChange(false)}>
          <ResponsiveDialogTitle>{dialogTitle}</ResponsiveDialogTitle>
        </ResponsiveDialogHeader>

        <ResponsiveDialogBody className="space-y-4">
          <div className="space-y-1.5">
            <Label>{t("loops.name")}</Label>
            <Input
              value={form.name}
              onChange={(e) => form.setName(e.target.value)}
              placeholder="daily-code-review"
            />
          </div>

          <div className="space-y-1.5">
            <Label>{t("loops.description")}</Label>
            <Input
              value={form.description}
              onChange={(e) => form.setDescription(e.target.value)}
              placeholder={t("loops.descriptionPlaceholder")}
            />
          </div>

          <AgentSelect
            agents={availableAgents}
            selectedAgentSlug={form.selectedAgentSlug}
            onSelect={form.setSelectedAgentSlug}
            t={t}
          />

          {form.selectedAgentSlug && (
            <>
              <PromptInput
                value={form.promptTemplate}
                onChange={form.setPromptTemplate}
                placeholder={t("loops.promptPlaceholder")}
                t={t}
              />

              <LoopPodConfigSection
                agentSlug={form.selectedAgentSlug}
                runners={runners}
                repositories={repositories}
                envBundles={envBundles}
                configFields={configFields}
                configValues={configValues}
                loadingConfig={loadingConfig}
                loadingBundles={loadingBundles}
                selectedRunnerId={form.selectedRunnerId}
                onSelectRunner={form.setSelectedRunnerId}
                selectedCredentialName={form.selectedCredentialName}
                onSelectCredential={form.setSelectedCredentialName}
                selectedRuntimeBundleNames={form.selectedRuntimeBundleNames}
                onSelectRuntimeBundles={form.setSelectedRuntimeBundleNames}
                selectedRepositoryId={form.selectedRepositoryId}
                onSelectRepository={form.setSelectedRepositoryId}
                selectedBranch={form.selectedBranch}
                onChangeBranch={form.setSelectedBranch}
                onConfigChange={handleConfigChange}
                t={t}
              />
            </>
          )}

          <LoopScheduleSection
            cronEnabled={form.cronEnabled}
            onCronEnabledChange={form.setCronEnabled}
            cronExpression={form.cronExpression}
            onCronExpressionChange={form.setCronExpression}
            executionMode={form.executionMode}
            onExecutionModeChange={form.setExecutionMode}
            sandboxStrategy={form.sandboxStrategy}
            onSandboxStrategyChange={form.setSandboxStrategy}
            concurrencyPolicy={form.concurrencyPolicy}
            onConcurrencyPolicyChange={form.setConcurrencyPolicy}
            timeoutMinutes={form.timeoutMinutes}
            onTimeoutMinutesChange={form.setTimeoutMinutes}
            maxConcurrentRuns={form.maxConcurrentRuns}
            onMaxConcurrentRunsChange={form.setMaxConcurrentRuns}
            maxRetainedRuns={form.maxRetainedRuns}
            onMaxRetainedRunsChange={form.setMaxRetainedRuns}
            sessionPersistence={form.sessionPersistence}
            onSessionPersistenceChange={form.setSessionPersistence}
            callbackUrl={form.callbackUrl}
            onCallbackUrlChange={form.setCallbackUrl}
            t={t}
          />
        </ResponsiveDialogBody>

        <ResponsiveDialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("common.cancel")}
          </Button>
          <Button
            onClick={() => form.submit(configValues)}
            disabled={
              form.loading ||
              !form.name.trim() ||
              !form.promptTemplate.trim() ||
              !form.selectedAgentSlug
            }
          >
            {form.loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {form.isEdit ? t("common.save") : t("loops.createLoop")}
          </Button>
        </ResponsiveDialogFooter>
      </ResponsiveDialogContent>
    </ResponsiveDialog>
  );
}
