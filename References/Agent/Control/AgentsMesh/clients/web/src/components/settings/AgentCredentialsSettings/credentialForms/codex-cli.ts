import type { CredentialFormSpec } from "./types";

// AgentFile source: backend/migrations/000088_add_agentfile_source.up.sql
//   ENV OPENAI_API_KEY SECRET OPTIONAL
// allowCustomEnv enables proxy / model overrides (e.g. OPENAI_BASE_URL).
export const codexCliFormSpec: CredentialFormSpec = {
  agentSlug: "codex-cli",
  fields: [
    {
      kind: "secret",
      envKey: "OPENAI_API_KEY",
      label: "settings.credentialForm.openai.apiKey",
      placeholder: "sk-...",
    },
  ],
  allowCustomEnv: true,
  customEnvHint: "settings.credentialForm.codex.customEnvHint",
};
