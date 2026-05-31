"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
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
import { CredentialFormFields } from "../CredentialFormFields";
import { hasInvalidCustomEnvKey } from "../CustomEnvSection";
import {
  getCredentialFormSpec,
  getEnvKeysFromSpec,
} from "./credentialForms";
import {
  initFormStateFromProfile,
  buildCredentialsPayload,
  type CredentialFormState,
} from "./credentialForms/formState";
import type { CredentialProfileDialogProps } from "./types";

export function CredentialProfileDialog({
  open,
  onOpenChange,
  agentSlug,
  editingProfile,
  onSubmit,
  t,
}: CredentialProfileDialogProps) {
  const spec = useMemo(() => getCredentialFormSpec(agentSlug), [agentSlug]);
  const declaredKeys = useMemo(() => getEnvKeysFromSpec(spec), [spec]);

  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formState, setFormState] = useState<CredentialFormState>(() =>
    initFormStateFromProfile(spec, null)
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setFormName(editingProfile?.name ?? "");
    setFormDescription(editingProfile?.description ?? "");
    setFormState(initFormStateFromProfile(spec, editingProfile));
    setError(null);
  }, [open, editingProfile, spec]);

  const onValueChange = useCallback((envKey: string, value: string) => {
    setFormState((prev) => ({ ...prev, values: { ...prev.values, [envKey]: value } }));
  }, []);

  const onOneOfChange = useCallback((group: string, envKey: string) => {
    setFormState((prev) => ({
      ...prev,
      selectedOneOf: { ...prev.selectedOneOf, [group]: envKey },
    }));
  }, []);

  const onCustomEnvChange = useCallback((entries: CredentialFormState["customEnv"]) => {
    setFormState((prev) => ({ ...prev, customEnv: entries }));
  }, []);

  const customEnvInvalid = hasInvalidCustomEnvKey(formState.customEnv, declaredKeys);

  const handleSubmit = async () => {
    if (!formName.trim() || customEnvInvalid) return;
    try {
      setSubmitting(true);
      setError(null);
      const credentials = buildCredentialsPayload(spec, formState);
      await onSubmit({ name: formName, description: formDescription, credentials });
      onOpenChange(false);
    } catch (err) {
      console.error("Failed to save profile:", err);
      setError(t("settings.agentCredentials.failedToSave"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>
            {editingProfile
              ? t("settings.agentCredentials.editProfile")
              : t("settings.agentCredentials.addProfile")}
          </DialogTitle>
          <DialogDescription>
            {t("settings.agentCredentials.customProfileDescription")}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 px-6 py-4">
          {error && <div className="text-sm text-destructive">{error}</div>}

          <div className="grid gap-2">
            <Label htmlFor="cred-name">{t("settings.agentCredentials.name")}</Label>
            <Input
              id="cred-name"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder={t("settings.agentCredentials.namePlaceholder")}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="cred-desc">{t("settings.agentCredentials.descriptionLabel")}</Label>
            <Textarea
              id="cred-desc"
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              placeholder={t("settings.agentCredentials.descriptionPlaceholder")}
              rows={2}
            />
          </div>

          <CredentialFormFields
            spec={spec}
            values={formState.values}
            onValueChange={onValueChange}
            selectedOneOf={formState.selectedOneOf}
            onOneOfChange={onOneOfChange}
            customEnv={formState.customEnv}
            onCustomEnvChange={onCustomEnvChange}
            isEditing={!!editingProfile}
            t={t}
          />
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("common.cancel")}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={submitting || !formName.trim() || customEnvInvalid}
          >
            {submitting
              ? t("common.saving")
              : editingProfile
                ? t("common.save")
                : t("common.create")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default CredentialProfileDialog;
