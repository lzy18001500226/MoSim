import type { CliTool, CliVendor } from "../types/index.js";

export const REPO = "first-fluke/oh-my-agent";
export const INSTALLED_SKILLS_DIR = ".agents/skills";

/**
 * Canonical vendor set: host LLM CLIs that have both a type identity and a
 * hook-detection identity in this codebase. Single source of truth consumed
 * by validators, registries, doc-merging loops in cli/, and the derived
 * `VendorType` in `cli/types/vendors.ts`. NOTE: cursor is included here
 * because it has hook detection, rules generation, and CLI binary identity,
 * even though it lacks a full runtime adapter under `cli/vendors/cursor/`.
 * Sites that require a fully implemented runtime (doctor probe, agent
 * review, native dispatch) keep their own narrower lists.
 */
export const VENDORS = [
  "antigravity",
  "claude",
  "codex",
  "cursor",
  "gemini",
  "qwen",
] as const;

/**
 * All CLI tools including non-hook vendors (skill-install only).
 * Derived from VENDORS plus the install-only targets, sorted alphabetically
 * for deterministic output where consumers iterate.
 */
export const ALL_CLI_VENDORS: CliVendor[] = [
  ...VENDORS,
  "copilot",
  "hermes",
].sort() as CliVendor[];

export interface SkillTargetSpec {
  /** Relative path under the install root when mode === "project". */
  projectPath: string;
  /** Relative path under the install root when mode === "global". */
  homePath: string;
  /**
   * When true, this vendor writes outside the project directory even in
   * project mode (HOME-base). Callers must obtain explicit user consent
   * before proceeding. Today only `hermes` qualifies.
   */
  requiresHomeConsent?: boolean;
}

export const CLI_SKILLS_DIR: Record<CliTool, SkillTargetSpec> = {
  antigravity: {
    projectPath: ".gemini/antigravity-cli/skills",
    homePath: ".gemini/antigravity-cli/skills",
    requiresHomeConsent: true,
  },
  claude: { projectPath: ".claude/skills", homePath: ".claude/skills" },
  codex: { projectPath: ".codex/skills", homePath: ".codex/skills" },
  copilot: { projectPath: ".github/skills", homePath: ".copilot/skills" },
  cursor: { projectPath: ".cursor/skills", homePath: ".cursor/skills" },
  gemini: { projectPath: ".gemini/skills", homePath: ".gemini/skills" },
  hermes: {
    projectPath: ".hermes/skills/oma",
    homePath: ".hermes/skills/oma",
    requiresHomeConsent: true,
  },
  qwen: { projectPath: ".qwen/skills", homePath: ".qwen/skills" },
};
