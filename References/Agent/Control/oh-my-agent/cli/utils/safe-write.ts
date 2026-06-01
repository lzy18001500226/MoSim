import * as fs from "node:fs";
import * as path from "node:path";

const BACKUP_RETENTION = 3;

/**
 * Filenames safeWriteJson refuses to overwrite — owned by vendor CLIs, not by oma.
 * Matched by basename, case-sensitively. Add new entries here if a future vendor
 * introduces a user-state file we must not touch.
 *
 * Current entries:
 *   ".claude.json" — Claude Code's user-level session/config store (~/.claude.json).
 *                    Overwriting it would destroy the user's Claude Code authentication
 *                    state, custom settings, and session data.
 *
 * How to add a new entry: append the exact basename string (including any leading dot)
 * to the array below and add a one-line comment explaining which vendor CLI owns it.
 */
export const FORBIDDEN_VENDOR_FILES: ReadonlySet<string> = new Set<string>([
  ".claude.json", // Claude Code user-level session/config store
]);

/**
 * Atomically write a JSON value to `targetPath`.
 *
 * Strategy:
 * 1. Stamp existing target (if any) into `<dir>/.<name>.backup-<Date.now()>-<pid>` (3-tier rotation: keep last 3, delete older).
 * 2. Write payload to a sibling temp file `<dir>/.<name>.tmp-<Date.now()>-<pid>`.
 * 3. `fs.renameSync(tmp, target)` for atomic swap.
 *    - On `EXDEV` (cross-device link error), fall back to `fs.copyFileSync(tmp, target)` + `fs.unlinkSync(tmp)`.
 * 4. Best-effort: leave backups around. They are only pruned when retention threshold exceeded.
 *
 * Pretty-printed JSON (2-space indent) with trailing newline.
 *
 * Throws immediately (before any filesystem operation) if the basename of `targetPath`
 * is listed in `FORBIDDEN_VENDOR_FILES`. These are files owned by vendor CLIs (e.g.
 * `~/.claude.json`) that oma must never overwrite.
 *
 * @param targetPath absolute path
 * @param value any JSON-serializable value
 * @throws {Error} if `path.basename(targetPath)` is in `FORBIDDEN_VENDOR_FILES`
 */
export function safeWriteJson(targetPath: string, value: unknown): void {
  const basename = path.basename(targetPath);
  if (FORBIDDEN_VENDOR_FILES.has(basename)) {
    throw new Error(
      `safeWriteJson: refusing to write ${basename} — vendor-owned file (FORBIDDEN_VENDOR_FILES). targetPath=${targetPath}`,
    );
  }

  const dir = path.dirname(targetPath);
  const stamp = `${Date.now()}-${process.pid}`;

  // Ensure parent directory exists
  fs.mkdirSync(dir, { recursive: true });

  // Step 1: backup existing target if it exists
  if (fs.existsSync(targetPath)) {
    const backupPath = path.join(dir, `.${basename}.backup-${stamp}`);
    fs.copyFileSync(targetPath, backupPath);
  }

  // Step 2: write to temp file
  const tmpPath = path.join(dir, `.${basename}.tmp-${stamp}`);
  const payload = `${JSON.stringify(value, null, 2)}\n`;
  fs.writeFileSync(tmpPath, payload, "utf-8");

  // Step 3: atomic rename, EXDEV fallback
  try {
    fs.renameSync(tmpPath, targetPath);
  } catch (err) {
    if (
      err instanceof Error &&
      (err as NodeJS.ErrnoException).code === "EXDEV"
    ) {
      fs.copyFileSync(tmpPath, targetPath);
      fs.unlinkSync(tmpPath);
    } else {
      throw err;
    }
  }

  // Step 4: prune old backups, keep last BACKUP_RETENTION
  pruneBackups(dir, basename);
}

/** List existing backups for diagnostic / restore use. Sorted newest-first. */
export function listBackups(targetPath: string): string[] {
  const dir = path.dirname(targetPath);
  const basename = path.basename(targetPath);
  return getBackupsSortedNewestFirst(dir, basename);
}

function getBackupsSortedNewestFirst(dir: string, basename: string): string[] {
  let entries: fs.Dirent[];
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return [];
  }

  const prefix = `.${basename}.backup-`;
  const backupPaths = entries
    .filter((e) => e.isFile() && e.name.startsWith(prefix))
    .map((e) => path.join(dir, e.name));

  if (backupPaths.length === 0) return [];

  // Sort newest-first by mtime
  return backupPaths.sort((a, b) => {
    try {
      const mtimeA = fs.statSync(a).mtimeMs;
      const mtimeB = fs.statSync(b).mtimeMs;
      return mtimeB - mtimeA;
    } catch {
      return 0;
    }
  });
}

function pruneBackups(dir: string, basename: string): void {
  const sorted = getBackupsSortedNewestFirst(dir, basename);
  const toDelete = sorted.slice(BACKUP_RETENTION);
  for (const filePath of toDelete) {
    try {
      fs.unlinkSync(filePath);
    } catch {
      // Best-effort: ignore pruning errors
    }
  }
}
