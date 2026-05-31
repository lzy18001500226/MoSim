"use client";

import { Button } from "@/components/ui/button";
import { Sliders, Star, Check, Edit2, Trash2, Plus } from "lucide-react";
import type { RuntimeBundleViewModel } from "./types";

interface Props {
  bundles: RuntimeBundleViewModel[];
  onSetDefault: (id: number) => Promise<void>;
  onClearDefault: () => Promise<void>;
  onEdit: (b: RuntimeBundleViewModel) => void;
  onDelete: (id: number) => Promise<void>;
  onAdd: () => void;
  t: (key: string) => string;
}

/**
 * RuntimeBundlesSection — manages runtime-kind EnvBundles for one agent.
 *
 * Runtime bundles hold non-secret preferences (model overrides, log levels,
 * proxy hosts, etc.) the agent reads via env vars. Unlike credential
 * bundles there is no implicit "no bundle" fallback row — the list is
 * either empty (no runtime preferences attached) or shows each bundle's
 * configured KV preview in plaintext. `kind_primary` flags the bundle the
 * Pod-create dialog will pre-select.
 */
export function RuntimeBundlesSection({
  bundles,
  onSetDefault,
  onClearDefault,
  onEdit,
  onDelete,
  onAdd,
  t,
}: Props) {
  const hasDefault = bundles.some((b) => b.is_default);

  return (
    <div className="border border-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Sliders className="w-5 h-5 text-muted-foreground" />
        <h3 className="text-lg font-semibold">
          {t("settings.agentConfig.runtimeBundles.title")}
        </h3>
      </div>
      <p className="text-sm text-muted-foreground mb-4">
        {t("settings.agentConfig.runtimeBundles.description")}
      </p>

      <div className="space-y-2">
        {bundles.length === 0 && (
          <div className="text-sm text-muted-foreground py-2">
            {t("settings.agentConfig.runtimeBundles.empty")}
          </div>
        )}

        {bundles.map((b) => (
          <div
            key={b.id}
            className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted/50"
          >
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <Sliders className="w-4 h-4 text-muted-foreground shrink-0" />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium truncate">{b.name}</span>
                  {b.is_default && (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-primary/10 text-primary shrink-0">
                      <Star className="w-3 h-3 mr-0.5" />
                      {t("settings.agentCredentials.default")}
                    </span>
                  )}
                </div>
                {b.description && (
                  <div className="text-xs text-muted-foreground truncate">
                    {b.description}
                  </div>
                )}
                <div className="text-xs text-muted-foreground font-mono mt-0.5 truncate">
                  {b.configured_values && Object.keys(b.configured_values).length > 0
                    ? Object.entries(b.configured_values)
                        .map(([k, v]) => `${k}=${v}`)
                        .join("  ")
                    : t("settings.agentConfig.runtimeBundles.noEnv")}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              {!b.is_default && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onSetDefault(b.id)}
                  title={t("settings.agentCredentials.setAsDefault")}
                >
                  <Check className="w-4 h-4" />
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(b)}
              >
                <Edit2 className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(b.id)}
                className="text-destructive hover:text-destructive"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        ))}

        <div className="flex items-center gap-2 mt-2">
          <Button variant="outline" size="sm" onClick={onAdd}>
            <Plus className="w-4 h-4 mr-1" />
            {t("settings.agentConfig.runtimeBundles.add")}
          </Button>
          {hasDefault && (
            <Button variant="ghost" size="sm" onClick={onClearDefault}>
              {t("settings.agentConfig.runtimeBundles.clearDefault")}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

export default RuntimeBundlesSection;
