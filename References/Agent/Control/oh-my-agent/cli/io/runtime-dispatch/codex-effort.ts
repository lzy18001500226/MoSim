import fs from "node:fs";
import path from "node:path";
import type { EffortLevel } from "../../platform/model-registry.js";
import {
  parseCodexConfig,
  serializeCodexConfig,
  setCodexReasoningEffort,
} from "../../vendors/codex/settings.js";

/**
 * Write plan.effort to the project-local .codex/config.toml.
 * Idempotent: no-op when effort already matches or no effort is set.
 * Silently skips on I/O errors (non-fatal).
 */
export function persistCodexEffortToToml(
  cwd: string,
  effort: EffortLevel,
): void {
  const codexConfigPath = path.join(cwd, ".codex", "config.toml");
  try {
    const rawToml = fs.existsSync(codexConfigPath)
      ? fs.readFileSync(codexConfigPath, "utf-8")
      : "";
    const current = parseCodexConfig(rawToml);
    if (current.model_reasoning_effort === effort) return;
    const next = setCodexReasoningEffort(current, effort);
    fs.mkdirSync(path.dirname(codexConfigPath), { recursive: true });
    fs.writeFileSync(codexConfigPath, `${serializeCodexConfig(next)}\n`);
  } catch {
    console.warn(
      `[runtime-dispatch] Failed to write .codex/config.toml — effort '${effort}' not persisted`,
    );
  }
}
