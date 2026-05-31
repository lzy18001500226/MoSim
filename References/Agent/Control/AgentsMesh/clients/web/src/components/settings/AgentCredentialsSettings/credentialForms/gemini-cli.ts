import type { CredentialFormSpec } from "./types";

// AgentFile source: backend/migrations/000088_add_agentfile_source.up.sql
//   ENV GOOGLE_API_KEY SECRET OPTIONAL
export const geminiCliFormSpec: CredentialFormSpec = {
  agentSlug: "gemini-cli",
  fields: [
    {
      kind: "secret",
      envKey: "GOOGLE_API_KEY",
      label: "settings.credentialForm.google.apiKey",
    },
  ],
  allowCustomEnv: true,
  customEnvHint: "settings.credentialForm.gemini.customEnvHint",
};
