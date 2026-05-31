"use client";

/**
 * AgentFile Layer editor with form/source mode toggle.
 * Form mode: read-only preview of generated Layer.
 * Source mode: CodeMirror 6 editor with syntax highlighting + autocomplete.
 */
import React, { useMemo } from "react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { AgentfileCodeEditor } from "./AgentfileCodeEditor";
import type { AgentfileCompletionContext } from "@/lib/codemirror-agentfile";
import type { ConfigField } from "@/lib/api";
import type { RepositoryData, AgentData, EnvBundleSummary } from "@/lib/api";

interface AgentfileLayerEditorProps {
  generatedLayer: string;
  rawMode: boolean;
  rawText: string;
  onRawModeChange: (enabled: boolean) => void;
  onRawTextChange: (text: string) => void;
  /** Agent config schema for CONFIG field/value completions */
  configFields?: ConfigField[];
  /** Available agents for AGENT keyword completions */
  agents?: AgentData[];
  /** Available repositories for REPO/BRANCH completions */
  repositories?: RepositoryData[];
  /** EnvBundles for USE_ENV_BUNDLE completions */
  envBundles?: EnvBundleSummary[];
  t: (key: string) => string;
}

export function AgentfileLayerEditor({
  generatedLayer,
  rawMode,
  rawText,
  onRawModeChange,
  onRawTextChange,
  configFields = [],
  agents,
  repositories,
  envBundles,
  t,
}: AgentfileLayerEditorProps) {
  // Build completion context from all available data sources
  const completionContext = useMemo<AgentfileCompletionContext>(() => ({
    configFields,
    agents: agents?.map((a) => ({ slug: a.slug, name: a.name })),
    repositories: repositories?.map((r) => ({
      slug: r.slug,
      name: r.name,
      default_branch: r.default_branch,
    })),
    envBundles: envBundles?.map((b) => ({
      name: b.name,
    })),
  }), [configFields, agents, repositories, envBundles]);

  return (
    <div className="space-y-2 border-t pt-3">
      {/* Toggle: Form Mode / Source Mode */}
      <div className="flex items-center justify-between">
        <Label className="text-sm">{t("ide.createPod.agentfileLayer")}</Label>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">
            {t("ide.createPod.sourceMode")}
          </span>
          <Switch checked={rawMode} onCheckedChange={onRawModeChange} />
        </div>
      </div>

      {/* Layer preview or CodeMirror editor */}
      {rawMode ? (
        <AgentfileCodeEditor
          value={rawText}
          onChange={onRawTextChange}
          completionContext={completionContext}
        />
      ) : (
        generatedLayer && (
          <pre className="bg-muted/50 rounded-md p-3 text-xs font-mono text-muted-foreground overflow-x-auto whitespace-pre-wrap">
            {generatedLayer}
          </pre>
        )
      )}
    </div>
  );
}
