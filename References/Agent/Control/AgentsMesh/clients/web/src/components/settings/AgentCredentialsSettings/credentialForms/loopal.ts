import type { CredentialFormSpec } from "./types";

// AgentFile source: backend/migrations/000122_add_loopal_agent.up.sql
//   ENV ANTHROPIC_API_KEY SECRET OPTIONAL
//   ENV OPENAI_API_KEY SECRET OPTIONAL
//   ENV GOOGLE_API_KEY SECRET OPTIONAL
export const loopalFormSpec: CredentialFormSpec = {
  agentSlug: "loopal",
  fields: [
    {
      kind: "secret",
      envKey: "ANTHROPIC_API_KEY",
      label: "settings.credentialForm.anthropic.apiKey",
      placeholder: "sk-ant-...",
    },
    {
      kind: "secret",
      envKey: "OPENAI_API_KEY",
      label: "settings.credentialForm.openai.apiKey",
      placeholder: "sk-...",
    },
    {
      kind: "secret",
      envKey: "GOOGLE_API_KEY",
      label: "settings.credentialForm.google.apiKey",
    },
  ],
  allowCustomEnv: true,
  customEnvHint: "settings.credentialForm.loopal.customEnvHint",
};
