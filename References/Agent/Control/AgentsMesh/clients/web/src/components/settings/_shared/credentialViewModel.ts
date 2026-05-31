/**
 * Settings-shared ViewModel for the per-agent credentials UI. Adapts the
 * generic `EnvBundle` wire type (kind=credential) into a per-agent grouped
 * shape that the two settings sub-pages (AgentCredentialsSettings and
 * AgentConfigPage) already speak. Lives in `settings/_shared/` rather than
 * in `@/lib/api` because nothing outside the settings tree should think in
 * terms of "credential profiles" anymore — Pod creation and Loop binding
 * both consume `EnvBundle` directly.
 */
export interface CredentialProfileViewModel {
  id: number;
  agent_slug: string;
  name: string;
  description?: string;
  is_default: boolean;
  is_active: boolean;
  configured_fields?: string[];
  configured_values?: Record<string, string>;
  agent_name?: string;
  created_at: string;
  updated_at: string;
}

export interface CredentialProfilesByAgent {
  agent_slug: string;
  agent_name: string;
  profiles: CredentialProfileViewModel[];
}

export function getProfileStatusLabel(profile: CredentialProfileViewModel): string {
  if (profile.configured_fields && profile.configured_fields.length > 0) {
    return "Configured";
  }
  return "Not configured";
}
