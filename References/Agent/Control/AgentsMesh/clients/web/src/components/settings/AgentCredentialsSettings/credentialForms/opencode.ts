import type { CredentialFormSpec } from "./types";

// AgentFile source: backend/migrations/000088_add_agentfile_source.up.sql
// (no ENV declarations — opencode relies on its own config files)
// Custom ENV remains available for users who need provider keys.
export const opencodeFormSpec: CredentialFormSpec = {
  agentSlug: "opencode",
  fields: [],
  allowCustomEnv: true,
  customEnvHint: "settings.credentialForm.opencode.customEnvHint",
};
