import type { CredentialFormSpec, CredentialFieldSpec } from "./types";
import { claudeCodeFormSpec } from "./claude-code";
import { codexCliFormSpec } from "./codex-cli";
import { loopalFormSpec } from "./loopal";
import { geminiCliFormSpec } from "./gemini-cli";
import { aiderFormSpec } from "./aider";
import { opencodeFormSpec } from "./opencode";

const REGISTRY: Record<string, CredentialFormSpec> = {
  [claudeCodeFormSpec.agentSlug]: claudeCodeFormSpec,
  [codexCliFormSpec.agentSlug]: codexCliFormSpec,
  [loopalFormSpec.agentSlug]: loopalFormSpec,
  [geminiCliFormSpec.agentSlug]: geminiCliFormSpec,
  [aiderFormSpec.agentSlug]: aiderFormSpec,
  [opencodeFormSpec.agentSlug]: opencodeFormSpec,
};

// e2e-echo is a test-only agent (see deploy/dev/seed/e2e_echo.sql). The
// `NEXT_PUBLIC_E2E` build-time flag is inlined as the literal "" in
// production builds (see clients/web/next.config.ts → env) so this entire
// branch — including the `require` call — is dead-code-eliminated by
// webpack. The form spec never enters the prod bundle.
if (process.env.NEXT_PUBLIC_E2E === "true") {
  // eslint-disable-next-line @typescript-eslint/no-require-imports, no-restricted-imports
  const { e2eEchoFormSpec } = require("./e2e-echo") as typeof import("./e2e-echo");
  REGISTRY[e2eEchoFormSpec.agentSlug] = e2eEchoFormSpec;
}

// Unknown / user-defined agents fall back to a pure custom-ENV form.
function makeFallback(agentSlug: string): CredentialFormSpec {
  return { agentSlug, fields: [], allowCustomEnv: true };
}

export function getCredentialFormSpec(agentSlug: string): CredentialFormSpec {
  return REGISTRY[agentSlug] ?? makeFallback(agentSlug);
}

export function getEnvKeysFromSpec(spec: CredentialFormSpec): Set<string> {
  const keys = new Set<string>();
  for (const field of spec.fields) {
    if (field.kind === "oneof") {
      for (const opt of field.options) keys.add(opt.envKey);
    } else {
      keys.add(field.envKey);
    }
  }
  return keys;
}

export function findFieldByEnvKey(
  spec: CredentialFormSpec,
  envKey: string
): CredentialFieldSpec | undefined {
  for (const field of spec.fields) {
    if (field.kind === "oneof") {
      if (field.options.some((o) => o.envKey === envKey)) return field;
    } else if (field.envKey === envKey) {
      return field;
    }
  }
  return undefined;
}

// Resolve display label for an ENV key (used by "configured fields" summaries).
// Falls back to the raw ENV name when the key isn't part of the spec.
export function getEnvKeyLabel(
  agentSlug: string,
  envKey: string,
  t: (key: string) => string
): string {
  const spec = getCredentialFormSpec(agentSlug);
  for (const field of spec.fields) {
    if (field.kind === "oneof") {
      const opt = field.options.find((o) => o.envKey === envKey);
      if (opt) {
        const translated = t(opt.label);
        return translated === opt.label ? envKey : translated;
      }
    } else if (field.envKey === envKey) {
      const translated = t(field.label);
      return translated === field.label ? envKey : translated;
    }
  }
  return envKey;
}

export type { CredentialFormSpec, CredentialFieldSpec, CustomEnvEntry } from "./types";
