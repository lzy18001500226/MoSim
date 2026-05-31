"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CustomEnvSection, hasInvalidCustomEnvKey } from "../CustomEnvSection";
import type { CustomEnvEntry } from "../AgentCredentialsSettings/credentialForms/types";
import type { RuntimeBundleViewModel, RuntimeBundleFormData } from "./types";

/**
 * Empty Set — runtime bundles have no declared schema, so CustomEnvSection's
 * conflict-with-declared check is a no-op. Hoisted to avoid a fresh allocation
 * (and therefore a CustomEnvSection re-render) on every parent re-render.
 */
const EMPTY_DECLARED_KEYS = new Set<string>();

function newEntryId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editingBundle: RuntimeBundleViewModel | null;
  onSubmit: (
    data: RuntimeBundleFormData,
    editingBundle: RuntimeBundleViewModel | null
  ) => Promise<void>;
  t: (key: string) => string;
}

/**
 * RuntimeBundleDialog — create/edit a runtime-kind EnvBundle.
 *
 * Runtime bundles hold non-secret preferences (e.g. `OPENAI_MODEL=gpt-4`,
 * `LOG_LEVEL=debug`). The backend stores values in plaintext and echoes them
 * back, so the form pre-fills from `configured_values` on edit and renders
 * KV pairs in a `text` input (not the masked password input the credential
 * dialog uses).
 */
export function RuntimeBundleDialog({
  open,
  onOpenChange,
  editingBundle,
  onSubmit,
  t,
}: Props) {
  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [entries, setEntries] = useState<CustomEnvEntry[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setFormName(editingBundle?.name ?? "");
    setFormDescription(editingBundle?.description ?? "");
    const initial = editingBundle?.configured_values
      ? Object.entries(editingBundle.configured_values).map(([key, value]) => ({
          id: newEntryId(),
          key,
          value,
        }))
      : [{ id: newEntryId(), key: "", value: "" }];
    setEntries(initial);
    setError(null);
  }, [open, editingBundle]);

  const onEntriesChange = useCallback(
    (next: CustomEnvEntry[]) => setEntries(next),
    []
  );

  const invalid = hasInvalidCustomEnvKey(entries, EMPTY_DECLARED_KEYS);

  const handleSubmit = async () => {
    if (!formName.trim() || invalid) return;
    try {
      setSubmitting(true);
      setError(null);
      const data: Record<string, string> = {};
      for (const e of entries) {
        const k = e.key.trim();
        if (k) data[k] = e.value;
      }
      await onSubmit(
        { name: formName, description: formDescription, data },
        editingBundle
      );
      onOpenChange(false);
    } catch (err) {
      console.error("Failed to save runtime bundle:", err);
      setError(t("settings.agentConfig.runtimeBundles.saveFailed"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>
            {editingBundle
              ? t("settings.agentConfig.runtimeBundles.editTitle")
              : t("settings.agentConfig.runtimeBundles.addTitle")}
          </DialogTitle>
          <DialogDescription>
            {t("settings.agentConfig.runtimeBundles.formDescription")}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 px-6 py-4">
          {error && <div className="text-sm text-destructive">{error}</div>}

          <div className="grid gap-2">
            <Label htmlFor="runtime-name">
              {t("settings.agentConfig.runtimeBundles.name")}
            </Label>
            <Input
              id="runtime-name"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder={t(
                "settings.agentConfig.runtimeBundles.namePlaceholder"
              )}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="runtime-desc">
              {t("settings.agentConfig.runtimeBundles.descriptionLabel")}
            </Label>
            <Textarea
              id="runtime-desc"
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              placeholder={t(
                "settings.agentConfig.runtimeBundles.descriptionPlaceholder"
              )}
              rows={2}
            />
          </div>

          <CustomEnvSection
            title={t("settings.agentConfig.runtimeBundles.envTitle")}
            hint={t("settings.agentConfig.runtimeBundles.envHint")}
            entries={entries}
            declaredKeys={EMPTY_DECLARED_KEYS}
            onChange={onEntriesChange}
            isEditing={!!editingBundle}
            t={t}
            valueType="text"
          />
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("common.cancel")}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={submitting || !formName.trim() || invalid}
          >
            {submitting
              ? t("common.saving")
              : editingBundle
                ? t("common.save")
                : t("common.create")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default RuntimeBundleDialog;
