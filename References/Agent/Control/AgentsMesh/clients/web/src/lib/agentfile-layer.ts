/**
 * Utilities for generating AgentFile Layer source from form fields.
 * An AgentFile Layer is a DSL fragment that configures a Pod's environment.
 */

import { POD_MODE_PTY } from "@/lib/pod-modes";

/**
 * Escape a string for use in an AgentFile quoted value.
 * Must align with backend FormatStringLiteral (agentfile/format.go).
 */
function escapeAgentfileString(s: string): string {
  return s
    .replace(/\\/g, "\\\\")
    .replace(/"/g, '\\"')
    .replace(/\n/g, "\\n")
    .replace(/\t/g, "\\t");
}

/**
 * Escape and quote a string value for AgentFile syntax.
 * Must align with backend FormatStringLiteral (agentfile/format.go).
 */
function formatAgentfileValue(value: unknown): string {
  if (typeof value === "string") return `"${escapeAgentfileString(value)}"`;
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return String(value);
  return `"${escapeAgentfileString(String(value))}"`;
}

/**
 * Build an AgentFile Layer source string from structured form parameters.
 * Each non-empty field is emitted as an AgentFile declaration line.
 */
export function buildAgentfileLayer(params: {
  configValues: Record<string, unknown>;
  repositorySlug?: string;
  branchName?: string;
  interactionMode?: string;
  /**
   * Credential bundle name (kind='credential') to attach. Emitted FIRST in
   * the USE_ENV_BUNDLE sequence so runtime preferences listed after can
   * override credential defaults on conflicting keys.
   * Empty string / undefined = no credential injection (Agent uses its own
   * default auth: OAuth, CLI login, etc.).
   */
  credentialBundleName?: string;
  /**
   * Runtime bundle names (kind='runtime') to attach. Emitted AFTER the
   * credential line, in array order. Later entries override earlier ones
   * on conflicting env keys (mirrors backend eval order).
   */
  runtimeBundleNames?: string[];
  prompt?: string;
}): string {
  const lines: string[] = [];

  // MODE declaration (if not default PTY)
  if (params.interactionMode && params.interactionMode !== POD_MODE_PTY) {
    lines.push(`MODE ${params.interactionMode}`);
  }

  // USE_ENV_BUNDLE declarations — credential first, then runtime bundles
  // in selection order. Backend's eval merges each bundle's KV into the
  // Pod's env in declaration order; later wins on conflicts.
  const bundleNames: string[] = [];
  if (params.credentialBundleName) {
    bundleNames.push(params.credentialBundleName);
  }
  if (params.runtimeBundleNames) {
    for (const name of params.runtimeBundleNames) {
      if (name) bundleNames.push(name);
    }
  }
  for (const name of bundleNames) {
    lines.push(`USE_ENV_BUNDLE "${escapeAgentfileString(name)}"`);
  }

  // PROMPT declaration (prompt content)
  if (params.prompt) {
    lines.push(`PROMPT "${escapeAgentfileString(params.prompt)}"`);
  }

  // CONFIG declarations
  for (const [key, value] of Object.entries(params.configValues)) {
    if (value !== undefined && value !== null && value !== "") {
      lines.push(`CONFIG ${key} = ${formatAgentfileValue(value)}`);
    }
  }

  // Repository slug / branch
  if (params.repositorySlug) {
    lines.push(`REPO "${params.repositorySlug}"`);
  }
  if (params.branchName) {
    lines.push(`BRANCH "${params.branchName}"`);
  }

  return lines.join("\n");
}
