import type { CredentialFormSpec } from "./types";

// AgentFile source: backend/migrations/000127_add_e2e_echo_agent.up.sql
// Internal stub for MCP and EnvBundle e2e tests — no LLM, no production
// credentials. Exposes a sample test field + `allowCustomEnv` so e2e specs
// can drive the Settings credential dialog for this agent and seed
// arbitrary KV pairs as a credential bundle (verified end-to-end by
// reading the pod's stdout — see tests/scenarios/env-bundle-end-to-end).
export const e2eEchoFormSpec: CredentialFormSpec = {
  agentSlug: "e2e-echo",
  fields: [
    {
      kind: "secret",
      envKey: "E2E_TEST_CRED_KEY",
      label: "E2E Test Credential Key",
      description: "Internal stub — used only by EnvBundle end-to-end tests.",
      placeholder: "Test value (not a real credential)",
    },
  ],
  allowCustomEnv: true,
  customEnvHint: "Internal stub agent — values are echoed by the test pod.",
};
