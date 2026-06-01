/**
 * Migration 004: Remove OMA block from global ~/.claude/CLAUDE.md
 *
 * Previously, `oma install` merged the OMA usage guide into the global
 * ~/.claude/CLAUDE.md. This has been replaced by project-local ./CLAUDE.md.
 *
 * This migration:
 * 1. Strips the <!-- OMA:START ... --> ... <!-- OMA:END --> block from ~/.claude/CLAUDE.md
 * 2. Deletes the file if it becomes empty after stripping
 */
import { existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import type { Migration } from "./index.js";

const OMA_START_PREFIX = "<!-- OMA:START";
const OMA_END = "<!-- OMA:END -->";

export const migrateClaudeMdLocal: Migration = {
  name: "004-claude-md-local",
  up(_cwd: string): string[] {
    const actions: string[] = [];
    const homeDir = process.env.HOME || process.env.USERPROFILE || "";
    if (!homeDir) return actions;

    const globalClaudeMd = join(homeDir, ".claude", "CLAUDE.md");
    if (!existsSync(globalClaudeMd)) return actions;

    const content = readFileSync(globalClaudeMd, "utf-8");
    const startIdx = content.indexOf(OMA_START_PREFIX);
    const endIdx = content.indexOf(OMA_END);

    if (startIdx === -1 || endIdx === -1) return actions;

    const before = content.slice(0, startIdx);
    const after = content.slice(endIdx + OMA_END.length);
    const cleaned = `${before}${after}`.trim();

    if (cleaned.length === 0) {
      rmSync(globalClaudeMd);
      actions.push("~/.claude/CLAUDE.md removed (OMA block was only content)");
    } else {
      writeFileSync(globalClaudeMd, `${cleaned}\n`);
      actions.push(
        "~/.claude/CLAUDE.md: OMA block removed (migrated to local ./CLAUDE.md)",
      );
    }

    return actions;
  },
};
