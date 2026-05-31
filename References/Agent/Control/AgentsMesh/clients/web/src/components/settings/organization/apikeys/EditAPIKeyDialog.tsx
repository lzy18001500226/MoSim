"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { ScopeSelector } from "./ScopeSelector";
import type { ApiKey } from "@/lib/api/facade/apikey";
import type { TranslationFn } from "../GeneralSettings";

interface UpdateInput {
  name?: string;
  description?: string;
  scopes?: string[];
  isEnabled?: boolean;
}

interface EditAPIKeyDialogProps {
  apiKey: ApiKey;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (id: bigint, data: UpdateInput) => Promise<void>;
  t: TranslationFn;
}

export function EditAPIKeyDialog({ apiKey, open, onOpenChange, onSave, t }: EditAPIKeyDialogProps) {
  const [name, setName] = useState(apiKey.name);
  const [description, setDescription] = useState(apiKey.description || "");
  const [selectedScopes, setSelectedScopes] = useState<Set<string>>(
    new Set(apiKey.scopes)
  );
  const [isEnabled, setIsEnabled] = useState(apiKey.isEnabled);
  const [saving, setSaving] = useState(false);

  const toggleScope = (scope: string) => {
    const next = new Set(selectedScopes);
    if (next.has(scope)) {
      next.delete(scope);
    } else {
      next.add(scope);
    }
    setSelectedScopes(next);
  };

  const handleSave = async () => {
    if (!name.trim() || selectedScopes.size === 0) return;
    setSaving(true);
    try {
      await onSave(apiKey.id, {
        name: name.trim(),
        description: description.trim() || undefined,
        scopes: Array.from(selectedScopes),
        isEnabled,
      });
      onOpenChange(false);
    } catch (err) {
      console.error("Failed to update API key:", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("settings.apiKeys.editDialog.title")}</DialogTitle>
          <DialogDescription>
            <code className="bg-muted px-2 py-0.5 rounded text-xs">{apiKey.keyPrefix}...</code>
          </DialogDescription>
        </DialogHeader>

        <div className="px-6 py-4 space-y-4">
          <div>
            <label htmlFor="edit-apikey-name" className="block text-sm font-medium mb-2">
              {t("settings.apiKeys.createDialog.nameLabel")}
            </label>
            <Input
              id="edit-apikey-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="edit-apikey-description" className="block text-sm font-medium mb-2">
              {t("settings.apiKeys.createDialog.descriptionLabel")}
            </label>
            <Input
              id="edit-apikey-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              {t("settings.apiKeys.createDialog.scopesLabel")}
            </label>
            <ScopeSelector
              selectedScopes={selectedScopes}
              onToggle={toggleScope}
              t={t}
            />
          </div>

          <div className="flex items-center justify-between">
            <label htmlFor="edit-apikey-enabled" className="text-sm font-medium">
              {t("settings.apiKeys.enabled")}
            </label>
            <Switch
              id="edit-apikey-enabled"
              checked={isEnabled}
              onCheckedChange={setIsEnabled}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("settings.apiKeys.editDialog.cancel")}
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving || !name.trim() || selectedScopes.size === 0}
          >
            {saving ? t("settings.apiKeys.editDialog.saving") : t("settings.apiKeys.editDialog.save")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
