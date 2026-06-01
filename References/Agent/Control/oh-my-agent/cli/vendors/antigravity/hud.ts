/**
 * Antigravity CLI (agy) wiring. agy maintains HOME-only config at
 * `~/.gemini/antigravity-cli/settings.json` and supports Claude-style
 * hook events plus a native `StatusLine` field. `PreInvocation` is the
 * prompt-entry hook used for OMA workflow/skill/L1 state injection.
 *
 * This installer is parallel to (not part of) the project-scoped
 * `installHooksFromVariant` pipeline because:
 *   - paths resolve under $HOME, not the project root
 *   - hook commands must be absolute (agy doesn't expose a project-dir env)
 *   - the file shares space with `colorScheme`, `toolPermission`, etc., so
 *     we merge instead of overwrite
 */

import {
  cpSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { clearNonDirectory } from "../../utils/fs-utils.js";

const AGY_HOME_DIR = ".gemini/antigravity-cli";
const ANTIGRAVITY_VARIANT = ".agents/hooks/variants/antigravity.json";

interface HookRef {
  hook: string;
  matcher?: string;
  timeout: number;
}

interface AntigravityVariant {
  events: Record<string, HookRef | HookRef[]>;
  statusLine?: { hook: string };
}

interface AgySettings {
  // biome-ignore lint/suspicious/noExplicitAny: settings.json schema is dynamic
  [key: string]: any;
}

function agyPaths() {
  const home = homedir();
  const settingsPath = join(home, AGY_HOME_DIR, "settings.json");
  const hooksDir = join(home, AGY_HOME_DIR, "hooks");
  return { home, settingsPath, hooksDir };
}

function readAgySettings(settingsPath: string): AgySettings {
  if (!existsSync(settingsPath)) return {};
  try {
    return JSON.parse(readFileSync(settingsPath, "utf-8"));
  } catch {
    return {};
  }
}

function copyCoreHooks(sourceDir: string, hooksDir: string): void {
  const src = join(sourceDir, ".agents", "hooks", "core");
  if (!existsSync(src)) return;

  mkdirSync(hooksDir, { recursive: true });
  for (const entry of readdirSync(hooksDir, { withFileTypes: true })) {
    clearNonDirectory(join(hooksDir, entry.name));
  }
  cpSync(src, hooksDir, { recursive: true, force: true, dereference: true });
}

function readAntigravityVariant(sourceDir: string): AntigravityVariant {
  const path = join(sourceDir, ANTIGRAVITY_VARIANT);
  try {
    return JSON.parse(readFileSync(path, "utf-8")) as AntigravityVariant;
  } catch {
    return {
      events: {
        PreInvocation: [
          { hook: "keyword-detector.ts", timeout: 5 },
          { hook: "state-boundary.ts", timeout: 5 },
          { hook: "skill-injector.ts", timeout: 3 },
        ],
        PreToolUse: { hook: "test-filter.ts", matcher: "Bash", timeout: 5 },
        Stop: { hook: "persistent-mode.ts", timeout: 5 },
      },
      statusLine: { hook: "hud.ts" },
    };
  }
}

function hookName(hook: string): string {
  return hook.replace(/\.[^.]+$/, "");
}

function hookHandler(hooksDir: string, ref: HookRef): Record<string, unknown> {
  return {
    name: hookName(ref.hook),
    type: "command",
    command: `bun "${join(hooksDir, ref.hook)}"`,
    timeout: ref.timeout,
  };
}

function buildAgyHookEntries(
  hooksDir: string,
  variant: AntigravityVariant,
): Record<string, unknown> {
  const entries: Record<string, unknown> = {};
  for (const [eventName, rawConfig] of Object.entries(variant.events)) {
    const configs = Array.isArray(rawConfig) ? rawConfig : [rawConfig];
    const hooks = configs.map((config) => hookHandler(hooksDir, config));

    if (eventName === "PreInvocation" || eventName === "PostInvocation") {
      entries[eventName] = hooks;
      continue;
    }

    if (eventName === "Stop") {
      entries[eventName] = hooks;
      continue;
    }

    const matcher = configs.find((config) => config.matcher)?.matcher;
    entries[eventName] = [{ ...(matcher ? { matcher } : {}), hooks }];
  }
  return entries;
}

interface AgyInstallResult {
  installed: boolean;
  reason?: string;
  settingsPath?: string;
  hooksDir?: string;
}

/**
 * Install the OMA HUD (and supporting Claude-style hooks) into agy's HOME
 * config. Idempotent — running twice produces the same settings.json. Other
 * keys (colorScheme, toolPermission, trustedWorkspaces, ...) are preserved.
 *
 * Returns `installed: false` with a `reason` when agy's config dir doesn't
 * exist, which signals "agy not installed / never run" — we don't bootstrap
 * the dir ourselves because we'd risk masking an install bug.
 */
export function installAntigravityHud(sourceDir: string): AgyInstallResult {
  const { settingsPath, hooksDir } = agyPaths();
  const agyConfigDir = join(homedir(), AGY_HOME_DIR);

  if (!existsSync(agyConfigDir)) {
    return {
      installed: false,
      reason: `agy config dir not found at ~/${AGY_HOME_DIR} — run agy once to initialize`,
    };
  }

  copyCoreHooks(sourceDir, hooksDir);

  const settings = readAgySettings(settingsPath);
  const variant = readAntigravityVariant(sourceDir);
  const statusLineHook = variant.statusLine?.hook ?? "hud.ts";

  settings.statusLine = {
    type: "command",
    command: `bun "${join(hooksDir, statusLineHook)}"`,
  };

  const existingHooks =
    settings.hooks && typeof settings.hooks === "object" ? settings.hooks : {};

  settings.hooks = {
    ...existingHooks,
    ...buildAgyHookEntries(hooksDir, variant),
  };

  mkdirSync(join(homedir(), AGY_HOME_DIR), { recursive: true });
  writeFileSync(settingsPath, `${JSON.stringify(settings, null, 2)}\n`);

  return { installed: true, settingsPath, hooksDir };
}
