"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import { ConfirmDialog, useConfirmDialog } from "@/components/ui/confirm-dialog";
import { updateOrg, deleteOrg } from "@/lib/api/facade/org";
import { getLocalizedErrorMessage } from "@/lib/api/errors";
import { useCurrentOrg, useAuthOrganizations, useAuthStore } from "@/stores/auth";
import { toast } from "sonner";

export type TranslationFn = (key: string, params?: Record<string, string | number>) => string;

interface GeneralSettingsProps {
  org: { name: string; slug: string } | null;
  t: TranslationFn;
}

export function GeneralSettings({ org, t }: GeneralSettingsProps) {
  const [name, setName] = useState(org?.name || "");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  useEffect(() => { if (org?.name && !name) setName(org.name); }, [org?.name]);
  const currentOrg = useCurrentOrg();
  const organizations = useAuthOrganizations();
  const setCurrentOrg = useAuthStore((s) => s.setCurrentOrg);
  const setOrganizations = useAuthStore((s) => s.setOrganizations);

  const deleteOrgDialog = useConfirmDialog({
    title: t("settings.dangerZone.title"),
    description: t("settings.dangerZone.description"),
    confirmText: t("settings.dangerZone.deleteOrg"),
    variant: "destructive",
  });

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateOrg(org!.slug, { name });

      if (currentOrg && currentOrg.slug === org!.slug) {
        setCurrentOrg({ ...currentOrg, name });
      }
      setOrganizations(
        organizations.map((o) =>
          o.slug === org!.slug ? { ...o, name } : o
        )
      );

      toast.success(t("settings.organizationDetails.saveSuccess") || "Saved");
    } catch (error) {
      console.error("Failed to save:", error);
      toast.error(getLocalizedErrorMessage(error, t, t("settings.organizationDetails.saveFailed") || "Failed to save"));
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteOrg = async () => {
    const confirmed = await deleteOrgDialog.confirm();
    if (!confirmed) return;

    setDeleting(true);
    try {
      await deleteOrg(org!.slug);

      const remaining = organizations.filter((o) => o.slug !== org!.slug);
      // Hard nav (window.location.assign) instead of router.push: when
      // setOrganizations writes the updated SSOT slice, OrgLayout's effect
      // detects "current URL slug no longer in orgs" and fires its own
      // `router.replace` — racing this handler's soft navigation. The two
      // competing Next.js client navigations abort each other, freezing
      // the URL on the deleted org's settings page (test flake source).
      // Switching orgs already reinits wasm + Connect streams, so a full
      // reload costs nothing extra and removes the race.
      const target = remaining.length > 0 ? `/${remaining[0].slug}/workspace` : "/";
      await setOrganizations(remaining);
      if (remaining.length > 0) {
        await setCurrentOrg(remaining[0]);
      }
      toast.success(t("settings.dangerZone.deleteSuccess") || "Organization deleted");
      window.location.assign(target);
    } catch (error) {
      console.error("Failed to delete organization:", error);
      toast.error(getLocalizedErrorMessage(error, t, t("settings.dangerZone.deleteFailed") || "Failed to delete"));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border border-border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">{t("settings.organizationDetails.title")}</h2>
        <div className="space-y-4">
          <FormField
            label={t("settings.organizationDetails.nameLabel")}
            htmlFor="org-name"
          >
            <Input
              id="org-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t("settings.organizationDetails.namePlaceholder")}
            />
          </FormField>

          <FormField
            label={t("settings.organizationDetails.slugLabel")}
            htmlFor="org-slug"
            hint={t("settings.organizationDetails.slugHint")}
          >
            <Input id="org-slug" value={org?.slug || ""} disabled />
          </FormField>
        </div>
        <div className="mt-6">
          <Button onClick={handleSave} disabled={saving}>
            {saving ? t("settings.organizationDetails.saving") : t("settings.organizationDetails.saveChanges")}
          </Button>
        </div>
      </div>

      <div className="border border-destructive rounded-lg p-6">
        <h2 className="text-lg font-semibold text-destructive mb-4">
          {t("settings.dangerZone.title")}
        </h2>
        <p className="text-sm text-muted-foreground mb-4">
          {t("settings.dangerZone.description")}
        </p>
        <Button variant="destructive" onClick={handleDeleteOrg} disabled={deleting}>
          {deleting ? t("settings.dangerZone.deleting") || "Deleting..." : t("settings.dangerZone.deleteOrg")}
        </Button>
      </div>

      <ConfirmDialog {...deleteOrgDialog.dialogProps} />
    </div>
  );
}
