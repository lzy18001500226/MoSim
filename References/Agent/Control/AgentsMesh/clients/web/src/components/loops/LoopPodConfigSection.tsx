"use client";

import { RunnerSelect } from "@/components/pod/CreatePodForm/RunnerSelect";
import { CredentialBundleSelect } from "@/components/pod/CreatePodForm/CredentialBundleSelect";
import { EnvBundleMultiSelect } from "@/components/pod/CreatePodForm/EnvBundleMultiSelect";
import { RepositorySelect, BranchInput } from "@/components/pod/CreatePodForm/RepositorySelect";
import { AdvancedOptions } from "@/components/pod/CreatePodForm/AdvancedOptions";
import { ConfigForm } from "@/components/ide/ConfigForm";
import { Spinner } from "@/components/ui/spinner";
import type { ConfigField, EnvBundleSummary, RepositoryData, RunnerData } from "@/lib/api";

/**
 * LoopPodConfigSection — the "Pod runtime" half of the create dialog,
 * wrapped in an AdvancedOptions disclosure. Reuses Pod-creation primitives
 * so a Loop's Pods configure identically to ad-hoc Pods.
 *
 * EnvBundle picker is split into two:
 *   - Credential (single-select): kind='credential' bundles, plus "use default".
 *   - Runtime (multi-select): kind='runtime' bundles, ordered.
 *
 * Stateless: parent owns selection state and passes setters.
 */
interface LoopPodConfigSectionProps {
  agentSlug: string;
  runners: RunnerData[];
  repositories: RepositoryData[];
  envBundles: EnvBundleSummary[];
  configFields: ConfigField[];
  configValues: Record<string, unknown>;
  loadingConfig: boolean;
  loadingBundles: boolean;

  selectedRunnerId: number | null;
  onSelectRunner: (id: number | null) => void;

  selectedCredentialName: string;
  onSelectCredential: (name: string) => void;

  selectedRuntimeBundleNames: string[];
  onSelectRuntimeBundles: (names: string[]) => void;

  selectedRepositoryId: number | null;
  onSelectRepository: (id: number | null) => void;

  selectedBranch: string;
  onChangeBranch: (branch: string) => void;

  onConfigChange: (key: string, value: unknown) => void;

  t: (key: string) => string;
}

export function LoopPodConfigSection({
  agentSlug,
  runners,
  repositories,
  envBundles,
  configFields,
  configValues,
  loadingConfig,
  loadingBundles,
  selectedRunnerId,
  onSelectRunner,
  selectedCredentialName,
  onSelectCredential,
  selectedRuntimeBundleNames,
  onSelectRuntimeBundles,
  selectedRepositoryId,
  onSelectRepository,
  selectedBranch,
  onChangeBranch,
  onConfigChange,
  t,
}: LoopPodConfigSectionProps) {
  return (
    <AdvancedOptions t={t}>
      <RunnerSelect
        runners={runners}
        selectedRunnerId={selectedRunnerId}
        onSelect={onSelectRunner}
        t={t}
      />

      <CredentialBundleSelect
        bundles={envBundles.filter((b) => b.kind === "credential")}
        selectedBundleName={selectedCredentialName}
        onSelect={onSelectCredential}
        loading={loadingBundles}
        t={t}
      />

      <EnvBundleMultiSelect
        bundles={envBundles.filter((b) => b.kind === "runtime")}
        selectedBundleNames={selectedRuntimeBundleNames}
        onChange={onSelectRuntimeBundles}
        loading={loadingBundles}
        t={t}
      />

      <RepositorySelect
        repositories={repositories}
        selectedRepositoryId={selectedRepositoryId}
        onSelect={onSelectRepository}
        t={t}
      />

      {selectedRepositoryId && (
        <BranchInput
          value={selectedBranch}
          onChange={onChangeBranch}
          t={t}
        />
      )}

      {loadingConfig ? (
        <div className="flex items-center justify-center py-4">
          <Spinner size="sm" className="mr-2" />
          <span className="text-sm text-muted-foreground">
            {t("ide.createPod.loadingPlugins")}
          </span>
        </div>
      ) : (
        configFields.length > 0 && (
          <div>
            <label className="block text-sm font-medium mb-2">
              {t("ide.createPod.pluginConfig")}
            </label>
            <ConfigForm
              fields={configFields}
              values={configValues}
              onChange={onConfigChange}
              agentSlug={agentSlug}
            />
          </div>
        )
      )}
    </AdvancedOptions>
  );
}
