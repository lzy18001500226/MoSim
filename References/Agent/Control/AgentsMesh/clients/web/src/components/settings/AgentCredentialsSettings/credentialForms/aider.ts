import type { CredentialFormSpec } from "./types";

// AgentFile source: backend/migrations/000088_add_agentfile_source.up.sql
//   ENV OPENAI_API_KEY SECRET OPTIONAL
//   ENV ANTHROPIC_API_KEY SECRET OPTIONAL
export const aiderFormSpec: CredentialFormSpec = {
  agentSlug: "aider",
  fields: [
    {
      kind: "secret",
      envKey: "OPENAI_API_KEY",
      label: "settings.credentialForm.openai.apiKey",
      placeholder: "sk-...",
    },
    {
      kind: "secret",
      envKey: "ANTHROPIC_API_KEY",
      label: "settings.credentialForm.anthropic.apiKey",
      placeholder: "sk-ant-...",
    },
  ],
  allowCustomEnv: true,
  customEnvHint: "settings.credentialForm.aider.customEnvHint",
};
