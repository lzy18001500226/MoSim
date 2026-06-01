/**
 * File-based TTL cache for `oma market harvest`.
 *
 * Design ref: docs/plans/designs/011-oma-market-research.md §4 (harvest cache) and §7 (idempotency).
 * Cache layout: ~/.cache/oma/market/{sha1-key}/result.json
 *
 * Rules:
 * - Never throws — all filesystem errors are caught and converted to null returns.
 * - Atomic writes via .tmp → rename to survive interrupted processes.
 * - No third-party deps; only Node builtins.
 */

import { createHash } from "node:crypto";
import {
  access,
  mkdir,
  readFile,
  rename,
  rm,
  stat,
  writeFile,
} from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";

const CACHE_BASE = join(homedir(), ".cache", "oma", "market-research");

// ---------------------------------------------------------------------------
// cacheKey
// ---------------------------------------------------------------------------

/**
 * Derives a deterministic cache key from an arbitrary record.
 * Keys are sorted before JSON serialisation so that insertion order does not
 * affect the result.
 */
export function cacheKey(parts: Record<string, unknown>): string {
  const sorted = Object.fromEntries(
    Object.entries(parts).sort(([a], [b]) => a.localeCompare(b)),
  );
  const payload = JSON.stringify(sorted);
  return createHash("sha1").update(payload, "utf-8").digest("hex");
}

// ---------------------------------------------------------------------------
// cachePath
// ---------------------------------------------------------------------------

/**
 * Resolves the absolute path for a cache entry and creates the parent
 * directory on demand. Returns the path regardless of whether creation
 * succeeded — the caller will surface any IO error later via the cache miss
 * path.
 */
export async function cachePath(key: string): Promise<string> {
  const dir = join(CACHE_BASE, key);
  try {
    await mkdir(dir, { recursive: true });
  } catch {
    // Best-effort: if mkdir fails the subsequent read/write will also fail and
    // be caught individually.
  }
  return join(dir, "result.json");
}

// ---------------------------------------------------------------------------
// readCache
// ---------------------------------------------------------------------------

/**
 * Returns the cached value if the file exists and its mtime is within `ttlMs`
 * milliseconds of now. Returns null on any error (missing file, parse error,
 * expired TTL).
 */
export async function readCache<T>(
  key: string,
  ttlMs: number,
): Promise<T | null> {
  try {
    const file = await cachePath(key);
    const info = await stat(file);
    const ageMs = Date.now() - info.mtimeMs;
    if (ageMs >= ttlMs) return null;
    const raw = await readFile(file, "utf-8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// writeCache
// ---------------------------------------------------------------------------

/**
 * Writes `value` to the cache with an atomic tmp → rename sequence.
 * An interrupted process will leave a `.tmp` orphan; v1 does not clean these up.
 */
export async function writeCache(key: string, value: unknown): Promise<void> {
  try {
    const file = await cachePath(key);
    const tmp = `${file}.tmp`;
    await writeFile(tmp, JSON.stringify(value), "utf-8");
    await rename(tmp, file);
  } catch {
    // Silently swallow — a failed write is a warm-cache miss on the next run.
  }
}

// ---------------------------------------------------------------------------
// parseTtl
// ---------------------------------------------------------------------------

/**
 * Parses a human-readable TTL string into milliseconds.
 *
 * Accepted formats:
 *   "15m"   → 15 minutes
 *   "1h"    → 1 hour
 *   "2d"    → 2 days
 *   "900000"→ raw ms integer
 *   undefined → defaultMs (15 minutes by default)
 */
export function parseTtl(
  input: string | undefined,
  defaultMs = 15 * 60_000,
): number {
  if (input === undefined || input === "") return defaultMs;

  const trimmed = input.trim();

  const minuteMatch = /^(\d+(?:\.\d+)?)m$/i.exec(trimmed);
  if (minuteMatch !== null) {
    return Math.round(Number(minuteMatch[1]) * 60_000);
  }

  const hourMatch = /^(\d+(?:\.\d+)?)h$/i.exec(trimmed);
  if (hourMatch !== null) {
    return Math.round(Number(hourMatch[1]) * 60 * 60_000);
  }

  const dayMatch = /^(\d+(?:\.\d+)?)d$/i.exec(trimmed);
  if (dayMatch !== null) {
    return Math.round(Number(dayMatch[1]) * 24 * 60 * 60_000);
  }

  const raw = Number(trimmed);
  if (!Number.isNaN(raw) && raw > 0) return Math.round(raw);

  return defaultMs;
}

// ---------------------------------------------------------------------------
// purgeStale
// ---------------------------------------------------------------------------

/**
 * Walks the cache directory and removes entries whose `result.json` is older
 * than `maxAgeMs`. Each entry lives in its own subdirectory named by its key.
 *
 * Intended for manual maintenance; not called in the hot path.
 */
export async function purgeStale(
  maxAgeMs: number,
): Promise<{ removed: number; skipped: number }> {
  let removed = 0;
  let skipped = 0;

  try {
    await access(CACHE_BASE);
  } catch {
    // Cache directory does not exist yet — nothing to purge.
    return { removed, skipped };
  }

  const { readdir } = await import("node:fs/promises");
  let entries: string[];
  try {
    entries = await readdir(CACHE_BASE);
  } catch {
    return { removed, skipped };
  }

  const now = Date.now();

  await Promise.all(
    entries.map(async (entry) => {
      const entryDir = join(CACHE_BASE, entry);
      const resultFile = join(entryDir, "result.json");
      try {
        const info = await stat(resultFile);
        const ageMs = now - info.mtimeMs;
        if (ageMs >= maxAgeMs) {
          await rm(entryDir, { recursive: true, force: true });
          removed++;
        } else {
          skipped++;
        }
      } catch {
        // Malformed entry (no result.json, unreadable stat) — skip silently.
        skipped++;
      }
    }),
  );

  return { removed, skipped };
}
