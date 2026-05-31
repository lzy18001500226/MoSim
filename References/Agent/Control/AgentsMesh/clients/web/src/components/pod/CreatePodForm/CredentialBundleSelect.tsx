"use client";

import { Key, Star } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import type { EnvBundleSummary } from "@/lib/api";

interface Props {
  bundles: EnvBundleSummary[];
  selectedBundleName: string;
  onSelect: (name: string) => void;
  loading?: boolean;
  t: (key: string) => string;
}

/**
 * Single-select picker for credential-kind EnvBundles.
 *
 * Always offers "use Agent default authentication" as the first option
 * (empty string value) so users can deliberately opt out of bundle
 * injection — same semantics as the per-agent Settings page.
 *
 * Caller must filter `bundles` to `kind === 'credential'`.
 */
export function CredentialBundleSelect({
  bundles,
  selectedBundleName,
  onSelect,
  loading,
  t,
}: Props) {
  if (loading) {
    return (
      <div>
        <label className="block text-sm font-medium mb-2">
          {t("ide.createPod.selectCredential")}
        </label>
        <div className="flex items-center text-sm text-muted-foreground py-2">
          <Spinner size="sm" className="mr-2" />
          {t("common.loading")}
        </div>
      </div>
    );
  }

  return (
    <div>
      <label
        htmlFor="credential-bundle-select"
        className="block text-sm font-medium mb-2"
      >
        {t("ide.createPod.selectCredential")}
      </label>
      <select
        id="credential-bundle-select"
        className="w-full px-3 py-2 rounded-md border border-border bg-background text-sm"
        value={selectedBundleName}
        onChange={(e) => onSelect(e.target.value)}
      >
        <option value="">
          {t("ide.createPod.useAgentDefaultAuth")}
        </option>
        {bundles.map((b) => (
          <option key={b.id} value={b.name}>
            {b.name}
            {b.kind_primary ? ` (${t("settings.agentCredentials.default")})` : ""}
          </option>
        ))}
      </select>
      <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
        {selectedBundleName ? (
          <>
            <Key className="w-3 h-3 shrink-0" />
            {t("ide.createPod.credentialSelectedHint")}
          </>
        ) : (
          <>
            {bundles.some((b) => b.kind_primary) && (
              <Star className="w-3 h-3 shrink-0 text-primary" />
            )}
            {t("ide.createPod.noCredentialHint")}
          </>
        )}
      </p>
    </div>
  );
}

export default CredentialBundleSelect;
