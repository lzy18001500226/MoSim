import { execFileSync, execSync } from "node:child_process";
import {
  appendFileSync,
  existsSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { resolve, sep } from "node:path";

/**
 * True when `repoRoot` is inside a git work tree (or is one).
 * No-throw — returns false on any error.
 */
export function isGitRepo(repoRoot: string): boolean {
  try {
    execFileSync("git", ["rev-parse", "--is-inside-work-tree"], {
      cwd: repoRoot,
      stdio: ["ignore", "ignore", "ignore"],
    });
    return true;
  } catch {
    return false;
  }
}

/**
 * Per-path gitignore check. Returns false outside a git repo.
 *
 * Uses `git check-ignore -q` with an array argument list — no shell
 * interpolation, so paths with spaces or quotes are safe.
 */
export function isPathGitIgnored(absPath: string, repoRoot: string): boolean {
  try {
    execFileSync("git", ["check-ignore", "-q", "--", absPath], {
      cwd: repoRoot,
      stdio: ["ignore", "ignore", "ignore"],
    });
    return true;
  } catch {
    return false;
  }
}

/**
 * Bulk-list every gitignored path under `repoRoot` (resolved absolute).
 * Cheaper than per-file checks when walking a tree.
 *
 * Returns an empty Set if `repoRoot` is not a git repo.
 */
export function listGitIgnoredPaths(repoRoot: string): Set<string> {
  try {
    const output = execSync(
      "git ls-files --others --ignored --exclude-standard --directory -z",
      {
        cwd: repoRoot,
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "ignore"],
      },
    );
    const paths = output.split("\0").filter(Boolean);
    return new Set(paths.map((p) => resolve(repoRoot, p)));
  } catch {
    return new Set();
  }
}

/**
 * Membership test against a Set returned by `listGitIgnoredPaths`.
 * Honors directory-prefix matches (git emits dir entries with trailing /).
 */
export function isInIgnoredSet(
  absPath: string,
  ignoredSet: Set<string>,
): boolean {
  if (ignoredSet.has(absPath)) return true;
  for (const ignored of ignoredSet) {
    const normalized = ignored.endsWith("/") ? ignored.slice(0, -1) : ignored;
    if (absPath === normalized || absPath.startsWith(`${normalized}${sep}`)) {
      return true;
    }
  }
  return false;
}

export interface EnsureGitignoredResult {
  added: string[];
  alreadyPresent: string[];
  skipped: boolean;
}

/**
 * Append `patterns` to `<repoRoot>/.gitignore` when not already covered.
 *
 * - Skips with `skipped: true` when `repoRoot` is not a git repo.
 * - Creates `.gitignore` if missing.
 * - Compares pattern lines exactly (after trimming, ignoring blanks/comments).
 * - On first append, optionally writes a single `header` line ahead of the
 *   new patterns. The header is also tracked exactly, so re-runs do not
 *   duplicate it.
 *
 * Note: this does NOT consult `git check-ignore` — a pattern can be
 * effectively ignored via parent globs (e.g. `**\/*.log` covers
 * `docs/*.log`) without an exact line match. We only avoid duplicate
 * exact lines; semantic-coverage checks are out of scope.
 */
export function ensureGitignored(
  repoRoot: string,
  patterns: string[],
  options: { header?: string } = {},
): EnsureGitignoredResult {
  if (!isGitRepo(repoRoot)) {
    return { added: [], alreadyPresent: [], skipped: true };
  }

  const gitignorePath = resolve(repoRoot, ".gitignore");
  const existing = existsSync(gitignorePath)
    ? readFileSync(gitignorePath, "utf-8")
    : "";

  const existingLines = new Set(
    existing
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line.length > 0 && !line.startsWith("#")),
  );

  const added: string[] = [];
  const alreadyPresent: string[] = [];
  for (const raw of patterns) {
    const pattern = raw.trim();
    if (!pattern) continue;
    if (existingLines.has(pattern)) {
      alreadyPresent.push(pattern);
    } else {
      added.push(pattern);
      existingLines.add(pattern);
    }
  }

  if (added.length === 0) {
    return { added, alreadyPresent, skipped: false };
  }

  const header = options.header?.trim();
  const headerAlreadyPresent =
    header !== undefined &&
    existing.split(/\r?\n/).some((line) => line.trim() === header);

  const block: string[] = [];
  if (header && !headerAlreadyPresent) block.push(header);
  block.push(...added);

  const needsLeadingNewline =
    existing.length > 0 && !existing.endsWith("\n") ? "\n" : "";
  const padding = existing.length > 0 ? "\n" : "";
  const payload = `${needsLeadingNewline}${padding}${block.join("\n")}\n`;

  if (existing.length === 0) {
    writeFileSync(gitignorePath, payload);
  } else {
    appendFileSync(gitignorePath, payload);
  }

  return { added, alreadyPresent, skipped: false };
}
